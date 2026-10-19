#!/usr/bin/env python3
"""
Hybrid Window-PRIME Attention Surgery for Phi-3 & Qwen2 Models
==============================================================
Adapted from https://github.com/batteryphil/PRIME-Moment-Attention (`hybrid.py`).

Combines:
  1. Local Sliding Window [t - W + 1, t]: Exact Softmax attention over recent W tokens.
  2. Recurrent Second-Order Moment State [0, t - W]: Taylor polynomial recurrence
     accumulating all historical tokens evicted from the sliding window:
       S0_t = lambda * S0_{t-1} + v_t
       S1_t = lambda * S1_{t-1} + k_t v_t^T
       S2_t = lambda * S2_{t-1} + (k_t odot k_t) v_t^T
  3. Gated Convex Combination:
       Output_t = alpha * Attn_local(W) + (1 - alpha) * Attn_PRIME(S0, S1, S2)

Memory is strictly bounded to O(W + D^2) and independent of sequence length L.
Supports both split projections (`q_proj`, `k_proj`, `v_proj` in Qwen/Llama) and
fused projections (`qkv_proj` in Phi-3 Mini).
"""

from typing import Optional, Tuple, List
import torch
import torch.nn as nn
import torch.nn.functional as F


class HybridWindowPrimeAttention(nn.Module):
    def __init__(
        self,
        original_attn: nn.Module,
        layer_idx: int,
        window_size: int = 256,
        decay: float = 0.9995,
        alpha: float = 0.5,
    ):
        super().__init__()
        self.config = getattr(original_attn, "config", None)
        self.layer_idx = layer_idx
        self.hidden_size = getattr(
            original_attn,
            "hidden_size",
            getattr(self.config, "hidden_size", 3072),
        )
        self.num_heads = getattr(
            original_attn,
            "num_heads",
            getattr(self.config, "num_attention_heads", 32),
        )
        self.head_dim = getattr(
            original_attn,
            "head_dim",
            self.hidden_size // self.num_heads,
        )
        self.num_key_value_heads = getattr(
            original_attn,
            "num_key_value_heads",
            getattr(self.config, "num_key_value_heads", self.num_heads),
        )
        self.num_key_value_groups = max(1, self.num_heads // self.num_key_value_heads)
        self.scaling = 1.0 / (self.head_dim ** 0.5)
        self.window_size = window_size
        self.decay = decay
        self.alpha = alpha

        # Support both Phi-3 fused qkv_proj and Llama/Qwen split q_proj/k_proj/v_proj
        self.has_fused_qkv = hasattr(original_attn, "qkv_proj")
        if self.has_fused_qkv:
            self.qkv_proj = original_attn.qkv_proj
        else:
            self.q_proj = original_attn.q_proj
            self.k_proj = original_attn.k_proj
            self.v_proj = original_attn.v_proj
        self.o_proj = original_attn.o_proj

    def _project_qkv(self, hidden_states: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        B, L, _ = hidden_states.shape
        if self.has_fused_qkv:
            qkv = self.qkv_proj(hidden_states)
            q_pos = self.num_heads * self.head_dim
            kv_pos = q_pos + self.num_key_value_heads * self.head_dim
            q = qkv[..., :q_pos].view(B, L, self.num_heads, self.head_dim).transpose(1, 2)
            k = qkv[..., q_pos:kv_pos].view(B, L, self.num_key_value_heads, self.head_dim).transpose(1, 2)
            v = qkv[..., kv_pos:].view(B, L, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        else:
            q = self.q_proj(hidden_states).view(B, L, self.num_heads, self.head_dim).transpose(1, 2)
            k = self.k_proj(hidden_states).view(B, L, self.num_key_value_heads, self.head_dim).transpose(1, 2)
            v = self.v_proj(hidden_states).view(B, L, self.num_key_value_heads, self.head_dim).transpose(1, 2)

        if self.num_key_value_groups > 1:
            k = k.repeat_interleave(self.num_key_value_groups, dim=1)
            v = v.repeat_interleave(self.num_key_value_groups, dim=1)
        return q, k, v

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_value: Optional[ object] = None,
        output_attentions: bool = False,
        use_cache: bool = False,
        **kwargs,
    ):
        B, L, _ = hidden_states.shape
        device = hidden_states.device
        query_states, key_states, value_states = self._project_qkv(hidden_states)

        # Mandatory Per-Head QK LayerNorm to prevent Taylor parabolic rebound for x < -1
        q_norm = F.layer_norm(query_states.float(), (self.head_dim,))
        k_norm = F.layer_norm(key_states.float(), (self.head_dim,))
        v_f32 = value_states.float()

        # 1. Second-Order PRIME Moment Recurrence Scan
        out_prime = torch.zeros_like(q_norm)
        S0 = torch.zeros(B, self.num_heads, self.head_dim, device=device, dtype=torch.float32)
        S1 = torch.zeros(B, self.num_heads, self.head_dim, self.head_dim, device=device, dtype=torch.float32)
        S2 = torch.zeros(B, self.num_heads, self.head_dim, self.head_dim, device=device, dtype=torch.float32)
        Z0 = torch.zeros(B, self.num_heads, 1, device=device, dtype=torch.float32)
        Z1 = torch.zeros(B, self.num_heads, self.head_dim, device=device, dtype=torch.float32)
        Z2 = torch.zeros(B, self.num_heads, self.head_dim, device=device, dtype=torch.float32)

        inv_sqrt_d = self.scaling
        inv_2d = 0.5 / float(self.head_dim)

        for t in range(L):
            qt = q_norm[:, :, t]
            kt = k_norm[:, :, t]
            vt = v_f32[:, :, t]
            kt2 = kt * kt
            qt2 = qt * qt

            S0 = self.decay * S0 + vt
            S1 = self.decay * S1 + torch.einsum("bhd,bhe->bhde", kt, vt)
            S2 = self.decay * S2 + torch.einsum("bhd,bhe->bhde", kt2, vt)
            Z0 = self.decay * Z0 + 1.0
            Z1 = self.decay * Z1 + kt
            Z2 = self.decay * Z2 + kt2

            num = (
                S0
                + torch.einsum("bhd,bhde->bhe", qt, S1) * inv_sqrt_d
                + torch.einsum("bhd,bhde->bhe", qt2, S2) * inv_2d
            )
            den = (
                Z0
                + torch.sum(qt * Z1, dim=-1, keepdim=True) * inv_sqrt_d
                + torch.sum(qt2 * Z2, dim=-1, keepdim=True) * inv_2d
            ).clamp(min=1e-3)
            out_prime[:, :, t] = num / den

        out_prime = out_prime.to(query_states.dtype)

        # 2. Bounded Local Sliding-Window Softmax [t - W + 1, t]
        q_scaled = query_states * self.scaling
        scores = torch.matmul(q_scaled, key_states.transpose(2, 3))
        idx = torch.arange(L, device=device)
        diff = idx.unsqueeze(1) - idx.unsqueeze(0)
        win_mask = (diff < 0) | (diff >= self.window_size)
        scores = scores.masked_fill(win_mask.unsqueeze(0).unsqueeze(0), float("-inf"))
        attn_weights = F.softmax(scores.float(), dim=-1).to(query_states.dtype)
        out_local = torch.matmul(attn_weights, value_states)

        # 3. Gated Convex Combination
        fused = self.alpha * out_local + (1.0 - self.alpha) * out_prime
        out = fused.transpose(1, 2).contiguous().view(B, L, -1)
        return self.o_proj(out), None, past_key_value


def convert_transformer_to_hybrid_prime(
    model: nn.Module,
    target_layers: Optional[List[int]] = None,
    window_size: int = 256,
    decay: float = 0.9995,
    alpha: float = 0.5,
) -> Tuple[nn.Module, List[int]]:
    """
    Surgically replaces specified Transformer attention layers with bounded
    O(W + D^2) HybridWindowPrimeAttention.
    """
    layers = None
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        layers = model.model.layers
    elif hasattr(model, "layers"):
        layers = model.layers
    if layers is None:
        return model, []

    num_layers = len(layers)
    if target_layers is None:
        target_layers = [num_layers // 2]

    for idx in target_layers:
        layer = layers[idx]
        attr_name = "self_attn" if hasattr(layer, "self_attn") else "attn"
        orig_attn = getattr(layer, attr_name)
        hybrid_layer = HybridWindowPrimeAttention(
            original_attn=orig_attn,
            layer_idx=idx,
            window_size=window_size,
            decay=decay,
            alpha=alpha,
        )
        setattr(layer, attr_name, hybrid_layer)

    return model, target_layers

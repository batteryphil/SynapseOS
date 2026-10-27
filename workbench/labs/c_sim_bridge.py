"""
SynapseOS C99 Simulation & Neural Core Bridge (`workbench/labs/c_sim_bridge.py`)
================================================================================
Loads the compiled C99 shared library (`cortex/c_prime/bin/libsynapse_core.so`)
built alongside the Fil-C Memory-Safe Cosmopolitan APE (`synapse_core_filc.com`)
and Cosmopolitan APE (`synapse_core.com`).

Provides direct ctypes bindings for:
  1. `synapse_mlp_predict` & `synapse_mlp_train_epochs` (Lab 5: 2D MLP Backprop)
  2. `synapse_track_dist` & `synapse_car_cast_rays` (Lab 2: 5-Beam Lidar Raycaster)
  3. `synapse_swarm_step` (Lab 6: O(N^2) Predator-Prey Boids Swarm)
  4. `synapse_cartpole_step` (Lab 4: CartPole Non-Linear Euler-Lagrange Physics)
  5. `synapse_lander_step` (Lab 1: Rocket Moon Lander Physics & Terrain Collision)
  6. `synapse_neat_forward` (Topological NEAT Feed-Forward Evaluation)
"""

import ctypes
import os
from typing import Optional

_C_FLOAT_P = ctypes.POINTER(ctypes.c_float)
_C_INT_P = ctypes.POINTER(ctypes.c_int)


def _load_synapse_core() -> Optional[ctypes.CDLL]:
    here = os.path.dirname(os.path.realpath(__file__))
    root = os.path.abspath(os.path.join(here, "..", ".."))
    candidates = [
        os.path.join(root, "cortex", "c_prime", "bin", "libsynapse_core.so"),
        os.path.join(root, "cortex", "c_prime", "bin", "libprime.so"),
        "/usr/local/lib/synapse/cortex/c_prime/bin/libsynapse_core.so",
        "/usr/local/lib/synapse/cortex/c_prime/bin/libprime.so",
    ]
    for path in candidates:
        if not os.path.exists(path):
            continue
        try:
            lib = ctypes.CDLL(path)
            if not hasattr(lib, "synapse_mlp_train_epochs"):
                continue

            lib.synapse_mlp_predict.argtypes = [
                ctypes.c_float, ctypes.c_float, ctypes.c_int, ctypes.c_int, ctypes.c_float,
                _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P, ctypes.c_float, _C_FLOAT_P,
            ]
            lib.synapse_mlp_predict.restype = ctypes.c_float

            lib.synapse_mlp_train_epochs.argtypes = [
                ctypes.c_int, ctypes.c_int,
                _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P,
                ctypes.c_int, ctypes.c_int, ctypes.c_float, ctypes.c_float, ctypes.c_float,
                _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P,
                _C_FLOAT_P, _C_FLOAT_P,
            ]
            lib.synapse_mlp_train_epochs.restype = None

            lib.synapse_track_dist.argtypes = [
                ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float,
            ]
            lib.synapse_track_dist.restype = ctypes.c_float

            lib.synapse_car_cast_rays.argtypes = [
                ctypes.c_float, ctypes.c_float, ctypes.c_float,
                ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float,
                _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P,
            ]
            lib.synapse_car_cast_rays.restype = None

            lib.synapse_swarm_step.argtypes = [
                ctypes.c_int,
                _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P,
                ctypes.c_int,
                _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P,
                ctypes.c_int,
                _C_FLOAT_P, _C_FLOAT_P,
                ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float,
                ctypes.c_uint,
            ]
            lib.synapse_swarm_step.restype = None

            lib.synapse_cartpole_step.argtypes = [
                _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P,
                _C_INT_P, ctypes.c_int,
                ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float,
            ]
            lib.synapse_cartpole_step.restype = ctypes.c_int

            lib.synapse_lander_step.argtypes = [
                _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P,
                _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P,
                _C_INT_P, ctypes.c_int,
                ctypes.c_int, ctypes.c_int, ctypes.c_int,
                ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float,
                ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float,
                _C_INT_P, _C_INT_P,
            ]
            lib.synapse_lander_step.restype = ctypes.c_int

            if hasattr(lib, "synapse_trit64_bench"):
                lib.synapse_trit64_bench.argtypes = [
                    ctypes.c_int, ctypes.c_int,
                    _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P, _C_INT_P,
                ]
                lib.synapse_trit64_bench.restype = None

            if hasattr(lib, "synapse_prime_trit64_bench"):
                lib.synapse_prime_trit64_bench.argtypes = [
                    ctypes.c_int, ctypes.c_int, ctypes.c_int,
                    _C_FLOAT_P, _C_FLOAT_P, _C_FLOAT_P,
                ]
                lib.synapse_prime_trit64_bench.restype = None

            return lib
        except Exception:
            continue
    return None


SYNAPSE_C_CORE = _load_synapse_core()


def benchmark_buildbit_potato_kernels(dim: int = 1024, n_tokens: int = 64) -> dict:
    """Run BuildbitOS 1.58-Bit Ternary Bit-Sliced POPCNT + PRIME-Moment Attention Potato Benchmarks."""
    if SYNAPSE_C_CORE is None or not hasattr(SYNAPSE_C_CORE, "synapse_trit64_bench"):
        return {"available": False}
    fp32_ms = ctypes.c_float(0.0)
    trit_ms = ctypes.c_float(0.0)
    speedup = ctypes.c_float(0.0)
    exact = ctypes.c_int(0)
    SYNAPSE_C_CORE.synapse_trit64_bench(
        dim, n_tokens,
        ctypes.byref(fp32_ms), ctypes.byref(trit_ms),
        ctypes.byref(speedup), ctypes.byref(exact),
    )

    prime_ms = ctypes.c_float(0.0)
    tok_s = ctypes.c_float(0.0)
    state_kb = ctypes.c_float(0.0)
    SYNAPSE_C_CORE.synapse_prime_trit64_bench(
        8, 64, 512,
        ctypes.byref(prime_ms), ctypes.byref(tok_s), ctypes.byref(state_kb),
    )
    return {
        "available": True,
        "dim": dim,
        "n_tokens": n_tokens,
        "fp32_ms": round(float(fp32_ms.value), 3),
        "trit_ms": round(float(trit_ms.value), 3),
        "trit_speedup": round(float(speedup.value), 2),
        "trit_exact_match": bool(exact.value == 1),
        "prime_step_ms": round(float(prime_ms.value), 3),
        "prime_tok_per_sec": round(float(tok_s.value), 1),
        "prime_state_kb": round(float(state_kb.value), 1),
    }



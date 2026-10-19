"""
Cortex Knowledge Base: AI Paradigms & Experimentation Guide
Covers Neuroevolution (NEAT), Genetic Algorithms, Reinforcement Learning,
Deep Learning, Foundation Models/LLMs, and Computer Vision.
"""

from typing import Dict, List, Any

AI_TOPICS: Dict[str, Dict[str, Any]] = {
    "neat": {
        "paradigm": "Neuroevolution",
        "title": "NEAT (Neuroevolution of Augmenting Topologies)",
        "summary": "Evolves both the connection weights AND the neural network structure (nodes & connections) simultaneously from minimal topologies.",
        "key_concepts": {
            "Genome": "Represents an individual neural network, consisting of Node genes (inputs, hidden, outputs) and Connection genes.",
            "Historical Markings (Innovations)": "Unique global innovation numbers tracking when connections arise, solving the crossover compatibility problem.",
            "Speciation": "Groups similar topologies into species so new innovative structural mutations have time to optimize weights before facing competition.",
            "Fitness Function": "Score assigned to each genome reflecting performance (e.g. distance to landing pad, soft touchdown velocity, fuel conserved)."
        },
        "hyperparameters": {
            "pop_size": {"desc": "Number of neural networks per generation.", "recommended": "100 - 300", "effect": "Higher explores more diversity; lower runs faster."},
            "conn_add_prob": {"desc": "Probability of adding a new synaptic connection.", "recommended": "0.05 - 0.2", "effect": "Controls how quickly networks become denser."},
            "node_add_prob": {"desc": "Probability of inserting a new neuron.", "recommended": "0.02 - 0.05", "effect": "Controls structural complexity growth."},
            "weight_mutate_power": {"desc": "Standard deviation of weight perturbations.", "recommended": "0.5 - 1.0", "effect": "Higher causes dramatic behavioral swings; lower allows fine tuning."},
            "compatibility_threshold": {"desc": "Distance threshold to split networks into separate species.", "recommended": "2.5 - 3.5", "effect": "Tuned to maintain ~8-15 active species."}
        },
        "lunar_lander_recipe": {
            "inputs": ["x_pos", "y_pos", "x_vel", "y_vel", "angle", "angular_vel", "left_leg_contact", "right_leg_contact"],
            "outputs": ["do_nothing", "fire_left_engine", "fire_main_engine", "fire_right_engine"],
            "fitness_formula": "fitness = 100 - (100 * dist_to_target) - (50 * abs(velocity)) + (200 if landed else -100 if crashed) - (0.3 * fuel_spent)"
        }
    },
    "reinforcement_learning": {
        "paradigm": "Reinforcement Learning",
        "title": "RL: PPO, DQN, and Actor-Critic",
        "summary": "Agents learn optimal policies through trial-and-error feedback (rewards/penalties) inside Markov Decision Process (MDP) environments.",
        "algorithms": {
            "DQN (Deep Q-Network)": "Value-based method for discrete action spaces (e.g. Atari, CartPole). Uses replay buffer and target networks.",
            "PPO (Proximal Policy Optimization)": "Policy-gradient actor-critic method for both continuous (robot joints) and discrete control. Clipped surrogate objective prevents destructive policy updates.",
            "SAC (Soft Actor-Critic)": "Off-policy maximum entropy actor-critic method ideal for continuous robotic manipulation and sample efficiency."
        },
        "hyperparameters": {
            "learning_rate (alpha)": "Step size for optimizer (typically 3e-4 for PPO, 1e-3 for DQN).",
            "discount_factor (gamma)": "Value of future rewards vs immediate rewards (typically 0.99).",
            "clip_epsilon": "PPO surrogate clipping bound (typically 0.2).",
            "batch_size": "Number of experience transitions sampled per gradient update."
        }
    },
    "llm_and_foundation_models": {
        "paradigm": "Language & Foundation Models",
        "title": "Local LLM Inference, Fine-Tuning & RAG",
        "summary": "Running, adapting, and querying transformer-based generative models locally with zero external network reliance.",
        "workflows": {
            "Local Inference (llama.cpp / Ollama)": "Quantized GGUF models (Q4_K_M, Q8_0) executed directly on GPU/CPU with low memory footprints.",
            "LoRA (Low-Rank Adaptation)": "Parameter-Efficient Fine-Tuning (PEFT) freezing the base model and training small rank decomposition matrices (A and B).",
            "RAG (Retrieval-Augmented Generation)": "Chunking documents, embedding them into vector space, retrieving top-k matches, and injecting them into the LLM context window."
        },
        "key_parameters": {
            "temperature": "Controls randomness (0.0 = deterministic/coding; 0.7 = natural conversation; 1.2 = creative brainstorming).",
            "top_p": "Nucleus sampling probability mass cutoff.",
            "context_window (n_ctx)": "Maximum token limit the model can remember in a single session.",
            "quantization": "Precision reduction (e.g. FP16 -> INT4) yielding 75% memory reduction with negligible perceptual loss."
        }
    },
    "computer_vision": {
        "paradigm": "Computer Vision",
        "title": "Object Detection & Diffusion",
        "summary": "Visual scene understanding, real-time object tracking, and generative visual synthesis.",
        "tools": {
            "YOLO (You Only Look Once)": "Single-stage real-time object detector achieving 60+ FPS on edge hardware.",
            "Stable Diffusion / Latent Diffusion": "Generates imagery by progressively denoising random latents guided by text embeddings via cross-attention.",
            "OpenCV": "Classical image processing (edge detection, optical flow, geometric transforms, contour analysis)."
        }
    }
}

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

            return lib
        except Exception:
            continue
    return None


SYNAPSE_C_CORE = _load_synapse_core()

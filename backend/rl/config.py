"""Central configuration for the SmartFlow RL traffic-signal controller.

Single source of truth for file paths, the SUMO/RL environment settings, and
training hyperparameters. Importing from one module keeps train.py, evaluate.py
and the API in sync and makes runs reproducible.
"""
from __future__ import annotations

from pathlib import Path

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
RL_DIR = Path(__file__).resolve().parent          # backend/rl
BACKEND_DIR = RL_DIR.parent                        # backend
NETS_DIR = RL_DIR / "nets"
ARTIFACTS_DIR = BACKEND_DIR / "artifacts"          # models, logs, plots (gitignored)
MODELS_DIR = ARTIFACTS_DIR / "models"
LOG_DIR = ARTIFACTS_DIR / "logs"                   # TensorBoard + episode CSVs
PLOTS_DIR = ARTIFACTS_DIR / "plots"

NET_FILE = NETS_DIR / "single.net.xml"                 # static-TL network
NET_ACTUATED_FILE = NETS_DIR / "single_actuated.net.xml"  # gap-based actuated TL
ROUTE_FILE = NETS_DIR / "single.rou.xml"
SUMOCFG_FILE = NETS_DIR / "single.sumocfg"

# Phase 5: emergency-vehicle preemption scenario (reuses the static network).
SCENARIOS_DIR = BACKEND_DIR / "scenarios"
EMERGENCY_ROUTE_FILE = SCENARIOS_DIR / "emergency" / "emergency.rou.xml"

# Presentable demo assets (colourful typed traffic + sumo-gui view settings).
DEMO_ROUTE_FILE = SCENARIOS_DIR / "demo" / "demo.rou.xml"
DEMO_VIEW_FILE = SCENARIOS_DIR / "demo" / "demo.view.xml"

# Multi-intersection (2x2 grid) scenario for multi-agent RL.
GRID_DIR = NETS_DIR / "grid"
GRID_NET_FILE = GRID_DIR / "grid.net.xml"                  # static-TL grid
GRID_NET_ACTUATED_FILE = GRID_DIR / "grid_actuated.net.xml"  # actuated-TL grid
GRID_ROUTE_FILE = GRID_DIR / "grid.rou.xml"
GRID_VIEW_FILE = GRID_DIR / "grid.view.xml"                 # sumo-gui view settings

for _d in (MODELS_DIR, LOG_DIR, PLOTS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------- #
# Reproducibility
# --------------------------------------------------------------------------- #
SEED = 42

# --------------------------------------------------------------------------- #
# Environment (sumo-rl SumoEnvironment) settings
#
#   delta_time : sim-seconds between agent decisions
#   yellow_time: fixed yellow inserted by sumo-rl on every phase switch
#   min_green  : minimum green an approach must hold before it can switch
#   max_green  : cap on a single green so a starved approach is never ignored
#   num_seconds: simulated seconds per episode (matches the 1h route file)
#
# Observation (19 dims): phase one-hot(2) + min-green flag(1)
#                        + per-lane density(8) + per-lane queue(8)
# Action: Discrete(2)  -> activate NS-green or EW-green next.
# --------------------------------------------------------------------------- #
ENV_CONFIG = dict(
    num_seconds=3600,
    delta_time=5,
    yellow_time=3,
    min_green=10,
    max_green=60,
)

# --------------------------------------------------------------------------- #
# Training hyperparameters
# --------------------------------------------------------------------------- #
DQN_PARAMS = dict(
    learning_rate=1e-3,
    buffer_size=50_000,
    learning_starts=2_000,
    batch_size=64,
    gamma=0.95,
    train_freq=1,
    target_update_interval=1_000,
    exploration_fraction=0.4,
    exploration_final_eps=0.02,
    policy_kwargs=dict(net_arch=[128, 128]),
)

PPO_PARAMS = dict(
    learning_rate=3e-4,
    n_steps=512,
    batch_size=128,
    gamma=0.95,
    gae_lambda=0.95,
    ent_coef=0.01,
    policy_kwargs=dict(net_arch=[128, 128]),
)

DEFAULT_TOTAL_TIMESTEPS = 100_000

# Multi-agent (parameter-sharing PPO) hyperparameters for the grid. One shared
# policy controls all intersections; the N agents are vectorised, so each
# environment step yields N transitions.
GRID_ENV_CONFIG = dict(
    num_seconds=3600,
    delta_time=5,
    yellow_time=3,
    min_green=10,
    max_green=60,
)
GRID_PPO_PARAMS = dict(
    learning_rate=3e-4,
    n_steps=256,
    batch_size=128,
    gamma=0.95,
    gae_lambda=0.95,
    ent_coef=0.01,
    policy_kwargs=dict(net_arch=[128, 128]),
)
GRID_DEFAULT_TIMESTEPS = 200_000

"""Train a shared multi-agent policy on the 2x2 grid (parameter-sharing PPO).

One command, reproducible (fixed seed), TensorBoard logging. A single PPO policy
is shared across all four intersections; with the agents vectorised, each
environment step contributes N transitions.

Examples
--------
    # from backend/, project venv
    python -m rl.train_grid --timesteps 200000
    python -m rl.train_grid --timesteps 50000 --tag quick

TensorBoard:
    tensorboard --logdir backend/artifacts/logs
"""
from __future__ import annotations

import argparse

from stable_baselines3 import PPO
from stable_baselines3.common.utils import set_random_seed

from . import config
from .grid_env import make_grid_vec_env


def train(timesteps: int, seed: int, tag: str) -> str:
    """Train the shared grid policy and return the saved model path."""
    run_name = f"grid_ppo_{tag}" if tag else "grid_ppo"
    set_random_seed(seed)

    venv = make_grid_vec_env(reward="queue_wait", seed=seed)
    # Reproducibility comes from set_random_seed (numpy/torch) above + the env's
    # sumo_seed. We pass seed=None to PPO because SB3 would otherwise call
    # VecEnv.seed(), which supersuit's ConcatVecEnv does not implement.
    model = PPO(
        "MlpPolicy",
        venv,
        seed=None,
        verbose=1,
        tensorboard_log=str(config.LOG_DIR),
        **config.GRID_PPO_PARAMS,
    )

    print(f"[train] {run_name}: {timesteps} timesteps across {venv.num_envs} agents, seed={seed}")
    model.learn(total_timesteps=timesteps, tb_log_name=run_name, progress_bar=True)

    model_path = str(config.MODELS_DIR / f"{run_name}.zip")
    model.save(model_path)
    venv.close()
    print(f"[ok] model -> {model_path}")
    return model_path


def main() -> None:
    p = argparse.ArgumentParser(description="Train parameter-sharing PPO on the grid.")
    p.add_argument("--timesteps", type=int, default=config.GRID_DEFAULT_TIMESTEPS)
    p.add_argument("--seed", type=int, default=config.SEED)
    p.add_argument("--tag", default="v1", help="suffix for the run/model name")
    args = p.parse_args()
    train(args.timesteps, args.seed, args.tag)


if __name__ == "__main__":
    main()

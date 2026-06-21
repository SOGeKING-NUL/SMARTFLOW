"""Multi-intersection (2x2 grid) environment for multi-agent RL.

Wraps sumo-rl's PettingZoo ``parallel_env``. All four intersections are
homogeneous (identical 19-dim observation, 2-action spaces), so a **single
shared policy** controls every intersection via parameter sharing (SuperSuit):
the N agents become N vectorised sub-environments of one Stable-Baselines3
policy, and each environment step yields N transitions.

This is the regime where learning is expected to beat per-junction heuristics:
the shared policy can learn to coordinate adjacent signals (e.g. green waves)
from the objective, which fixed-time and purely local controllers cannot.

Compatibility note
------------------
sumo-rl 1.4.5 predates pettingzoo>=1.25 / supersuit 3.11. Two tiny shims bridge
the gap (applied once, at import): the ``agent_selector`` class was renamed to
``AgentSelector``, and supersuit expects a ``render_mode`` attribute on the env.
Multi-agent must use pure traci (not libsumo), so ``LIBSUMO_AS_TRACI`` is
cleared before sumo-rl is imported.
"""
from __future__ import annotations

import os
from typing import Callable, Optional, Union

# Multi-agent uses pure traci; sumo-rl detects libsumo by env-var *presence*.
os.environ.pop("LIBSUMO_AS_TRACI", None)

# --- compatibility shims for sumo-rl 1.4.5 on newer pettingzoo/supersuit ----- #
import sumo_rl.environment.env as _senv
from pettingzoo.utils import AgentSelector as _AgentSelector

_senv.agent_selector = _AgentSelector
if not hasattr(_senv.SumoEnvironmentPZ, "render_mode"):
    _senv.SumoEnvironmentPZ.render_mode = None
# ---------------------------------------------------------------------------- #

import sumo_rl

from . import config
from .rewards import queue_wait, CUSTOM_REWARD_NAME


def _resolve_reward(reward: Union[str, Callable]) -> Union[str, Callable]:
    if reward == CUSTOM_REWARD_NAME:
        return queue_wait
    return reward


def make_grid_parallel_env(
    *,
    reward: Union[str, Callable] = CUSTOM_REWARD_NAME,
    use_gui: bool = False,
    fixed_ts: bool = False,
    seed: int = config.SEED,
    num_seconds: Optional[int] = None,
    net_file: Optional[str] = None,
    route_file: Optional[str] = None,
    out_csv_name: Optional[str] = None,
    additional_sumo_cmd: Optional[str] = None,
):
    """Build the raw PettingZoo parallel env for the grid (one agent / intersection).

    Used directly for evaluation (per-controller rollouts); wrapped by
    ``make_grid_vec_env`` for training.
    """
    env_kwargs = dict(config.GRID_ENV_CONFIG)
    if num_seconds is not None:
        env_kwargs["num_seconds"] = num_seconds

    return sumo_rl.parallel_env(
        net_file=str(net_file or config.GRID_NET_FILE),
        route_file=str(route_file or config.GRID_ROUTE_FILE),
        reward_fn=_resolve_reward(reward),
        use_gui=use_gui,
        fixed_ts=fixed_ts,
        sumo_seed=seed,
        out_csv_name=out_csv_name,
        additional_sumo_cmd=additional_sumo_cmd,
        sumo_warnings=False,
        **env_kwargs,
    )


def make_grid_vec_env(
    *,
    reward: Union[str, Callable] = CUSTOM_REWARD_NAME,
    seed: int = config.SEED,
    num_seconds: Optional[int] = None,
):
    """Parameter-sharing VecEnv for Stable-Baselines3.

    The N intersections of one SUMO simulation become N vectorised sub-envs that
    share a single policy.
    """
    import supersuit as ss

    penv = make_grid_parallel_env(reward=reward, seed=seed, num_seconds=num_seconds)
    venv = ss.pettingzoo_env_to_vec_env_v1(penv)
    venv = ss.concat_vec_envs_v1(venv, 1, num_cpus=1, base_class="stable_baselines3")
    return venv

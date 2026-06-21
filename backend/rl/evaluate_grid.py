"""Evaluate the shared multi-agent grid policy against baselines.

Runs the trained shared PPO policy and three baselines -- fixed-time, actuated
(SUMO), and per-intersection max-pressure -- over the *same* 2x2 grid scenario
and seeds, and reports network-wide metrics:

    * avg waiting time per vehicle (s)   - SUMO tripinfo
    * avg time loss per vehicle  (s)     - SUMO tripinfo
    * avg queue length (halted veh)      - time-averaged network state
    * mean speed (m/s)                   - time-averaged network state
    * throughput (vehicles completed)    - SUMO tripinfo count

Usage (from backend/, project venv):
    python -m rl.evaluate_grid --model results/grid_ppo_v1.zip --seeds 42 7 123
"""
from __future__ import annotations

import argparse
from statistics import mean
from typing import Dict, List

from . import config
from .grid_env import make_grid_parallel_env  # applies the compat shims + clears libsumo
from .rollout import parse_tripinfo

CONTROLLERS = {
    "fixed": "Fixed-time",
    "actuated": "Actuated",
    "maxpressure": "Max-pressure",
    "rl": "RL (PPO, shared)",
}


# --------------------------------------------------------------------------- #
# Per-intersection max-pressure
# --------------------------------------------------------------------------- #
def _phase_lanes(inner, ts_id) -> Dict[int, List[str]]:
    ts = inner.traffic_signals[ts_id]
    links = inner.sumo.trafficlight.getControlledLinks(ts_id)
    out: Dict[int, List[str]] = {}
    for i, phase in enumerate(ts.green_phases):
        served = []
        for j, sig in enumerate(phase.state):
            if sig in ("G", "g") and j < len(links) and links[j]:
                served.append(links[j][0][0])
        out[i] = list(dict.fromkeys(served))
    return out


def _max_pressure_action(inner, phase_lanes: Dict[int, List[str]]) -> int:
    halting = inner.sumo.lane.getLastStepHaltingNumber
    pressures = {p: sum(halting(l) for l in lanes) for p, lanes in phase_lanes.items()}
    return max(pressures, key=lambda p: (pressures[p], -p))


# --------------------------------------------------------------------------- #
# Episode rollout (one controller over the whole grid)
# --------------------------------------------------------------------------- #
def run_grid_episode(kind: str, model, seed: int) -> Dict[str, float]:
    fixed = kind in ("fixed", "actuated")
    net = str(config.GRID_NET_ACTUATED_FILE) if kind == "actuated" else str(config.GRID_NET_FILE)
    tripinfo = str(config.LOG_DIR / f"grid_{kind}_{seed}.xml")

    env = make_grid_parallel_env(
        reward="queue_wait", fixed_ts=fixed, net_file=net, seed=seed,
        additional_sumo_cmd=f"--tripinfo-output {tripinfo}",
    )
    obs, _ = env.reset(seed=seed)
    inner = env.unwrapped.env
    phase_lanes = {ts: _phase_lanes(inner, ts) for ts in inner.ts_ids} if kind == "maxpressure" else {}

    stopped, speeds = [], []
    while env.agents:
        actions = {}
        for a in env.agents:
            if kind == "rl":
                actions[a] = int(model.predict(obs[a], deterministic=True)[0])
            elif kind == "maxpressure":
                actions[a] = _max_pressure_action(inner, phase_lanes[a])
            else:  # fixed / actuated -> SUMO drives the signal, action ignored
                actions[a] = 0
        obs, _, _, _, info = env.step(actions)
        if info:
            ai = next(iter(info.values()))
            if "system_total_stopped" in ai:
                stopped.append(ai["system_total_stopped"])
                speeds.append(ai.get("system_mean_speed", 0.0))
    env.close()

    trip = parse_tripinfo(tripinfo)
    return {
        "avg_wait_s": trip["avg_wait_s"],
        "avg_timeloss_s": trip["avg_timeloss_s"],
        "avg_queue_veh": mean(stopped) if stopped else 0.0,
        "mean_speed_ms": mean(speeds) if speeds else 0.0,
        "throughput_veh": trip["throughput_veh"],
    }


def evaluate(model_path: str, seeds: List[int]) -> "pd.DataFrame":
    import pandas as pd
    from stable_baselines3 import PPO

    model = PPO.load(model_path)  # the grid policy is always parameter-sharing PPO
    rows = []
    for kind, label in CONTROLLERS.items():
        per_seed = []
        for seed in seeds:
            m = run_grid_episode(kind, model if kind == "rl" else None, seed)
            per_seed.append(m)
            print(f"  {label:<18} seed={seed}: wait={m['avg_wait_s']:.1f}s "
                  f"queue={m['avg_queue_veh']:.1f} thru={m['throughput_veh']:.0f}")
        agg = {k: mean(d[k] for d in per_seed) for k in per_seed[0]}
        agg["controller"] = label
        rows.append(agg)

    df = pd.DataFrame(rows).set_index("controller")
    return df[["avg_wait_s", "avg_timeloss_s", "avg_queue_veh", "mean_speed_ms", "throughput_veh"]]


def _to_markdown(df) -> str:
    try:
        return df.to_markdown()
    except ImportError:
        cols = [df.index.name or "controller", *map(str, df.columns)]
        lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
        for idx, row in df.iterrows():
            lines.append("| " + " | ".join([str(idx), *[str(v) for v in row.values]]) + " |")
        return "\n".join(lines)


def _plot(df, out_png: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    metrics = [
        ("avg_wait_s", "Avg waiting time (s)\nlower is better"),
        ("avg_queue_veh", "Avg queue (veh)\nlower is better"),
        ("mean_speed_ms", "Mean speed (m/s)\nhigher is better"),
        ("throughput_veh", "Throughput (veh)\nhigher is better"),
    ]
    fig, axes = plt.subplots(1, len(metrics), figsize=(16, 4.5))
    colors = ["#9aa5b1", "#7b8794", "#52606d", "#2bb673"]
    for ax, (col, title) in zip(axes, metrics):
        vals = df[col]
        ax.bar(range(len(vals)), vals.values, color=colors)
        ax.set_xticks(range(len(vals)))
        ax.set_xticklabels(vals.index, rotation=30, ha="right", fontsize=8)
        ax.set_title(title, fontsize=10)
        ax.grid(axis="y", alpha=0.3)
    fig.suptitle("Multi-agent RL vs. baselines (2x2 grid, identical scenario)", fontsize=12)
    fig.tight_layout()
    fig.savefig(out_png, dpi=120)
    plt.close(fig)
    print(f"[ok] plot -> {out_png}")


def main() -> None:
    p = argparse.ArgumentParser(description="Evaluate the grid policy vs. baselines.")
    p.add_argument("--model", default=str(config.MODELS_DIR / "grid_ppo_v1.zip"))
    p.add_argument("--seeds", type=int, nargs="+", default=[config.SEED])
    args = p.parse_args()

    print(f"[eval] grid model={args.model} seeds={args.seeds}")
    df = evaluate(args.model, args.seeds)
    print("\n=== Grid results (mean over seeds) ===")
    print(df.round(2).to_string())

    df.round(2).to_csv(config.ARTIFACTS_DIR / "grid_comparison.csv")
    with open(config.ARTIFACTS_DIR / "grid_comparison.md", "w") as f:
        f.write(_to_markdown(df.round(2)))
    _plot(df, str(config.PLOTS_DIR / "grid_comparison.png"))


if __name__ == "__main__":
    main()

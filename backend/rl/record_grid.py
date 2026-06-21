"""Record a GIF of the shared multi-agent policy controlling the 2x2 grid.

Drives sumo-gui through traci (the grid uses pure traci, not libsumo) with the
trained parameter-sharing PPO policy applied to every intersection, and captures
a screenshot per decision step. Needs a desktop/GUI session -- this is a
demo/recording tool, not part of training. A short warm-up runs first so the
roads are already busy in the first frame.

Usage (from backend/, project venv):
    python -m rl.record_grid --model results/grid_ppo_v1.zip
    python -m rl.record_grid --model results/grid_ppo_v1.zip --steps 200 --warmup 25 --fps 12
"""
from __future__ import annotations

import argparse
import glob
import os

from stable_baselines3 import PPO

from . import config
from .grid_env import make_grid_parallel_env  # clears LIBSUMO + applies compat shims

DEFAULT_VIEW = "View #0"


def record(model_path: str, steps: int, out_gif: str, fps: int = 12, warmup: int = 20) -> None:
    import imageio.v2 as imageio

    frames_dir = config.ARTIFACTS_DIR / "frames_grid"
    frames_dir.mkdir(parents=True, exist_ok=True)
    for old in glob.glob(str(frames_dir / "*.png")):
        os.remove(old)

    model = PPO.load(model_path)
    env = make_grid_parallel_env(
        reward="queue_wait",
        use_gui=True,
        seed=config.SEED,
        num_seconds=(steps + warmup + 5) * config.GRID_ENV_CONFIG["delta_time"],
        additional_sumo_cmd=f"--gui-settings-file {config.GRID_VIEW_FILE}",
    )
    obs, _ = env.reset(seed=config.SEED)
    sumo = env.unwrapped.env.sumo  # the (gui) SUMO connection shared by all agents

    def agent_step():
        actions = {a: int(model.predict(obs[a], deterministic=True)[0]) for a in env.agents}
        return env.step(actions)

    # Warm-up so the first captured frame already has traffic.
    for _ in range(warmup):
        obs, _, _, _, _ = agent_step()
        if not env.agents:
            break

    saved = []
    for i in range(steps):
        frame_path = str(frames_dir / f"frame_{i:04d}.png")
        try:
            sumo.gui.screenshot(DEFAULT_VIEW, frame_path)  # written on next step
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] screenshot failed ({exc}); aborting GIF capture")
            break
        obs, _, _, _, _ = agent_step()
        if os.path.exists(frame_path):
            saved.append(frame_path)
        if not env.agents:
            break
    env.close()

    if not saved:
        print("[warn] no frames captured; GIF not created (needs a GUI session)")
        return

    images = [imageio.imread(p) for p in saved]
    imageio.mimsave(out_gif, images, fps=fps, loop=0)
    print(f"[ok] grid GIF ({len(images)} frames) -> {out_gif}")


def main() -> None:
    p = argparse.ArgumentParser(description="Record a GIF of the grid policy.")
    p.add_argument("--model", default=str(config.MODELS_DIR / "grid_ppo_v1.zip"))
    p.add_argument("--steps", type=int, default=180)
    p.add_argument("--warmup", type=int, default=20)
    p.add_argument("--out", default=str(config.PLOTS_DIR / "grid_demo.gif"))
    p.add_argument("--fps", type=int, default=12)
    args = p.parse_args()
    record(args.model, args.steps, args.out, args.fps, args.warmup)


if __name__ == "__main__":
    main()

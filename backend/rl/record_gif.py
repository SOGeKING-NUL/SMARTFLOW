"""Record a presentable GIF of the trained agent controlling the intersection.

Drives sumo-gui through traci and captures a screenshot each decision step, then
assembles the frames into a GIF. Uses sumo-gui (not libsumo), so it needs a
desktop/GUI session -- this is a demo/recording tool, not part of training.

For a polished result it loads:
  * the colourful demo traffic (cars/buses/trucks + red emergency vehicles), and
  * the demo view settings (real-world background, enlarged vehicles, framed on
    the junction) via --gui-settings-file.
A short warm-up runs before capturing so the roads are already full of traffic
in the first frame.

Usage (from backend/, project venv):
    python -m rl.record_gif --model results/dqn_v1.zip
    python -m rl.record_gif --model results/dqn_v1.zip --steps 180 --warmup 25 --fps 12
"""
from __future__ import annotations

import argparse
import os

# Must NOT use libsumo here: GUI screenshots require sumo-gui.
os.environ.pop("LIBSUMO_AS_TRACI", None)
os.environ["LIBSUMO_AS_TRACI"] = "0"

import glob

from . import config
from .env import make_env
from .policy import load_model

DEFAULT_VIEW = "View #0"


def record(
    model_path: str,
    steps: int,
    out_gif: str,
    fps: int = 12,
    warmup: int = 20,
    route_file: str | None = None,
    view_file: str | None = None,
) -> None:
    import imageio.v2 as imageio

    route_file = route_file or str(config.DEMO_ROUTE_FILE)
    view_file = view_file or str(config.DEMO_VIEW_FILE)

    frames_dir = config.ARTIFACTS_DIR / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    for old in glob.glob(str(frames_dir / "*.png")):
        os.remove(old)

    model = load_model(model_path)
    env = make_env(
        reward="queue_wait",
        use_gui=True,
        seed=config.SEED,
        route_file=route_file,
        num_seconds=(steps + warmup + 5) * config.ENV_CONFIG["delta_time"],
        additional_sumo_cmd=f"--gui-settings-file {view_file}",
    )
    obs, _ = env.reset()

    def agent_step():
        action, _ = model.predict(obs, deterministic=True)
        return env.step(int(action))

    # Warm-up: let traffic build up so the first captured frame isn't empty.
    for _ in range(warmup):
        obs, _, term, trunc, _ = agent_step()
        if term or trunc:
            break

    saved = []
    for i in range(steps):
        frame_path = str(frames_dir / f"frame_{i:04d}.png")
        try:
            env.sumo.gui.screenshot(DEFAULT_VIEW, frame_path)  # written on next step
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] screenshot failed ({exc}); aborting GIF capture")
            break
        obs, _, term, trunc, _ = agent_step()
        if os.path.exists(frame_path):
            saved.append(frame_path)
        if term or trunc:
            break
    env.close()

    if not saved:
        print("[warn] no frames captured; GIF not created (needs a GUI session)")
        return

    images = [imageio.imread(p) for p in saved]
    imageio.mimsave(out_gif, images, fps=fps, loop=0)
    print(f"[ok] GIF ({len(images)} frames) -> {out_gif}")


def main() -> None:
    p = argparse.ArgumentParser(description="Record a GIF of the trained agent.")
    p.add_argument("--model", default=str(config.MODELS_DIR / "dqn_v1.zip"))
    p.add_argument("--steps", type=int, default=160)
    p.add_argument("--warmup", type=int, default=20, help="decision steps to run before capturing")
    p.add_argument("--out", default=str(config.PLOTS_DIR / "agent_demo.gif"))
    p.add_argument("--fps", type=int, default=12)
    args = p.parse_args()
    record(args.model, args.steps, args.out, args.fps, args.warmup)


if __name__ == "__main__":
    main()

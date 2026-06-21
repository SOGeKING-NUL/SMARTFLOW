import Reveal from "./Reveal";
import BarChart from "./BarChart";
import { GRID_RESULTS, GRID_META, relImprovement } from "../data/results";

const RL = GRID_RESULTS[GRID_RESULTS.length - 1];

export default function GridResults() {
  const deltas = GRID_RESULTS.filter((r) => !r.isRL).map((ref) => ({
    name: ref.controller,
    pct: relImprovement(ref.avg_wait_s, RL.avg_wait_s, "lower"),
  }));

  return (
    <div className="mt-16 border-t border-rule pt-12">
      <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
        <h3 className="font-display text-2xl font-semibold text-ink">
          Scaling up — a 2×2 grid of four intersections
        </h3>
        <span className="microlabel">{GRID_META.policy} · n = {GRID_META.seeds.length} seeds</span>
      </div>
      <p className="mt-4 max-w-prose text-lg leading-relaxed text-graphite">
        A single shared-parameter PPO policy controls all four signals. It roughly
        halves waiting time versus fixed-time control and matches max-pressure —
        but on this scenario it does <strong className="text-ink">not</strong> beat
        SUMO&rsquo;s actuated controller. An honest result, and a useful one.
      </p>

      <div className="mt-8 grid gap-8 lg:grid-cols-[1.4fr_1fr]">
        <Reveal className="figure-frame p-6 md:p-8">
          <div className="mb-6 flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
            <h4 className="font-display text-lg font-semibold text-ink">Avg waiting time</h4>
            <span className="microlabel">Fig. 3 · 2×2 grid</span>
          </div>
          <BarChart
            metric="avg_wait_s"
            unit="s / veh"
            betterWhen="lower"
            data={GRID_RESULTS}
            errorBars={false}
          />
          <p className="mt-6 border-t border-rule pt-4 text-sm leading-relaxed text-graphite">
            Mean seconds each vehicle spends stopped across the four-intersection grid.
          </p>
        </Reveal>

        <Reveal className="flex flex-col gap-4">
          <span className="microlabel">RL agent vs. baseline (avg waiting time)</span>
          {deltas.map((d) => {
            const better = d.pct >= 0;
            return (
              <div key={d.name} className="figure-frame flex items-center justify-between px-5 py-4">
                <span className="text-sm text-graphite">{d.name}</span>
                <span className={`font-mono text-2xl font-bold ${better ? "text-go" : "text-stop"}`}>
                  {better ? "−" : "+"}
                  {Math.abs(d.pct).toFixed(1)}%
                </span>
              </div>
            );
          })}
          <p className="mt-1 text-sm leading-relaxed text-graphite">
            {GRID_META.note}
          </p>
        </Reveal>
      </div>

      {/* real trained-policy rollout */}
      <Reveal className="mt-8">
        <figure className="figure-frame overflow-hidden">
          <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1 border-b border-rule px-5 py-3">
            <span className="microlabel">Fig. 4 · trained-policy rollout</span>
            <span className="microlabel">SUMO · 2×2 grid</span>
          </div>
          <img
            src="/grid_demo.gif"
            alt="The trained shared-parameter PPO policy controlling the four signals of the 2x2 grid in SUMO."
            loading="lazy"
            className="w-full bg-sunken"
          />
        </figure>
      </Reveal>
    </div>
  );
}

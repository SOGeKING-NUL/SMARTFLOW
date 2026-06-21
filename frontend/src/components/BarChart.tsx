import { motion, useReducedMotion } from "framer-motion";
import { RESULTS, seedStats, type ControllerResult, type MetricKey } from "../data/results";

interface Props {
  metric: MetricKey;
  unit: string;
  betterWhen: "lower" | "higher";
  /** dataset to chart (defaults to the single-intersection results) */
  data?: ControllerResult[];
  /** show per-seed min–max whiskers (only the single intersection has seed data) */
  errorBars?: boolean;
}

/** Horizontal bar chart of one metric across all controllers, RL highlighted,
 *  with optional per-seed min–max error bars where seed-level data exists. */
export default function BarChart({ metric, unit, betterWhen, data = RESULTS, errorBars = true }: Props) {
  const reduce = useReducedMotion();
  const values = data.map((r) => r[metric]);
  const max = Math.max(...values);

  // For "throughput" the bars are near-identical; anchor the axis a little below
  // the min so the (small but real) differences stay visible without distorting.
  const min = Math.min(...values);
  const spread = max - min;
  const axisMin = spread / max < 0.05 ? min - spread * 1.4 : 0;
  const range = max - axisMin || 1;
  const toPct = (v: number) => ((v - axisMin) / range) * 100;

  const anyErrorBars = errorBars && data.some((r) => seedStats(r.controller, metric));

  return (
    <div role="img" aria-label={`${metric} by controller`} className="space-y-3">
      {data.map((r, i) => {
        const pct = toPct(r[metric]);
        const stats = errorBars ? seedStats(r.controller, metric) : null;
        return (
          <div key={r.controller} className="grid grid-cols-[7.5rem_1fr] items-center gap-3 sm:grid-cols-[9rem_1fr]">
            <div className="text-right">
              <span
                className={`text-sm ${r.isRL ? "font-semibold text-ink" : "text-graphite"}`}
              >
                {r.controller}
              </span>
            </div>
            <div className="relative h-9">
              <div className="absolute inset-0 rounded-sm bg-sunken" aria-hidden="true" />
              <motion.div
                className={`absolute inset-y-0 left-0 rounded-sm ${
                  r.isRL ? "bg-go" : "bg-graphite/55"
                }`}
                initial={reduce ? false : { width: 0 }}
                whileInView={reduce ? undefined : { width: `${pct}%` }}
                animate={reduce ? { width: `${pct}%` } : undefined}
                viewport={{ once: true, amount: 0.6 }}
                transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1], delay: i * 0.08 }}
                style={reduce ? { width: `${pct}%` } : undefined}
              />

              {/* per-seed min–max whisker */}
              {stats && stats.max > stats.min && (
                <motion.div
                  className="pointer-events-none absolute inset-y-0"
                  style={{ left: `${toPct(stats.min)}%`, width: `${toPct(stats.max) - toPct(stats.min)}%` }}
                  initial={reduce ? false : { opacity: 0 }}
                  whileInView={reduce ? undefined : { opacity: 1 }}
                  viewport={{ once: true, amount: 0.6 }}
                  transition={{ duration: 0.4, delay: 0.5 + i * 0.08 }}
                >
                  <div className="absolute top-1/2 h-px w-full -translate-y-1/2 bg-ink/70" />
                  <div className="absolute left-0 top-1/2 h-2.5 w-px -translate-y-1/2 bg-ink/70" />
                  <div className="absolute right-0 top-1/2 h-2.5 w-px -translate-y-1/2 bg-ink/70" />
                </motion.div>
              )}

              <span
                className={`absolute right-3 top-1/2 -translate-y-1/2 font-mono text-sm font-bold ${
                  r.isRL ? "text-white" : "text-ink"
                }`}
              >
                {r[metric].toLocaleString()}
              </span>
            </div>
          </div>
        );
      })}
      <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1 pt-1">
        <span className="microlabel">{unit}</span>
        <span className="microlabel">
          {anyErrorBars ? "│ min–max over 3 seeds · " : ""}
          {betterWhen === "lower" ? "↓ lower is better" : "↑ higher is better"}
        </span>
      </div>
    </div>
  );
}

// Real measured results, transcribed verbatim from the repository.
// Source: backend/results/comparison.csv  (mean over seeds 42, 7, 123)
// Produced by: backend/rl/evaluate.py  on the single-intersection SUMO scenario.
// DO NOT edit these by hand to "improve" them — they must match the repo.

export type MetricKey =
  | "avg_wait_s"
  | "avg_timeloss_s"
  | "avg_queue_veh"
  | "mean_speed_ms"
  | "throughput_veh";

export interface ControllerResult {
  controller: string;
  /** is this the learned RL policy (vs. a baseline)? */
  isRL: boolean;
  /** short note on what kind of controller this is */
  kind: "fixed" | "heuristic" | "learned";
  avg_wait_s: number;
  avg_timeloss_s: number;
  avg_queue_veh: number;
  mean_speed_ms: number;
  throughput_veh: number;
}

export const RESULTS: ControllerResult[] = [
  {
    controller: "Fixed-time",
    isRL: false,
    kind: "fixed",
    avg_wait_s: 11.37,
    avg_timeloss_s: 21.49,
    avg_queue_veh: 7.37,
    mean_speed_ms: 6.48,
    throughput_veh: 2048.67,
  },
  {
    controller: "Actuated",
    isRL: false,
    kind: "heuristic",
    avg_wait_s: 6.87,
    avg_timeloss_s: 16.39,
    avg_queue_veh: 4.55,
    mean_speed_ms: 7.41,
    throughput_veh: 2050,
  },
  {
    controller: "Max-pressure",
    isRL: false,
    kind: "heuristic",
    avg_wait_s: 5.28,
    avg_timeloss_s: 14.5,
    avg_queue_veh: 3.27,
    mean_speed_ms: 7.82,
    throughput_veh: 2050.67,
  },
  {
    controller: "RL (DQN)",
    isRL: true,
    kind: "learned",
    avg_wait_s: 5.14,
    avg_timeloss_s: 14.31,
    avg_queue_veh: 3.19,
    mean_speed_ms: 7.86,
    throughput_veh: 2054,
  },
];

export interface MetricMeta {
  key: MetricKey;
  label: string;
  unit: string;
  /** lower-is-better metrics get the delta sign flipped for "improvement" */
  betterWhen: "lower" | "higher";
  caption: string;
}

export const METRICS: MetricMeta[] = [
  {
    key: "avg_wait_s",
    label: "Avg waiting time",
    unit: "s / veh",
    betterWhen: "lower",
    caption: "Mean seconds each vehicle spends stopped (SUMO tripinfo).",
  },
  {
    key: "avg_queue_veh",
    label: "Avg queue length",
    unit: "veh",
    betterWhen: "lower",
    caption: "Time-averaged number of halted vehicles on the approaches.",
  },
  {
    key: "mean_speed_ms",
    label: "Mean speed",
    unit: "m / s",
    betterWhen: "higher",
    caption: "Time-averaged network speed across all vehicles.",
  },
  {
    key: "throughput_veh",
    label: "Throughput",
    unit: "veh",
    betterWhen: "higher",
    caption: "Vehicles that completed their trip in the hour (demand-saturated).",
  },
];

const fixed = RESULTS[0];
const rl = RESULTS[RESULTS.length - 1];

/** Percentage improvement of the RL agent over a reference controller. */
export function improvement(
  metric: MetricKey,
  betterWhen: "lower" | "higher",
  reference: ControllerResult = fixed
): number {
  const a = reference[metric];
  const b = rl[metric];
  const raw = betterWhen === "lower" ? (a - b) / a : (b - a) / a;
  return raw * 100;
}

// Pre-computed headline deltas (RL vs. fixed-time) — the honest hero numbers.
export const HEADLINE = {
  waitReductionVsFixed: Math.round(improvement("avg_wait_s", "lower")), // 55
  queueReductionVsFixed: Math.round(improvement("avg_queue_veh", "lower")), // 57
  speedGainVsFixed: Math.round(improvement("mean_speed_ms", "higher")), // 21
  waitReductionVsActuated: Math.round(
    improvement("avg_wait_s", "lower", RESULTS[1])
  ), // 25
  rlWait: rl.avg_wait_s, // 5.14
  fixedWait: fixed.avg_wait_s, // 11.37
};

export const EVAL_META = {
  seeds: [42, 7, 123],
  episodeSeconds: 3600,
  scenario: "Single 4-way intersection",
  simulator: "SUMO via sumo-rl",
  note: "Every controller runs the identical scenario and seeds; metrics come from SUMO tripinfo and time-averaged network state.",
};

// Per-seed values, parsed from backend/artifacts/logs/tripinfo_<ctrl>_<seed>.xml
// (seeds 42, 7, 123). Only tripinfo-derived metrics have per-seed records;
// avg_queue_veh / mean_speed_ms are time-averaged during the run and were only
// persisted as the 3-seed mean, so error bars are shown for the metrics below.
interface SeedSeries {
  wait: number[];
  timeloss: number[];
  throughput: number[];
}

export const PER_SEED: Record<string, SeedSeries> = {
  "Fixed-time": {
    wait: [11.387, 11.391, 11.329],
    timeloss: [21.529, 21.513, 21.425],
    throughput: [2049, 2049, 2048],
  },
  Actuated: {
    wait: [7.251, 6.72, 6.653],
    timeloss: [16.888, 16.059, 16.208],
    throughput: [2055, 2047, 2048],
  },
  "Max-pressure": {
    wait: [5.198, 5.481, 5.148],
    timeloss: [14.393, 14.794, 14.311],
    throughput: [2050, 2050, 2052],
  },
  "RL (DQN)": {
    wait: [5.164, 5.013, 5.24],
    timeloss: [14.338, 14.119, 14.483],
    throughput: [2056, 2051, 2055],
  },
};

const METRIC_TO_SEED_KEY: Partial<Record<MetricKey, keyof SeedSeries>> = {
  avg_wait_s: "wait",
  avg_timeloss_s: "timeloss",
  throughput_veh: "throughput",
};

/** Per-seed {mean,min,max} for a controller+metric, or null if not recorded. */
export function seedStats(
  controller: string,
  metric: MetricKey
): { mean: number; min: number; max: number } | null {
  const key = METRIC_TO_SEED_KEY[metric];
  const series = key && PER_SEED[controller]?.[key];
  if (!series || !series.length) return null;
  const mean = series.reduce((a, b) => a + b, 0) / series.length;
  return { mean, min: Math.min(...series), max: Math.max(...series) };
}

// Native learning curve, downsampled from backend/artifacts/logs/dqn_v1_monitor.csv
// (138 episodes over 100k steps). `mean` is a 10-episode rolling average.
export interface LearningPoint {
  step: number;
  reward: number;
  mean: number;
}

export const LEARNING_CURVE: LearningPoint[] = [
  { step: 720, reward: -12.43, mean: -12.43 },
  { step: 2880, reward: -10.74, mean: -11.86 },
  { step: 5040, reward: -11.67, mean: -12.05 },
  { step: 7200, reward: -11.52, mean: -11.82 },
  { step: 9360, reward: -10.13, mean: -11.32 },
  { step: 11520, reward: -10.83, mean: -10.84 },
  { step: 13680, reward: -9.85, mean: -10.51 },
  { step: 15840, reward: -9.46, mean: -10.05 },
  { step: 18000, reward: -9.1, mean: -9.81 },
  { step: 20160, reward: -9.37, mean: -9.58 },
  { step: 22320, reward: -9.0, mean: -9.45 },
  { step: 24480, reward: -8.58, mean: -9.13 },
  { step: 26640, reward: -9.53, mean: -8.86 },
  { step: 28800, reward: -8.97, mean: -8.68 },
  { step: 30960, reward: -7.78, mean: -8.54 },
  { step: 33120, reward: -8.51, mean: -8.5 },
  { step: 35280, reward: -7.87, mean: -8.3 },
  { step: 37440, reward: -8.18, mean: -8.22 },
  { step: 39600, reward: -7.61, mean: -8.09 },
  { step: 41760, reward: -7.81, mean: -7.92 },
  { step: 43920, reward: -8.07, mean: -7.93 },
  { step: 46080, reward: -7.82, mean: -7.87 },
  { step: 48240, reward: -8.17, mean: -7.94 },
  { step: 50400, reward: -8.06, mean: -7.9 },
  { step: 52560, reward: -7.9, mean: -8.17 },
  { step: 54720, reward: -7.64, mean: -8.14 },
  { step: 56880, reward: -7.75, mean: -8.08 },
  { step: 59040, reward: -7.73, mean: -7.78 },
  { step: 61200, reward: -8.01, mean: -7.7 },
  { step: 63360, reward: -7.63, mean: -7.69 },
  { step: 65520, reward: -7.54, mean: -7.66 },
  { step: 67680, reward: -7.78, mean: -7.73 },
  { step: 69840, reward: -8.03, mean: -7.75 },
  { step: 72000, reward: -8.11, mean: -7.8 },
  { step: 74160, reward: -7.72, mean: -7.82 },
  { step: 76320, reward: -7.91, mean: -7.86 },
  { step: 78480, reward: -7.75, mean: -7.82 },
  { step: 80640, reward: -7.56, mean: -7.74 },
  { step: 82800, reward: -7.99, mean: -7.73 },
  { step: 84960, reward: -7.82, mean: -7.76 },
  { step: 87120, reward: -7.69, mean: -7.73 },
  { step: 89280, reward: -7.72, mean: -7.75 },
  { step: 91440, reward: -7.5, mean: -7.7 },
  { step: 93600, reward: -7.92, mean: -7.8 },
  { step: 95760, reward: -7.54, mean: -7.73 },
  { step: 97920, reward: -8.04, mean: -7.71 },
  { step: 99360, reward: -7.78, mean: -7.71 },
];

// --------------------------------------------------------------------------- //
// Multi-intersection: 2x2 grid (4 intersections), one shared-parameter PPO
// policy. Source: backend/results/grid_comparison.csv (3-seed mean, 42/7/123).
// No per-seed data was persisted for the grid, so its chart shows means only
// (no error bars). On this scenario the policy matches max-pressure and roughly
// halves waiting vs fixed-time, but does NOT beat SUMO's actuated controller.
// --------------------------------------------------------------------------- //
export const GRID_RESULTS: ControllerResult[] = [
  {
    controller: "Fixed-time",
    isRL: false,
    kind: "fixed",
    avg_wait_s: 20.42,
    avg_timeloss_s: 38.21,
    avg_queue_veh: 16.02,
    mean_speed_ms: 6.78,
    throughput_veh: 2505.33,
  },
  {
    controller: "Actuated",
    isRL: false,
    kind: "heuristic",
    avg_wait_s: 9.94,
    avg_timeloss_s: 26.35,
    avg_queue_veh: 7.71,
    mean_speed_ms: 8.05,
    throughput_veh: 2507.67,
  },
  {
    controller: "Max-pressure",
    isRL: false,
    kind: "heuristic",
    avg_wait_s: 11.14,
    avg_timeloss_s: 27.43,
    avg_queue_veh: 7.66,
    mean_speed_ms: 7.98,
    throughput_veh: 2508.33,
  },
  {
    controller: "RL (PPO, shared)",
    isRL: true,
    kind: "learned",
    avg_wait_s: 11.08,
    avg_timeloss_s: 26.78,
    avg_queue_veh: 7.65,
    mean_speed_ms: 8.05,
    throughput_veh: 2508.67,
  },
];

const gridFixed = GRID_RESULTS[0];
const gridRl = GRID_RESULTS[GRID_RESULTS.length - 1];

export const GRID_META = {
  intersections: 4,
  seeds: [42, 7, 123],
  policy: "Shared-parameter PPO",
  // (20.42 - 11.08) / 20.42
  waitReductionVsFixed: Math.round(((gridFixed.avg_wait_s - gridRl.avg_wait_s) / gridFixed.avg_wait_s) * 100),
  rlWait: gridRl.avg_wait_s,
  fixedWait: gridFixed.avg_wait_s,
  actuatedWait: GRID_RESULTS[1].avg_wait_s,
  note: "One shared policy controls all four intersections. Demand is uniformly random, with no sustained directional platoons — the regime where coordinated green-waves would let learning pull ahead.",
};

/** Signed % improvement of value `b` over reference `a` for a metric. */
export function relImprovement(a: number, b: number, betterWhen: "lower" | "higher"): number {
  const raw = betterWhen === "lower" ? (a - b) / a : (b - a) / a;
  return raw * 100;
}

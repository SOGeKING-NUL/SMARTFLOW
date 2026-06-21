// Site copy + technical facts, all sourced from the repository
// (backend/rl/config.py, env.py, rewards.py, train.py, api/*).
// SmartFlow is a group project; the site is written in a neutral, team voice
// and describes the project, not individual contributions.

export const LINKS = {
  github: "https://github.com/Karush2807/SMARTFLOW", // TODO: confirm canonical repo URL
};

export const META = {
  version: "v1.0",
  year: "2025",
  kind: "Group project · applied study",
};

export const HERO = {
  kicker: "Reinforcement learning · SUMO · signal control",
  headline: "A traffic light that learns to clear the queue.",
  sub: "An RL agent observes lane-level demand at an intersection and chooses the next green phase — trained in the SUMO traffic simulator and benchmarked against fixed-time, actuated, and max-pressure control.",
};

// Abstract — written in the voice of a short applied-research report.
export const ABSTRACT =
  "We frame isolated traffic-signal control as a Markov decision process and train a deep reinforcement-learning agent (DQN) in the SUMO microsimulator to select signal phases from live, lane-level demand. On a single four-way intersection under a one-hour demand profile, the learned policy lowers average vehicle waiting time by ~55% versus a fixed-time controller and ~25% versus an actuated controller, and matches the strongest classical heuristic (max-pressure) — evaluated over three random seeds on an identical scenario. We describe the formulation, a custom reward, the benchmark against three baselines, and the limitations of the study.";

export const CONTRIBUTIONS = [
  "Formulate isolated signal control as a 19-dimensional MDP — phase, min-green flag, and per-lane density and queue — with a discrete phase-selection action.",
  "Design queue_wait, a dense, bounded reward that combines waiting-time improvement with a standing-queue penalty (Eq. 1).",
  "Train DQN and PPO agents with Stable-Baselines3 in the SUMO / sumo-rl environment.",
  "Benchmark the learned policy against fixed-time, actuated, and max-pressure baselines over three seeds on an identical scenario.",
];

// Verified references — each maps to a method, tool, or baseline actually used.
export interface Reference {
  n: number;
  authors: string;
  year: string;
  title: string;
  venue: string;
  url: string;
  /** what in this project it grounds */
  role: string;
}

export const REFERENCES: Reference[] = [
  {
    n: 1,
    authors: "Mnih et al.",
    year: "2015",
    title: "Human-level control through deep reinforcement learning",
    venue: "Nature 518:529–533",
    url: "https://www.nature.com/articles/nature14236",
    role: "DQN — the agent",
  },
  {
    n: 2,
    authors: "Schulman et al.",
    year: "2017",
    title: "Proximal Policy Optimization Algorithms",
    venue: "arXiv:1707.06347",
    url: "https://arxiv.org/abs/1707.06347",
    role: "PPO — alternative agent",
  },
  {
    n: 3,
    authors: "Lopez et al.",
    year: "2018",
    title: "Microscopic Traffic Simulation using SUMO",
    venue: "IEEE ITSC, 2575–2582",
    url: "https://doi.org/10.1109/ITSC.2018.8569938",
    role: "Simulator",
  },
  {
    n: 4,
    authors: "Alegre",
    year: "2019",
    title: "SUMO-RL",
    venue: "Open-source library",
    url: "https://github.com/LucasAlegre/sumo-rl",
    role: "RL environment wrapper",
  },
  {
    n: 5,
    authors: "Raffin et al.",
    year: "2021",
    title: "Stable-Baselines3: Reliable Reinforcement Learning Implementations",
    venue: "JMLR 22(268)",
    url: "https://jmlr.org/papers/v22/20-1364.html",
    role: "Training framework",
  },
  {
    n: 6,
    authors: "Varaiya",
    year: "2013",
    title: "Max pressure control of a network of signalized intersections",
    venue: "Transportation Research Part C 36:177–195",
    url: "https://www.sciencedirect.com/science/article/abs/pii/S0968090X13001782",
    role: "Strongest baseline",
  },
  {
    n: 7,
    authors: "Wei et al.",
    year: "2018",
    title: "IntelliLight: A Reinforcement Learning Approach for Intelligent Traffic Light Control",
    venue: "ACM SIGKDD, 2496–2505",
    url: "https://www.kdd.org/kdd2018/accepted-papers/view/intellilight-a-reinforcement-learning-approach-for-intelligent-traffic-ligh",
    role: "Field context — first DQN for signals",
  },
  {
    n: 8,
    authors: "Wei et al.",
    year: "2019",
    title: "PressLight: Learning Max Pressure Control to Coordinate Traffic Signals in Arterial Network",
    venue: "ACM SIGKDD, 1290–1298",
    url: "https://www.kdd.org/kdd2019/accepted-papers/view/presslight-learning-max-pressure-control-for-signalized-intersections-in-ar",
    role: "Field context — RL meets max-pressure",
  },
  {
    n: 9,
    authors: "Wei et al.",
    year: "2021",
    title: "Recent Advances in Reinforcement Learning for Traffic Signal Control: A Survey of Models and Evaluation",
    venue: "ACM SIGKDD Explorations 22(2)",
    url: "https://dl.acm.org/doi/10.1145/3447556.3447565",
    role: "Survey",
  },
];

// --- The MDP, straight from backend/rl/env.py + rewards.py + config.py ---
export const MDP = {
  state: {
    title: "State",
    dims: 19,
    summary: "What the agent sees at each decision",
    items: [
      "Current phase, one-hot (2)",
      "Min-green-elapsed flag (1)",
      "Per-lane density, 8 lanes (8)",
      "Per-lane queue ratio, 8 lanes (8)",
    ],
    note: "All values normalised to [0, 1] — the same vector the live API consumes.",
  },
  action: {
    title: "Action",
    dims: 2,
    summary: "What the agent decides",
    items: ["Activate NS-green next", "Activate EW-green next"],
    note: "sumo-rl inserts the yellow transition and enforces min/max-green, so every action is physically valid.",
  },
  reward: {
    title: "Reward",
    summary: "What the agent optimises",
    formula: "rₜ = (Wₜ₋₁ − Wₜ) − α · mean_queueₜ",
    items: [
      "(Wₜ₋₁ − Wₜ): responsive — positive when the last action reduced delay",
      "mean_queueₜ ∈ [0,1]: dense, bounded penalty on standing queues",
      "α = 0.5 balances clearing delay against starving an approach",
    ],
    note: "A custom reward chosen over the sparse built-in diff-waiting-time for stabler value learning.",
  },
};

export const ENV_CONFIG = [
  { label: "Decision interval", value: "5 s" },
  { label: "Yellow time", value: "3 s" },
  { label: "Min green", value: "10 s" },
  { label: "Max green", value: "60 s" },
  { label: "Episode length", value: "3600 s" },
  { label: "Incoming lanes", value: "8" },
];

export const TRAINING = [
  { label: "Algorithm", value: "DQN (Stable-Baselines3)" },
  { label: "Training steps", value: "100,000" },
  { label: "Network", value: "MLP [128, 128]" },
  { label: "Discount γ", value: "0.95" },
  { label: "Exploration", value: "ε 1.0 → 0.02" },
  { label: "Seed", value: "42 (reproducible)" },
];

// --- Architecture: state → agent → SUMO → reward → API ---
export const ARCHITECTURE = [
  {
    id: "state",
    title: "Traffic state",
    detail: "Per-lane density + queue + phase, normalised to a 19-dim vector.",
  },
  {
    id: "agent",
    title: "RL agent",
    detail: "DQN policy maps the state to a green-phase decision (NS / EW).",
  },
  {
    id: "sumo",
    title: "SUMO env",
    detail: "sumo-rl switches the physical signal phase; the simulation advances.",
  },
  {
    id: "reward",
    title: "Reward",
    detail: "queue_wait scores the outcome and feeds back to training.",
  },
  {
    id: "api",
    title: "FastAPI",
    detail: "/predict, /simulate, /metrics serve the trained policy over HTTP.",
  },
];

// --- System components (neutral, project-level; no per-person attribution) ---
export interface Component {
  area: string;
  tag: string;
  items: string[];
}

export const COMPONENTS: Component[] = [
  {
    area: "RL model & environment",
    tag: "Reinforcement learning",
    items: ["SUMO MDP design", "Custom queue_wait reward", "DQN / PPO training"],
  },
  {
    area: "Baselines & evaluation",
    tag: "Benchmarking",
    items: ["Fixed-time · actuated · max-pressure", "Seeded SUMO benchmark harness"],
  },
  {
    area: "Backend API",
    tag: "Backend",
    items: ["FastAPI service", "Pydantic-validated /predict · /simulate · /metrics"],
  },
  {
    area: "Emergency preemption",
    tag: "Control",
    items: ["RFID-triggered green priority", "Validated in the SUMO digital twin"],
  },
  {
    area: "Computer vision",
    tag: "Vision",
    items: ["YOLOv8 vehicle detection & counting", "Feeds per-lane demand to the controller"],
  },
  {
    area: "Hardware",
    tag: "Embedded",
    items: ["ESP32 + RFID reader/writer firmware", "Tagged-vehicle detection"],
  },
  {
    area: "Mobile app",
    tag: "Client",
    items: ["Expo / React Native dashboard"],
  },
];

export const STACK = [
  "Python",
  "PyTorch",
  "Stable-Baselines3",
  "Gymnasium",
  "SUMO / sumo-rl",
  "FastAPI",
  "Pydantic",
  "NumPy",
  "React",
  "TypeScript",
  "Vite",
  "Tailwind",
];

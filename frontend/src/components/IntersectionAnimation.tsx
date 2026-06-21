import { useEffect, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";

type Phase = "NS" | "NS_Y" | "EW" | "EW_Y";
const NEXT: Record<Phase, Phase> = { NS: "NS_Y", NS_Y: "EW", EW: "EW_Y", EW_Y: "NS" };
const DURATION: Record<Phase, number> = { NS: 3000, NS_Y: 800, EW: 3000, EW_Y: 800 };

// Emergency-vehicle preemption along the top corridor.
const EV_GAP = 5000;
const EV_DUR = 2800;

const GO = "#157F5B";
const AMBER = "#E08A00";
const STOP = "#C2453C";
const RULE = "#C9C2B2";
const INK = "#14171A";
const ROAD = "#E4DDCC";
const GRAPHITE = "#4A5058";

// 2x2 grid geometry
const XS = [150, 290]; // vertical road centres
const YS = [150, 290]; // horizontal road centres
const HALF = 18; // road half-width
const LANE = 8; // lane offset from centreline
const NODES = [
  { x: 150, y: 150 },
  { x: 290, y: 150 },
  { x: 150, y: 290 },
  { x: 290, y: 290 },
];

/** Moving vehicles along one green lane (rendered only while active). */
function FlowLane({
  vertical,
  pos,
  from,
  to,
  active,
  n = 2,
}: {
  vertical: boolean;
  pos: number;
  from: number;
  to: number;
  active: boolean;
  n?: number;
}) {
  if (!active) return null;
  const dur = 2.6;
  return (
    <g>
      {Array.from({ length: n }).map((_, i) => {
        const box = { width: vertical ? 9 : 14, height: vertical ? 14 : 9, rx: 2, fill: GRAPHITE };
        const t = { repeat: Infinity, ease: "linear" as const, duration: dur, delay: (i * dur) / n };
        return vertical ? (
          <motion.rect key={i} x={pos - 4.5} initial={{ y: from }} animate={{ y: [from, to] }} transition={t} {...box} />
        ) : (
          <motion.rect key={i} y={pos - 4.5} initial={{ x: from }} animate={{ x: [from, to] }} transition={t} {...box} />
        );
      })}
    </g>
  );
}

/** A short stationary queue near a stop line on a red corridor. */
function Queue({ x, y, dx, dy, show }: { x: number; y: number; dx: number; dy: number; show: boolean }) {
  return (
    <g>
      {[0, 1, 2].map((i) => (
        <motion.rect
          key={i}
          x={x + dx * i - 4}
          y={y + dy * i - 4}
          width={8}
          height={8}
          rx={1.5}
          fill={GRAPHITE}
          initial={false}
          animate={{ opacity: show ? 0.85 : 0 }}
          transition={{ duration: 0.35, delay: show ? i * 0.05 : 0 }}
        />
      ))}
    </g>
  );
}

/** Emergency vehicle crossing the top corridor (eastbound), with siren + halo. */
function EmergencyVehicle({ id }: { id: number }) {
  const pulse = { repeat: Infinity, duration: 0.5, ease: "easeInOut" as const };
  const halo = { repeat: Infinity, duration: 1, ease: "easeOut" as const };
  return (
    <motion.g key={id} initial={{ x: -40 }} animate={{ x: 480 }} transition={{ duration: EV_DUR / 1000, ease: "linear" }}>
      <g transform="translate(0,157)">
        <motion.circle cx={0} cy={0} r={8} fill="none" stroke={STOP} strokeWidth={1.5}
          initial={{ r: 7, opacity: 0.5 }} animate={{ r: 15, opacity: 0 }} transition={halo} />
        <rect x={-9} y={-6} width={18} height={12} rx={2.5} fill={STOP} />
        <rect x={-9} y={-6} width={5} height={12} rx={1.5} fill="#fff" opacity={0.9} />
        <motion.circle cx={-6} cy={0} r={2} fill="#fff" animate={{ opacity: [1, 0.2, 1] }} transition={pulse} />
      </g>
    </motion.g>
  );
}

export default function IntersectionAnimation() {
  const reduce = useReducedMotion();
  const [phase, setPhase] = useState<Phase>("NS");
  const [ev, setEv] = useState<number | null>(null);

  useEffect(() => {
    if (reduce) return;
    const t = setTimeout(() => setPhase((p) => NEXT[p]), DURATION[phase]);
    return () => clearTimeout(t);
  }, [phase, reduce]);

  useEffect(() => {
    if (reduce) return;
    let n = 0;
    let on: number;
    let off: number;
    const loop = () => {
      on = window.setTimeout(() => {
        n += 1;
        setEv(n);
        off = window.setTimeout(() => {
          setEv(null);
          loop();
        }, EV_DUR);
      }, EV_GAP);
    };
    loop();
    return () => {
      clearTimeout(on);
      clearTimeout(off);
    };
  }, [reduce]);

  const emActive = ev !== null;
  const nsGreen = emActive ? false : phase === "NS";
  const ewGreen = emActive ? true : phase === "EW"; // EV preempts the EW corridor
  const nsYellow = !emActive && phase === "NS_Y";
  const ewYellow = !emActive && phase === "EW_Y";

  const lamp = (axisGreen: boolean, axisYellow: boolean) =>
    axisGreen ? GO : axisYellow ? AMBER : STOP;
  const nsLamp = lamp(nsGreen, nsYellow);
  const ewLamp = lamp(ewGreen, ewYellow);

  const label = emActive
    ? "PRIORITY · EW PREEMPT"
    : nsGreen
    ? "N–S · GREEN"
    : ewGreen
    ? "E–W · GREEN"
    : "TRANSITION";

  return (
    <figure
      className="relative"
      aria-label="Animated 2x2 grid of four intersections: one shared policy coordinates the signals and preempts the corridor for an emergency vehicle."
    >
      <svg viewBox="0 0 440 440" className="w-full" role="img">
        {/* blueprint frame ticks */}
        <g stroke={RULE} strokeWidth="1">
          <line x1="22" y1="22" x2="42" y2="22" />
          <line x1="22" y1="22" x2="22" y2="42" />
          <line x1="418" y1="418" x2="398" y2="418" />
          <line x1="418" y1="418" x2="418" y2="398" />
        </g>

        {/* roads (base) */}
        {XS.map((x) => (
          <rect key={`vx${x}`} x={x - HALF} y={0} width={HALF * 2} height={440} fill={ROAD} />
        ))}
        {YS.map((y) => (
          <rect key={`hy${y}`} x={0} y={y - HALF} width={440} height={HALF * 2} fill={ROAD} />
        ))}
        {/* active-corridor tint: green where the axis has the green */}
        {XS.map((x) => (
          <motion.rect key={`vt${x}`} x={x - HALF} y={0} width={HALF * 2} height={440} fill={GO}
            initial={false} animate={{ opacity: nsGreen ? 0.13 : 0 }} transition={{ duration: 0.4 }} />
        ))}
        {YS.map((y) => (
          <motion.rect key={`ht${y}`} x={0} y={y - HALF} width={440} height={HALF * 2} fill={GO}
            initial={false} animate={{ opacity: ewGreen ? 0.13 : 0 }} transition={{ duration: 0.4 }} />
        ))}
        {/* road edges for crisp definition */}
        {XS.map((x) => (
          <g key={`ve${x}`} stroke={RULE} strokeWidth="1">
            <line x1={x - HALF} y1={0} x2={x - HALF} y2={440} />
            <line x1={x + HALF} y1={0} x2={x + HALF} y2={440} />
          </g>
        ))}
        {YS.map((y) => (
          <g key={`he${y}`} stroke={RULE} strokeWidth="1">
            <line x1={0} y1={y - HALF} x2={440} y2={y - HALF} />
            <line x1={0} y1={y + HALF} x2={440} y2={y + HALF} />
          </g>
        ))}
        {/* centre lines */}
        {XS.map((x) => (
          <line key={`vc${x}`} x1={x} y1={0} x2={x} y2={440} stroke={RULE} strokeWidth="1" strokeDasharray="4 8" />
        ))}
        {YS.map((y) => (
          <line key={`hc${y}`} x1={0} y1={y} x2={440} y2={y} stroke={RULE} strokeWidth="1" strokeDasharray="4 8" />
        ))}
        {/* intersection boxes (mask the edge lines crossing the junction) */}
        {NODES.map((nd, i) => (
          <rect key={i} x={nd.x - HALF} y={nd.y - HALF} width={HALF * 2} height={HALF * 2} fill={ROAD} stroke={INK} strokeWidth="1" strokeOpacity="0.15" />
        ))}

        {/* flowing vehicles on the green axis */}
        {!reduce && (
          <>
            {XS.map((x) => (
              <g key={`vf${x}`}>
                <FlowLane vertical pos={x - LANE} from={-20} to={460} active={nsGreen} />
                <FlowLane vertical pos={x + LANE} from={460} to={-20} active={nsGreen} />
              </g>
            ))}
            {YS.map((y) => (
              <g key={`hf${y}`}>
                <FlowLane vertical={false} pos={y + LANE} from={-20} to={460} active={ewGreen} />
                <FlowLane vertical={false} pos={y - LANE} from={460} to={-20} active={ewGreen} />
              </g>
            ))}
          </>
        )}

        {/* short queues on the red corridors (one per vertical / horizontal road) */}
        {XS.map((x) => (
          <Queue key={`vq${x}`} x={x - LANE} y={YS[0] - HALF - 8} dx={0} dy={-11} show={!nsGreen} />
        ))}
        {YS.map((y) => (
          <Queue key={`hq${y}`} x={XS[0] - HALF - 8} y={y - LANE} dx={-11} dy={0} show={!ewGreen} />
        ))}

        {/* emergency vehicle on the top corridor */}
        {emActive && !reduce && <EmergencyVehicle id={ev!} />}

        {/* per-intersection signal lamps (NS + EW) */}
        {NODES.map((nd, i) => (
          <g key={i}>
            <circle cx={nd.x - 12} cy={nd.y - 12} r={3.6} fill={nsLamp} stroke={INK} strokeWidth={1} />
            <circle cx={nd.x + 12} cy={nd.y + 12} r={3.6} fill={ewLamp} stroke={INK} strokeWidth={1} />
          </g>
        ))}
      </svg>

      <figcaption className="mt-4 border-t border-rule pt-3">
        <div className="flex items-center justify-between">
          <span className="microlabel">2×2 grid · live phase</span>
          <span className={`font-mono text-xs font-bold tracking-widest ${emActive ? "text-stop" : "text-ink"}`}>
            {label}
          </span>
        </div>
        <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1.5">
          <Legend color={GO} label="green / flow" />
          <Legend color={GRAPHITE} label="queue" />
          <Legend color={STOP} label="priority vehicle" />
        </div>
      </figcaption>
    </figure>
  );
}

function Legend({ color, label }: { color: string; label: string }) {
  return (
    <span className="flex items-center gap-1.5 font-mono text-[0.625rem] uppercase tracking-wider text-graphite">
      <span className="h-2 w-2 rounded-sm" style={{ background: color }} aria-hidden="true" />
      {label}
    </span>
  );
}
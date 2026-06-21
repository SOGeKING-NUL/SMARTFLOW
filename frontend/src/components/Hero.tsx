import { motion, useReducedMotion } from "framer-motion";
import { ArrowDown, Github } from "lucide-react";
import { HERO, LINKS, META } from "../data/content";
import { HEADLINE } from "../data/results";
import IntersectionAnimation from "./IntersectionAnimation";

// The hero is the LCP block, so its entrance is a pure-CSS animation
// (Tailwind `animate-fade-up`) rather than a JS-driven one — it always ends
// visible regardless of load timing, and the reduced-motion media query in
// index.css neutralises it. Framer is reserved for the live signal animation.
export default function Hero() {
  const reduce = useReducedMotion();

  return (
    <section
      id="top"
      aria-labelledby="hero-title"
      className="mx-auto flex max-w-page flex-col gap-12 px-6 pb-20 pt-16 md:grid md:grid-cols-[1.15fr_0.85fr] md:items-center md:gap-16 md:px-10 md:pb-28 md:pt-24"
    >
      <div className="min-w-0 animate-fade-up">
        <p className="font-mono text-micro uppercase tracking-[0.14em] text-muted">
          {META.kind} · {META.version} · {META.year}
        </p>
        <p className="microlabel mt-2">{HERO.kicker}</p>

        <h1
          id="hero-title"
          className="mt-6 font-display text-display-sm font-semibold leading-[1.0] tracking-tight text-ink sm:text-display-md sm:leading-[0.98] md:text-display-lg"
        >
          {HERO.headline}
        </h1>

        <p className="mt-7 max-w-prose text-lg leading-relaxed text-graphite">
          {HERO.sub}
        </p>

        {/* Strongest real result */}
        <div className="mt-9 flex flex-wrap items-end gap-x-8 gap-y-4 border-t border-rule pt-7">
          <div>
            <span className="font-display text-5xl font-semibold tracking-tight text-go-deep">
              −{HEADLINE.waitReductionVsFixed}%
            </span>
            <p className="mt-1 max-w-[22ch] text-sm text-graphite">
              average vehicle waiting time vs. a fixed-time controller
            </p>
          </div>
          <div className="font-mono text-sm text-graphite">
            <span className="text-ink">{HEADLINE.rlWait}s</span> RL
            <span className="px-2 text-rule">/</span>
            <span>{HEADLINE.fixedWait}s</span> fixed-time
          </div>
        </div>

        <div className="mt-9 flex flex-wrap gap-3">
          <a
            href="#results"
            className="inline-flex items-center gap-2 rounded bg-go px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-go-deep"
          >
            View the results
          </a>
          <a
            href={LINKS.github}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 rounded border border-ink px-5 py-3 text-sm font-semibold text-ink transition-colors hover:bg-ink hover:text-paper"
          >
            <Github className="h-4 w-4" aria-hidden="true" />
            GitHub
          </a>
        </div>
      </div>

      {/* Domain hero animation */}
      <div
        className="figure-frame relative min-w-0 animate-fade-up p-5 md:p-7"
        style={reduce ? undefined : { animationDelay: "0.12s" }}
      >
        <div className="mb-3 flex flex-wrap items-center justify-between gap-x-3 gap-y-1">
          <span className="microlabel">Fig. 0 — 2×2 intersection grid</span>
          <span className="microlabel text-go-deep">agent-controlled</span>
        </div>
        <IntersectionAnimation />
      </div>

      {/* scroll cue */}
      {!reduce && (
        <motion.a
          href="#approach"
          aria-label="Scroll to approach"
          className="mx-auto hidden text-graphite md:col-span-2 md:block"
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 1.8, repeat: Infinity, ease: "easeInOut" }}
        >
          <ArrowDown className="h-5 w-5" />
        </motion.a>
      )}
    </section>
  );
}

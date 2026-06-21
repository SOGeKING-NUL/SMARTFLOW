import Reveal from "./Reveal";
import { REFERENCES } from "../data/content";

export default function References() {
  return (
    <section
      id="references"
      aria-labelledby="references-title"
      className="mx-auto w-full max-w-page px-6 py-20 md:px-10 md:py-28"
    >
      <Reveal>
        <header className="border-t border-rule pt-6">
          <span className="microlabel">References</span>
          <h2
            id="references-title"
            className="mt-5 max-w-3xl font-display text-3xl font-semibold tracking-tight text-ink sm:text-4xl md:text-display-sm"
          >
            The methods, tools, and baselines this builds on.
          </h2>
          <p className="mt-5 max-w-prose text-lg leading-relaxed text-graphite">
            Each reference grounds something used in the project — the agent, the
            simulator, the training library, or the baseline being compared against.
          </p>
        </header>
      </Reveal>

      <Reveal className="mt-12">
        <ol className="space-y-px overflow-hidden rounded-md border border-rule">
          {REFERENCES.map((r) => (
            <li
              key={r.n}
              id={`ref-${r.n}`}
              className="grid grid-cols-[2rem_1fr] gap-3 bg-surface px-5 py-4 scroll-mt-24 sm:grid-cols-[2.5rem_1fr]"
            >
              <span className="font-mono text-sm text-go-deep">[{r.n}]</span>
              <div>
                <p className="text-sm leading-relaxed text-ink">
                  <span className="font-medium">{r.authors}</span>{" "}
                  <span className="text-graphite">({r.year}).</span>{" "}
                  <a
                    href={r.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline decoration-rule underline-offset-2 transition-colors hover:decoration-go hover:text-go-deep"
                  >
                    {r.title}
                  </a>
                  . <span className="italic text-graphite">{r.venue}.</span>
                </p>
                <span className="mt-1 inline-block font-mono text-xs text-muted">
                  {r.role}
                </span>
              </div>
            </li>
          ))}
        </ol>
      </Reveal>
    </section>
  );
}

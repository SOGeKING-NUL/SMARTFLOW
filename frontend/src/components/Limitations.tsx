import Section from "./Section";
import Reveal from "./Reveal";

const LIMITATIONS = [
  {
    title: "Simulation, not the street",
    body: "Both scenarios run in SUMO over a one-hour demand profile, with demand randomised via randomTrips rather than drawn from a measured dataset — so absolute figures are scenario-specific.",
  },
  {
    title: "Competitive, not dominant",
    body: "On the single intersection the policy beats all three baselines; on the 2×2 grid it matches max-pressure and beats fixed-time (~46%) but does not beat SUMO's actuated controller.",
  },
  {
    title: "Demand isn't coordination-favorable",
    body: "The grid uses uniformly random demand with no sustained directional platoons — the regime where coordinated green-waves would let a learned policy pull ahead of local heuristics.",
  },
  {
    title: "Preemption is a validated capability, not a headline number",
    body: "Emergency-vehicle preemption is implemented and validated in the digital twin; on the tested seed the emergency vehicle was already unobstructed, so no delay reduction is claimed.",
  },
];

export default function Limitations() {
  return (
    <Section
      id="limitations"
      index="§4"
      label="Limitations"
      title="What these numbers do and don't claim."
      intro="Stating the boundaries of the study plainly — a fair, seeded benchmark on a single intersection and a 2×2 grid, not a deployment claim."
    >
      <div className="grid gap-5 md:grid-cols-2">
        {LIMITATIONS.map((l) => (
          <Reveal asChild key={l.title} className="figure-frame border-l-2 border-l-amber p-6">
            <h3 className="font-display text-lg font-semibold text-ink">{l.title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-graphite">{l.body}</p>
          </Reveal>
        ))}
      </div>
    </Section>
  );
}

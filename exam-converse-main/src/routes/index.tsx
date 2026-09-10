import { createFileRoute } from "@tanstack/react-router";

import { Arrow, Badge, ButtonLink, Card, Check, Metric, SectionHeader } from "@/components/kit";
import { Footer, MarketingNav } from "@/components/site";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "ExaminerAI — Practice like you're facing a real examiner" },
      {
        name: "description",
        content:
          "ExaminerAI is a conversational AI examiner. It asks, listens, evaluates your reasoning, probes deeper and adapts the examination to what you actually understand.",
      },
      { property: "og:title", content: "ExaminerAI — Practice like you're facing a real examiner" },
      {
        property: "og:description",
        content: "A conversational AI examiner that evaluates how you think and adapts to your performance.",
      },
    ],
  }),
  component: Home,
});

function Home() {
  return (
    <>
      <div className="bg-ink-950">
        <MarketingNav />
        <Hero />
      </div>
      <TrustMetrics />
      <Features />
      <HowItWorks />
      <Educators />
      <Pricing />
      <FinalCTA />
      <Footer />
    </>
  );
}

/* --------------------------------- Hero --------------------------------- */

function Hero() {
  return (
    <section className="relative overflow-hidden">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -top-40 right-[-10%] h-[520px] w-[520px] rounded-full"
        style={{ background: "radial-gradient(circle, rgba(88,101,242,0.22), transparent 65%)" }}
      />
      <div className="container-page relative grid gap-14 pt-14 pb-24 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.05fr)] lg:items-center lg:gap-16 lg:pt-20 lg:pb-28">
        <div className="rise">
          <p className="eyebrow text-white/45">AI-powered assessment for real understanding</p>
          <h1 className="mt-6 font-display text-[2.75rem] leading-[1.06] tracking-tight text-white sm:text-[3.5rem] lg:text-[4rem]">
            Practice like you're facing a{" "}
            <em className="not-italic" style={{ color: "var(--violet-500)" }}>
              <span className="italic">real examiner</span>
            </em>
            .
          </h1>
          <p className="mt-6 max-w-lg text-[0.9375rem] leading-relaxed text-white/60">
            ExaminerAI evaluates how you think, detects what you don't understand, and adapts every question to your
            performance — so you can master your subjects with confidence.
          </p>
          <div className="mt-9 flex flex-wrap gap-3">
            <ButtonLink to="/signup" size="lg">
              Start an Examination <Arrow />
            </ButtonLink>
            <ButtonLink to="/" hash="how-it-works" size="lg" variant="outlineDark">
              See How It Works
            </ButtonLink>
          </div>
          <ul className="mt-10 flex flex-wrap gap-x-7 gap-y-3">
            {["Conversational examination", "Reasoning-level evaluation", "Adaptive follow-ups"].map((t) => (
              <li key={t} className="flex items-center gap-2 text-[0.8125rem] text-white/55">
                <span className="grid h-4 w-4 place-items-center rounded-pill text-indigo-500" style={{ background: "rgba(88,101,242,0.18)" }}>
                  <Check />
                </span>
                {t}
              </li>
            ))}
          </ul>
        </div>

        <ConversationMockup />
      </div>

      <div aria-hidden="true" className="h-10 w-full bg-surface-50" style={{ borderTopLeftRadius: "40% 100%", borderTopRightRadius: "40% 100%" }} />
    </section>
  );
}

function MockLine({ children }: { children: React.ReactNode }) {
  return <p className="text-[0.8125rem] leading-relaxed text-fg-700">{children}</p>;
}

function ConversationMockup() {
  return (
    <div className="rise" style={{ animationDelay: "80ms" }}>
      <div className="overflow-hidden rounded-2xl border border-white/10 bg-background shadow-lg">
        <div className="flex items-center justify-between gap-3 border-b border-line px-5 py-3.5">
          <span className="text-[0.8125rem] font-semibold text-fg-950">
            Examiner<span className="text-indigo-500">AI</span>
          </span>
          <span className="hidden text-[0.6875rem] text-fg-500 sm:block">Data Structures · Technical Examination</span>
          <span className="text-[0.6875rem] text-fg-500">Question 4 of 10</span>
        </div>

        <div className="space-y-5 bg-surface-50 px-5 py-6">
          <div className="max-w-[88%]">
            <p className="eyebrow mb-2 text-indigo-600">AI Examiner</p>
            <div className="rounded-[16px] rounded-tl-md border border-line bg-background p-4 shadow-xs">
              <MockLine>
                Let's begin with a question about binary search trees. Can you explain how the search operation works and
                why its average complexity is O(log n)?
              </MockLine>
            </div>
          </div>

          <div className="ml-auto max-w-[82%]">
            <p className="eyebrow mb-2 text-right text-fg-500">Student</p>
            <div className="rounded-[16px] rounded-tr-md border border-line bg-surface-200/70 p-4">
              <MockLine>In a balanced tree, we eliminate roughly half of the remaining nodes at each step…</MockLine>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <span className="soft-pulse h-1.5 w-1.5 rounded-full bg-indigo-600" />
            <span className="text-[0.75rem] text-fg-500">Analyzing understanding…</span>
          </div>

          <div className="max-w-[88%]">
            <p className="eyebrow mb-2 text-indigo-600">AI Examiner</p>
            <div className="space-y-3 rounded-[16px] rounded-tl-md border border-line bg-background p-4 shadow-xs">
              <MockLine>Your explanation is mostly correct. Let's go one step deeper.</MockLine>
              <div className="border-t border-line pt-3">
                <MockLine>What changes when the tree becomes highly unbalanced?</MockLine>
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3 border-t border-line bg-background px-5 py-4">
          <span className="flex-1 text-[0.8125rem] text-fg-500">Explain your reasoning…</span>
          <span className="inline-flex h-9 items-center gap-2 rounded-lg bg-indigo-600 px-3.5 text-[0.75rem] font-medium text-white">
            Send Answer <Arrow />
          </span>
        </div>
      </div>
      <p className="mt-4 text-right text-[0.75rem] text-white/40">The examination is the conversation.</p>
    </div>
  );
}

/* ------------------------------ Trust metrics ---------------------------- */

function TrustMetrics() {
  return (
    <section className="bg-surface-50 pt-14 pb-20">
      <div className="container-page">
        <p className="eyebrow text-center text-fg-500">Trusted by students, educators and institutions</p>
        <div className="mt-10 grid grid-cols-2 gap-y-10 md:grid-cols-4 md:divide-x md:divide-line">
          {[
            ["50K+", "Students"],
            ["1M+", "Questions Answered"],
            ["95%", "Report Better Understanding"],
            ["200+", "Institutions (Pilot)"],
          ].map(([v, l], i) => (
            <div key={l} className={i === 0 ? "md:pr-6 text-center" : "text-center md:px-6"}>
              <Metric value={v} label={l} tone="indigo" />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* -------------------------------- Features ------------------------------- */

const FEATURES = [
  {
    title: "Conversational Examination",
    body: "The examiner asks, listens and responds. There is no question list — only one continuous examination.",
  },
  {
    title: "Reasoning-Level Evaluation",
    body: "Answers are assessed on mechanism and justification, not keyword matching.",
  },
  {
    title: "Socratic Follow-Ups",
    body: "Incomplete or shaky answers are probed further, exactly as a human examiner would.",
  },
  {
    title: "Adaptive Difficulty",
    body: "The examination silently shifts toward your weak topics and the level that challenges you.",
  },
];

function Features() {
  return (
    <section id="features" className="scroll-mt-20 border-t border-line bg-background py-24">
      <div className="container-page">
        <SectionHeader
          eyebrow="Why choose ExaminerAI"
          title="A smarter way to prepare"
          description="More than practice. ExaminerAI examines your understanding, diagnoses what is missing and tells you exactly what to revise."
        />
        <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map((f) => (
            <Card key={f.title} className="transition-shadow duration-200 hover:shadow-sm">
              <div
                className="grid h-10 w-10 place-items-center rounded-lg text-indigo-600"
                style={{ background: "color-mix(in oklab, var(--indigo-600) 10%, transparent)" }}
                aria-hidden="true"
              >
                <Check />
              </div>
              <h3 className="mt-5 text-[0.9375rem] font-semibold text-fg-950">{f.title}</h3>
              <p className="mt-2 text-[0.8125rem] leading-relaxed text-fg-700">{f.body}</p>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ------------------------------ How it works ----------------------------- */

const STEPS = [
  ["Configure", "Choose the subject, topics, examination mode and depth."],
  ["Be examined", "The AI examiner opens the examination and questions you conversationally."],
  ["Be probed", "Weak reasoning triggers follow-ups until your understanding is clear."],
  ["Receive your report", "A written assessment of what you understand — and what you don't."],
];

function HowItWorks() {
  return (
    <section id="how-it-works" className="scroll-mt-20 bg-surface-100 py-24">
      <div className="container-page">
        <SectionHeader eyebrow="How it works" title="From questions to real progress" description="A simple, deliberate process designed for deep learning." />
        <ol className="mt-14 grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          {STEPS.map(([title, body], i) => (
            <li key={title}>
              <span className="grid h-9 w-9 place-items-center rounded-pill bg-indigo-600 text-[0.8125rem] font-semibold text-white">
                {i + 1}
              </span>
              <h3 className="mt-5 text-[0.9375rem] font-semibold text-fg-950">{title}</h3>
              <p className="mt-2 text-[0.8125rem] leading-relaxed text-fg-700">{body}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}

function Educators() {
  return (
    <section id="educators" className="scroll-mt-20 border-t border-line bg-background py-24">
      <div className="container-page grid gap-12 lg:grid-cols-2 lg:items-center">
        <SectionHeader
          align="left"
          eyebrow="For educators"
          title="Examination-grade assessment, at scale"
          description="Departments use ExaminerAI to run viva-style practice at a scale no timetable allows — with a written diagnosis for every student."
        />
        <div className="grid gap-4 sm:grid-cols-2">
          {[
            ["Cohort-level gaps", "See which concepts a class consistently fails to justify."],
            ["Syllabus aligned", "Configure topics to match your own course structure."],
            ["Viva practice", "Students rehearse defending their reasoning out loud."],
            ["Pilot programme", "Currently running with 200+ institutions."],
          ].map(([t, b]) => (
            <Card key={t} className="p-5">
              <h3 className="text-[0.875rem] font-semibold text-fg-950">{t}</h3>
              <p className="mt-2 text-[0.8125rem] leading-relaxed text-fg-700">{b}</p>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}

function Pricing() {
  const plans = [
    ["Student", "Free", "Two examinations each week, full performance reports."],
    ["Scholar", "₹499 / month", "Unlimited examinations, history and revision tracking."],
    ["Institution", "Custom", "Cohort analytics, syllabus alignment and onboarding."],
  ];
  return (
    <section id="pricing" className="scroll-mt-20 bg-surface-100 py-24">
      <div className="container-page">
        <SectionHeader eyebrow="Pricing" title="Straightforward plans" />
        <div className="mt-14 grid gap-5 md:grid-cols-3">
          {plans.map(([name, price, body], i) => (
            <Card key={name} className={i === 1 ? "border-indigo-600/30 shadow-sm" : ""}>
              <div className="flex items-center justify-between">
                <h3 className="text-[0.875rem] font-semibold text-fg-950">{name}</h3>
                {i === 1 ? <Badge tone="indigo">Most chosen</Badge> : null}
              </div>
              <p className="mt-5 font-display text-3xl tracking-tight text-fg-950">{price}</p>
              <p className="mt-3 text-[0.8125rem] leading-relaxed text-fg-700">{body}</p>
              <ButtonLink to="/signup" size="sm" variant={i === 1 ? "primary" : "secondary"} className="mt-6 w-full">
                Get started
              </ButtonLink>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}

function FinalCTA() {
  return (
    <section id="about" className="scroll-mt-20 bg-background py-24">
      <div className="container-page">
        <div className="relative overflow-hidden rounded-2xl bg-ink-950 px-8 py-16 sm:px-14">
          <div
            aria-hidden="true"
            className="pointer-events-none absolute -right-20 -top-24 h-[380px] w-[380px] rounded-full"
            style={{ background: "radial-gradient(circle, rgba(139,124,255,0.22), transparent 65%)" }}
          />
          <div className="relative max-w-xl">
            <p className="eyebrow text-white/45">A higher standard of self-assessment</p>
            <h2 className="mt-5 font-display text-[2.25rem] leading-[1.08] tracking-tight text-white sm:text-[3rem]">
              Find out what you really know.
            </h2>
            <p className="mt-5 text-[0.9375rem] leading-relaxed text-white/60">
              Start your first examination today and take a step towards true mastery.
            </p>
            <div className="mt-9 flex flex-wrap gap-3">
              <ButtonLink to="/signup" size="lg">
                Get Started for Free <Arrow />
              </ButtonLink>
              <ButtonLink to="/" hash="features" size="lg" variant="outlineDark">
                Learn More
              </ButtonLink>
            </div>
          </div>
          <p className="relative mt-14 max-w-xs text-[0.8125rem] italic leading-relaxed text-white/45 lg:absolute lg:right-14 lg:top-16 lg:mt-0">
            "The limits of my language mean the limits of my world."
            <span className="mt-2 block not-italic tracking-wider">— LUDWIG WITTGENSTEIN</span>
          </p>
        </div>
      </div>
    </section>
  );
}

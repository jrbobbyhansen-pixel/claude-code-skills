# Claude Code Skills Library

A collection of 10 battle-tested custom skills for [Claude Code](https://claude.com/claude-code) by [Bobby Hansen Jr.](https://github.com/jrbobbyhansen-pixel) — audit engines, build pipelines, deliberation systems, and quality loops. Every skill here is the exact version I run daily, shared verbatim.

Skills are markdown-defined capabilities Claude Code loads on demand. Each one lives in its own folder with a `SKILL.md` entry point, plus optional `references/` (doctrine, rubrics, templates the skill reads mid-run) and `scripts/` (deterministic Python/shell helpers).

## Installation

Copy any skill folder into your user-level skills directory:

```bash
git clone https://github.com/jrbobbyhansen-pixel/claude-code-skills.git
cp -r claude-code-skills/skills/polish ~/.claude/skills/
```

Or install everything at once:

```bash
cp -r claude-code-skills/skills/* ~/.claude/skills/
```

Restart Claude Code (or start a new session) and invoke with `/skill-name`. To scope a skill to one project instead, copy it to `<project>/.claude/skills/`.

**Requirements:** Claude Code CLI. Skills with `scripts/` need Python 3. `/council`'s multi-provider mode optionally uses API keys from env vars (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `XAI_API_KEY`, `OPENROUTER_API_KEY`, `GEMINI_API_KEY`) — it degrades gracefully without them.

## The Library

| Skill | One-liner | Size |
|---|---|---|
| [`/ascend`](skills/ascend/SKILL.md) | Compounding enhancement-build loop toward best-in-class | 12 files |
| [`/council`](skills/council/SKILL.md) | 22-persona multi-round deliberation on hard decisions | 30 files |
| [`/elon-audit`](skills/elon-audit/SKILL.md) | First-principles audit of 100% of a codebase | 1 file |
| [`/feel`](skills/feel/SKILL.md) | Conform an app to a fixed interaction-feel standard | 6 files |
| [`/gauntlet`](skills/gauntlet/SKILL.md) | Goal-anchored ship-readiness audit + fix plan | 32 files |
| [`/grill-me`](skills/grill-me/SKILL.md) | Relentless plan interviewer + missed-idea surfacer | 1 file |
| [`/loom`](skills/loom/SKILL.md) | Platform for self-running, verified quality loops | 40 files |
| [`/polish`](skills/polish/SKILL.md) | Surface every UI/UX refinement, statically | 16 files |
| [`/ship`](skills/ship/SKILL.md) | Autonomous idea-to-launch build pipeline | 9 files |
| [`/tla-precheck`](skills/tla-precheck/SKILL.md) | Formally verify state machines via a TypeScript DSL | 3 files |

**How they relate.** Four form a quality ladder — `/polish` (refine what exists) → `/feel` (conform to a fixed interaction standard) → `/ascend` (add best-in-class capability) → `/gauntlet` (prove it's ready to ship). `/elon-audit` is the deep-clean that pairs with any of them. `/ship` builds new things end-to-end, `/loom` turns any of the above into scheduled self-running loops, and `/council` + `/grill-me` pressure-test the thinking before you build. `/tla-precheck` verifies the state machines underneath it all.

---

## `/ascend` — Enhancement-Build Loop

**Take an app from "good" to "best-in-class" by building it up — never tearing it down.**

Reads the entire codebase, locks the app's purpose and users (goal-lock), then runs a compounding loop of **≥3 passes that escalate in fidelity**. Each pass:

1. **Benchmarks** the 2–3 best-in-class exemplars for *this app's specific job* (Asana for boards, Linear for speed/triage, Stripe for forms/data, Notion for views, Figma for collaboration)
2. **Researches** their real patterns — hybrid recall + web-verification, with truthful citations only
3. **Scores** quantified gaps between your app and the exemplars
4. **Builds** the enhancement on an isolated branch, in the app's own design language
5. **Verifies** it actually works — tests, liveness, and reachability checks (never claims without proof)
6. **Reviews** via an independent agent, then pauses for your diff review
7. **Carries forward** the new state as the baseline for the next pass

Enhancement build, **not** redesign (never tears down identity or information architecture) and **not** mere polish (it adds real capability). Deterministic scaffolding scripts handle state, pass initialization, and codebase scanning; a coverage-guaranteed MAP phase ensures nothing is missed.

v1.1 (built by running ascend on itself) adds: **`--slate`** ideas-first mode — gate on the full scored slate *before* anything is built; a **`--snapshot`** isolation lane — safe for non-git targets and targets nested inside a larger repo, with per-pass snapshots and a scripted, dependency-preserving revert; and **prompt-artifact targets** — point ascend at a skill or prompt, not just an app, with live-fire verify tiers and class-gated state validation.

v1.2 (same recursive session) replaces the divide-by-effort score as selector: candidates are now ranked by **impact = value × identity-fit × confidence** (RICE-style confidence locked to 1.0 verified/observed · 0.8 recalled · 0.5 hypothesis, and it must match the cited evidence), effort becomes a per-pass **weight-class budget** (S/M/L — ambition is a declared choice, not an automatic penalty), and every candidate killed by the bar rides to the gate as a visible **graveyard**. All of it machine-enforced: omitted confidence or weight-class on a modern record is a hard rejection, not a free maximum.

**Use it when:** "make this world-class", "level this app up", "enrich it toward [billion-dollar competitor]".

**Inside:** `SKILL.md` + 6 references (doctrine, exemplar patterns, goal-intake, loop mechanics, state schema, a full worked example pass) + 5 scripts (detect, init, new-pass, scan, state).

---

## `/council` — Council of High Intelligence

**22 thinkers argue your hardest decision across multiple structured rounds.**

A multi-persona deliberation system with real enforcement mechanisms — polarity-pair separation constraints (opposed thinkers never share a triad), claim-type labeling (empirical / mechanistic / strategic / ethical / heuristic), and structured disagreement that surfaces minority reports instead of averaging them away.

- **`/council`** (standard): auto-selects the 2 complementary triads best suited to your question, runs 3 rounds — independent analysis → cross-examination → final crystallization — then synthesizes a verdict with explicit agreements, core disagreements, minority report, and a recommended action.
- **`/council --deep`**: all 22 members in an extended multi-round fight.

The bench spans engineering (Torvalds, Karpathy, Sutskever, Ada Lovelace), strategy (Sun Tzu, Machiavelli, Bezos, Jensen, Graham), epistemics (Feynman, Kahneman, Taleb, Munger, Meadows), philosophy (Socrates, Aristotle, Diogenes, Lao Tzu, Aurelius, Watts, Musashi), and design (Rams). Persona files define each member's actual reasoning style, not just a name.

Supports multi-provider model routing (Anthropic, OpenAI, xAI, OpenRouter, Gemini, local Ollama) so different personas can literally run on different models — provider detection is automatic from env keys.

**Use it when:** a decision is genuinely hard, has no clean answer, and you want structured disagreement instead of a single model's take.

**Inside:** `SKILL.md` + 22 persona definitions + provider-routing reference + 6 scripts (multi-provider calls, deliberation tracking, provider detection, context injection, research briefs, streaming). *Note: `inject-context.py` reads from the author's local setup — adapt its paths/name for your own environment, or skip it; the core deliberation works without it.*

---

## `/elon-audit` — First-Principles Codebase Audit

**Every file read. Every bug surfaced. Every fix specified to the line.**

A surgical, zero-mercy audit of an entire repository, run in five phases modeled on first-principles manufacturing review:

1. **Inventory** — sense the atoms: parallel agents over bounded slices, each returning a coverage receipt; the audit cannot proceed until `UNMAPPED = ∅` — **coverage is proven, never claimed**
2. **Physics Test** — prove it works: verify claimed behavior against actual code paths
3. **Delete/Trim** — ruthless 80/20: dead code, unused deps, unreachable branches
4. **Risk/Edge Proof** — hunt unhandled edges, race conditions, hardcoded secrets, silent failures
5. **Cross-Examination** — fresh-context adversarial verifiers try to *refute* every P0 (plus a P1/P2 sample) before anything executes; the kill rate is reported honestly — the maker never grades itself
6. **Handoff** — one dependency-ordered, executable fix plan, ranked P0 → P2

Every finding carries evidence under **the Finding Contract**: `[PROVEN]` (executed or traced this run, receipts attached) or `[SUSPECTED]` (pattern-matched) — and a suspected P0 can never execute unverified. The philosophy is honesty-first: every finding ships with a specific fix or an explicit `[NEEDS MANUAL CONFIRM]` — no vague recommendations, no nice-to-haves. Output includes an inline report and (when your wiki exists) an Obsidian-ready audit note with health scores.

**Use it when:** you want to ruthlessly debug, clean, and harden a project in one command.

**Inside:** a single self-contained `SKILL.md` — the whole engine is the prompt architecture.

---

## `/feel` — Instill the House Feel

**Conform any app to one fixed, opinionated interaction standard — the UX-DNA.**

Where `/polish` finds an app's own best self, `/feel` drives an app toward a **single embedded baseline** distilled from apps that feel great: spring-not-tween motion, every-tap-answered touch feedback, breathe-sparingly animation loops, flat/predictable navigation, strict 4px spacing rhythm, and depth-by-shadow instead of borders. No reference app needed — the standard ships inside the skill.

Runs as: detect the stack → **calibrate to the target's identity** (the anti-clone step — conformance never means making every app identical) → audit principle-by-principle → produce a conformance **scorecard** (the core deliverable) → on `--apply`, make the fixes. Mechanical fixes (press-scale, haptics, tokens, entrance/value-bump/pulse motion, borders→shadow) apply directly; **structural retrofits** (flatten navigation, reset-on-auth, drawer→modal, custom headers) are separately gated because they touch architecture. A static verify gate runs after every apply; re-runs are stateful deltas.

First-class support for React Native (Reanimated) and React web (Framer Motion / react-spring / CSS), principles-only elsewhere.

**Use it when:** "make this app feel like my other one", "apply our interaction standard", "match the smooth one." For open-ended refinement with no fixed standard, use `/polish` instead.

**Inside:** `SKILL.md` + the baseline rubric, doctrine, scorecard template, and per-stack presets (React Native, web).

---

## `/gauntlet` — The Newsroom

**A publishing house of role-defined agents that answers one question: does anything block your goal by your deadline?**

Every finding is gated on a concrete mandate — goal, deadline, demo path — so the audit never devolves into a generic nitpick list. Three steps:

1. **GRILL** — a project-adaptive interview that locks the mandate with zero guessing (borrowed from `/grill-me`)
2. **AUDIT** — bounded-slice, multi-desk deliberation rounds: sweep → cross-desk → red-team → cross-examination → **live field-test** (it actually runs your demo path) → subtraction pass. Returns ONE deduplicated punch-list and a quantitative **GO/NO-GO** verdict.
3. **FIX PLAN** — dependency-ordered, conflict-checked, verifiable remediation with opt-in tier-by-tier execution (borrowed from `/elon-audit`)

The bench holds 20 specialist desk charters — security, money/billing, privacy, concurrency, reliability, performance, mobile, embedded, ML-inference, AI/LLM-app, API contracts, build/release, dependencies, data, copy/UX, and more — cast per-project by a rubric so you only pay for relevant desks. The **bounded-slice guarantee** keeps every desk's context under control on large repos. Stateful across runs: each project keeps a persistent quality bar in `.gauntlet/` so re-audits measure deltas.

**Use it when:** "are we ready to launch?", "run it through the gauntlet", "make me a fix plan" — any time readiness must be judged against a real goal and date.

**Inside:** `SKILL.md` + 26 references (doctrine, casting/scoring rubrics, failure modes, field-test playbook, intake templates, 19 role charters, a worked readiness example) + 5 scripts (cast, split, aggregate, plan, field-test scaffold).

---

## `/grill-me` — The Relentless Interviewer

**Get grilled on your plan until every branch of the decision tree is resolved — and hear what the billion-dollar products you're implicitly competing with would do.**

Enters plan mode (read-only — no code changes possible), then runs a structured interrogation with two jobs: find every hole, and surface the features, workflows, and UI/UX ideas that proven products use for your exact problem — the ones you missed.

The interview has a spine: it opens with a **Branch Map** — the plan decomposed into a decision tree, **rooted in the outcome** (grill the opportunity before the solution; solution branches resting on unvalidated needs get flagged — the Opportunity Solution Tree principle), **swept against fixed dimensions** (users/UX · data · failure modes · security · cost · ops · distribution · timeline, so coverage never depends on one lucky decomposition), then walked highest-stakes-first with dependencies resolved first. Questions come one at a time with the interviewer's recommended answer stated up front. Per branch it runs the **Exemplar Move** (how do 2–3 real products handle this? matched to the surface type, claims marked recalled-vs-verified, never invented), **reversibility triage** (one-way doors get drilled hard and must name kill criteria; two-way doors resolve fast), and the **past-tense rule** (Mom Test discipline: "users will want it" doesn't resolve a branch — when did that last actually happen? — or it resolves as an admitted untested assumption with a named risk). An **anchoring guard** flips the interviewer to steelmanning the opposite if you agree too easily. After the walk: a **pre-mortem** round ("six months later, it failed — what killed it?") and a **Missed-Angle Sweep** (3–7 concrete ideas the plan lacks, each with the company that proves it works). It closes by rendering a **Decision Ledger** — every decision with rationale, rejected alternative, and confidence; hypothetical-evidence decisions flagged; surfaced ideas marked adopted/rejected/on-the-table — then offers three exits: BUILD-SPEC, ExitPlanMode, or `/gauntlet`. `/grill-me quick` grills only the top-3 highest-stakes branches.

Still one lean file, and still the front door to `/gauntlet` (whose GRILL step descends from it) — the cheapest way to find out your plan has a hole before you build it.

**Use it when:** you want a plan stress-tested *before* writing code, want to discover what best-in-class products would do here, or say "grill me."

**Inside:** a single 58-line `SKILL.md`. Proof that a skill is a behavior, not a codebase.

---

## `/loom` — The Loom

**A platform for self-running, verified quality loops — design the pattern once, the loop runs the motion.**

The biggest system in the library. A loom weaves quality from repetitive motion under a designed pattern; `/loom` does the same with coding agents. You design a loop once — what work it finds, what objective gate fails it, what state survives between runs — and it runs on schedule from then on.

The honest core is **the 4-condition gate**: `/loom` *refuses* to build loops that don't earn their cost (most automation ideas fail this). Loops that pass get scaffolded as a minimum viable loop (skill + state + objective gate + independent checker), **backtested against history** before deployment, then deployed nightly/always/event-driven at a **trust-gated maturity stage**: shadow (report only) → PR-only → auto-merge-trivial. Write access is earned, never granted.

Fleet-level hardening for running many loops across repos: registry + status dashboard, review-backpressure (loops slow down when you stop reviewing their output), crash-loop and dependency circuit breakers, freeze windows, a dead-man's-switch, cost budgets, untrusted-input isolation, value/comprehension-debt accounting, and a morning digest.

Ships with 7 ready-made loop templates: ci-triage, coverage-ratchet, dep-bump, elon-trim, lint-fix, nightly-polish, weekly-gauntlet — the last three wrap other skills in this library into compounding loops.

**Use it when:** "set up a nightly X loop", "should this be a loop?", "what did the loops do overnight?"

**Inside:** `SKILL.md` + 12 references (doctrine, the gate, trust ladder, deploy matrix, fleet reliability, security model, cost governance, observability, context hygiene, failure modes, value/human factors, tool surface) + 7 loop templates + 13 scripts (registry, backtest, budget, watchdog, sandbox, trace store, gate detection/mutation, and more).

---

## `/polish` — Make It Shine

**Turn "it works" into "it feels great" — every shippable refinement, found statically.**

Reads the codebase without ever running the app and fans out expert-lens **desks** over bounded slices: micro-interactions, motion, copy, empty/loading/error states, accessibility, typographic rhythm, consistency, layout/adaptivity, forms, performance/jank, and gestures.

Discipline is the point — this is polish, **not** redesign. It never touches information architecture, navigation, data models, or component APIs, and never adds features or dependencies. Every finding must:

- cite `file:line` plus a **read-proof anchor** (evidence the desk actually read the code, not pattern-matched)
- explain *why* it elevates the experience
- name a billion-dollar company that truthfully does it (invented specs are forbidden by doctrine)
- be classed **OBJECTIVE / CONVENTION / TASTE** so you know what's fact vs. opinion

A calibration phase locks the app's *own* design language first, so suggestions match the app rather than genericizing it. Findings aggregate into an apply menu; approved fixes go through a two-tier static verify gate. Re-runs are stateful deltas — it remembers what you rejected.

**Use it when:** "make it feel premium / Apple-quality", "find every micro-interaction we're missing."

**Inside:** `SKILL.md` + 10 desk charters + doctrine, north-stars, and output template + 2 scripts (scan, aggregate).

---

## `/ship` — The Shipyard

**Hand it an idea; a crew takes it from dock to water. You own taste and the one tap that ships.**

An autonomous build-and-ship pipeline where role-defined stations run research → architect → build → test → review → fix → polish → staged launch. Safe to be aggressive because everything happens on a throwaway `ship/<slug>` branch in an **isolated git worktree** — a wrong build costs nothing to discard. Deploy is **always human-gated**.

Two lanes with strict separation:

- **FAST** (`/ship`): reviews + tests + gates the *current diff* in minutes — a pre-merge quality gate
- **FULL** (`/ship "<idea>"`): runs the whole pipeline unattended, pinging you only at the launch gate, an escalation, or an abort

Project-adaptive via a detected **Project Profile** — the same skill correctly handles an app, a webpage, or a CLI, with profile adapters for common deploy targets. The test ⇄ review ⇄ fix loop iterates until reviewers pass the build. `/ship --init` generates a project's `CLAUDE.md` foundation so future runs (and every other skill) work better.

**Use it when:** "ship this", "take this idea and build it", "review before I merge."

**Inside:** `SKILL.md` + 5 references (doctrine, profile adapters, reviewer lenses, workflow kit, CLAUDE.md template) + 3 scripts (detect, notify, summarize). *Note: `workflow-kit.md` and `profile-adapters.md` use the author's own repos as worked examples — swap in yours.*

---

## `/tla-precheck` — Formal State-Machine Verification

**TLA+ semantics without writing TLA — catch state-machine bugs before they corrupt data.**

A restricted TypeScript DSL for designing and formally verifying state machines. You write `.machine.ts` files — variables, actions, invariants — and the checker exhaustively explores the state space, proving invariants hold across every reachable state. You never write `.tla` files.

Three-command workflow: start a new machine → run the design loop until it passes → ship it (generates a runtime adapter plus all artifacts for adapter-capable machines). Proof tiers let you declare how much verification a machine warrants, and a clear runtime boundary defines what the proof does and doesn't cover.

**Use it when:** building billing flows, subscription lifecycles, agent orchestration, queue processing, deployment pipelines — anywhere a state-machine bug means corrupted data, stuck users, or silent failures.

**Inside:** `SKILL.md` + DSL cheatsheet + CLI workflow reference.

---

## License

[CC0 1.0 Universal](LICENSE) — public domain. Take anything, use it anywhere, no attribution required (though a star is appreciated).

---
name: evolve
description: Ideas-first, human-gated enhancement slate for an app or a single surface (page, tab, screen). /evolve deep-reads the target and its plumbing behind a machine-verified coverage gate, then develops enhancement briefs across four lanes — DEEPEN (richer interaction on data already on the surface), CONNECT (wire surfaces/data that share entities but don't talk yet), MODEL (advance the surface with the model of record, trust-ladder gated), COMPLEMENT (a new capability that completes a job users already start here) — every claim anchored file:line and audited against disk by script, confidence computed (never declared), incomplete briefs mechanically rejected, survivors adversarially cross-examined, ranked, and presented as a slate you approve/defer/kill BEFORE anything is built. Approved briefs route to /ascend (capability) and finish with /polish (presentational); /evolve itself never edits app code. Use when the user says "/evolve", asks "what could this page/screen do next", wants to enhance a surface with tightly-coupled capabilities, connect data or wiring between existing surfaces, layer capability onto what exists without changing what the app is, or wants well-thought-out enhancement ideas gated by them before any build.
version: 1.1.0
author: Bobby Hansen Jr. (bobbyhansenjr)
license: CC0
platforms: [linux, macos]
---

# `/evolve` — Evolution, Not New Species

Decide **what an existing surface should do next** — before a line of it is built. `/evolve` deep-reads a surface
and the plumbing around it, then develops enhancement ideas the way a strong staff engineer would pitch them: each
one a full **brief**, grounded in cited evidence from the real code, wired only through services that already exist
and the model already integrated, adversarially cross-examined, ranked — and then it **stops**. The slate is the
deliverable. Nothing is built until you approve it, item by item.

The promises are **mechanical, not honor-system** (`scripts/verify.py`, stdlib-only): coverage is proven before
ideation opens (the UNCHARTED gate), every anchor is audited against disk at the exact cited line, an incomplete
brief is rejected in public, and confidence is *computed* from the evidence — declaring it is itself a rejection.

The test every idea must pass: **would a returning user say "the app got better at its job" — not "the app does a
new job now"?** Evolution of what exists. Never a new species.

## The Ladder — where `/evolve` sits
```
/polish    refine what's there — presentational only                     "make it shine"
/evolve    decide what to layer on next — ideas-first, human-gated  ← THIS  "tighten & extend"
/ascend    build approved capability up, benchmark-driven passes         "make it world-class"
```
`/grill-me` interrogates a plan **you** bring; `/evolve` **generates** the plan from the code. `/ascend --slate`
also gates ideas first, but sources them from *competitor benchmarks*; `/evolve` sources them from the app's **own
latent structure** — data already fetched, entities already shared, services already deployed, the model already
wired in. The two are complements: `/evolve` decides, `/ascend` builds.

## Invocation
```
/evolve                              # whole app: slate per major surface
/evolve src/pages/Dashboard          # one surface (dir, page, screen, or component)
/evolve "reports tab"                # name a surface; Phase 0 resolves it to files
/evolve --lanes connect,model        # restrict to specific lanes (default: all four)
```
No other flags. A bare re-run in a repo with `.evolve/state.json` **resumes**: it presents undecided briefs first,
honors the graveyard, offers to route approved-but-unrouted briefs, and only then scans for new material.

## The Four Lanes — deep charters in `references/lanes/` (pasted per-lane into ideation agents)

| Lane | The question it asks | Charter |
|------|----------------------|---------|
| **DEEPEN** | What could the data *already on this surface* do that it doesn't? | `lanes/deepen.md` — latent-data vein, hunting battery, new-data kill |
| **CONNECT** | Which surfaces/data share an entity but don't talk? | `lanes/connect.md` — the both-ends rule, four wire types |
| **MODEL** | What could the **model of record** do with THIS surface's data? | `lanes/model.md` — the trust ladder, capability shapes, chat kill |
| **COMPLEMENT** | What adjacent capability *completes a job users already start here*? | `lanes/complement.md` — the last-step rule, gravity kill |

## The Platform Lock (hard constraints — flags are machine-derived into report-only)
- **Existing services only.** Every wire cites a real endpoint / query / store with a `file:line` anchor. New
  backend service, third-party API, or queue → `[REQUIRES NEW SERVICE]`.
- **Model of record only.** AI capability flows through the already-integrated model call path. A new provider,
  SDK, or tier → `[REQUIRES NEW MODEL]`.
- **No new dependencies auto-blessed** → `[REQUIRES DEP: <name>]`.
- Any `REQUIRES` flag ⇒ the brief is **report-only**: rendered in the slate, flagged, never routed to build. The
  human may lift the lock; the skill may not.
- **The evolution test** (hardest on COMPLEMENT): an idea that starts a new job is a **NEW SPECIES** — logged
  visibly in its own slate section, never briefed, never built.

## Execution Protocol

### Phase 0 — Scan, dossier, and the UNCHARTED gate
1. `mkdir -p .evolve && python3 scripts/scan.py <root> [--surface <path>] --json > .evolve/scan.json` —
   deterministic plumbing sweep: UI surfaces, endpoints, stores, model calls, navigation. Emits the
   **accounting keys** the dossier must answer for. (`--surface` narrows ideation focus, never the sweep —
   CONNECT needs the whole repo's plumbing.)
2. **Read, don't skim**, and write two artifacts: `.evolve/dossier.md` (prose, for the human) and
   `.evolve/dossier.json` (claims + accounting, for the machine — schema in `brief-template.md`). Five sections:
   **on-screen data** · **latent data** (fetched-but-unshown — DEEPEN's and MODEL's raw material) ·
   **neighbors & shared entities** (CONNECT's) · **service inventory** · **model of record**. Every claim carries
   `file:line` + a verbatim anchor. Every accounting key is marked `covered` or `dismissed: <reason>`.
3. `python3 scripts/verify.py --root <root> --evolve .evolve --check-dossier` — **ideation is BLOCKED until this
   exits clean**: anchors verified against disk, no UNCHARTED keys, no truncated scan categories. Coverage is
   proven, never claimed.

### Phase 1 — Lane ideation (fan-out)
Spawn one Agent (`general-purpose`) per active lane — **batch 3 concurrent, sequential between batches.** Paste
into each **in full**: `references/doctrine.md` + `references/brief-template.md` + **that lane's charter**
(`references/lanes/<lane>.md`) + both dossier artifacts. Each agent works its charter's hunting battery against
the real dossier and emits `.evolve/briefs/<lane>.json` — complete briefs per the machine contract, plus
`undeveloped[]` (one-liners it couldn't fill — honesty, not filler) and `new_species[]` (what tempted it).
No idea may cite anything outside the dossier; a gap found mid-ideation extends the dossier (and re-runs the
gate) first.

### Phase 2 — Mechanical law, then cross-examination, then the slate
1. `python3 scripts/verify.py --root <root> --evolve .evolve --check-briefs` — hard schema rejection, anchor audit,
   computed confidence, content-hash IDs, dup detection, report-only derivation, impact scoring →
   `.evolve/briefs.verified.json`. Rejections are public (they render, collapsed, in the slate).
2. **Cross-examination — the maker never grades itself.** For each surviving brief, spawn a fresh-context verifier
   to refute what the script can't judge: the species audit, job-reality audit, wiring-semantics audit, score
   audit, and (MODEL) trust audit — duties in `doctrine.md`. **L-weight and COMPLEMENT briefs get two independent
   verifiers** (species lens + wiring lens); either can kill. Write kills (with refutations) to
   `.evolve/kills.json`; survivable objections are appended to the brief's `risks` (then re-run step 1 so the
   edit is re-audited).
3. `python3 scripts/verify.py --root <root> --evolve .evolve --slate` — renders `.evolve/SLATE.md`: per-lane
   ranking (impact = job_value × tightness × confidence), ≤5 presented per lane, visible bench, report-only
   section, NEW SPECIES log, cross-exam kills with refutations, mechanical rejections, graveyard (collapsed),
   and the **dependency apply-order** (cycles flagged loudly). Updates `state.json`.

### Phase 3 — THE GATE (the point of the skill)
Present the slate and **YIELD THE TURN.** Never build, route, or edit in the gate turn. Decision menu per brief:
**approve · defer · kill <reason> · promote <bench-id>**. Record every decision in `.evolve/state.json`: kills
enter the **graveyard** (never re-proposed; rendered collapsed with reasons), deferred briefs resurface first next
run, approved briefs move to routing.

### Phase 4 — Route to build (a later turn, only for `approved[]`)
`/evolve` **never edits app code.** Write `.evolve/handoff.json` (full approved briefs + the Platform Lock text +
the approved subset's apply order), then:
- **Capability briefs** (the normal case) → run `/ascend` focused per brief (`/ascend "<brief name>" <surface>`) —
  or one run with the approved set as its pass slate — **pasting the Platform Lock into ascend's goal-lock as
  additional Untouchables**, and respecting the apply order.
- **Purely presentational briefs** (rare in these lanes) → note them for the `/polish <surface>` pass.
- **Finish** with `/polish <surface>` after builds land, to sand the new edges (ascend already hands it
  `deferred_polish[]`).
The user may equally take the briefs and build anywhere — the handoff file is self-contained.

### Re-run = Stateful Delta
`state.json` holds the dossier hash, every brief (stable content-hash IDs), and every decision. On re-run:
unchanged dossier hash → skip Phase 0; undecided briefs present first; graveyard stays buried; `approved[]` minus
`routed{}` is offered before new ideation.

## Claude Code Notes
- Fan-out via the **Agent tool**, max 3 concurrent, sequential between batches. Paste doctrine, template, lane
  charter, and dossier **in full** — never summarized.
- Run scripts with the **Bash tool** (`python3`, stdlib-only — no installs). All artifacts live under `.evolve/`
  (suggest the user gitignore it). `SLATE.md` is rendered by the script — never hand-written, never hand-edited.
- This skill's safety model is **having no apply step.** The moment you feel the urge to "just wire it up while
  you're here," you are in `/ascend`'s jurisdiction — stop and route.

## Pitfalls
1. **Species drift** — a COMPLEMENT brief that's really a new product ("add a CRM to the invoice page"). The
   last-step rule and gravity kill exist for exactly this; log it to NEW SPECIES.
2. **Phantom wiring** — citing an endpoint or payload field that doesn't exist. The machine kills bad anchors;
   verifiers kill bad *semantics* (the endpoint exists but doesn't return what the brief assumes).
3. **Exemplar envy** — "Linear has X, so we should." Benchmark-driven ideation is `/ascend`'s lane, deliberately
   absent here. Every `/evolve` idea roots in this app's own latent structure.
4. **Building in the gate turn** — presenting the slate and starting the build in one turn defeats the gate. Yield.
5. **Score gaming** — inflating `job_value`/`tightness` to climb the ranking. Justifications are machine-required
   and verifier-audited; a COMPLEMENT brief claiming tightness 3 is mis-scored by definition.
6. **Skipping the scan** — hand-writing the dossier without `scan.json` voids the coverage guarantee; the
   UNCHARTED gate only proves coverage of what the sweep found.
7. **Ideation before the gate is clean** — a BLOCKED dossier means the evidence floor has holes; briefs written on
   it inherit them. Fix the dossier first.
8. **Treating deferred as killed** — deferred briefs resurface next run; only kills enter the graveyard. Record
   the kill *reason* — it's what keeps the graveyard persuasive later.

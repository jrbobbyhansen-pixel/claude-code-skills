---
name: evolve
description: Ideas-first, human-gated enhancement slate for an app or a single surface (page, tab, screen). /evolve deep-reads the target and its plumbing, then develops enhancement briefs across four lanes — DEEPEN (richer interaction on data already on the surface), CONNECT (wire surfaces/data that share entities but don't talk yet), MODEL (advance the surface with the model of record), COMPLEMENT (a new capability that completes a job users already start here) — every idea grounded in cited file:line evidence, cross-examined by adversarial verifiers, locked to existing services and the already-integrated model, ranked, and presented as a slate you approve/defer/kill BEFORE anything is built. Approved briefs route to /ascend (capability) and finish with /polish (presentational); /evolve itself never edits app code. Use when the user says "/evolve", asks "what could this page/screen do next", wants to enhance a surface with tightly-coupled capabilities, connect data or wiring between existing surfaces, layer capability onto what exists without changing what the app is, or wants well-thought-out enhancement ideas gated by them before any build.
version: 1.0.0
author: Bobby Hansen Jr. (bobbyhansenjr)
license: CC0
platforms: [linux, macos]
---

# `/evolve` — Evolution, Not New Species

Decide **what an existing surface should do next** — before a line of it is built. `/evolve` deep-reads a surface and
the plumbing around it, then develops enhancement ideas the way a strong staff engineer would pitch them: each one a
full **brief**, grounded in cited evidence from the real code, wired only through services that already exist and the
model already integrated, adversarially cross-examined, ranked — and then it **stops**. The slate is the deliverable.
Nothing is built until you approve it, item by item.

The test every idea must pass: **would a returning user say "the app got better at its job" — not "the app does a
new job now"?** Evolution of what exists. Never a new species.

## The Ladder — where `/evolve` sits
```
/polish    refine what's there — presentational only                     "make it shine"
/evolve    decide what to layer on next — ideas-first, human-gated  ← THIS  "tighten & extend"
/ascend    build approved capability up, benchmark-driven passes         "make it world-class"
```
`/grill-me` interrogates a plan **you** bring; `/evolve` **generates** the plan from the code. `/ascend --slate` also
gates ideas first, but sources them from *competitor benchmarks*; `/evolve` sources them from the app's **own latent
structure** — data already fetched, entities already shared, services already deployed, the model already wired in.
The two are complements: `/evolve` decides, `/ascend` builds.

## Invocation
```
/evolve                              # whole app: slate per major surface
/evolve src/pages/Dashboard          # one surface (dir, page, screen, or component)
/evolve "reports tab"                # name a surface; Phase 0 resolves it to files
/evolve --lanes connect,model        # restrict to specific lanes (default: all four)
```
No other flags. A bare re-run in a repo with `.evolve/state.json` **resumes**: it presents undecided briefs first,
honors the graveyard, and only then scans for new material.

## The Four Lanes (deep law in `references/doctrine.md` — pasted in full into every agent)

| Lane | The question it asks | Example |
|------|----------------------|---------|
| **DEEPEN** | What could the data *already on this surface* do that it doesn't? | sort/filter/inline-edit, bulk actions, drill-down, keyboard flow on an existing list |
| **CONNECT** | Which surfaces/data share an entity but don't talk? | the order row links to the customer surface that owns it; cross-filtering; shared selection context |
| **MODEL** | What could the **model of record** do with THIS surface's data? | summarize the visible set, classify/triage rows, suggest next action, explain an anomaly |
| **COMPLEMENT** | What adjacent capability *completes a job users already start here*? | export the report they already assemble; saved views for filters they already apply |

## The Platform Lock (hard constraints — machine of the doctrine)
- **Existing services only.** Every wire in a brief names a real endpoint / store / table / query that exists today,
  with a `file:line` anchor. Needs a new backend service, third-party API, or queue → tag `[REQUIRES NEW SERVICE]`,
  report-only, never routed to build.
- **Model of record only.** MODEL-lane briefs call the already-integrated model through existing call paths (cite
  them). A new provider or SDK → `[REQUIRES NEW MODEL]`, report-only.
- **No new dependencies auto-blessed** → `[REQUIRES DEP: <name>]`, report-only (same law as `/polish`).
- **The evolution test** (applies to every lane, hardest on COMPLEMENT): the idea must tighten a job users already do
  on this surface. An idea that starts a new job is a **NEW SPECIES** — logged visibly in its own section so you see
  it was weighed, never briefed for build.

## Execution Protocol

### Phase 0 — Target lock & Surface Dossier
Resolve the argument to a concrete surface (or enumerate major surfaces for a whole-app run). Then **read, don't
skim** — the surface's components, its data plumbing, and its neighbors — and write the **Surface Dossier** to
`.evolve/dossier.md`, every claim carrying a `file:line` + verbatim anchor:
1. **On-screen data** — what the surface renders, field by field.
2. **Latent data** — fetched-but-unshown fields, store slices the surface ignores, response payload the UI drops.
   *(This section is DEEPEN's and MODEL's raw material — it's where the cheapest wins hide.)*
3. **Neighbors & shared entities** — every surface that reads/writes the same entities; how you get from here to
   there today (or can't). *(CONNECT's raw material.)*
4. **Service inventory** — existing endpoints/queries/mutations reachable from this app, whether this surface uses
   them or not.
5. **Model of record** — which model is integrated, through what call path, used by which features today.
The dossier is the evidence floor: **no idea may cite anything the dossier doesn't contain.** If ideation surfaces a
gap, extend the dossier (with anchors) first.

### Phase 1 — Lane ideation (fan-out)
Spawn one Agent (`general-purpose`) per active lane — **batch 3 concurrent, sequential between batches**. Paste into
each **in full**: `references/doctrine.md` + `references/brief-template.md` + the Surface Dossier. Each lane agent
develops candidates into complete **briefs** (the template is the contract): builds-on evidence, the job it tightens,
UX sketch with states, wiring plan through existing services, evolution-test verdict, weight class (S/M/L),
confidence (`verified` / `recalled` / `hypothesis` — must match the cited evidence), risks, and an explicit
**NOT-THIS scope fence**. Half-thoughts are not briefs: a candidate that can't fill every section is dropped or
downgraded to a one-line `Undeveloped` note. Ideas failing the Platform Lock or evolution test go to `new_species[]`
/ flagged report-only — never silently deleted. Output: `.evolve/briefs/<lane>.json`.

### Phase 2 — Cross-examination & ranking
The maker never grades itself. For each surviving brief, spawn a **fresh-context verifier** whose job is to
**refute** it: Does every cited anchor exist on disk, verbatim? Is the wiring real — endpoint present, data actually
in the payload/store? Does the idea secretly need a new service/model/dep? Does it flunk the evolution test? A brief
whose wiring is phantom is killed with the refutation attached; a survivable objection becomes a listed risk. Then
mechanically: **dedupe/merge** across lanes (same target + same job → one brief, lanes noted), rank by
**impact = job-value × coupling-tightness × confidence**, and cap the presented slate at **≤5 briefs per lane** —
the remainder renders as a collapsed, visible **bench** (never silently cut).

### Phase 3 — THE GATE (the point of the skill)
Render `.evolve/SLATE.md` — briefs grouped by lane, ranked, with the NEW SPECIES log, report-only flags, bench, and
graveyard (collapsed) — present it, and **YIELD THE TURN.** Never build, route, or edit in the gate turn. Decision
menu per brief: **approve · defer · kill <reason>**. Record every decision in `.evolve/state.json`: killed briefs
enter the **graveyard** (never re-proposed; render collapsed on future runs), deferred briefs resurface next run,
approved briefs move to routing.

### Phase 4 — Route to build (a later turn, only for `approved[]`)
`/evolve` **never edits app code.** Write `.evolve/handoff.json` (approved briefs + the Platform Lock text), then:
- **Capability briefs** (the normal case) → run `/ascend` focused per brief (`/ascend "<brief name>" <surface>`) —
  or one run with the approved set as its pass slate — **pasting the Platform Lock into ascend's goal-lock as
  additional Untouchables.**
- **Purely presentational briefs** (rare in these lanes) → note them for the `/polish <surface>` pass.
- **Finish** with `/polish <surface>` after builds land, to sand the new edges (ascend already hands it
  `deferred_polish[]`).
The user may equally take the briefs and build anywhere — the handoff file is self-contained.

### Re-run = Stateful Delta
`state.json` holds the dossier hash, every brief (stable content-hash IDs), and every decision. On re-run: unchanged
dossier → skip Phase 0; undecided briefs present first; graveyard stays buried; `approved[]` not yet routed is
offered before new ideation.

## Claude Code Notes
- Fan-out via the **Agent tool**, max 3 concurrent, sequential between batches. Paste doctrine, template, and
  dossier **in full** — never summarized.
- All artifacts live under `.evolve/` (suggest the user gitignore it). No scripts — state is plain JSON/markdown the
  main agent writes.
- This skill's safety model is **having no apply step.** The moment you feel the urge to "just wire it up while
  you're here," you are in `/ascend`'s jurisdiction — stop and route.

## Pitfalls
1. **Species drift** — a COMPLEMENT brief that's really a new product ("add a CRM to the invoice page"). The
   evolution test exists to kill exactly this; log it to NEW SPECIES.
2. **Phantom wiring** — citing an endpoint or payload field that doesn't exist. Every wire needs a dossier anchor;
   Phase 2 verifiers kill on sight.
3. **Exemplar envy** — "Linear has X, so we should." Benchmark-driven ideation is `/ascend`'s lane, deliberately
   absent here. Every `/evolve` idea roots in this app's own latent structure.
4. **Building in the gate turn** — presenting the slate and starting the build in one turn defeats the gate. Yield.
5. **Slate flood** — 40 shallow ideas is worse than 12 developed ones. The brief contract + per-lane cap force
   depth; the bench keeps honesty.
6. **Ideation before evidence** — skipping the dossier produces confident fiction. The dossier is the floor.
7. **Treating deferred as killed** — deferred briefs resurface next run; only kills enter the graveyard. Record the
   kill *reason* — it's what keeps the graveyard persuasive later.

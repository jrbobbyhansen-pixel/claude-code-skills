# Brief Template & Artifact Formats — the machine contract

> Pasted **in full** into every lane agent (Phase 1). These JSON shapes are not documentation — they are what
> `scripts/verify.py` enforces. A field the schema requires and you omit is a **public rejection in the slate**,
> not a quiet gap. The human-readable slate is *rendered from* this JSON by the script; you never write SLATE.md.

## A CLAIM — the atom of evidence (used in builds_on, job.anchors, wiring)
```json
{ "text": "customerId is mapped but never rendered",
  "file": "src/pages/Orders.tsx", "line": 4, "anchor": "customerId: o.customerId" }
```
- `anchor`: 5–12 verbatim words living at exactly that line. Verified against disk; an anchor found at a different
  line is rejected with the real line named. Cite what you read.
- A claim you cannot anchor may instead carry `"tag": "recalled" | "hypothesis"` **plus** `"basis": "<why you
  believe it>"`. No anchor and no tag/basis = rejection.

## A BRIEF — one per idea (`.evolve/briefs/<lane>.json`)
```json
{
  "name": "Show customer column with sort",
  "weight": "S",
  "job_value": 3,  "job_value_why": "the table IS the surface; triage by customer is its core job",
  "tightness": 3,  "tightness_why": "customerId already fetched and mapped, purely latent",
  "builds_on": [ CLAIM, ... ],
  "job": { "text": "users scan the orders table to triage", "anchors": [ CLAIM, ... ] },
  "ux": { "sketch": "customer column, header click sorts",
          "states": "empty: unchanged; loading: unchanged; error: n/a",
          "trust_posture": "(MODEL lane only, required there) rung + wrong-answer behavior + undo path" },
  "wiring": [ { "text": "no new wire — data already in row map",
                "file": "src/pages/Orders.tsx", "line": 4, "anchor": "customerId: o.customerId",
                "flags": [] } ],
  "evolution_test": { "verdict": "PASS", "line": "returning user: the orders page got better at triage" },
  "risks": [ "..." ],
  "depends_on": [ "<other brief name or id>" ],
  "not_this": "not a customer management view — one column, no drill-in"
}
```
Machine law (what `--check-briefs` rejects):
- any missing/empty required field · `weight` outside S/M/L · scores outside 1–3 · justification under 10 chars
- a **declared `confidence`** — confidence is computed (min over all claims: verified 1.0 · recalled 0.8 ·
  hypothesis 0.5) and printed in the slate with its label
- `builds_on` < 1 (< 2 for COMPLEMENT) · `job.anchors` empty · MODEL brief without `ux.trust_posture`
- `evolution_test.verdict` ≠ PASS (a FAIL belongs in `new_species[]`) · any failed anchor (ANCHOR-FAILED)
- `wiring` empty — "no new wire" is itself a wiring item, anchored to where the data already flows
Machine derivations: `id` (stable content-hash of lane|name|primary anchor — keys the graveyard),
`impact = job_value × tightness × confidence`, `report_only` (any `REQUIRES` flag), `DUP-CANDIDATE(...)` flags
when two briefs share a primary anchor.

## The lane file (`.evolve/briefs/<lane>.json`)
```json
{ "lane": "deepen",
  "briefs": [ BRIEF, ... ],
  "undeveloped": [ "column resize (couldn't fill wiring)" ],
  "new_species": [ { "name": "full CRM", "why_tempting": "customerId is right there" } ] }
```

## The dossier (`.evolve/dossier.json` — Phase 0, alongside the prose dossier.md)
```json
{ "surface": "src/pages/Dashboard",
  "sections": { "on_screen": [ CLAIM... ], "latent": [ CLAIM... ], "neighbors": [ CLAIM... ],
                "services": [ CLAIM... ], "model_of_record": [ CLAIM... ] },
  "accounting": { "endpoint::src/api/orders.ts": "covered",
                  "store::src/legacy/oldStore.ts": "dismissed: dead code, no importers" } }
```
Every `accounting_keys` entry from `scan.json` must appear as `covered` or `dismissed: <real reason>`.
`--check-dossier` exits 1 (ideation BLOCKED) on any anchor failure, missing section, UNCHARTED key, or truncated
scan category.

## Verifier kills (`.evolve/kills.json` — Phase 2, written by the main agent from verifier verdicts)
```json
[ { "id": "83ac10b258", "refutation": "sort would fight server pagination — orders.ts:41 paginates upstream" } ]
```

## State (`.evolve/state.json` — decisions are the human's; the script preserves them)
```json
{ "dossier": { "path": ".evolve/dossier.md", "hash": "<sha, script-set>" },
  "briefs": { "<id>": { "lane": "...", "name": "...", "status": "presented|benched|report_only|graveyard|cross_examined_kill", "impact": 9.0 } },
  "decisions": { "approved": ["<id>"], "deferred": ["<id>"], "killed": { "<id>": "<user's reason>" } },
  "routed": { "<id>": "ascend|polish|manual" } }
```
- `decisions.killed` **is** the graveyard — filtered out of every future slate, rendered collapsed with reasons.
- `deferred` resurfaces at the top of its lane next run (tagged DEFERRED-RESURFACED).
- `approved` minus `routed` = the "offer to route before new ideation" list on resume.

## The slate (`.evolve/SLATE.md` — rendered by `--slate`, never hand-written)
Inline summary (presented/report-only/benched counts, mechanical rejection rate, cross-exam kills, new-species,
graveyard) → per-lane ranked briefs (≤5, deferred first) → Report-only (Platform Lock) → Bench (collapsed,
promotable by ID) → NEW SPECIES log → Cross-examination kills with refutations → Mechanical rejections (collapsed)
→ Graveyard (collapsed) → **Apply order** (topological; cycles flagged loudly) → the DECIDE menu:
`approve <ids> · defer <ids> · kill <ids>: <reason> · promote <bench-ids>` — **then the skill YIELDS.**

## Handoff (`.evolve/handoff.json` — Phase 4, approved briefs only)
Self-contained: the full brief bodies (not IDs), computed confidence/impact included, the Platform Lock text
verbatim (for pasting into `/ascend`'s goal-lock as additional Untouchables), the apply order for the approved
subset, and the surface path. A consumer needs nothing else from `.evolve/`.

# Brief Template & Slate Format — the output contract

> Pasted **in full** into every lane agent (Phase 1). The slate render (below) is produced by the main agent in
> Phase 3. A brief with an empty section is not a brief.

## The Brief (one per idea — `.evolve/briefs/<lane>.json`, rendered as below in the slate)

```
### <ID> · <LANE> · <Name>                       weight: S|M|L · confidence: verified|recalled|hypothesis
BUILDS ON      the existing data/components/services this extends — every item `file:line` + verbatim anchor,
               all present in the Surface Dossier
JOB IT TIGHTENS the job users already do on this surface, stated past-tense where the code proves it
               ("users filter this table — <anchor>"), with the brief as that job's next notch
UX SKETCH      where it lives on the surface · the interaction · empty/loading/error states ·
               (MODEL lane: trust posture — suggestion vs. auto-action, undo path)
WIRING PLAN    each wire through an EXISTING endpoint/query/store/model call path, cited ·
               flags: [REQUIRES NEW SERVICE] / [REQUIRES NEW MODEL] / [REQUIRES DEP: <name>] → report-only
EVOLUTION TEST PASS/FAIL + one line ("returning user: 'the orders page got better at triage'")
RISKS          survivable objections from cross-examination · future-tense-demand admissions ·
               DEPENDS ON: <other brief IDs>, if any
NOT THIS       the explicit scope fence — the adjacent bigger thing this brief deliberately is not
```

**ID**: stable content-hash of `(lane, name, primary builds-on anchor)` — survives re-runs, keys the graveyard.

## Field rules
- `BUILDS ON` — minimum one anchor; a brief that builds on nothing citable is a NEW SPECIES candidate, not a brief.
- `confidence` — must match the weakest evidence tag inside the brief (one `hypothesis` claim ⇒ the brief is
  `hypothesis`). Phase 2 verifiers enforce; mismatch is a kill.
- `weight` — S: ≲2 files · M: one surface + its plumbing · L: crosses surfaces (CONNECT briefs are usually M/L).
  Declared honestly; ambition is a choice, not a penalty.
- `NOT THIS` — mandatory. It is the anti-species-drift device: naming the bigger thing you're *not* proposing is
  what keeps the approved build from swelling into it.

## The Slate (`.evolve/SLATE.md` — Phase 3 render)

```
# EVOLVE SLATE — <surface> · <date> · dossier <hash>

## Inline summary
<n> briefs (<n_deepen>/<n_connect>/<n_model>/<n_complement>) · <n> report-only · <n> killed in
cross-examination (rate stated) · <n> benched · <n> NEW SPECIES logged · graveyard: <n> (collapsed)

## DEEPEN            (≤5, ranked by impact = job-value × coupling-tightness × confidence)
<briefs>
## CONNECT
<briefs>
## MODEL
<briefs>
## COMPLEMENT
<briefs>

## Report-only (Platform Lock)      — rendered, flagged, bottom of slate; human may lift the lock, you may not
## Bench                            — collapsed; over-cap briefs, one line each + ID (promotable by ID)
## NEW SPECIES (logged, not briefed) — one honest line each on why it tempted
## Cross-examination kills           — brief name + the refutation (credibility, not clutter)
## Graveyard                         — collapsed; prior kills with recorded reasons; never re-proposed

── DECIDE ──────────────────────────────────────────────
approve <ids> · defer <ids> · kill <ids>: <reason> · promote <bench-ids>
(then YIELD. Nothing builds this turn.)
```

## State (`.evolve/state.json`)
```json
{
  "surface": "src/pages/Dashboard",
  "dossier": { "path": ".evolve/dossier.md", "hash": "<sha>" },
  "briefs":  { "<id>": { "lane": "...", "name": "...", "status": "presented|benched|report_only" } },
  "decisions": {
    "approved": ["<id>"],
    "deferred": ["<id>"],
    "killed":   { "<id>": "<user's reason>" }
  },
  "routed":   { "<id>": "ascend|polish|manual" },
  "new_species": [ { "name": "...", "why_tempting": "..." } ]
}
```
- `decisions.killed` **is** the graveyard — never re-proposed, rendered collapsed with reasons.
- `deferred` resurfaces at the top of the next slate.
- `approved` minus `routed` = the "offer to route before new ideation" list on resume.

## Handoff (`.evolve/handoff.json` — Phase 4, approved briefs only)
Self-contained: the full brief bodies (not IDs), the Platform Lock text verbatim (for pasting into `/ascend`'s
goal-lock as additional Untouchables), and the surface path. A consumer needs nothing else from `.evolve/`.

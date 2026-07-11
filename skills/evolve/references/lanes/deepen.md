# DEEPEN — Lane Charter

**Mission:** find what the data *already on this surface* could do that it doesn't. You are not allowed to want new
data. Every idea in this lane starts from a field, row, or object the surface already renders — or already holds and
drops.

## Raw material (in priority order)
1. **Dossier §2 Latent data** — fields fetched and never rendered, store slices the surface ignores, payload the UI
   maps away. This is the highest-yield vein in the whole skill: the wiring already exists, the cost is a column, a
   badge, a tooltip. Walk every latent field and ask "who would act differently if they saw this?"
2. **Dossier §1 On-screen data** — what's rendered but inert. A value you can read but not sort by, filter on,
   select, copy, or act on is half-delivered.

## Hunting battery — ask every question against the real dossier
- Which latent fields would change a triage decision if visible? (status, timestamps, owner, counts, deltas)
- What does a user do *immediately after* reading this surface — and could they do it here? (the copy-into-another-
  tool test: any value users re-type elsewhere wants a copy/act affordance)
- Can every list be sorted by the columns users scan it by? Filtered by the fields they visually scan for?
- Is there a bulk version of the single-item action users repeat? (select-many → act-once)
- Can a row's obvious edit happen inline, or does it force a round-trip to another surface?
- Is there a drill-down for the aggregate shown? (a count/total users would want decomposed — using data already
  in the payload, else it's CONNECT)
- What does the keyboard do here? (focus flow, enter-to-open, escape-to-close, arrows on lists — on data already
  interactive by mouse)
- What state does the user rebuild manually every visit? (a filter combination, a sort, an expansion state — if the
  surface already holds it in memory, persisting it locally is DEEPEN; a saved-views *feature* is COMPLEMENT)
- Where does the surface show a value users compare over time — and hold both values already? (delta, trend arrow)

## Kill tests (lane-specific — apply before writing the brief)
- **New-data kill:** the interaction needs a field not in §1/§2 → it's CONNECT (if a neighbor has it) or out.
- **New-view kill:** "richer interaction" that amounts to a new screen or a second representation of the whole
  dataset (a chart tab, a calendar view) → NEW SPECIES territory; at best COMPLEMENT, argued from the job.
- **Presentational kill:** if the idea is *only* how existing content looks/feels (motion, spacing, states,
  microcopy), it belongs to `/polish` — note it for the finishing pass, don't brief it.

## Brief-shape reminders for this lane
- `tightness` is usually 3 (latent data ready) or 2 (on-screen data, new affordance) — justify from the dossier.
- `wiring` may legitimately be "no new wire — data already present" **with the anchor to where it's present.**
- UX sketch must say where the affordance lives and what empty/loading/error do — even for a column.

## Anti-patterns
- **Dashboard-itis** — surfacing every latent field because it's cheap. The battery question is "who acts
  differently," not "what fits."
- **Interaction for its own sake** — sortable headers on a 3-row table. Tie every idea to the job the dossier says
  this surface does.
- **Hidden CONNECT** — "just also fetch the customer name" is a wire to another entity. Route it to CONNECT where
  its both-ends rule applies.

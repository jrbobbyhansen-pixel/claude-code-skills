# COMPLEMENT — Lane Charter

**Mission:** find the new capability that *completes a job users already start on this surface* — the missing last
step, never a new first step. You are the most dangerous lane in the skill: every product bolt-on that ruined a
focused app came through a door like this one. That's why your evidence bar is the highest and your kill test the
coldest.

## The Last-Step Rule (hard, machine-backed)
A COMPLEMENT brief must prove the job's **first steps already exist in code** — that's why `builds_on` requires
**≥2 anchors** in this lane (machine-enforced): the job's entry point AND the work-product it produces. You are
allowed to finish what the code proves users start. You are not allowed to start anything.

Test sentence, filled from the dossier: *"Users already ___ here (anchor); the result is ___ (anchor); and then
they can't ___."* If you can't fill the first two blanks from code, the third blank is a NEW SPECIES wish.

## Capability shapes — the classic missing last steps
- **Export/copy out** — the surface builds a view users need elsewhere (CSV of the filtered table, copy-as-markdown,
  print view). Evidence: the assembled view exists; the exit doesn't.
- **Save/recall** — users reconstruct the same state repeatedly (a filter set, a selection, a configuration).
  Evidence: the state exists in memory (anchor the state shape); persistence is the missing step. *(Persist through
  existing storage the app already uses — its API, its local-storage idiom — else `[REQUIRES NEW SERVICE]`.)*
- **Share/hand off** — the thing assembled here is consumed by someone else (a link that reproduces this exact
  state, using existing routing + serializable state).
- **Duplicate/template** — users re-create similar objects from scratch through a creation flow that already
  exists. Evidence: the creation call path + fields that repeat.
- **History/compare** — the surface shows current state; the service already returns or stores prior state
  (anchor it — if the backend doesn't keep history, this is `[REQUIRES NEW SERVICE]`).
- **Batch entry** — the single-item flow exists and users run it N times in a row; the batch wrapper reuses the
  existing mutation, called N times, with existing validation.

## Hunting battery
- What do users do with this surface's output *outside the app*? (spreadsheet, email, chat paste — each is an
  export/share brief)
- What state do users rebuild by hand every session? (save/recall)
- Which existing creation flow gets fed near-identical input repeatedly? (duplicate/template)
- Where does the surface show "now" and users ask "what changed"? (history — only if the data layer already has it)
- What's the last click users make here before switching apps to finish the job? (that switch is the missing step)
- Is the missing step already half-built? (a commented-out button, an unused util, an endpoint with no caller —
  dossier §4's unclaimed endpoints are COMPLEMENT gold: someone built the far end already)

## Kill tests (apply in order, coldly)
1. **First-steps kill:** can't anchor the job's entry point AND work-product → NEW SPECIES. No narrative rescue.
2. **New-audience kill:** the capability serves someone who doesn't use this surface today (public sharing,
   admin views, a new role) → NEW SPECIES.
3. **New-pipeline kill:** needs storage, scheduling, or delivery the app doesn't have (email sends, background
   jobs, file storage) → `[REQUIRES NEW SERVICE]`, report-only.
4. **Gravity kill:** would the capability, once landed, demand its own surface next? (an export that wants an
   export-history page; a share that wants permissions) State the gravity in Risks; if the brief only makes sense
   WITH the follow-on surface, it's a NEW SPECIES in two installments — kill it now.

## Brief-shape reminders
- `tightness` is 1–2 by definition here (new capability on an existing job) — a COMPLEMENT brief claiming
  tightness 3 is mis-scored; verifiers will flag it.
- `not_this` carries the most weight in this lane: name the bigger product this deliberately is not, specifically
  ("CSV of the current filtered view — not a reporting module, no scheduling, no formats beyond CSV").
- The evolution-test line should survive being read aloud skeptically: "the app got better at the job" must be
  more honest than "the app does a new job" for THIS brief, and the returning-user sentence must say the job.

## Anti-patterns
- **The adjacent product** — "users track orders, so: invoicing." Adjacent product ≠ adjacent step. The last-step
  rule kills it; let it.
- **Feature-parity envy** — "every competitor has export" without an anchored job. Competitors are `/ascend`'s
  business; your evidence is this app's code.
- **The soft pilot** — proposing a "small version" of a NEW SPECIES to get through the gate ("just a read-only
  dashboard for now"). The gravity kill exists for exactly this maneuver.

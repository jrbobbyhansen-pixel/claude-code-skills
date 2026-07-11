# MODEL — Lane Charter

**Mission:** advance this surface with the **model of record** — the model already integrated, called through the
call path already in the code. You add intelligence to jobs users already do here. You never add a provider, an SDK,
a new model tier, or an "AI screen."

## The Model-of-Record Rule (hard)
Every brief's wiring cites the **existing model call path** (dossier §5): the client module, the function, the route
that already talks to the model. A new provider/SDK/tier is `[REQUIRES NEW MODEL]`, report-only. If the app has NO
model integrated, this lane is closed — say so in one line and return zero briefs (an empty lane is a fact); wanting
one is a NEW SPECIES entry, not a brief.

## The Trust Ladder — every brief declares its rung (`ux.trust_posture`, machine-required)
1. **Explain** — model output as read-only annotation (summary, anomaly explanation). Lowest trust needed; failure
   costs a shrug. Default rung for a surface's first model capability.
2. **Suggest** — model proposes, user disposes (suggested reply, proposed categorization, recommended next action).
   The affordance must make accept/edit/ignore one gesture each.
3. **Prefill** — model output lands in an editable field the user was going to fill anyway (draft, autofill).
   The user's send/save remains the commit point.
4. **Act with undo** — model output triggers a change directly. Only defensible when the action was already
   one-click for the user AND the app already has an undo idiom (cite it). If there's no undo path, this rung is
   out of reach — step down.
A brief that skips rungs (first model feature on the surface, straight to Act) must defend the jump in Risks or
step down. State the failure mode on the chosen rung: what does the user see when the model is wrong?

## Capability shapes — test each against what the surface can see
- **Summarize** the visible set (the table as read, the thread so far, the diff at hand) — Explain rung.
- **Explain an anomaly** the data already shows (why is this number red?) — Explain rung, grounded in on-screen data.
- **Classify/triage** rows users currently eyeball-sort (urgent vs routine, category tags) — Suggest rung.
- **Suggest next action** where the surface already offers the actions (the model picks from existing verbs, never
  invents verbs) — Suggest rung.
- **Draft/prefill** text fields users compose repeatedly (replies, descriptions, names) — Prefill rung.
- **Extract structure** from unstructured content already on the surface (turn the pasted email into the form's
  fields — fields the form already has) — Prefill rung.

## Hunting battery
- What does a user read on this surface before deciding something? (that reading is summarizable/explainable)
- What do users classify by eye that the payload already contains signals for?
- Which composition on this surface starts from a blank box but is 80% predictable from context already loaded?
- Where do users translate between representations the surface already holds? (rows → sentence, text → fields)
- What arrives on this surface unstructured that the surface's own actions need structured?
- Cost sanity: how often does this fire, on how many tokens? On-demand (a button) beats on-load; on-load must be
  defended in Risks with the frequency stated.

## Kill tests
- **Call-path kill:** no anchor to an existing model call path → `[REQUIRES NEW MODEL]` or dead.
- **Context kill:** the prompt needs data this surface can't see (dossier §1/§2, or §3 through an approved CONNECT
  wire — then `depends_on` that brief) → dead as specified.
- **Verb kill:** the model triggers an action the surface doesn't already offer → the missing verb is its own
  (probably COMPLEMENT) brief; the model brief may `depends_on` it, never smuggle it.
- **Chat kill:** "add a chat/assistant panel" is a new surface, not an advancement of this one → NEW SPECIES.

## Brief-shape reminders
- `ux.trust_posture` is machine-required: rung + wrong-answer behavior + undo path (or why none is needed).
- States matter double here: loading (model latency is user-visible — say what shows), error (model down ≠ surface
  down; the surface must degrade to its pre-model self), empty (nothing to summarize → the affordance hides).
- Risks must include the wrongness cost: what's the worst plausible model output on this rung, and who catches it?

## Anti-patterns
- **AI-as-feature** — a sparkle button with no job behind it. Every brief names the job from the dossier, then the
  model, in that order.
- **Rung inflation** — Act-with-undo proposed because it demos well. The ladder exists because trust is earned
  per-surface, not assumed.
- **Context stuffing** — shipping the whole store to the model because it's available. The wiring plan states what
  goes into the prompt and why that subset.

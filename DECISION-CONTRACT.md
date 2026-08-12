# The Decision Contract

*A shared interaction standard for every skill in this library.*

These skills are strong at analysis and weak at handoff. A run does an enormous
amount of work — reads the tree, casts desks, scores findings, verifies
citations — and then ends by handing the operator a flat menu:

```
Apply? [ ALL · by desk · pick <ids> · none ]
```

Every fact needed to answer that question was just computed. The skill knows
which findings are mechanical and which are taste, which are backed up and which
touch a dependency, which are on the critical path and which are cosmetic. Then
it throws all of that away and asks the operator to re-derive the decision from a
list. **That is the back-and-forth.** Not the analysis — the handoff.

The contract below is what every skill owes the operator at a decision point. It
is stated once here, and enforced inline in each skill (skills are installed
individually, so each must stand alone).

---

## D1 — Every gate ships a default

**A menu without a recommendation is unfinished work.**

A skill that has done the analysis must state what it would do. Not as a
suggestion buried under options — as the pre-selected answer, with the operator's
cheapest possible action being acceptance.

```
RECOMMENDED — apply 14 of 19  (all OBJECTIVE + CONVENTION, all reversible)
  Holding back: 3 TASTE · 1 REQUIRES-DEP · 1 CONFLICT   → listed below, name them to include

Reply `go` to take the recommendation · `go except 7,12` · `pick 3,9,14` · `none`
```

`go` is one token. Composing a considered subset is a paragraph. The default must
be the thing you'd have chosen anyway most of the time, so that most of the time
the interaction costs one word.

**Test:** if the operator replies `go` on every run for a month and the outcome
is what they wanted, the default is calibrated. If they routinely edit it, the
default is wrong — fix the default, not the operator.

---

## D2 — Reversibility decides what's in the default

**A default is only safe to accept blindly if everything in it is cheap to undo.**

Every proposed action carries exactly one class:

| Class | Meaning | In the default? |
|---|---|---|
| `[REVERSIBLE]` | Backed up or branch-isolated; one command undoes it | **Yes** — automatically |
| `[STICKY]` | Undoable, but by hand — migrations with a down path, config edits | No — named individually |
| `[ONE-WAY]` | Cannot be undone — installed deps, pushed commits, dropped data, sent mail | **Never** — explicit yes, every time |

This is what makes D1 safe rather than reckless. The operator accepting a default
is not accepting risk; they're accepting a bundle the skill has already proven is
recoverable. Anything that can't be walked back gets its own sentence and its own
yes.

The class is computed, never asserted. If a skill can't prove a change is
reversible — no backup written, no branch, no snapshot — it is not `[REVERSIBLE]`.

---

## D3 — Bounded intake, stated assumptions

**"Ask until nothing is unknown" is an unbounded loop with a human in it.**

Interrogation has a budget. When the budget is spent, remaining unknowns do not
block the run — they become *assumptions stated out loud* and written to the
run's state.

1. **Read before asking.** Any question the codebase can answer is not a question.
   This is already the rule in `/gauntlet` and `/grill-me`; it is now universal.
2. **Every question ships with its own answer.** The skill's best guess, plus the
   evidence behind it, so the operator confirms or corrects rather than composes
   from nothing.
3. **Hard cap per phase.** A number, declared in the skill. Not "as many as it
   takes."
4. **At the cap, assume out loud.** Unresolved unknowns are written to an
   **Assumption Ledger** — each one carrying what was assumed, why that default,
   and what breaks if it's wrong. The run proceeds.

The old rule was *if you'd have to assume it, you must ask it.* The new rule is
**ask once, then assume it in writing.** A visible wrong assumption gets corrected
in one turn. A blocked run gets abandoned.

---

## D4 — One verdict, imperative mood

**Uncertainty belongs in a number, not in a verb.**

Terminal output states exactly one recommended action, in the imperative. These
words are banned from a verdict line: *consider, might, could, maybe, possibly,
perhaps, potentially, it depends, you may want to, options include.*

- Bad: *You might consider addressing the auth findings before launch, though it
  depends on your risk tolerance.*
- Good: **Fix the 3 auth P0s before launch. Confidence 85%. Reverses if the
  pen-test clears them.**

Every verdict carries three things and stops:

- **The call** — one action, imperative.
- **The confidence** — a number, so doubt is legible without being wishy-washy.
- **The reversal trigger** — what evidence would change this call. This is where
  genuine uncertainty goes; it is far more useful than a hedged verb.

Disagreement is not hedging. When a deliberation genuinely deadlocks, the verdict
is *"deadlocked — here is the tension, here is the tiebreaker to go get."* That's
still one call, stated plainly.

---

## D5 — Batch the gates

**N passes should cost one decision, not N decisions.**

A loop that stops after every pass costs the operator a full context reload each
time. Multi-pass skills declare their gate policy **once, upfront**, then run
unattended while conditions hold:

```
GATE POLICY (declared at start, one decision covers the run)
  Auto-advance while:  verify tier ≥ render-tested · zero new test failures · no [ONE-WAY] · no TASTE
  Stop immediately on: any flag above · confidence < 0.8 · graveyard kill of a top-3 candidate
  Otherwise:           run all 3 passes, present one combined diff at the end
```

The operator sets the tripwires once and reviews once. Anything that trips a wire
stops the loop *at that point* and surfaces immediately — so batching never means
finding out late.

---

## Applying the contract

| Rule | Kills | Applied in |
|---|---|---|
| D1 Default | Menu paralysis | `/polish` `/feel` `/triptych` `/gauntlet` `/ascend` |
| D2 Reversibility | Fear of accepting a default | `/polish` `/feel` `/ascend` `/gauntlet` |
| D3 Bounded intake | Unbounded interviews | `/gauntlet` `/grill-me` |
| D4 One verdict | Hedged conclusions | `/council` `/gauntlet` `/triptych` |
| D5 Batched gates | Round-trip tax on loops | `/ascend` `/grill-me` |

**The one-line version:** the skill has already done the thinking — it must ship
the conclusion, pre-classified by what's safe to accept, and make agreement cost
one word.

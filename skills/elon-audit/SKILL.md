---
name: elon-audit
description: First-principles surgical audit of an entire codebase. Scours 100% of files via parallel agents with receipt-verified coverage (UNMAPPED must be empty), surfaces every bug/waste/risk ranked P0→P2 with exact fixes and proven-vs-suspected evidence, cross-examines its own findings with adversarial verifiers before anything executes, delivers a dependency-ordered executable plan. One command. Use when you want to ruthlessly debug, clean, and supercharge a project.
---

# Elon Audit — First-Principles Codebase Audit

Surgical, zero-mercy audit of the entire repo. Every file read. Every bug surfaced. Every fix specified to the line. Delivered as an executable plan ready to approve and run.

**Philosophy:** Delete what isn't proven. Fix what's broken. Supercharge what's verified. No vague recommendations. No nice-to-haves. Every finding ships with a specific fix or an honest `[NEEDS MANUAL CONFIRM]`.

---

## Invocation

```
/elon-audit
/elon-audit --build "xcodebuild -scheme KeepApp -destination 'platform=iOS Simulator,name=iPhone 16'"
```

Runs against current working directory. `cd` to the project first.

---

## Phase 1 — Inventory (Sense the Atoms)

**Goal:** Complete structural picture before touching anything.

1. Run `find . -type f | wc -l` and `git log --oneline -10`
2. Run pygount or cloc for LOC/language breakdown (install if missing)
3. Auto-detect build command (priority order):
   - `Package.swift` → `xcodebuild -scheme [detected] -destination 'platform=iOS Simulator,...'`
   - `package.json` with `build` script → `npm run build`
   - `package.json` without `build` → `npm ci`
   - `requirements.txt` / `pyproject.toml` → `pip install -e . && python -m pytest`
   - Multiple stacks → run all, report independently
   - None detected → emit `[NEEDS CONFIRM]`, pause for user input before continuing
4. Build the file manifest, then slice it into bounded batches — ≤15 files or ≤2,500 LOC per agent, whichever binds
   first (split oversized
   directories, merge tiny ones). Spawn parallel Agent subagents, one per slice, 3 at a time, sequential between
   batches. Each agent reads 100% of its slice and returns structured findings `{file, line, type, severity,
   evidence, fix}` PLUS `covered_files[]` — its coverage receipt.
5. Stitch the receipts: `UNMAPPED = manifest − ∪covered_files`. UNMAPPED ≠ ∅ → dispatch a sweeper agent for the
   remainder and re-assert. The audit does not proceed past Phase 1 until UNMAPPED = ∅ — **coverage is proven,
   never claimed.**
6. Collect all findings. Deduplicate. Build dependency graph across all findings.

**Output:**
```
INVENTORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total files:     N
Total LOC:       N
Primary stack:   [detected]
Build command:   [detected or confirmed]
Agents spawned:  N across N slices
Coverage:        N/N files read — UNMAPPED: 0 ✓ (receipt-verified)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Phase 2 — Physics Test (Prove It Works)

**Goal:** Verify current build state. Non-blocking.

1. Run detected build command. Timeout = 300s.
2. Capture: exit code, warnings, errors, build time.
3. Build success → note warning count. Continue.
4. Build failure → capture exact errors. Auto-promote to P0. Continue — do not abort.
5. If build succeeds: smoke-test core paths (auth, main feature, network layer). Log pass/fail.

**Output:**
```
PHYSICS TEST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Build:    PASS / FAIL
Warnings: N
Errors:   N  (→ P0 auto-promoted)
Time:     Ns
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## The Finding Contract (applies to every finding, wherever raised)

Every finding carries `evidence` — no naked findings:
- **[PROVEN]** — executed or traced this run: the failing command + output, the zero-caller grep transcript, the
  exact call path. Proven findings may auto-execute in their tier.
- **[SUSPECTED]** — pattern-matched, not yet demonstrated. A suspected P0 MUST be proven (execute or trace it) or
  downgraded to `[NEEDS MANUAL CONFIRM]` before the execution phase — no exceptions. Suspected P1/P2 execute only
  behind their tier's build gate.

Schema: `{file, line, type, severity, evidence: proven|suspected, fix}`.

---

## Phase 3 — Delete/Trim (Ruthless 80/20)

**Goal:** Surface everything that shouldn't exist. Every finding includes exact file path, exact line(s), exact removal command or diff.

- **Dead code**: functions/classes with zero callers (grep-verified), `_disabled_` prefixes, commented-out blocks >20 LOC
- **Unused dependencies**: zero imports in codebase — exact `npm uninstall X` or SPM removal
- **Duplicate logic**: identical blocks >10 LOC — exact unification diff
- **TODO/FIXME**: every instance, classified P0/P1/P2 by context
- **Deprecated APIs**: exact replacement for each call
- **Asset bloat**: unused image/media assets, uncompressed assets over 500KB — exact removal or compression command
- **Debug logs in production**: `print()`, `console.log()`, `NSLog()` not gated by debug flag — exact removal or `#if DEBUG` wrap

---

## Phase 4 — Risk/Edge Proof (Infinite Loop)

**Goal:** Surface everything that will bite you. Every finding includes exact fix.

**P0 — Kill Shots (fix first, no exceptions):**
- Force-unwraps on live execution paths
- Missing auth checks on API endpoints, Supabase RPC calls, or protected routes
- Data loss paths (unguarded deletes, missing CoreData/Realm migrations)
- Security: hardcoded secrets (`sk_live_`, `Bearer `, `password =`, `.env` values committed to git)
- Security: RLS not enabled on Supabase tables holding user data
- Security: `.gitignore` missing coverage for `.env`, `secrets/`, credential files
- Security: entitlements mismatched to build target, debug entitlements in release
- Dependency CVEs at critical/high severity — exact `npm audit fix` or package update command
- Race conditions / unprotected shared mutable state / `@MainActor` violations
- Build errors (promoted from Phase 2)

**P1 — Performance & Waste:**
- Memory leaks and retain cycles (ARC) — exact `[weak self]` or `unowned` fix
- Synchronous operations on main thread — exact `Task {}` or `DispatchQueue.global()` migration
- Redundant network calls — exact deduplication fix
- O(n²) loops with known-bounded inputs — exact algorithm replacement
- Missing error handling on critical paths (auth, payments, persistence)
- Broken or skipped tests (`XCTSkip`, `.skip`, `.only` left in) — exact fix or deletion
- Test coverage gaps on P0 paths (auth, payments, data persistence) — exact test stubs to add
- Dependency CVEs at medium severity
- Build warnings that will become errors — exact fix per warning

**P2 — Supercharge:**
- Half-implemented features with clear scaffolding and obvious intent — exact completion diff
- Verifiable performance improvements (O(n log n) replacements, caching opportunities) — exact diff
- Duplicate logic unification — exact refactor
- Localization gaps — hardcoded user-facing strings — exact `.strings` extraction
- CoreData/Realm schema changes without migration paths — exact migration stub
- iOS App Store compliance: privacy manifest gaps, deprecated API usage before deployment target — exact fixes
- Build config hygiene: debug flags in release, version/build number mismatches across targets — exact fixes
- Documentation gaps on public APIs — exact docstring additions
- New features ONLY if directly implied by existing scaffolding (half-built, intent obvious)

**Dependency rule:** If any fix depends on another fix in a lower tier, that dependency is promoted up. The dependency graph built in Phase 1 is enforced throughout execution. Nothing moves down until its tier is 100% complete and verified.

---

## Phase 4.5 — Cross-Examination (The Maker Never Grades Itself)

Before anything executes: spawn adversarial verifier agents with fresh context — they see the findings and the code,
never the authoring reasoning. Their single job is to REFUTE.

1. Every P0 gets a verifier; P1/P2 get a ≥20% sample (the whole tier if it's small).
2. A verifier re-derives the finding from the code: reproduce the proof, or produce the counter-evidence. A verifier
   that independently demonstrates a [SUSPECTED] finding upgrades it to [PROVEN].
3. Refuted → cut or downgraded, refutation logged in the report; a refuted finding's dependents are re-checked
   before the plan is presented. Survived → confirmed.
4. Report the kill rate honestly: `P0: 12 raised → 9 confirmed · 3 refuted`. A 0% refute rate on a large audit is a
   smell, not a flex.

Only **confirmed** findings enter the executable plan as P0s. Unexamined P1/P2 findings enter the plan **as raised**
— their tier's build gate is their check; "confirmed" means *not refuted*. If the sample's refute rate exceeds ~20%,
widen the sample before presenting the plan.

---

## Phase 5 — Handoff (Holy Shit Done)

1. Write `AUDIT.md` to repo root — full findings (with evidence + cross-exam stats), fix list, tier breakdown,
   before/after stats
2. If `~/clawd/wiki/` exists: write the audit note to `~/clawd/wiki/systems/[appname]-audit-YYYY-MM-DD.md` (format
   below) and update `~/clawd/wiki/projects/[appname].md` with `Last audited: YYYY-MM-DD → [[systems/...]]`.
   If it doesn't exist: skip both and say so — never invent the tree.
3. Update Claude auto-memory: project name, audit date, P-tiers completed, top 3 findings, health status

---

## Execution Flow

After the audit report is presented inline, enter plan mode with the full fix list.

On approval:
1. Execute all **confirmed** P0 fixes (proven + cross-examined; anything else is `[NEEDS MANUAL CONFIRM]`) → run
   build → confirm passes → `git commit -m "[elon-audit] P0: kill shots — N fixes"`
2. Execute all P1 fixes → run build → confirm passes → `git commit -m "[elon-audit] P1: performance & waste — N fixes"`
3. Execute all P2 fixes → run build → confirm passes → `git commit -m "[elon-audit] P2: supercharge — N fixes"`
4. Run Phase 5 Handoff

If build fails after any tier: stop, surface the regression, fix before moving to next tier.

After all tiers committed:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Audit complete. Run /elon-audit again to verify zero new findings.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Audit Report Format (Inline)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ELON AUDIT — [PROJECT NAME]
[DATE] | [N] LOC | [N] files | [STACK]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INVENTORY        [summary] — Coverage: N/N files, UNMAPPED: 0 ✓
PHYSICS TEST     PASS/FAIL — N warnings, N errors
CROSS-EXAM       P0: N raised → N confirmed · N refuted | P1/P2 sample: N checked → N confirmed

P0 KILL SHOTS    N confirmed
──────────────────────────────────────────────────
[ID]  [file:line]  [PROVEN|SUSPECTED]  [issue]
      FIX: [exact command or diff]

P1 PERF/WASTE    N confirmed
──────────────────────────────────────────────────
[ID]  [file:line]  [PROVEN|SUSPECTED]  [issue]
      FIX: [exact command or diff]

P2 SUPERCHARGE   N confirmed
──────────────────────────────────────────────────
[ID]  [file:line]  [PROVEN|SUSPECTED]  [issue]
      FIX: [exact command or diff]

DEPENDENCY ORDER
──────────────────────────────────────────────────
[Any promotions or reorderings]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: N fixes | 3 commits | Build gate per tier
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Obsidian Wiki Note Format

`~/clawd/wiki/systems/[appname]-audit-YYYY-MM-DD.md`:

```markdown
---
title: [AppName] Elon Audit
type: audit
project: [appname]
date: YYYY-MM-DD
status: complete
p0: N
p1: N
p2: N
---

# [AppName] Audit — YYYY-MM-DD

## Summary
[1-3 sentence executive summary]

## Top Findings
- P0: [top finding]
- P1: [top finding]
- P2: [top finding]

## Health
LOC before/after: N → N
Warnings before/after: N → N
Build time before/after: Ns → Ns

## Full Report
→ AUDIT.md in repo root
```

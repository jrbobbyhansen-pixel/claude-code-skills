#!/usr/bin/env python3
"""Mechanically enforce the Decision Contract (DECISION-CONTRACT.md) across every skill.

Prose rules rot. This is the enforcement half: it reads every skills/*/SKILL.md and
fails the build on a contract regression. Same philosophy the skills themselves run on —
coverage is proven, never claimed.

Usage:
    python3 scripts/check_decision_contract.py            # check all skills
    python3 scripts/check_decision_contract.py polish     # check one
    python3 scripts/check_decision_contract.py --verbose  # show every check, not just failures

Exit code 0 = clean, 1 = at least one FAIL.

A skill may declare a rule inapplicable with an inline HTML comment:

    <!-- contract: D2 n/a - read-only skill, applies no changes -->

Exemptions are always REPORTED, never silent: a rule you opted out of shows up as
N/A with its stated reason in the output. An unexplained exemption is itself a failure.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"

# D4: banned in a verdict line. Uncertainty belongs in a confidence number, not a verb.
HEDGES = [
    "consider", "might", "maybe", "could be", "possibly", "perhaps",
    "potentially", "it depends", "options include", "you may want",
]

# Lines that DECLARE the ban (or quote it) are not violations of it.
META = re.compile(
    r"banned|ban-list|uncertainty goes|never a hedged|hedge|D4\b|decision contract",
    re.I,
)

# A verdict line: where the skill states its call.
VERDICT = re.compile(r"RECOMMENDED|THE CALL|verdict:|GO/NO-GO", re.I)

# A menu: options separated by middots, ending in an escape hatch.
MENU = re.compile(r"(Ask:|Apply\?|`go`).*·.*(none|pick|keep the incumbent)", re.I)

# D3: unbounded-intake language.
UNBOUNDED = re.compile(
    r"not capped at a question count|as many as it takes|no cap on questions"
    r"|until (?:every|all)[^.]{0,60}(?:are|is) (?:facts|resolved)(?![^.]{0,200}budget)",
    re.I,
)
BUDGETED = re.compile(
    r"capped at|≤\s*\d+\s*Q|\bask once\b|budget|at most one|one round|never a third"
    r"|assumption ledger|whichever comes first"
    # a cap stated in prose counts too: "3-4 questions max", "state assumptions"
    r"|\d+\s*[-–]?\s*\d*\s*questions? max|asking only what|state assumptions",
    re.I,
)

# D2: a skill that mutates the tree must class its changes.
# Deliberately narrow: the bare word "apply" appears in ordinary prose ("apply the
# Idiot Index", "apply pressure") and matching it flags read-only skills. Require a
# signal that files actually change.
MUTATES = re.compile(
    r"Apply\?|apply gate|--apply\b|apply the (?:edit|fix|patch)|apply via Edit|the Edit tool"
    r"|Execute (?:all|top|the)|execute P0|git commit|open(?:s)? a PR|merge .{0,20}branch"
    # build-on-a-branch skills mutate too, and say so in their own vocabulary
    r"|dedicated branch|throwaway branch|Never on main|implement the pick|delete the los",
    re.I,
)

# D5: a skill that runs multiple passes must declare its gate policy once.
MULTIPASS = re.compile(r"≥3 passes|multi-pass|each pass|per-pass|N passes|passes that escalate", re.I)
GATEPOLICY = re.compile(r"GATE POLICY|--gate|batched(?: gate)?|tripwire|batched slate", re.I)

EXEMPT = re.compile(r"<!--\s*contract:\s*(D[1-5])\s*n/a\s*[-–—:]\s*(.+?)\s*-->", re.I)


class Result:
    __slots__ = ("skill", "rule", "status", "detail")

    def __init__(self, skill, rule, status, detail=""):
        self.skill, self.rule, self.status, self.detail = skill, rule, status, detail


class Skill:
    """A skill is its SKILL.md plus every markdown file it reads mid-run.

    Intake templates, output templates, scoring rubrics and role charters all carry
    decision points, so checking SKILL.md alone reports false N/A. The corpus is
    every .md in the skill folder; `entry` is SKILL.md on its own where a rule is
    genuinely about the entry point.
    """

    def __init__(self, path):
        self.name = path.parent.name
        self.entry = path.read_text(encoding="utf-8")
        self.docs = []  # [(relpath, text)]
        for md in sorted(path.parent.rglob("*.md")):
            self.docs.append((md.relative_to(path.parent).as_posix(),
                              md.read_text(encoding="utf-8")))
        self.all = "\n".join(t for _, t in self.docs)
        self.exempt = {m.group(1).upper(): m.group(2) for m in EXEMPT.finditer(self.all)}


def scan_lines(skill, predicate):
    """Yield (relpath, lineno, line) for every line matching predicate, across the skill."""
    for rel, text in skill.docs:
        for i, ln in enumerate(text.split("\n")):
            if predicate(ln):
                yield rel, i + 1, ln


def check_d1_default(s):
    """Every menu ships a pre-selected recommendation."""
    if "D1" in s.exempt:
        return Result(s.name, "D1", "N/A", s.exempt["D1"])
    offenders = []
    for rel, text in s.docs:
        ls = text.split("\n")
        for i, ln in enumerate(ls):
            if not MENU.search(ln) or META.search(ln):
                continue
            window = "\n".join(ls[max(0, i - 12): i + 4])
            if not re.search(r"RECOMMENDED", window):
                offenders.append(f"{rel}:{i + 1}")
    if offenders:
        return Result(s.name, "D1", "FAIL",
                      f"menu with no RECOMMENDED nearby — {', '.join(offenders)}")
    return Result(s.name, "D1", "PASS")


def check_d2_reversibility(s):
    """A skill that mutates the tree classes its changes by reversibility."""
    if "D2" in s.exempt:
        return Result(s.name, "D2", "N/A", s.exempt["D2"])
    if not MUTATES.search(s.all):
        return Result(s.name, "D2", "N/A", "applies no changes")
    # The taxonomy must be stated at the entry point — it is a contract with the
    # operator, not an implementation detail buried in a reference.
    has_rev = "[REVERSIBLE]" in s.entry
    has_one = "[ONE-WAY]" in s.entry
    if has_rev and has_one:
        return Result(s.name, "D2", "PASS")
    missing = [t for t, ok in (("[REVERSIBLE]", has_rev), ("[ONE-WAY]", has_one)) if not ok]
    return Result(s.name, "D2", "FAIL",
                  f"mutates the tree but SKILL.md never declares {' or '.join(missing)}")


def check_d3_bounded(s):
    """Intake is capped; unknowns become stated assumptions, not blockers."""
    if "D3" in s.exempt:
        return Result(s.name, "D3", "N/A", s.exempt["D3"])
    for rel, text in s.docs:
        m = UNBOUNDED.search(text)
        if m:
            return Result(s.name, "D3", "FAIL",
                          f"unbounded intake in {rel}: {m.group(0)[:48]!r}")
    # Narrow on purpose: personas and doctrine say "ask" constantly as a reasoning
    # style ("Always ask: who is the customer"). Only operator-facing intake counts.
    if not re.search(r"AskUserQuestion|\bintake\b|interview|\bGRILL\b|grill the"
                     r"|asking only what|questions? max|[Ss]cope lock",
                     s.all):
        return Result(s.name, "D3", "N/A", "asks the operator nothing")
    if BUDGETED.search(s.all):
        return Result(s.name, "D3", "PASS")
    return Result(s.name, "D3", "FAIL", "questions the operator but declares no budget")


def check_d4_verdict(s):
    """No hedge words in a verdict line — or in the lines that state that verdict.

    Checking only the marker line misses the realistic failure: a heading like
    '### THE CALL' followed by a hedged sentence underneath it. The verdict is the
    whole block, so the block is what gets checked.
    """
    if "D4" in s.exempt:
        return Result(s.name, "D4", "N/A", s.exempt["D4"])
    offenders = []
    for rel, text in s.docs:
        ls = text.split("\n")
        for i, ln in enumerate(ls):
            if not VERDICT.search(ln) or META.search(ln):
                continue
            # The marker line plus the block it introduces, to the next blank line
            # (cap at 4 so a heading never swallows a whole section).
            block = [(i, ln)]
            for j in range(i + 1, min(i + 5, len(ls))):
                if not ls[j].strip():
                    break
                block.append((j, ls[j]))
            for n, bl in block:
                if META.search(bl):
                    continue
                for h in HEDGES:
                    if re.search(rf"\b{re.escape(h)}\b", bl, re.I):
                        offenders.append(f"{rel}:{n + 1} ({h})")
    if offenders:
        return Result(s.name, "D4", "FAIL",
                      f"hedge in verdict block — {', '.join(sorted(set(offenders)))}")
    return Result(s.name, "D4", "PASS")


def check_d5_batched(s):
    """A multi-pass loop declares its gate policy once, upfront."""
    if "D5" in s.exempt:
        return Result(s.name, "D5", "N/A", s.exempt["D5"])
    if not MULTIPASS.search(s.entry):
        return Result(s.name, "D5", "N/A", "single-pass")
    if GATEPOLICY.search(s.entry):
        return Result(s.name, "D5", "PASS")
    return Result(s.name, "D5", "FAIL", "multi-pass but declares no batched gate policy")


CHECKS = [check_d1_default, check_d2_reversibility, check_d3_bounded,
          check_d4_verdict, check_d5_batched]


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("-")]
    verbose = any(a in ("-v", "--verbose") for a in sys.argv[1:])

    paths = sorted(SKILLS.glob("*/SKILL.md"))
    if argv:
        want = set(argv)
        paths = [p for p in paths if p.parent.name in want]
        if not paths:
            print(f"no such skill: {', '.join(argv)}", file=sys.stderr)
            return 2

    results = []
    for p in paths:
        skill = Skill(p)
        for check in CHECKS:
            results.append(check(skill))

    fails = [r for r in results if r.status == "FAIL"]
    nas = [r for r in results if r.status == "N/A"]

    width = max(len(r.skill) for r in results) + 1
    shown = results if verbose else fails
    if shown:
        print(f"\n{'skill':<{width}} rule  status  detail")
        print("─" * 78)
        for r in shown:
            print(f"{r.skill:<{width}} {r.rule:<5} {r.status:<7} {r.detail}")

    skills_n = len({r.skill for r in results})
    print(f"\n{len(results)} checks over {skills_n} skills · "
          f"{len(results) - len(fails) - len(nas)} pass · {len(nas)} n/a · {len(fails)} fail")

    # Exemptions are surfaced, never silent — a rule opted out of is still reported.
    declared = [r for r in nas if r.detail and not r.detail.startswith(
        ("applies no changes", "asks the operator nothing", "single-pass"))]
    if declared:
        print("\ndeclared exemptions:")
        for r in declared:
            print(f"  {r.skill} {r.rule} — {r.detail}")

    if fails:
        print(f"\nFAIL — {len(fails)} contract violation(s). See DECISION-CONTRACT.md.")
        return 1
    print("\nOK — every skill honours the Decision Contract.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

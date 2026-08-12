#!/usr/bin/env python3
"""Prove the Decision Contract checker can actually fail.

A checker that only ever returns green is decoration. This injects a known
regression for each rule into a throwaway copy of the skills tree and asserts the
matching check goes FAIL. If a rule stops catching its own regression, this fails
the build even though check_decision_contract.py is still green — which is the
exact failure mode a linter dies of.

Usage:  python3 scripts/selftest_decision_contract.py
Exit 0 = every rule still bites.
"""

import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_decision_contract import (  # noqa: E402
    Skill, check_d1_default, check_d2_reversibility,
    check_d3_bounded, check_d4_verdict, check_d5_batched,
)

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"

# (rule, skill, check fn, description, mutation applied to that skill's SKILL.md)
CASES = [
    ("D1", "polish", check_d1_default,
     "strip the recommendation, leaving a bare menu",
     lambda t: t.replace("RECOMMENDED — apply <n> of <N>",
                         "Apply? [ ALL · by desk · pick <ids> · none ] <n> of <N>")),

    ("D2", "ascend", check_d2_reversibility,
     "rename the reversibility classes to untyped labels",
     lambda t: t.replace("[REVERSIBLE]", "[SAFE]").replace("[ONE-WAY]", "[RISKY]")),

    ("D3", "gauntlet", check_d3_bounded,
     "restore the unbounded interview",
     lambda t: t.replace("**Stop condition = the budget, not the unknowns**",
                         "**Stop condition = zero guessing.** Not capped at a question count.")),

    ("D4", "council", check_d4_verdict,
     "hedge the line underneath the verdict heading",
     lambda t: t.replace("### THE CALL",
                         "### THE CALL\nYou might want to pick whichever seems best.")),

    ("D5", "ascend", check_d5_batched,
     "remove the declared gate policy from a multi-pass loop",
     lambda t: re.sub(r"GATE POLICY|--gate|batched|tripwires?", "gate", t, flags=re.I)),
]


def main():
    failures = []
    print(f"{'rule':<5} {'skill':<10} {'result':<8} case")
    print("─" * 78)

    for rule, skill_name, check, desc, mutate in CASES:
        with tempfile.TemporaryDirectory() as tmp:
            dst = Path(tmp) / skill_name
            shutil.copytree(SKILLS / skill_name, dst)
            entry = dst / "SKILL.md"

            # Sanity: the unmutated copy must pass, or the test proves nothing.
            before = check(Skill(entry))
            if before.status == "FAIL":
                failures.append(f"{rule}/{skill_name}: baseline already FAILs — {before.detail}")
                print(f"{rule:<5} {skill_name:<10} {'BASELINE':<8} {desc}")
                continue

            entry.write_text(mutate(entry.read_text(encoding="utf-8")), encoding="utf-8")
            after = check(Skill(entry))

            if after.status == "FAIL":
                print(f"{rule:<5} {skill_name:<10} {'caught':<8} {desc}")
            else:
                failures.append(
                    f"{rule}/{skill_name}: regression NOT caught "
                    f"(got {after.status}) — {desc}")
                print(f"{rule:<5} {skill_name:<10} {'MISSED':<8} {desc}")

    print()
    if failures:
        print(f"SELF-TEST FAILED — {len(failures)} rule(s) no longer catch their regression:")
        for f in failures:
            print(f"  · {f}")
        return 1
    print(f"OK — all {len(CASES)} rules still catch their regressions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

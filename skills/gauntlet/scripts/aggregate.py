#!/usr/bin/env python3
"""
gauntlet aggregate.py — the keystone. Reads desk findings JSON, VERIFIES every
citation (phantom file:line rejected), dedupes, scores per scoring-rubric.md,
computes delta vs prior run, and writes READINESS.md + updated history.

Usage:
    aggregate.py --findings .gauntlet/findings/<run> --root . \
                 --goal "payments live" --deadline 2026-05-29 \
                 [--history .gauntlet/history.json] [--out READINESS.md]

Finding schema (one JSON file per desk-section, {"desk","section","findings":[...]}):
    {file, line, type, severity:P0|P1|P2, confidence:0.5-1.0, blast:local|section|systemic,
     critical_path:bool, fix, gate_note, citation:"file:line",
     evidence:{type:cited|trace|run|mcp|NONE, verdict:PROVEN|UNPROVEN|DISPROVEN},
     status:open|resolved, id}
"""
from __future__ import annotations
import argparse, glob, hashlib, json, os, sys

SEV_W = {"P0": 40, "P1": 10, "P2": 2}
BLAST = {"local": 1.0, "section": 1.5, "systemic": 2.5}
RISK_W = {"payments": 5, "money": 5, "billing": 5, "data": 5, "auth": 4,
          "security": 4, "core": 3, "infra": 3}


def file_hash(path: str) -> str:
    try:
        return hashlib.sha1(open(path, "rb").read()).hexdigest()[:12]
    except OSError:
        return ""


def load_findings(findings_dir: str) -> list[dict]:
    out = []
    for fp in sorted(glob.glob(os.path.join(findings_dir, "*.json"))):
        try:
            blob = json.load(open(fp))
        except (OSError, json.JSONDecodeError) as e:
            print(f"  ! skipping {fp}: {e}", file=sys.stderr)
            continue
        desk, section = blob.get("desk", "?"), blob.get("section", "?")
        for f in blob.get("findings", []):
            f.setdefault("desk", desk)
            f.setdefault("section", section)
            f.setdefault("confidence", 0.7)
            f.setdefault("blast", "section")
            f.setdefault("severity", "P1")
            f.setdefault("critical_path", False)
            f.setdefault("status", "open")
            f.setdefault("evidence", {"type": "NONE", "verdict": "UNPROVEN"})
            out.append(f)
    return out


def verify_citations(findings: list[dict], root: str) -> tuple[list[dict], list[dict]]:
    """Reject any finding whose file:line does not exist. Doctrine: no phantoms."""
    kept, rejected = [], []
    for f in findings:
        path = os.path.join(root, f.get("file", ""))
        ok = bool(f.get("file")) and os.path.isfile(path)
        if ok and f.get("line"):
            try:
                n = sum(1 for _ in open(path, encoding="utf-8", errors="ignore"))
                ok = 1 <= int(f["line"]) <= n
            except (OSError, ValueError):
                ok = False
        (kept if ok else rejected).append(f)
    return kept, rejected


def dedupe(findings: list[dict]) -> list[dict]:
    by_key: dict[tuple, dict] = {}
    for f in findings:
        key = (f.get("file"), f.get("line"), f.get("type"))
        if key in by_key:
            cur = by_key[key]
            cur["desk"] = ",".join(sorted(set(str(cur["desk"]).split(",") + [str(f["desk"])])))
            if SEV_W.get(f["severity"], 0) > SEV_W.get(cur["severity"], 0):
                cur["severity"] = f["severity"]
            cur["confidence"] = max(cur["confidence"], f["confidence"])
        else:
            by_key[key] = dict(f)
    return list(by_key.values())


def is_unproven(f: dict) -> bool:
    ev = f.get("evidence", {})
    return ev.get("verdict") != "PROVEN" or ev.get("type", "NONE") == "NONE"


def eff_weight(f: dict) -> int:
    # UNPROVEN on a critical path is scored as a P0-equivalent risk
    if f["critical_path"] and is_unproven(f):
        return SEV_W["P0"]
    return SEV_W.get(f["severity"], 10)


def impact(f: dict) -> float:
    return eff_weight(f) * max(0.5, float(f["confidence"])) * BLAST.get(f["blast"], 1.5)


def score(findings: list[dict]) -> dict:
    sections: dict[str, dict] = {}
    for f in findings:
        if f["status"] != "open":
            continue
        s = sections.setdefault(f["section"], {"impact": 0.0, "p0": 0, "unproven_crit": 0,
                                               "razor": False, "findings": 0})
        s["impact"] += impact(f)
        s["findings"] += 1
        if f["severity"] == "P0":
            s["p0"] += 1
        if f["critical_path"] and is_unproven(f):
            s["unproven_crit"] += 1
        if str(f["desk"]).find("razor") >= 0 or "subtract" in f.get("type", "") or "dead" in f.get("type", ""):
            s["razor"] = True

    for name, s in sections.items():
        readiness = max(0, round(100 - s["impact"]))
        if s["p0"] or s["unproven_crit"]:
            band = "RED"
        elif not s["razor"]:
            band = "YELLOW"  # subtraction not run → cannot certify GREEN
            readiness = min(readiness, 84)
        elif readiness >= 85:
            band = "GREEN"
        elif readiness >= 60:
            band = "YELLOW"
        else:
            band = "RED"
        s["readiness"], s["band"] = readiness, band

    total_p0 = sum(s["p0"] for s in sections.values())
    total_unproven = sum(s["unproven_crit"] for s in sections.values())
    if sections:
        num = sum(s["readiness"] * RISK_W.get(n, 1) for n, s in sections.items())
        den = sum(RISK_W.get(n, 1) for n in sections)
        ship = max(0, round(num / den - 10 * total_unproven))
    else:
        ship = 0
    go = total_p0 == 0 and total_unproven == 0 and ship >= 80
    return {"sections": sections, "p0": total_p0, "unproven_crit": total_unproven,
            "ship_confidence": ship, "go": go}


def delta_line(cur: dict, hist: dict) -> str:
    if not hist:
        return ""
    def d(now, was):
        if was is None:
            return ""
        diff = now - was
        arrow = "▼" if (diff < 0 and now < was) else ("▲" if diff > 0 else "■")
        return f" ({arrow} from {was})"
    return (f"P0: {cur['p0']}{d(cur['p0'], hist.get('p0'))}   "
            f"ship-confidence: {cur['ship_confidence']}%{d(cur['ship_confidence'], hist.get('ship_confidence'))}")


def reopened_green(hist: dict, root: str) -> list[str]:
    out = []
    for g in (hist or {}).get("proven_green", []):
        f = g.get("file")
        if f not in out and file_hash(os.path.join(root, f or "")) != g.get("hash"):
            out.append(f)
    return out


def render(cur, rejected, hist, root, goal, deadline) -> str:
    L = []
    L.append("# READINESS — gauntlet\n")
    L.append(f"**Goal:** {goal or '—'}  **Deadline:** {deadline or '—'}\n")
    verdict = "GO" if cur["go"] else "NO-GO"
    blockers = []
    if cur["p0"]:
        blockers.append(f"{cur['p0']} P0")
    if cur["unproven_crit"]:
        blockers.append(f"{cur['unproven_crit']} UNPROVEN critical path")
    tail = f" — {' + '.join(blockers)} between you and ship." if blockers else ""
    L.append(f"## VERDICT: **{verdict}**  (ship-confidence {cur['ship_confidence']}%){tail}\n")
    dl = delta_line(cur, hist)
    if dl:
        L.append(f"_{dl}_\n")
    ro = reopened_green(hist, root)
    if ro:
        L.append(f"_Re-opened (files changed since proven-green): {', '.join(ro)}_\n")

    L.append("\n## Sections (worst-first)\n")
    for name, s in sorted(cur["sections"].items(), key=lambda kv: kv[1]["readiness"]):
        emoji = {"GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴"}[s["band"]]
        L.append(f"- {emoji} **§{name}** — {s['readiness']}/100 · "
                 f"{s['p0']} P0 · {s['unproven_crit']} unproven-crit · {s['findings']} findings"
                 f"{'' if s['razor'] else ' · ⚠ subtraction not run'}")
    if rejected:
        L.append(f"\n## Rejected (phantom citations — file:line not found): {len(rejected)}\n")
        for f in rejected[:10]:
            L.append(f"- ~~{f.get('citation', f.get('file'))}~~ ({f.get('desk')}/{f.get('type')})")
    L.append("\n_Full punch-list, evidence ledger, and live-test scripts follow in the inline report._\n")
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Aggregate, verify, score gauntlet findings.")
    ap.add_argument("--findings", required=True)
    ap.add_argument("--root", default=".")
    ap.add_argument("--history", default=None)
    ap.add_argument("--out", default="READINESS.md")
    ap.add_argument("--goal", default="")
    ap.add_argument("--deadline", default="")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    findings = load_findings(args.findings)
    kept, rejected = verify_citations(findings, root)
    kept = dedupe(kept)
    cur = score(kept)
    hist = {}
    if args.history and os.path.isfile(args.history):
        try:
            hist = json.load(open(args.history))
        except (OSError, json.JSONDecodeError):
            hist = {}

    md = render(cur, rejected, hist, root, args.goal, args.deadline)
    open(args.out, "w").write(md)

    if args.history:
        pg = {f["file"]: file_hash(os.path.join(root, f["file"]))
              for f in kept if not is_unproven(f) and f["severity"] != "P0"}  # one entry per file
        json.dump({"p0": cur["p0"], "ship_confidence": cur["ship_confidence"], "unproven_crit": cur["unproven_crit"],
                   "sections": {n: s["readiness"] for n, s in cur["sections"].items()},
                   "proven_green": [{"file": k, "hash": v} for k, v in pg.items()]},
                  open(args.history, "w"), indent=2)

    if not args.quiet:
        print(f"verdict: {'GO' if cur['go'] else 'NO-GO'}  ship-confidence: {cur['ship_confidence']}%  "
              f"P0: {cur['p0']}  unproven-crit: {cur['unproven_crit']}  "
              f"rejected-phantoms: {len(rejected)}  → {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""evolve verify.py — the mechanical law of /evolve. stdlib only, no installs.

Three modes (run from anywhere; paths are explicit):

  --check-dossier   Audit .evolve/dossier.json: every claim's anchor must match
                    disk at the cited line, and every scan.json accounting key
                    must be covered or dismissed-with-reason. Exit 1 while any
                    anchor fails or any key is UNCHARTED — ideation is BLOCKED.

  --check-briefs    Audit .evolve/briefs/<lane>.json: hard schema rejection of
                    incomplete briefs, anchor audit against disk, COMPUTED
                    confidence (min over claims — never declared), content-hash
                    IDs, report-only flagging, duplicate detection, impact
                    scoring. Writes .evolve/briefs.verified.json.

  --slate           Render .evolve/SLATE.md from briefs.verified.json +
                    state.json (+ optional kills.json from verifier agents):
                    per-lane ranking and caps, bench, report-only section,
                    graveyard filtering, deferred resurfacing, dependency
                    apply-order (cycles flagged). Updates state.json.

Usage:
  python3 verify.py --root <repo> --evolve <repo>/.evolve --check-dossier
  python3 verify.py --root <repo> --evolve <repo>/.evolve --check-briefs
  python3 verify.py --root <repo> --evolve <repo>/.evolve --slate
"""
import argparse
import hashlib
import json
import os
import re
import sys

LANES = ["deepen", "connect", "model", "complement"]
CONF = {"verified": 1.0, "recalled": 0.8, "hypothesis": 0.5}
PRESENT_CAP = 5          # briefs presented per lane; the rest bench (visible)
REQUIRES = re.compile(r"REQUIRES (NEW SERVICE|NEW MODEL|DEP)", re.I)

_file_cache = {}


def read_lines(root, rel):
    key = os.path.normpath(rel)
    if key not in _file_cache:
        path = os.path.join(root, rel)
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                _file_cache[key] = f.read().splitlines()
        except OSError:
            _file_cache[key] = None
    return _file_cache[key]


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def anchor_check(root, rel, line, anchor):
    """Exact-line anchor audit. Returns (ok, detail)."""
    lines = read_lines(root, rel)
    if lines is None:
        return False, f"file not found: {rel}"
    if not isinstance(line, int) or not (1 <= line <= len(lines)):
        return False, f"{rel}: line {line} out of range (file has {len(lines) if lines else 0})"
    a = norm(anchor or "")
    if len(a) < 4:
        return False, f"{rel}:{line}: anchor too short to prove a read ({anchor!r})"
    if a in norm(lines[line - 1]):
        return True, ""
    for i, l in enumerate(lines, 1):
        if a in norm(l):
            return False, f"{rel}: anchor found at line {i}, cited line {line} — cite what you read"
    return False, f"{rel}:{line}: anchor not found anywhere in file ({anchor!r})"


def load_json(path, required=True):
    if not os.path.exists(path):
        if required:
            print(f"error: missing {path}", file=sys.stderr)
            sys.exit(2)
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(2)


def sha(s, n=10):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:n]


# ---------------------------------------------------------------- dossier ----

DOSSIER_SECTIONS = ["on_screen", "latent", "neighbors", "services", "model_of_record"]


def check_dossier(root, evolve):
    dossier = load_json(os.path.join(evolve, "dossier.json"))
    scan = load_json(os.path.join(evolve, "scan.json"))
    failures, uncharted = [], []

    for sec in DOSSIER_SECTIONS:
        if sec not in dossier.get("sections", {}):
            failures.append(f"dossier missing section: {sec}")
    for sec, claims in dossier.get("sections", {}).items():
        for c in claims:
            ok, detail = anchor_check(root, c.get("file", ""), c.get("line"), c.get("anchor"))
            if not ok:
                failures.append(f"[{sec}] {c.get('text', '?')[:60]} — {detail}")

    accounting = dossier.get("accounting", {})
    for key in scan.get("accounting_keys", []):
        val = accounting.get(key, "")
        if val == "covered" or (isinstance(val, str) and val.startswith("dismissed:") and len(val) > len("dismissed:") + 3):
            continue
        uncharted.append(key)
    for cat, is_trunc in scan.get("truncated", {}).items():
        if is_trunc:
            failures.append(f"scan category '{cat}' was TRUNCATED — re-scan narrower; coverage over a truncated sweep proves nothing")

    print(f"dossier audit: {sum(len(v) for v in dossier.get('sections', {}).values())} claims · "
          f"{len(failures)} anchor/section failures · {len(uncharted)} UNCHARTED keys")
    for f in failures:
        print(f"  ANCHOR-FAIL {f}")
    for k in uncharted[:40]:
        print(f"  UNCHARTED   {k}  (mark 'covered' or 'dismissed: <reason>')")
    if len(uncharted) > 40:
        print(f"  ... and {len(uncharted) - 40} more")
    if failures or uncharted:
        print("VERDICT: BLOCKED — fix the dossier before any ideation. Coverage is proven, never claimed.")
        return 1
    print("VERDICT: DOSSIER CLEAN — ideation may open.")
    return 0


# ----------------------------------------------------------------- briefs ----

def claim_conf(root, claim, ctx, reject):
    """Return the claim's confidence value, auditing anchors; append rejections."""
    if "anchor" in claim or "file" in claim:
        ok, detail = anchor_check(root, claim.get("file", ""), claim.get("line"), claim.get("anchor"))
        if not ok:
            reject.append(f"ANCHOR-FAILED [{ctx}]: {detail}")
            return 0.0
        return CONF["verified"]
    tag, basis = claim.get("tag"), claim.get("basis", "")
    if tag not in ("recalled", "hypothesis"):
        reject.append(f"[{ctx}] claim has neither an anchor nor a valid tag (recalled|hypothesis): {claim.get('text', '?')[:60]}")
        return 0.0
    if len(basis.strip()) < 10:
        reject.append(f"[{ctx}] '{tag}' claim missing a real basis: {claim.get('text', '?')[:60]}")
        return 0.0
    return CONF[tag]


def check_brief(root, lane, b):
    """Returns (verified_brief | None, rejection_reasons)."""
    reject = []

    def need(field, kind=str, where=b, label=None):
        v = where.get(field)
        if v is None or (kind is str and not str(v).strip()) or (kind is list and not v):
            reject.append(f"missing/empty field: {label or field}")
            return None
        return v

    name = need("name") or "?"
    weight = b.get("weight")
    if weight not in ("S", "M", "L"):
        reject.append(f"weight must be S|M|L, got {weight!r}")
    for score, why in (("job_value", "job_value_why"), ("tightness", "tightness_why")):
        v = b.get(score)
        if v not in (1, 2, 3):
            reject.append(f"{score} must be 1|2|3, got {v!r}")
        if len(str(b.get(why, "")).strip()) < 10:
            reject.append(f"{why} missing — declared scores must carry an auditable justification")
    if "confidence" in b:
        reject.append("confidence is COMPUTED by verify.py — remove the declared value")

    builds_on = need("builds_on", list) or []
    min_bo = 2 if lane == "complement" else 1
    if len(builds_on) < min_bo:
        reject.append(f"builds_on needs ≥{min_bo} claims for {lane.upper()} (got {len(builds_on)})")
    job = b.get("job") or {}
    need("text", str, job, "job.text")
    job_anchors = job.get("anchors") or []
    if not job_anchors:
        reject.append("job.anchors empty — the job must be proven in code (past-tense evidence), not asserted")
    ux = b.get("ux") or {}
    need("sketch", str, ux, "ux.sketch")
    need("states", str, ux, "ux.states")
    if lane == "model" and not str(ux.get("trust_posture", "")).strip():
        reject.append("MODEL brief missing ux.trust_posture (suggestion vs auto-action; undo path)")
    wiring = need("wiring", list) or []
    ev = b.get("evolution_test") or {}
    if ev.get("verdict") != "PASS":
        reject.append(f"evolution_test.verdict must be PASS (a FAIL belongs in new_species[]), got {ev.get('verdict')!r}")
    if len(str(ev.get("line", "")).strip()) < 10:
        reject.append("evolution_test.line missing — state the returning-user sentence")
    need("not_this", str)
    if not isinstance(b.get("risks", None), list):
        reject.append("risks must be a list (empty only if cross-examination found nothing survivable)")

    confs, flags = [], []
    for i, c in enumerate(builds_on):
        confs.append(claim_conf(root, c, f"builds_on[{i}]", reject))
    for i, c in enumerate(job_anchors):
        confs.append(claim_conf(root, c, f"job.anchors[{i}]", reject))
    for i, w in enumerate(wiring):
        if not str(w.get("text", "")).strip():
            reject.append(f"wiring[{i}] missing text")
        wf = w.get("flags", []) or []
        flags.extend(wf)
        if any(REQUIRES.search(str(f)) for f in wf):
            continue  # report-only wire: no anchor demanded, the flag IS the finding
        confs.append(claim_conf(root, w, f"wiring[{i}]", reject))

    if reject:
        return None, reject

    confidence = min(confs) if confs else CONF["hypothesis"]
    label = {1.0: "verified", 0.8: "recalled", 0.5: "hypothesis"}.get(confidence, "hypothesis")
    primary = builds_on[0]
    primary_anchor = f"{primary.get('file', '?')}:{primary.get('line', '?')}"
    vb = dict(b)
    vb.update({
        "lane": lane,
        "id": sha(f"{lane}|{name}|{primary_anchor}"),
        "confidence": confidence,
        "confidence_label": label,
        "impact": round(b["job_value"] * b["tightness"] * confidence, 2),
        "report_only": any(REQUIRES.search(str(f)) for f in flags),
        "all_flags": sorted(set(map(str, flags))),
        "primary_anchor": primary_anchor,
    })
    return vb, []


def check_briefs(root, evolve):
    briefs_dir = os.path.join(evolve, "briefs")
    if not os.path.isdir(briefs_dir):
        print(f"error: missing {briefs_dir}", file=sys.stderr)
        return 2
    verified, rejected, new_species, undeveloped = [], [], [], {}
    for lane in LANES:
        path = os.path.join(briefs_dir, f"{lane}.json")
        data = load_json(path, required=False)
        if data is None:
            continue
        if data.get("lane") != lane:
            print(f"warning: {path} declares lane {data.get('lane')!r}", file=sys.stderr)
        new_species.extend(data.get("new_species", []))
        if data.get("undeveloped"):
            undeveloped[lane] = data["undeveloped"]
        for b in data.get("briefs", []):
            vb, reasons = check_brief(root, lane, b)
            if vb:
                verified.append(vb)
            else:
                rejected.append({"lane": lane, "name": b.get("name", "?"), "reasons": reasons})

    by_primary = {}
    for vb in verified:
        by_primary.setdefault(vb["primary_anchor"], []).append(vb)
    for anchor, group in by_primary.items():
        if len(group) > 1:
            ids = [g["id"] for g in group]
            for g in group:
                g["all_flags"] = sorted(set(g["all_flags"] + [f"DUP-CANDIDATE({','.join(i for i in ids if i != g['id'])})"]))

    out = {
        "briefs": sorted(verified, key=lambda v: (-v["impact"], v["lane"], v["name"])),
        "rejected": rejected,
        "new_species": new_species,
        "undeveloped": undeveloped,
        "stats": {
            "verified": len(verified),
            "rejected": len(rejected),
            "report_only": sum(1 for v in verified if v["report_only"]),
            "rejection_rate": round(len(rejected) / max(1, len(rejected) + len(verified)), 2),
        },
    }
    dest = os.path.join(evolve, "briefs.verified.json")
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    s = out["stats"]
    print(f"briefs audit: {s['verified']} verified · {s['rejected']} REJECTED (rate {s['rejection_rate']}) · "
          f"{s['report_only']} report-only · {len(new_species)} new-species logged → {dest}")
    for r in rejected:
        print(f"  REJECTED [{r['lane']}] {r['name']}:")
        for reason in r["reasons"]:
            print(f"    - {reason}")
    return 0


# ------------------------------------------------------------------ slate ----

def topo_order(briefs):
    """Apply order from depends_on (names or ids). Returns (ordered_ids, cycle_ids)."""
    by_id = {b["id"]: b for b in briefs}
    by_name = {b["name"]: b["id"] for b in briefs}
    deps = {
        b["id"]: [by_name.get(d, d) for d in (b.get("depends_on") or []) if by_name.get(d, d) in by_id]
        for b in briefs
    }
    ordered, state = [], {}  # state: 1=visiting, 2=done
    cycles = set()

    def visit(n, stack):
        if state.get(n) == 2:
            return
        if state.get(n) == 1:
            cycles.update(stack[stack.index(n):])
            return
        state[n] = 1
        for d in deps.get(n, []):
            visit(d, stack + [n])
        state[n] = 2
        ordered.append(n)

    for n in sorted(deps):
        visit(n, [])
    return ordered, sorted(cycles)


def render_brief(b, state_decisions):
    tags = []
    if b["id"] in state_decisions.get("deferred", []):
        tags.append("DEFERRED-RESURFACED")
    tags.extend(b["all_flags"])
    tagline = (" · " + " · ".join(tags)) if tags else ""
    lines = [
        f"### {b['id']} · {b['lane'].upper()} · {b['name']}",
        f"impact {b['impact']} (job {b['job_value']} × tight {b['tightness']} × conf {b['confidence']}"
        f" [{b['confidence_label']}]) · weight {b['weight']}{tagline}",
        f"- **BUILDS ON:** " + "; ".join(
            f"{c.get('file', '?')}:{c.get('line', '?')} `{c.get('anchor', c.get('tag', '?'))}`" for c in b["builds_on"]),
        f"- **JOB IT TIGHTENS:** {b['job']['text']}",
        f"- **UX:** {b['ux']['sketch']} · states: {b['ux']['states']}"
        + (f" · trust: {b['ux']['trust_posture']}" if b["ux"].get("trust_posture") else ""),
        f"- **WIRING:** " + "; ".join(
            w["text"] + (f" [{', '.join(w.get('flags', []))}]" if w.get("flags") else "") for w in b["wiring"]),
        f"- **EVOLUTION TEST:** PASS — {b['evolution_test']['line']}",
        f"- **RISKS:** " + ("; ".join(b["risks"]) if b["risks"] else "none survived cross-examination"),
        f"- **NOT THIS:** {b['not_this']}",
    ]
    if b.get("depends_on"):
        lines.append(f"- **DEPENDS ON:** {', '.join(b['depends_on'])}")
    return "\n".join(lines)


def slate(root, evolve):
    data = load_json(os.path.join(evolve, "briefs.verified.json"))
    state_path = os.path.join(evolve, "state.json")
    state = load_json(state_path, required=False) or {}
    decisions = state.setdefault("decisions", {"approved": [], "deferred": [], "killed": {}})
    kills = load_json(os.path.join(evolve, "kills.json"), required=False) or []

    killed_ids = set(decisions.get("killed", {}))
    xkilled = {k.get("id") or k.get("name"): k.get("refutation", "") for k in kills}
    live, graveyarded, xexamined = [], [], []
    for b in data["briefs"]:
        if b["id"] in killed_ids:
            graveyarded.append(b)
        elif b["id"] in xkilled or b["name"] in xkilled:
            b["refutation"] = xkilled.get(b["id"]) or xkilled.get(b["name"])
            xexamined.append(b)
        else:
            live.append(b)

    deferred_ids = set(decisions.get("deferred", []))
    presented, benched, report_only = [], [], []
    for lane in LANES:
        lane_briefs = [b for b in live if b["lane"] == lane]
        ro = [b for b in lane_briefs if b["report_only"]]
        rest = [b for b in lane_briefs if not b["report_only"]]
        rest.sort(key=lambda b: (b["id"] not in deferred_ids, -b["impact"]))
        presented.extend(rest[:PRESENT_CAP])
        benched.extend(rest[PRESENT_CAP:])
        report_only.extend(ro)

    order, cycles = topo_order(presented)
    dossier_path = os.path.join(evolve, "dossier.md")
    dossier_hash = ""
    if os.path.exists(dossier_path):
        with open(dossier_path, "rb") as f:
            dossier_hash = hashlib.sha1(f.read()).hexdigest()[:10]

    s = data["stats"]
    L = []
    L.append(f"# EVOLVE SLATE — dossier {dossier_hash or 'n/a'}\n")
    L.append("## Inline summary")
    lane_counts = "/".join(str(sum(1 for b in presented if b["lane"] == l)) for l in LANES)
    L.append(
        f"{len(presented)} presented ({lane_counts} across {'/'.join(l.upper() for l in LANES)}) · "
        f"{len(report_only)} report-only · {len(benched)} benched · "
        f"{s['rejected']} mechanically rejected (rate {s['rejection_rate']}) · "
        f"{len(xexamined)} killed in cross-examination · "
        f"{len(data['new_species'])} new-species logged · graveyard {len(graveyarded)}\n"
    )
    for lane in LANES:
        L.append(f"## {lane.upper()}")
        lane_p = [b for b in presented if b["lane"] == lane]
        if not lane_p:
            L.append("*(no briefs survived for this lane — see bench/rejections; an empty lane is a fact, not a failure)*")
        for b in lane_p:
            L.append(render_brief(b, decisions))
            L.append("")
    if report_only:
        L.append("## Report-only (Platform Lock) — human may lift the lock; the skill may not")
        for b in report_only:
            L.append(f"- `{b['id']}` [{b['lane'].upper()}] **{b['name']}** — {', '.join(b['all_flags'])} · impact {b['impact']}")
    if benched:
        L.append("\n<details><summary><b>Bench — over-cap, promotable by ID</b></summary>\n")
        for b in benched:
            L.append(f"- `{b['id']}` [{b['lane'].upper()}] {b['name']} · impact {b['impact']}")
        L.append("</details>")
    if data["new_species"]:
        L.append("\n## NEW SPECIES (logged, never briefed)")
        for nsp in data["new_species"]:
            L.append(f"- **{nsp.get('name', '?')}** — {nsp.get('why_tempting', '')}")
    if xexamined:
        L.append("\n## Cross-examination kills (credibility, not clutter)")
        for b in xexamined:
            L.append(f"- `{b['id']}` [{b['lane'].upper()}] {b['name']} — REFUTED: {b.get('refutation', '?')}")
    if data["rejected"]:
        L.append("\n<details><summary><b>Mechanical rejections (schema/anchor law)</b></summary>\n")
        for r in data["rejected"]:
            L.append(f"- [{r['lane']}] {r['name']}: " + " · ".join(r["reasons"]))
        L.append("</details>")
    if graveyarded:
        L.append("\n<details><summary><b>Graveyard — killed by you, never re-proposed</b></summary>\n")
        for b in graveyarded:
            L.append(f"- `{b['id']}` {b['name']} — killed: {decisions['killed'].get(b['id'], '')}")
        L.append("</details>")
    if order:
        L.append("\n## Apply order (if all presented were approved)")
        by_id = {b["id"]: b for b in presented}
        L.append(" → ".join(f"{i} ({by_id[i]['name']})" for i in order if i in by_id))
    if cycles:
        L.append(f"\n**DEPENDENCY CYCLE — resolve before routing:** {', '.join(cycles)}")
    L.append("\n---\n**DECIDE:** approve <ids> · defer <ids> · kill <ids>: <reason> · promote <bench-ids>")
    L.append("*(then the skill YIELDS — nothing builds this turn.)*")

    dest = os.path.join(evolve, "SLATE.md")
    with open(dest, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")

    state["dossier"] = {"path": ".evolve/dossier.md", "hash": dossier_hash}
    reg = state.setdefault("briefs", {})
    for b in data["briefs"]:
        status = ("presented" if b in presented else
                  "report_only" if b in report_only else
                  "benched" if b in benched else
                  "graveyard" if b in graveyarded else "cross_examined_kill")
        reg[b["id"]] = {"lane": b["lane"], "name": b["name"], "status": status, "impact": b["impact"]}
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    print(f"slate → {dest} · state → {state_path}")
    print(f"presented {len(presented)} · report-only {len(report_only)} · benched {len(benched)} · "
          f"graveyard {len(graveyarded)}" + (f" · CYCLES: {cycles}" if cycles else ""))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--evolve", required=True)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check-dossier", action="store_true")
    mode.add_argument("--check-briefs", action="store_true")
    mode.add_argument("--slate", action="store_true")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    evolve = os.path.abspath(args.evolve)
    if args.check_dossier:
        return check_dossier(root, evolve)
    if args.check_briefs:
        return check_briefs(root, evolve)
    return slate(root, evolve)


if __name__ == "__main__":
    sys.exit(main())

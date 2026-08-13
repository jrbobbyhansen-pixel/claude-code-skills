#!/usr/bin/env python3
"""CUT stage: approved picks + beat grid -> edl.json

Grammar (references/grammar.md):
  - cold open: 2-beat tease of the MONEY moment first
  - then approved shots in given order; money re-appears in place, ramped
  - slots are 2 or 4 beats, varied to avoid metronome feel
  - ramp = 0.35x speed on a 4-beat slot, only if source >=60fps
  - impact shots keep natural audio hot; everything else ducks under music
  - music offset aligns the drop to the money shot when the track allows

Usage: cut.py <work_dir> [--target 25]
Reads <work_dir>/{candidates.json, clips.json, beats.json, picks.json}
picks.json: {"keep":[ids in order], "money": id|null, "crop": {"<id>":"left|center|right"}}
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import ENDCARD_SECONDS, die, load_json, save_json

RAMP_SPEED = 0.35
TEASE_BEATS = 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work_dir")
    ap.add_argument("--target", type=float, default=25.0)
    args = ap.parse_args()
    work = Path(args.work_dir)

    cands = {c["id"]: c for c in load_json(work / "candidates.json")["candidates"]}
    clips = {c["name"]: c for c in load_json(work / "clips.json")["clips"]}
    beats = load_json(work / "beats.json")
    picks = load_json(work / "picks.json")

    keep = picks["keep"]
    money = picks.get("money")
    crops = picks.get("crop", {})
    if not keep:
        die("picks.json has an empty keep list")
    for k in keep:
        if k not in cands:
            die(f"picked id {k} not in candidates")
    if money is not None and money not in keep:
        die(f"money id {money} is not in the keep list")

    bi = beats["beat_interval"]

    # slot plan: money gets 4 beats; every 3rd other shot gets 4 beats, rest 2
    order = list(keep)
    if money is not None:
        order = [("tease", money)] + [("shot", k) for k in keep]
    else:
        order = [("shot", k) for k in keep]

    slots = []
    nth = 0
    for kind, cid in order:
        if kind == "tease":
            slots.append(TEASE_BEATS)
        elif cid == money:
            slots.append(4)
        else:
            slots.append(4 if nth % 3 == 2 else 2)
            nth += 1

    def total(sl):
        return sum(sl) * bi + ENDCARD_SECONDS

    # squeeze toward target: demote non-money 4s to 2s if long, promote if short
    idx_flex = [i for i, (kind, cid) in enumerate(order) if kind == "shot" and cid != money]
    for i in reversed(idx_flex):
        if total(slots) <= args.target + 2:
            break
        if slots[i] == 4:
            slots[i] = 2
    for i in idx_flex:
        if total(slots) >= args.target - 3:
            break
        if slots[i] == 2:
            slots[i] = 4

    # build shots
    shots = []
    t = 0.0
    money_start_in_timeline = None
    for (kind, cid), nb in zip(order, slots):
        c = cands[cid]
        clip = clips.get(c["clip"])
        if clip is None:
            die(f"candidate {cid} references unknown clip {c['clip']}")
        slot_dur = nb * bi
        ramp = kind == "shot" and cid == money and c["ramp_ok"]
        speed = RAMP_SPEED if ramp else 1.0
        span = slot_dur * speed  # source seconds consumed
        mid = (c["t_start"] + c["t_end"]) / 2
        src_in = max(0.0, min(mid - span / 2, clip["duration"] - span))
        if kind == "shot" and cid == money:
            money_start_in_timeline = t
        shots.append({
            "id": cid,
            "kind": kind,
            "src": c["path"],
            "in": round(src_in, 3),
            "span": round(span, 3),
            "dur": round(slot_dur, 3),
            "speed": speed,
            "ramp": ramp,
            "crop": crops.get(str(cid), "center"),
            "hdr": c["hdr"],
            "audio": "mute" if (ramp or kind == "tease" or "no-audio" in c["tags"])
                     else ("hot" if "impact" in c["tags"] else "duck"),
            "t_timeline": round(t, 3),
        })
        t += slot_dur

    reel_dur = t + ENDCARD_SECONDS

    # music offset: put the drop under the money shot when the track can cover it
    offset = beats["grid_start"]
    reason = "grid_start"
    if money_start_in_timeline is not None and beats["drop"] > 0:
        cand_off = beats["drop"] - money_start_in_timeline
        if cand_off >= 0 and cand_off + reel_dur <= beats["duration"]:
            offset, reason = cand_off, "drop-aligned to money shot"
    if offset + reel_dur > beats["duration"]:
        offset, reason = 0.0, "track shorter than grid_start allows"
    if reel_dur > beats["duration"]:
        die(f"track ({beats['duration']}s) shorter than reel ({reel_dur:.1f}s); pick a longer track")

    edl = {
        "shots": shots,
        "music": {"file": beats["track"], "offset": round(offset, 3),
                  "bpm": beats["bpm"], "align": reason},
        "endcard_seconds": ENDCARD_SECONDS,
        "reel_seconds": round(reel_dur, 2),
    }
    save_json(work / "edl.json", edl)
    warn = "" if 20 <= reel_dur <= 32 else "  ** outside 20-30s target — add/drop picks or change --target **"
    print(f"EDL: {len(shots)} shots, {reel_dur:.1f}s incl. end card, "
          f"music {reason} @ {offset:.2f}s{warn}")


if __name__ == "__main__":
    main()

# /videocut BUILD-SPEC (locked 2026-08-12, planning session)

Status: SPEC ONLY. No code exists yet. Build is one dedicated session.

## Purpose

Folder of raw iPhone footage in -> one 20-30s beat-synced 9:16 hero reel out
(two files: music-burned + clean), via a human-gated pick sheet. Content:
BlindBuddy world (hunts, trade shows, land work). All local, all free (ffmpeg
+ python audio libs). Zero cloud spend.

## Locked decisions

| Axis | Decision |
|---|---|
| Output | 9:16 vertical, 1080x1920, one hero reel per run, 20-30s |
| Versions | Both: music-burned + clean (same cut timing) per reel |
| Selection | Hybrid: auto-scan finds candidates -> pick sheet -> Bobby approves -> render |
| Sources | iPhone only (HEVC/Dolby Vision; tonemap step mandatory) |
| Captions | None (v1) |
| Music | Per-run: Bobby drops 1-2 tracks next to footage; skill beat-syncs to it |
| Edit grammar | Punchy: hard cuts on beat, speed ramps on money moments, no crossfades |
| Kill/harvest | No filtering. Impact moments get an info tag on the pick sheet, nothing more |
| Branding | End card only, 1.5-2s, logo + handle/CTA. One-time setup: build card from existing logo |
| Folders | ~/Desktop/Hansen Capital Group LLC/BlindBuddy Content/{inbox, tracks, reels, archive} |

## Pipeline

```
inbox/*.mov
  -> PROBE      ffprobe every clip: duration, fps, resolution, rotation, HDR flag, creation date
  -> SCAN       candidate detection, three signals merged:
                  1. audio spikes (RMS/onset: gunshots, calls, laughter, "there he is")
                  2. scene changes (ffmpeg scdet or PySceneDetect)
                  3. motion density (frame-diff sampling)
  -> PICK SHEET static HTML: thumbnail grid + 2s animated webp preview per candidate,
                genre guess (hunt/show/land), impact-tag where detected, timestamp, clip source.
                ~20-25 candidates target. Bobby replies in chat: keep/kill/re-order/notes.
  -> BEAT MAP   track BPM + onset grid (librosa or aubio, free)
  -> CUT        EDL: approved shots mapped to beat grid, 1.5-2.5s per shot,
                money moment gets the slow-mo ramp (only if source >=60fps, else no ramp)
  -> RENDER     draft: 720p proxy, fast preset -> SendUserFile for review
                final: 1080x1920 H.264 high, ~12 Mbps, AAC 192k, -14 LUFS loudness norm
                HDR handling: tonemap Dolby Vision/HLG -> SDR BT.709 (zscale+tonemap=hable)
                end card appended, then x2 mux: music-burned + clean
  -> DELIVER    reels/<date>-<slug>/{hero-music.mp4, hero-clean.mp4, edl.json, picksheet.html}
```

## Skill anatomy (build session)

```
~/.claude/skills/videocut/
  SKILL.md          workflow prompt: gates, pick-sheet protocol, iteration loop
  scripts/
    probe.sh        ffprobe batch -> clips.json
    scan.py         candidate detection -> candidates.json + thumbs/ + previews/
    picksheet.py    candidates.json -> picksheet.html
    beatmap.py      track -> beats.json (BPM, onsets)
    cut.py          approved picks + beats.json -> edl.json
    render.sh       edl.json -> ffmpeg filtergraph -> mp4 (proxy|final flags)
  assets/
    endcard.png     built once from BlindBuddy logo (setup step)
  references/
    grammar.md      punchy edit rules: shot lengths by BPM, ramp rules, J-cut audio rules
```

Deps (all free): ffmpeg (brew), python3 + librosa (or aubio), Pillow. No paid APIs.

## Iteration loop

Draft proxy -> Bobby reacts in plain words ("first 3 shots drag", "end on the retrieve")
-> EDL edited, re-render proxy (fast, <1min) -> approve -> final render. EDL saved, so
re-cuts and future re-edits of the same footage are near-free.

## v1 explicitly OUT (v2 candidates)

- Captions/transcription (Whisper local, free, easy add later)
- Subject-tracking auto-crop for horizontal footage (v1 = center crop + manual x-offset per shot on pick sheet)
- Multi-reel batch mode per run
- 16:9 YouTube master
- Per-genre auto grammar switching
- Text overlays / title cards beyond end card

## Gotchas locked in during planning

1. iPhone Dolby Vision looks gray/washed after naive ffmpeg. Tonemap is a mandatory
   pipeline stage, not optional polish.
2. Slow-mo ramps need >=60fps source. Skill checks fps and refuses juddery 30fps ramps.
   Shooting guidance: 4K60 default on iPhone for anything that might get ramped.
3. Burned music can suppress platform reach; that is WHY the clean version exists.
   Post the clean one with trending in-app audio when reach matters.
4. iPhone rotation metadata lies sometimes; probe must read side_data rotation.
5. 20-30s at beat pace = 10-15 shots. Pick sheet needs ~2x that in candidates.
6. Chronology from creation_time metadata, not filename.
7. Impact/harvest content: IG/TikTok moderate graphic hunting footage. Tagged on
   pick sheet as info only per Bobby's call; he owns platform risk.

## One-time setup steps (build session)

1. brew install ffmpeg; pip install librosa Pillow (check versions)
2. Create BlindBuddy Content folder tree
3. Build endcard.png from BlindBuddy logo (pull from app repo assets)
4. Test run on any sample iPhone clip folder end-to-end before calling it live

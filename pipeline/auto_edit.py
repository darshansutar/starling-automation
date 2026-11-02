"""Auto-edit v1: re-cut an assembled Starling roleplay so it plays like an edited film (Claude, 2026-11-02).

    python pipeline/auto_edit.py PROJECT_DIR [--min-shot 2.0] [--push 1.15] [--out NAME]

Reads the project's animation/v1/preview-assembly.json (the per-node timeline the assembler wrote: every
clip's source render, and for narration the source start and length of each shot plus the narration audio
window) and writes a new set of node videos plus auto-edit-report.json. No render is re-requested.

1. Narration pacing. No shot shorter than --min-shot. The shortest short shot is dropped and its time is given
   to a neighbouring shot whose render has spare footage after its current end (shots were rendered with
   1-2 s buffers). The last shot before a dialogue is never dropped (it is the dialogue handoff), except that a
   narration shorter than SINGLE_PANEL_MAX keeps one narration panel (the first with enough footage), not the handoff. Shot windows
   come from scene-cut detection on each render (ffmpeg scdet, threshold 4: conservative).
2. Dialogue turn-taking. Each dialogue clip is trimmed to one spoken copy of its line: 0.15 s before the first
   word to 0.30 s after the approved line's length (ffmpeg silencedetect -35 dB / 0.1 s on the render and the
   approved audio). Anything EN2 says beyond that - a repeated or extra phrase - is cut.
3. Jump-cut cover. In a run of dialogue clips the first keeps the wide scene; each following line pushes in to
   --push on the speaker's side (Kamala/left, Ravi/right) so consecutive same-scene cuts read as intended
   shot changes.
4. Shot faults (ffmpeg only, no extra installs): black frames or fades inside a used shot are flagged; side or top
   bars are zoomed out up to MAX_BAR_ZOOM and flagged for re-render beyond it. A frame sheet of every narration shot
   (outputs/<out>/review-sheets) is written for Claude's no-talking and hallucination review.
5. Flags. animation/v1/auto-edit-flags.json may list narration shots to drop, e.g. {"segment_3_line_1":
   {"drop_shots": [3], "reason": "characters move their lips during narration"}} or
   {"bad_3_line_1_a": {"trim_head": {"1": 1.5}, "reason": "the register morphs as it closes"}}. A dropped shot's time,
   or the time a later-starting shot can no longer cover, is spread over the nearest remaining shots.
Narration audio is unchanged; nodes get shorter only where dialogue dead air is removed.
"""
import argparse
import json
import math
import re
import shutil
import subprocess
import wave
from pathlib import Path

FPS, SRC_FPS, EDGE, SR, W, H = 30, 24, 0.01, 48000, 1344, 768
LEAD, TAIL = 0.15, 0.30
LEFT_SPEAKERS = {"kamala"}


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True)


def duration(path, stream=None):
    args = ["ffprobe", "-v", "error"] + (["-select_streams", stream] if stream else []) + \
           ["-show_entries", ("stream" if stream else "format") + "=duration", "-of", "csv=p=0", str(path)]
    return float(run(args).stdout.strip().split("\n")[0])


def scene_cuts(path, cache):
    key = str(path)
    if key not in cache:
        err = subprocess.run(["ffmpeg", "-hide_banner", "-i", key, "-vf", "scdet=threshold=12,metadata=print", "-f", "null", "-"],
                             capture_output=True, text=True).stderr
        cache[key] = sorted(float(x) for x in re.findall(r"lavfi\.scd\.time=([0-9.]+)", err))
    return cache[key]


MAX_BAR_ZOOM = 1.15   # side/top bars are zoomed out up to this; larger bars are flagged for re-render


def shot_faults(src, t0, length):
    """Black frames / fades and letterbox or pillarbox bars inside the used part of a shot (ffmpeg only)."""
    err = subprocess.run(["ffmpeg", "-hide_banner", "-ss", f"{t0:.3f}", "-t", f"{length:.3f}", "-i", str(src), "-vf",
                          "blackdetect=d=0.05:pix_th=0.08,cropdetect=limit=24:round=2:reset=0", "-an", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    black = [round(float(x), 2) for x in re.findall(r"black_start:([0-9.]+)", err)]
    crops = re.findall(r"crop=(\d+):(\d+):(\d+):(\d+)", err)
    crop = None
    if crops:
        cw, ch, cx, cy = map(int, crops[-1])
        if cw < W - 8 or ch < H - 8:                      # bars present
            zoom = max(W / cw, H / ch)
            if zoom <= MAX_BAR_ZOOM:
                tw, th = round(W / zoom / 2) * 2 - 6, round(H / zoom / 2) * 2 - 6   # keep 16:9, stay inside the picture
                crop = f"crop={tw}:{th}:{cx + (cw - tw) // 2}:{cy + (ch - th) // 2}"
            else:
                crop = "too_large"
    return black, crop


def speech_span(path):
    """(first speech start, last speech end, file duration) by ffmpeg silencedetect."""
    d = duration(path)
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "silencedetect=noise=-35dB:d=0.1", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", err)]
    en = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", err)]
    first = en[0] if st and st[0] < 0.05 and en else 0.0
    last = st[-1] if st and (len(st) > len(en) or en[-1] > d - 0.05) else d
    return first, last, d


def dialogue_trim(render, approved):
    """Trim to one spoken copy of the line: from just before the first word to just after the approved line's
    length. Anything EN2 says after that (a repeated or extra phrase) is cut."""
    first, last, d = speech_span(render)
    a_first, a_last, _ = speech_span(approved)
    cap = first + (a_last - a_first) + 0.15
    end = min(last, cap)
    return max(0.0, first - LEAD), min(d, end + TAIL), d, last > cap + 0.3


def speech_bounds(path):
    d = duration(path)
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "silencedetect=noise=-35dB:d=0.1", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", err)]
    en = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", err)]
    first = en[0] if st and st[0] < 0.05 and en else 0.0
    last = st[-1] if st and len(st) > len(en) or (st and en and en[-1] > d - 0.05) else d
    return max(0.0, first - LEAD), min(d, last + TAIL), d


MIN_SPEED = 0.8   # B-roll may play down to 0.8x to fill a merged shot
SINGLE_PANEL_MAX = 3.75   # a narration shorter than this plays as one narration panel


def pace_narration(starts, lengths, src, protect_last, min_shot, cache, drop=(), trim_head=None):
    """Return (starts, lengths, speeds, notes) with no shot under min_shot where the footage allows.

    Each shot's footage window runs from its start to the next scene cut (or the next shot's start, or the end
    of the render). A dropped shot's time goes to a neighbour, which plays more of its own footage and, if
    needed, slows to no less than MIN_SPEED."""
    total_src = duration(src)
    cuts = scene_cuts(src, cache)
    S, L = list(starts), list(lengths)
    win = []
    for i, s in enumerate(S):
        ends = [c - EDGE for c in cuts if c > s + 0.05] + ([S[i + 1] - EDGE] if i + 1 < len(S) else []) + [total_src - EDGE]
        win.append(min(ends) - s)
    notes, stuck = [], set()

    def spread(t, i, keep):
        """Give t seconds to the shots in keep, nearest to shot i first, each up to its footage at MIN_SPEED."""
        for k in sorted(keep, key=lambda k: abs(k - i)):
            give = min(t, max(0.0, win[k] / MIN_SPEED - L[k]))
            L[k] += give
            t -= give
            if t <= 1e-6:
                return 0.0
        return t

    # Flagged hallucinated openings: start the shot later and pass any time it can no longer cover to its neighbours.
    for key, skip in (trim_head or {}).items():
        i = int(key) - 1
        if not 0 <= i < len(L):
            continue
        S[i] += skip
        win[i] -= skip
        over = L[i] - win[i] / MIN_SPEED
        if over > 0:
            L[i] -= over
            left = spread(over, i, [k for k in range(len(L)) if k != i])
            assert left <= 1e-6, f"not enough footage to trim {skip:.2f} s from shot {i + 1}"
        notes.append(f"shot {i + 1} starts {skip:.2f} s later (flagged opening removed)")
    # Flagged shots (e.g. people talking during narration) are removed first; their time is spread over the
    # nearest remaining shots, each up to what its footage allows at MIN_SPEED.
    for i in sorted({d - 1 for d in drop if 0 < d <= len(L)}, reverse=True):
        t, keep = L[i], [k for k in range(len(L)) if k != i]
        for k in sorted(keep, key=lambda k: abs(k - i)):
            give = min(t, max(0.0, win[k] / MIN_SPEED - L[k]))
            L[k] += give; t -= give
            if t <= 1e-6:
                break
        assert t <= 1e-6, f"not enough footage to drop flagged shot {i + 1}"
        notes.append(f"dropped flagged shot {i + 1} ({L[i]:.2f} s); time spread over the nearest shots")
        del S[i], L[i], win[i]
        protect_last = False
    total = sum(L)
    if len(L) > 1 and total < SINGLE_PANEL_MAX:
        for i in range(len(L)):
            if total <= win[i] / MIN_SPEED + 1e-6:
                notes.append(f"{total:.2f} s narration is too short for two shots: kept narration panel {i + 1} only")
                return [S[i]], [total], [round(min(1.0, win[i] / total), 4)], notes
    while len(L) > 1:
        cand = [i for i in range(len(L)) if L[i] < min_shot and i not in stuck and not (protect_last and i == len(L) - 1)]
        if not cand:
            break
        i = min(cand, key=lambda k: L[k])
        options = [j for j in (i - 1, i + 1) if 0 <= j < len(L) and L[j] + L[i] <= win[j] / MIN_SPEED + 1e-6]
        if not options:
            notes.append(f"kept {L[i]:.2f} s shot: neighbours lack footage even at {MIN_SPEED}x")
            stuck.add(i)
            continue
        j = min(options, key=lambda k: L[k])        # give the time to the shorter neighbour
        notes.append(f"dropped {L[i]:.2f} s shot; its time goes to the {'previous' if j < i else 'next'} shot")
        L[j] += L[i]
        del S[i], L[i], win[i]
        stuck = {k - 1 if k > i else k for k in stuck if k != i}
    speeds = [round(min(1.0, w / l), 4) for w, l in zip(win, L)]
    return S, L, speeds, notes


def piece(src, t0, frames, target, crop=None, speed=1.0):
    vf = f"fps=30,scale={W}:{H}:flags=lanczos,setsar=1"
    if crop:
        vf = f"fps=30,{crop},scale={W}:{H}:flags=lanczos,setsar=1"
    if speed < 0.999:
        vf = f"setpts=PTS/{speed:.4f}," + vf
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.6f}", "-i", str(src), "-vf", vf + ",tpad=stop_mode=clone:stop_duration=1",
         "-frames:v", str(frames), "-an", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30", str(target)])


def audio(src, t0, seconds, target):
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.6f}", "-i", str(src), "-map", "0:a:0", "-af",
         f"aresample={SR},apad,atrim=end_sample={round(seconds * SR)},asetpts=PTS-STARTPTS", "-ac", "2", "-c:a", "pcm_s16le", str(target)])


def push_crop(speaker, push):
    cw, ch = round(W / push / 2) * 2, round(H / push / 2) * 2
    x = 0 if speaker in LEFT_SPEAKERS else W - cw
    y = round((H - ch) * 0.35)
    return f"scale={W}:{H},crop={cw}:{ch}:{x}:{y}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--min-shot", type=float, default=2.0)
    ap.add_argument("--push", type=float, default=1.15)
    ap.add_argument("--out", default="Auto-Edit v1")
    a = ap.parse_args()
    root = Path(a.project).resolve()
    timeline = json.loads((root / "animation/v1/preview-assembly.json").read_text(encoding="utf-8"))
    script = json.loads((root / "canonical-script.json").read_text(encoding="utf-8"))
    speakers = {l["id"]: l["speaker"] for n in script["nodes"] for l in n["lines"]}
    units = {u["line_id"]: u for u in json.loads((root / "audio/audio_manifest.json").read_text(encoding="utf-8"))["units"]}
    out = root / "outputs" / a.out
    work = root / "animation/v1/auto-edit-work"
    out.mkdir(parents=True, exist_ok=True)
    flags_path = root / "animation/v1/auto-edit-flags.json"
    flags = json.loads(flags_path.read_text(encoding="utf-8")) if flags_path.exists() else {}
    cache, report = {}, []
    for node in timeline:
        home = work / node["node"]
        if home.exists():
            shutil.rmtree(home)
        home.mkdir(parents=True)
        cursor, vparts, aparts, rows, prev_dialogue = 0.0, [], [], [], False
        review_frames = []
        clips = node["clips"]
        for k, c in enumerate(clips):
            src = Path(c["source"])
            src = src if src.is_absolute() else root / src
            if c["kind"] == "dialogue":
                t0, t1, d, repeat = dialogue_trim(src, root / units[c["clip"]]["file"])
                length = math.floor((t1 - t0) * FPS) / FPS
                frames = round((cursor + length) * FPS) - round(cursor * FPS)
                crop = push_crop(speakers[c["clip"]], a.push) if prev_dialogue else None
                vp, apath = home / f"v{len(vparts):02d}.mp4", home / f"a{len(aparts):02d}.wav"
                piece(src, t0, frames, vp, crop)
                audio(src, t0, length, apath)
                vparts.append(vp); aparts.append(apath)
                rows.append({"clip": c["clip"], "kind": "dialogue", "trim": [round(t0, 3), round(t0 + length, 3)],
                             "removed_dead_air_s": round(d - length, 3), "framing": "push-in" if crop else "wide",
                             "extra_speech_cut": repeat})
                cursor += length
                prev_dialogue = True
                continue
            prev_dialogue = False
            if "spans" in c:
                starts, lengths = [s for s, _ in c["spans"]], [e - s for s, e in c["spans"]]
            else:
                starts, lengths = c["starts"], c["shots"]
            protect = k + 1 < len(clips) and clips[k + 1]["kind"] == "dialogue"
            flag = flags.get(c["clip"], {})
            S, L, V, notes = pace_narration(starts, lengths, src, protect, a.min_shot, cache, flag.get("drop_shots", ()),
                                            flag.get("trim_head"))
            if flag:
                notes.insert(0, "flag: " + flag.get("reason", ""))
            faults = []
            for n_shot, (s, l, v) in enumerate(zip(S, L, V), 1):
                frames = round((cursor + l) * FPS) - round(cursor * FPS)
                vp = home / f"v{len(vparts):02d}.mp4"
                black, bars = shot_faults(src, s, l * v)
                if black:
                    faults.append({"shot": n_shot, "fault": "black frames or fade", "at_source_s": black, "action": "flag for review / re-render"})
                if bars == "too_large":
                    faults.append({"shot": n_shot, "fault": "possible side or top bars too large to zoom out (a dark scene can look like bars)", "action": "Claude checks the review sheet; re-render only if real bars"})
                elif bars:
                    faults.append({"shot": n_shot, "fault": "side or top bars", "action": "zoomed out (" + bars + ")"})
                piece(src, s, frames, vp, crop=bars if bars and bars != "too_large" else None, speed=v)
                review_frames.append((c["clip"], n_shot, vp, cursor, l))
                vparts.append(vp)
                cursor += l
            line = re.sub(r"_[abc]$", "", c["clip"])
            a0, a1 = c["audio"] if "audio" in c else (0.0, sum(lengths))
            apath = home / f"a{len(aparts):02d}.wav"
            audio(root / units[line]["file"], a0, a1 - a0, apath)
            aparts.append(apath)
            rows.append({"clip": c["clip"], "kind": "narration", "shots_before": [round(x, 2) for x in lengths],
                         "shots_after": [round(x, 2) for x in L], "speeds": V, "notes": notes, "faults": faults})
        listing = home / "list.txt"
        listing.write_text("".join(f"file '{p.as_posix()}'\n" for p in vparts), encoding="utf-8")
        run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(home / "visual.mp4")])
        with wave.open(str(home / "audio.wav"), "wb") as w:
            w.setparams((2, 2, SR, 0, "NONE", "not compressed"))
            for p in aparts:
                with wave.open(str(p), "rb") as r:
                    w.writeframes(r.readframes(r.getnframes()))
        target = out / node["file"]
        run(["ffmpeg", "-v", "error", "-y", "-i", str(home / "visual.mp4"), "-i", str(home / "audio.wav"), "-map", "0:v:0", "-map", "1:a:0",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{cursor:.3f}", "-movflags", "+faststart", str(target)])
        assert abs(duration(target) - cursor) < 0.06, (node["node"], duration(target), cursor)
        if review_frames:   # three frames per narration shot, for Claude's no-talking / hallucination review
            sheet_dir = out / "review-sheets"
            sheet_dir.mkdir(exist_ok=True)
            tiles = []
            for clip, n_shot, vp, _, l in review_frames:
                for k, frac in enumerate((0.15, 0.5, 0.85)):
                    img = home / f"r-{clip}-{n_shot}-{k}.png"
                    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{l * frac:.3f}", "-i", str(vp), "-frames:v", "1", "-vf", "scale=448:-1", str(img)])
                    tiles.append(img)
            listing = home / "tiles.txt"
            listing.write_text("".join(f"file '{t.as_posix()}'\n" for t in tiles), encoding="utf-8")
            run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-vf", "tile=3x" + str(len(review_frames)),
                 "-frames:v", "1", str(sheet_dir / (Path(node["file"]).stem + "-narration-shots.png"))])
        report.append({"node": node["node"], "file": node["file"], "seconds_before": node["seconds"], "seconds_after": round(cursor, 3),
                       "clips": rows})
        print(f"{node['file']:<20} {node['seconds']:6.2f} -> {cursor:6.2f} s", flush=True)
    (root / "animation/v1/auto-edit-report.json").write_text(json.dumps({"settings": {"min_shot": a.min_shot, "push": a.push,
        "lead": LEAD, "tail": TAIL}, "nodes": report}, indent=2, ensure_ascii=False), encoding="utf-8")
    shots = [x for n in report for c in n["clips"] if c["kind"] == "narration" for x in c["shots_after"]]
    print("narration shots", len(shots), "under", a.min_shot, "s:", sum(x < a.min_shot for x in shots),
          "| dialogue dead air removed", round(sum(c.get("removed_dead_air_s", 0) for n in report for c in n["clips"]), 1), "s")


if __name__ == "__main__":
    main()

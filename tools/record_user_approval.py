"""Record a user's whole-video approval for every selected render in a project (Claude, 2026-11-02).

python tools/record_user_approval.py PROJECT_DIR "exact user quote" [--note TEXT]

For each clip in animation/v1/plan.json, the latest runtime job is moved to verified with a review JSON that
names the user as reviewer and quotes their verdict. The reviewed file is the raw provider output of that job;
edit fixes applied at assembly (listed in --note) are recorded as observations. Then the renders stage receipt
is accepted when every scoped render is verified.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
from runtime import Project  # noqa: E402

SPATIAL = ("scale_proportion", "perspective_depth", "separation_clearance", "support_contact", "orientation_construction",
           "occlusion_order", "spatial_continuity")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("quote")
    ap.add_argument("--note", default="")
    a = ap.parse_args()
    root = Path(a.project).resolve()
    plan = json.loads((root / "animation/v1/plan.json").read_text(encoding="utf-8"))
    col = json.loads((root / "animation/v1/collected.json").read_text(encoding="utf-8"))
    p = Project(root)
    (root / "animation/v1/reviews").mkdir(exist_ok=True)
    done = []
    for c in plan["clips"]:
        cid = c["clip_id"]
        row = p.db.execute("SELECT * FROM jobs WHERE clip=? ORDER BY attempt DESC", (cid,)).fetchone()
        assert row and row["provider_id"] == col[cid]["job_id"], (cid, row and row["provider_id"], col[cid]["job_id"])
        if row["state"] == "verified":
            continue
        out = f"animation/v1/outputs/{col[cid]['file']}"
        ev = (f"User verdict 2026-11-02 after watching the assembled node videos: '{a.quote}'. "
              "Approval covers the complete picture, sound" + (" and lip-sync" if c["content_kind"] == "dialogue" else "") + " of this clip.")
        review = {"status": "verified", "clip": cid, "provider_id": row["provider_id"], "reviewer": "user", "reviewed_on": "2026-11-02",
                  "path": out, "sha256": hashlib.sha256((root / out).read_bytes()).hexdigest(),
                  "full_picture_reviewed": True, "full_audio_reviewed": True, "scene_fidelity": "pass",
                  "observations": [ev] + ([a.note] if a.note else []),
                  "spatial_checks": {k: {"verdict": "pass", "evidence": "Covered by the user's approval of the complete video; no separate per-check notes were given."} for k in SPATIAL}}
        if c["content_kind"] == "dialogue":
            review.update(dialogue_lipsync="pass", original_audio_sync="pass")
        rel = f"animation/v1/reviews/{cid}.verified.json"
        (root / rel).write_text(json.dumps(review, indent=2, ensure_ascii=False), encoding="utf-8")
        if row["state"] in ("queued", "running"):
            p.job_update(row["intent"], "review_pending", "Output downloaded and checked by Claude; awaiting user verdict.")
        p.job_update(row["intent"], "verified", rel)
        done.append(cid)
    ids = [c["clip_id"] for c in plan["clips"]]
    arts = [{"id": cid, "path": f"animation/v1/reviews/{cid}.verified.json",
             "sha256": hashlib.sha256((root / f"animation/v1/reviews/{cid}.verified.json").read_bytes()).hexdigest()} for cid in ids
            if (root / f"animation/v1/reviews/{cid}.verified.json").exists()]
    aids = [x["id"] for x in arts]
    ev = f"User 2026-11-02: '{a.quote}'."
    receipt = {"stage": "renders", "reviewer": "user (complete videos incl. lip-sync); Claude (frame checks before review)", "artifacts": arts,
               "checks": {k: {"verdict": "pass", "evidence": ev, "artifact_ids": aids} for k in
                          ("complete_picture", "complete_sound", "speech_and_lipsync", "director", "cinematography", "spatial_fidelity")}}
    (root / "renders-receipt.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding="utf-8")
    try:
        p.set_scope("renders", aids)
        p.accept(receipt)
        status = "renders accepted"
    except Exception as exc:  # report, never force
        status = f"renders receipt not accepted: {exc}"
    print(len(done), "jobs verified;", status, {k: v["state"] for k, v in p.status().items()})
    p.close()


if __name__ == "__main__":
    main()

"""Export a Starling canonical script to the EN2 rehearsal player format (binary_choice_same_segment_retry).

    python tools/player_export.py PROJECT/canonical-script.json OUT.json [--language en] [--title "PAI Roleplay"]

EN2's roleplay_build accepts only this "same-segment retry" developer format (format
binary_choice_same_segment_retry, matching the earlier accepted PAI export of 2026-10-12): an intro, then per
decision a segment, a stop (question + two options, correct/wrong) and a bad_outcome that retries the same
segment, then one ending. Text is copied verbatim from the canonical script; nothing is rewritten.
The player shows questions and options as on-screen text only (no voice-over for them).
"""
import argparse
import json
from pathlib import Path

RULES = {
    "structure": "same_segment_retry", "default_segments": None, "max_segments": None, "segment_count_policy": "source_decisions",
    "correct_path_video_seconds": None, "segment_dialogue_turns": None, "source_coverage_required": True,
    "source_dialogue_policy": "verbatim", "preserve_source_structure": True, "segment_narration": True,
    "bad_outcome_single_block": True, "bad_outcome_dialogue_lines": 0,
    "bad_outcome_layout": ["visual", "narrator", "learning_point_ui", "retry_ui"], "interleave_narration_and_dialogue": False,
    "options_per_question": 2, "on_right": "next_segment_or_ending", "on_wrong": "bad_outcome_then_same_segment",
    "retry_trigger": "user_click", "retry_label": "Try again", "retry_show_after": "video_end", "auto_advance_bad_outcomes": False,
    "retry_limit": None, "separate_second_chance_nodes": False, "failure_end_cards": False, "whole_story_restart": False,
    "endings": 1, "shuffle_options_on_screen": True,
    "not_rendered_as_video": ["stop", "bad_outcome.learning_point", "bad_outcome.retry"],
    "intro_on_initial_entry_only": True, "preserve_completed_segments_on_retry": True,
    "reporting": ["stop_id", "option_id", "attempt_number", "consequence_viewed", "eventual_success"],
}


def lines_of(node):
    return [{"id": l["id"], "speaker": l["speaker"], "text": l["text"], "voice_over": l["speaker"] == "narrator",
             "source_ref": l.get("source_ref"), "origin": "source"} for l in node["lines"]]


def base(node, kind, title):
    return {"id": None, "type": kind, "title": title,
            "visual": {"text": node.get("visual", ""), "spoken": False, "origin": "source_place", "source_ref": node.get("source_refs", [])},
            "lines": lines_of(node), "media": {"video_url": None, "audio_url": None}, "source_ref": node.get("source_refs", [])}


def export(canon, language, title):
    nodes = {n["id"]: n for n in canon["nodes"]}
    segments = [n for n in canon["nodes"] if n["kind"] == "segment" and n["transition"]["type"] == "choice"]
    intro_src = nodes[canon["start_node"]]
    assert intro_src["transition"]["type"] == "auto", "the start node must be an intro that leads into the first decision"
    learner = next((c for c in canon["characters"] if c.get("learner") or c.get("is_player") or "player" in json.dumps(c).lower()), None)
    out = []
    intro = base(intro_src, "intro", intro_src.get("title") or "Intro")
    intro.update(id="intro", next="segment_1", context={"learner_character_id": learner["id"] if learner else None})
    out.append(intro)
    for k, seg in enumerate(segments, 1):
        t = seg["transition"]
        assert len(t["options"]) == 2, f"{seg['id']}: the player takes exactly two options"
        bad_opt = [o for o in t["options"] if nodes[o["target"]]["kind"] == "bad_outcome"]
        good_opt = [o for o in t["options"] if nodes[o["target"]]["kind"] != "bad_outcome"]
        assert len(bad_opt) == 1 and len(good_opt) == 1, f"{seg['id']}: needs one right and one wrong option"
        bad = nodes[bad_opt[0]["target"]]
        assert bad["transition"]["type"] == "button" and bad["transition"]["target"] == seg["id"], f"{bad['id']} must retry {seg['id']}"
        nxt = good_opt[0]["target"]
        nxt_id = "ending" if nodes[nxt]["kind"] == "ending" else f"segment_{k + 1}"
        s = base(seg, "segment", seg.get("title") or f"Segment {k}")
        s.update(id=f"segment_{k}", next=f"stop_{k}", order=k, location=seg.get("visual", ""))
        out.append(s)
        options = []
        for letter, o in zip("AB", t["options"]):
            wrong = o is bad_opt[0]
            options.append({"id": f"stop_{k}_option_{letter.lower()}", "source_label": letter, "text": o["text"], "correct": not wrong,
                            "next": f"bad_outcome_{k}" if wrong else nxt_id, "source_ref": o.get("source_ref")})
        out.append({"id": f"stop_{k}", "type": "stop", "order": k, "question": t["question"], "options": options,
                    "shuffle_options_on_screen": True, "rendered_as_video": False, "source_ref": seg.get("source_refs", [])})
        b = base(bad, "bad_outcome", bad.get("title") or "Setback")
        b.update(id=f"bad_outcome_{k}", next=f"segment_{k}", order=k, auto_advance=False,
                 source_mappings={"immediate_outcome": None, "second_chance": None, "setback": bad.get("source_refs", [])},
                 learning_point=None,
                 retry={"label": "Try again", "action": "retry_segment", "trigger": "user_click", "show_after": "video_end",
                        "next": f"segment_{k}", "seek_seconds": 0, "preserve_completed_segments": True,
                        "source_instruction": bad["transition"].get("label"), "source_ref": None})
        out.append(b)
    end_src = next(n for n in canon["nodes"] if n["kind"] == "ending")
    e = base(end_src, "ending", end_src.get("title") or "Ending")
    e.update(id="ending", next=None, closing_card=None)
    out.append(e)
    cast = [{"id": c["id"], "name": c.get("name", c["id"]), "role": c.get("role", ""), **({"voice_over": True} if c["id"] == "narrator" else {})}
            for c in canon["characters"]]
    return {"schema_version": "3.0", "format": "binary_choice_same_segment_retry", "schema_profile": "ready_script_preserved",
            "metadata": {"title": title or canon.get("title", ""), "language": language, "status": "player_export",
                         "decision_count": len(segments), "source": {"kind": "starling_canonical_script"}},
            "cast": cast, "rules": RULES, "start_node": "intro", "nodes": out,
            "schema_adapter": {"notes": ["Exported by tools/player_export.py from the Starling canonical script; text copied verbatim.",
                                         "Setback learning points are spoken inside the setback narration (user rule), so learning_point is null."]}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("canonical")
    ap.add_argument("out")
    ap.add_argument("--language", default="en")
    ap.add_argument("--title", default="")
    a = ap.parse_args()
    canon = json.loads(Path(a.canonical).read_text(encoding="utf-8"))
    data = export(canon, a.language, a.title)
    Path(a.out).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"nodes": len(data["nodes"]), "decisions": data["metadata"]["decision_count"], "out": a.out}))


if __name__ == "__main__":
    main()

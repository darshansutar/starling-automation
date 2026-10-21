---
name: starling-verification
description: Review Starling images, labelled narration storyboards, complete EN2 videos and final node assemblies against approved sources without generating media.
---

# Starling Verification

Apply [buffered timing and visual review](../starling-animation-pack/references/timing-and-visual-review.md) for storyboard/prompt timing, per-output visual checks, bounded repair and the user-owned manual lip-sync check.

Follow the [scene-matched reference selection](../starling-animation-pack/references/reference-bundle.md), including its failed-output repair exception.

Check temporal and lighting continuity throughout each clip: sky colour, sun position, exposure, artificial lights and shadow direction/length remain consistent with the approved scene. Flag unplanned timelapse, day/night cycling, changing weather or light flicker, even if the opening and closing frames match. Permit a time transition only when explicitly supported by the source and approved shot plan.

Review only the requested scope. Read [the handoff](../starling-prompt-pack/references/handoff-contract.md), [visual routing](../starling-animation-pack/references/visual-routing.md) and [spatial fidelity](../starling-cinematography/references/spatial-fidelity.md). Use Panel Corrector for still criteria, Animation Pack for video/assembly criteria and Director/Cinematography for their required verdicts. This review skill does not generate repairs, submit jobs, publish or activate monitoring.

Follow [narration storyboard production](../starling-animation-pack/references/narration-pairs.md) for audio-led beat coverage, 1x2/1x3 selection, monochrome style fidelity, white action/camera label backgrounds, whole-second printed timings and active side-view staging without back shots.

## Bind evidence

Identify canonical script/branches, accepted audio/cues, style/assets, exact image/board versions, prompts, motion plan and requested outputs. Record hashes and source IDs. Missing comparison material limits fidelity claims but does not prevent reporting a visible defect. Determine actual full picture/audio inspection capabilities before claiming them.

## Inspect

For stills inspect each complete image and all pictures and labels at useful resolution. Check identity, anatomy, cast, set/state, source meaning, clean presentation, aspect and framing and all applicable spatial checklist items. Verify the top-to-bottom pictures form two or three related shots, with matching camera/action/time labels below them and no arrows. All pictures and label accuracy must pass.

For video inspect complete normal-speed picture and sound, plus detailed cuts/suspicious intervals. Compare each shot against its actual storyboard picture, detailed panel description, printed action/camera/timing labels, saved inventory and scene-matched reference map. Confirm that reference selection follows visible identities: one-character shots do not inherit unrelated character sheets, and environment-only clips omit character and prop sheets. Shared two- or three-shot requests use the union of the shot inventories while preserving visibility separately in each shot. Flag added, duplicated or missing people/objects and reference-sheet content leaking into the scene, including temporary appearances during motion or cuts. Check approved visible inventory, only planned movement, supported action/contact, consistent background state, physical scale/depth/occlusion/orientation, the planned camera motion and the planned two- or three-shot sequence. Check every measured hard cut and edge-to-edge colour presentation. Flag fades, dissolves, overlays, white borders/frames, mixed storyboard panels, printed labels or layout leakage. Inspect all intervening motion; matching sampled frames alone cannot pass the clip. In camera-only clips, reject any object or subject movement beyond the planned change of framing, including temporary opening/closing, cargo changes or newly revealed invented content. Narration subjects remain silent; original voice-over is checked at assembly. Dialogue requires exact speakers, full accepted speech and original-audio alignment. Lip-sync is verified by the user and recorded separately against the exact output hash. Pending manual sync does not fail the visual review or trigger a replacement; it keeps overall dialogue acceptance pending. Samples/transcripts/metadata alone cannot establish whole-video acceptance.

For final nodes check selected EN2 provenance, complete words/pauses at original speed, all joins, the user’s manual dialogue-sync verdict, canonical order, actual outcomes and every required branch. Review cuts containing unverified footage are not final delivery. Existing local animation alternatives are retained as history and excluded from current selection.

## Decide and hand off

Use [review-record.md](references/review-record.md). Required checks are pass, fail or unverified; not_applicable requires a reason. Overall needs_fix if any required check fails, unverified when evidence is missing without an observed failure, verified only when all required checks pass or are justified inapplicable. Record exact observations, panel/region or actual time range, expected state, severity and smallest repair owner.

Return verification_report.json and counts for the declared scope. Production owners perform authorized image/prompt/EN2 repairs and return replacements for complete review. Preserve originals and review history. Never approve a render merely because the provider completed it.

Before stitching narration, filler, establishing or ending clips, remove the complete generated audio track, including background voices, and discard subtitle/text streams. Use only the accepted external narration for those intervals. Inspect the full picture for unwanted captions, labels and overlays. Burned-in text is part of the pixels: correct/regenerate the affected scene and re-review it before assembly; dropping a subtitle track does not erase it. Preserve source-required real-world signage. Dialogue retains its verified embedded speech and lip-sync.

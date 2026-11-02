---
name: starling-verification
description: Review Starling images, labelled narration storyboards, complete EN2 videos and final node assemblies against approved sources without generating media.
---

# Starling Verification

**Owner:** Claude reviews images, storyboards, prompts and technical evidence. The user reviews complete videos, final assemblies and lip-sync; Claude records the user's verdicts and never supplies them. See [roles and handoff](../starling-production-master/SKILL.md#roles-and-handoff).

Apply [buffered timing and visual review](../starling-animation-pack/references/timing-and-visual-review.md) for storyboard/prompt timing, per-output visual checks, bounded repair and the user-owned manual lip-sync check.

Follow the [scene-matched reference selection](../starling-animation-pack/references/reference-bundle.md), including its failed-output repair exception.

Review only the requested scope. Read [the handoff](../starling-prompt-pack/references/handoff-contract.md), [visual routing](../starling-animation-pack/references/visual-routing.md) and [spatial fidelity](../starling-cinematography/references/spatial-fidelity.md). Use Panel Corrector for still criteria, Animation Pack for video/assembly criteria and Director/Cinematography for their required verdicts. This review skill does not generate repairs, submit jobs, publish or activate monitoring.

Follow [narration storyboard production](../starling-animation-pack/references/narration-pairs.md) for transcript-first timing, fixed 1-3 shot layout, exact caption fields, source fidelity, transport verification and the pilot gate.

## Bind evidence

Identify canonical script/branches, accepted audio/cues, style/assets, exact image/board versions, prompts, motion plan and requested outputs. Record hashes and source IDs. Missing comparison material limits fidelity claims but does not prevent reporting a visible defect. Claude inspects stills, storyboards, prompts and technical evidence directly. Claude cannot watch video, so complete normal-speed picture and sound review of clips and final nodes is performed by the user; Claude prepares the review list (clip, output hash, storyboard, expected action and timing, specific things to check) and records only the verdicts the user gives. Frame extracts and contact sheets may point the user at suspicious intervals but never pass a clip.

## Inspect

For dialogue, compare framing throughout the full spoken line and fail any pan, tilt, zoom, dolly, tracking, orbit, crane, drift, recentering, reframing or focal-length change; the required camera is a pixel-locked static tripod. For narration, the storyboard is the per-shot composition authority: compare every shot, including the final shot, with its corresponding panel's complete environment, blocking, relative depth and visible inventory. Fail any appearance sheet, turnaround, neutral-background group or prop plate rendered as a scene.

For stills inspect each complete image and all pictures and labels at useful resolution. Check identity, anatomy, cast, set/state, source meaning, clean presentation, aspect and framing and all applicable spatial checklist items. Run `python pipeline/storyboard.py verify` on every narration board, then confirm its three pictures and the shot/time/camera/defining-action fields below them match the timing table. All pictures and label accuracy must pass.

Check temporal and lighting continuity throughout each clip: sky colour, sun position, exposure, artificial lights and shadow direction/length remain consistent with the approved scene. Flag unplanned timelapse, day/night cycling, changing weather or light flicker, even if the opening and closing frames match. Permit a time transition only when explicitly supported by the source and approved shot plan.

For video the user inspects complete normal-speed picture and sound, plus detailed cuts/suspicious intervals. Compare each shot against its actual storyboard picture, detailed panel description, printed action/camera/timing labels, saved inventory and scene-matched reference map. Confirm that reference selection follows visible identities: one-character shots do not inherit unrelated character sheets, and environment-only clips omit character and prop sheets. Shared multi-shot requests use the union of the shot inventories while preserving visibility separately in each shot. Flag added, duplicated or missing people/objects and reference-sheet content leaking into the scene, including temporary appearances during motion or cuts. Check approved visible inventory, only planned movement, supported action/contact, consistent background state, physical scale/depth/occlusion/orientation, the planned camera motion and the planned shot sequence. Check every measured hard cut and edge-to-edge colour presentation. Flag fades, dissolves, overlays, white borders/frames, mixed storyboard panels, printed labels or layout leakage. Inspect all intervening motion; matching sampled frames alone cannot pass the clip. In camera-only clips, reject any object or subject movement beyond the planned change of framing, including temporary opening/closing, cargo changes or newly revealed invented content. Narration subjects remain silent: any lips moving during narration is a defect (see [auto-edit rules](../starling-auto-edit/references/rules.md)); original voice-over is checked at assembly. Dialogue requires exact speakers, full accepted speech and original-audio alignment. Lip-sync is verified by the user and recorded separately against the exact output hash. Pending manual sync does not fail the visual review or trigger a replacement; it keeps overall dialogue acceptance pending. Samples/transcripts/metadata alone cannot establish whole-video acceptance.

For final nodes the user checks, and Claude records, selected EN2 provenance, complete words/pauses at original speed, all joins, the user’s manual dialogue-sync verdict, canonical order, actual outcomes and every required branch. Review cuts containing unverified footage are not final delivery. Existing local animation alternatives are retained as history and excluded from current selection.

## Decide and hand off

Use [review-record.md](references/review-record.md). Required checks are pass, fail or unverified; not_applicable requires a reason. Overall needs_fix if any required check fails, unverified when evidence is missing without an observed failure, verified only when all required checks pass or are justified inapplicable. Record exact observations, panel/region or actual time range, expected state, severity and smallest repair owner.

Return verification_report.json and counts for the declared scope. Production owners perform authorized image/prompt/EN2 repairs and return replacements for complete review. Preserve originals and review history. Never approve a render merely because the provider completed it.

In final nodes, confirm that narration, filler, establishing and ending intervals carry only the accepted external narration (no rendered voices or subtitle streams), that no unwanted burned-in captions, labels or overlays remain, and that dialogue keeps its verified embedded speech. Animation Pack owns the stitching steps.

# Narration storyboard production

Narration, filler, establishing and ending coverage use a black-and-white 1x2 line-drawing storyboard: two related shots stacked upper then lower. Each shot is an independent composition illustrating the same narration beat. Dialogue retains its clean-scene and accepted reference-audio workflow.

## Plan and draw

Map both shots to canonical source lines, branch facts and measured narration. Record visual_format=storyboard_1x2, shot_count=2 and exactly one cut_times value inside the generated interval. Follow [buffered timing and visual review](timing-and-visual-review.md): add 1–2 seconds per shot before drawing, print generated ranges and action/hold durations below both panels, repeat those exact timings and hard cut in the prompt, and save per-shot assembly source_spans. Keep generated duration and required edit duration separate. Check live provider limits and split if needed. Preserve original audio speed and complete source coverage. Split long narration at measured cues.

Create and inspect final-colour character sheets, matching environments and prop sheets first, following [the required reference bundle](reference-bundle.md). Build each storyboard with two wide illustrated picture areas at the target video aspect. Put a white caption strip BELOW each picture containing SHOT number, time range, CAMERA and ACTION. Keep the artwork itself free of planning text, arrows, motion symbols and gesture marks. Record picture-area boxes separately from caption strips and sheet boundaries. Captions and saved timings/actions must agree.

Plan restrained, visible, source-supported character action where appropriate. Describe its beginning, movement and settling pose; avoid freezing active characters. For a genuinely quiet shot, use a subtle 3–5 percent push-in or a small pan within established content. Camera movement alone preserves subject and object states. Keep identities, hairstyles, PPE, physical contact, object orientation, scale, weather and lighting consistent with the source. Each shot carries an exact visible cast and object inventory, including zero people for an empty insert.

## Inspect then prompt

Inspect both actual pictures and labels against accepted source/audio and identity references before writing the animation prompt. Apply the spatial fidelity checklist, including perspective, depth, supported contact, clearance, front/back faces and occlusion. Repair observed defects and recheck the whole board.

Attach all four required groups in order: character sheets, matching environment, prop sheets, storyboard. Follow reference-bundle.md for context-only visibility in empty inserts and missing references. Multiple sheet views supply appearance, not additional cast. Keep a visible gap between adjacent people and clearance for their gestures. Record exact attachment indexes, roles, paths and hashes; rebuild indexes after any change.

Use the five-section template in animation-template.md. Select 2D, 2.5D or 3D animation from the approved colour references; the planning drawing does not change the intended output style. Write affirmative instructions describing the desired result rather than negative-prompt lists. For presentation use: “Render each illustrated scene individually as an edge-to-edge, full-frame colour shot. At the specified time, switch directly to the next fully formed shot using a hard cut. Treat the storyboard layout and caption strips exclusively as production guidance.”

Specify observable action and camera motion separately for each timed shot. Use the storyboard's exact visible inventory. Unassigned machinery, gates, cargo and lighting retain their depicted state. Narration characters have naturally relaxed, closed mouths. Prepare a silent visual sequence for the accepted narration added at assembly.

## Submit and review

Upload the inspected board and relevant colour references, verify returned bytes, then submit refs in the recorded order with Fast quality=false. Keep narration external. Save exact payload, prompt, audio mapping, picture boxes, shot inventory review, upload evidence, intent and provider ID.

Review the complete video: two sequential full-frame shots, one hard cut at the planned time, source-faithful action and consistent identity/geometry. Reject fades, dissolves, overlays, mixed panels, white borders/frames, printed labels or storyboard layout appearing in the output. These are review criteria; generation prompts express the affirmative target above. Inspect all motion and sound; a contact sheet cannot certify the result. Follow Animation Pack's single scene-redesign replacement limit under the same logical clip ID. Preserve original media and paid-job history.

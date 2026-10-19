# Storyboard-grounded animation prompts

Inspect the actual pictures, below-picture labels and accepted audio before writing. Use [scene preservation](scene-preservation.md) for the detailed shot description and [reference selection](reference-bundle.md) for the attachments. Describe the approved composition and action precisely, using affirmative instructions. Omit unrelated stock wording and subjects absent from the shot.

Discover the live EN2 reference guide before submission. Its current format has six sections in this order: subject_definitions, summary, retention_analysis, detailed_description, overall_soundscape, non_diegetic_music. Historical five-section prompts remain archived; new prompts use the current provider format. If the live contract changes, reconcile the template and validator before submitting.

## Reference definitions

Define reusable identities, environments and props as <Subject N> sourced from their actual <Picture N>. Give the storyboard or clean scene its own <Picture N> entry as the composition anchor. Use <Audio N> for accepted dialogue recordings. Number each label category consistently and rebuild indexes after attachments change. Define only selected references; save filenames, hashes, upload names and per-shot visibility outside the prompt.

For narration, explicitly map the upper storyboard picture to Shot 1 and lower picture to Shot 2. Asset sheets supply appearance; the storyboard supplies composition, visible inventory, shot order and the printed action/camera/timing plan. Final footage presents each picture as one edge-to-edge colour shot. The board layout and caption strips remain production guidance.

## Narration structure

Replace the placeholders with inspected scene facts and measured timing. Definitions and indexes vary with the selected bundle; an environment-only sequence has no character or prop-sheet definitions.

```text
subject_definitions:
[Define only visible identities and relevant environment/prop subjects from the actual images.]
<Picture N> is the inspected two-shot storyboard. The upper picture defines Shot 1 and the lower picture defines Shot 2, including composition, visible inventory and printed CAMERA/ACTION/timing instructions.

summary:
[reference generation] [Duration]-second [2D, 2.5D or 3D] sequence showing [source-supported scene]. Two full-frame colour shots follow <Picture N>, with one hard cut at [cut time].

retention_analysis:
[For each selected Subject, state its assigned appearance role and the shots where it is visible.]
<Picture N>: fully_preserved - preserve the two compositions, visible inventories, spatial relationships and planned actions. Render one edge-to-edge colour scene at a time; the sheet layout and captions serve only as production guidance.

detailed_description:
[Animation style, colours, materials, depth and lighting from the inspected colour references.]
[Shot 1] [Generated range.] [Detailed upper-picture composition: visible cast, positions, expression/pose/gaze, props and support/orientation, background and camera side.] ACTION [interval]: [exact supported movement from the label, starting state and final pose]. CAMERA: [printed move and extent, or static]. BUFFER [interval]: [settled state]. [Scene-specific relationships that remain unchanged.]
[Shot 2] At [MM:SS.mmm], hard cut to [generated range and detailed lower-picture composition]. ACTION [interval]: [labelled movement and final pose]. CAMERA: [printed instruction]. BUFFER [interval]: [settled state]. [Continuity with Shot 1 and any explicit final provider-rounding hold.]

overall_soundscape:
Silent visual sequence; approved original narration is added during assembly.

non_diegetic_music:
N/A
```

State concrete observable motion. For a camera-only document insert, the camera reveals the existing rows while papers remain supported and unchanged. For an environment-only pond shot, describe the pictured shore, water level, inlet, steps and light, then the labelled ripples or trickle and camera movement. Do not introduce activity merely to fill time.

For an eight-second example with three seconds of required action per shot and one-second buffers: Shot 1 action 0–3, hold 3–4; hard cut at 4; Shot 2 action 4–7, hold 7–8. Print those same ranges below the pictures. Assembly source_spans [[0,3],[4,7]] retain six seconds without stretching narration. Follow the [timing contract](timing-and-visual-review.md).

## Dialogue adaptation

Use the same six sections, with the inspected clean scene as the composition anchor and the accepted speech as reference audio. Describe the actual visible participants, their separate positions and hand/prop contacts. The single-shot or approved multi-shot description preserves the complete turn, expression, listener response and camera plan. Do not impose a static camera when the approved scene plan specifies a move.

Assign speaker IDs in order of actual vocal events. An example binding is: `<Audio 1> is the approved speech for <Subject 1> (S1).` In detailed_description use `<Subject 1> (S1) says, <d>[English] Exact approved words.</d>`, keeping the original language and all source words. Preserve source-required off-screen speech without adding an unseen person to the image bundle.

For complete accepted audio reuse, begin summary with `[reference generation + audio reuse]` and use the audio retention marker `fully_copy`; preserve the recording from its beginning, including pauses and its final utterance, at original speed. Use `partially_copy` or `reference` only when that is the actual approved audio relationship. Visible reference roles use the provider's visual markers such as `fully_preserved`; do not apply visual retention markers to audio. overall_soundscape describes the approved sound layers; non_diegetic_music states N/A unless a score is explicitly planned.

## Preflight

Compare every written shot description, visible subject, object, movement, contact, camera instruction and timing against the corresponding actual picture and labels. Record shot_inventory_match with image hashes and observations. Check complete accepted speech and speaker mapping for dialogue. Follow [submission](en2-submission.md) for payloads and provider limits. Prompt detail and structural validation cannot replace complete rendered-picture and sound review.

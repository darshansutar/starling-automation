# Five-section animation templates

Adapted from the user's Home-Palliative Care prompt pack. Both production routes use these five headings. Write affirmative instructions describing the desired result; keep defect lists in review checklists. Read [narration storyboard production](narration-pairs.md) for the current narration method.

Inspect the approved clean scene and accepted speech first. Record visible cast, positions, object ownership/contact, background, lighting and supported movement. Attach only references needed by those visible subjects. Character sheets supply identity, not extra occupants; the clean scene controls composition. Save actual sequential Picture/Audio indexes and file hashes outside the prompt. Rebuild indexes when attachments change.

## Dialogue template

Use exactly these five headings. The indexes below are illustrative; match actual attachments and measured timing.

```text
subject_definitions:
<Picture 1> is the approved clean scene: [exact visible cast, positions and objects]. It controls framing, inventory and lighting.
<Picture 2> supplies [visible character]'s identity only: [retained traits].
<Audio 1> supplies [speaker]'s accepted speech and selected voice.

summary:
[reference generation] The target video runs [duration] seconds. [Concrete scene action.] Follow <Picture 1> with exactly [visible cast]. [Speaker] delivers the supplied speech while [listener] listens.

retention_analysis:
<Picture 1>: fully_preserved - [composition, cast, supported contact, background and lighting].
<Picture 2>: [fully_preserved/partially_preserved] - [assigned identity traits; explicit scene-grounded exceptions].
<Audio 1>: fully_preserved - [exact speaker, voice and original words].

detailed_description:
[Shot 1] [2D, 2.5D or 3D animation matching the inspected visual style; approved framing.] [Starting pose, gaze and contact.] [Exact supplied dialogue using the live reference guide's speech syntax and correct audio/speaker mapping.] [Observable gesture during the measured turn, listener response and final hold.] Camera remains fixed. [Only action supported by the scene.]

overall_soundscape:
[Supplied dialogue and explicitly planned compatible sound.] The supplied dialogue is the complete soundtrack.
```

Describe observable acting rather than emotional labels alone. Keep reference/state facts in retention_analysis and movement in detailed_description. Use fully_preserved only for the assigned role actually retained; name exceptions. Preserve words, voices and complete turns. Music decisions belong in overall_soundscape, not a sixth heading.

## Preflight evidence

Compare every prompted person, object, entry/exit, sound source and movement with the inspected inventory and source. Off-screen sound does not authorize an on-screen actor. Record shot_inventory_match with observations and image hashes. Follow [scene preservation](scene-preservation.md) and [submission](en2-submission.md). Runtime checks structure, not image semantics.

## Narration template

Inspect the actual storyboard first. Attach only relevant references in character, environment, prop, storyboard order. Omit unused categories; match every Picture index to its real upload. The example has one character reference, one environment reference and one storyboard; adapt actions to the inspected artwork.

```text
subject_definitions:
<Picture 1> supplies Meera's appearance: white hardhat, clear goggles, low dark bun, navy shirt and orange vest.
<Picture 2> supplies the workshop colours, lighting and machine materials.
<Picture 3> is the labelled 1x2 storyboard. Its upper picture defines Shot 1; its lower picture defines Shot 2. Each picture determines the visible cast, objects, placement and composition. Labels below the pictures provide timing, camera and action instructions.

summary:
[reference generation] An 8-second coloured 2D illustrated animation with two related shots. Meera inspects the machine, then considers what she notices. A direct hard cut at 4 seconds connects the shots.

retention_analysis:
<Picture 1>: partially_preserved - apply Meera's identity, hairstyle, clothing and proportions to the storyboard character.
<Picture 2>: partially_preserved - apply its appearance to the workshop and machine regions drawn in each shot.
<Picture 3>: fully_preserved - follow both illustrated compositions, visible inventories and action instructions. Render each illustrated scene individually as an edge-to-edge, full-frame colour shot. Treat the storyboard layout and caption strips exclusively as production guidance.

detailed_description:
Clean outlines, softly painted shading and warm colours match the supplied appearance references.
[Shot 1] 0-4 seconds: Begin immediately with the fully formed upper-panel scene, a medium shot of Meera beside the control housing. ACTION: She leans her head slightly forward to inspect it, hands comfortably behind her back, then settles. CAMERA: A gentle three-percent push-in. The machine remains stationary and lighting stays constant.
[Shot 2] 4-8 seconds: At exactly 4 seconds, switch directly to the fully formed lower-panel scene using a hard cut, a close-up of Meera and the housing. ACTION: Her gaze moves down the housing; she tilts her head slightly, blinks once naturally and settles. CAMERA: Static.
Each shot occupies the entire canvas, with scene imagery extending to every edge. Display one complete scene at a time. Preserve the pictured cast count, identity, hairstyle, object scale, contact and spatial relationships. Meera's mouth stays naturally relaxed and closed.

overall_soundscape:
Silent visual sequence prepared for the approved narration track to be added during assembly.
```

Replace example cast, props, actions, timings and animation style with the inspected storyboard and measured audio plan. Use 2D, 2.5D or 3D according to approved colour references. Captions and prompt must agree. Record geometry and review evidence outside the prompt.

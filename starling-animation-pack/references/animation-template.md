# Five-section animation template

Adapted from the user's Home-Palliative Care animation pack. These are our writing conventions; discover live EN2 payload fields, reference syntax and limits before submission.

## Inspect and map before writing

Inspect each actual approved panel. Save its visible people (including partial bodies), counts, positions, objects, ownership/contact, background and lighting state, and permitted movement. Record empty backgrounds explicitly. Script meaning determines the action; the approved panel determines what is visible. Repair the panel first if required action needs missing people, objects or staging.

Attach only relevant character sheets, environment, props and the complete board, in that order. For dialogue use the approved clean scene and accepted audio, with supplementary assets only when useful. Save an ordered filename/index/role/shot map outside the prompt. Use actual sequential `<Picture N>` and `<Audio N>` indexes. Rebuild this map and all prompt mentions if optional references are removed to meet live limits.

The board supplies composition, visible cast and state; character sheets supply identity, environment plates supply relevant set details, and props supply construction/material. Multiple views on a sheet represent one identity. A person visible in one shot must not appear in the other unless that panel also shows them. Exclude sheets for characters absent from the clip. References do not introduce their other occupants or objects into the scene. Name panel-grounded exceptions when wardrobe, visibility or state differs from an asset reference.

## Template

Use exactly these five headings, in order. Replace placeholders with inspected facts and measured timing. The three Picture entries below are illustrative; include exactly the references attached.

```text
subject_definitions:
<Picture 1> is the character-design reference for [visible character]: [distinctive identity traits]. It supplies appearance only for [applicable shots].
<Picture 2> is the environment reference for [location]: [relevant set details]. It does not add contents absent from the board.
<Picture 3> is the approved storyboard: TOP defines [Shot 1], BOTTOM defines [Shot 2]. It controls framing, visible people/objects, placement and lighting. Render one full-screen shot at a time; the sheet layout is not shown.

summary:
[reference generation] The target video runs [measured duration] seconds. [Scene purpose and concrete action progression.] Follow <Picture 3>. [Exact visible cast for each shot, including zero where appropriate.] Characters remain silent; narration is added separately.

retention_analysis:
<Picture 1> ([applicable shots]): fully_preserved - [specific identity traits retained and which body parts are actually visible].
<Picture 2> ([applicable shots]): partially_preserved - [set details retained and explicit panel-grounded lighting/state differences].
<Picture 3> ([Shot 1], [Shot 2]): partially_preserved - [panel-specific framing, positions, count, prop ownership and contact retained]; stacked-sheet presentation is excluded. [Relevant empty background or fixed object state.]

detailed_description:
The target video is [approved rendering style, palette and texture].
[Shot 1] [Framing and starting arrangement visible in the top panel.] [Character/reference identity, position, gaze and supported contact.] [Specific movement, expression change and resulting hold during the measured interval.] [Relevant objects/background retain their pictured state.] Camera remains fixed. No speech.
[Shot 2] At [exact measured timestamp], hard cut to [bottom panel composition]. [Exact cast and starting state.] [Supported action sequence and end state.] Camera remains fixed. Hold until [clip end]. No speech.

overall_soundscape:
[Only planned sound compatible with the audio/assembly plan.] No generated narration or music. [For the current narration assembly route, request silence: accepted narration is added separately and generated sound is discarded.]
```

Describe observable acting: gaze shifts, supported hand movement, expression and end hold, rather than only an emotional adjective. Quiet shots can remain still. Avoid invented background activity or generic setting phrases that imply additional occupants.

Use `fully_preserved` only for the assigned reference role actually retained. Use `partially_preserved` and name exceptions when needed; the label alone does not establish fidelity. Put reference/state facts in retention_analysis and action progression in detailed_description. Keep sections consistent on lighting, inventory, timing and reference roles, without repeating long restriction lists.

For dialogue keep these five headings but describe the clean scene, supplied `<Audio N>`, exact speaker/turn mapping and measured action/lip-sync. Preserve source words and selected voices; do not invent a voice or request generated narration. Dialogue retains its clean-scene route. Music decisions belong in overall_soundscape, not a sixth heading.

## Action-writing example

For an inspected panel showing one seated person holding a phone: "Exactly one person is visible. Nitin sits at frame right, his forearm supported on his thigh and the phone already in his right hand. He lowers his gaze to the dark screen, blinks once and holds. His thumb rests on its edge; the empty passage and closed door retain their pictured state. Camera fixed." This illustrates specificity, not a default character or action to insert elsewhere.

## Preflight evidence

Save the shot inventory and reference map with the prompt/plan, bound to inspected image hashes. Compare every prompt person, object, entry/exit, sound source and movement against the inventory and source. Off-screen sound does not authorize an on-screen actor. Record `shot_inventory_match` with concrete observations and artifact IDs, not just filename/count agreement. The runtime checks the receipt and headings; it cannot inspect image semantics. Follow [scene preservation](scene-preservation.md) and [submission](en2-submission.md).

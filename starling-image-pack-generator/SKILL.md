---
name: starling-image-pack-generator
description: Generate and review foundational assets, labelled narration storyboards and clean dialogue scenes using native ChatGPT images.
---

# Starling Image Pack Generator

Apply [buffered timing and visual review](../starling-animation-pack/references/timing-and-visual-review.md) for storyboard/prompt timing, per-output visual checks, bounded repair and the user-owned manual lip-sync check.

Follow the [scene-matched reference selection](../starling-animation-pack/references/reference-bundle.md), including its failed-output repair exception.

Check [mandatory intake](../pipeline/INTAKE.md), accepted audio and the approved Prompt Pack. Read [visual routing](../starling-animation-pack/references/visual-routing.md), [narration storyboards](../starling-animation-pack/references/narration-pairs.md) and [spatial fidelity](../starling-cinematography/references/spatial-fidelity.md). Use native ChatGPT image generation/editing and the installed imagegen skill. Own image production, not video or script rewriting.

Generate assets in strict dependency order: sheets for visible characters, one scene-specific environment in two consistent views, only the required visible props, then the final storyboard. Inspect and approve each asset before using it downstream. Generate every narration storyboard on a 1024 x 1536 portrait canvas with exactly three 16:9 shots stacked vertically and an ivory caption strip directly below each picture. Keep prompts specific to visible subjects, composition and physically plausible interactions.

Each narration board stacks three wide pictures in top-to-bottom order. Put `SHOT | exact start-end time | CAMERA | DEFINING ACTION` in a consistent ivory strip below each picture, using uppercase dark text and thin vertical separators. Keep artwork free of arrows and motion symbols. Save separate picture-area boxes and matching label metadata. Each picture defines one complete shot and one defining action; Animation Pack turns it into edge-to-edge colour footage with hard cuts at the printed times.

Match time of day, sky, light sources, exposure and shadow direction/length across related shots. A zoom or pan keeps the same moment and lighting; depict a time transition only when the source explicitly calls for it.

Build each prompt from that shot's explicit cast and object inventory. Include character-specific clothing and prop-orientation details only when that character or prop belongs in the shot; generic example wording can accidentally introduce absent subjects. State the exact visible person count, including zero for inserts.

Bind each visible character to the approved identity reference across all shot sizes. Carry the actual hairstyle (shape, length, tie/bun position and hairline), face and PPE into that character's prompt. Compare close-ups with the identity reference and adjacent shots; matching the storyboard views alone does not establish character continuity.

Immediately inspect the full output and all storyboard pictures and labels at useful resolution. Apply Panel Corrector plus Director/Cinematography checks, including anatomy, identity, scale, perspective, contact, clearance, front/back orientation, occlusion and shot continuity. Repair only observed defects using the actual image and required references; reinspect the complete replacement.

Save durable originals and corrected versions with real file type, dimensions, SHA-256, picture boxes and shot/label mapping, source IDs, input/reference mappings, generation provenance and review evidence in image_manifest.json. Validate JPEG delivery where required by the upload contract; changing a filename is not conversion. All pictures, caption accuracy and their narrative relationship must pass before animation. Unresolved checks stay unverified; preserve earlier versions and paid-job history.

Follow [narration storyboard production](../starling-animation-pack/references/narration-pairs.md) for transcript-first timing, the fixed 1024 x 1536 three-shot layout, exact caption fields, asset order, continuity, complex-action control, transport verification and the pilot gate.

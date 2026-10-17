---
name: starling-image-pack-generator
description: Generate and review foundational assets, labelled narration storyboards and clean dialogue scenes using native ChatGPT images.
---

# Starling Image Pack Generator

Follow the [required reference bundle](../starling-animation-pack/references/reference-bundle.md): character sheets, matching environment, prop sheets, then the narration storyboard or existing clean dialogue scene. Generate and inspect missing sheets/environments before submission; retain the existing dialogue audio route. Repair-only exception: after a generated animation is reviewed as needs_fix, use scene-specific single-character, individual prop and matching environment references for that failed clip, following the repair procedure in the shared reference bundle. Normal first submissions use sheets; dialogue keeps its clean scene and accepted speech.

Check [mandatory intake](../pipeline/INTAKE.md), accepted audio and the approved Prompt Pack. Read [visual routing](../starling-animation-pack/references/visual-routing.md), [narration storyboards](../starling-animation-pack/references/narration-pairs.md) and [spatial fidelity](../starling-cinematography/references/spatial-fidelity.md). Use native ChatGPT image generation/editing and the installed imagegen skill. Own image production, not video or script rewriting.

Generate final-colour character sheets, matching environments and prop sheets in dependency order. Use sheets for first submissions; the shared repair procedure permits isolated scene-specific references after an incorrect animation output. Inspect each before attaching it to a dependent request. Use actual selected style images and the full required cast. Then generate each black-and-white 1x2 narration storyboard with two related shots and inspect both pictures and their below-picture labels; generate each clean dialogue scene from its approved prompt and assigned references. Keep prompts specific to visible subjects, composition and physically plausible interactions. When people stand beside each other, show a clear gap between their bodies and enough space for their gestures in both pictures.

Each narration board stacks two wide line-drawing pictures, upper then lower. Put SHOT, time range, CAMERA and ACTION in a white strip below each picture. Keep artwork free of arrows and motion symbols. Save separate picture-area boxes and matching label metadata. Each picture defines a complete related shot; Animation Pack turns it into edge-to-edge colour footage with a hard cut between shots. Clean dialogue images show actual participants without printed planning content.

Match time of day, sky, light sources, exposure and shadow direction/length across related shots. A zoom or pan keeps the same moment and lighting; depict a time transition only when the source explicitly calls for it.

Build each prompt from that shot's explicit cast and object inventory. Include character-specific clothing and prop-orientation details only when that character or prop belongs in the shot; generic example wording can accidentally introduce absent subjects. State the exact visible person count, including zero for inserts.

Bind each visible character to the approved identity reference across all shot sizes. Carry the actual hairstyle (shape, length, tie/bun position and hairline), face and PPE into that character's prompt. Compare close-ups with the identity reference and adjacent shots; matching the two storyboard views alone does not establish character continuity.

Immediately inspect the full output and both storyboard pictures and labels at useful resolution. Apply Panel Corrector plus Director/Cinematography checks, including anatomy, identity, scale, perspective, contact, clearance, front/back orientation, occlusion and shot continuity. Repair only observed defects using the actual image and required references; reinspect the complete replacement.

Save durable originals and corrected versions with real file type, dimensions, SHA-256, picture boxes and shot/label mapping, source IDs, input/reference mappings, generation provenance and review evidence in image_manifest.json. Validate JPEG delivery where required by the upload contract; changing a filename is not conversion. Both pictures, caption accuracy and their narrative relationship must pass before animation. Unresolved checks stay unverified; preserve earlier versions and paid-job history.

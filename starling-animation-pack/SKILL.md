---
name: starling-animation-pack
description: Create source-bound animation prompts, submit approved two-shot boards and dialogue scenes to EN2, review repairs and stitch accepted node videos.
---

# Starling Animation Pack

Check completed [intake](../pipeline/INTAKE.md). Read [visual routing](references/visual-routing.md), [scene preservation](references/scene-preservation.md) and [submission](references/en2-submission.md). Use [the handoff contract](../starling-prompt-pack/references/handoff-contract.md) for durable versions and IDs. Honor the requested endpoint; prompt-only work does not submit jobs.

## Prepare from accepted inputs

Inspect both actual panels of every approved board or the clean dialogue scene, relevant assets and accepted audio/cues. Verify Director/Cinematography and spatial findings. Use the [five-section animation template](references/animation-template.md), with explicit Picture roles, per-shot retention and concrete acting from the inspected composition. Save a per-shot visible inventory and ordered reference map; record shot_inventory_match before submission. A board is two related shots: top then bottom with one measured hard cut, one full-screen scene at a time and locked cameras. Movement occurs within shots. Keep original narration outside EN2; dialogue uses accepted speech with speaker/turn mapping.

Save exact prompt/payload, source hashes, refs and audio mappings, board panel boxes, shot_count, cut_times, duration/used duration, source/assembly offsets and review evidence. Inspect returned uploaded bytes as well as local originals before render acceptance. Use EN2 reference mode and Fast quality=false throughout.

## Submit collect verify repair

Submit all preflight-approved clips once in an ordered pass respecting provider capacity. Record intents before tool calls and actual job IDs immediately afterward. Reconcile uncertain outcomes and existing jobs before retrying. Collect completed outputs and account for pending/failed jobs. Then use Verification with Director/Cinematography to inspect every complete picture and sound; technical decode and sampled sheets do not certify quality.

Apply the general spatial checks throughout motion, plus action fidelity, shot order/cut timing, silence in narration and dialogue speech/lip-sync. Correct an image/staging defect upstream; correct a prompt/render defect with a targeted EN2 replacement. Preserve correct work and all original outputs/IDs. Allow at most two replacements after the initial attempt. Re-review every replacement; exhausted or unavailable checks stay blocked. FFmpeg does not replace failed animation with stills or zoom effects.

## Stitch and deliver

Read [postproduction](../pipeline/POSTPRODUCTION.md). Reconcile the complete current manifest and assembly timeline, including dialogue, with explicit runtime_clip_id mappings. Only verified EN2 outputs can be selected. Trim/normalize and stitch by canonical node order; preserve original speech speed, words, pauses and measured joins. The current assembler uses pre-cut original audio units from their beginnings and discards generated sound; additional source offsets or sound mixing need an explicit supported plan.

Keep mutually exclusive outcomes separate. Review each final node's full picture/sound, all words, dialogue sync, cuts and joins. Record acceptance in runtime and postproduction, then package reviewed nodes with script/choices, plan and provenance. Report every blocked/unverified item and actual monitoring status. A completed provider job is not an approved video.

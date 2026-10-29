---
name: starling-production-master
description: Coordinate Starling production from mandatory intake through script, accepted audio, labelled narration storyboards, EN2 rendering, review and node assembly.
---

# Starling Production Master

Apply [buffered timing and visual review](../starling-animation-pack/references/timing-and-visual-review.md) for storyboard/prompt timing, per-output visual checks, bounded repair and the user-owned manual lip-sync check.

Follow the [scene-matched reference selection](../starling-animation-pack/references/reference-bundle.md), including its failed-output repair exception.

Read [the workflow](../pipeline/WORKFLOW.md) and use its runtime for scopes, evidence, handoffs and job history. ChatGPT executes connected tools in the active session. Instructions do not run background work. Infrastructure edits and review-only requests do not authorize generation.

## Intake before building

Follow [mandatory intake](../pipeline/INTAKE.md). Ask and record source mode, style source and every character/narrator voice ID or name before script building or generation. Read-only inspection can identify speakers and fetch actual source/style references. Wait for complete answers; reuse answered choices for the same source/version. Resolve voice names through ElevenLabs. Supplied final recordings and silent sources require explicit selection of that mode.

For a source Starling link, retrieve all beats, branches, recovery content, consequences, endings, cast and actual visual references through MCP. For a finalized document, keep its content authoritative and use the supplied image or Starling link for style and compatible beat/visual context. Resolve conflicting mapping with the user. Resolve Script Rebuilder from the installed personal catalog.

## Execute the requested scope

Before related panels, require one approved scene master and a continuity map for camera axis, named left/right positions, seating/furniture geometry, fixed landmarks, props and lighting. Generate later panels from that authority and reject swaps, mirrors, changed sitting orientation, furniture growth and background drift before animation. Use one narration composition when it covers the beat; every additional cut requires a recorded semantic purpose. Dialogue animation receives exactly one approved clean scene plus accepted audio. Immediate same-moment continuation may instead use one inspected last frame; continuation and multi-reference modes are mutually exclusive.

All production references use original files stored through the confirmed `darshan@en2.ai` Drive connection. Record Drive IDs, fetchable URLs, hashes, EN2 upload names and a visual-match check before paid submission. Apply the fixed order: visible characters, matching environment, visible props, composition authority last.

| Stage | Owner | Exit evidence |
|---|---|---|
| Script | starling-script-rebuilder | Source ledger, stable graph, matching Word/JSON and source comparison |
| Docs | Google Drive and Google Docs skills | Confirmed darshan@en2.ai account, real native document ID/URL and matching readback |
| Audio | starling-audio-pack | Complete accepted speech, speakers, listening and measured cues |
| Visual plan | starling-prompt-pack, director, cinematography | Full inventory and audio-timed source coverage |
| Images | image-pack-generator, panel-corrector | Approved scene masters, continuity maps, single narration scenes or justified multi-shot boards, and clean dialogue scenes |
| Animation preflight | starling-animation-pack | Exact approved inputs/uploads, prompts, shot mapping and measured timing |
| Submit and collect | animation-pack, animation-monitor | All ready clips submitted once, real IDs and downloaded outputs or explicit failures |
| Review and repair | verification, director, cinematography | Complete visual and audio reviews; user-owned lip-sync; targeted replacements rechecked |
| Assembly | animation-pack and postproduction | Verified nodes, original audio, branch/word/join checks and final ZIP |

At animation preflight, require scene-matched references and a concrete description of each actual panel and its labelled action/camera/timing, following Animation Pack. Detailed prompting still requires complete output review. Apply image review immediately after generation; foundational assets pass before dependent scenes. Use [visual routing](../starling-animation-pack/references/visual-routing.md) and [spatial fidelity](../starling-cinematography/references/spatial-fidelity.md). Submit all approved clips in one ordered pass respecting capacity, review each completed output promptly while continuing collection of the remaining scope. Failed/unverified clips cannot enter final stitching. After an initial visual failure, follow Animation Pack: redesign the scene once to match the same script beat, inspect fresh images and submit one EN2 Ultra replacement. If it fails, stop for user review. Match explicit 2D, 2.5D or 3D animation wording to the inspected visuals. During assembly, narration, filler, establishing and ending clips discard rendered sound and use accepted external narration. Dialogue and conversation clips retain the verified audio embedded in their selected video so speech remains aligned to the rendered lip movement; do not replace that interval with the standalone dialogue file. Measure the selected dialogue video's usable picture/audio duration and keep it through the completed final utterance. If it runs longer than the earlier standalone-audio timing, extend the node timeline rather than cutting speech. FFmpeg handles technical checks, trimming, normalization, audio routing and export; still-image video replacements are disabled.

## Providers and authority

Use Starling MCP retrieval, ElevenLabs eleven_v3 with selected voices, native ChatGPT images, EN2 MCP Ultra (`quality=true`), the selected Google account and local FFmpeg. Discover live schemas at execution. Preserve source words/routes, approved style, aspect and endpoint. Record hashes, inspection methods, provider IDs, voice/reference mappings and source versus assembly offsets. Receipts are reviewer attestations; missing listening or complete playback leaves required checks unverified. Publishing or external player changes require an explicit request.

## Resume and completion

Reconcile existing jobs before submission. Uncertain outcomes remain held until provider history resolves them. Preserve originals, paid IDs and prior reviews. Updated skills do not rerender media. Reconcile historical manifests and current scope explicitly before project adoption. Keep branches separate, including Bad Outcomes and canonical retry controls. Review final picture, sound, words, joins and all branches. Deliver actual outputs and exact blocks. Monitoring requires a demonstrated persistent runner and real recorded ID. Honor narrower endpoints without triggering later stages.

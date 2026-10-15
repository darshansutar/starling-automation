---
name: starling-production-master
description: Coordinate Starling production from mandatory intake through script, accepted audio, two-shot storyboards, EN2 rendering, review and node assembly.
---

# Starling Production Master

Read [the workflow](../pipeline/WORKFLOW.md) and use its runtime for scopes, evidence, handoffs and job history. ChatGPT executes connected tools in the active session. Instructions do not run background work. Infrastructure edits and review-only requests do not authorize generation.

## Intake before building

Follow [mandatory intake](../pipeline/INTAKE.md). Ask and record source mode, style source and every character/narrator voice ID or name before script building or generation. Read-only inspection can identify speakers and fetch actual source/style references. Wait for complete answers; reuse answered choices for the same source/version. Resolve voice names through ElevenLabs. Supplied final recordings and silent sources require explicit selection of that mode.

For a source Starling link, retrieve all beats, branches, recovery content, consequences, endings, cast and actual visual references through MCP. For a finalized document, keep its content authoritative and use the supplied image or Starling link for style and compatible beat/visual context. Resolve conflicting mapping with the user. Resolve Script Rebuilder from the installed personal catalog.

## Execute the requested scope

| Stage | Owner | Exit evidence |
|---|---|---|
| Script | starling-script-rebuilder | Source ledger, stable graph, matching Word/JSON and source comparison |
| Docs | Google Drive and Google Docs skills | Confirmed darshan@en2.ai account, real native document ID/URL and matching readback |
| Audio | starling-audio-pack | Complete accepted speech, speakers, listening and measured cues |
| Visual plan | starling-prompt-pack, director, cinematography | Full inventory and audio-timed source coverage |
| Images | image-pack-generator, panel-corrector | Approved assets, both panels of every board and clean dialogue scenes |
| Animation preflight | starling-animation-pack | Exact approved inputs/uploads, prompts, shot mapping and measured timing |
| Submit and collect | animation-pack, animation-monitor | All ready clips submitted once, real IDs and downloaded outputs or explicit failures |
| Review and repair | verification, director, cinematography | Complete picture/sound reviews; targeted EN2 replacements rechecked |
| Assembly | animation-pack and postproduction | Verified nodes, original audio, branch/word/join checks and final ZIP |

Apply image review immediately after generation; foundational assets pass before dependent scenes. Use [visual routing](../starling-animation-pack/references/visual-routing.md) and [spatial fidelity](../starling-cinematography/references/spatial-fidelity.md). Submit all approved boards in one ordered pass respecting capacity, collect the scoped outputs, then verify. Failed/unverified clips cannot enter final stitching. Repairs use EN2 Fast, at most two replacements after the initial attempt. FFmpeg handles technical checks, trimming, normalization, original-audio stitching and export; still-image video replacements are disabled.

## Providers and authority

Use Starling MCP retrieval, ElevenLabs eleven_v3 with selected voices, native ChatGPT images, EN2 MCP Fast (`quality=false`), the selected Google account and local FFmpeg. Discover live schemas at execution. Preserve source words/routes, approved style, aspect and endpoint. Record hashes, inspection methods, provider IDs, voice/reference mappings and source versus assembly offsets. Receipts are reviewer attestations; missing listening or complete playback leaves required checks unverified. Publishing or external player changes require an explicit request.

## Resume and completion

Reconcile existing jobs before submission. Uncertain outcomes remain held until provider history resolves them. Preserve originals, paid IDs and prior reviews. Updated skills do not rerender media. Reconcile historical manifests and current scope explicitly before project adoption. Keep branches separate, including Bad Outcomes and canonical retry controls. Review final picture, sound, words, joins and all branches. Deliver actual outputs and exact blocks. Monitoring requires a demonstrated persistent runner and real recorded ID. Honor narrower endpoints without triggering later stages.

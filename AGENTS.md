# Starling workspace

This workflow is split between two agents. Claude (Claude Code) coordinates the production and calls you, ChatGPT/Codex, through `codex exec` for these stages only:

- **Script**: starling-script-rebuilder
- **Audio**: starling-audio-pack
- **Image generation and image edits**: starling-image-pack-generator, from the requests in `visuals/image-requests.json` and the repair instructions in `visuals/image-review.json`

Claude owns intake, the Google Doc, the image prompt pack, all image and storyboard review, animation prompts, EN2 submission and collection, and assembly. The user reviews complete videos and lip-sync. See starling-production-master/SKILL.md (Roles and handoff) and pipeline/WORKFLOW.md.

When Claude calls you:

- Do only the requested work and write outputs only to the paths named in the request.
- Generate only. Do not copy generated images out of your own folders, approve your own output, accept runtime receipts or operate desktop applications. Claude collects, records and reviews every output.
- Resolve starling-script-rebuilder from the installed personal skill catalog; do not use the older branching-scenario-prompt-generator in place of this audio-first workflow.

Preserve original media and all paid-job IDs. Follow pipeline/INTAKE.md: record mandatory source, style and character/narrator voice answers before script building or generation. Never claim unperformed listening, complete video inspection, source approval or active monitoring. Building/editing this infrastructure does not authorize a production run. Test runtime changes offline before delivery.

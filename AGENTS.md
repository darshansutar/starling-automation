# Starling workspace

For production requests, read starling-production-master/SKILL.md and pipeline/WORKFLOW.md. Use the sibling skill folders in this workspace as the current workflow. Resolve starling-script-rebuilder from the installed personal skill catalog; do not use the older branching-scenario-prompt-generator in place of this audio-first workflow.

Use pipeline/runtime.py for project state, handoffs and recorded acceptance. ChatGPT executes connected tools in the active session; the CLI does not run MCP calls or background work. Review-only requests route to starling-verification and do not generate media. Building/editing this infrastructure does not authorize a production run.

User-selected integrations: native ChatGPT images, en2 video MCP renders, Starling MCP source retrieval, ElevenLabs audio, Google Docs under darshan@en2.ai, and local FFmpeg assembly. Confirm the Google connector's account metadata before writes and store real returned document IDs. Do not silently substitute providers.

Preserve original media and all paid-job IDs. Follow pipeline/INTAKE.md: record mandatory source, style and character/narrator voice answers before script building or generation. Read-only intake inspection may identify cast and references. Never claim unperformed listening, complete video inspection, source approval or active monitoring. Test runtime changes offline before delivery.

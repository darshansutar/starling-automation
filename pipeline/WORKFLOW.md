# Starling production workflow

Current contract: 16 October 2026. Read mandatory [INTAKE.md](INTAKE.md), the production Master and the owning stage skills. This runtime preserves state and issues handoffs; ChatGPT executes MCP tools in the active session. No detached runner or automatic perceptual reviewer is installed.

## Start and resume

Use a separate project for a new source. For existing projects read status/next without reinitializing. Before building or generation ask source mode, style source and speaker voice IDs/names; read-only intake inspection can identify cast and download references. Record actual answers and inspected artifacts in intake.json. Existing project answers may be reused when source/version and choices match; never fabricate a retrospective confirmation.

```powershell
python pipeline/runtime.py --project projects/PROJECT init --title "Project title"
python pipeline/runtime.py --project projects/PROJECT status
python pipeline/runtime.py --project projects/PROJECT intake intake.json
python pipeline/runtime.py --project projects/PROJECT next
```

New projects default to all_ready_once and current reference-mode routing. Existing projects retain their history; recording intake adopts the current policy for future work. It does not migrate manifests or resubmit jobs. Reconcile existing source/image/audio/prompt receipts and job versions before reuse. Missing/changed intake blocks new acceptance/submission.

## Execution and acceptance

Script -> audio -> prompts -> images -> animation_prompts -> renders -> assembly. Docs depends on script and is also required for final runtime assembly acceptance. Resolve Script Rebuilder from the installed personal catalog. Starling link mode retrieves complete content and actual style assets. Finalized-document mode preserves its text/routes and uses selected reference images or Starling style/beat context without replacing its story.

Declare expected scope with scope STAGE IDS. Save all real underlying artifacts and accept a JSON receipt with stage, reviewer, exact inventory and required checks. Every artifact has project-relative path and SHA-256; every check has verdict, concrete evidence and artifact_ids. Status/resume rechecks hashes. not_applicable is restricted to explicitly silent audio or absent dialogue checks. Receipts attest human/assistant review; code does not watch/listen. Source changes invalidate affected dependencies while preserving media/job history.

Confirm Google account metadata is darshan@en2.ai before native Docs writes. Save actual document ID/URL and native readback. Re-read remote Docs on resume: local hashes do not detect remote changes. Use ElevenLabs eleven_v3 selected voices, native ChatGPT images, EN2 reference-to-video Fast quality=false and local FFmpeg editing. Discover live schemas and limits; do not substitute providers.

## Visual and render handoff

Follow [visual routing](../starling-animation-pack/references/visual-routing.md): each 1x2 board contains two related shots with one measured hard cut. Clean dialogue scenes use approved speech. Narration stays outside generation. Actual panels, spatial relationships, audio cues and uploaded bytes must pass preflight.

Declare complete render scope. Animation receipt render_plans match it exactly: payload, content_kind, visual_format, shot_count/cut_times for boards and measured reference_seconds for dialogue. Keep these local metadata fields outside API payloads. The runtime validates structure; actual image geometry and full prompt meaning require review.

Animation prompts use the [five-section template](../starling-animation-pack/references/animation-template.md). Save a per-shot visible inventory and ordered reference map, and record shot_inventory_match with inspected evidence. Older animation receipts without this review or with the previous heading format become stale; reconcile and reaccept the prompt stage before new submissions. Preserve historical prompts, media and paid-job IDs. This change does not automatically regenerate or resubmit any clip.

prepare-render CLIP PAYLOAD --kind narration returns a saved intent and exact tool arguments. The host submits once, then records actual provider ID using job INTENT queued --provider-id REAL_ID --evidence RESPONSE. Submit all ready clips in canonical order respecting provider limits. Review is not a hold between initial submission groups. Unknown outcomes use submission_unknown and are reconciled, not blindly retried. Repairs retain at most two replacements after the initial attempt.

Collect all known outputs or explicit pending/failed records, then review complete picture/sound and repair defects through EN2. Full review is required for verified jobs; missing capability remains unverified. Read [POSTPRODUCTION.md](POSTPRODUCTION.md) for selected outputs, exact current manifests, stitching and final ZIP. FFmpeg still-image animation fallbacks are disabled.

After the complete initial render pass, the animation monitor can run as a ten-minute scheduled follow-up in the same chat when scheduling and connector access are demonstrated. It uses studio_queue for shared queue context and video_status for exact project IDs; `postproduction.py monitor-report` gives project counts and review scorecards. Record a real scheduled task ID only after a successful first run. Scheduling does not itself approve output or authorize paid replacements.

Run offline checks with `python -m unittest discover -s pipeline -p test_*.py -v`. Test fixtures do not approve production media. Archived projects, provider-guide snapshots and historical media remain preserved; current skill contracts govern new work.

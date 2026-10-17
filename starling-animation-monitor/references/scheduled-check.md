# Ten-minute EN2 animation check

Use this in the existing production chat after the full approved initial render scope has been submitted once and every submitted clip has a real EN2 provider ID in `pipeline/runtime.py`. Keep one scheduled task per project. The task returns to the same chat every ten minutes; its alert is the scheduled run result. Do not send email or Slack unless separately instructed.

## First-run proof and activation

1. Run the check once manually. Confirm the exact project path, render scope, current manifest mapping, and all paid provider IDs. Hold uncertain submissions for reconciliation.
2. Call `mcp__en2_video__studio_queue` and `mcp__en2_video__video_status` for every recorded project ID. Confirm the scheduled environment can use these connected tools. If project-local files are needed, use a desktop local-project task and verify read/write access. Web tasks cannot write this workspace.
3. Create the recurring task in this chat at a ten-minute interval. Record the returned real task ID, schedule destination and successful first-run evidence in the project's `postproduction/automation.json`; only then change `runner_status` to `active`. Never record a guessed ID.
4. Use single-project locking or a task that cannot overlap its own prior run. Keep the project and task identity in every alert. If the first run cannot access EN2, local files, or both, leave `runner_status` inactive and report the exact missing capability.

## Durable task prompt

> Every 10 minutes, check EN2 animation progress for PROJECT_PATH using $starling-animation-monitor. First read the current render scope and latest recorded provider IDs from pipeline/runtime.py. Do not submit or regenerate videos. Call en2 studio_queue for whole-studio context and video_status for each project ID. Save the actual responses as immutable project snapshots, preserving full paid IDs. Feed the individual status results to pipeline/postproduction.py ingest, fetch each newly completed video atomically using the returned video URL, and attach it to its exact clip ID. Retry failed downloads without regenerating. Run pipeline/postproduction.py monitor-report with the saved queue snapshot. Report project counts for queued, rendering, generated, downloaded, awaiting review, verified and needs_fix, plus any failures, new outputs, queue position, progress and the next due time. Keep studio-wide counts separately labelled. For each attached output, report its scorecard, evidence coverage and actual review verdict. Route new outputs to full picture/sound verification; do not infer acceptance from decode, metadata, still frames, provider completion or a numeric score. Identify exact failed checks and repair owner. If a job is missing from a provider response, leave it unknown. Do not send messages through other services or make paid render calls. Continue until every scoped clip has a verified or needs_fix decision, then stop the schedule and report the final counts. If the task cannot access EN2 or local project state, report the failure and do not claim monitoring is active.

The host owns MCP calls and downloads. `pipeline/runtime.py` and `pipeline/postproduction.py` only manage local state, handoffs and reports. The queue is shared across the studio, so project counts must come from recorded provider IDs, never from folder names alone.

## Local commands for an active run

```powershell
python pipeline/runtime.py --project projects/PROJECT status
python pipeline/postproduction.py --project projects/PROJECT ingest postproduction/snapshots/STATUS_FILE.json
python pipeline/postproduction.py --project projects/PROJECT monitor-report --queue-snapshot postproduction/snapshots/QUEUE_FILE.json
```

Save the raw status results as a JSON list of the individual `video_status` structured results with `id`, `state`, and returned `video_url` where present. Save the raw `studio_queue` structured result separately. The monitor report is read-only. `ingest` records observed states and creates `postproduction/download-handoff.json`. Complete its download and attach handoffs before claiming outputs are downloaded. Never put a short-lived signed video URL in the alert.

## Score and decision

The monitor's scorecard reads the actual attached review record. `evidence_coverage_percent` shows how many required checks have a recorded pass/fail verdict. `quality_score_percent` remains null while any required check is unverified; when complete, it is the equal-weight percentage of passing checks. It is descriptive, not an acceptance threshold. Only a version-bound `verified` review with complete normal-speed picture/sound, approved-source fidelity, spatial checks, and dialogue sync where applicable can enter assembly. A `needs_fix` verdict names the failing check, location/time, and smallest repair owner; the production owner decides whether to regenerate within the existing repair limit.

---
name: starling-animation-monitor
description: Reconcile submitted Starling EN2 jobs, collect outputs and hand off full review and targeted repairs during an active session or demonstrated supported runner.
---

# Starling Animation Monitor

**Owner:** Claude, in the active Claude Code session. See [roles and handoff](../starling-production-master/SKILL.md#roles-and-handoff).

Apply [buffered timing and visual review](../starling-animation-pack/references/timing-and-visual-review.md) for storyboard/prompt timing, per-output visual checks, bounded repair and the user-owned manual lip-sync check.

Read [EN2 submission](../starling-animation-pack/references/en2-submission.md), [postproduction](../pipeline/POSTPRODUCTION.md), and [scheduled check](references/scheduled-check.md). This skill manages collection after all-ready submission. Infrastructure edits and status-only requests do not authorize new jobs.

Reconcile the current approved scope, exact manifest/runtime ID mappings and known paid jobs. Submit unsubmitted ready work only within existing production authorization through runtime intents. Respect provider capacity and retain one active attempt per clip. Never duplicate an uncertain paid call.

In an active collection pass, call studio_queue for shared-studio context and video_status for every known project ID. Save immutable provider/queue snapshots, ingest real states and fetch new complete outputs atomically. Deduplicate by provider ID/output hash. Missing response entries remain unknown, not failed. Download errors cause download retries. Run `monitor-report` to separate submitted, queued, rendering, generated, downloaded, awaiting review, verified and needs-fix counts. Save progress before yielding.

Add every downloaded complete output immediately to the user's review list through Verification, including dialogue, while continuing to account for pending jobs. Keep visual verdicts separate from user-owned manual lip-sync; manual sync pending alone is not a visual defect or a repair trigger. Technical checks and evidence coverage can be calculated automatically; the quality score stays null until all required checks have verdicts. A score never overrides the review status. Explicit pending/failure blocks remain visible while available outputs can be inspected. Complete picture/sound review is the user's; until the user gives a verdict the checks stay unverified. Route observed defects to image/prompt/render owners, use EN2 Ultra replacements with one script-faithful scene redesign and one replacement limit and re-review. No local still-image video fallback.

On resume reconcile existing intents and outputs first. Report submitted, pending, collected, awaiting review, needs-fix, verified and blocked counts separately. Final stitching requires accepted complete coverage and reconciled manifests.

For the requested ten-minute follow-up, run a recurring check in the same Claude Code session (`/loop 10m` with the durable prompt in [scheduled check](references/scheduled-check.md)). Start it only after the complete initial batch has recorded real IDs, and run the first check manually against EN2 and the local project. The session, computer and Claude Code must stay open; a loop ends with the session. Record the loop's real job ID in project `postproduction/automation.json` only after a successful run. Use one loop per project and stop it once all scoped clips reach a terminal review decision or the user stops monitoring. Never claim an unscheduled task, saved prompt, or long sleep is active monitoring. See [scheduled check](references/scheduled-check.md).

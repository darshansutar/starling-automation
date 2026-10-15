---
name: starling-animation-monitor
description: Reconcile submitted Starling EN2 jobs, collect outputs and hand off full review and targeted repairs during an active session or demonstrated supported runner.
---

# Starling Animation Monitor

Read [EN2 submission](../starling-animation-pack/references/en2-submission.md) and [postproduction](../pipeline/POSTPRODUCTION.md). This skill manages collection after all-ready submission; it does not create a background service. Infrastructure edits and status-only requests do not authorize new jobs.

Reconcile the current approved scope, exact manifest/runtime ID mappings and known paid jobs. Submit unsubmitted ready work only within existing production authorization through runtime intents. Respect provider capacity and retain one active attempt per clip. Never duplicate an uncertain paid call.

In an active collection pass, poll known IDs, save an immutable provider snapshot, ingest real states and fetch new complete outputs atomically. Deduplicate by provider ID/output hash. Missing response entries remain unknown, not failed. Download errors cause download retries. Save progress before yielding.

Account for the full initial submission pass, then hand every complete output to Verification, including dialogue. Explicit pending/failure blocks remain visible while available outputs can be inspected. Full picture/sound review requires demonstrated capability; absence leaves checks unverified. Route observed defects to image/prompt/render owners, use EN2 Fast replacements with the two-repair limit and re-review. No local still-image video fallback.

On resume reconcile existing intents and outputs first. Report submitted, pending, collected, awaiting review, needs-fix, verified and blocked counts separately. Final stitching requires accepted complete coverage and reconciled manifests.

Unattended collection additionally requires a supported authenticated runner with EN2 tools, workspace access, durable state, single-project locking and a real recorded runner/schedule ID. Test actual access before activation. Record full audiovisual review capability separately. A saved cadence or long sleep does not activate monitoring; never promise post-turn checks without that runner.

# Collect review and stitch

ChatGPT polls EN2 and downloads outputs during the active session. postproduction.py stores durable state and runs local FFmpeg edits; it cannot invoke MCP or wake the host. A persistent monitor requires a supported authenticated runner and separately demonstrated full audiovisual review.

## Reconcile inputs before collection

The current animation/animation-manifest.json and animation/assembly-plan.json must cover the whole production, including retained dialogue. Each clip has clip_id, explicit runtime_clip_id (or identical canonical ID), content_kind, visual_format, approved inputs/hashes and used_duration_seconds. Boards use storyboard_1x2 with two shots and one measured cut. Store source/audio/image manifest hashes. Do not automatically infer a new pairs ID from an old clip ID or split a timeline by filename.

Existing projects require a reviewed, versioned migration of these files before collecting a changed scope. Preserve prior manifests and job IDs. known_jobs rejects an unmapped scoped job. The manifest/timeline clip inventories must match. A workflow edit does not migrate production artifacts.

## Submit collect review

1. Submit all approved clips once through runtime intents in an ordered pass; save real provider IDs.
2. Poll known IDs and save an immutable snapshot. ingest filters mapped jobs and emits download-handoff.json. Record pending/failure states accurately; absent response entries are not failures.
3. Download actual returned URLs atomically and attach CLIP PATH --provider-id ID. Technical decode, dimensions and duration checks create review_pending, never visual approval.
4. Once the initial pass is accounted for, inspect complete picture/sound of available outputs with all spatial, scene, cut and speech checks. Pending/failed jobs remain blockers to completion. Record named reviewer, actual observations/time ranges and hashes. review RECORD selects only verified EN2 outputs; dialogue also requires lip-sync and original-audio alignment.
5. Repair source/prompt/render defects via the owning skill and EN2 Fast, maximum two replacements after the first attempt. Preserve failed jobs. Reinspect replacements. Local still-image/zoom animation replacements are disabled and cannot be selected, even if historical files exist.
6. advance emits remaining poll/review/repair actions and assembles ready nodes. Final delivery requires complete current-scope coverage and accepted final-node reviews.

## Stitching

assemble NODE checks source hashes, exact selected-output review hashes, contiguous visual intervals and complete audio duration. Normalize approved clips to 1280x720 at 30 fps with aspect-preserving scale/padding. Use cumulative frame boundaries, concatenate in canonical node order and strip rendered audio. Join pre-cut original audio units from their beginnings at 48 kHz stereo PCM without speed changes; encode AAC once for delivery. The implementation currently does not apply arbitrary source-in offsets or mix ambience/music; prepare truthful pre-cut units or implement a separately reviewed extension.

Decode and duration checks create a final review_pending record. Review full picture, original audio, joins and word/branch coverage before accepting. Outputs are separate canonical node videos, not a concatenation of mutually exclusive outcomes. Current landscape settings must be adapted and tested before portrait delivery.

## Runtime and final package

Verified raw EN2 reviews update corresponding runtime job verification when their preflight remains current. Final-node review stays in postproduction. Accept renders and assembly receipts in runtime with all required specialist and branch checks before packaging. package requires those runtime gates and every final node's accepted review, then writes a ZIP containing videos, canonical script/choices, assembly plan, reviews and selected-output provenance.

Commands: status, ingest SNAPSHOT, attach CLIP PATH --provider-id ID, review RECORD, assemble NODE, advance, package. Paths stay within the project. Review-only cuts produced outside these final gates remain clearly labelled review material. No legacy review-cut helper can serve as final acceptance.

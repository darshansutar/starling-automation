# Collect review and stitch

ChatGPT calls EN2 and downloads outputs during an active session or a demonstrated scheduled task. postproduction.py stores durable state and runs local FFmpeg edits; it cannot invoke MCP or wake the host. The requested follow-up cadence is ten minutes. A scheduled task must demonstrate connected EN2 and local workspace access before it is recorded as active. Full audiovisual review capability must be demonstrated separately.

## Reconcile inputs before collection

The current animation/animation-manifest.json and animation/assembly-plan.json must cover the whole production, including retained dialogue. Each clip has clip_id, explicit runtime_clip_id (or identical canonical ID), content_kind, visual_format, approved inputs/hashes and used_duration_seconds. Boards use storyboard_1x2 with two shots and one measured cut. Store source/audio/image manifest hashes. Do not automatically infer a new pairs ID from an old clip ID or split a timeline by filename.

Existing projects require a reviewed, versioned migration of these files before collecting a changed scope. Preserve prior manifests and job IDs. known_jobs rejects an unmapped scoped job. The manifest/timeline clip inventories must match. A workflow edit does not migrate production artifacts.

## Submit collect review

1. Submit all approved clips once through runtime intents in an ordered pass; save real provider IDs.
2. Poll known IDs and save an immutable snapshot. ingest filters mapped jobs and emits download-handoff.json. Record pending/failure states accurately; absent response entries are not failures.
3. Download actual returned URLs atomically and attach CLIP PATH --provider-id ID. Technical decode, dimensions and duration checks create review_pending, never visual approval.
4. Once the initial pass is accounted for, inspect complete picture/sound of available outputs with all spatial, scene, cut and speech checks. Pending/failed jobs remain blockers to completion. Record named reviewer, actual observations/time ranges and hashes. review RECORD selects only verified EN2 outputs; dialogue also requires lip-sync and original-audio alignment.
5. After an initial visual failure, follow Animation Pack for one script-faithful scene redesign and one EN2 Fast replacement. Reinspect it; a second failure stops for user review. Preserve failed jobs and the original logical clip ID. Local still-image/zoom animation replacements are disabled and cannot be selected, even if historical files exist.
6. advance emits remaining poll/review/repair actions and assembles ready nodes. Final delivery requires complete current-scope coverage and accepted final-node reviews.

For progress alerts, save `studio_queue` separately from individual `video_status` results. `ingest` consumes a JSON list of individual status results and emits exact download handoffs. `monitor-report --queue-snapshot PATH` reports project counts from recorded provider IDs, separate studio context, and scorecards for attached outputs. `evidence_coverage_percent` is not a quality verdict; `quality_score_percent` stays null while required checks are unverified. Only accepted review records authorize assembly. See [the scheduled check](../starling-animation-monitor/references/scheduled-check.md).

## Stitching

assemble NODE checks source hashes, exact selected-output review hashes, contiguous visual intervals and complete audio duration. Normalize approved clips to 1280x720 at 30 fps with aspect-preserving scale-to-fill and centred crop; review framing for cropped edge content. Use cumulative frame boundaries and concatenate in canonical node order. Narration, filler, establishing and ending intervals strip rendered sound and use pre-cut accepted narration units from their beginnings. Dialogue and conversation intervals retain the verified audio embedded in the selected video, with picture and sound kept together; do not replace lip-synced video dialogue with the standalone dialogue file. Measure usable dialogue duration from both streams, retain the complete final utterance and extend the node timeline when it exceeds the earlier standalone-audio interval. The assembler rejects missing embedded audio, mismatched stream starts/durations and any interval shorter than the complete selected media. Reconcile and save a longer timeline, shifting following clips and audio units, before retrying assembly. Mixed nodes require audio-unit boundaries to match each dialogue interval. Only sub-frame end padding is permitted for frame alignment; full spoken content is retained. Complete speech/lip-sync review remains mandatory because duration checks cannot identify missing words in a generated source. Normalize routed audio once to 48 kHz stereo PCM and encode AAC once for delivery. The implementation currently does not apply arbitrary source-in offsets or mix ambience/music; prepare truthful pre-cut units or implement a separately reviewed extension.

Decode and duration checks create a final review_pending record. Review full picture, original audio, joins and word/branch coverage before accepting. Outputs are separate canonical node videos, not a concatenation of mutually exclusive outcomes. Current landscape settings must be adapted and tested before portrait delivery.

## Runtime and final package

Verified raw EN2 reviews update corresponding runtime job verification when their preflight remains current. Final-node review stays in postproduction. Accept renders and assembly receipts in runtime with all required specialist and branch checks before packaging. package requires those runtime gates and every final node's accepted review, then writes a ZIP containing videos, canonical script/choices, assembly plan, reviews and selected-output provenance.

Commands: status, ingest SNAPSHOT, monitor-report [--queue-snapshot PATH], attach CLIP PATH --provider-id ID, review RECORD, assemble NODE, advance, package. Paths stay within the project. Review-only cuts produced outside these final gates remain clearly labelled review material. No legacy review-cut helper can serve as final acceptance.

Before stitching narration, filler, establishing or ending clips, remove the complete generated audio track, including background voices, and discard subtitle/text streams. Use only the accepted external narration for those intervals. Inspect the full picture for unwanted captions, labels and overlays. Burned-in text is part of the pixels: correct/regenerate the affected scene and re-review it before assembly; dropping a subtitle track does not erase it. Preserve source-required real-world signage. Dialogue retains its verified embedded speech and lip-sync.

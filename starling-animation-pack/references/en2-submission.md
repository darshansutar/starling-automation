# EN2 submission and collection

Discover live EN2 upload, generation, status and reference-guide tools in the active session. Use the installed connector, not undocumented endpoints or extracted browser credentials. Local Python returns handoffs and cannot execute MCP calls.

## Before submission

Check completed intake, source/audio acceptance, approved images, director/cinematography/spatial reviews and measured timing. Declare the complete clip inventory. Store exact `render_plans` in animation-prompts acceptance. Every plan uses `visual_format: storyboard_1x2` or `dialogue_scene`; board plans contain `shot_count: 2` and one `cut_times` value strictly inside duration. Record `reference_seconds` for dialogue from the actual combined audio. Board plans have no reference speech.

Before upload, compare the prompt against the saved per-shot visible inventory and record shot_inventory_match. Use only references relevant to those visible subjects; save an ordered filename/index/role/shot map and reconcile every Picture/Audio mention after upload. Upload relevant references in their planned order. For boards: character -> environment -> props -> full board. For dialogue: clean scene and approved speech, with supplementary assets only when useful. Save actual returned uploaded names, indexes, byte counts and SHA-256. Retrieve the uploaded bytes and inspect the returned image; reconcile any mismatch before paying for video.

Build reference payloads with prompt, refs, duration, output dimensions and `quality: false`; dialogue additionally has ref_audios. Use current live limits. The runtime has a conservative under-15-second combined dialogue reference guard; stricter live limits also apply. Do not add local manifest fields to the API payload. Use the five-section reference format, not image/keyframe alignment instructions.

## Submit all ready once

Call prepare-render per approved clip, save its intent, invoke the exact returned connected tool once, then record the real provider ID immediately. Submit in canonical order respecting service capacity. There is no review hold between initial groups. Input acceptance, duplicate prevention and repair limits still apply. Hold uncertain submissions and reconcile history instead of submitting again.

## Collect then review

Poll known scoped IDs during the active session, save real snapshots and download complete outputs atomically. Retain pending jobs and explicit failures; an omitted job is not failed. Retry downloads without regenerating. Once the initial scoped pass is accounted for, verify every available complete video and repair failures. Unresolved jobs block final completion but need not prevent inspection of available files. Preserve all attempts and real paid IDs.

Use an explicit runtime_clip_id per assembly clip; reconcile source hashes, timelines and retained dialogue before attaching a new production scope. Never infer ID migrations. Follow pipeline/POSTPRODUCTION.md for complete review and stitching. Background polling requires a demonstrated runner; all-ready submission alone is not monitoring.

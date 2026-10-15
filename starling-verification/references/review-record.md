# Verification report contract

Write UTF-8 JSON with schema_version "1.0", project_id (null when unknown), review_scope, created_at (ISO 8601 with timezone), items and summary. Scope lists the requested IDs/files and excluded branches where relevant. Never include credentials.

Each item contains:

- item_id, kind, node_id, branch_id, panel_id (null where inapplicable).
- artifact: path, sha256 and source_version; null for unavailable values, with a limitation explaining why.
- comparison_sources: actual script, image, audio and cue paths/IDs with hashes where available.
- inspection: methods, reviewed_time_ranges_seconds, full_picture_reviewed, full_audio_reviewed and limitations. Use null for full-audio review on a still, not a fabricated true value. Record who performed any externally supplied review and its exact artifact version.
- checks: objects with check_id, required, verdict (pass/fail/unverified/not_applicable), observation, evidence and limitation. Evidence identifies a viewed region/panel, measured result or inspected time interval and method. Unsupported conclusions cannot pass.
- findings: objects with finding_id, severity (blocking/minor), check_id, observed, expected, location, recommended_fix and owner. Location uses panel/region or start/end seconds as appropriate; never fabricated precision.
- status: verified, needs_fix or unverified, derived from required checks as specified in SKILL.md.
- blocked_reason: null or concrete missing input/capability.
- next_action and supersedes_review_id, if applicable.

Summary contains total, verified, needs_fix and unverified item counts; these must sum to total. Count panels separately only if they are declared scope items; avoid counting a board and its nested panel checks as multiple delivered boards. Preserve both board-level and per-panel evidence.

Maintain distinct check IDs for raw-render review and final assembled-audio review. Optional observations do not silently become required gates. Existing pipeline requirements remain required even when the runtime cannot perform them.

For animation scene-fidelity review, include checks for `visible_inventory_preserved`, `only_planned_motion`, `action_end_and_contact` and `background_state_preserved`, referencing the exact approved source and motion-plan version. Record actual inspected intervals/method and observed additions, disappearances, growth, transformations or unrelated events as applicable. These detail the existing fidelity checks; they are not new runtime receipt keys. Full-clip evidence is required for a full-clip pass, throughout both related shots and the cut. Endpoint samples alone leave intervening motion unverified.

A proposed repair handoff includes item_id, reviewed hash, finding IDs, target owner, approved source dependencies and recheck scope. The receiving owner decides execution within existing user authorization and repair limits. A review handoff is not a render request or authorization for spending.

## Spatial review and runtime handoff

Include all seven applicable check IDs from spatial-fidelity.md: scale_proportion, perspective_depth, separation_clearance, support_contact, orientation_construction, occlusion_order and spatial_continuity. Give each a verdict and actual evidence; not_applicable requires an explanation. Examples explain the general checks, not special-case exceptions.

For runtime/postproduction acceptance, save a version-bound JSON review with reviewer, observations, scene_fidelity, full_picture_reviewed, full_audio_reviewed, path, sha256, provider_id and spatial_checks keyed by those IDs (each with verdict and evidence). Dialogue also requires dialogue_lipsync and original_audio_sync. A node review uses node_id with audio_joins and script_coverage. Translate the aggregate report only from actual inspected findings; do not fill pass values mechanically. Keep the detailed report alongside it.

Current selected clips must be actual EN2 outputs. Historical still-image alternatives remain evidence only. Final node and runtime stage acceptance are both required before final packaging.

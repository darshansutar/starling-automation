# Workflow audit 18 October 2026

The current skills and supporting references use one shared [timing and visual review contract](../starling-animation-pack/references/timing-and-visual-review.md). Nine downstream skill entrypoints link to it. Script Rebuilder and Audio Pack retain their source and audio responsibilities; their Word exports were refreshed without adding animation responsibilities.

## Corrections

- Consolidated repeated reference-bundle and repair-exception paragraphs into links to their owning contract.
- Replaced stale used-duration cut wording with generated-duration cuts. Storyboard captions and animation prompts now share per-shot 1–2 second buffers, action/hold splits and hard-cut times.
- Changed collection instructions to review each downloaded output while accounting for remaining jobs.
- Separated visual hallucination findings from the user's manual lip-sync check. Pending manual sync does not trigger a paid visual repair or qualify dialogue for final acceptance.
- Corrected the dialogue template's attachment order and made the narration example's action and hold timings explicit.
- Clarified that a manual monitoring check cannot prove a scheduled environment works; an actual scheduled execution is required. Collection-only and authorized repair scopes remain distinct.
- Replaced the old report generator's embedded obsolete workflow narrative with a compatibility entrypoint to the current builder. Dated historical exports remain preserved locally.

## Verification

All 11 skill entrypoints, 29 active Markdown files and 91 local reference links passed structural and provenance checks. No second embedded skill frontmatter/version was found. Historical endpoint-format parsing in runtime remains intentionally available for old receipts; it does not authorize that route for new submissions.

All 44 offline tests passed. The new synthetic media test verifies that per-shot source spans remove internal buffers, retain the intended red/blue shots at the correct edit times and preserve the accepted narration source. Invalid, overlapping, out-of-range and dialogue spans are rejected.

The 19-page workflow PDF and 11 Word documents were rebuilt. Exact source-text/hash checks and page-boundary checks passed. All 45 final rendered pages were visually inspected; two nearly empty trailing pages were corrected. Microsoft Word rendered the DOCX files because the packaged renderer could not find LibreOffice. Review images are local QA intermediates.

This audit covers workflow instructions, code and documents. It does not approve any production clip, launch generation, install an unattended visual reviewer or activate monitoring. Visual truth, printed storyboard labels and manual lip-sync still require actual version-bound review evidence.

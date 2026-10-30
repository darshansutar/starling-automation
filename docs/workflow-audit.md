# Workflow audit 30 October 2026

## Mandatory narration storyboards

Every narration clip now uses a labelled 1x2 or 1x3 storyboard planned from the accepted narration audio; single full-frame narration is invalid and the runtime rejects it for new plans. Narration before dialogue ends on a panel that hands off to the clean dialogue scene (upcoming speakers in their dialogue positions, same scene master, set, lighting and camera side) for continuous lip-sync; the dialogue render plan enforces that handoff. Narration after dialogue is mainly B-roll and subject action with no handoff requirement. Narration between dialogues applies both rules at its ends. Opening and ending narration use the normal storyboard method. Dialogue keeps exactly one clean scene plus accepted audio.

Validation: 48 offline tests passed. The audit checked 11 skill entrypoints, 29 Markdown files and 103 local links, and all source hashes match the rebuilt exports. The 20-page workflow PDF and eleven Word documents were rebuilt, passed source-text and page-bound checks, and all 66 rendered pages were visually inspected. No production media was generated or accepted.

# Workflow audit 21 October 2026

## Narration and dialogue update

Dialogue TTS now uses a separately saved transliteration input: first 2-3 words in Hindi/Devanagari, remaining words in Roman/English script, with canonical wording preserved. Narration planning listens to accepted audio and covers each semantic beat using 1x2 or 1x3 boards. The shared storyboard contract owns monochrome style fidelity, white label backgrounds, whole-second printed timings, side/three-quarter action staging without back shots, and silent closed-lip characters.

The animation template links the official MiniMax H3 reference and base guides. It distinguishes external narration from explicitly requested generated voiceover, which uses the official per-line phrase and closed-lips statement. Reference prompts retain six sections. New animation instructions use the selected Ultra quality=true default; the runtime accepts explicit boolean quality so historical Fast records remain readable. Two- and three-shot plans require matching format/count and strictly increasing internal cuts.

Updated entrypoints: starling-audio-pack, starling-prompt-pack, starling-director, starling-cinematography, starling-image-pack-generator, starling-panel-corrector, starling-animation-pack, starling-animation-monitor, starling-production-master and starling-verification. Script Rebuilder's source responsibilities are unchanged; its document was refreshed with the other exports.

Validation: 45 offline tests passed, including valid 1x3 and malformed cut plans, Ultra inputs and historical compatibility. Eleven skill entrypoints passed the skill validator. The source audit checked 29 Markdown files and 103 local links. The 20-page workflow PDF and eleven Word exports passed full source-text/hash and page-bound checks; all 63 rendered pages were inspected. Microsoft Word rendered the DOCX files because the packaged renderer reported missing LibreOffice. No production media was generated or accepted by this update.

## Previous audit 18 October 2026

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

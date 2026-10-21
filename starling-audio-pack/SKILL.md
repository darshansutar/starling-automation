---
name: starling-audio-pack
description: Prepare selected ElevenLabs speech or supplied recordings with complete listening review and measured cues for Starling production.
---

# Starling Audio Pack

Check [mandatory intake](../pipeline/INTAKE.md). The user must have answered which voice ID or name each character/narrator uses, or selected supplied recordings/silent production. Resolve names with ElevenLabs, clarify multiple matches and record actual IDs. Keep every source speaker.

Read [the handoff contract](../starling-prompt-pack/references/handoff-contract.md). Inventory exact spoken lines, speakers, language, nodes and branches. Classify narration/dialogue/speech-free intervals. Voice player controls only when the canonical script explicitly speaks them. Reuse accepted recordings unchanged.

For newly generated dialogue, keep canonical text unchanged and save a separate tts_text: transliterate the first 2-3 spoken words into Hindi/Devanagari and the remaining words into Roman/English script. Transliteration changes writing, not language, meaning or word order; do not translate or add an opening phrase. Save canonical_text, tts_text and their line mapping. Listen to the complete result for the intended accent and exact spoken content; script choice alone does not guarantee accent. This rule does not alter accepted recordings or automatically apply to narrator lines.

For new speech read the installed ElevenLabs creative-studio skill and live tool schema; use eleven_v3 and selected voices. Persist actual asynchronous job IDs immediately, reconcile uncertain paid requests and download durable originals. Generate only the authorized number of takes.

Listen to each complete recording and compare words, speaker identity, pronunciation, pauses and joins with the script. Measure durations and cues. Transcription/alignment assists but cannot replace listening. Missing evidence blocks audio acceptance. Silent sources have an explicit empty speech inventory.

Save audio_manifest.json with source/version/hash, exact text and line IDs, voice/model/provider IDs, accepted file/hash/duration, source offsets, content kind, node/branch mapping and review evidence. Keep source offsets distinct from assembly positions. Dialogue excerpts and derived conversation tracks preserve original speed, turns and pauses; save source mappings and inspect every join.

Narration remains an external assembly master across picture cuts. Dialogue reference audio goes to EN2 with exact speaker/turn mapping. Storyboard rendering receives no speech audio. Replacement speech requires remeasurement and dependent revalidation. Hand off only accepted speech/cues; preserve originals and paid IDs.

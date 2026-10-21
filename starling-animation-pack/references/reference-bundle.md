# Scene-matched animation references

Inspect the actual storyboard pictures or clean dialogue scene before choosing references. Attach only references needed by the visible inventory. The storyboard controls staging and action; appearance references do not add occupants or objects.

| Visible content | Reference selection |
|---|---|
| One character | Only that character's approved sheet, matching environment, relevant visible prop sheets and storyboard or clean scene |
| Multiple characters | Only the sheets for those visible characters, matching environment, relevant visible prop sheets and storyboard or clean scene |
| Environment only | Matching environment and storyboard; omit character and prop sheets. Describe the visible landscape, fixed structures, lighting and supported environmental movement. |
| Person-free prop/document insert | Matching environment or surface, relevant prop sheets and storyboard; omit character sheets. An insert of a book or file is not an environment-only shot. |

Preserve this order among the applicable groups: character sheets, environment, prop sheets, storyboard or clean dialogue scene. Dialogue also retains the accepted reference audio and speaker mapping, including a source-required off-screen voice without adding its character sheet to the image bundle. Omit absent groups rather than supplying unrelated context sheets.

References apply to the entire render request. For a two- or three-shot clip, take the union of the visible identities and relevant props across all its pictures and explicitly record visibility per shot. A character visible only in Shot 1 supplies a reference for Shot 1, not permission to appear in an empty Shot 2. Separate requests use their own inventories; do not inherit the whole scene's cast. Keep the approved shot timing unless a source-supported replan is needed.

For first submissions, use approved sheets for the selected visible characters and props. A sheet's multiple views describe one identity/object. Reuse suitable assets; generate and inspect a missing reference only when the visible scene needs it. The repair exception below allows individual references after an incorrect animation output.

Save ordered roles, filenames, hashes, upload names and per-shot visibility. After any attachment change, rebuild all Picture/Subject indexes and remove definitions and prose for omitted subjects. Check every prompted identity/object against the actual pictures. If the selected bundle exceeds the provider limit, consolidate compatible references or split at a source-supported cue while preserving coverage and timing. Preserve already-submitted payloads and paid IDs; a revised reference plan does not alter a queued job or authorize a duplicate.

## People standing together

Stage adjacent people with a clear visible gap between their shoulders, torsos, arms, hips and feet. Give each a separate standing position and enough room for the planned gesture. This applies to every pairing, including a woman and a man. Preserve believable conversational distance, eyelines and shared perspective. Intentional contact must be supported by the script and explicitly staged. Check both storyboard pictures and the entire animation for merged silhouettes, body intersections or loss of the planned gap.

## Repair-only individual references

When inspection of a generated animation identifies an incorrect output, record needs_fix, the visible defect and the original job ID. For that failed clip, generate and inspect scene-specific single-character references, individual prop references and a matching environment from the approved sheets, style and script. Keep identity, costume, object state, scale, lighting and layout consistent. Use only subjects relevant to the inspected storyboard; a new reference does not add a subject to the scene.

Select the repair bundle by the same visible-inventory rules above, using individual references where applicable, and keep the applicable groups in order. Dialogue retains its clean scene as the final visual and its accepted speech and turn mapping. Correct the storyboard when it contains the defect, then analyze it again and rewrite the affirmative animation prompt against the actual replacement images. Rebuild Picture indexes, record reference hashes and preserve originals and paid-job IDs.

This exception is only for a reviewed failed output, not routine first generation. It uses the existing single repair attempt; it does not add another automatic retry cycle. Review the complete repaired picture and sound. If it remains incorrect, retain needs_fix and report it rather than continuing automatic regeneration. Review-only skills identify the repair and route it to production; they do not generate media.

# Current visual routing

| Content | Approved visual | EN2 reference inputs | Speech |
|---|---|---|---|
| Narration, filler, establishing and ending coverage | 1x2 board with two related shots | Relevant assets then complete board in refs | Original narration added in assembly; omit ref_audios |
| Dialogue | Clean full-frame scene of actual participants | Scene in refs, approved dialogue in ref_audios; relevant extra assets only as needed | Explicit speaker/turn mapping and lip-sync review |

Read [the storyboard contract](narration-pairs.md). Each board is one column, two stacked panels. Top/bottom become Shot 1/Shot 2 with exactly one measured hard cut. This applies to narrated and speech-free bookends alike. A dialogue source remains one clean scene; mixed nodes split into ordered narration/dialogue blocks while preserving canonical node/branch IDs.

Use reference-to-video and Fast quality=false. Discover live limits and guide syntax before submission. Dimensions, durations, upload names and reference audio budgets are actual submission metadata, not invented API fields. A silent/narrated board has no dummy audio reference. Image sheets never appear as output layouts.

Preserve historical media and job IDs as evidence. New production uses this contract; adopting it for an existing project requires explicit reconciliation of manifests, clip mappings, durations and dialogue coverage. Updating instructions alone neither changes an existing job nor approves its output.

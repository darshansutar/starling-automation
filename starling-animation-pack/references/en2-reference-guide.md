# Reference mode prompt syntax

Use the live EN2 reference guide at execution. This local summary keeps the required structure discoverable; it does not establish current provider limits. Provider reference: https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md

Use six sections, in order: subject_definitions, summary, retention_analysis, detailed_description, overall_soundscape, non_diegetic_music. Section headings end with a colon. Write instructions in English while preserving source dialogue language.

Use <Subject N> for defined identities/objects, <Picture N> for uploaded images and <Audio N> for accepted dialogue references. Keep indexes and roles consistent. Reference a character sheet for identity, an environment for set geometry and the complete storyboard for exact shot compositions. Map the storyboard TOP to [Shot 1] and BOTTOM to [Shot 2]. In detailed_description give the exact hard-cut cue, permitted movement and fixed camera for each shot. Dialogue instead uses its clean scene and explicit speaker/turn/audio mapping with the live dialogue syntax.

retention_analysis states what each actual reference preserves and that the sheet presentation is absent from output. overall_soundscape contains only appropriate planned sound; non_diegetic_music is N/A unless requested. Reference footage/images are guidance, not evidence that a generated result passed review.

Apply the workflow's [scene preservation](scene-preservation.md), [routing](visual-routing.md) and [submission](en2-submission.md). Provider examples do not authorize extra movement, cast, music or a different local production route.

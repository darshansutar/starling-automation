# Starling workspace (Claude)

For production requests, read starling-production-master/SKILL.md (especially Roles and handoff) and pipeline/WORKFLOW.md. Use the sibling skill folders in this workspace as the current workflow. `python pipeline/runtime.py --project PROJECT next` returns the next stage with its owner and reviewer; never take over a stage owned by ChatGPT or the user.

Claude's work:

- Intake: ask the user and record the source, style and voice answers.
- Google Doc under darshan@en2.ai: confirm the connector account before any write and store the real document ID.
- Image prompt pack: Director, Cinematography and Prompt Pack, ending in `visuals/image-requests.json`.
- Image, storyboard and prompt review: Panel Corrector and Verification, writing `visuals/image-review.json`.
- Animation prompts, EN2 uploads, Ultra (`quality=true`) submission, collection and monitoring.
- FFmpeg assembly.

ChatGPT's work (script, audio, image generation and image edits) runs through Codex:

```powershell
codex exec --skip-git-repo-check --sandbox workspace-write -C <project directory> "<exact request>"
```

Tell Codex in every request that it generates only: no copying files out of its folders, no approving its own output, no desktop applications. Collect generated images from `~/.codex/generated_images/<session>/` into the project, then record each one's hash and dimensions in `visuals/image_manifest.json` before reviewing it.

Claude cannot watch video or listen to audio. Complete video, sound and lip-sync review belongs to the user: prepare the review list and record only the verdicts the user gives. Never claim unperformed listening, complete video inspection, source approval or active monitoring.

Preserve original media and all paid-job IDs. Paid EN2 submission needs the user's approval. Building or editing this infrastructure does not authorize a production run. Run `python -m unittest discover -s pipeline -p "test_*.py"` after any runtime change.

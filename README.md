# Starling automation

Source-faithful branching video workflow: script, accepted audio, labelled black-and-white two-shot narration storyboards, EN2 animation, review and final assembly.

## Contents

- `starling-*/`: 11 skills, reference instructions and the Script Rebuilder helper.
- `pipeline/`: project state, intake, handoffs, acceptance, assembly and offline tests.
- `docs/Starling_Workflow_Explained.pdf`: illustrated 18-page workflow explanation.
- `docs/skill-documents/`: full text of each skill in 11 separate Word documents.

## Setup

1. Clone this repository and open its root folder in Codex.
2. Use Python 3.10 or newer. The runtime and Script Rebuilder use the Python standard library. Install FFmpeg and ffprobe on PATH for assembly and media tests.
3. Install the bundled `starling-script-rebuilder` folder into your personal Codex skills directory (normally `~/.codex/skills/`). Review any existing installation before replacing it. Keep the other skill folders beside `pipeline/` so relative reference links work.
4. Connect Starling MCP, EN2 video MCP, ElevenLabs, and Google Drive/Docs in the active assistant session. Native ChatGPT image generation is also required. Connections and credentials are not distributed in this repository.
5. Read `AGENTS.md`, `starling-production-master/SKILL.md` and `pipeline/WORKFLOW.md`. Record source, visual style and voice choices before building or generating.

The configured Google account is `darshan@en2.ai`; confirm live connector account metadata before any write. That account requirement is intentional and is also enforced by the runtime. The included PDF and Word documents are dated snapshots; their original Windows paths document the source machine and are not installation requirements.

## Start a project

Run from the repository root:

```powershell
python pipeline/runtime.py --project projects/project-2 init --title "Project 2"
python pipeline/runtime.py --project projects/project-2 status
python pipeline/runtime.py --project projects/project-2 next
```

Keep each production under `projects/`. Its media, local account snapshots and databases are excluded from Git. Follow `pipeline/INTAKE.md` to record actual answers before dependent work.

## Offline validation

```powershell
python -m unittest discover -s pipeline -p "test_*.py" -v
```

FFmpeg and ffprobe are required for the synthetic media tests. Offline tests do not certify production picture, sound or lip-sync quality.

## Execution limits

The CLI records state and prepares handoffs. It does not run MCP calls or a background service. Connected operations happen in the active assistant session. Full listening and video review must be performed before acceptance. Failed video is repaired through EN2; FFmpeg is used for technical checks and accepted-media assembly, not still-image replacement animation.

Original production media, paid-job IDs, credentials, historical exports and local connector-link IDs are not included in this repository. No production run is triggered by cloning or pushing it.

Narration requires character sheets, matching environment, prop sheets and the labelled storyboard in that order. Generate missing sheets first; preserve clear space between adjacent people. Dialogue keeps its clean scene and accepted speech. Before narration or establishing assembly, discard generated sound and subtitle streams; correct unwanted burned-in text before approval. Dialogue retains complete embedded speech.

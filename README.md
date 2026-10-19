# Starling automation

Source-faithful branching video workflow: script, accepted audio, labelled black-and-white two-shot narration storyboards, EN2 animation, review and final assembly.

## Contents

- `starling-*/`: 11 skills, reference instructions and the Script Rebuilder helper.
- `pipeline/`: project state, intake, handoffs, acceptance, assembly and offline tests.
- `docs/Starling_Workflow_Explained.pdf`: illustrated 19-page workflow explanation.
- `docs/skill-documents/`: full text of each skill in 11 separate Word documents, with the shared timing and visual-review contract included where relevant.
- `tools/reports/`: current document builders, verification and instruction audit.
- `docs/validation.json`: offline checks and document validation results.

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

Run `python tools/reports/audit_workflow.py` to check active skill links and exported source hashes. See [the workflow audit](docs/workflow-audit.md) for the cleanup findings and verification scope.

## Rebuild the documents

The report tools use Windows Arial/Consolas fonts, Python ReportLab, PyMuPDF and Pillow, plus Microsoft Word for DOCX export and rendering. Run `build_explanation_report.py`, then `create_skill_docs.ps1`, then `verify_explanation_report.py` from `tools/reports/`. Outputs go to `deliveries/workflow-explanation-2026-10-18`; intermediate page images go to `tmp/pdfs/workflow-explanation`. Inspect every rendered page before replacing the files in `docs/`. The legacy flow-report commands route to these current builders.

## Execution limits

The CLI records state and prepares handoffs. It does not run MCP calls or a background service. Connected operations happen in the active assistant session. Full listening and video review must be performed before acceptance. Failed video is repaired through EN2; FFmpeg is used for technical checks and accepted-media assembly, not still-image replacement animation.

Original production media, paid-job IDs, credentials, historical exports and local connector-link IDs are not included in this repository. No production run is triggered by cloning or pushing it.

## Timing and visual review

Narration and establishing shots include 1–2 seconds of extra footage per shot. Storyboard labels and animation prompts use identical generated ranges and exact hard cuts; the edit keeps separate required durations. Ordered `source_spans` remove each shot’s buffer without stretching original narration. Dialogue keeps its complete embedded speech.

Review every completed clip against its approved panels for extra or missing characters/objects, distorted anatomy, scene changes, unplanned motion and transition defects. Lip-sync is the user’s separate manual check. One authorized visual replacement is allowed per logical clip, followed by complete reinspection; a second failure stops for review. See [the shared contract](starling-animation-pack/references/timing-and-visual-review.md).

Reference selection follows visible content: one character uses only its sheet; environment-only clips use environment and storyboard; document inserts retain relevant prop references. Order only the applicable groups, ending with the storyboard or clean scene, and map visibility per shot. Animation prompts describe each actual panel in detail and follow its printed action, camera and timing. Failed-output repair uses the documented individual-reference exception. Current instructions replace conflicting older guidance. Dated historical exports and media remain archives, not active rules.

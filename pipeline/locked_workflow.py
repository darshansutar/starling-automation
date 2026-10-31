"""Immutable workflow contract and deterministic orchestration helpers.

The model may explain or recommend work, but this module owns stage order,
provider policy, approvals, and side-effect boundaries.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from .runtime import PipelineError, Project
except ImportError:
    from runtime import PipelineError, Project


LOCK_PATH = Path(__file__).with_name("workflow_lock.json")
# Update only as part of an explicitly reviewed workflow-contract change.
EXPECTED_LOCK_SHA256 = "7b95316c3865d3ebe44e7e6470b6edbaf4b4ba996b4a273f6b09a6e677810b0c"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_workflow_lock() -> dict[str, Any]:
    actual = file_sha256(LOCK_PATH)
    if actual != EXPECTED_LOCK_SHA256:
        raise PipelineError(
            "Workflow lock changed without updating the reviewed contract hash; "
            f"expected {EXPECTED_LOCK_SHA256}, got {actual}"
        )
    data = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    required = {
        "schema_version", "workflow_id", "workflow_version", "stage_order",
        "providers", "render_defaults", "hard_rules", "approval_boundaries",
        "agent_roles",
    }
    if set(data) < required:
        raise PipelineError("Workflow lock is missing required sections")
    if data["render_defaults"].get("quality") is not True:
        raise PipelineError("Locked workflow requires EN2 Ultra quality=true")
    if data["render_defaults"].get("batch_size") != 10:
        raise PipelineError("Locked workflow requires review batches of 10")
    return data


def validate_locked_prompt(prompt: str, content_kind: str) -> None:
    """Enforce current production invariants without invalidating legacy receipts."""
    normalized = prompt.lower()
    if content_kind == "dialogue":
        required = ("static tripod", "zero camera movement", "no automatic reframing")
        if not all(term in normalized for term in required):
            raise PipelineError(
                "Dialogue prompt must hard-lock a static tripod, zero camera movement "
                "and no automatic reframing"
            )
    elif content_kind == "narration":
        required = (
            "storyboard is the per-shot composition authority",
            "identity and material only",
            "final storyboard panel",
        )
        if not all(term in normalized for term in required):
            raise PipelineError(
                "Narration prompt must lock per-shot storyboard composition, "
                "identity-only sheets and the final panel"
            )


@dataclass(frozen=True)
class LockedAction:
    stage: str
    instruction: str
    needs_human_approval: bool
    expected_ids: tuple[str, ...] = ()


class LockedProductionController:
    """Thin deterministic boundary between an agent and the production runtime."""

    def __init__(self, project_path: str | Path):
        self.lock = load_workflow_lock()
        self.project = Project(project_path)

    def close(self) -> None:
        self.project.close()

    def status(self) -> dict[str, Any]:
        return {
            "workflow": {
                "id": self.lock["workflow_id"],
                "version": self.lock["workflow_version"],
                "sha256": EXPECTED_LOCK_SHA256,
            },
            "intake": self.project.intake_status(),
            "stages": self.project.status(),
            "handoff": self.project.handoff(),
        }

    def next_action(self) -> LockedAction:
        handoff = self.project.handoff()
        stage = handoff.get("stage")
        if stage is None:
            return LockedAction("complete", "No stage remains.", False)
        approvals = {
            "intake": "source_style_voice_intake",
            "prompts": "prompt_pack",
            "images": "generated_images",
            "renders": "paid_animation_submission",
        }
        return LockedAction(
            stage=stage,
            instruction=handoff["instruction"],
            needs_human_approval=stage in approvals,
            expected_ids=tuple(handoff.get("expected_ids") or ()),
        )

    def prepare_render(
        self,
        clip: str,
        payload: dict[str, Any],
        content_kind: str,
        reference_seconds: float | None = None,
    ) -> dict[str, Any]:
        defaults = self.lock["render_defaults"]
        if payload.get("quality") is not defaults["quality"]:
            raise PipelineError("Render differs from locked Ultra quality=true")
        if payload.get("width") != defaults["width"] or payload.get("height") != defaults["height"]:
            raise PipelineError("Render dimensions differ from the locked 1344x768 contract")
        validate_locked_prompt(payload.get("prompt", ""), content_kind)
        # Project.prepare_render writes a durable intent before any provider call.
        return self.project.prepare_render(
            clip, payload, content_kind, reference_seconds=reference_seconds
        )

    def record_submission(
        self,
        intent: str,
        provider_id: str | None,
        evidence: str,
        outcome: str,
    ) -> None:
        allowed = {"queued", "submission_unknown", "submission_rejected", "cancelled_before_call"}
        if outcome not in allowed:
            raise PipelineError("Unsupported submission outcome")
        self.project.job_update(intent, outcome, evidence, provider_id)


def agent_sdk_available() -> bool:
    try:
        import agents  # noqa: F401
    except ImportError:
        return False
    return True


def build_manager_agent(project_path: str | Path):
    """Create the optional OpenAI Agents SDK manager.

    Import is lazy so the deterministic runtime and its tests stay dependency-free.
    The paid render tool always interrupts for human approval. It returns a saved
    intent and exact provider arguments; the host performs the connected MCP call.
    """
    try:
        from agents import Agent, function_tool
    except ImportError as exc:
        raise RuntimeError(
            "Install the optional OpenAI Agents SDK dependency from "
            "requirements-agents.txt before creating the manager agent."
        ) from exc

    controller = LockedProductionController(project_path)

    @function_tool
    def workflow_status() -> str:
        """Return immutable workflow identity, stage state, and next handoff."""
        return json.dumps(controller.status(), ensure_ascii=False)

    @function_tool
    def next_locked_action() -> str:
        """Return the next code-determined action; never choose a stage freely."""
        return json.dumps(controller.next_action().__dict__, ensure_ascii=False)

    @function_tool(needs_approval=True)
    def prepare_paid_render(
        clip: str,
        payload_json: str,
        content_kind: str,
        reference_seconds: float | None = None,
    ) -> str:
        """Save one approved EN2 intent before the host performs the paid MCP call."""
        payload = json.loads(payload_json)
        task = controller.prepare_render(clip, payload, content_kind, reference_seconds)
        return json.dumps(task, ensure_ascii=False)

    instructions = (
        "You are the Starling production manager. The code-owned workflow lock and "
        "SQLite runtime are authoritative. Never invent, skip, reorder, accept, retry, "
        "or publish work. Read workflow_status, call next_locked_action, and use only "
        "the returned stage. Paid rendering must use prepare_paid_render and wait for "
        "human approval. Provider completion is not acceptance."
    )
    return Agent(
        name="Locked Starling Production Manager",
        instructions=instructions,
        tools=[workflow_status, next_locked_action, prepare_paid_render],
    )


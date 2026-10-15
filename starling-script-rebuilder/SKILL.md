---
name: starling-script-rebuilder
description: Build a source-faithful branching video script from a Starling roleplay, or adapt a finalized script document into a matching review document and developer graph.
---

# Starling Script Rebuilder

Own canonical script content, source coverage and the matching Word/JSON artifacts. Follow the user-selected source mode. Read [intake](references/intake.md) before starting; obtain the mandatory source, style and voice answers before building. Read-only source inspection to identify speakers and references is intake work. Media generation belongs to downstream specialists.

## 1 Establish the source

**Starling roleplay:** discover the connected Starling MCP tools, resolve the supplied link/content ID, and retrieve all available beats, choices, branch targets, recovery lanes, consequences, endings, cast and visual assets. Save the actual responses, IDs and downloaded visual references. Inspect style from the real images. Complete the source inventory before writing; unresolved source access or missing branch targets remain explicit blockers.

**Finalized document:** extract paragraphs and tables in reading order with stable source locators. Preserve wording, speakers, scenes, choices and routes. Use the user's style image or supplied Starling reference only for visual style and relevant beat context. Resolve conflicting beat mapping with the user. An ambiguous route is a question, not a license to rewrite the script.

## 2 Map the complete story

Read [the data contract and worked example](references/data-contract.md). A Segment is a source-supported playable scene block; it may end in a decision or continue into another scene. Map all source beats, including non-decision beats, in source order. Keep the entire cast and every source choice and consequence. Derive duration from the content and later accepted audio; requested duration changes require a content decision.

Create a source inventory and coverage ledger mapping each source element to its output node or element. Recovery scenes and recovery questions get explicit nodes and routes. Each choice follows its own consequence; if that consequence is missing, ask for clarification rather than borrowing another choice's outcome. Preserve facts in full; allocate additional dialogue or narration where authorized instead of forcing an arbitrary line count.

For a converted Bad Outcome with a same-Segment retry, use one button transition labelled `Try again` targeting its owning Segment. This button is the only outgoing transition from that outcome. Preserve explicitly supplied recovery routes and finalized-document routing; ask before changing them. Keep endings distinct when the source has distinct endings.

Document any user-authorized content change with the source locator and actual authorization. Without that instruction, keep the source text and graph. Describe the format directly; requests such as “same format” require an identifiable reference, not presumed conversation memory.

## 3 Build from one canonical file

Populate the contract once as `canonical-script.json`, with `input_mode`, full cast, nodes, explicit transitions, source inventory, coverage and change records. The finalized-document adapter maps heading/paragraph/table locators to this graph without regenerating prose. Keep the original document alongside it. Validate extraction against the original document, including tables and UI-only text.

Run `python scripts/build_script.py canonical-script.json --out OUTPUT_DIRECTORY`. The helper validates graph targets, coverage, speakers and transition semantics, then writes matching developer JSON and a Word review document. Formatting constants live in the helper. Its validations supplement source comparison; they cannot prove the inventory itself is complete.

The review document contains title and source mode, full cast, flow summary, each scene's Visual and spoken lines, decisions/buttons, coverage ledger and authorized changes. Timing is labelled provisional until audio is measured. Keep player controls distinct from speech.

## 4 Verify and hand off

Compare every extracted source element with its mapped output, check all reachable branches and same-Segment retries, and verify Word/JSON wording and routes agree. Use the Documents skill to render the Word file and inspect every page once, fixing layout defects before delivery. Missing rendering capability remains an explicit delivery limitation.

Deliver the review DOCX, developer JSON, canonical data, coverage ledger/source snapshots and completed intake reference. Preserve original source and stable IDs. Hand off approved style artifacts and speaker selections to their owning downstream skills; this skill does not generate media or publish a player.

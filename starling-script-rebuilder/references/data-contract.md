# Canonical script data contract

Use schema_version `3.0`. This is a source-preserving graph, not a player-specific import format. Any external player adapter must be documented and tested separately before publication.

Top-level fields: `schema_version`, `title`, `input_mode` (`starling_link` or `finalized_document`), `source` (original URI/path and snapshot hash), `characters` (all cast IDs/names/roles), `start_node`, `nodes`, `source_inventory`, `coverage`, `changes`.

Every node has `id`, `kind` (`segment`, `recovery`, `bad_outcome`, `ending`, `decision`), `title`, `visual`, `lines` (unique `id`, known `speaker`, exact `text`), `source_refs` and exactly one `transition`:

- `{"type":"auto","target":"node_id"}` for source-supported automatic progression.
- `{"type":"choice","question":"...","options":[{"id":"...","text":"...","target":"node_id"}, ...]}` for all source options. At least two; count follows the source.
- `{"type":"button","label":"Try again","target":"segment_id"}` for a same-Segment retry. Set `owner_segment_id` on the Bad Outcome.
- `{"type":"end"}` for a terminal node.

Every source inventory item has unique `id`, `kind`, `locator`, and `text` when it represents exact text. Use distinct items for lines, questions, choices, routes, visuals, facts and cast where present. Coverage has one record per source ID with `target_ids` pointing to nodes, lines or options. A text item maps to a line/option/question/visual containing the same text; an authorized edit needs a `changes` record with `source_id`, `reason` and `authorization`. Facts must remain covered even when their text is distributed across lines; explicitly document and manually verify such mapping rather than inventing a text match.

## Worked example

This small invented example illustrates graph mechanics, not a production source or approved speech. A main scene offers two source options. The wrong option reaches its own consequence, whose button returns to the same scene. The right option reaches the ending. A real source with more options or a recovery question retains those nodes too.

```json
{
  "schema_version": "3.0", "title": "Check the delivery", "input_mode": "starling_link",
  "source": {"uri": "illustrative fixture"},
  "characters": [{"id": "lead", "name": "Asha", "role": "Supervisor"}],
  "start_node": "segment_1",
  "nodes": [
    {"id":"segment_1","kind":"segment","title":"Check","visual":"Asha beside the delivery.","source_refs":["beat1"],"lines":[],
     "transition":{"type":"choice","question":"What should Asha do?","options":[
       {"id":"check","text":"Check the record","target":"ending"},
       {"id":"skip","text":"Skip the check","target":"bad_1"}]}},
    {"id":"bad_1","kind":"bad_outcome","title":"Mismatch","visual":"The mismatch remains unresolved.","source_refs":["consequence1"],"lines":[],"owner_segment_id":"segment_1",
     "transition":{"type":"button","label":"Try again","target":"segment_1"}},
    {"id":"ending","kind":"ending","title":"Complete","visual":"Asha checks the record.","source_refs":["end1"],"lines":[],"transition":{"type":"end"}}
  ],
  "source_inventory":[{"id":"beat1","kind":"beat","locator":"fixture beat"},{"id":"consequence1","kind":"consequence","locator":"fixture consequence"},{"id":"end1","kind":"ending","locator":"fixture ending"}],
  "coverage":[{"source_id":"beat1","target_ids":["segment_1"]},{"source_id":"consequence1","target_ids":["bad_1"]},{"source_id":"end1","target_ids":["ending"]}],
  "changes":[]
}
```

Ready-document adapter: assign source locators such as `paragraph:12` or `table:2/row:3/cell:1`, record exact text, map to nodes/lines/options and copy it unchanged. Keep title and cast information as source items as well. If a document lacks an explicit branch target or a speaker cannot be identified, resolve it before completing the graph. Style-reference beat IDs are companion visual mappings, not replacements for these canonical nodes.

"""Check active instruction links and current exported source provenance."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
skills = sorted(ROOT.glob('starling-*/SKILL.md'))
if not any(p.parent.name == 'starling-script-rebuilder' for p in skills):
    skills.append(Path.home()/'.codex/skills/starling-script-rebuilder/SKILL.md')
assert len(skills) == 11, 'Expected eleven active skill entrypoints'
markdown = set(ROOT.glob('pipeline/*.md'))
for skill in skills:
    text = skill.read_text(encoding='utf-8-sig')
    assert re.match(r'---\nname: [^\n]+\ndescription: [^\n]+\n', text), skill
    assert text.count('\n---\n') == 1, ('Repeated skill frontmatter', skill)
    markdown.update(skill.parent.rglob('*.md'))
links = 0
for path in sorted(markdown):
    text = path.read_text(encoding='utf-8-sig')
    for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
        if '://' in target or target.startswith('#'):
            continue
        assert (path.parent/target.split('#')[0]).exists(), (path, target)
        links += 1
    for stale in ('cut_times value inside the used interval', 'cut_times value within used duration',
                  'Account for the full initial submission pass, then hand',
                  'Once the initial pass is accounted for, inspect'):
        assert stale not in text, (path, stale)
out = ROOT/'deliveries/workflow-explanation-2026-10-18'
if not out.exists(): out = ROOT/'docs'
records = json.loads((out/'source-index.json').read_text(encoding='utf-8'))
for record in records:
    source = next(p for p in skills if p.parent.name == record['name'])
    assert hashlib.sha256(source.read_bytes()).hexdigest() == record['sha256'], source
print(json.dumps({'skills':len(skills), 'markdown_files':len(markdown), 'local_links':links,
                  'source_hashes':'passed', 'stale_instruction_scan':'passed'}, indent=2))

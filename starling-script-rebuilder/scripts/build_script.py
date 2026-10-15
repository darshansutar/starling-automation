"""Validate one canonical graph and build matching Word and JSON artifacts. Stdlib only."""
import argparse
import json
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZipFile, ZIP_DEFLATED

def require(value, message):
    if not value: raise ValueError(message)

def validate(d):
    require(d.get('schema_version')=='3.0','Expected schema 3.0')
    require(d.get('title') and d.get('source'),'Title and source required')
    require(d.get('input_mode') in ('starling_link','finalized_document'),'Input mode required')
    cast=[c['id'] for c in d['characters']]
    require(len(cast)==len(set(cast)),'Duplicate cast IDs')
    nodes=d['nodes']; ids=[n['id'] for n in nodes]
    require(nodes and len(ids)==len(set(ids)) and d['start_node'] in ids,'Invalid node inventory/start')
    byid={n['id']:n for n in nodes}; elements={}; edges={}
    def add(ident,text):
        require(ident not in elements,'Duplicate element ID: '+ident);elements[ident]=text
    for n in nodes:
        require(n['kind'] in ('segment','recovery','bad_outcome','ending','decision'),'Unknown node kind')
        require(n.get('visual') and n.get('source_refs'),'Visual and source refs required')
        require(not any(k in n for k in ('next','retry','auto_advance')),'Use exactly one transition object')
        t=n['transition']; typ=t['type']; add(n['id'],n['visual']+'\n'+t.get('question',''))
        for line in n['lines']:
            require(line['speaker'] in cast,'Unknown speaker');require(isinstance(line['text'],str),'Line text required')
            add(line['id'],line['text'])
        targets=[]
        if typ=='choice':
            require(t.get('question') and len(t.get('options',[]))>=2,'Question and options required')
            for o in t['options']:add(o['id'],o['text']);targets.append(o['target'])
        elif typ in ('auto','button'):
            targets=[t['target']]
            if typ=='button':require(t.get('label'),'Button label required')
            if typ=='button' and t['label']=='Try again':
                require(n.get('owner_segment_id')==t['target'] and byid[t['target']]['kind']=='segment','Retry must target owning Segment')
        else:require(typ=='end','Invalid transition')
        require(all(x in byid for x in targets),'Dangling route');edges[n['id']]=targets
    seen=set();todo=[d['start_node']]
    while todo:
        node=todo.pop()
        if node not in seen:seen.add(node);todo.extend(edges[node])
    require(seen==set(ids),'Unreachable source nodes')
    require(any(n['transition']['type']=='end' for n in nodes),'No terminal outcome')
    inventory=d['source_inventory'];source_ids=[s['id'] for s in inventory]
    require(source_ids and len(source_ids)==len(set(source_ids)),'Invalid source inventory')
    coverage=d['coverage'];cov_ids=[c['source_id'] for c in coverage]
    require(len(cov_ids)==len(set(cov_ids)) and set(cov_ids)==set(source_ids),'Incomplete/duplicate coverage')
    require(all(set(n['source_refs']).issubset(source_ids) for n in nodes),'Unknown source reference')
    changes=d.get('changes',[])
    require(all(c.get('source_id') in source_ids and c.get('reason') and c.get('authorization') for c in changes),'Authorized change evidence required')
    changed={c['source_id'] for c in changes};original={s['id']:s for s in inventory}
    for c in coverage:
        require(c.get('target_ids') and set(c['target_ids']).issubset(elements),'Unknown coverage target')
        src=original[c['source_id']]
        if 'text' in src and c['source_id'] not in changed:
            require(src['text'] in '\n'.join(elements[x] for x in c['target_ids']),'Source text missing or changed: '+src['id'])
    return d

def paragraphs(d):
    yield 'Title',d['title']
    yield 'Normal','Source mode: '+d['input_mode']
    yield 'Normal','Timing: provisional until accepted audio is measured.'
    yield 'Heading1','Cast'
    for c in d['characters']:yield 'Normal',c['name']+' ('+c['id']+'): '+c.get('role','')
    yield 'Heading1','Flow summary'
    for n in d['nodes']:
        t=n['transition'];routes=', '.join(o['text']+' → '+o['target'] for o in t.get('options',[])) if t['type']=='choice' else t.get('target','End')
        yield 'Normal',n['id']+' | '+t['type']+' | '+routes
    for n in d['nodes']:
        yield 'Heading1',n['title']+' ['+n['id']+']'
        yield 'Normal','Visual: '+n['visual']
        for l in n['lines']:yield 'Normal',l['speaker']+': '+l['text']
        t=n['transition']
        if t['type']=='choice':
            yield 'Heading2',t['question']
            for o in t['options']:yield 'Normal',o['text']+' → '+o['target']
        elif t['type']=='button':yield 'Normal','[ '+t['label']+' ] → '+t['target']
        elif t['type']=='auto':yield 'Normal','Continue to '+t['target']
        else:yield 'Normal','End'
    yield 'Heading1','Source coverage'
    for c in d['coverage']:yield 'Normal',c['source_id']+' → '+', '.join(c['target_ids'])
    yield 'Heading1','Authorized changes'
    for c in d.get('changes',[]):yield 'Normal',c['source_id']+': '+c['reason']+' | '+c['authorization']
    if not d.get('changes'):yield 'Normal','Source content retained.'

def build(d,out):
    validate(d);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/'script.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
    ns='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    body=''.join('<w:p><w:pPr><w:pStyle w:val="'+style+'"/></w:pPr><w:r><w:t xml:space="preserve">'+escape(text)+'</w:t></w:r></w:p>' for style,text in paragraphs(d))
    document=f'<w:document xmlns:w="{ns}"><w:body>'+body+'<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/></w:sectPr></w:body></w:document>'
    styles=f'<w:styles xmlns:w="{ns}"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="22"/><w:color w:val="000000"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="120"/></w:pPr></w:pPrDefault></w:docDefaults>'
    for name,size in [('Normal',22),('Title',36),('Heading1',28),('Heading2',24)]:
        styles+=f'<w:style w:type="paragraph" w:styleId="{name}"><w:name w:val="{name}"/><w:pPr>'+('<w:keepNext/>' if name!='Normal' else '')+f'</w:pPr><w:rPr><w:sz w:val="{size}"/>'+('<w:b/>' if name!='Normal' else '')+'</w:rPr></w:style>'
    styles+='</w:styles>'
    files={'word/document.xml':document,'word/styles.xml':styles,
        '[Content_Types].xml':'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>',
        '_rels/.rels':'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>',
        'word/_rels/document.xml.rels':'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'}
    with ZipFile(out/'script.docx','w',ZIP_DEFLATED) as z:
        for path,xml in files.items():z.writestr(path,'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'+xml)

if __name__=='__main__':
    cli=argparse.ArgumentParser();cli.add_argument('source');cli.add_argument('--out');a=cli.parse_args()
    data=json.loads(Path(a.source).read_text(encoding='utf-8'));validate(data)
    if a.out:build(data,a.out)
    print('Canonical graph valid'+('; Word and JSON built, visual render review still required' if a.out else ''))

from pathlib import Path
import sys,json,re,zipfile,hashlib
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tmp/pdf-deps'))
import fitz
from PIL import Image,ImageDraw
OUT=ROOT/'deliveries/workflow-explanation-2026-10-21';QA=ROOT/'tmp/pdfs/workflow-explanation'
records=json.loads((QA/'word-inputs.json').read_text(encoding='utf-8'))
report=fitz.open(OUT/'Starling_Workflow_Explained.pdf')
assert len(report)==20
text='\n'.join(p.get_text() for p in report)
for term in ['intake.json','canonical-script.json','state.sqlite3','darshan@en2.ai','FFmpeg','ElevenLabs','Starling MCP','EN2','shot_inventory_match','retention_analysis','44 offline']:
    assert term in text,term
assert all(term in text for term in ('source_spans', 'manual lip-sync', 'buffer', 'hard cut'))
pages=[];counts=[]
for name,pdf in [('REPORT',OUT/'Starling_Workflow_Explained.pdf')]+[(r['name'],Path(r['render'])) for r in records]:
    document=fitz.open(pdf);counts.append({'name':name,'pages':len(document)})
    for n,page in enumerate(document,1):
        png=QA/(name+'-'+str(n)+'.png')
        page.get_pixmap(matrix=fitz.Matrix(1.25,1.25),alpha=False).save(png)
        pages.append((name,n,png))
        # Page-edge overflow only; visual review checks overlaps and spacing.
        for b in page.get_text('blocks'):
            assert b[0]>=-1 and b[1]>=-1 and b[2]<=page.rect.width+1 and b[3]<=page.rect.height+1,(name,n,b[:4])
    document.close()
for record in records:
    source=record['content'].replace('\r\n','\n').rstrip('\n')
    with zipfile.ZipFile(record['output']) as z:
        assert z.testzip() is None
        xml=ET.fromstring(z.read('word/document.xml'))
        ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        paras=[''.join(p.itertext()) for p in []]
        paras=[''.join(t.text or '' for t in p.findall('.//w:t',ns)) for p in xml.findall('.//w:body/w:p',ns)]
        body='\n'.join(paras).rstrip('\n')
        assert source in body,record['name']+' missing source text'
        if record.get('shared_contract'): assert record['shared_contract'].replace('\r\n','\n').rstrip('\n') in body
    assert hashlib.sha256(Path(record['source']).read_bytes()).hexdigest()==record['sha256']
contacts=[]
for index in range(0,len(pages),2):
    batch=pages[index:index+2];images=[Image.open(p[2]).convert('RGB') for p in batch]
    width=sum(im.width for im in images);height=max(im.height for im in images)+28
    sheet=Image.new('RGB',(width,height),'#e6eaee');draw=ImageDraw.Draw(sheet);x=0
    for item,im in zip(batch,images):
        draw.text((x+8,7),item[0]+' / page '+str(item[1]),fill='black');sheet.paste(im,(x,28));x+=im.width
    path=QA/f'inspect-{index//2+1:02}.jpg';sheet.save(path,quality=92);contacts.append(str(path))
(QA/'qa-summary.json').write_text(json.dumps({'page_counts':counts,'total_pages':len(pages),'source_checks':'All 11 Word documents contain the complete original skill text','contacts':contacts},indent=2),encoding='utf-8')
print(json.dumps({'page_counts':counts,'total_pages':len(pages),'contact_sheets':len(contacts),'source_text_checks':'passed','page_bounds':'passed'},indent=2))

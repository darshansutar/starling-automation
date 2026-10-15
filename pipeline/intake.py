"""Structural intake validation; user answers and visual inspection remain attestations."""
import hashlib
from pathlib import Path

def validate_intake(record, root):
    def need(value,message):
        if not value: raise ValueError(message)
    need(record.get('schema_version')=='1.0','Intake schema required')
    need(record.get('mode') in ('starling_link','finalized_document'),'Source mode required')
    need(record.get('confirmed_by')=='user' and record.get('status')=='complete','User intake answers required')
    need(all(record.get('answers',{}).get(k) for k in ('source','style','voices')),'Source, style and voice answers required')
    need(record.get('audio_mode') in ('generate','supplied','silent'),'Audio mode required')
    for name in ('source','style'):
        item=record.get(name,{})
        need(item.get('uri') and item.get('artifacts'),name+' evidence required')
        if name=='style':need(item.get('kind') in ('starling_link','reference_image'),'Style source required')
        for a in item['artifacts']:
            path=(Path(root)/a['path']).resolve()
            need(path.is_relative_to(Path(root).resolve()) and path.is_file(),'Intake artifact outside project or missing')
            need(hashlib.sha256(path.read_bytes()).hexdigest()==a['sha256'],'Intake artifact changed')
    speakers=record.get('speakers');need(isinstance(speakers,list) and len(speakers)==len(set(speakers)),'Speaker inventory required')
    voices=record.get('voices',[])
    need(len(voices)==len(speakers) and {v['speaker_id'] for v in voices}==set(speakers),'Every speaker needs a voice answer')
    if record['audio_mode']=='silent':need(not speakers and not voices,'Silent intake must have no speakers')
    else:need(speakers,'Speaking intake needs speakers')
    for v in voices:
        need(v.get('requested'),'Voice request required')
        need(v.get('selection_type') in ('id','name','recording'),'Voice selection type required')
        if v['selection_type']!='recording':need(v.get('resolved_voice_id'),'Resolve voice name/ID before completing intake')
        if record['audio_mode']=='supplied':need(v['selection_type']=='recording','Supplied audio must identify selected recordings')
    return record

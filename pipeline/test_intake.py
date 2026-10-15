import copy
import json
import tempfile
import unittest
from pathlib import Path
from runtime import Project, PipelineError, digest
from intake import validate_intake

def complete_intake(project):
    root=project.path
    source=root/'intake-source.txt';source.write_text('OFFLINE fixture source')
    style=root/'intake-style.txt';style.write_text('OFFLINE fixture stand-in, not visual approval')
    r={'schema_version':'1.0','mode':'starling_link','confirmed_by':'user','status':'complete','audio_mode':'generate',
       'source':{'uri':'fixture source','artifacts':[{'path':source.name,'sha256':digest(source)}]},
       'style':{'kind':'starling_link','uri':'fixture style','artifacts':[{'path':style.name,'sha256':digest(style)}]},
       'speakers':['narrator'],'voices':[{'speaker_id':'narrator','selection_type':'name','requested':'fixture','resolved_voice_id':'fixture-id'}],
       'answers':{k:'Synthetic user answer for offline test only' for k in ('source','style','voices')}}
    (root/'intake.json').write_text(json.dumps(r));project.record_intake('intake.json');return r

class IntakeTests(unittest.TestCase):
    def test_gate_and_changed_evidence(self):
        with tempfile.TemporaryDirectory() as t:
            p=Project(t,create=True)
            try:
                self.assertEqual(p.handoff()['stage'],'intake')
                with self.assertRaises(PipelineError):p.accept({'stage':'script'})
                complete_intake(p);p.require_intake()
                (p.path/'intake-style.txt').write_text('changed')
                with self.assertRaises(PipelineError):p.require_intake()
            finally:p.close()

    def test_missing_voice_and_finalized_mode(self):
        with tempfile.TemporaryDirectory() as t:
            p=Project(t,create=True)
            try:
                r=complete_intake(p);r['mode']='finalized_document';validate_intake(r,p.path)
                bad=copy.deepcopy(r);bad['voices']=[]
                with self.assertRaises(ValueError):validate_intake(bad,p.path)
                bad=copy.deepcopy(r);bad['voices'][0]['resolved_voice_id']=''
                with self.assertRaises(ValueError):validate_intake(bad,p.path)
                bad=copy.deepcopy(r);bad['answers']['style']=''
                with self.assertRaises(ValueError):validate_intake(bad,p.path)
            finally:p.close()

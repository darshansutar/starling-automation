"""Offline synthetic media tests. These attest no production clip quality."""
import json
import tempfile
import unittest
from pathlib import Path
from postproduction import Postproduction, write, execute, probe, visual_spans
from runtime import Project, PipelineError, digest, STAGES
from test_intake import complete_intake
from test_runtime import payload

SPATIAL={key:{"verdict":"pass","evidence":"Synthetic fixture only, not production review"} for key in ("scale_proportion","perspective_depth","separation_clearance","support_contact","orientation_construction","occlusion_order","spatial_continuity")}


class PostproductionTests(unittest.TestCase):
    def test_buffered_shots_trim_each_hold_and_preserve_audio(self):
        import subprocess
        execute(['ffmpeg','-v','error','-y','-f','lavfi','-i',
                 'color=red:s=1280x720:d=0.2:r=30[r];color=green:s=1280x720:d=0.2:r=30[g];color=blue:s=1280x720:d=0.2:r=30[b];color=yellow:s=1280x720:d=0.2:r=30[y];[r][g][b][y]concat=n=4:v=1:a=0',
                 '-an','-c:v','libx264','-pix_fmt','yuv420p',str(self.root/'buffered.mp4')])
        r=self.engine.attach('a','buffered.mp4','test_a')
        r.update(reviewer='OFFLINE SYNTHETIC TEST ONLY',status='verified',observations=['Synthetic only'],
                 full_picture_reviewed=True,full_audio_reviewed=True,scene_fidelity='pass',spatial_checks=SPATIAL)
        write(self.root/'a.json',r);self.engine.record_review('a.json');self.accept_fixture('b')
        self.engine.timeline[0]['clips'][0]['source_spans']=[[0,.2],[.4,.6]]
        result=self.engine.assemble('node');output=self.root/result['path']
        self.assertAlmostEqual(float(probe(output)['format']['duration']),.8,delta=.05)
        self.assertEqual(result['audio_units'][0]['sha256'],digest(self.root/'voice.wav'))
        for time,channel in ((.1,0),(.3,2)):
            pixel=subprocess.run(['ffmpeg','-v','error','-ss',str(time),'-i',str(output),
                                  '-frames:v','1','-vf','scale=1:1','-pix_fmt','rgb24','-f','rawvideo','-'],
                                 capture_output=True,check=True).stdout
            self.assertGreater(pixel[channel],180)
            self.assertLess(max(pixel[i] for i in range(3) if i!=channel),60)

    def test_invalid_buffer_spans_block_assembly(self):
        clip={'start':0,'end':6,'source_spans':[[0,3],[4,7]]}
        self.assertEqual(visual_spans(clip,'narration',8),clip['source_spans'])
        with self.assertRaisesRegex(PipelineError,'never dialogue'):visual_spans(clip,'dialogue',8)
        for spans in ([[0,3],[2,5]], [[0,3],[6,9]], [[0,2],[4,7]], [], [[0,float('nan')]]):
            with self.subTest(spans=spans), self.assertRaises(PipelineError):
                visual_spans(dict(clip,source_spans=spans),'narration',8)

    def test_dialogue_uses_embedded_audio_and_blocks_short_timeline(self):
        from unittest.mock import patch
        self.engine.clips['a']['content_kind']='dialogue'
        node={'clips':[{'clip_id':'a','start':0,'end':1}],
              'audio_units':[{'path':'standalone.wav','sha256':'old','duration':1}]}
        selected=[{'path':'fixture.mp4','sha':'selected-video-hash'}]
        streams={'streams':[{'codec_type':'video','duration':'1','start_time':'0'},
                            {'codec_type':'audio','duration':'1','start_time':'0'}]}
        with patch('postproduction.probe',return_value=streams):
            routed=self.engine.assembly_audio(node,selected)
            self.assertEqual(routed[0]['path'],'fixture.mp4')
            self.assertTrue(routed[0]['embedded_dialogue'])
            node['clips'][0]['end']=.8
            with self.assertRaisesRegex(PipelineError,'Dialogue would be cut'):
                self.engine.assembly_audio(node,selected)
            node['clips'][0]['end']=1
            node['audio_units'][0]['duration']=1.2
            with self.assertRaisesRegex(PipelineError,'boundaries'):
                self.engine.assembly_audio(node,selected)
        with patch('postproduction.probe',return_value={'streams':[streams['streams'][0]]}):
            with self.assertRaisesRegex(PipelineError,'embedded'):
                self.engine.assembly_audio(node,selected)

    def test_real_mixed_assembly_keeps_embedded_dialogue(self):
        execute(['ffmpeg','-v','error','-y','-i',str(self.root/'fixture.mp4'),'-i',str(self.root/'voice.wav'),
                 '-map','0:v:0','-map','1:a:0','-t','0.4','-c:v','copy','-c:a','aac',str(self.root/'dialogue.mp4')])
        self.engine.clips['a']['content_kind']='dialogue'
        r=self.engine.attach('a','dialogue.mp4','test_a')
        r.update(reviewer='OFFLINE SYNTHETIC TEST ONLY',status='verified',observations=['Synthetic only'],
                 full_picture_reviewed=True,full_audio_reviewed=True,scene_fidelity='pass',spatial_checks=SPATIAL,
                 dialogue_lipsync='pass',original_audio_sync='pass')
        write(self.root/'a.json',r);self.engine.record_review('a.json');self.accept_fixture('b')
        self.engine.timeline[0]['audio_units']=[{'path':'voice.wav','sha256':digest(self.root/'voice.wav'),'duration':.4} for _ in range(2)]
        result=self.engine.assemble('node')
        self.assertEqual(result['audio_units'][0]['path'],'dialogue.mp4')
        self.assertEqual(result['audio_units'][1]['path'],'voice.wav')
        self.assertAlmostEqual(float(probe(self.root/result['path'])['format']['duration']),.8,delta=.05)
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        runtime=Project(self.root,create=True,title='Offline synthetic postproduction')
        runtime.set_scope('renders',['a','b'])
        runtime.close()
        execute(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=c=blue:s=1280x720:d=0.4:r=30','-an','-c:v','libx264','-pix_fmt','yuv420p',str(self.root/'fixture.mp4')])
        execute(['ffmpeg','-v','error','-y','-f','lavfi','-i','sine=frequency=440:sample_rate=48000:duration=0.8','-ac','2','-c:a','pcm_s16le',str(self.root/'voice.wav')])
        execute(['ffmpeg','-v','error','-y','-i',str(self.root/'fixture.mp4'),'-frames:v','1',str(self.root/'still.jpg')])
        write(self.root/'canonical-script.json',{'nodes':[{'id':'node'}]})
        write(self.root/'audio/audio_manifest.json',{'synthetic':True});write(self.root/'visuals/image_manifest.json',{'synthetic':True})
        clips=[{'clip_id':cid,'content_kind':'narration','visual_format':'storyboard_1x2','used_duration_seconds':.4,'source_visual_sha256':digest(self.root/'still.jpg'),'inputs':[{'path':'still.jpg','sha256':digest(self.root/'still.jpg')}]} for cid in ('a','b')]
        write(self.root/'animation/animation-manifest.json',{'clips':clips,'source_sha256':digest(self.root/'canonical-script.json'),'audio_manifest_sha256':digest(self.root/'audio/audio_manifest.json'),'image_manifest_sha256':digest(self.root/'visuals/image_manifest.json')})
        write(self.root/'animation/assembly-plan.json',[{'node_id':'node','duration':.8,'clips':[{'clip_id':'a','start':0,'end':.4},{'clip_id':'b','start':.4,'end':.8}],'audio_units':[{'path':'voice.wav','duration':.8,'sha256':digest(self.root/'voice.wav')}]}])
        self.engine=Postproduction(self.root)
        complete_intake(self.engine.runtime)
        for stage in list(STAGES)[:6]:self.accept_stage(stage)
        for cid in ('a','b'):
            task=self.engine.runtime.prepare_render(cid,payload(),'narration')
            self.engine.runtime.job_update(task['intent'],'queued','Synthetic response','test_'+cid)
            self.engine.runtime.job_update(task['intent'],'review_pending','Synthetic completion')

    def tearDown(self):
        self.engine.close();self.temp.cleanup()

    def accept_stage(self,stage):
        runtime=self.engine.runtime
        ids=['a','b'] if stage=='renders' else [stage]
        runtime.set_scope(stage,ids)
        artifacts=[]
        for ident in ids:
            path=self.root/(ident+'-receipt.txt');path.write_text('OFFLINE synthetic evidence '+stage)
            artifacts.append({'id':ident,'path':path.name,'sha256':digest(path)})
        r={'stage':stage,'reviewer':'OFFLINE fixture','artifacts':artifacts,'checks':{key:{'verdict':'pass','evidence':'Synthetic only','artifact_ids':ids} for key in STAGES[stage]['checks']}}
        if stage=='docs':r.update(account_email='darshan@en2.ai',document_url='https://docs.google.com/document/d/offline-test')
        if stage=='animation_prompts':r['render_plans']={cid:{'payload':payload(),'content_kind':'narration','visual_format':'storyboard_1x2','shot_count':2,'cut_times':[2]} for cid in ('a','b')}
        runtime.accept(r)

    def accept_fixture(self,cid):
        r=self.engine.attach(cid,'fixture.mp4','test_'+cid)
        r.update(reviewer='OFFLINE SYNTHETIC TEST ONLY',status='verified',observations=['Synthetic fixture; not production review'],full_picture_reviewed=True,full_audio_reviewed=True,scene_fidelity='pass',spatial_checks=SPATIAL)
        write(self.root/(cid+'.json'),r);self.engine.record_review(cid+'.json')

    def test_deduplicated_completion_and_missing_clip_blocks_assembly(self):
        self.engine.attach('a','fixture.mp4','test_a')
        self.assertTrue(self.engine.attach('a','fixture.mp4','test_a')['deduplicated'])
        write(self.root/'snapshot.json',[{'id':'test_a','state':'done','video_url':'https://example.invalid/a'},{'id':'unrelated','state':'done','video_url':'https://example.invalid/b'}])
        self.assertEqual(self.engine.ingest('snapshot.json')['download_count'],0)
        self.assertEqual(len(self.engine.status()['outputs']),1)
        with self.assertRaises(PipelineError):self.engine.assemble('node')

    def test_ten_minute_monitor_scopes_queue_and_scores_only_reviewed_output(self):
        write(self.root/'statuses.json', [{'id':'test_a','state':'done','video_url':'https://example.invalid/a'},
                                          {'id':'test_b','state':'done','video_url':'https://example.invalid/b'}])
        result=self.engine.ingest('statuses.json')
        self.assertAlmostEqual(result['next_due_epoch']-float(self.engine.db.execute(
            "SELECT value FROM settings WHERE key='last_poll'").fetchone()[0]),600,delta=1)
        write(self.root/'queue.json', {'lanes':1,'items':[{'id':'test_a','state':'in line','videos_ahead':0},
                                                      {'id':'other','state':'rendering'}], 'all_done_in_s':80})
        pending=self.engine.monitor_report('queue.json')
        self.assertEqual(pending['studio_queue']['total'],2)
        self.assertEqual(pending['studio_queue']['project_items'],1)
        self.assertEqual(pending['counts']['generated'],2)
        self.assertEqual(pending['counts']['downloaded'],0)
        self.engine.attach('a','fixture.mp4','test_a')
        provisional=self.engine.monitor_report('queue.json')
        self.assertIsNone(provisional['clips'][0]['scorecard']['quality_score_percent'])
        self.assertEqual(provisional['clips'][0]['scorecard']['decision'],'unverified')
        review_path=self.engine.db.execute("SELECT review FROM outputs WHERE clip='a'").fetchone()[0]
        review=json.loads((self.root/review_path).read_text(encoding='utf-8'))
        review.update(reviewer='OFFLINE SYNTHETIC TEST ONLY',status='verified',
                      observations=['Synthetic fixture; not production review'],
                      full_picture_reviewed=True,full_audio_reviewed=True,
                      scene_fidelity='pass',spatial_checks=SPATIAL)
        write(self.root/'monitor-review.json',review)
        self.engine.record_review('monitor-review.json')
        accepted=self.engine.monitor_report('queue.json')
        self.assertEqual(accepted['counts']['verified'],1)
        self.assertEqual(accepted['clips'][0]['scorecard']['quality_score_percent'],100)

    def test_partial_review_cannot_pass_and_dialogue_cannot_zoom(self):
        r=self.engine.attach('a','fixture.mp4','test_a');r.update(reviewer='fixture',observations=['sample only'],status='verified',scene_fidelity='pass',spatial_checks=SPATIAL);write(self.root/'partial.json',r)
        with self.assertRaises(PipelineError):self.engine.record_review('partial.json')
        self.engine.clips['a']['content_kind']='dialogue';write(self.root/'recipe.json',{'clip_id':'a'})
        with self.assertRaises(PipelineError):self.engine.zoom('recipe.json')

    def test_real_assembly_and_final_package_gate(self):
        self.accept_fixture('a');self.accept_fixture('b');r=self.engine.assemble('node')
        self.assertAlmostEqual(float(probe(self.root/r['path'])['format']['duration']),.8,delta=.05)
        with self.assertRaises(PipelineError):self.engine.package()
        r.update(reviewer='OFFLINE SYNTHETIC TEST ONLY',observations=['Synthetic fixture only'],status='verified',full_picture_reviewed=True,full_audio_reviewed=True,scene_fidelity='pass',spatial_checks=SPATIAL,audio_joins='pass',script_coverage='pass')
        write(self.root/'final-review.json',r);self.engine.record_review('final-review.json')
        self.accept_stage('renders');self.accept_stage('assembly')
        result=self.engine.package();self.assertTrue((self.root/result['path']).is_file())
        write(self.root/'a.json',{'status':'verified'})
        with self.assertRaises(PipelineError):self.engine.selected('a')

    def test_changed_source_stops_work(self):
        (self.root/'still.jpg').write_bytes(b'changed')
        with self.assertRaises(PipelineError):self.engine.advance()

    def test_fallback_is_disabled_and_old_selection_rejected(self):
        with self.assertRaises(PipelineError):self.engine.zoom('unused.json')
        with self.assertRaises(PipelineError):self.engine.attach('a','fixture.mp4','test_a',kind='ffmpeg_still_zoom')
        self.accept_fixture('a')
        with self.engine.db:self.engine.db.execute("UPDATE outputs SET kind='ffmpeg_still_zoom' WHERE clip='a'")
        with self.assertRaises(PipelineError):self.engine.selected('a')

    def test_explicit_new_id_mapping_and_mismatch(self):
        runtime=self.engine.runtime
        runtime.set_scope('renders',['pairs_v3_a','pairs_v3_b'])
        with runtime.db:
            runtime.db.execute("UPDATE jobs SET clip='pairs_v3_a' WHERE clip='a'")
            runtime.db.execute("UPDATE jobs SET clip='pairs_v3_b' WHERE clip='b'")
        with self.assertRaises(PipelineError):self.engine.known_jobs()
        for cid in ('a','b'):self.engine.clips[cid]['runtime_clip_id']='pairs_v3_'+cid
        self.assertEqual(self.engine.known_jobs()['test_a']['source_clip'],'a')
        self.engine.timeline[0]['clips'].pop()
        with self.assertRaises(PipelineError):self.engine.source_check()

    def test_spatial_checks_and_dialogue_sync_are_required(self):
        r=self.engine.attach('a','fixture.mp4','test_a')
        r.update(reviewer='OFFLINE fixture',observations=['Synthetic only'],status='verified',full_picture_reviewed=True,full_audio_reviewed=True,scene_fidelity='pass')
        write(self.root/'missing-spatial.json',r)
        with self.assertRaises(PipelineError):self.engine.record_review('missing-spatial.json')
        r['spatial_checks']=SPATIAL;self.engine.clips['a']['content_kind']='dialogue'
        write(self.root/'missing-sync.json',r)
        with self.assertRaises(PipelineError):self.engine.record_review('missing-sync.json')
        self.assertEqual(self.engine.runtime.db.execute("SELECT state FROM jobs WHERE clip='a'").fetchone()[0],'review_pending')

    def test_rejected_reinspection_allows_en2_repair(self):
        self.accept_fixture('a')
        r=json.loads((self.root/'a.json').read_text())
        r.update(status='needs_fix',observations=['Synthetic later-discovered contact defect'])
        write(self.root/'reinspection.json',r);self.engine.record_review('reinspection.json')
        with self.assertRaises(PipelineError):self.engine.selected('a')
        task=self.engine.runtime.prepare_render('a',payload(),'narration')
        self.assertTrue(task['intent'])

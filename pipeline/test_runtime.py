"""Offline behavioral tests: no connected services or paid generation."""
import json
import tempfile
import unittest
from pathlib import Path
from runtime import Project, PipelineError, STAGES, digest, validate_render, validate_plan
from test_intake import complete_intake


def reference_prompt(description='approved two related shots'):
    return '\n\n'.join(k+': '+(description if k=='detailed_description' else 'fixture') for k in ('subject_definitions','summary','retention_analysis','detailed_description','overall_soundscape'))

def payload():
    return {'prompt':reference_prompt(), 'refs':['uploaded-board.jpg'], 'duration':5, 'width':1280, 'height':720, 'quality':False}


class RuntimeTests(unittest.TestCase):
    def test_three_shot_storyboard_and_cut_validation(self):
        plan = {'payload': dict(payload(), quality=True, duration=12), 'content_kind': 'narration',
                'visual_format': 'storyboard_1x3', 'shot_count': 3, 'cut_times': [4, 8]}
        validate_plan(plan)
        validate_plan(dict(plan, visual_format='storyboard_1x2', shot_count=2, cut_times=[6]))
        validate_plan(dict(plan, visual_format='narration_scene', shot_count=1, cut_times=[]))
        for changes in ({'cut_times': [8, 4]}, {'cut_times': [4, 4]}, {'cut_times': [4]},
                        {'cut_times': [4, 12]}, {'cut_times': [0, 8]}, {'visual_format': 'storyboard_1x2'},
                        {'shot_count': 4}):
            with self.subTest(changes=changes), self.assertRaises(PipelineError):
                validate_plan(dict(plan, **changes))

    def test_explicit_replacement_authorization_is_payload_and_attempt_bound(self):
        from runtime import canonical_hash
        self.ready()
        for _ in range(2):
            h = self.project.prepare_render('clip1', payload(), 'narration')
            self.project.job_update(h['intent'], 'queued', 'fixture', 'fixture-id-'+str(_))
            self.project.job_update(h['intent'], 'needs_fix', 'fixture')
        with self.assertRaises(PipelineError):
            self.project.prepare_render('clip1', payload(), 'narration')
        auth = {'authorized_by':'user', 'user_instruction':'Restart this reviewed clip',
                'clips':{'clip1':{'attempt':2,'payload_sha256':canonical_hash(payload())}}}
        path = Path(self.temp.name, 'replacement.json')
        path.write_text(json.dumps(auth))
        changed = dict(payload(), duration=6)
        with self.assertRaises(PipelineError):
            self.project.prepare_render('clip1', changed, 'narration', replacement_authorization='replacement.json')
        h = self.project.prepare_render('clip1', payload(), 'narration', replacement_authorization='replacement.json')
        with self.assertRaises(PipelineError):
            self.project.prepare_render('clip1', payload(), 'narration', replacement_authorization='replacement.json')
        self.project.job_update(h['intent'], 'queued', 'fixture', 'fixture-new')
        self.project.job_update(h['intent'], 'needs_fix', 'fixture')
        with self.assertRaises(PipelineError):
            self.project.prepare_render('clip1', payload(), 'narration', replacement_authorization='replacement.json')

    def test_first_last_handoff_and_input_isolation(self):
        self.ready()
        p = {'prompt': 'How the reference pictures align with the target video — Picture 1 opens; Picture 2 ends.\n\nintegrated_multimodal_description: [Shot 1] Fixture.\n\noverall_soundscape: Silence.\n\nnon_diegetic_music: N/A',
             'image': 'first.jpg', 'end': 'last.jpg', 'duration': 5, 'width': 1344, 'height': 768, 'quality': False}
        plan = {'payload': p, 'content_kind': 'narration', 'visual_format': 'first_last_frames', 'shot_count': 1, 'cut_times': []}
        r = self.receipt('animation_prompts')
        r['render_plans'] = {'clip1': plan}
        self.project.accept(r)
        # Historical receipts remain readable, but the retired route cannot submit.
        self.assertEqual(self.project.status()['animation_prompts']['state'], 'verified')
        with self.assertRaises(PipelineError): self.project.prepare_render('clip1', p, 'narration')
        for change in ({'refs': ['board.jpg']}, {'ref_audios': ['speech.wav']}, {'image': ''}, {'duration': 3}):
            with self.subTest(change=change):
                with self.assertRaises(PipelineError): validate_render(dict(p, **change), 'narration')
        with self.assertRaises(PipelineError): validate_render(p, 'dialogue')
        with self.assertRaises(PipelineError): validate_plan(dict(plan, cut_times=[5]))

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.project = Project(self.temp.name, create=True, title='Offline fixture')
        complete_intake(self.project)

    def tearDown(self):
        self.project.close()
        self.temp.cleanup()

    def receipt(self, stage, ids=None):
        ids = ids or [stage]
        self.project.set_scope(stage, ids)
        artifacts = []
        for item in ids:
            path = Path(self.temp.name) / (item + '.txt')
            path.write_text('Synthetic offline test artifact ' + stage, encoding='utf-8')
            artifacts.append({'id': item, 'path': path.name, 'sha256': digest(path)})
        r = {'stage': stage, 'reviewer': 'offline test fixture, not real QA', 'artifacts': artifacts,
             'checks': {c: {'verdict': 'pass', 'evidence': 'Synthetic test evidence', 'artifact_ids': ids} for c in STAGES[stage]['checks']}}
        if stage == 'docs':
            r.update(account_email='darshan@en2.ai', document_url='https://docs.google.com/document/d/offline-test')
        if stage == 'animation_prompts':
            r['render_plans'] = {c: {'payload': payload(), 'content_kind': 'narration', 'visual_format':'storyboard_1x2', 'shot_count':2, 'cut_times':[2.0]} for c in self.project.scope('renders')}
        return r

    def ready(self, clips=None):
        self.project.set_scope('renders', clips or ['clip1'])
        for stage in list(STAGES)[:6]:
            self.project.accept(self.receipt(stage))

    def test_first_handoff_and_resume(self):
        self.assertEqual(self.project.handoff()['stage'], 'script')
        self.project.accept(self.receipt('script'))
        self.project.close()
        self.project = Project(self.temp.name)
        self.assertEqual(self.project.handoff()['stage'], 'docs')

    def test_scoped_submission_waiver_preserves_preflight_and_duplicate_gates(self):
        config=self.project.config();config['submission_policy']='review_batches_10'
        with self.project.db:self.project.db.execute("UPDATE settings SET value=? WHERE key='config'",(json.dumps(config),))
        clips = ['clip'+str(i) for i in range(11)]
        self.ready(clips)
        with self.assertRaises(PipelineError):
            self.project.prepare_render('clip10', payload(), 'narration')
        path = Path(self.temp.name, 'waiver.json')
        path.write_text(json.dumps({'authorized_by': 'user', 'submission_only': True,
                                   'user_instruction': 'Queue all remaining clips', 'clip_ids': ['clip10']}))
        first = self.project.prepare_render('clip10', payload(), 'narration', review_boundary_waiver='waiver.json')
        self.assertTrue(first['intent'])
        with self.assertRaises(PipelineError):
            self.project.prepare_render('clip10', payload(), 'narration', review_boundary_waiver='waiver.json')
        with self.assertRaises(PipelineError):
            self.project.prepare_render('clip0', payload(), 'narration', review_boundary_waiver='waiver.json')
        with self.project.db:
            self.project.invalidate('images', 'Synthetic stale input')
        with self.assertRaises(PipelineError):
            self.project.prepare_render('clip10', payload(), 'narration', review_boundary_waiver='waiver.json')

    def test_dependency_gate(self):
        with self.assertRaises(PipelineError): self.project.accept(self.receipt('audio'))

    def test_legacy_and_current_reference_section_contract(self):
        validate_render(payload(), 'narration')
        current = payload(); current['prompt'] += '\nnon_diegetic_music: N/A'
        validate_render(current, 'narration')
        for prompt in (reference_prompt()+'\nunknown_section: N/A',
                       reference_prompt().replace('summary:', 'subject_definitions:'),
                       reference_prompt().replace('retention_analysis:', 'unmapped:')):
            with self.subTest(prompt=prompt):
                p=payload();p['prompt']=prompt
                with self.assertRaises(PipelineError):validate_render(p,'narration')

    def test_animation_requires_inventory_review(self):
        self.project.set_scope('renders',['clip1'])
        for stage in list(STAGES)[:5]:self.project.accept(self.receipt(stage))
        receipt=self.receipt('animation_prompts')
        del receipt['checks']['shot_inventory_match']
        with self.assertRaises(PipelineError):self.project.accept(receipt)
        self.project.accept(self.receipt('animation_prompts'))

    def test_saved_animation_receipt_needs_current_review(self):
        self.ready()
        row=self.project.db.execute("SELECT receipt FROM stages WHERE name='animation_prompts'").fetchone()
        receipt=json.loads(row[0]);del receipt['checks']['shot_inventory_match']
        with self.project.db:
            self.project.db.execute("UPDATE stages SET receipt=? WHERE name='animation_prompts'",(json.dumps(receipt),))
        self.assertEqual(self.project.status()['animation_prompts']['state'],'stale')

    def test_connector_rejection_without_job_can_retry(self):
        self.ready()
        first = self.project.prepare_render('clip1', payload(), 'narration')
        path = Path(self.temp.name, 'rejection.json')
        record = {'intent': first['intent'], 'response': {'isError': True, 'structuredContent': {
            'error_code': 'INVALID_ARGUMENT', 'error_data': {'reason': 'INVALID_PARAMETERS'}}}}
        path.write_text(json.dumps(record), encoding='utf-8')
        self.project.job_update(first['intent'], 'submission_rejected', path.name)
        retry = self.project.prepare_render('clip1', payload(), 'narration')
        self.assertNotEqual(first['intent'], retry['intent'])

    def test_integer_duration_validation_rejection_can_retry(self):
        self.ready()
        first = self.project.prepare_render('clip1', payload(), 'narration')
        path = Path(self.temp.name, 'typed-rejection.json')
        path.write_text(json.dumps({'intent': first['intent'], 'response': {'isError': True,
            'content': [{'type': 'text', 'text': '1 validation error for call[video_generate]\nduration\nInput should be a valid integer [type=int_from_float]'}]}}), encoding='utf-8')
        self.project.job_update(first['intent'], 'submission_rejected', path.name)
        retry = self.project.prepare_render('clip1', payload(), 'narration')
        self.assertNotEqual(first['intent'], retry['intent'])

    def test_timeout_cannot_be_reclassified_as_rejection(self):
        self.ready()
        first = self.project.prepare_render('clip1', payload(), 'narration')
        path = Path(self.temp.name, 'timeout.json')
        path.write_text(json.dumps({'intent': first['intent'], 'response': {'isError': True,
            'structuredContent': {'error_code': 'TIMEOUT'}}}), encoding='utf-8')
        with self.assertRaises(PipelineError):
            self.project.job_update(first['intent'], 'submission_rejected', path.name)
        with self.assertRaises(PipelineError):
            self.project.prepare_render('clip1', payload(), 'narration')

    def test_incomplete_evidence_rejected(self):
        r = self.receipt('script')
        r['checks']['stable_ids']['verdict'] = 'unverified'
        with self.assertRaises(PipelineError): self.project.accept(r)
        r['checks']['stable_ids']['verdict'] = 'not_applicable'
        with self.assertRaises(PipelineError): self.project.accept(r)

    def test_changed_file_invalidates_dependencies(self):
        self.project.accept(self.receipt('script'))
        self.project.accept(self.receipt('audio'))
        Path(self.temp.name, 'script.txt').write_text('Changed source')
        status = self.project.status()
        self.assertEqual(status['script']['state'], 'stale')
        self.assertEqual(status['audio']['state'], 'stale')

    def test_inventory_mismatch_rejected(self):
        r = self.receipt('script')
        self.project.set_scope('script', ['script', 'missing'])
        with self.assertRaises(PipelineError): self.project.accept(r)

    def test_wrong_google_account_rejected(self):
        self.project.accept(self.receipt('script'))
        r = self.receipt('docs'); r['account_email'] = 'other@example.com'
        with self.assertRaises(PipelineError): self.project.accept(r)

    def test_local_path_containment(self):
        with self.assertRaises(PipelineError): self.project.file('../outside.txt')

    def test_fast_and_input_modes(self):
        p = payload(); validate_render(p, 'narration')
        p['ref_audios'] = None
        with self.assertRaises(PipelineError): validate_render(p, 'narration')
        p = payload(); p['quality'] = True
        validate_render(p, 'narration')
        with self.assertRaises(PipelineError): validate_render(dict(p, quality='true'), 'narration')

    def test_dialogue_reference_budget(self):
        p = payload(); p.update(prompt=reference_prompt(), refs=['grid.jpg'], ref_audios=['speech.wav'])
        validate_render(p, 'dialogue', 14.9)
        with self.assertRaises(PipelineError): validate_render(p, 'dialogue', 15)

    def test_clean_dialogue_requires_audio(self):
        p = payload()
        p.update(prompt=reference_prompt(), refs=['scene.jpg'])
        with self.assertRaises(PipelineError): validate_render(p, 'dialogue')
        p['ref_audios'] = ['conversation.wav']
        validate_render(p, 'dialogue', 8.5)
        with self.assertRaises(PipelineError):
            validate_render(dict(p, refs=['scene.jpg', 'character-sheet.jpg']), 'dialogue', 8.5)

    def test_dialogue_plan_requires_scene_continuity(self):
        p = dict(payload(), refs=['scene.jpg'], ref_audios=['conversation.wav'])
        plan = {'payload': p, 'content_kind': 'dialogue', 'reference_seconds': 8.5,
                'visual_format': 'dialogue_scene'}
        with self.assertRaises(PipelineError):
            validate_plan(plan)
        plan['scene_continuity'] = {'review': 'pass', 'scene_master_sha256': 'a' * 64,
                                    'camera_side': 'window-facing side',
                                    'screen_positions': {'Ravi': 'left', 'Kamala': 'right'}}
        validate_plan(plan)

    def test_inspected_last_frame_continuation(self):
        p = {'prompt': 'How the reference pictures align with the target video - Picture 1 continues the approved scene.\n\nintegrated_multimodal_description: Continue the same moment.\n\noverall_soundscape: Silence.\n\nnon_diegetic_music: N/A',
             'image': 'last-frame.png', 'duration': 5, 'width': 1344, 'height': 768, 'quality': True}
        plan = {'payload': p, 'content_kind': 'narration', 'visual_format': 'continuation_frame',
                'shot_count': 1, 'cut_times': [], 'continuation_source': {
                    'inspection': 'pass', 'provider_id': 'video_previous',
                    'frame_upload_name': 'last-frame.png', 'scene_master_match': 'pass'}}
        validate_plan(plan)
        with self.assertRaises(PipelineError):
            validate_plan(dict(plan, continuation_source=dict(plan['continuation_source'], inspection='pending')))

    def test_bookend_reference_without_dummy_audio(self):
        p = payload()
        p.update(prompt=reference_prompt(), refs=['cast.jpg', 'set.jpg', 'board.jpg'])
        validate_render(p, 'speech_free')
        validate_render(p, 'narration', 0)
        for audio in (None, [], ['narrator.wav']):
            with self.subTest(audio=audio):
                with self.assertRaises(PipelineError):
                    validate_render(dict(p, ref_audios=audio), 'narration')
        with self.assertRaises(PipelineError): validate_render(dict(p, image='scene.jpg'), 'speech_free')
        with self.assertRaises(PipelineError): validate_render(dict(p, refs=[]), 'speech_free')
        validate_render(dict(p, quality=True), 'speech_free')
        with self.assertRaises(PipelineError): validate_render(dict(p, prompt='For the target video'), 'speech_free')
        with self.assertRaises(PipelineError): validate_render(p, 'speech_free', 2)

    def test_bookend_render_intent_preserves_source_plan(self):
        self.project.set_scope('renders', ['bookend'])
        for stage in list(STAGES)[:5]:
            self.project.accept(self.receipt(stage))
        p = payload()
        p.update(prompt=reference_prompt(), refs=['board.jpg'])
        r = self.receipt('animation_prompts')
        r['render_plans']['bookend'] = dict(payload=p, content_kind='speech_free', visual_format='storyboard_1x2', shot_count=2, cut_times=[2])
        self.project.accept(r)
        task = self.project.prepare_render('bookend', p, 'speech_free')
        self.assertTrue(task['intent'])
        self.project.job_update(task['intent'], 'submission_unknown', 'Synthetic timeout')
        with self.assertRaises(PipelineError): self.project.prepare_render('bookend', p, 'speech_free')

    def test_explicit_capacity_rejection_without_job(self):
        self.ready()
        task = self.project.prepare_render('clip1', payload(), 'narration')
        rejection = {'intent': task['intent'], 'response': {'isError': True, 'content': [
            {'type': 'text', 'text': 'the render line is about 35 minutes long and the box drops renders that wait past 40 — let it drain first'}]}}
        path = Path(self.temp.name, 'capacity-rejection.json')
        path.write_text(json.dumps(rejection), encoding='utf-8')
        self.project.job_update(task['intent'], 'submission_rejected', path.name)
        row = self.project.db.execute('SELECT state,provider_id FROM jobs WHERE intent=?', (task['intent'],)).fetchone()
        self.assertEqual(row['state'], 'submission_rejected')
        self.assertIsNone(row['provider_id'])

    def test_unknown_submission_never_duplicates(self):
        self.ready()
        task = self.project.prepare_render('clip1', payload(), 'narration')
        self.project.job_update(task['intent'], 'submission_unknown', 'Timeout after request')
        with self.assertRaises(PipelineError): self.project.prepare_render('clip1', payload(), 'narration')
        self.project.job_update(task['intent'], 'queued', 'Reconciled provider history', 'job1')

    def test_unapproved_payload_rejected(self):
        self.ready()
        p = payload(); p['refs'] = ['different.jpg']
        with self.assertRaises(PipelineError): self.project.prepare_render('clip1', p, 'narration')

    def test_batch_gate(self):
        config=self.project.config();config['submission_policy']='review_batches_10'
        with self.project.db:self.project.db.execute("UPDATE settings SET value=? WHERE key='config'",(json.dumps(config),))
        self.ready([f'clip{i}' for i in range(11)])
        with self.assertRaises(PipelineError): self.project.prepare_render('clip10', payload(), 'narration')

    def test_provider_done_is_not_verified(self):
        self.ready()
        task = self.project.prepare_render('clip1', payload(), 'narration')
        self.project.job_update(task['intent'], 'queued', 'Provider response', 'job1')
        self.project.job_update(task['intent'], 'review_pending', 'Provider done')
        review = Path(self.temp.name, 'review.json')
        review.write_text(json.dumps({'status': 'verified', 'provider_id': 'job1', 'full_picture_reviewed': False, 'full_audio_reviewed': False}))
        with self.assertRaises(PipelineError): self.project.job_update(task['intent'], 'verified', 'review.json')

    def test_repair_limit(self):
        self.ready()
        # Existing projects may retain the old setting; the current policy still caps retries.
        config = self.project.config()
        config['max_replacements'] = 2
        with self.project.db:
            self.project.db.execute('UPDATE settings SET value=? WHERE key=?', (json.dumps(config), 'config'))
        for attempt in range(2):
            task = self.project.prepare_render('clip1', payload(), 'narration')
            self.project.job_update(task['intent'], 'queued', 'Provider response', f'job{attempt}')
            self.project.job_update(task['intent'], 'needs_fix', 'Observed blocking defect')
        with self.assertRaises(PipelineError): self.project.prepare_render('clip1', payload(), 'narration')

    def test_complete_offline_handoff(self):
        self.ready()
        task = self.project.prepare_render('clip1', payload(), 'narration')
        self.project.job_update(task['intent'], 'queued', 'Synthetic provider response', 'offline-job')
        self.project.job_update(task['intent'], 'review_pending', 'Synthetic completion')
        r = self.receipt('renders', ['clip1'])
        artifact = r['artifacts'][0]
        review = dict(status='verified', provider_id='offline-job', full_picture_reviewed=True,
                      full_audio_reviewed=True, path=artifact['path'], sha256=artifact['sha256'])
        review.update(reviewer='OFFLINE fixture', observations=['Synthetic test only'], scene_fidelity='pass',
                      spatial_checks={key:{'verdict':'pass','evidence':'Synthetic only'} for key in ('scale_proportion','perspective_depth','separation_clearance','support_contact','orientation_construction','occlusion_order','spatial_continuity')})
        Path(self.temp.name, 'review.json').write_text(json.dumps(review), encoding='utf-8')
        self.project.job_update(task['intent'], 'verified', 'review.json')
        self.project.accept(r)
        self.project.accept(self.receipt('assembly'))
        self.assertTrue(self.project.handoff()['complete'])
        self.project.close()
        self.project = Project(self.temp.name)
        self.assertTrue(self.project.handoff()['complete'])

    def test_rejected_receipt_preserves_prior_acceptance(self):
        r = self.receipt('script'); self.project.accept(r)
        r['checks']['stable_ids']['evidence'] = ''
        with self.assertRaises(PipelineError): self.project.accept(r)
        self.assertEqual(self.project.status()['script']['state'], 'verified')


    def test_all_ready_default_and_board_metadata(self):
        self.ready([f'clip{i}' for i in range(11)])
        task=self.project.prepare_render('clip10',payload(),'narration')
        self.assertTrue(task['intent'])
        with self.assertRaises(PipelineError):self.project.prepare_render('clip10',payload(),'narration')
        plan={'payload':payload(),'content_kind':'narration','visual_format':'storyboard_1x2','shot_count':2,'cut_times':[2]}
        validate_plan(plan)
        for patch in ({'shot_count':1},{'cut_times':[]},{'cut_times':[5]},{'visual_format':'single_image'}):
            with self.assertRaises(PipelineError):validate_plan(dict(plan,**patch))
        old=payload();old.pop('refs');old['image']='old.jpg'
        with self.assertRaises(PipelineError):validate_render(old,'narration')

if __name__ == '__main__':
    unittest.main()

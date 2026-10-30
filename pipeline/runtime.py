"""Local state and handoff engine. Connected tools execute in ChatGPT, not here."""
import argparse
import hashlib
import json
import math
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
try:
    from .intake import validate_intake
except ImportError:
    from intake import validate_intake


STAGES = {
    'script': {'deps': [], 'skills': ['starling-script-rebuilder'],
               'checks': ['canonical_content', 'stable_ids', 'branch_routing']},
    'docs': {'deps': ['script'], 'skills': ['google-drive:google-docs'],
             'checks': ['account_identity', 'native_doc_readback', 'script_matches']},
    'audio': {'deps': ['script'], 'skills': ['starling-audio-pack'],
              'checks': ['word_coverage', 'speakers', 'measured_cues', 'listening']},
    'prompts': {'deps': ['audio'], 'skills': ['starling-director', 'starling-cinematography', 'starling-prompt-pack'],
                'checks': ['style_reference', 'director', 'cinematography', 'audio_mapping', 'complete_inventory']},
    'images': {'deps': ['prompts'], 'skills': ['starling-image-pack-generator', 'starling-verification'],
               'checks': ['all_assets_and_panels', 'director', 'cinematography', 'format_and_geometry', 'spatial_fidelity']},
    'animation_prompts': {'deps': ['images'], 'skills': ['starling-animation-pack'],
                          'checks': ['actual_inputs_inspected', 'mode_and_references', 'shot_inventory_match', 'measured_timing', 'provider_limits']},
    'renders': {'deps': ['animation_prompts'], 'skills': ['starling-animation-pack', 'starling-verification'],
                'checks': ['complete_picture', 'complete_sound', 'speech_and_lipsync', 'director', 'cinematography', 'spatial_fidelity']},
    'assembly': {'deps': ['renders', 'docs'], 'skills': ['starling-animation-pack', 'starling-verification'],
                 'checks': ['complete_picture', 'assembled_audio', 'joins', 'all_branches', 'word_coverage']},
}


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


class PipelineError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise PipelineError(message)


def positive(value):
    return type(value) in (int, float) and math.isfinite(value) and value > 0


def validate_render(payload, content_kind, reference_seconds=None):
    """Validate the observed MCP input contract; live provider limits still need review."""
    allowed = {'prompt', 'duration', 'folder', 'height', 'width', 'quality', 'refs',
               'ref_videos', 'ref_audios', 'audio', 'image', 'end', 'clip', 'seed'}
    require(isinstance(payload, dict) and not set(payload) - allowed, 'Unknown EN2 fields')
    require(isinstance(payload.get('quality'), bool), 'EN2 quality must be explicit; new requests default to Ultra quality=true, historical Fast remains readable')
    require(isinstance(payload.get('prompt'), str) and payload['prompt'].strip(), 'Missing prompt')
    require(positive(payload.get('duration')), 'A positive render duration is required')
    for field in ('height', 'width'):
        require(type(payload.get(field)) is int and payload[field] > 0, f'Invalid {field}')
    require(content_kind in {'narration', 'speech_free', 'dialogue'}, 'Unknown content kind')
    if 'end' in payload:
        require(content_kind != 'dialogue', 'First/last frames keep speech external')
        require(all(isinstance(payload.get(k), str) and payload[k].strip() for k in ('image', 'end')), 'Both uploaded endpoint frames required')
        require(not any(k in payload for k in ('refs', 'ref_videos', 'ref_audios', 'audio', 'clip')), 'Endpoint frames cannot mix with reference inputs')
        require(4 <= payload['duration'] <= 15, 'Endpoint duration must be 4-15 seconds')
        require(reference_seconds is None or (type(reference_seconds) in (int, float) and reference_seconds == 0), 'Endpoint frames have no reference audio')
        headings = re.findall(r'^([a-z_]+):', payload['prompt'], re.MULTILINE)
        require(headings == ['integrated_multimodal_description', 'overall_soundscape', 'non_diegetic_music'], 'Endpoint prompt requires live base-guide sections')
        require(payload['prompt'].startswith('How the reference pictures align with the target video'), 'Endpoint alignment instruction required')
        return
    require('refs' in payload, 'Current production requires reference-to-video inputs')
    require(not any(k in payload for k in ('image', 'clip', 'audio', 'ref_videos')), 'Use scene/board refs with dialogue audio only when applicable')
    for field in ('refs',):
        values = payload.get(field)
        require(isinstance(values, list) and values and all(isinstance(v, str) and v for v in values),
                f'Missing uploaded {field}')
    if content_kind == 'dialogue':
        require(len(payload['refs']) == 1, 'Dialogue requires exactly one approved clean scene reference')
        values = payload.get('ref_audios')
        require(isinstance(values, list) and values and all(isinstance(v, str) and v for v in values),
                'Missing uploaded ref_audios')
        require(positive(reference_seconds) and reference_seconds < 15, 'Measured combined reference audio must be under 15 seconds')
    else:
        require('ref_audios' not in payload, 'Bookends keep narration external and omit reference audio')
        require(reference_seconds is None or (type(reference_seconds) in (int, float) and reference_seconds == 0),
                'Visual-only bookends have no reference audio duration')
    sections = ['subject_definitions', 'summary', 'retention_analysis', 'detailed_description', 'overall_soundscape']
    headings = re.findall(r'^([a-z_]+):', payload['prompt'], re.MULTILINE)
    require(headings in (sections, sections + ['non_diegetic_music']),
            'Reference prompt requires five legacy sections or six current provider sections in order')


def validate_plan(plan):
    validate_render(plan['payload'], plan['content_kind'], plan.get('reference_seconds'))
    if plan['content_kind'] == 'dialogue':
        require(plan.get('visual_format') == 'dialogue_scene', 'Dialogue requires a clean scene')
        continuity = plan.get('scene_continuity', {})
        require(continuity.get('review') == 'pass' and continuity.get('scene_master_sha256')
                and continuity.get('camera_side') and continuity.get('screen_positions'),
                'Dialogue requires an approved scene master, camera side and stable screen positions')
        if plan.get('preceding_narration_clip_id'):
            handoff = plan.get('narration_dialogue_handoff', {})
            require(handoff.get('review') == 'pass'
                    and handoff.get('scene_master_sha256') == continuity.get('scene_master_sha256')
                    and handoff.get('final_narration_panel_sha256')
                    and handoff.get('dialogue_scene_sha256')
                    and handoff.get('camera_axis_match') == 'pass'
                    and handoff.get('set_and_lighting_match') == 'pass'
                    and handoff.get('screen_positions_match') == 'pass',
                    'Narration before dialogue requires a passed visual continuity handoff')
    else:
        if 'end' in plan['payload']:
            # Historical endpoint receipts stay readable; prepare_render rejects the route for new submissions.
            require(plan.get('visual_format') == 'first_last_frames', 'Endpoint frame format required')
            require(plan.get('shot_count') == 1, 'Endpoints require one continuous shot')
            cuts = plan.get('cut_times')
            require(isinstance(cuts, list) and len(cuts) == plan['shot_count'] - 1, 'Endpoint cuts must match shot count')
            require(all(positive(t) and t < plan['payload']['duration'] for t in cuts), 'Endpoint cuts must be inside duration')
            return
        count = plan.get('shot_count')
        if plan['content_kind'] == 'narration':
            require(count in (2, 3) and plan.get('visual_format') == f'storyboard_1x{count}',
                    'Narration requires a matching labelled two- or three-panel storyboard')
            # Narration after dialogue is B-roll/subject action; only the narration-before-dialogue handoff is enforced, on the dialogue plan.
        elif count == 1:
            require(plan.get('visual_format') == 'narration_scene', 'Single-shot speech-free coverage requires one approved full-frame scene')
        else:
            require(count in (2, 3) and plan.get('visual_format') == f'storyboard_1x{count}', 'Storyboard requires matching two or three shot format')
        cuts = plan.get('cut_times')
        require(isinstance(cuts, list) and len(cuts) == count - 1 and all(positive(t) and t < plan['payload']['duration'] for t in cuts) and all(a < b for a, b in zip(cuts, cuts[1:])), 'Storyboard cuts must match shot count and increase strictly inside duration')


class Project:
    def __init__(self, path, create=False, title=None):
        self.path = Path(path).resolve()
        db = self.path / 'pipeline.sqlite3'
        require(create or db.is_file(), 'Project does not exist; run init first')
        if create:
            self.path.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(db, timeout=10)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS stages (name TEXT PRIMARY KEY, receipt TEXT);
            CREATE TABLE IF NOT EXISTS scopes (stage TEXT PRIMARY KEY, ids TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS jobs (intent TEXT PRIMARY KEY, clip TEXT NOT NULL,
                attempt INTEGER NOT NULL, payload TEXT NOT NULL, fingerprint TEXT NOT NULL,
                state TEXT NOT NULL, provider_id TEXT UNIQUE, preflight_hash TEXT NOT NULL,
                UNIQUE(clip, attempt));
            CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, at TEXT NOT NULL,
                action TEXT NOT NULL, detail TEXT NOT NULL);
        ''')
        if create:
            with self.db:
                require(not self.db.execute('SELECT 1 FROM settings').fetchone(), 'Project already initialized')
                self.db.execute('INSERT INTO settings VALUES (?,?)', ('config', json.dumps({
                    'title': title or self.path.name, 'google_email': 'darshan@en2.ai',
                    'aspect': '16:9', 'execution': 'chatgpt_session', 'monitor': 'not_active',
                    'image_provider': 'chatgpt_imagegen', 'audio_provider': 'elevenlabs',
                    'audio_model': 'eleven_v3', 'video_provider': 'en2_video_mcp',
                    'max_replacements': 1, 'submission_policy': 'all_ready_once',
                    'workflow_version': '2026-10-16', 'intake_required': True
                })))
                self.db.executemany('INSERT INTO stages VALUES (?,NULL)', [(s,) for s in STAGES])
                self.event('init', {'title': title})

    def close(self):
        self.db.close()

    def event(self, action, detail):
        self.db.execute('INSERT INTO events(at,action,detail) VALUES (?,?,?)',
                        (now(), action, json.dumps(detail)))

    def config(self):
        return json.loads(self.db.execute("SELECT value FROM settings WHERE key='config'").fetchone()[0])

    def intake_status(self):
        if not self.config().get('intake_required'):
            return {'state': 'historical', 'reason': 'Adopt current workflow with an explicit intake record before new production'}
        row = self.db.execute("SELECT value FROM settings WHERE key='intake'").fetchone()
        try:
            require(row is not None, 'Mandatory source, style and voice intake is incomplete')
            saved = json.loads(row[0]); path = self.file(saved['path'])
            require(digest(path) == saved['sha256'], 'Intake record changed')
            validate_intake(json.loads(path.read_text(encoding='utf-8')), self.path)
            return {'state': 'complete', 'path': saved['path']}
        except (ValueError, OSError, KeyError, TypeError) as exc:
            return {'state': 'blocked', 'reason': str(exc)}

    def record_intake(self, path):
        source = self.file(path)
        validate_intake(json.loads(source.read_text(encoding='utf-8')), self.path)
        record = {'path': path, 'sha256': digest(source)}
        with self.db:
            old = self.db.execute("SELECT value FROM settings WHERE key='intake'").fetchone()
            if old and json.loads(old[0]) != record:
                self.invalidate('script', 'Intake source/style/voice choices changed; reconcile existing work')
            config = self.config()
            config.update(workflow_version='2026-10-16', intake_required=True, submission_policy='all_ready_once')
            self.db.execute('UPDATE settings SET value=? WHERE key=?', (json.dumps(config), 'config'))
            self.db.execute('INSERT OR REPLACE INTO settings VALUES (?,?)', ('intake', json.dumps(record)))
            self.event('intake', record)

    def require_intake(self):
        state = self.intake_status()
        require(state['state'] == 'complete', state.get('reason', 'Complete mandatory intake first'))

    def file(self, relative):
        require(isinstance(relative, str) and relative, 'Artifact path required')
        path = (self.path / relative).resolve()
        require(path.is_relative_to(self.path), 'Artifact must be inside the project directory')
        require(path.is_file(), f'Missing artifact: {relative}')
        return path

    def scope(self, stage):
        row = self.db.execute('SELECT ids FROM scopes WHERE stage=?', (stage,)).fetchone()
        return json.loads(row[0]) if row else None

    def invalidate(self, stage, reason):
        require(stage in STAGES and reason.strip(), 'Stage and reason required')
        affected = {stage}
        for name, spec in STAGES.items():
            if any(d in affected for d in spec['deps']):
                affected.add(name)
        self.db.executemany('UPDATE stages SET receipt=NULL WHERE name=?', [(s,) for s in affected])
        self.event('invalidate', {'stages': sorted(affected), 'reason': reason})

    def set_scope(self, stage, ids):
        require(stage in STAGES, 'Unknown stage')
        require(isinstance(ids, list) and ids and all(isinstance(i, str) and i.strip() for i in ids), 'Nonempty item IDs required')
        require(len(ids) == len(set(ids)), 'Duplicate item IDs')
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            if self.scope(stage) != ids:
                self.invalidate(stage, 'Expected inventory changed')
                self.db.execute('INSERT OR REPLACE INTO scopes VALUES (?,?)', (stage, json.dumps(ids)))

    def status(self):
        result = {}
        for stage, spec in STAGES.items():
            row = self.db.execute('SELECT receipt FROM stages WHERE name=?', (stage,)).fetchone()
            receipt = json.loads(row[0]) if row and row[0] else None
            blockers = [d for d in spec['deps'] if result[d]['state'] != 'verified']
            state, reason = ('pending', 'Awaiting stage artifacts and evidence')
            if receipt:
                state, reason = 'verified', None
                try:
                    if stage == 'animation_prompts':
                        require(receipt.get('checks', {}).get('shot_inventory_match', {}).get('verdict') == 'pass',
                                'Animation prompt inventory review required under current contract')
                        for plan in receipt.get('render_plans', {}).values():
                            validate_plan(plan)
                    for artifact in receipt['artifacts']:
                        require(digest(self.file(artifact['path'])) == artifact['sha256'], 'Artifact changed: ' + artifact['path'])
                except (PipelineError, OSError) as exc:
                    state, reason = 'stale', str(exc)
            if blockers:
                state, reason = ('stale' if receipt else 'blocked'), 'Dependencies: ' + ', '.join(blockers)
            result[stage] = {'state': state, 'reason': reason, 'scope': self.scope(stage)}
        return result

    def handoff(self):
        intake = self.intake_status()
        if intake['state'] != 'complete':
            return {'stage': 'intake', 'instruction': 'Read pipeline/INTAKE.md; obtain user source/style/voice answers before building or generation', **intake}
        states = self.status()
        for stage, spec in STAGES.items():
            if states[stage]['state'] in {'pending', 'stale'} and all(states[d]['state'] == 'verified' for d in spec['deps']):
                return {'stage': stage, 'skills': spec['skills'], 'required_checks': spec['checks'],
                        'expected_ids': self.scope(stage), 'dependencies': spec['deps'],
                        'instruction': 'Read the owning skills, execute within user scope using connected ChatGPT tools, save artifacts and evidence, then accept a receipt. Do not fabricate evidence.',
                        'execution': 'chatgpt_session', 'config': self.config()}
        return {'stage': None, 'complete': all(s['state'] == 'verified' for s in states.values()), 'states': states}

    def accept(self, receipt):
        self.require_intake()
        stage = receipt.get('stage')
        require(stage in STAGES, 'Unknown receipt stage')
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            states = self.status()
            require(all(states[d]['state'] == 'verified' for d in STAGES[stage]['deps']), 'Dependencies are not verified')
            expected = self.scope(stage)
            require(expected is not None, 'Declare expected scope before acceptance')
            artifacts = receipt.get('artifacts')
            require(isinstance(artifacts, list) and artifacts, 'Receipt must bind actual files')
            ids = [a.get('id') for a in artifacts]
            require(len(ids) == len(set(ids)) and set(ids) == set(expected), 'Artifact inventory does not match declared scope')
            for a in artifacts:
                require(digest(self.file(a['path'])) == a.get('sha256'), 'Artifact hash mismatch: ' + a['path'])
            checks = receipt.get('checks', {})
            for check in STAGES[stage]['checks']:
                record = checks.get(check, {})
                require(record.get('verdict') in {'pass', 'not_applicable'}, f'Unverified/failed check: {check}')
                if record.get('verdict') == 'not_applicable':
                    allowed_na = (stage == 'audio' and receipt.get('speech_inventory') == []) or (stage == 'renders' and check == 'speech_and_lipsync' and receipt.get('dialogue_inventory') == [])
                    require(allowed_na, f'Required check cannot be waived: {check}')
                require(isinstance(record.get('evidence'), str) and record['evidence'].strip(), f'Evidence/reason required: {check}')
                require(record.get('artifact_ids') and set(record['artifact_ids']).issubset(set(ids)), f'Check must reference reviewed artifacts: {check}')
            require(isinstance(receipt.get('reviewer'), str) and receipt['reviewer'].strip(), 'Reviewer required')
            if stage == 'docs':
                require(receipt.get('account_email') == self.config()['google_email'], 'Wrong Google account')
                require(isinstance(receipt.get('document_url'), str) and receipt['document_url'].startswith('https://docs.google.com/document/d/'), 'Readback document URL required')
            if stage == 'animation_prompts':
                plans = receipt.get('render_plans', {})
                require(set(plans) == set(self.scope('renders') or [] ) and plans, 'Preflight must cover declared render inventory')
                for plan in plans.values():
                    validate_plan(plan)
            if stage == 'renders':
                for clip in expected:
                    latest = self.db.execute('SELECT state FROM jobs WHERE clip=? ORDER BY attempt DESC LIMIT 1', (clip,)).fetchone()
                    require(latest and latest[0] == 'verified', 'Render job lacks verified review: ' + clip)
            self.invalidate(stage, 'New accepted stage version')
            saved = dict(receipt, accepted_at=now())
            self.db.execute('UPDATE stages SET receipt=? WHERE name=?', (json.dumps(saved), stage))
            self.event('accept', saved)

    def prepare_render(self, clip, payload, content_kind, reference_seconds=None, review_boundary_waiver=None, replacement_authorization=None):
        self.require_intake()
        require('end' not in payload and 'image' not in payload, 'New production uses approved scene/storyboard refs and clean-scene refs for dialogue')
        require(re.fullmatch(r'[a-zA-Z0-9_-]+', clip or ''), 'Invalid clip ID')
        validate_render(payload, content_kind, reference_seconds)
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            require(self.status()['animation_prompts']['state'] == 'verified', 'Animation preflight must pass')
            require(clip in (self.scope('renders') or []), 'Clip not in approved render inventory')
            rows = self.db.execute('SELECT * FROM jobs WHERE clip=? ORDER BY attempt', (clip,)).fetchall()
            require(not rows or rows[-1]['state'] in {'needs_fix', 'submission_rejected', 'cancelled_before_call'}, 'Existing job must be reconciled/reviewed; do not resubmit')
            attempt = len(rows)
            replacement_record = None
            if replacement_authorization:
                authorization_file = self.file(replacement_authorization)
                authorization = json.loads(authorization_file.read_text(encoding='utf-8'))
                entry = authorization.get('clips', {}).get(clip, {})
                require(authorization.get('authorized_by') == 'user'
                        and isinstance(authorization.get('user_instruction'), str)
                        and authorization['user_instruction'].strip()
                        and entry.get('attempt') == attempt
                        and entry.get('payload_sha256') == canonical_hash(payload),
                        'Explicit user authorization must match clip, attempt and exact payload')
                replacement_record = {'path': replacement_authorization, 'sha256': digest(authorization_file)}
            require(replacement_record or attempt <= min(self.config()['max_replacements'], 1), 'Automatic replacement limit reached; stop for user review')
            scope = self.scope('renders')
            index = scope.index(clip)
            batch_start = (index // 10) * 10
            waiver_record = None
            if review_boundary_waiver:
                waiver_file = self.file(review_boundary_waiver)
                waiver_record = json.loads(waiver_file.read_text(encoding='utf-8'))
                require(waiver_record.get('authorized_by') == 'user'
                        and waiver_record.get('submission_only') is True
                        and isinstance(waiver_record.get('user_instruction'), str)
                        and waiver_record['user_instruction'].strip()
                        and clip in waiver_record.get('clip_ids', []),
                        'Explicit scoped user submission waiver required')
                waiver_record = {'path': review_boundary_waiver, 'sha256': digest(waiver_file)}
            for prior in ([] if waiver_record or self.config().get('submission_policy') == 'all_ready_once' else scope[:batch_start]):
                latest = self.db.execute('SELECT state FROM jobs WHERE clip=? ORDER BY attempt DESC LIMIT 1', (prior,)).fetchone()
                require(latest and latest[0] == 'verified', 'Previous batch must be fully verified')
            preflight = self.db.execute("SELECT receipt FROM stages WHERE name='animation_prompts'").fetchone()[0]
            approved = json.loads(preflight)['render_plans'].get(clip)
            require(approved is not None, 'Clip lacks accepted preflight')
            validate_plan(approved)
            require(approved and approved['payload'] == payload and approved['content_kind'] == content_kind
                    and approved.get('reference_seconds') == reference_seconds, 'Payload differs from accepted preflight')
            fingerprint = canonical_hash(payload)
            intent = f'{clip}-{attempt}-{fingerprint[:12]}'
            self.db.execute('INSERT INTO jobs VALUES (?,?,?,?,?,?,?,?)',
                            (intent, clip, attempt, json.dumps(payload), fingerprint, 'submitting', None, canonical_hash(preflight)))
            self.event('prepare_render', {'intent': intent, 'content_kind': content_kind,
                                          'review_boundary_waiver': waiver_record,
                                          'replacement_authorization': replacement_record})
            return {'intent': intent, 'tool': 'mcp__en2_video__video_generate' if 'end' in payload else 'mcp__codex_apps__en2_video_generate_video', 'arguments': payload,
                    'warning': 'Intent saved before external call. On uncertainty, reconcile instead of submitting again.'}

    def job_update(self, intent, state, evidence, provider_id=None):
        transitions = {'submitting': {'queued', 'submission_unknown', 'submission_rejected', 'cancelled_before_call'}, 'submission_unknown': {'queued'},
                       'cancelled_before_call': set(),
                       'submission_rejected': set(),
                       'queued': {'running', 'review_pending', 'needs_fix'},
                       'running': {'review_pending', 'needs_fix'},
                       'review_pending': {'verified', 'needs_fix'}, 'verified': {'needs_fix'}, 'needs_fix': set()}
        require(isinstance(evidence, str) and evidence.strip(), 'Evidence required')
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            row = self.db.execute('SELECT * FROM jobs WHERE intent=?', (intent,)).fetchone()
            require(row is not None and state in transitions[row['state']], 'Invalid job transition')
            actual_id = provider_id or row['provider_id']
            if state == 'submission_rejected':
                rejection = json.loads(self.file(evidence).read_text(encoding='utf-8'))
                response = rejection.get('response', {})
                error = response.get('structuredContent', {})
                typed_error = any(x.get('type') == 'text' and
                                  'validation error for call[video_generate]' in x.get('text', '') and
                                  'type=int_from_float' in x.get('text', '')
                                  for x in response.get('content', []))
                structured_error = (error.get('error_code') == 'INVALID_ARGUMENT' and
                                    error.get('error_data', {}).get('reason') == 'INVALID_PARAMETERS')
                capacity_error = any(x.get('type') == 'text' and
                                     'the render line is about ' in x.get('text', '') and
                                     'the box drops renders that wait past ' in x.get('text', '') and
                                     'let it drain first' in x.get('text', '')
                                     for x in response.get('content', []))
                require(rejection.get('intent') == intent and not actual_id and response.get('isError') is True
                        and (structured_error or typed_error or capacity_error),
                        'Explicit connector parameter or capacity rejection without a provider job required')
            require(state in {'submission_unknown', 'submission_rejected', 'cancelled_before_call'} or actual_id, 'Provider job ID required')
            require(not row['provider_id'] or actual_id == row['provider_id'], 'Provider job ID cannot change')
            if state == 'verified':
                require(self.status()['animation_prompts']['state'] == 'verified', 'Source preflight is stale')
                preflight = self.db.execute("SELECT receipt FROM stages WHERE name='animation_prompts'").fetchone()[0]
                if canonical_hash(preflight) != row['preflight_hash']:
                    current_plan = json.loads(preflight).get('render_plans', {}).get(row['clip'])
                    require(current_plan is not None
                            and canonical_hash(current_plan.get('payload')) == row['fingerprint'],
                            'Job belongs to an older preflight and its clip payload changed')
                review = json.loads(self.file(evidence).read_text(encoding='utf-8'))
                require(review.get('status') == 'verified' and review.get('provider_id') == actual_id, 'Verified job review required')
                require(review.get('full_picture_reviewed') is True and review.get('full_audio_reviewed') is True, 'Full picture and sound review required')
                require(review.get('reviewer') and review.get('observations') and review.get('scene_fidelity') == 'pass', 'Concrete named scene review required')
                for key in ('scale_proportion', 'perspective_depth', 'separation_clearance', 'support_contact', 'orientation_construction', 'occlusion_order', 'spatial_continuity'):
                    check = review.get('spatial_checks', {}).get(key, {})
                    require(check.get('verdict') in ('pass', 'not_applicable') and check.get('evidence'), 'Spatial review missing: ' + key)
                plan = json.loads(preflight)['render_plans'][row['clip']]
                if plan['content_kind'] == 'dialogue':
                    require(review.get('dialogue_lipsync') == 'pass' and review.get('original_audio_sync') == 'pass', 'Dialogue synchronization review required')
                require(digest(self.file(review['path'])) == review.get('sha256'), 'Review output hash mismatch')
            self.db.execute('UPDATE jobs SET state=?,provider_id=? WHERE intent=?', (state, actual_id, intent))
            if state == 'needs_fix':
                self.invalidate('renders', 'Observed render defect; affected outputs require repair/review')
            self.event('job_update', {'intent': intent, 'state': state, 'evidence': evidence, 'provider_id': actual_id})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, help='Project directory')
    commands = parser.add_subparsers(dest='command', required=True)
    init = commands.add_parser('init'); init.add_argument('--title')
    commands.add_parser('status'); commands.add_parser('next')
    intake = commands.add_parser('intake'); intake.add_argument('path', help='Project-relative completed intake JSON')
    scope = commands.add_parser('scope'); scope.add_argument('stage', choices=STAGES); scope.add_argument('ids', nargs='+')
    accept = commands.add_parser('accept'); accept.add_argument('receipt')
    invalidate = commands.add_parser('invalidate'); invalidate.add_argument('stage', choices=STAGES); invalidate.add_argument('--reason', required=True)
    prepare = commands.add_parser('prepare-render'); prepare.add_argument('clip'); prepare.add_argument('payload'); prepare.add_argument('--kind', choices=['narration', 'dialogue', 'speech_free'], required=True); prepare.add_argument('--reference-seconds', type=float)
    prepare.add_argument('--review-boundary-waiver', help='Project-relative scoped user authorization; submission only, never output acceptance')
    prepare.add_argument('--replacement-authorization', help='Project-relative user authorization for an exact additional replacement payload')
    update = commands.add_parser('job'); update.add_argument('intent'); update.add_argument('state'); update.add_argument('--evidence', required=True); update.add_argument('--provider-id')
    args = parser.parse_args()
    project = None
    try:
        project = Project(args.project, create=args.command == 'init', title=getattr(args, 'title', None))
        result = None
        if args.command in {'init', 'status'}:
            result = {'config': project.config(), 'intake': project.intake_status(), 'stages': project.status(), 'jobs': [dict(r) for r in project.db.execute('SELECT intent,clip,attempt,state,provider_id FROM jobs')]}
        elif args.command == 'intake': project.record_intake(args.path)
        elif args.command == 'next': result = project.handoff()
        elif args.command == 'scope': project.set_scope(args.stage, args.ids)
        elif args.command == 'accept': project.accept(json.loads(Path(args.receipt).read_text(encoding='utf-8')))
        elif args.command == 'invalidate':
            with project.db: project.invalidate(args.stage, args.reason)
        elif args.command == 'prepare-render': result = project.prepare_render(args.clip, json.loads(Path(args.payload).read_text(encoding='utf-8')), args.kind, args.reference_seconds, args.review_boundary_waiver, args.replacement_authorization)
        elif args.command == 'job': project.job_update(args.intent, args.state, args.evidence, args.provider_id)
        print(json.dumps(result if result is not None else {'ok': True}, indent=2))
    except (PipelineError, OSError, KeyError, TypeError, sqlite3.Error, json.JSONDecodeError) as exc:
        parser.exit(1, f'Pipeline error: {exc}\n')
    finally:
        if project: project.close()


if __name__ == '__main__':
    main()

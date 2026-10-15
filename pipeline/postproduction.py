"""Resumable EN2 review/repair/edit handoff. MCP calls stay in the active host."""
import argparse
import hashlib
import json
import math
import sqlite3
import subprocess
import time
import wave
import zipfile
from pathlib import Path
try:
    from .runtime import Project, PipelineError, require, digest
except ImportError:
    from runtime import Project, PipelineError, require, digest


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2), encoding='utf-8')
    temp.replace(path)


def execute(args):
    result = subprocess.run(args, capture_output=True, text=True)
    require(result.returncode == 0, result.stderr[-3000:])
    return result.stdout


def probe(path):
    return json.loads(execute(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)]))


class Postproduction:
    def __init__(self, project):
        self.runtime = Project(project)
        self.root = self.runtime.path
        self.home = self.root / 'postproduction'
        self.home.mkdir(exist_ok=True)
        self.db = sqlite3.connect(self.home / 'state.sqlite3', timeout=30)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS outputs (
          clip TEXT, sha TEXT, path TEXT, kind TEXT, provider_id TEXT,
          state TEXT, review TEXT, PRIMARY KEY(clip,sha));
        CREATE TABLE IF NOT EXISTS selections (clip TEXT PRIMARY KEY, sha TEXT);
        CREATE TABLE IF NOT EXISTS nodes (node TEXT PRIMARY KEY, path TEXT, sha TEXT,
          fingerprint TEXT, state TEXT, review TEXT);
        CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
        ''')
        self.manifest = read(self.root / 'animation/animation-manifest.json')
        self.clips = {c['clip_id']: c for c in self.manifest['clips']}
        require(len(self.clips) == len(self.manifest['clips']), 'Duplicate manifest clip IDs')
        self.timeline = read(self.root / 'animation/assembly-plan.json')
        cfg = self.home / 'automation.json'
        if not cfg.exists():
            write(cfg, {'poll_interval_seconds': 300, 'timezone': 'Asia/Calcutta',
                        'runner_status': 'blocked_runtime', 'runner_id': None,
                        'reason': 'No connected persistent scheduler with EN2 MCP and local workspace access',
                        'review_all_clips': True, 'auto_continue_authorized': True,
                        'submission_policy': 'all_ready_once',
                        'animation_fallback': 'disabled', 'max_paid_repairs': 2,
                        'delivery': 'separate_node_videos_zip',
                        'full_audiovisual_review_capability': 'unavailable_in_current_session'})

    def close(self):
        self.db.close()
        self.runtime.close()

    def file(self, relative):
        return self.runtime.file(relative)

    def rel(self, path):
        return Path(path).resolve().relative_to(self.root).as_posix()

    def event(self, action, detail):
        with self.runtime.db:
            self.runtime.event('postproduction_' + action, detail)

    def source_check(self):
        self.runtime.require_intake()
        timeline_ids = [c['clip_id'] for n in self.timeline for c in n['clips']]
        require(len(timeline_ids) == len(set(timeline_ids)) and set(timeline_ids) == set(self.clips), 'Timeline and manifest clip inventories differ')
        require(len({n['node_id'] for n in self.timeline}) == len(self.timeline), 'Duplicate assembly nodes')
        self.known_jobs()
        for path, key in [('canonical-script.json', 'source_sha256'),
                          ('audio/audio_manifest.json', 'audio_manifest_sha256'),
                          ('visuals/image_manifest.json', 'image_manifest_sha256')]:
            require(digest(self.file(path)) == self.manifest[key], 'Changed approved source: ' + path)
        for c in self.clips.values():
            for item in c['inputs']:
                require(digest(self.file(item['path'])) == item['sha256'], 'Changed clip input: ' + item['path'])

    def known_jobs(self):
        scope = self.runtime.scope('renders') or []
        mappings = {c.get('runtime_clip_id', cid): cid for cid, c in self.clips.items()}
        require(len(mappings) == len(self.clips), 'Duplicate runtime clip mappings')
        require(set(scope) == set(mappings), 'Render scope and assembly manifest differ; reconcile explicit runtime_clip_id mappings')
        result = {}
        for cid in scope:
            row = self.runtime.db.execute('SELECT * FROM jobs WHERE clip=? ORDER BY attempt DESC LIMIT 1', (cid,)).fetchone()
            if row and row['provider_id']:
                original = mappings[cid]
                result[row['provider_id']] = {**dict(row), 'source_clip': original}
        return result

    def ingest(self, snapshot):
        data = read(self.file(snapshot))
        if isinstance(data, dict):
            data = data.get('structuredContent', data)
            data = data.get('result', data.get('items', []))
        known = self.known_jobs()
        download, observed = [], []
        for item in data:
            pid = item.get('id')
            if pid not in known:
                continue
            job = known[pid]
            state = item.get('state')
            observed.append({'provider_id': pid, 'clip_id': job['source_clip'], 'state': state})
            if state == 'done':
                present = self.db.execute('SELECT * FROM outputs WHERE provider_id=?', (pid,)).fetchall()
                intact = any((self.root / r['path']).is_file() and digest(self.root / r['path']) == r['sha'] for r in present)
                if not intact and item.get('video_url'):
                    download.append({'clip_id': job['source_clip'], 'provider_id': pid,
                                     'url': item['video_url'],
                                     'path': f'postproduction/raw/{pid}.mp4'})
                if job['state'] in ('queued', 'running'):
                    self.runtime.job_update(job['intent'], 'review_pending', snapshot)
            elif state in ('running', 'rendering') and job['state'] == 'queued':
                self.runtime.job_update(job['intent'], 'running', snapshot)
            elif state in ('failed', 'error') and item.get('error') and job['state'] in ('queued', 'running', 'review_pending'):
                self.runtime.job_update(job['intent'], 'needs_fix', snapshot)
        now = time.time()
        with self.db:
            self.db.execute('INSERT OR REPLACE INTO settings VALUES (?,?)', ('last_poll', str(now)))
        write(self.home / 'download-handoff.json', download)
        self.event('poll', {'snapshot': snapshot, 'observed': observed, 'next_due_epoch': now + 300})
        return {'observed': observed, 'download_count': len(download), 'next_due_epoch': now + 300}

    def attach(self, clip, path, provider_id, kind='en2_render'):
        require(kind == 'en2_render', 'Only EN2 animation outputs may be attached for current production')
        require(clip in self.clips, 'Unknown clip')
        if kind == 'en2_render':
            require(provider_id in self.known_jobs() and self.known_jobs()[provider_id]['source_clip'] == clip, 'Wrong provider/clip mapping')
        source = self.file(path)
        sha = digest(source)
        exists = self.db.execute('SELECT state FROM outputs WHERE clip=? AND sha=?', (clip, sha)).fetchone()
        if exists:
            return {'clip': clip, 'sha256': sha, 'state': exists['state'], 'deduplicated': True}
        info = probe(source)
        video = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
        require(video is not None, 'Missing video stream')
        geometry = 'pass' if abs(video['width'] / video['height'] - 16 / 9) < .01 else 'requires_safe_aspect_normalization'
        require(float(info['format']['duration']) + .05 >= self.clips[clip]['used_duration_seconds'], 'Output shorter than planned interval')
        execute(['ffmpeg', '-v', 'error', '-i', str(source), '-f', 'null', '-'])
        packet = self.home / 'review' / (clip + '-' + sha[:12])
        packet.mkdir(parents=True, exist_ok=True)
        execute(['ffmpeg', '-v', 'error', '-y', '-i', str(source), '-vf', 'fps=2,scale=384:216,tile=4x4',
                 '-fps_mode', 'passthrough', str(packet / 'sheet-%02d.jpg')])
        review = {'clip_id': clip, 'provider_id': provider_id, 'path': path, 'sha256': sha,
                  'status': 'review_pending', 'kind': kind, 'technical_decode': 'pass', 'geometry': geometry, 'probe': info,
                  'full_picture_reviewed': False, 'full_audio_reviewed': False,
                  'scene_fidelity': 'unverified', 'dialogue_lipsync': 'unverified',
                  'original_audio_sync': 'unverified', 'observations': [],
                  'instruction': 'Review every clip, including dialogue. Sheets locate defects but do not pass full audiovisual QA.'}
        write(packet / 'review.json', review)
        with self.db:
            self.db.execute('INSERT INTO outputs VALUES (?,?,?,?,?,?,?)',
                            (clip, sha, path, kind, provider_id, 'review_pending', self.rel(packet / 'review.json')))
        self.event('output_attached', {'clip': clip, 'sha256': sha, 'path': path, 'kind': kind})
        return review

    def record_review(self, path):
        self.source_check()
        r = read(self.file(path))
        require(r.get('observations') and r.get('reviewer'), 'Named reviewer and concrete observations required')
        require(digest(self.file(r['path'])) == r['sha256'], 'Reviewed file changed')
        require(r.get('status') in ('verified', 'needs_fix', 'review_pending'), 'Invalid review state')
        if r['status'] == 'verified':
            require(r.get('full_picture_reviewed') is True and r.get('full_audio_reviewed') is True,
                    'Complete picture and audio review required')
            require(r.get('scene_fidelity') == 'pass', 'Scene fidelity must pass')
            for key in ('scale_proportion', 'perspective_depth', 'separation_clearance', 'support_contact', 'orientation_construction', 'occlusion_order', 'spatial_continuity'):
                check = r.get('spatial_checks', {}).get(key, {})
                require(check.get('verdict') in ('pass', 'not_applicable') and check.get('evidence'), 'Spatial review missing: ' + key)
            if 'clip_id' in r:
                output = self.db.execute('SELECT * FROM outputs WHERE clip=? AND sha=?', (r['clip_id'], r['sha256'])).fetchone()
                require(output is not None and output['kind'] == 'en2_render', 'Current attached EN2 output required')
                if self.clips[r['clip_id']]['content_kind'] == 'dialogue':
                    require(r.get('dialogue_lipsync') == 'pass' and r.get('original_audio_sync') == 'pass', 'Dialogue lip-sync and original audio alignment required')
                job = self.known_jobs().get(r.get('provider_id'))
                require(job and job['source_clip'] == r['clip_id'], 'Current provider/clip mapping required')
                require(self.runtime.status()['animation_prompts']['state'] == 'verified', 'Current animation preflight required')
                if job['state'] != 'verified':
                    self.runtime.job_update(job['intent'], 'verified', path)
        with self.db:
            if 'node_id' in r:
                node = self.db.execute('SELECT * FROM nodes WHERE node=?', (r['node_id'],)).fetchone()
                require(node and node['sha'] == r['sha256'], 'Unknown assembled version')
                if r['status'] == 'verified':
                    require(r.get('audio_joins') == 'pass' and r.get('script_coverage') == 'pass', 'Assembly joins/coverage required')
                self.db.execute('UPDATE nodes SET state=?,review=? WHERE node=?', (r['status'], path, r['node_id']))
            else:
                clip = r['clip_id']
                row = self.db.execute('SELECT * FROM outputs WHERE clip=? AND sha=?', (clip, r['sha256'])).fetchone()
                require(row is not None, 'Attach output before reviewing')
                require(row['kind'] == 'en2_render' or r['status'] != 'verified', 'Historical animation fallback cannot be verified for current selection')
                if r['status'] == 'verified' and self.clips[clip]['content_kind'] == 'dialogue':
                    require(r.get('dialogue_lipsync') == 'pass' and r.get('original_audio_sync') == 'pass', 'Dialogue lip-sync and original audio alignment required')
                self.db.execute('UPDATE outputs SET state=?,review=? WHERE clip=? AND sha=?', (r['status'], path, clip, r['sha256']))
                if r['status'] == 'verified':
                    self.db.execute('INSERT OR REPLACE INTO selections VALUES (?,?)', (clip, r['sha256']))
                else:
                    self.db.execute('DELETE FROM selections WHERE clip=? AND sha=?', (clip, r['sha256']))
        self.event('review', {'path': path, 'sha256': digest(self.file(path)), 'verdict': r['status']})
        if 'clip_id' in r and r['status'] == 'needs_fix':
            job = self.known_jobs().get(r.get('provider_id'))
            if job and job['state'] in ('queued', 'running', 'review_pending', 'verified'):
                self.runtime.job_update(job['intent'], 'needs_fix', path)
        return {'status': r['status']}

    def zoom(self, recipe_path):
        raise PipelineError('Still-image animation fallback is disabled; repair the clip through EN2')

    def concat_video(self, parts, target):
        listing = target.with_suffix('.concat.txt')
        require(all("'" not in str(p) for p in parts), 'Unsupported apostrophe in media path')
        listing.write_text(''.join("file '" + p.resolve().as_posix() + "'\n" for p in parts), encoding='utf-8')
        execute(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(listing), '-c', 'copy', '-an', str(target)])

    def selected(self, cid):
        row = self.db.execute('SELECT o.* FROM outputs o JOIN selections s ON o.clip=s.clip AND o.sha=s.sha WHERE o.clip=? AND o.state=?', (cid,'verified')).fetchone()
        require(row is not None, 'Unverified clip: ' + cid)
        require(row['kind'] == 'en2_render', 'Historical still-image alternatives cannot enter current stitching')
        job = self.known_jobs().get(row['provider_id'])
        require(job and job['source_clip'] == cid and job['state'] == 'verified', 'Selected output must match a current verified EN2 job')
        require(digest(self.file(row['path'])) == row['sha'], 'Selected output changed: ' + cid)
        review = read(self.file(row['review']))
        require(review.get('status') == 'verified' and review.get('sha256') == row['sha'], 'Selected review changed')
        review_sha = self.accepted_review_hash(row['review'])
        return {**dict(row), 'review_sha256': review_sha}

    def accepted_review_hash(self, path):
        actual = digest(self.file(path))
        for event in self.runtime.db.execute('SELECT detail FROM events WHERE action=? ORDER BY id DESC', ('postproduction_review',)):
            detail = json.loads(event[0])
            if detail['path'] == path:
                require(detail['sha256'] == actual and detail['verdict'] == 'verified', 'Accepted review changed or revoked')
                return actual
        raise PipelineError('No recorded review acceptance')

    def assemble(self, node_id):
        self.source_check()
        node = next(n for n in self.timeline if n['node_id'] == node_id)
        selected = [self.selected(c['clip_id']) for c in node['clips']]
        cursor = 0
        for c in node['clips']:
            require(abs(c['start']-cursor)<.001 and c['end']>c['start'], 'Timeline gap/overlap'); cursor=c['end']
        require(abs(cursor-node['duration'])<.001, 'Timeline duration mismatch')
        require(abs(sum(u['duration'] for u in node['audio_units'])-node['duration'])<.001, 'Audio coverage gap')
        fingerprint = hashlib.sha256(json.dumps([node, selected],sort_keys=True).encode()).hexdigest()
        previous = self.db.execute('SELECT * FROM nodes WHERE node=?', (node_id,)).fetchone()
        if previous and previous['fingerprint']==fingerprint and (self.root/previous['path']).is_file() and digest(self.root/previous['path'])==previous['sha']:
            return dict(previous)
        home = self.home / 'edited' / (node_id+'-'+fingerprint[:12]); home.mkdir(parents=True,exist_ok=True)
        parts=[]
        for n,(c,s) in enumerate(zip(node['clips'],selected)):
            frames=round(c['end']*30)-round(c['start']*30); target=home/f'visual-{n:02}.mp4'
            execute(['ffmpeg','-v','error','-y','-i',str(self.file(s['path'])),'-vf','scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30','-frames:v',str(frames),'-an','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p',str(target)])
            require(int(probe(target)['streams'][0]['nb_frames'])==frames,'Insufficient visual frames');parts.append(target)
        visual=home/'visual.mp4';self.concat_video(parts,visual)
        pcm=home/'original-audio.wav'
        with wave.open(str(pcm),'wb') as joined:
            joined.setparams((2,2,48000,0,'NONE','not compressed'))
            for n,u in enumerate(node['audio_units']):
                source=self.file(u['path']);require(digest(source)==u['sha256'],'Accepted audio changed')
                part=home/f'audio-{n:02}.wav';samples=round(u['duration']*48000)
                execute(['ffmpeg','-v','error','-y','-i',str(source),'-af',f'aresample=48000,atrim=end_sample={samples},asetpts=PTS-STARTPTS','-ac','2','-c:a','pcm_s16le',str(part)])
                with wave.open(str(part),'rb') as audio:
                    require(audio.getnframes()==samples,'Audio shorter than approved interval');joined.writeframes(audio.readframes(samples))
        target=home/(node_id+'.mp4')
        execute(['ffmpeg','-v','error','-y','-i',str(visual),'-i',str(pcm),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(node['duration']),'-movflags','+faststart',str(target)])
        execute(['ffmpeg','-v','error','-i',str(target),'-f','null','-'])
        require(abs(float(probe(target)['format']['duration'])-node['duration'])<=.05,'Assembly duration drift')
        review={'node_id':node_id,'path':self.rel(target),'sha256':digest(target),'status':'review_pending','full_picture_reviewed':False,'full_audio_reviewed':False,'scene_fidelity':'unverified','audio_joins':'unverified','script_coverage':'unverified','observations':[],'source_outputs':selected,'audio_units':node['audio_units'],'fingerprint':fingerprint}
        write(home/'review.json',review)
        with self.db:self.db.execute('INSERT OR REPLACE INTO nodes VALUES (?,?,?,?,?,?)',(node_id,self.rel(target),digest(target),fingerprint,'review_pending',self.rel(home/'review.json')))
        self.event('assembled',review)
        return review

    def package(self):
        self.source_check()
        states = self.runtime.status()
        require(states['renders']['state'] == 'verified' and states['assembly']['state'] == 'verified', 'Runtime renders and assembly receipts must pass before packaging')
        files=[]; nodes=[]
        for n in self.timeline:
            # Reconcile current selected inputs before accepting an older node review.
            self.assemble(n['node_id'])
            row=self.db.execute('SELECT * FROM nodes WHERE node=?',(n['node_id'],)).fetchone()
            require(row and row['state']=='verified','Final node review pending: '+n['node_id'])
            require(digest(self.file(row['path']))==row['sha'],'Edited video changed')
            self.accepted_review_hash(row['review'])
            files.extend([(self.file(row['path']),'videos/'+n['node_id']+'.mp4'),(self.file(row['review']),'reviews/'+n['node_id']+'.json')]);nodes.append(dict(row))
        files.extend([(self.file('canonical-script.json'),'script.json'),(self.file('animation/assembly-plan.json'),'assembly-plan.json')])
        provenance={'nodes':nodes,'selected_outputs':[self.selected(c) for c in self.clips],'branch_policy':'Separate nodes; choices and retries retained in script.json. No mutually exclusive outcomes concatenated.'}
        write(self.home/'delivery-manifest.json',provenance);files.append((self.home/'delivery-manifest.json','delivery-manifest.json'))
        target=self.home/(self.root.name+'-final.zip');temp=target.with_suffix('.pending.zip')
        with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_STORED) as archive:
            for src,name in files:archive.write(src,name)
            archive.writestr('README.txt','Use videos by canonical node ID and follow script.json choices. Original narration/dialogue timing retained. See reviews and delivery-manifest.json.\n')
        with zipfile.ZipFile(temp) as archive:require(archive.testzip() is None,'ZIP integrity error')
        temp.replace(target);self.event('packaged',{'path':self.rel(target),'sha256':digest(target)})
        return {'path':self.rel(target),'sha256':digest(target),'nodes':len(nodes)}

    def status(self):
        row=self.db.execute('SELECT value FROM settings WHERE key=?',('last_poll',)).fetchone()
        last=float(row[0]) if row else 0
        return {'configuration':read(self.home/'automation.json'),'poll_due':time.time()>=last+300,'next_due_epoch':last+300,
                'outputs':[dict(x) for x in self.db.execute('SELECT clip,kind,state,path,review FROM outputs')],
                'nodes':[dict(x) for x in self.db.execute('SELECT node,state,path,review FROM nodes')]}

    def advance(self):
        """Run available deterministic work; emit host-owned review/repair/poll tasks."""
        self.source_check(); actions=[]
        for row in self.db.execute('SELECT * FROM outputs WHERE state!=?',('verified',)).fetchall():
            action='review_complete_picture_and_sound' if row['state']=='review_pending' else 'repair_en2_animation'
            actions.append({'action':action,'clip_id':row['clip'],'path':row['path'],'review':row['review']})
        assembled=[]
        for node in self.timeline:
            try:
                for c in node['clips']:self.selected(c['clip_id'])
            except PipelineError:continue
            assembled.append(self.assemble(node['node_id']))
        actions.extend({'action':'review_final_node_and_audio_joins','node_id':r['node'],'path':r['path'],'review':r['review']} for r in self.db.execute('SELECT * FROM nodes WHERE state!=?',('verified',)))
        if self.status()['poll_due']:
            actions.insert(0,{'action':'poll_en2_known_jobs','tool':'en2_video.list_videos','provider_ids':list(self.known_jobs()),'interval_seconds':300})
        result={'actions':actions,'assembled':len(assembled),'automatic_external_runner':'not_active'}
        if len(list(self.db.execute('SELECT node FROM nodes WHERE state=?',('verified',))))==len(self.timeline):
            if self.runtime.status()['assembly']['state'] == 'verified':
                result['package']=self.package()
            else:
                actions.append({'action':'accept_runtime_renders_and_assembly_receipts','instruction':'Record all specialist, word and branch coverage evidence before packaging'})
        write(self.home/'next-actions.json',result);return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--project',required=True)
    sub=parser.add_subparsers(dest='command',required=True)
    for name in ('status','advance','package'):sub.add_parser(name)
    cmd=sub.add_parser('ingest');cmd.add_argument('snapshot')
    cmd=sub.add_parser('attach');cmd.add_argument('clip');cmd.add_argument('path');cmd.add_argument('--provider-id',required=True)
    cmd=sub.add_parser('review');cmd.add_argument('path')
    cmd=sub.add_parser('assemble');cmd.add_argument('node')
    args=parser.parse_args();engine=Postproduction(args.project)
    try:
        calls={'ingest':lambda:engine.ingest(args.snapshot),'attach':lambda:engine.attach(args.clip,args.path,args.provider_id),'review':lambda:engine.record_review(args.path),'assemble':lambda:engine.assemble(args.node),'advance':engine.advance,'status':engine.status,'package':engine.package}
        print(json.dumps(calls[args.command](),indent=2))
    except (PipelineError,OSError,KeyError,ValueError) as exc:parser.exit(1,str(exc)+'\n')
    finally:engine.close()


if __name__=='__main__':main()

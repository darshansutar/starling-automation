from pathlib import Path
import sys,json,hashlib,html,re
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tmp/pdf-deps'))
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

OUT=ROOT/'deliveries/workflow-explanation-2026-10-21';OUT.mkdir(parents=True,exist_ok=True)
QA=ROOT/'tmp/pdfs/workflow-explanation';QA.mkdir(parents=True,exist_ok=True)
FONT=Path('C:/Windows/Fonts')
for n,f in [('Body','arial.ttf'),('Bold','arialbd.ttf'),('Mono','consola.ttf')]:pdfmetrics.registerFont(TTFont(n,str(FONT/f)))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Body',boldItalic='Bold')
W,H=A4;M=43;CW=W-2*M
navy=colors.HexColor('#163247');teal=colors.HexColor('#0D6F73');gray=colors.HexColor('#53616C');pale=colors.HexColor('#EDF5F5')
styles={
'body':ParagraphStyle('body',fontName='Body',fontSize=10.5,leading=15.3,textColor=navy,spaceAfter=9),
'small':ParagraphStyle('small',fontName='Body',fontSize=8.5,leading=12,textColor=gray),
'head':ParagraphStyle('head',fontName='Bold',fontSize=13,leading=17,textColor=navy),
'cell':ParagraphStyle('cell',fontName='Body',fontSize=9,leading=12.5,textColor=navy),
'white':ParagraphStyle('white',fontName='Bold',fontSize=10,leading=13,textColor=colors.white),
'mono':ParagraphStyle('mono',fontName='Mono',fontSize=9,leading=13,textColor=navy)}
c=canvas.Canvas(str(OUT/'Starling_Workflow_Explained.pdf'),pagesize=A4)
c.setTitle('Starling workflow explained from user input to final output');c.setAuthor('Starling workflow documentation')
page=0;y=0;log=[]
def text(t,style='body',width=None,x=M):
    global y
    obj=Paragraph(t,styles[style]);w,h=obj.wrap(width or CW,1000)
    assert y-h>49,(page,t[:90],y,h)
    obj.drawOn(c,x,y-h);y-=h+9;return h
def head(t):
    global y
    y-=6;text(t,'head')
def page_start(title,kicker):
    global page,y
    if page:c.showPage()
    page+=1;log.append((page,title));c.bookmarkPage('p'+str(page));c.addOutlineEntry(title,'p'+str(page),0,False)
    c.setFillColor(teal);c.rect(0,H-9,W,9,fill=1,stroke=0)
    c.setFont('Bold',9);c.drawString(M,H-40,'STARLING  /  WORKFLOW EXPLAINED')
    c.setFillColor(gray);c.setFont('Body',8);c.drawRightString(W-M,H-40,'30 OCTOBER 2026')
    c.setFillColor(navy);c.setFont('Bold',23);c.drawString(M,H-78,title)
    y=H-100;text(kicker,'small')
    c.setStrokeColor(colors.HexColor('#D7E1E7'));c.line(M,40,W-M,40)
    c.setFont('Body',8);c.setFillColor(gray);c.drawString(M,26,'Source-based production  |  Current workflow snapshot');c.drawRightString(W-M,26,str(page))
def table(headers,rows,widths):
    global y
    data=[[Paragraph(html.escape(t),styles['white']) for t in headers]]+[[Paragraph(html.escape(str(t)).replace('\n','<br/>'),styles['cell']) for t in row] for row in rows]
    t=Table(data,colWidths=widths,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),navy),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#CCD7DF')),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F5F8FA')])]))
    _,h=t.wrap(CW,1000);assert y-h>49,(page,h,y);t.drawOn(c,M,y-h);y-=h+14
def skills(t):text('<b>Relevant skills:</b> '+t,'small')
def callout(t):
    global y
    obj=Paragraph(t,styles['body']);_,h=obj.wrap(CW-24,1000)
    c.setFillColor(pale);c.roundRect(M,y-h-20,CW,h+20,5,fill=1,stroke=0);obj.drawOn(c,M+12,y-h-10);y-=h+33
def bullets(items):
    for item in items:text('&#8226; '+item)

page_start('From input to final output','A user provides a Starling roleplay link or a finalized script. The workflow turns that source into reviewed, voiced node videos while preserving the story branches.')
text('The complete flow','head')
# A compact flowchart with two source entries, then a single ordered chain.
top=y;boxw=246;boxh=37;gap=9
def box(x,yy,w,h,label,fill=pale):
    c.setFillColor(fill);c.setStrokeColor(colors.HexColor('#BCD1D5'));c.roundRect(x,yy-h,w,h,5,fill=1,stroke=1)
    p=Paragraph(label,styles['cell']);_,ph=p.wrap(w-18,h);p.drawOn(c,x+9,yy-(h+ph)/2)
def arrow(x,yy,xx,yyy):
    c.setStrokeColor(teal);c.setLineWidth(1.2);c.line(x,yy,xx,yyy)
    c.line(xx,yyy,xx-3,yyy+5);c.line(xx,yyy,xx+3,yyy+5)
box(M,top,boxw,boxh,'<b>Starling roleplay link</b><br/>Retrieve story and visual references')
box(W-M-boxw,top,boxw,boxh,'<b>Finalized script document</b><br/>Keep its script; obtain style references')
center=W/2
c.line(M+boxw/2,top-boxh,M+boxw/2,top-boxh-12);c.line(W-M-boxw/2,top-boxh,W-M-boxw/2,top-boxh-12)
c.line(M+boxw/2,top-boxh-12,W-M-boxw/2,top-boxh-12)
yy=top-boxh-25;arrow(center,top-boxh-12,center,yy)
steps=[('1  Confirm inputs','Source mode, style and voices'),('2  Prepare the script','Complete branches; store and verify script'),('3  Accept the audio','Generate or reuse speech; listen and measure'),('4  Plan and approve images','Assets, two/three-shot boards and dialogue scenes'),('5  Prepare and submit animation','Check prompts/uploads; submit all ready once'),('6  Collect and verify videos','Review complete outputs; repair through EN2'),('7  Stitch and review final nodes','Join accepted clips with original audio'),('8  Export the final package','Separate node MP4s, script, plan and reviews')]
for i,(label,sub) in enumerate(steps):
    box(M+50,yy,CW-100,39,'<b>'+label+'</b>  |  '+sub)
    if i<len(steps)-1:arrow(center,yy-39,center,yy-49)
    yy-=49
y=yy-2
text('<b>Repair loop:</b> a failed image returns to image correction; a failed video returns to its source/prompt or EN2 render step, then is reviewed again. Only accepted videos enter stitching.','small')
text('The following pages explain each stage, its skills and outputs. Technical references and storage details follow the plain-language flow. The 11 separate Word files contain the complete current SKILL.md text.','small')

page_start('1  Confirm the inputs','The first step is to establish what the user wants to preserve and which style and voices to use.')
head('Three mandatory questions')
bullets(['<b>Source:</b> Is the input a Starling roleplay link or a finalized script document?','<b>Style:</b> Use the actual visual references from the source roleplay, or provide a style image / Starling reference link for the finalized document.','<b>Voices:</b> Which ElevenLabs voice ID or voice name should each speaking character and narrator use? Alternatively, explicitly select supplied final recordings or a silent production.'])
head('Two clear starting paths')
table(['Input','What happens'],[('Starling link','Retrieve every available beat, choice, branch, recovery, consequence, ending, character and actual visual reference through Starling MCP.'),('Finalized document','Follow its words, speakers, scenes and routes directly. A style-reference roleplay supplies visual style and compatible beat context; it does not replace the finalized story.')],[125,CW-125])
text('Read-only source inspection may identify the complete speaker list before voice mapping is finalized. Building and media generation wait for the answers. Existing answers for the same source/version are reused; an ambiguous voice name is clarified rather than guessed.')
callout('<b>Saved result:</b> intake.json records the source mode, selected style, speaker list, voice choices and the actual user answers. Referenced local files have fingerprints so a later change can be detected.')
skills('starling-production-master; starling-script-rebuilder; starling-audio-pack. Shared rule: pipeline/INTAKE.md.')

page_start('2  Prepare and store the script','The script becomes the fixed reference for all later speech, visuals and branching.')
head('Build from the complete source')
text('For a Starling link, retrieve the full source through MCP and build a coverage list. Every source element is mapped to a scene, line, choice or route. Keep all characters and source choices; do not force the story into a fixed number of stops or a fixed duration.')
text('For a finalized document, extract the content in reading order, including tables, and map it into the same structure without rewriting the approved prose. Ask about unclear speakers or missing route targets.')
head('Keep the branches explicit')
text('A node is one playable story unit. A Segment is a source-supported scene block; it may end with a decision or continue. Each choice points to its own destination. A same-Segment retry uses one explicit Try again button. Preserve any recovery route or ending already specified by the source.')
head('One source for Word and JSON')
text('The canonical script file is written once. The reusable builder validates it and produces a Word review document and a developer JSON graph from that same data. This keeps the dialogue and routes aligned. Word layout is rendered and inspected before a real script deliverable is approved.')
head('Store the approved script in Google Docs')
text('Confirm the connected account is darshan@en2.ai before writing. Save the real document ID and URL, then read back its native content and compare it with the canonical script. Google Docs is an additional script-storage gate; local files remain the production reference.')
callout('<b>Outputs:</b> canonical-script.json, source snapshots and coverage records, a review DOCX, matching developer JSON, and a native Google Doc with verified readback. The script builder emits script.docx and script.json in the selected output directory.')
skills('starling-script-rebuilder; starling-production-master. Supporting integrations: Google Drive / Google Docs and Documents skills.')

page_start('3  Create and accept the audio','Audio is completed before the final visual timing is planned.')
head('Generate only the required speech')
text('Inventory every spoken line with its speaker, language and branch. Use the selected ElevenLabs voices with the eleven_v3 model, or reuse explicitly selected final recordings. Choice buttons and other player controls are spoken only when the script says they are spoken.')
head('Listen and measure')
bullets(['Compare the entire recording with the script: all words, speaker identity, pronunciation, pauses and joins.','Measure real duration and speech cues. A word-count estimate is not a final timing measurement.','Save original recordings and actual provider job IDs. Reconcile an uncertain paid request before submitting again.'])
head('Keep narration and dialogue distinct')
table(['Type','How it is used'],[('Narration','Kept as an unchanged audio master. It can continue over visual cuts and is added during final stitching.'),('Dialogue','Accepted recordings are supplied to EN2 with the clean scene, clear speaker assignments and measured turn order. The user reviews lip-sync manually.'),('Speech-free coverage','Uses an explicit empty speech inventory for the interval. No dummy narration is generated.')],[105,CW-105])
text('A derived conversation track may join separate character recordings in the correct order. Any excerpt keeps its original speed and records where it came from. Replacing audio requires new timing checks for the affected visuals.')
callout('<b>Outputs:</b> accepted audio files, audio/audio_manifest.json, speaker/voice mappings, duration and cue records, listening evidence and any derived dialogue excerpts.')
skills('starling-audio-pack; starling-production-master. Connection: ElevenLabs MCP.')

page_start('4  Plan the visual coverage','Each visual explains a particular meaning or action in the script at the right point in the audio.')
head('Map meaning to time')
text('Read the whole story and all branches. Break each scene into meaningful visual beats: an introduction, location, problem, action, detail, reaction or outcome. Link each beat to its source line and actual accepted-audio interval. One script segment may need several storyboards.')
head('Decide what the viewer must understand')
bullets(['Record who and what is visible, the setting, current object state and the purpose of the shot.','Separate a proposed action from one that has already happened. Keep the correct outcome for that branch.','Use a wide view for orientation, a medium view for interaction and a detail view when a specific object matters.','Include recognizable character introductions, relevant setting/task coverage, useful opening orientation and closing coverage for actual endings and completed Bad Outcomes.'])
head('Every narration is a two- or three-shot storyboard')
text('Choose 1x2 or 1x3 from the actual audio beats; a single full-frame narration scene is not used. Listen to the entire recording first. A 13-second narration describing three situations must cover all three. Each panel adds supported information, such as action progress, a detail or a supported reaction, not just an ending pose for the previous image.')
table(['Narration position','Storyboard rule'],[('Before dialogue','The final panel leads straight into the dialogue lip-sync scene: upcoming speakers, lips closed, in their dialogue positions with the same scene master, set, lighting and camera side. Checked side by side.'),('After dialogue','Mainly B-roll and subject action that justify the scene. No handoff with the preceding dialogue is required.'),('Opening and ending','Normal audio-led storyboard method.')],[125,CW-125])
text('Place the edit cut at a measured audio cue. Add 1–2 seconds of buffer per narration or establishing shot before drawing. Generated cut times include those buffers and differ from edit cut times. Print generated ranges and action/hold durations below the panels and repeat them exactly in the prompt.')
callout('<b>Outputs:</b> a full asset inventory, source-to-audio-to-shot map, image prompts, reference assignments, shot purposes, planned timing and director/cinematography review records.')
skills('starling-prompt-pack; starling-director; starling-cinematography.')

page_start('5  Generate the image pack','Foundational references are approved before the storyboard and dialogue images that depend on them.')
head('Generate in dependency order')
text('<b>Character sheets → matching environments → prop sheets → storyboards and dialogue scenes.</b> Use native ChatGPT image generation and actual selected style images. Reference sheets define identity and materials; extra views on a character sheet are not extra characters in a scene.')
head('Use two or three stacked panels')
top=y;bw=220;bh=66
box(M,top,bw,bh,'<b>TOP PANEL</b><br/>Shot 1 composition')
box(M,top-bh,bw,bh,'<b>BOTTOM PANEL</b><br/>Shot 2 composition')
yy=top
for t in ['One column, two or three panels.','Each panel uses the output aspect.','Monochrome, matching approved design.','SHOT, time, CAMERA and ACTION below.','Whole-second labels match the plan.']:
    obj=Paragraph(t,styles['cell']);_,hh=obj.wrap(CW-bw-22,100);obj.drawOn(c,M+bw+22,yy-hh);yy-=hh+8
y=top-2*bh-20
text('Each picture has a white label strip below it with black SHOT, whole-second time, CAMERA and ACTION text. Keep picture areas free of white frames and gutters; preserve the approved style in grayscale without colour. Keep arrows and motion symbols out of the artwork. Leave a clear gap between adjacent people, with room for gestures. Save picture-area boxes separately from labels. The video presents one edge-to-edge colour scene at a time, connected by a hard cut.')
head('Dialogue follows a separate image route')
text('Dialogue uses one clean full-frame scene containing the actual participants, with approved dialogue audio for the later EN2 request. A mixed scene can contain narration and dialogue blocks without changing its canonical story node.')
callout('<b>Outputs:</b> durable image files, versions and reference mappings; visuals/image_manifest.json; actual dimensions and panel boxes; and review records for every asset, board and scene.')
skills('starling-image-pack-generator; starling-panel-corrector; starling-director; starling-cinematography.')

page_start('6  Check images before animation','The check is general physical plausibility, not a list of rules for one particular prop.')
table(['Check','Plain-language question'],[('Scale and proportion','Do people, objects and surroundings have believable size relationships for the approved style and camera distance?'),('Perspective and depth','Do the camera view, distances and placement agree?'),('Separation and clearance','Do solid bodies remain distinct, with enough space for the pose or action?'),('Support and contact','Is a seated person supported? Are feet grounded and grips physically plausible?'),('Orientation and construction','Are front/back faces, attachments, joints and object parts correctly arranged?'),('Occlusion','Do nearer surfaces correctly hide what is behind them?'),('Continuity','Do identity, ownership, scale and state remain consistent across all shots?')],[135,CW-135])
text('These checks catch a person merging into a chair or table, an implausible human-to-machine scale, or front-side content appearing on the back of a held object. A legitimately large machine or a justified perspective change is not automatically a defect.')
text('Also check source meaning, anatomy, cast count, clothing, lighting, scene state and clean presentation. Inspect every panel at useful resolution. If any panel fails, repair the actual image using its approved references, then recheck the complete replacement.')
callout('<b>Approval is version-specific.</b> Record the inspected file fingerprint, panel/region, observation and correction. All panels and their relationship must pass before an animation prompt is accepted.')
skills('starling-panel-corrector; starling-cinematography; starling-director; starling-verification. Shared reference: spatial-fidelity.md.')

page_start('7  Turn boards into animation','Approved images become specific instructions and inputs for one EN2 video request per storyboard.')
head('Write the prompt from the actual approved board')
text('The animation prompt identifies each reference, maps panels in top-to-bottom order to Shot 1, Shot 2 and optionally Shot 3, and describes only the supported movement within each shot. It specifies the clip duration, exact hard-cut cue, planned camera movement and scene relationships that must remain consistent.')
head('Upload the actual files and verify them')
text('For a board, upload visible character sheets, matching environment and relevant prop sheets, followed by the complete two- or three-panel board. For dialogue, upload only the clean scene. Save the returned upload names and fingerprints. Retrieve the uploaded image bytes and inspect them before submitting a paid render; an upload success message alone is not verification.')
table(['Request','Images and sound sent to EN2'],[('Storyboard video','Character sheets, matching environment, prop sheets, then storyboard. Original narration stays outside generation.'),('Dialogue video','Exactly one approved clean dialogue scene plus accepted speech with speaker/turn assignments.')],[125,CW-125])
head('What one board produces')
text('Example: two required 3-second shots plus a 1-second buffer each produce an 8-second render. Both storyboard and prompt say Shot 1 0–4, Shot 2 4–8 and hard cut at 4 seconds. Trim each hold separately to retain 6 seconds. Actual action, duration and provider limits govern each plan.')
text('Use EN2 reference-to-video and Ultra mode (quality=true). Narration characters remain silent. Dialogue lip-sync belongs only to the active speaker. The prompt is a request to the model; the result still needs complete review.')
callout('<b>Outputs:</b> exact animation prompts and payloads, approved render plans, uploaded-file evidence, shot/cut timing and source-to-clip mappings.')
skills('starling-animation-pack, with starling-director and starling-cinematography. Connection: EN2 video MCP.')

page_start('Final narration presentation','Inspect the actual storyboard first, then write affirmative instructions that describe the intended result.')
head('Audio-led shots with clear action')
text('Use black-and-white 1x2 or 1x3 storyboards with SHOT, time, CAMERA and ACTION labels below each picture. Actions and labels must match the inspected staging. A quiet shot may use a subtle 3-5 percent push-in or a small pan while object states stay fixed. Preserve time of day, lighting, weather, identity and hairstyle.')
head('Scene-matched reference groups')
text('Include only visible character identities, matching environment and relevant props, then the storyboard. Empty environment inserts need environment and storyboard only. Asset sheets supply appearance; the storyboard controls visible cast, objects, scale and placement. Choose 2D, 2.5D or 3D animation from the approved colour references.')
head('Affirmative prompt wording')
callout('Render each illustrated scene individually as an edge-to-edge, full-frame colour shot. At the specified time, switch directly to the next fully formed shot using a hard cut. Treat the storyboard layout and caption strips exclusively as production guidance.')
head('Review the finished video')
text('Check the full result for all planned scenes and timed hard cuts. Fades, dissolves, overlays, mixed panels, white borders or frames, labels and storyboard layout appearing in the video are defects. Keep these defect lists in verification; generation prompts describe the desired full-frame result positively.')
skills('starling-animation-pack; starling-verification. Final narration contract: references/narration-pairs.md. Worked prompt example: references/animation-template.md.')

page_start('Animation prompt structure','The official MiniMax H3 reference guide defines six sections. Its base guide supplies shared voiceover and speaker conventions.')
table(['Prompt section','What it says'],[('subject_definitions','Identify each attached Picture or Audio by its actual index. Explain its role and the shots where it applies.'),('summary','Explain the scene purpose, duration, exact visible cast and planned shot progression.'),('retention_analysis','For each reference and applicable shot, specify what is fully or partly preserved and explain any approved differences.'),('detailed_description','Describe each pictured starting pose, specific action, gaze/expression change and end hold. State the planned camera move and measured hard cut.'),('overall_soundscape','Describe ambience and physical sounds; keep speech separate.'),('non_diegetic_music','Use N/A for no music, as specified by the official guide.')],[135,CW-135])
head('Select the scene-matched reference bundle')
text('Attach only visible character sheets, the matching environment and relevant props, then the storyboard. Empty inserts omit unrelated sheets. After a reviewed failure, use scene-specific references for the single allowed repair; reinspect the board and rebuild indexes. Preserve original jobs. Save ordered filenames, Picture indexes, roles and shot visibility. Dialogue retains its clean scene and accepted audio.')
head('Prevent additions before submitting')
text('Record the people, objects, positions, contact, lighting and empty background visible in each panel. Compare every person, object and movement in the final prompt with that inventory. Fix incompatible staging in the image first. Save this comparison as shot_inventory_match evidence tied to the actual image files.')
callout('<b>Example of precise action:</b> Exactly one person is visible, seated at frame right with the phone already in his hand. He lowers his gaze to its dark screen, blinks once and holds. His forearm stays supported on his thigh; the empty passage retains its pictured state. Camera fixed.')
text('New prompts use six headings; the runtime also reads legacy five-section records and requires the recorded inventory review; it cannot judge the pictures itself. Older animation approvals missing the new review or using the former format become stale before further submissions. Existing jobs and media remain preserved. Inspect the whole resulting video for added, duplicated or missing subjects, including during cuts.')
skills('starling-animation-pack and starling-verification. Full reusable template: starling-animation-pack/references/animation-template.md.')

page_start('Narration and speech rules','Updated 30 October 2026. These rules apply to new work; preserve accepted originals and paid-job history.')
head('Dialogue pronunciation input')
text('Keep canonical dialogue unchanged. Save a separate TTS input with the first 2-3 words transliterated into Hindi/Devanagari and the remaining words in Roman/English script. Do not translate, insert words or change meaning. Listen to the whole result for words and accent; retain both texts and their mapping.')
head('Listen before planning pictures')
text('Listen to the complete accepted narration and map every situation, action and B-roll beat to exact audio cues. Choose 1x2 or 1x3 by coverage and pacing. Use more boards if required; never omit a narrated situation to fit a panel count. Keep precise audio and assembly timing internally, with whole seconds on storyboard labels.')
head('Monochrome pictures and white labels')
text('Preserve the selected design style, identity, wardrobe and setting in black, white and grayscale only. Use white backgrounds for all action/camera labels with readable black text. No colour accents, white picture frames or grid gutters. Label camera direction, extent/speed and action clearly below each picture.')
head('Silent action during narration')
text('Prefer source-supported activity in side or three-quarter views, without back shots or speaking-to-camera poses. State in every shot that visible people are silent, their lips completely closed, with no speech-like mouth or jaw movement. Narration remains separate and is added during assembly.')
head('Official voiceover rule when speech is generated')
text('Only for explicitly requested generated voiceover, use <b>says in an off-screen voiceover</b> for every line. Inside &lt;d&gt; put only language and exact spoken words. Immediately after each block state that visible characters keep their lips closed. Use stable speaker IDs only for vocal sources; describe the voice on first use. Mark both sides of a cut with &lt;scenetrans&gt; for continuing speech. Inspect any rewritten prompt for these rules.')
text('Authority: MiniMaxAI/MiniMax-H3 on Hugging Face, docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md and docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md section 4.4. The reference route uses six sections; no music is non_diegetic_music: N/A.','small')

page_start('8  Submit collect and repair','All approved work can be submitted before reviewing the generated output, while duplicate protections remain in place.')
head('Submit all ready clips once')
text('Submit the complete approved set in an ordered pass, respecting provider capacity. Save a local intent before each tool call and the real provider job ID immediately afterward. If a call has an uncertain outcome, reconcile the known job instead of making another paid request blindly.')
head('Collect and account for every clip')
text('Poll known IDs during the active session. Save returned states and download completed videos to durable storage. Record unfinished jobs and explicit failures separately. A missing item in a partial response is not automatically a failed render. A download failure triggers another download, not another video generation.')
head('Review complete videos')
text('Review each downloaded clip immediately against every approved panel, including all motion, buffers and transitions. Flag extra/missing people or props, distorted bodies, wrong identity, invented movement and mixed panels. Record timestamps and visual verdict separately. The user checks lip-sync manually; pending sync does not trigger visual regeneration.')
head('Repair through EN2 and inspect again')
text('After an initial visual failure, redesign the scene once with simpler source-faithful staging, inspect fresh images and submit one EN2 Ultra replacement. If it also fails, stop for review. Preserve the logical clip ID, originals and all paid-job IDs.')
callout('<b>No still-image animation fallback.</b> Failed animation is not replaced with a slow zoom or still sequence. FFmpeg is retained for checking, trimming, stitching, original-audio handling and export.')
skills('starling-animation-monitor; starling-animation-pack; starling-verification; director/cinematography for their review checks.')

page_start('Buffered timing and visual checks','One timing plan drives the storyboard, animation prompt and final trim. The user owns manual lip-sync review.')
table(['Timing','Shot 1','Shot 2'],[('Required edit duration','3 seconds','3 seconds'),('Extra generated buffer','1 second','1 second'),('Printed and prompted range','0–4 seconds','4–8 seconds'),('Action then settled hold','Action 0–3; hold 3–4','Action 4–7; hold 7–8'),('Retained source span','[0,3]','[4,7]')],[160,(CW-160)/2,(CW-160)/2])
text('Generate 8 seconds with a hard cut exactly at 4 seconds. Keep 6 seconds for the edit, where the cut falls at 3 seconds. Never truncate only the end of the render: that would keep the first buffer and lose second-shot coverage. Original narration remains unchanged.')
head('Inspect every scene throughout motion')
text('The approved panel inventory controls visible content. Reference sheets provide appearance only. Check exact cast, props, anatomy, clothing, background, lighting, object state and supported movement. An extra character that appears only briefly is still a defect. Empty inserts stay empty. Check hard cuts and reject ghosting, dissolves, mixed panels and label leakage.')
head('Separate visual review from manual lip-sync')
text('Record visual_status and exact findings against the output hash. The user supplies the dialogue lip-sync verdict for that same version. A visual pass with manual sync pending is not a visual failure, but cannot be selected as fully verified dialogue. Missing complete-video inspection leaves visual review unverified.')
head('Bound the repair loop')
text('Within authorized production, one observed visual failure permits one source-faithful scene repair and EN2 replacement. Inspect fresh inputs, preserve paid IDs and recheck the entire new render. A second visual failure stops for user review. Instructions alone do not install an unattended reviewer or active schedule.')
skills('Shared authority: starling-animation-pack/references/timing-and-visual-review.md. Assembly supports ordered narration source_spans.')

page_start('9  Stitch and export','Only accepted EN2 videos are selected for the finished story nodes.')
head('Join pictures in the script order')
text('The assembly plan names each story node, its ordered clips, exact boundaries and original audio units. The code checks that all required clips are present, approved and unchanged. A clip-ID mismatch stops the handoff so footage is not silently skipped.')
head('Add the original accepted audio')
text('Before stitching narration and establishing clips, discard generated sound, background voices and subtitle tracks; use approved narration only. Unwanted text burned into the picture requires correction and review before assembly. Dialogue keeps its clean-scene generation and verified embedded speech.')
text('Output is 1280 x 720 at 30 fps, scaled to fill and centrally cropped; inspect edge content. Assembly blocks an interval shorter than the selected dialogue. Extend that interval and shift following clips/audio units before retrying. Audio units must align with dialogue boundaries. Complete listening still establishes that the generated source contains every word. Audio is encoded once. Ordered source_spans trim narration shot buffers; dialogue spans are rejected. Extra music mixing and external-audio offsets remain unsupported.')
head('Review the assembled result')
bullets(['Check complete picture and sound, every spoken word and pause, the user’s manual dialogue-sync verdict and the joins between clips.','Check every required branch. A correct-path review does not approve the alternative outcomes.','Keep mutually exclusive outcomes in separate node videos. Player choices and retries remain in the script graph.'])
callout('<b>Final package:</b> separate node MP4s, canonical script with choices, assembly plan, final review records, selected-output provenance and a README. Packaging does not publish an external player.')
skills('starling-animation-pack; starling-verification. Local implementation: pipeline/postproduction.py and FFmpeg.')

page_start('10  Where outputs are stored','The workspace keeps each production in its own project directory. The names below describe the current implementation and its recommended organization.')
text('<b>Workspace:</b> C:\\Users\\darsh\\Downloads\\roleplay<br/><b>Project root:</b> projects/&lt;project-name&gt;/')
tree=[
'projects/<project-name>/',
'  intake.json',
'  canonical-script.json',
'  pipeline.sqlite3',
'  source/                 [recommended source snapshots]',
'  script/                 [chosen builder output folder]',
'    script.docx',
'    script.json',
'  audio/',
'    audio_manifest.json',
'    ...original files, excerpts and cues',
'  visuals/',
'    image_manifest.json',
'    ...assets, boards, scenes and image reviews',
'  animation/',
'    animation-manifest.json',
'    assembly-plan.json',
'    ...prompts, payloads and upload evidence',
'  postproduction/',
'    state.sqlite3',
'    automation.json',
'    download-handoff.json',
'    raw/<provider-id>.mp4',
'    review/<clip-id>-<hash>/review.json',
'    edited/<node-id>-<version>/<node-id>.mp4',
'    edited/<node-id>-<version>/review.json',
'    delivery-manifest.json',
'    <project-name>-final.zip']
for line in tree:text(html.escape(line).replace(' ','&nbsp;'),'mono') if False else None
obj=Paragraph('<br/>'.join(html.escape(line).replace(' ','&nbsp;') for line in tree),styles['mono']);_,hh=obj.wrap(CW,1000);assert y-hh>90;obj.drawOn(c,M,y-hh);y-=hh+18
text('Folders marked recommended or chosen are organization conventions, not automatically created source-retrieval folders. Manifest and postproduction filenames shown above are used by the current code. Existing productions may retain additional version folders.','small')
text('Google Docs stores a native script copy remotely. Its actual returned ID/URL and a local readback record are preserved with the project. Media is downloaded locally rather than relying only on temporary provider URLs.','small')

page_start('11  What each saved record means','Most records are small files that let the workflow resume accurately without repeating paid work.')
table(['Saved item','Purpose'],[('intake.json','Source mode, style and voice answers, selected speaker mappings and supporting evidence.'),('canonical-script.json','The approved words and story graph used by all production stages.'),('audio/audio_manifest.json','Which recording belongs to which line/speaker, its duration and measured source cues.'),('visuals/image_manifest.json','Approved assets and images, versions, panel geometry, references and review information.'),('animation/animation-manifest.json','Clip inventory, approved inputs, content type, used duration and explicit runtime clip mapping.'),('animation/assembly-plan.json','Ordered clips and original audio units for each final node.'),('pipeline.sqlite3','Durable stage scopes, acceptance receipts, render intents, provider IDs and event history.'),('postproduction/state.sqlite3','Downloaded outputs, reviewed selections and assembled-node versions.'),('Review files','Who inspected which exact version, what was checked, observations and verdicts.'),('delivery-manifest.json','Which accepted outputs were selected for the final package.')],[175,CW-175])
text('A file fingerprint (SHA-256) detects changed bytes. If a source or accepted file changes, affected approval must be revisited. A fingerprint does not prove that the image or video is correct.','small')
text('Provider responses and original media are preserved. Updating a skill does not rewrite an already submitted job or automatically migrate an older project into a new clip layout.','small')

page_start('12  Connections and local tools','MCP is the connection that lets the active assistant call an external service. It is not a background process by itself.')
table(['Connection or tool','What it does','Where the result lives'],[('Starling MCP','Retrieves the selected roleplay structure and available visual references.','Original source remains in Starling; snapshots and downloaded references are local.'),('ElevenLabs MCP','Resolves selected voices and generates speech with eleven_v3.','Real job IDs and downloaded audio stay with the project.'),('Native ChatGPT images','Generates/edits foundational assets, storyboards and dialogue scenes.','Actual images and review records are saved locally.'),('EN2 video MCP','Uploads references, submits Ultra reference-video jobs and retrieves job states/results.','Real job IDs are recorded; video files are downloaded locally.'),('Google Drive / Google Docs','Stores a native script copy under the confirmed darshan@en2.ai connection.','Native document in Google Docs; real ID/URL and readback stored locally.'),('FFmpeg and ffprobe','Check media, normalize/trim clips, join audio/video and export final nodes.','Local files under postproduction.'),('Python and SQLite','Validate records, preserve progress and create the next handoff.','Local code and project databases.')],[113,192,CW-305])
text('The workflow uses these selected providers. It does not silently switch image/video generation to another service. Live tool names, schemas and limits must be checked when production is executed.','small')
text('This report describes the implemented integration design; it is not a new live connectivity or account-access test. Native image generation and local FFmpeg are distinct from the external MCP services.','small')

page_start('13  How the workflow is built','The system has three layers: written specialist instructions, saved project state and connected execution.')
head('Skills explain the work')
text('A SKILL.md tells the assistant what a specialist stage owns, which inputs it needs and what must be checked. Shared references hold rules used by several stages, such as intake, two/three-shot storyboard geometry and physical/spatial review. This keeps the individual skills short and consistent.')
head('Runtime records enforce the handoffs')
text('pipeline/runtime.py records the expected inventory for each stage and accepts a receipt only when its required evidence and file fingerprints are present. It saves an intent before a video request and the returned provider ID afterward. This helps avoid duplicate paid submissions and detects changed source files.')
text('pipeline/postproduction.py connects scoped jobs to the assembly plan, records downloaded clips and reviews, selects accepted EN2 outputs, assembles nodes and checks final-package gates. It calls local FFmpeg; it does not run MCP calls.')
head('The active session performs connected actions')
text('The assistant reads the relevant skill, uses the connected tool, saves the actual result and records evidence. A Python command can issue the next handoff, but cannot independently fetch from the assistant’s MCP connections or claim that a video has been watched.')
table(['Term','Simple meaning'],[('Scope','The exact list of items expected in a stage.'),('Receipt','A saved approval record tied to exact files and checks.'),('Manifest','An inventory and mapping of related production files.'),('Intent / provider ID','The local record before submission / the service’s actual returned job identifier.'),('Verified','Required review is complete for that exact version and scope.')],[123,CW-123])

page_start('14  Skill map and supporting files','Each separate Word document contains the complete current source of the named workflow skill.')
table(['Stage or responsibility','Skill document'],[('Overall orchestration and mandatory intake','starling-production-master.docx'),('Source retrieval and canonical script','starling-script-rebuilder.docx'),('Selected voices, speech and measured cues','starling-audio-pack.docx'),('Beat mapping and image prompts','starling-prompt-pack.docx'),('Meaning, staging and action continuity','starling-director.docx'),('Framing, geometry and spatial relationships','starling-cinematography.docx'),('Image generation and durable outputs','starling-image-pack-generator.docx'),('Detailed still/panel checking and repair','starling-panel-corrector.docx'),('Animation prompts, EN2 repairs and stitching','starling-animation-pack.docx'),('Job reconciliation and output collection','starling-animation-monitor.docx'),('Evidence-based still/video/final review','starling-verification.docx')],[228,CW-228])
head('Additional files that support those skills')
text('pipeline/INTAKE.md defines the required questions. WORKFLOW.md and POSTPRODUCTION.md explain operation and acceptance. narration-pairs.md and visual-routing.md define the two/three-shot route. spatial-fidelity.md defines general physical checks. scene-preservation.md and en2-submission.md govern animation handoff. handoff-contract.md and review-record.md define saved evidence.')
text('The installed Script Rebuilder also includes references/data-contract.md, references/intake.md and scripts/build_script.py. The script skill is installed under the personal skill catalog; the other ten workflow skills live in the roleplay workspace.','small')

page_start('15  Checks limits and final delivery','The workflow has implemented safeguards, but saved instructions alone do not make production unattended.')
head('What has been tested')
text('The current workflow passed 48 offline pipeline, intake and postproduction tests; current results are recorded separately in docs/validation.json. Coverage includes narration reference routing, preserved historical records, duplicate prevention, review gates, embedded-dialogue audio, rejection of short dialogue intervals and synthetic mixed-audio assembly and per-shot buffer trimming. These results do not approve production media.')
head('What those tests do not prove')
text('Synthetic tests do not certify pronunciation, character identity, believable movement or lip-sync in real production. Complete listening and picture/sound inspection remain required. A structural audit checks current skill frontmatter, reference links and documentation source hashes.')
head('Current operational limits')
bullets(['No persistent background runner is active. Collection through MCP needs an active session unless a supported runner is separately demonstrated.','Full audiovisual review capability must be established for the actual files. A completed render or contact sheet is not enough.','Older project manifests and clip mappings need explicit reconciliation before adopting the new workflow. Existing media and paid IDs remain preserved.','The assembler uses external narration and embedded dialogue audio at 720p/30 fps. It does not mix additional ambience/music.'])
callout('<b>Delivery is complete only when:</b> all required nodes and branches are present, their selected EN2 clips and final picture/sound pass review, original speech is intact, joins are checked, runtime receipts pass and the final ZIP is verified.')
text('This PDF explains the current workflow as recorded on 30 October 2026. Its companion Word files reproduce the current skill instructions for manual checking. No new production run, publication or live monitoring is implied.','small')
c.save()

order=['starling-production-master','starling-script-rebuilder','starling-audio-pack','starling-prompt-pack','starling-director','starling-cinematography','starling-image-pack-generator','starling-panel-corrector','starling-animation-pack','starling-animation-monitor','starling-verification']
docs=[]
for i,name in enumerate(order,1):
    src=ROOT/name/'SKILL.md'
    if name=='starling-script-rebuilder' and not src.exists(): src=Path.home()/'.codex/skills'/name/'SKILL.md'
    data=src.read_bytes();content=data.decode('utf-8-sig')
    docs.append({'name':name,'title':name.replace('-',' ').title(),'source':str(src),'sha256':hashlib.sha256(data).hexdigest(),'content':content,'shared_contract':'\n\n'.join((ROOT/'starling-animation-pack/references'/ref).read_text(encoding='utf-8') for ref in (['timing-and-visual-review.md','narration-pairs.md','animation-template.md'] if name == 'starling-animation-pack' else ['timing-and-visual-review.md','narration-pairs.md'])) if name not in ('starling-script-rebuilder','starling-audio-pack') else '', 'output':str(OUT/'skill-documents'/(name+'.docx')),'render':str(QA/(name+'.pdf'))})
(QA/'word-inputs.json').write_text(json.dumps(docs,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'source-index.json').write_text(json.dumps([{k:v for k,v in d.items() if k not in ('content','shared_contract')} for d in docs],indent=2),encoding='utf-8')
(QA/'report-pages.json').write_text(json.dumps(log,indent=2))
print(json.dumps({'pdf':str(OUT/'Starling_Workflow_Explained.pdf'),'pages':page,'skill_documents':len(docs)},indent=2))

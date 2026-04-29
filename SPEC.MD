# Integration Plan: Local Tools with Director Framework (VideoDB Fallback)

## Overview
The task is to modify the Director framework to prioritize local open-source tools (yt-dlp, Edit Mind, Whishper, FFmpeg) for video processing tasks (download, highlight analysis, translation, subtitles, formatting for TikTok/YouTube Shorts), while maintaining VideoDB as an optional fallback. This allows local operation on low-end hardware (i5 4th gen, 8GB RAM, 2GB NVIDIA 840M GPU, 200GB storage) for privacy and cost, with cloud fallback for heavier tasks. The integration will involve creating/modifying agents, tools, and configs in Director's backend.

## Goals
- Enable natural language commands in Director to use local tools by default.
- Keep VideoDB connection intact for selective use (e.g., via config toggle).
- Support user's use cases: YouTube downloads, viral highlights detection, language translation, automatic subtitles, and video formatting/generation.
- Ensure local processing works within hardware constraints (e.g., 1-2 videos at a time, slow but functional).
- Maintain Director's chat-based UI and reasoning engine.

## Requirements
### Hardware/Software
- Existing: Python 3.9+, Node.js, Director repo cloned.
- New: yt-dlp, Docker (for Edit Mind, Whishper), FFmpeg.
- GPU: NVIDIA 840M (2GB VRAM) for light acceleration; fallback to CPU.
- Storage: 200GB+ for videos/metadata.

### Functional
- Config toggle (USE_LOCAL_TOOLS) in .env to switch modes.
- New/Modified Agents: LocalVideoAgent for core workflow.
- New Tools: LocalVideoTool wrapper for yt-dlp, etc.
- Fallback: VideoDBTool remains for cloud tasks.
- Output: Processed videos, highlights, subtitles, formatted clips.

### Non-Functional
- Performance: <2hrs per video on hardware.
- Privacy: All local processing.
- Extensibility: Easy to add more tools.

## Detailed Steps
1. **Setup Local Tools**:
   - Install yt-dlp: `pip install yt-dlp`.
   - Install Docker and run Whishper: `docker run -p 3000:3000 pluja/whishper`.
   - Install Edit Mind: Clone repo, `docker-compose up`.
   - Install FFmpeg: Download from ffmpeg.org, add to PATH.
   - Verify: Test each tool with sample video (e.g., yt-dlp download, Whishper transcription).

2. **Create Local Tool Wrapper**:
   - File: `backend/director/tools/local_video_tool.py`.
   - Methods: download_video(), extract_highlights(), generate_subtitles(), format_video().
   - Use subprocess for CLI tools, requests for APIs (e.g., Whishper if exposed).

3. **Create/Modify Agent**:
   - File: `backend/director/agents/local_video_agent.py` (based on sample_agent.py).
   - Add conditional logic: If USE_LOCAL_TOOLS=true, use LocalVideoTool; else VideoDBTool.
   - Implement run(): Download -> Analyze -> Subtitle/Translate -> Format.
   - Handle progress: Use output_message.actions for updates.

4. **Update Handler and Config**:
   - File: `backend/director/handler.py`: Register LocalVideoAgent.
   - File: `backend/.env`: Add USE_LOCAL_TOOLS=true.
   - Ensure VideoDB config remains.

5. **Test Integration**:
   - Run Director: `make run`.
   - Input commands: "Download https://youtube.com/... and find highlights with Spanish subtitles, format for TikTok."
   - Verify output: Check logs, generated files.
   - Toggle to VideoDB: Change .env, restart, test fallback.

6. **Handle Errors and Optimization**:
   - Add try/except for hardware limits (e.g., GPU OOM).
   - Optimize: Process in batches, use GPU where possible.
   - Document: Update README with local setup.

## Dependencies
- Director backend (Python, asyncio).
- Local tools' APIs/CLI stability.
- Hardware: May require RAM/GPU upgrades if slow.
- User: Basic Python/Docker knowledge for setup.

## Risks and Mitigations
- **Hardware Bottleneck**: Slow processing. Mitigation: Limit to 1 video, add progress indicators.
- **Tool Incompatibilities**: APIs change. Mitigation: Pin versions, test thoroughly.
- **VideoDB Removal**: Accidental breakage. Mitigation: Keep separate branches.
- **Security**: Local tools expose ports. Mitigation: Run in isolated containers.
- **Scope Creep**: Full AI generation too heavy. Mitigation: Focus on transcription/formatting; note limitations.

## Timeline
- Phase 1 (Setup): 1-2 days (install tools, test).
- Phase 2 (Coding): 3-5 days (create files, integrate).
- Phase 3 (Testing): 2-3 days (end-to-end, toggle modes).
- Total: 1-2 weeks, depending on debugging.

## Appendix: Video Moment Types for Highlights

Videos can be broken down into several distinct moments or structural elements, depending on whether you're analyzing them for storytelling, editing, marketing, or AI video understanding. The local highlight detection (Edit Mind, Whishper) and the LocalVideoAgent should target these moment types when analyzing videos for viral clips, TikTok/Shorts formatting, and general highlight extraction.

### 1. Narrative Moments
These drive the story or message forward:

- **Inciting Incident**: The event that kicks off the story.
- **Turning Points**: Moments where the direction of the plot changes.
- **Climax**: The peak of tension or emotional intensity.
- **Resolution**: How the story concludes or wraps up loose ends.

### 2. Emotional Beats
Moments designed to evoke specific feelings:

- **Humor**: Jokes, funny visuals, or comedic timing.
- **Tension**: Suspenseful scenes that build anxiety.
- **Empathy**: Scenes that make the viewer connect emotionally with characters.
- **Triumph**: Moments of victory or success.

### 3. Visual & Audio Highlights
Distinct sensory moments:

- **Establishing Shots**: Wide shots that set the scene or location.
- **Close-ups**: Focus on facial expressions or important details.
- **Slow Motion**: Used to emphasize a critical or dramatic moment.
- **Sound Drops**: Sudden silence or a powerful musical swell to heighten impact.

### 4. Action & Movement
Physical events occurring in the frame:

- **Transitions**: Cuts, dissolves, or wipes that move between scenes.
- **Camera Movements**: Pans, tilts, dolly shots, or tracking shots.
- **Physical Actions**: Stunts, fights, or specific choreographed movements.

### 5. Informational Moments
Common in tutorials, news, or documentaries:

- **Callouts**: Text overlays or graphics highlighting key data.
- **Demonstrations**: Showing "how-to" steps in real-time.
- **Interviews**: Direct quotes or expert opinions.
- **Call to Action (CTA)**: The moment asking the viewer to subscribe, buy, or visit a link.

### 6. Technical Moments
Often used by editors and AI models:

- **Scene Cuts**: The exact frame where one scene ends and another begins.
- **Shot Changes**: Shifts in camera angle or focal length within a scene.
- **Silence Pauses**: Intentional gaps in audio for dramatic effect.

### Mapping to Tools and Agents

| Moment Type | Primary Detection Tool | Use Case |
|---|---|---|
| Narrative Moments | Edit Mind (semantic search + Whisper transcription) | Highlight extraction, story-based clipping |
| Emotional Beats | Edit Mind (DeepFace for expressions) + Whisper (tone analysis) | Viral clip detection, engagement scoring |
| Visual & Audio Highlights | Edit Mind (YOLO for objects, scene detection) + FFmpeg (slow-mo detection) | Cinematic clips, attention-grabbing moments |
| Action & Movement | Edit Mind (YOLO for objects/movement) + FFmpeg (motion analysis) | Action compilations, dynamic Shorts |
| Informational Moments | Whisper (transcription) + Edit Mind (OCR/text detection) | Tutorial clips, how-to Shorts, quote extraction |
| Technical Moments | FFmpeg (scene cut detection: `-f lavfi -i "select=gt(scene\,0.3)"`) + Edit Mind | Edit decision lists, chapter markers, precise clipping |

### Integration Notes
- The `LocalVideoAgent` should accept a `moment_types` parameter (e.g., `["emotional_beats", "action_movement"]`) to filter which moment categories to detect.
- Default for "viral TikTok highlights" should prioritize: **Emotional Beats** (humor, triumph) and **Action & Movement** (physical actions, camera movements).
- For tutorial/educational content, prioritize: **Informational Moments** (demonstrations, callouts).
- The `extract_highlights()` method in `LocalVideoTool` should accept and pass `moment_types` to Edit Mind's API or FFmpeg filters.

## Questions for User
- Do you want to support video generation locally (e.g., via scripts), or stick to editing/formatting?
- Any specific languages for translation (e.g., English to Spanish)?
- Should the agent handle multiple videos in parallel, or sequentially?</content>
<parameter name="filePath">C:\Users\ASUS PC\Desktop\Projects\Director\.kilo\plans\1776789057307-lucky-cabin.md
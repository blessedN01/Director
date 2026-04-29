"""Local video processing tool wrapping yt-dlp, FFmpeg, Whishper, and Edit Mind."""

import os
import subprocess
import requests
import logging
from typing import Any, Dict, List, Optional

from director.constants import DOWNLOADS_PATH

logger = logging.getLogger(__name__)

_FORMAT_SUFFIX = {
    "tiktok": "_tiktok",
    "youtube_shorts": "_shorts",
}


class LocalVideoTool:
    def __init__(self):
        self.downloads_path = os.getenv("LOCAL_DOWNLOADS_PATH", DOWNLOADS_PATH)
        os.makedirs(self.downloads_path, exist_ok=True)

    def _format_timestamp(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def download_video(self, url: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        if not url or not isinstance(url, str):
            return {
                "success": False,
                "error": "Invalid URL provided",
                "message": "URL must be a non-empty string",
            }

        if not output_path:
            output_path = os.path.join(self.downloads_path, "%(title)s.%(ext)s")

        try:
            cmd = [
                "yt-dlp",
                "--output", output_path,
                "--print", "after_move:%(filepath)s",
                url,
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
                timeout=300,
            )

            lines = result.stdout.strip().split("\n")
            file_path = None
            for line in lines:
                if line.startswith("after_move:"):
                    file_path = line.split("after_move:", 1)[1].strip()
                    break
            if not file_path or not os.path.exists(file_path):
                raise Exception("Could not determine downloaded file path")

            return {
                "success": True,
                "file_path": file_path,
                "message": "Video downloaded successfully",
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"yt-dlp download failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to download video",
            }
        except subprocess.TimeoutExpired:
            logger.error("yt-dlp download timed out")
            return {
                "success": False,
                "error": "Download timed out",
                "message": "Video download timed out after 300 seconds",
            }

    def extract_highlights(self, video_path: str, moment_types: Optional[List[str]] = None) -> Dict[str, Any]:
        if not video_path or not os.path.exists(video_path):
            return {
                "success": False,
                "error": "Video file not found",
                "message": f"Video file does not exist: {video_path}",
            }

        if not moment_types:
            moment_types = ["emotional_beats", "action_movement"]

        try:
            edit_mind_url = os.getenv("EDIT_MIND_URL")
            if edit_mind_url:
                logger.warning(
                    "EDIT_MIND_URL is configured but Edit Mind integration is not yet "
                    "implemented. Falling back to FFmpeg scene detection. "
                    "Remove EDIT_MIND_URL from your environment if this is unintended."
                )

            # FFmpeg scene detection filter.
            # The double-backslash produces a single backslash in the argument string,
            # which is the required escaping for FFmpeg's filter parser when invoked
            # via subprocess (non-shell) mode: select=gt(scene\,0.3)
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vf", "select=gt(scene\\,0.3)",
                "-f", "null",
                "-",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            highlights = []
            for line in result.stderr.split("\n"):
                if "st:" in line:
                    parts = line.split("st:")
                    if len(parts) > 1:
                        try:
                            timestamp = float(parts[1].split()[0])
                            moment_type = (
                                "emotional_beats"
                                if "emotional_beats" in moment_types
                                else moment_types[0]
                                if moment_types
                                else "scene_change"
                            )
                            highlights.append(
                                {
                                    "timestamp": timestamp,
                                    "type": moment_type,
                                    "description": f"Scene change at {timestamp:.2f}s",
                                }
                            )
                        except (ValueError, IndexError):
                            continue

            return {
                "success": True,
                "highlights": highlights,
                "message": f"Extracted {len(highlights)} highlights using FFmpeg scene detection",
            }
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg scene detection timed out")
            return {
                "success": False,
                "error": "Timeout during scene detection",
                "message": "Highlights extraction timed out",
            }
        except Exception as e:
            logger.error(f"Highlights extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to extract highlights",
            }

    def generate_subtitles(self, video_path: str, language: str = "en") -> Dict[str, Any]:
        if not video_path or not os.path.exists(video_path):
            return {
                "success": False,
                "error": "Video file not found",
                "message": f"Video file does not exist: {video_path}",
            }

        if not language or not isinstance(language, str):
            language = "en"

        try:
            whishper_url = os.getenv("WHISHPER_URL", "http://localhost:3000")

            # Extract audio via FFmpeg first — Whishper expects audio, not full video.
            # This also dramatically reduces upload size and processing time.
            # Use the downloads directory for the temp audio file to avoid
            # write-permission issues if the video is in a read-only location.
            base_name = os.path.basename(video_path).rsplit(".", 1)[0]
            audio_path = os.path.join(self.downloads_path, f"{base_name}_audio.wav")
            extract_cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vn",
                "-acodec", "pcm_s16le",
                "-ar", "16000",
                "-ac", "1",
                "-y",
                audio_path,
            ]
            subprocess.run(extract_cmd, check=True, capture_output=True, text=True, timeout=120)

            try:
                with open(audio_path, "rb") as f:
                    files = {"file": f}
                    data = {"language": language}
                    response = requests.post(
                        f"{whishper_url}/transcribe",
                        files=files,
                        data=data,
                        timeout=600,
                    )
                    response.raise_for_status()
                result = response.json()
            finally:
                if os.path.exists(audio_path):
                    os.remove(audio_path)

            subtitle_path = video_path.rsplit(".", 1)[0] + ".srt"
            with open(subtitle_path, "w", encoding="utf-8") as f:
                segments = result.get("segments", [])
                if segments:
                    for i, segment in enumerate(segments, 1):
                        start_time = self._format_timestamp(segment["start"])
                        end_time = self._format_timestamp(segment["end"])
                        text = segment["text"].strip()
                        f.write(f"{i}\n{start_time} --> {end_time}\n{text}\n\n")
                else:
                    text = result.get("text", "")
                    f.write(f"1\n00:00:00,000 --> 00:01:00,000\n{text}\n")

            return {
                "success": True,
                "subtitle_path": subtitle_path,
                "message": "Subtitles generated successfully",
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Audio extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to extract audio for transcription",
            }
        except subprocess.TimeoutExpired:
            logger.error("Audio extraction timed out")
            return {
                "success": False,
                "error": "Audio extraction timed out",
                "message": "Timed out while extracting audio from video",
            }
        except requests.exceptions.Timeout:
            logger.error("Whishper transcription request timed out")
            return {
                "success": False,
                "error": "Transcription request timed out",
                "message": "Whishper transcription timed out",
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Whishper transcription request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to connect to Whishper for transcription",
            }
        except Exception as e:
            logger.error(f"Subtitle generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate subtitles",
            }

    def format_video(
        self,
        video_path: str,
        format_type: str = "tiktok",
        highlights: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        if not video_path or not os.path.exists(video_path):
            return {
                "success": False,
                "error": "Video file not found",
                "message": f"Video file does not exist: {video_path}",
            }

        if format_type not in _FORMAT_SUFFIX:
            return {
                "success": False,
                "error": "Unsupported format type",
                "message": (
                    f"Format type '{format_type}' not supported. "
                    f"Use one of: {', '.join(_FORMAT_SUFFIX.keys())}"
                ),
            }

        try:
            base_name = os.path.basename(video_path).rsplit(".", 1)[0]
            output_path = os.path.join(
                self.downloads_path,
                f"{base_name}{_FORMAT_SUFFIX[format_type]}.mp4",
            )

            # Determine start time and duration for clipping.
            # If highlights are provided, clip around the first highlight;
            # otherwise fall back to the beginning of the video.
            max_duration = 60
            if highlights:
                ts = highlights[0].get("timestamp", 0)
                # Start 5s before the highlight, but never before 0.
                # For early highlights, just start from the beginning.
                start_time = max(0, ts - 5) if ts > 5 else 0
            else:
                start_time = 0

            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-ss", str(start_time),
                "-t", str(max_duration),
                "-vf",
                "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2",
                "-c:v", "libx264",
                "-c:a", "aac",
                "-y",
                output_path,
            ]
            subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=300)

            return {
                "success": True,
                "output_path": output_path,
                "start_time": start_time,
                "duration": max_duration,
                "message": f"Video formatted for {format_type} successfully",
            }
        except subprocess.TimeoutExpired:
            logger.error("Video formatting timed out")
            return {
                "success": False,
                "error": "Video formatting timed out",
                "message": "FFmpeg formatting timed out after 300 seconds",
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Video formatting failed: {e}")
            stderr = e.stderr or ""
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to format video: {stderr[:200]}",
            }

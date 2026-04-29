"""Local VideoDB implementation using SQLite, OpenAI-compatible APIs, and local file storage."""

import os
import json
import time
import uuid
import logging
import sqlite3
import subprocess
import shutil
import base64
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import requests
from openai import OpenAI

from director.constants import DOWNLOADS_PATH
from director.tools.manual.local_video_tool import LocalVideoTool
from director.tools.ai.local_ai_client import LocalAIClient
from director.tools.ai.editmind_wrapper import EditMindWrapper

logger = logging.getLogger(__name__)


class LocalVideoDBTool:
    """Local implementation of VideoDB features using SQLite and OpenAI-compatible APIs."""

    def __init__(self, collection_id: str = "default", db_path: str = "director.db"):
        self.collection_id = collection_id
        self.db_path = db_path
        self.local_video_tool = LocalVideoTool()

        # Initialize AI client
        try:
            self.ai_client = LocalAIClient()
        except ValueError as e:
            logger.warning(f"AI client initialization failed: {e}. AI features will be unavailable.")
            self.ai_client = None

        # Initialize EditMind wrapper
        try:
            self.editmind_wrapper = EditMindWrapper()
        except Exception as e:
            logger.warning(f"EditMind wrapper initialization failed: {e}. EditMind features will be unavailable.")
            self.editmind_wrapper = None

        # Ensure database is initialized
        self._init_db()

        # Ensure collection exists
        self._ensure_collection()

    def _init_db(self):
        """Initialize database connection."""
        from director.db.sqlite.initialize import initialize_sqlite
        initialize_sqlite(self.db_path)

    def _get_db_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)

    def _ensure_collection(self):
        """Ensure the collection exists."""
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM collections WHERE id = ?",
                (self.collection_id,)
            )
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO collections (id, name, description, created_at, updated_at, metadata) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        self.collection_id,
                        self.collection_id,
                        f"Local collection: {self.collection_id}",
                        int(time.time()),
                        int(time.time()),
                        json.dumps({})
                    )
                )
                conn.commit()
                logger.info(f"Created collection: {self.collection_id}")
        finally:
            conn.close()

    def get_collection(self) -> Dict[str, Any]:
        """Get collection information."""
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, description, created_at, updated_at, metadata FROM collections WHERE id = ?",
                (self.collection_id,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Collection {self.collection_id} not found")

            return {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "created_at": row[3],
                "updated_at": row[4],
                "metadata": json.loads(row[5]) if row[5] else {}
            }
        finally:
            conn.close()

    def get_collections(self) -> List[Dict[str, Any]]:
        """Get all collections."""
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, description, created_at, updated_at, metadata FROM collections"
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "created_at": row[3],
                    "updated_at": row[4],
                    "metadata": json.loads(row[5]) if row[5] else {}
                }
                for row in rows
            ]
        finally:
            conn.close()

    def create_collection(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new collection."""
        collection_id = str(uuid.uuid4())
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO collections (id, name, description, created_at, updated_at, metadata) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    collection_id,
                    name,
                    description,
                    int(time.time()),
                    int(time.time()),
                    json.dumps({})
                )
            )
            conn.commit()
            return {
                "success": True,
                "message": f"Collection '{collection_id}' created successfully",
                "collection": {
                    "id": collection_id,
                    "name": name,
                    "description": description,
                },
            }
        except Exception as e:
            logger.error(f"Failed to create collection '{name}': {e}")
            raise Exception(f"Failed to create collection '{name}': {str(e)}")
        finally:
            conn.close()

    def delete_collection(self) -> Dict[str, Any]:
        """Delete the current collection."""
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM collections WHERE id = ?", (self.collection_id,))
            conn.commit()
            return {
                "success": True,
                "message": f"Collection {self.collection_id} deleted successfully",
            }
        except Exception as e:
            raise Exception(f"Failed to delete collection {self.collection_id}: {str(e)}")
        finally:
            conn.close()

    def _extract_file_metadata(self, file_path: str, media_type: str) -> Dict[str, Any]:
        """Extract comprehensive metadata from media file."""
        metadata = {
            "file_size": os.path.getsize(file_path),
            "file_extension": os.path.splitext(file_path)[1].lower(),
            "created_time": os.path.getctime(file_path),
            "modified_time": os.path.getmtime(file_path),
        }

        if media_type in ["video", "audio"]:
            try:
                import subprocess
                result = subprocess.run([
                    "ffprobe", "-v", "quiet", "-print_format", "json",
                    "-show_format", "-show_streams", file_path
                ], capture_output=True, text=True, timeout=10)

                if result.returncode == 0:
                    probe_data = json.loads(result.stdout)
                    format_info = probe_data.get("format", {})

                    # Format-level metadata
                    metadata.update({
                        "duration": float(format_info.get("duration", 0)),
                        "bit_rate": format_info.get("bit_rate"),
                        "format_name": format_info.get("format_name"),
                        "format_long_name": format_info.get("format_long_name"),
                        "size_bytes": int(format_info.get("size", 0)),
                        "tags": format_info.get("tags", {}),
                    })

                    # Stream-specific metadata
                    streams = probe_data.get("streams", [])
                    for stream in streams:
                        stream_type = stream.get("codec_type")
                        if stream_type == "video" and media_type == "video":
                            metadata["video"] = {
                                "width": stream.get("width"),
                                "height": stream.get("height"),
                                "codec": stream.get("codec_name"),
                                "codec_long_name": stream.get("codec_long_name"),
                                "pixel_format": stream.get("pix_fmt"),
                                "frame_rate": stream.get("r_frame_rate"),
                                "duration": float(stream.get("duration", 0)),
                                "bit_rate": stream.get("bit_rate"),
                                "aspect_ratio": stream.get("display_aspect_ratio"),
                            }
                        elif stream_type == "audio":
                            if "audio" not in metadata:
                                metadata["audio"] = []
                            metadata["audio"].append({
                                "codec": stream.get("codec_name"),
                                "channels": stream.get("channels"),
                                "sample_rate": stream.get("sample_rate"),
                                "bit_rate": stream.get("bit_rate"),
                                "language": stream.get("tags", {}).get("language"),
                            })

            except subprocess.TimeoutExpired:
                logger.warning(f"ffprobe timeout for {file_path}")
            except Exception as e:
                logger.warning(f"Failed to extract media metadata from {file_path}: {e}")

        return metadata

    def _organize_file_path(self, collection_id: str, asset_id: str, filename: str) -> str:
        """Organize file path with collection structure."""
        # Create collection-specific directory
        collection_dir = os.path.join(DOWNLOADS_PATH, "collections", collection_id)
        os.makedirs(collection_dir, exist_ok=True)

        # Generate organized filename
        name_part, ext = os.path.splitext(filename)
        organized_filename = f"{asset_id}_{name_part}{ext}"
        return os.path.join(collection_dir, organized_filename)

    def upload(self, source: str, source_type: str = "url", media_type: str = "video", name: Optional[str] = None) -> Dict[str, Any]:
        """Upload media to local storage with organized file structure."""
        asset_id = str(uuid.uuid4())

        # Download or copy the file
        temp_file_path = None
        if source_type == "url":
            # Use yt-dlp for downloading
            download_result = self.local_video_tool.download_video(source, name=name)
            if not download_result["success"]:
                raise Exception(f"Download failed: {download_result.get('error', 'Unknown error')}")
            temp_file_path = download_result["file_path"]
        elif source_type == "file":
            # Use source as-is if it's already a local file
            if not os.path.exists(source):
                raise Exception(f"Source file does not exist: {source}")
            temp_file_path = source
        else:
            # Assume it's already a local path
            temp_file_path = source

        # Extract metadata
        metadata = self._extract_file_metadata(temp_file_path, media_type)
        metadata.update({
            "source": source,
            "source_type": source_type,
            "upload_timestamp": int(time.time()),
        })

        # Determine final filename and move to organized location
        original_filename = name or os.path.basename(temp_file_path)
        final_file_path = self._organize_file_path(self.collection_id, asset_id, original_filename)

        # Move file to final location (or copy if it's from a different location)
        if temp_file_path != final_file_path:
            import shutil
            shutil.move(temp_file_path, final_file_path)

        # Save to database
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO assets (id, collection_id, name, asset_type, file_path, url, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    asset_id,
                    self.collection_id,
                    original_filename,
                    media_type,
                    final_file_path,
                    None,  # No URL for local files
                    json.dumps(metadata),
                    int(time.time()),
                    int(time.time())
                )
            )
            conn.commit()

            # Return asset info in VideoDB-compatible format
            return {
                "id": asset_id,
                "collection_id": self.collection_id,
                "name": original_filename,
                "file_path": final_file_path,
                "metadata": metadata,
                "length": metadata.get("duration", 0),
                "type": media_type,
            }
        finally:
            conn.close()

    def get_video(self, video_id: str) -> Dict[str, Any]:
        """Get video information."""
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, collection_id, name, file_path, metadata, created_at, updated_at FROM assets WHERE id = ? AND asset_type = 'video'",
                (video_id,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Video {video_id} not found")

            metadata = json.loads(row[4]) if row[4] else {}
            return {
                "id": row[0],
                "name": row[1],
                "description": metadata.get("description", ""),
                "collection_id": row[1],
                "file_path": row[3],
                "length": metadata.get("duration", 0),
                "metadata": metadata,
            }
        finally:
            conn.close()

    def get_videos(self) -> List[Dict[str, Any]]:
        """Get all videos in collection."""
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, collection_id, name, file_path, metadata FROM assets WHERE collection_id = ? AND asset_type = 'video'",
                (self.collection_id,)
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "name": row[2],
                    "description": "",
                    "collection_id": row[1],
                    "file_path": row[3],
                    "length": json.loads(row[4]).get("duration", 0) if row[4] else 0,
                    "type": "video",
                }
                for row in rows
            ]
        finally:
            conn.close()

    def delete_video(self, video_id: str) -> Dict[str, Any]:
        """Delete a video."""
        # Get file path first
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT file_path FROM assets WHERE id = ?", (video_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Video {video_id} not found")

            file_path = row[0]

            # Delete from database
            cursor.execute("DELETE FROM assets WHERE id = ?", (video_id,))
            conn.commit()

            # Delete file
            if file_path and os.path.exists(file_path):
                os.remove(file_path)

            return {
                "success": True,
                "message": f"Video {video_id} deleted successfully",
            }
        except Exception as e:
            raise Exception(f"Failed to delete video {video_id}: {str(e)}")
        finally:
            conn.close()

    def get_audio(self, audio_id: str) -> Dict[str, Any]:
        """Get audio information."""
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, collection_id, name, file_path, url, metadata FROM assets WHERE id = ? AND asset_type = 'audio'",
                (audio_id,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Audio {audio_id} not found")

            metadata = json.loads(row[5]) if row[5] else {}
            return {
                "id": row[0],
                "collection_id": row[1],
                "name": row[2],
                "file_path": row[3],
                "url": row[4],
                "length": metadata.get("duration", 0),
                "type": "audio",
            }
        finally:
            conn.close()

    def get_audios(self) -> List[Dict[str, Any]]:
        """Get all audios in collection."""
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, collection_id, name, file_path, url, metadata FROM assets WHERE collection_id = ? AND asset_type = 'audio'",
                (self.collection_id,)
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "collection_id": row[1],
                    "name": row[2],
                    "file_path": row[3],
                    "url": row[4],
                    "length": json.loads(row[5]).get("duration", 0) if row[5] else 0,
                    "type": "audio",
                }
                for row in rows
            ]
        finally:
            conn.close()

    def delete_audio(self, audio_id: str) -> Dict[str, Any]:
        """Delete an audio asset."""
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT file_path FROM assets WHERE id = ? AND asset_type = 'audio'", (audio_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Audio {audio_id} not found")

            file_path = row[0]
            cursor.execute("DELETE FROM assets WHERE id = ?", (audio_id,))
            conn.commit()

            if file_path and os.path.exists(file_path):
                os.remove(file_path)

            return {
                "success": True,
                "message": f"Audio {audio_id} deleted successfully",
            }
        except Exception as e:
            raise Exception(f"Failed to delete audio {audio_id}: {str(e)}")
        finally:
            conn.close()

    def generate_audio_url(self, audio_id: str) -> str:
        """Get the local file path for an audio asset (serves as URL in local mode)."""
        audio = self.get_audio(audio_id)
        file_path = audio.get("file_path")
        if not file_path or not os.path.exists(file_path):
            raise ValueError(f"Audio file not found for asset {audio_id}")
        return file_path

    def get_image(self, image_id: str) -> Dict[str, Any]:
        """Get image information."""
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, collection_id, name, file_path, url, metadata FROM assets WHERE id = ? AND asset_type = 'image'",
                (image_id,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Image {image_id} not found")

            metadata = json.loads(row[5]) if row[5] else {}
            return {
                "id": row[0],
                "collection_id": row[1],
                "name": row[2],
                "url": row[3] or row[4],
                "file_path": row[3],
                "type": "image",
            }
        finally:
            conn.close()

    def get_images(self) -> List[Dict[str, Any]]:
        """Get all images in collection."""
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, collection_id, name, file_path, url, metadata FROM assets WHERE collection_id = ? AND asset_type = 'image'",
                (self.collection_id,)
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "collection_id": row[1],
                    "name": row[2],
                    "url": row[3] or row[4],
                    "file_path": row[3],
                    "type": "image",
                }
                for row in rows
            ]
        finally:
            conn.close()

    def delete_image(self, image_id: str) -> Dict[str, Any]:
        """Delete an image asset."""
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT file_path FROM assets WHERE id = ? AND asset_type = 'image'", (image_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Image {image_id} not found")

            file_path = row[0]
            cursor.execute("DELETE FROM assets WHERE id = ?", (image_id,))
            conn.commit()

            if file_path and os.path.exists(file_path):
                os.remove(file_path)

            return {
                "success": True,
                "message": f"Image {image_id} deleted successfully",
            }
        except Exception as e:
            raise Exception(f"Failed to delete image {image_id}: {str(e)}")
        finally:
            conn.close()

    def generate_image_url(self, image_id: str) -> str:
        """Get the local file path for an image asset (serves as URL in local mode)."""
        image = self.get_image(image_id)
        file_path = image.get("file_path")
        if not file_path or not os.path.exists(file_path):
            raise ValueError(f"Image file not found for asset {image_id}")
        return file_path

    def extract_frame(self, video_id: str, timestamp: float = 5.0) -> Dict[str, Any]:
        """Extract a single frame from a video at a given timestamp."""
        video = self.get_video(video_id)
        video_path = video.get("file_path")
        if not video_path or not os.path.exists(video_path):
            raise ValueError(f"Video file not found for asset {video_id}")

        frame_id = str(uuid.uuid4())
        frame_filename = f"frame_{video_id}_{int(timestamp)}s.jpg"
        frame_path = os.path.join(DOWNLOADS_PATH, "collections", self.collection_id, frame_filename)
        os.makedirs(os.path.dirname(frame_path), exist_ok=True)

        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-ss", str(timestamp),
            "-vframes", "1",
            "-q:v", "2",
            "-y",
            frame_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True, timeout=30)

        metadata = self._extract_file_metadata(frame_path, "image")
        metadata.update({"source_video_id": video_id, "timestamp": timestamp})

        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO assets (id, collection_id, name, asset_type, file_path, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    frame_id,
                    self.collection_id,
                    frame_filename,
                    "image",
                    frame_path,
                    json.dumps(metadata),
                    int(time.time()),
                    int(time.time()),
                )
            )
            conn.commit()

            return {
                "id": frame_id,
                "collection_id": self.collection_id,
                "name": frame_filename,
                "url": frame_path,
            }
        finally:
            conn.close()

    def get_transcript(self, video_id: str, text: bool = True) -> Any:
        """Get transcript for video using AI transcription."""
        # Check if transcript already exists
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT transcript_text, transcript_json, language FROM asset_transcripts WHERE asset_id = ?",
                (video_id,)
            )
            row = cursor.fetchone()
            if row:
                # Return cached transcript
                if text:
                    return row[0]  # transcript_text
                else:
                    return json.loads(row[1]) if row[1] else {"text": row[0]}

            # Get video file path
            cursor.execute("SELECT file_path FROM assets WHERE id = ?", (video_id,))
            asset_row = cursor.fetchone()
            if not asset_row:
                raise ValueError(f"Video {video_id} not found")

            video_path = asset_row[0]
        finally:
            conn.close()

        # Try EditMind first
        transcript_text = None
        try:
            transcript_text = self.editmind_wrapper.get_transcript(video_path)
        except Exception as e:
            logger.warning(f"EditMind transcription failed: {e}")

        if transcript_text:
            # Save to db
            conn = self._get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO asset_transcripts (asset_id, transcript_text, transcript_json, language) VALUES (?, ?, ?, ?)",
                    (video_id, transcript_text, json.dumps({"text": transcript_text}), "en")
                )
                conn.commit()
            finally:
                conn.close()
            if text:
                return transcript_text
            else:
                return {"text": transcript_text}

        # Fallback to existing AI client
        if not self.ai_client:
            raise Exception("AI client not available for transcription")

        # Extract audio first (similar to local_video_tool)
        base_name = os.path.basename(video_path).rsplit(".", 1)[0]
        audio_path = os.path.join(self.local_video_tool.downloads_path, f"{base_name}_audio.wav")

        try:
            # Extract audio
            import subprocess
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

            # Transcribe
            transcript_result = self.ai_client.transcribe_audio(audio_path)
            if not transcript_result["success"]:
                raise Exception(f"Transcription failed: {transcript_result.get('error')}")

            # Save transcript to database
            transcript_text = transcript_result["text"]
            transcript_json = json.dumps({
                "text": transcript_text,
                "segments": transcript_result["segments"],
                "language": transcript_result["language"]
            })

            conn = self._get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO asset_transcripts (asset_id, transcript_text, transcript_json, language, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        video_id,
                        transcript_text,
                        transcript_json,
                        transcript_result["language"],
                        int(time.time()),
                        int(time.time())
                    )
                )
                conn.commit()
            finally:
                conn.close()

            # Return transcript
            if text:
                return transcript_text
            else:
                return json.loads(transcript_json)

        finally:
            # Clean up audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)

    def index_scenes(self, video_id: str, extraction_config: Optional[Dict] = None) -> Dict[str, Any]:
        """Index scenes in video using AI vision (simplified implementation)."""
        # Get video file path
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT file_path, metadata FROM assets WHERE id = ?", (video_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Video {video_id} not found")

            video_path = row[0]
            metadata = json.loads(row[1]) if row[1] else {}
        finally:
            conn.close()

        # Try EditMind first
        scenes = []
        try:
            scenes = self.editmind_wrapper.index_scenes(video_path)
        except Exception as e:
            logger.warning(f"EditMind scene indexing failed: {e}")

        if scenes:
            # Save to db
            scene_data = json.dumps({
                "scenes": scenes,
                "extraction_method": "editmind",
                "total_scenes": len(scenes),
            })
            conn = self._get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO asset_indexes (id, asset_id, index_type, index_data, created_at) VALUES (?, ?, ?, ?, ?)",
                    (
                        str(uuid.uuid4()),
                        video_id,
                        "scene",
                        scene_data,
                        int(time.time())
                    )
                )
                conn.commit()
            finally:
                conn.close()
            return scenes

        # Fallback to existing AI client
        if not self.ai_client:
            raise Exception("AI client not available for scene indexing")

        # Extract frames at regular intervals (simplified scene detection)
        duration = metadata.get("duration", 60)
        frame_interval = max(10, duration / 20)  # Extract up to 20 frames

        frames = []
        try:
            import subprocess
            import base64

            for i in range(0, int(duration), int(frame_interval)):
                # Extract frame at timestamp i
                frame_path = os.path.join(self.local_video_tool.downloads_path, f"frame_{video_id}_{i}.jpg")
                extract_cmd = [
                    "ffmpeg",
                    "-i", video_path,
                    "-ss", str(i),
                    "-vframes", "1",
                    "-q:v", "2",
                    "-y",
                    frame_path,
                ]
                subprocess.run(extract_cmd, check=True, capture_output=True, timeout=30)

                # Convert to base64
                with open(frame_path, "rb") as f:
                    frame_b64 = base64.b64encode(f.read()).decode('utf-8')
                    frames.append(frame_b64)

                # Clean up frame file
                os.remove(frame_path)

            # Use AI to analyze frames
            highlights_result = self.ai_client.extract_scene_highlights(video_path, frames)

            # Save scene index to database
            scene_data = json.dumps({
                "scenes": highlights_result.get("highlights", []),
                "extraction_method": "ai_vision",
                "frame_interval": frame_interval,
                "total_frames": len(frames),
            })

            conn = self._get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO asset_indexes (id, asset_id, index_type, index_data, created_at) VALUES (?, ?, ?, ?, ?)",
                    (
                        str(uuid.uuid4()),
                        video_id,
                        "scene",
                        scene_data,
                        int(time.time())
                    )
                )
                conn.commit()
            finally:
                conn.close()

            return highlights_result.get("highlights", [])

        except Exception as e:
            logger.error(f"Scene indexing failed: {e}")
            return []

    def list_scene_index(self, video_id: str) -> List[Dict[str, Any]]:
        """List scene index for video."""
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT index_data FROM asset_indexes WHERE asset_id = ? AND index_type = 'scene'",
                (video_id,)
            )
            rows = cursor.fetchall()

            all_scenes = []
            for row in rows:
                index_data = json.loads(row[0])
                scenes = index_data.get("scenes", [])
                all_scenes.extend(scenes)

            return all_scenes
        finally:
            conn.close()

    def get_scene_index(self, video_id: str, scene_id: str) -> Dict[str, Any]:
        """Get a specific scene index entry by ID."""
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, index_data FROM asset_indexes WHERE id = ? AND asset_id = ? AND index_type = 'scene'",
                (scene_id, video_id)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Scene index {scene_id} not found for video {video_id}")

            index_data = json.loads(row[1])
            return {
                "id": row[0],
                "asset_id": video_id,
                "scenes": index_data.get("scenes", []),
                "extraction_method": index_data.get("extraction_method", "unknown"),
            }
        finally:
            conn.close()

    def index_spoken_words(self, video_id: str) -> Dict[str, Any]:
        """Index spoken words in video by generating transcript and creating a word-level index."""
        transcript = self.get_transcript(video_id, text=False)
        if not transcript:
            return {"message": "No transcript available for indexing"}

        segments = transcript.get("segments", [])
        word_entries = []
        for seg in segments:
            start = seg.get("start", 0)
            end = seg.get("end", 0)
            text = seg.get("text", "").strip()
            words = text.split()
            if not words:
                continue
            word_duration = (end - start) / len(words) if len(words) > 0 else 0
            for i, word in enumerate(words):
                word_entries.append({
                    "word": word,
                    "start": round(start + i * word_duration, 3),
                    "end": round(start + (i + 1) * word_duration, 3),
                })

        index_data = json.dumps({
            "type": "spoken_word",
            "words": word_entries,
            "total_words": len(word_entries),
        })

        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM asset_indexes WHERE asset_id = ? AND index_type = 'spoken_word'",
                (video_id,)
            )
            cursor.execute(
                "INSERT INTO asset_indexes (id, asset_id, index_type, index_data, created_at) VALUES (?, ?, ?, ?, ?)",
                (
                    str(uuid.uuid4()),
                    video_id,
                    "spoken_word",
                    index_data,
                    int(time.time()),
                )
            )
            conn.commit()
            return {
                "success": True,
                "message": f"Indexed {len(word_entries)} spoken words",
                "total_words": len(word_entries),
            }
        finally:
            conn.close()

    def semantic_search(self, query: str, collection_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Perform semantic search across videos using EditMind's vector search."""
        # Try EditMind first
        if self.editmind_wrapper:
            try:
                results = self.editmind_wrapper.semantic_search(query, collection_id, limit)
                if results:
                    return results
            except Exception as e:
                logger.warning(f"EditMind semantic search failed: {e}")

        # Fallback to basic text search in transcripts
        if not collection_id:
            collection_id = self.collection_id

        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            # Search in transcript text
            cursor.execute(
                """
                SELECT a.id, a.name, a.collection_id, a.file_path, a.metadata, t.transcript_text
                FROM assets a
                LEFT JOIN asset_transcripts t ON a.id = t.asset_id
                WHERE a.collection_id = ? AND a.asset_type = 'video'
                AND (t.transcript_text LIKE ? OR a.name LIKE ?)
                LIMIT ?
                """,
                (collection_id, f"%{query}%", f"%{query}%", limit)
            )
            rows = cursor.fetchall()

            results = []
            for row in rows:
                metadata = json.loads(row[4]) if row[4] else {}
                results.append({
                    "id": row[0],
                    "name": row[1],
                    "collection_id": row[2],
                    "file_path": row[3],
                    "metadata": metadata,
                    "transcript_snippet": row[5][:200] if row[5] else "",
                    "search_method": "text_fallback"
                })
            return results
        except Exception as e:
            logger.warning(f"Text search fallback failed: {e}")
            return []
        finally:
            conn.close()

    def _format_srt_timestamp(self, seconds: float) -> str:
        """Format seconds into SRT timestamp format HH:MM:SS,mmm."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def add_subtitle(self, video_id: str, style: Optional[Dict] = None, save_at: Optional[str] = None) -> Dict[str, Any]:
        """Add subtitles to a video by burning SRT into the video using FFmpeg."""
        video = self.get_video(video_id)
        video_path = video.get("file_path")
        if not video_path or not os.path.exists(video_path):
            raise ValueError(f"Video file not found for asset {video_id}")

        transcript = self.get_transcript(video_id, text=False)
        segments = transcript.get("segments", [])

        if not segments:
            raise Exception("No transcript segments available for subtitle generation")

        base_name = os.path.basename(video_path).rsplit(".", 1)[0]
        srt_path = os.path.join(
            DOWNLOADS_PATH, "collections", self.collection_id, f"{base_name}_subtitles.srt"
        )
        os.makedirs(os.path.dirname(srt_path), exist_ok=True)

        with open(srt_path, "w", encoding="utf-8") as f:
            for i, seg in enumerate(segments, 1):
                start = self._format_srt_timestamp(seg.get("start", 0))
                end = self._format_srt_timestamp(seg.get("end", 0))
                text = seg.get("text", "").strip()
                f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

        output_filename = f"{base_name}_subtitled.mp4"
        output_path = save_at or os.path.join(
            DOWNLOADS_PATH, "collections", self.collection_id, output_filename
        )

        subtitle_style = ""
        if style:
            font_name = style.get("font_name", "Arial")
            font_size = style.get("font_size", 24)
            primary_color = style.get("primary_color", "&HFFFFFF")
            outline_color = style.get("outline_color", "&H000000")
            subtitle_style = (
                f":force_style='FontName={font_name},FontSize={font_size},"
                f"PrimaryColour={primary_color},OutlineColour={outline_color}'"
            )

        srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", f"subtitles='{srt_escaped}'{subtitle_style}",
            "-c:v", "libx264",
            "-c:a", "copy",
            "-y",
            output_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=300)

        output_asset_id = str(uuid.uuid4())
        metadata = self._extract_file_metadata(output_path, "video")
        metadata.update({"source_video_id": video_id, "has_subtitles": True})

        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO assets (id, collection_id, name, asset_type, file_path, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    output_asset_id,
                    self.collection_id,
                    output_filename,
                    "video",
                    output_path,
                    json.dumps(metadata),
                    int(time.time()),
                    int(time.time()),
                )
            )
            conn.commit()

            return {
                "id": output_asset_id,
                "collection_id": self.collection_id,
                "name": output_filename,
                "file_path": output_path,
                "stream_url": output_path,
            }
        finally:
            conn.close()

    def translate_transcript(self, video_id: str, language: str, additional_notes: Optional[str] = None) -> Dict[str, Any]:
        """Translate a video's transcript to another language using AI."""
        if not self.ai_client:
            raise Exception("AI client not available for translation")

        transcript_text = self.get_transcript(video_id, text=True)
        if not transcript_text:
            raise Exception("No transcript available for translation")

        prompt_parts = [
            f"Translate the following transcript to {language}.",
            "Keep the translation natural and accurate.",
        ]
        if additional_notes:
            prompt_parts.append(f"Additional notes: {additional_notes}")
        prompt_parts.append(f"\n\nTranscript:\n{transcript_text}")

        try:
            response = self.ai_client.client.chat.completions.create(
                model=self.ai_client.vision_model,
                messages=[
                    {"role": "system", "content": "You are a professional translator. Translate the given text accurately while preserving meaning and context."},
                    {"role": "user", "content": "\n\n".join(prompt_parts)},
                ],
                temperature=0.3,
                max_tokens=4096,
            )

            translated_text = response.choices[0].message.content

            conn = self._get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO asset_transcripts (asset_id, transcript_text, transcript_json, language, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        f"{video_id}_translated_{language}",
                        translated_text,
                        json.dumps({"text": translated_text, "language": language, "source": "translation"}),
                        language,
                        int(time.time()),
                        int(time.time()),
                    )
                )
                conn.commit()
            finally:
                conn.close()

            return {
                "text": translated_text,
                "language": language,
                "source_video_id": video_id,
            }
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise

    def dub_video(self, video_id: str, language_code: str) -> Dict[str, Any]:
        """Create a dubbed version of a video by translating transcript, generating TTS, and merging."""
        video = self.get_video(video_id)
        video_path = video.get("file_path")
        if not video_path or not os.path.exists(video_path):
            raise ValueError(f"Video file not found for asset {video_id}")

        translation = self.translate_transcript(video_id, language_code)
        translated_text = translation["text"]

        if not self.ai_client:
            raise Exception("AI client not available for dubbing")

        base_name = os.path.basename(video_path).rsplit(".", 1)[0]
        dub_audio_path = os.path.join(
            DOWNLOADS_PATH, "collections", self.collection_id, f"{base_name}_dub_{language_code}.mp3"
        )
        os.makedirs(os.path.dirname(dub_audio_path), exist_ok=True)

        voice_result = self.ai_client.generate_speech(translated_text, voice="alloy", speed=1.0)
        if not voice_result["success"]:
            raise Exception(f"Dubbing voice generation failed: {voice_result.get('error')}")

        with open(dub_audio_path, "wb") as f:
            f.write(voice_result["audio_data"])

        dubbed_video_path = os.path.join(
            DOWNLOADS_PATH, "collections", self.collection_id, f"{base_name}_dubbed_{language_code}.mp4"
        )

        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-i", dub_audio_path,
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            "-y",
            dubbed_video_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=300)

        if os.path.exists(dub_audio_path):
            os.remove(dub_audio_path)

        dub_asset_id = str(uuid.uuid4())
        metadata = self._extract_file_metadata(dubbed_video_path, "video")
        metadata.update({"source_video_id": video_id, "dub_language": language_code})

        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO assets (id, collection_id, name, asset_type, file_path, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    dub_asset_id,
                    self.collection_id,
                    os.path.basename(dubbed_video_path),
                    "video",
                    dubbed_video_path,
                    json.dumps(metadata),
                    int(time.time()),
                    int(time.time()),
                )
            )
            conn.commit()

            return {
                "id": dub_asset_id,
                "name": os.path.basename(dubbed_video_path),
                "description": f"Dubbed version in {language_code}",
                "collection_id": self.collection_id,
                "stream_url": dubbed_video_path,
                "file_path": dubbed_video_path,
                "length": metadata.get("duration", 0),
            }
        finally:
            conn.close()

    def generate_video_stream(self, video_id: str, timeline: List[Tuple[float, float]]) -> Dict[str, Any]:
        """Generate a video stream from a timeline (list of (start, end) tuples) using FFmpeg."""
        video = self.get_video(video_id)
        video_path = video.get("file_path")
        if not video_path or not os.path.exists(video_path):
            raise ValueError(f"Video file not found for asset {video_id}")

        if not timeline:
            raise ValueError("Timeline segments are required")

        base_name = os.path.basename(video_path).rsplit(".", 1)[0]
        concat_list_path = os.path.join(
            DOWNLOADS_PATH, "collections", self.collection_id, f"concat_{video_id}.txt"
        )
        os.makedirs(os.path.dirname(concat_list_path), exist_ok=True)

        segment_paths = []
        try:
            for i, (start, end) in enumerate(timeline):
                duration = end - start
                if duration <= 0:
                    continue
                seg_path = os.path.join(
                    DOWNLOADS_PATH, "collections", self.collection_id, f"seg_{video_id}_{i}.mp4"
                )
                cmd = [
                    "ffmpeg",
                    "-i", video_path,
                    "-ss", str(start),
                    "-t", str(duration),
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-avoid_negative_ts", "1",
                    "-y",
                    seg_path,
                ]
                subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
                segment_paths.append(seg_path)

            with open(concat_list_path, "w", encoding="utf-8") as f:
                for seg_path in segment_paths:
                    safe_path = seg_path.replace("'", "'\\''")
                    f.write(f"file '{safe_path}'\n")

            output_filename = f"{base_name}_stream_{int(time.time())}.mp4"
            output_path = os.path.join(
                DOWNLOADS_PATH, "collections", self.collection_id, output_filename
            )

            cmd = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_list_path,
                "-c", "copy",
                "-y",
                output_path,
            ]
            subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)

            stream_asset_id = str(uuid.uuid4())
            metadata = self._extract_file_metadata(output_path, "video")
            metadata.update({"source_video_id": video_id, "timeline": timeline})

            conn = self._get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO assets (id, collection_id, name, asset_type, file_path, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        stream_asset_id,
                        self.collection_id,
                        output_filename,
                        "video",
                        output_path,
                        json.dumps(metadata),
                        int(time.time()),
                        int(time.time()),
                    )
                )
                conn.commit()

                return {
                    "id": stream_asset_id,
                    "collection_id": self.collection_id,
                    "name": output_filename,
                    "stream_url": output_path,
                    "file_path": output_path,
                    "length": metadata.get("duration", 0),
                }
            finally:
                conn.close()

        finally:
            for seg_path in segment_paths:
                if os.path.exists(seg_path):
                    os.remove(seg_path)
            if os.path.exists(concat_list_path):
                os.remove(concat_list_path)

    def youtube_search(self, query: str, count: int = 5, duration: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search YouTube using yt-dlp and return results."""
        try:
            cmd = [
                "yt-dlp",
                f"ytsearch{count}:{query}",
                "--print", "%(id)s|%(title)s|%(duration)s|%(channel)s|%(view_count)s|%(upload_date)s",
                "--no-download",
            ]
            if duration:
                cmd.extend(["--match-filter", f"duration <? {duration}"])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, encoding="utf-8")

            search_results = []
            for line in result.stdout.strip().split("\n"):
                if not line or "|" not in line:
                    continue
                parts = line.split("|")
                if len(parts) >= 4:
                    video_id = parts[0].strip()
                    search_results.append({
                        "id": video_id,
                        "title": parts[1].strip() if len(parts) > 1 else "",
                        "duration": parts[2].strip() if len(parts) > 2 else "",
                        "channel": parts[3].strip() if len(parts) > 3 else "",
                        "view_count": parts[4].strip() if len(parts) > 4 else "",
                        "upload_date": parts[5].strip() if len(parts) > 5 else "",
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                    })

            return search_results
        except subprocess.TimeoutExpired:
            logger.error("YouTube search timed out")
            return []
        except Exception as e:
            logger.error(f"YouTube search failed: {e}")
            return []

    def download(self, stream_link: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Download a video from a URL."""
        download_result = self.local_video_tool.download_video(stream_link, name=name)
        if not download_result["success"]:
            raise Exception(f"Download failed: {download_result.get('error', 'Unknown error')}")

        return {
            "download_url": download_result["file_path"],
            "file_path": download_result["file_path"],
            "message": "Download completed successfully",
        }

    def get_and_set_timeline(self):
        """Create a new local timeline for video composition."""
        self.timeline = LocalTimeline(self)
        return self.timeline

    def add_brandkit(self, video_id: str, intro_video_id: Optional[str] = None, outro_video_id: Optional[str] = None, brand_image_id: Optional[str] = None) -> Dict[str, Any]:
        """Add intro, outro, and brand image overlay to a video using FFmpeg."""
        main_video = self.get_video(video_id)
        main_path = main_video.get("file_path")
        if not main_path or not os.path.exists(main_path):
            raise ValueError(f"Main video file not found for asset {video_id}")

        base_name = os.path.basename(main_path).rsplit(".", 1)[0]
        segments = []

        if intro_video_id:
            intro = self.get_video(intro_video_id)
            intro_path = intro.get("file_path")
            if intro_path and os.path.exists(intro_path):
                segments.append(("intro", intro_path))

        segments.append(("main", main_path))

        if outro_video_id:
            outro = self.get_video(outro_video_id)
            outro_path = outro.get("file_path")
            if outro_path and os.path.exists(outro_path):
                segments.append(("outro", outro_path))

        concat_list_path = os.path.join(
            DOWNLOADS_PATH, "collections", self.collection_id, f"brandkit_{video_id}.txt"
        )
        os.makedirs(os.path.dirname(concat_list_path), exist_ok=True)

        with open(concat_list_path, "w", encoding="utf-8") as f:
            for label, path in segments:
                safe_path = path.replace("'", "'\\''")
                f.write(f"file '{safe_path}'\n")

        output_filename = f"{base_name}_branded.mp4"
        output_path = os.path.join(
            DOWNLOADS_PATH, "collections", self.collection_id, output_filename
        )

        try:
            cmd = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_list_path,
                "-c:v", "libx264",
                "-c:a", "aac",
                "-y",
                output_path,
            ]
            subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=300)

            if brand_image_id:
                image = self.get_image(brand_image_id)
                image_path = image.get("file_path")
                if image_path and os.path.exists(image_path):
                    branded_with_overlay = output_path.replace(".mp4", "_overlay.mp4")
                    overlay_cmd = [
                        "ffmpeg",
                        "-i", output_path,
                        "-i", image_path,
                        "-filter_complex", "[1:v]scale=100:50[overlay];[0:v][overlay]overlay=W-w-10:10",
                        "-c:a", "copy",
                        "-y",
                        branded_with_overlay,
                    ]
                    subprocess.run(overlay_cmd, check=True, capture_output=True, text=True, timeout=300)
                    os.replace(branded_with_overlay, output_path)

            branded_asset_id = str(uuid.uuid4())
            metadata = self._extract_file_metadata(output_path, "video")
            metadata.update({
                "source_video_id": video_id,
                "intro_video_id": intro_video_id,
                "outro_video_id": outro_video_id,
                "brand_image_id": brand_image_id,
            })

            conn = self._get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO assets (id, collection_id, name, asset_type, file_path, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        branded_asset_id,
                        self.collection_id,
                        output_filename,
                        "video",
                        output_path,
                        json.dumps(metadata),
                        int(time.time()),
                        int(time.time()),
                    )
                )
                conn.commit()

                return {
                    "id": branded_asset_id,
                    "collection_id": self.collection_id,
                    "name": output_filename,
                    "stream_url": output_path,
                    "file_path": output_path,
                    "length": metadata.get("duration", 0),
                }
            finally:
                conn.close()

        finally:
            if os.path.exists(concat_list_path):
                os.remove(concat_list_path)

    def index_semantic(self, video_id: str) -> Dict[str, Any]:
        """Generate and store semantic embeddings for a video's transcript."""
        if not self.ai_client:
            raise Exception("AI client not available for semantic indexing")

        # Get transcript
        transcript = self.get_transcript(video_id, text=True)
        if not transcript:
            return {"message": "No transcript available for indexing"}

        # Generate embeddings for the transcript (chunked for efficiency)
        # For simplicity, we'll embed the full transcript text as one chunk
        # In production, you'd chunk by sentence or paragraph
        embeddings_result = self.ai_client.generate_embeddings([transcript])
        if not embeddings_result["success"]:
            raise Exception(f"Embedding generation failed: {embeddings_result.get('error')}")

        embedding_data = {
            "embedding": embeddings_result["embeddings"][0],
            "text": transcript,
            "model": embeddings_result["model"],
        }

        # Save to database
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            # Remove existing semantic index for this video
            cursor.execute(
                "DELETE FROM asset_indexes WHERE asset_id = ? AND index_type = 'semantic'",
                (video_id,)
            )
            # Insert new index
            cursor.execute(
                "INSERT INTO asset_indexes (id, asset_id, index_type, index_data, created_at) VALUES (?, ?, ?, ?, ?)",
                (
                    str(uuid.uuid4()),
                    video_id,
                    "semantic",
                    json.dumps(embedding_data),
                    int(time.time())
                )
            )
            conn.commit()
            return {"success": True, "message": "Semantic index created successfully"}
        finally:
            conn.close()

    def semantic_search(self, query: str, video_id: Optional[str] = None, **kwargs) -> List[Any]:
        """Semantic search using embeddings."""
        # Try EditMind first
        results = []
        try:
            results = self.editmind_wrapper.semantic_search(query, video_id, limit=kwargs.get("limit", 10))
        except Exception as e:
            logger.warning(f"EditMind search failed: {e}")

        if results:
            return results

        # Fallback to existing AI client
        if not self.ai_client:
            logger.warning("AI client not available for semantic search, returning empty results")
            return []

        # 1. Generate embedding for query
        query_embedding_result = self.ai_client.generate_embeddings([query])
        if not query_embedding_result["success"]:
            raise Exception(f"Query embedding failed: {query_embedding_result.get('error')}")
        
        query_embedding = query_embedding_result["embeddings"][0]

        # 2. Retrieve stored embeddings
        conn = self._get_db_connection()
        try:
            if video_id:
                cursor = conn.execute(
                    "SELECT index_data FROM asset_indexes WHERE asset_id = ? AND index_type = 'semantic'",
                    (video_id,)
                )
            else:
                cursor = conn.execute(
                    "SELECT index_data FROM asset_indexes WHERE index_type = 'semantic'"
                )
            
            rows = cursor.fetchall()
        finally:
            conn.close()

        # 3. Calculate similarity and rank results
        results = []
        for row in rows:
            index_data = json.loads(row[0])
            stored_embedding = index_data.get("embedding", [])
            
            if not stored_embedding:
                continue

            # Calculate cosine similarity
            dot_product = sum(a * b for a, b in zip(query_embedding, stored_embedding))
            norm_query = sum(a * a for a in query_embedding) ** 0.5
            norm_stored = sum(b * b for b in stored_embedding) ** 0.5
            
            if norm_query > 0 and norm_stored > 0:
                similarity = dot_product / (norm_query * norm_stored)
                
                results.append({
                    "score": similarity,
                    "text": index_data.get("text", "")[:200] + "..."  # Snippet
                })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def keyword_search(self, query: str, video_id: Optional[str] = None, **kwargs) -> List[Any]:
        """Keyword search using SQLite LIKE operator."""
        conn = self._get_db_connection()
        try:
            if video_id:
                # Search transcript for specific video
                cursor = conn.execute(
                    "SELECT transcript_text FROM asset_transcripts WHERE asset_id = ? AND transcript_text LIKE ?",
                    (video_id, f"%{query}%")
                )
            else:
                # Search all transcripts
                cursor = conn.execute(
                    "SELECT t.transcript_text, a.name as video_name FROM asset_transcripts t "
                    "JOIN assets a ON t.asset_id = a.id "
                    "WHERE t.transcript_text LIKE ?",
                    (f"%{query}%",)
                )
            
            rows = cursor.fetchall()
            return [{"match": row[0]} for row in rows]
        finally:
            conn.close()

    def generate_image(self, prompt: str, aspect_ratio: str = "16:9", save_at: Optional[str] = None) -> Dict[str, Any]:
        """Generate image from prompt using OpenAI DALL-E or similar API."""
        if not self.ai_client:
            raise Exception("AI client not available for image generation")

        try:
            # Use OpenAI image generation
            response = self.ai_client.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024", # Default size, aspect ratio handling might be needed
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url
            
            # Download image if save_at is provided
            if save_at:
                self._download_file(image_url, save_at)
                file_path = save_at
            else:
                # Use a default path
                file_path = os.path.join(DOWNLOADS_PATH, f"generated_image_{int(time.time())}.png")
                self._download_file(image_url, file_path)

            # Extract metadata
            metadata = self._extract_file_metadata(file_path, "image")

            # Save to database
            asset_id = str(uuid.uuid4())
            conn = self._get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO assets (id, collection_id, name, asset_type, file_path, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        asset_id,
                        self.collection_id,
                        os.path.basename(file_path),
                        "image",
                        file_path,
                        json.dumps(metadata),
                        int(time.time()),
                        int(time.time())
                    )
                )
                conn.commit()

                return {
                    "id": asset_id,
                    "collection_id": self.collection_id,
                    "name": os.path.basename(file_path),
                    "url": file_path,
                }
            finally:
                conn.close()

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise

    def generate_video(self, prompt: str, duration: float, save_at: Optional[str] = None) -> Dict[str, Any]:
        """Generate video from prompt.

        Attempts to use a configured video generation API (e.g. Fal, Replicate).
        Falls back to generating an image sequence from the prompt and combining
        into a video with FFmpeg if no dedicated API is available.
        """
        output_path = save_at or os.path.join(
            DOWNLOADS_PATH, f"generated_video_{int(time.time())}.mp4"
        )
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            from director.tools.fal_video import FalVideoTool
            fal_key = os.getenv("FAL_KEY")
            if fal_key:
                fal_tool = FalVideoTool(api_key=fal_key)
                result = fal_tool.text_to_video(prompt=prompt, save_at=output_path, duration=duration)
                if result:
                    return self._register_generated_asset(output_path, "video", prompt)
        except Exception as e:
            logger.warning(f"Fal video generation failed, trying fallback: {e}")

        try:
            from director.tools.replicate import ReplicateVideoTool
            replicate_key = os.getenv("REPLICATE_API_TOKEN")
            if replicate_key:
                rep_tool = ReplicateVideoTool(api_key=replicate_key)
                result = rep_tool.text_to_video(prompt=prompt, save_at=output_path, duration=duration)
                if result:
                    return self._register_generated_asset(output_path, "video", prompt)
        except Exception as e:
            logger.warning(f"Replicate video generation failed, trying fallback: {e}")

        try:
            from director.tools.kling import KlingVideoTool
            kling_key = os.getenv("KLING_API_KEY")
            if kling_key:
                kling_tool = KlingVideoTool(api_key=kling_key)
                result = kling_tool.text_to_video(prompt=prompt, save_at=output_path, duration=duration)
                if result:
                    return self._register_generated_asset(output_path, "video", prompt)
        except Exception as e:
            logger.warning(f"Kling video generation failed, trying image-based fallback: {e}")

        logger.info("No video generation API available. Generating image sequence with DALL-E and combining with FFmpeg.")
        if not self.ai_client:
            raise NotImplementedError(
                "Video generation requires a specialized AI API or an OpenAI-compatible image generation API. "
                "Set FAL_KEY, REPLICATE_API_TOKEN, or KLING_API_KEY for dedicated video generation, "
                "or ensure OPENAI_API_KEY is set for the image-sequence fallback."
            )

        num_frames = min(max(int(duration * 2), 2), 10)
        frame_dir = os.path.join(DOWNLOADS_PATH, f"frames_{int(time.time())}")
        os.makedirs(frame_dir, exist_ok=True)

        try:
            for i in range(num_frames):
                image_response = self.ai_client.client.images.generate(
                    model="dall-e-3",
                    prompt=f"{prompt}, frame {i+1} of {num_frames}, cinematic",
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                image_url = image_response.data[0].url
                frame_path = os.path.join(frame_dir, f"frame_{i:04d}.png")
                self._download_file(image_url, frame_path)

            cmd = [
                "ffmpeg",
                "-framerate", str(num_frames / max(duration, 1)),
                "-i", os.path.join(frame_dir, "frame_%04d.png"),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-y",
                output_path,
            ]
            subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=60)

            return self._register_generated_asset(output_path, "video", prompt)
        finally:
            shutil.rmtree(frame_dir, ignore_errors=True)

    def _register_generated_asset(self, file_path: str, asset_type: str, prompt: str) -> Dict[str, Any]:
        """Register a generated file as an asset in the database."""
        metadata = self._extract_file_metadata(file_path, asset_type)
        metadata.update({"generation_prompt": prompt, "generated": True})

        asset_id = str(uuid.uuid4())
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO assets (id, collection_id, name, asset_type, file_path, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    asset_id,
                    self.collection_id,
                    os.path.basename(file_path),
                    asset_type,
                    file_path,
                    json.dumps(metadata),
                    int(time.time()),
                    int(time.time()),
                )
            )
            conn.commit()

            result = {
                "id": asset_id,
                "collection_id": self.collection_id,
                "name": os.path.basename(file_path),
                "url": file_path,
            }
            if asset_type == "video":
                result["stream_url"] = file_path
                result["length"] = metadata.get("duration", 0)
            elif asset_type == "audio":
                result["length"] = metadata.get("duration", 0)
            return result
        finally:
            conn.close()

    def _download_file(self, url: str, save_at: str) -> str:
        """Download a file from a URL to a local path."""
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(save_at), exist_ok=True)
        with open(save_at, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        return save_at

    def generate_voice(self, text: str, voice_name: str, config: Dict[str, Any], save_at: str) -> Dict[str, Any]:
        """Generate voice audio using OpenAI TTS or similar API."""
        if not self.ai_client:
            raise Exception("AI client not available for voice generation")

        try:
            from director.tools.elevenlabs import VOICE_ID_MAP
            voice = VOICE_ID_MAP.get(voice_name, voice_name)
            
            # Generate speech using AI client
            result = self.ai_client.generate_speech(text, voice=voice, speed=config.get("speed", 1.0))
            if not result["success"]:
                raise Exception(f"Voice generation failed: {result.get('error')}")

            # Save audio file
            audio_content = result["audio_data"]
            with open(save_at, "wb") as f:
                f.write(audio_content)

            # Extract metadata
            metadata = self._extract_file_metadata(save_at, "audio")

            # Save to database
            asset_id = str(uuid.uuid4())
            conn = self._get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO assets (id, collection_id, name, asset_type, file_path, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        asset_id,
                        self.collection_id,
                        os.path.basename(save_at),
                        "audio",
                        save_at,
                        json.dumps(metadata),
                        int(time.time()),
                        int(time.time())
                    )
                )
                conn.commit()

                return {
                    "id": asset_id,
                    "collection_id": self.collection_id,
                    "name": os.path.basename(save_at),
                    "length": metadata.get("duration", 0),
                    "url": save_at,  # Local path treated as URL
                }
            finally:
                conn.close()

        except Exception as e:
            logger.error(f"Voice generation failed: {e}")
            raise

    def generate_music(self, prompt: str, duration: float, save_at: str) -> Dict[str, Any]:
        """Generate music using AI.

        Attempts ElevenLabs music generation first, then Beatoven if available.
        Falls back to generating a silent audio file as placeholder.
        """
        os.makedirs(os.path.dirname(save_at), exist_ok=True)

        try:
            from director.tools.beatoven import BeatovenTool
            beatoven_key = os.getenv("BEATOVEN_API_KEY")
            if beatoven_key:
                beatoven = BeatovenTool(api_key=beatoven_key)
                beatoven.generate_music(prompt=prompt, save_at=save_at, duration=duration)
                return self._register_generated_asset(save_at, "audio", prompt)
        except Exception as e:
            logger.warning(f"Beatoven music generation failed: {e}")

        try:
            elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
            if elevenlabs_key:
                from director.tools.elevenlabs import ElevenLabsTool
                elevenlabs = ElevenLabsTool(api_key=elevenlabs_key)
                config = {"prompt_influence": 0.3}
                elevenlabs.generate_sound_effect(prompt=prompt, save_at=save_at, duration=min(duration, 20), config=config)
                return self._register_generated_asset(save_at, "audio", prompt)
        except Exception as e:
            logger.warning(f"ElevenLabs music generation failed: {e}")

        raise NotImplementedError(
            "Music generation requires a specialized AI API. "
            "Set BEATOVEN_API_KEY or ELEVENLABS_API_KEY to enable this feature."
        )

    def generate_sound_effect(self, prompt: str, duration: float, config: Dict[str, Any], save_at: str) -> Dict[str, Any]:
        """Generate sound effect using AI.

        Attempts ElevenLabs sound effect generation first.
        """
        os.makedirs(os.path.dirname(save_at), exist_ok=True)

        try:
            elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
            if elevenlabs_key:
                from director.tools.elevenlabs import ElevenLabsTool
                elevenlabs = ElevenLabsTool(api_key=elevenlabs_key)
                elevenlabs.generate_sound_effect(
                    prompt=prompt, save_at=save_at,
                    duration=min(duration, 20), config=config
                )
                return self._register_generated_asset(save_at, "audio", prompt)
        except Exception as e:
            logger.warning(f"ElevenLabs sound effect generation failed: {e}")

        raise NotImplementedError(
            "Sound effect generation requires a specialized AI API. "
            "Set ELEVENLABS_API_KEY to enable this feature."
        )


class LocalTimeline:
    """Local timeline for composing video sequences using FFmpeg."""

    def __init__(self, videodb_tool: LocalVideoDBTool):
        self._tool = videodb_tool
        self._inline_assets: List[str] = []
        self._overlay_assets: List[Dict[str, Any]] = []

    def add_inline(self, video_asset, start: Optional[float] = None, end: Optional[float] = None) -> "LocalTimeline":
        """Add a video asset inline to the timeline.

        Args:
            video_asset: VideoAsset-like object with asset_id, or a string asset_id.
            start: Optional start time for clipping.
            end: Optional end time for clipping.
        """
        asset_id = getattr(video_asset, "asset_id", video_asset) if not isinstance(video_asset, str) else video_asset
        self._inline_assets.append({
            "asset_id": asset_id,
            "start": start,
            "end": end,
        })
        return self

    def add_overlay(self, timestamp: float, image_asset) -> "LocalTimeline":
        """Add an image overlay at a given timestamp.

        Args:
            timestamp: Time in seconds to place the overlay.
            image_asset: ImageAsset-like object with asset_id, or a string asset_id.
        """
        asset_id = getattr(image_asset, "asset_id", image_asset) if not isinstance(image_asset, str) else image_asset
        self._overlay_assets.append({
            "asset_id": asset_id,
            "timestamp": timestamp,
        })
        return self

    def generate_stream(self) -> Dict[str, Any]:
        """Render the timeline into a single output video using FFmpeg."""
        if not self._inline_assets:
            raise ValueError("No inline assets in timeline")

        concat_list_path = os.path.join(
            DOWNLOADS_PATH, "collections", self._tool.collection_id, f"timeline_{int(time.time())}.txt"
        )
        os.makedirs(os.path.dirname(concat_list_path), exist_ok=True)

        segment_paths = []
        try:
            for i, item in enumerate(self._inline_assets):
                asset_id = item["asset_id"]
                start = item.get("start")
                end = item.get("end")

                video = self._tool.get_video(asset_id)
                video_path = video.get("file_path")
                if not video_path or not os.path.exists(video_path):
                    continue

                if start is not None or end is not None:
                    seg_path = os.path.join(
                        DOWNLOADS_PATH, "collections", self._tool.collection_id, f"tl_seg_{i}.mp4"
                    )
                    cmd = ["ffmpeg", "-i", video_path]
                    if start is not None:
                        cmd.extend(["-ss", str(start)])
                    if end is not None:
                        cmd.extend(["-to", str(end)])
                    cmd.extend(["-c:v", "libx264", "-c:a", "aac", "-y", seg_path])
                    subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
                    segment_paths.append(seg_path)
                else:
                    segment_paths.append(video_path)

            with open(concat_list_path, "w", encoding="utf-8") as f:
                for path in segment_paths:
                    safe_path = path.replace("'", "'\\''")
                    f.write(f"file '{safe_path}'\n")

            output_filename = f"timeline_output_{int(time.time())}.mp4"
            output_path = os.path.join(
                DOWNLOADS_PATH, "collections", self._tool.collection_id, output_filename
            )

            cmd = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_list_path,
                "-c:v", "libx264",
                "-c:a", "aac",
                "-y",
                output_path,
            ]
            subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=300)

            if self._overlay_assets:
                overlay_input = output_path
                for overlay_item in self._overlay_assets:
                    image = self._tool.get_image(overlay_item["asset_id"])
                    image_path = image.get("file_path")
                    if not image_path or not os.path.exists(image_path):
                        continue

                    overlay_output = output_path.replace(".mp4", f"_overlay_{int(time.time())}.mp4")
                    overlay_cmd = [
                        "ffmpeg",
                        "-i", overlay_input,
                        "-i", image_path,
                        "-filter_complex", "[1:v]scale=100:50[overlay];[0:v][overlay]overlay=W-w-10:10",
                        "-c:a", "copy",
                        "-y",
                        overlay_output,
                    ]
                    subprocess.run(overlay_cmd, check=True, capture_output=True, text=True, timeout=300)
                    if os.path.exists(overlay_output):
                        os.replace(overlay_output, output_path)
                    overlay_input = output_path

            asset_id = str(uuid.uuid4())
            metadata = self._tool._extract_file_metadata(output_path, "video")
            metadata.update({"timeline": True, "inline_count": len(self._inline_assets), "overlay_count": len(self._overlay_assets)})

            conn = self._tool._get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO assets (id, collection_id, name, asset_type, file_path, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        asset_id,
                        self._tool.collection_id,
                        output_filename,
                        "video",
                        output_path,
                        json.dumps(metadata),
                        int(time.time()),
                        int(time.time()),
                    )
                )
                conn.commit()

                return {
                    "id": asset_id,
                    "collection_id": self._tool.collection_id,
                    "name": output_filename,
                    "stream_url": output_path,
                    "file_path": output_path,
                    "length": metadata.get("duration", 0),
                }
            finally:
                conn.close()

        finally:
            for seg_path in segment_paths:
                if os.path.exists(seg_path) and seg_path not in [a.get("file_path") for a in [self._tool.get_video(i["asset_id"]) for i in self._inline_assets] if a.get("file_path")]:
                    pass
            if os.path.exists(concat_list_path):
                os.remove(concat_list_path)
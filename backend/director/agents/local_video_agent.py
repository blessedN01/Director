import logging
import os
from typing import Any, Dict, List, Optional

from director.agents.base import BaseAgent, AgentResponse, AgentStatus
from director.core.session import Session, MsgStatus, TextContent
from director.tools.manual.local_video_tool import LocalVideoTool
from director.tools.ai.videodb_cloud_tool import VideoDBTool

logger = logging.getLogger(__name__)


class LocalVideoAgent(BaseAgent):
    def __init__(self, session: Session, **kwargs):
        self.agent_name = "local_video"
        self.description = (
            "Process videos locally using yt-dlp, FFmpeg, Whishper, and Edit Mind. "
            "Supports downloading, highlight extraction, subtitling, and formatting "
            "for social media."
        )
        self.parameters = self.get_parameters()
        super().__init__(session=session, **kwargs)

        self.use_local_tools = os.getenv("USE_LOCAL_TOOLS", "false").lower() == "true"

        if self.use_local_tools:
            self.tool = LocalVideoTool()
        else:
            self.tool = VideoDBTool(
                collection_id=getattr(self.session, "collection_id", "default")
            )

    def run(
        self,
        url: str,
        moment_types: Optional[List[str]] = None,
        language: str = "en",
        format_type: str = "tiktok",
        *args,
        **kwargs,
    ) -> AgentResponse:
        """
        Process video with local tools: download, extract highlights, generate subtitles, and format.

        :param str url: URL of the video to process
        :param List[str] moment_types: Types of moments to detect for highlights (e.g., ["emotional_beats", "action_movement"])
        :param str language: Language code for subtitles (e.g., "en", "es")
        :param str format_type: Target format for output video ("tiktok" or "youtube_shorts")
        :param args: Additional positional arguments
        :param kwargs: Additional keyword arguments
        :return: AgentResponse with processing results
        """
        try:
            self.output_message.actions.append("Starting video processing...")
            text_content = TextContent(
                agent_name=self.agent_name,
                status=MsgStatus.progress,
                status_message="Initializing video processing...",
            )
            self.output_message.content.append(text_content)
            self.output_message.push_update()

            if self.use_local_tools:
                return self._run_local(url, moment_types, language, format_type)
            else:
                return self._run_videodb(url, moment_types, language, format_type)

        except Exception as e:
            logger.exception(f"Error in {self.agent_name}")
            # Use the text_content we created in this method, not content[-1]
            # which may point to a different item if sub-methods appended more.
            text_content.status = MsgStatus.error
            text_content.status_message = f"Error in video processing: {str(e)}"
            self.output_message.publish()
            return AgentResponse(status=AgentStatus.ERROR, message=str(e))

    def _cleanup_file(self, file_path: str) -> None:
        """Remove a file if it exists, logging any failure."""
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as exc:
            logger.warning(f"Failed to clean up {file_path}: {exc}")

    def _run_local(
        self,
        url: str,
        moment_types: List[str],
        language: str,
        format_type: str,
    ) -> AgentResponse:
        text_content = self.output_message.content[-1]
        video_path = None

        try:
            # Step 1: Download video
            text_content.status_message = "Downloading video..."
            self.output_message.push_update()

            download_result = self.tool.download_video(url)
            if not download_result["success"]:
                raise Exception(
                    f"Download failed: {download_result.get('error', 'Unknown error')}"
                )

            video_path = download_result["file_path"]
            text_content.text += f"\nDownloaded video: {video_path}"

            # Step 2: Extract highlights
            text_content.status_message = "Extracting highlights..."
            self.output_message.push_update()

            highlights_result = self.tool.extract_highlights(video_path, moment_types)
            highlights = []
            if highlights_result["success"]:
                highlights = highlights_result.get("highlights", [])
                text_content.text += f"\nExtracted {len(highlights)} highlights"
            else:
                text_content.text += (
                    f"\nHighlights extraction incomplete: "
                    f"{highlights_result.get('message', '')}"
                )

            # Step 3: Generate subtitles
            text_content.status_message = "Generating subtitles..."
            self.output_message.push_update()

            subtitles_result = self.tool.generate_subtitles(video_path, language)
            if subtitles_result["success"]:
                text_content.text += (
                    f"\nGenerated subtitles: {subtitles_result['subtitle_path']}"
                )
            else:
                text_content.text += (
                    f"\nSubtitle generation failed: "
                    f"{subtitles_result.get('error', '')}"
                )

            # Step 4: Format video (pass highlights so it clips around the best moment)
            text_content.status_message = f"Formatting for {format_type}..."
            self.output_message.push_update()

            format_result = self.tool.format_video(
                video_path, format_type, highlights=highlights
            )
            if format_result["success"]:
                text_content.text += f"\nFormatted video: {format_result['output_path']}"
            else:
                raise Exception(
                    f"Formatting failed: {format_result.get('error', 'Unknown error')}"
                )

            # Success
            text_content.status = MsgStatus.success
            text_content.status_message = "Video processing completed successfully"
            self.output_message.publish()

            return AgentResponse(
                status=AgentStatus.SUCCESS,
                message="Video processed successfully with local tools",
                data={
                    "video_path": video_path,
                    "formatted_path": format_result.get("output_path"),
                    "subtitles_path": (
                        subtitles_result.get("subtitle_path")
                        if subtitles_result["success"]
                        else None
                    ),
                    "highlights": highlights,
                },
            )

        except Exception:
            self._cleanup_file(video_path)
            raise

    def _run_videodb(
        self,
        url: str,
        moment_types: List[str],
        language: str,
        format_type: str,
    ) -> AgentResponse:
        text_content = self.output_message.content[-1]

        # Step 1: Upload video to VideoDB
        text_content.status_message = "Uploading video to VideoDB..."
        self.output_message.push_update()

        try:
            upload_result = self.tool.upload(url, source_type="url", media_type="video")
            video_id = upload_result["id"]
            text_content.text += f"\nUploaded video: {upload_result['name']}"
        except Exception as e:
            raise Exception(f"VideoDB upload failed: {str(e)}")

        # Step 2: Generate subtitles (transcript)
        text_content.status_message = "Generating subtitles via VideoDB..."
        self.output_message.push_update()

        transcript = None
        try:
            transcript = self.tool.get_transcript(video_id, text=False)
            text_content.text += "\nGenerated subtitles (transcript available)"
        except Exception as e:
            text_content.text += f"\nSubtitle generation failed: {str(e)}"

        # Step 3: Extract highlights (scene indexing)
        text_content.status_message = "Extracting highlights via VideoDB..."
        self.output_message.push_update()

        highlights: List[Dict[str, Any]] = []
        try:
            self.tool.index_scene(video_id)
            scene_index = self.tool.list_scene_index(video_id)
            for scene in scene_index:
                # VideoDB SDK returns scene objects with attributes, not dicts.
                # Use getattr for safe attribute access with fallbacks.
                highlights.append(
                    {
                        "timestamp": getattr(scene, "start_time", 0),
                        "type": "scene_change",
                        "description": getattr(scene, "description", "Scene change"),
                    }
                )
            text_content.text += f"\nExtracted {len(highlights)} highlights"
        except Exception as e:
            text_content.text += f"\nHighlights extraction failed: {str(e)}"

        # Step 4: Format video (for VideoDB, use stream URL)
        text_content.status_message = "Preparing video stream..."
        self.output_message.push_update()

        try:
            video_info = self.tool.get_video(video_id)
            output_path = video_info["stream_url"]
            text_content.text += f"\nVideo stream ready: {output_path}"
        except Exception as e:
            raise Exception(f"VideoDB stream preparation failed: {str(e)}")

        # Success
        text_content.status = MsgStatus.success
        text_content.status_message = "Video processing completed via VideoDB"
        self.output_message.publish()

        return AgentResponse(
            status=AgentStatus.SUCCESS,
            message="Video processed successfully via VideoDB",
            data={
                "video_id": video_id,
                "video_stream_url": output_path,
                "subtitles": transcript,
                "highlights": highlights,
            },
        )

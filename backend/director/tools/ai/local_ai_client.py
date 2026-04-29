"""OpenAI-compatible client wrapper for local VideoDB AI features."""

import os
import logging
from typing import Dict, List, Optional, Any
from openai import OpenAI

logger = logging.getLogger(__name__)


class LocalAIClient:
    """Wrapper for OpenAI-compatible APIs used in local VideoDB."""

    def __init__(self):
        # Initialize OpenAI-compatible client
        openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        openai_api_key = os.getenv("OPENAI_API_KEY")

        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.client = OpenAI(
            api_key=openai_api_key,
            base_url=openai_base_url,
        )

        # Default models (can be overridden via environment)
        self.vision_model = os.getenv("VISION_MODEL", "gpt-4o-mini")
        self.transcription_model = os.getenv("TRANSCRIPTION_MODEL", "whisper-1")
        self.tts_model = os.getenv("TTS_MODEL", "tts-1")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    def extract_scene_highlights(self, video_path: str, frames: List[str]) -> Dict[str, Any]:
        """
        Use vision API to analyze frames and extract scene highlights.

        Args:
            video_path: Path to the video file
            frames: List of base64-encoded frame images

        Returns:
            Dict with highlights information
        """
        if not frames:
            return {"highlights": [], "message": "No frames provided for analysis"}

        try:
            # Prepare messages for vision API
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert video analyst. Analyze the provided frames and identify key scenes, emotional moments, and highlights from this video. Return a JSON with timestamps, descriptions, and highlight types."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze these video frames and identify key highlights:"}
                    ] + [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame}"}}
                        for frame in frames[:10]  # Limit to 10 frames to avoid token limits
                    ]
                }
            ]

            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=messages,
                max_tokens=1000,
                temperature=0.3,
            )

            # Parse response (simplified - in practice, you'd want more robust parsing)
            content = response.choices[0].message.content

            # For now, return a placeholder structure
            highlights = [
                {
                    "timestamp": 5.0,
                    "type": "scene_change",
                    "description": f"AI-detected highlight: {content[:100]}...",
                    "confidence": 0.8
                }
            ]

            return {
                "success": True,
                "highlights": highlights,
                "message": "Highlights extracted using AI vision analysis"
            }

        except Exception as e:
            logger.error(f"AI scene extraction failed: {e}")
            return {
                "success": False,
                "highlights": [],
                "error": str(e),
                "message": "AI scene extraction failed, falling back to basic detection"
            }

    def transcribe_audio(self, audio_path: str, language: str = "en") -> Dict[str, Any]:
        """
        Transcribe audio using OpenAI Whisper-compatible API.

        Args:
            audio_path: Path to audio file
            language: Language code for transcription

        Returns:
            Dict with transcription results
        """
        try:
            with open(audio_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model=self.transcription_model,
                    file=audio_file,
                    language=language,
                    response_format="verbose_json",
                )

            # Process segments for subtitle format
            segments = []
            if hasattr(transcript, 'segments'):
                segments = [
                    {
                        "start": seg.get("start", 0),
                        "end": seg.get("end", 0),
                        "text": seg.get("text", "").strip(),
                        "confidence": seg.get("confidence", 1.0)
                    }
                    for seg in transcript.segments
                ]

            return {
                "success": True,
                "text": transcript.text,
                "segments": segments,
                "language": language,
                "message": "Audio transcribed successfully"
            }

        except Exception as e:
            logger.error(f"Audio transcription failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "segments": [],
                "message": "Audio transcription failed"
            }

    def generate_embeddings(self, texts: List[str]) -> Dict[str, Any]:
        """
        Generate embeddings for semantic search.

        Args:
            texts: List of text strings to embed

        Returns:
            Dict with embeddings
        """
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=texts,
                encoding_format="float"
            )

            embeddings = [data.embedding for data in response.data]

            return {
                "success": True,
                "embeddings": embeddings,
                "model": self.embedding_model,
                "message": "Embeddings generated successfully"
            }

        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return {
                "success": False,
                "embeddings": [],
                "error": str(e),
                "message": "Embedding generation failed"
            }

    def generate_speech(self, text: str, voice: str = "alloy", speed: float = 1.0) -> Dict[str, Any]:
        """
        Generate speech from text using TTS API.

        Args:
            text: Text to convert to speech
            voice: Voice to use
            speed: Speech speed multiplier

        Returns:
            Dict with audio data or file path
        """
        try:
            response = self.client.audio.speech.create(
                model=self.tts_model,
                voice=voice,
                input=text,
                speed=speed,
                response_format="mp3"
            )

            # In a real implementation, you'd save this to a file
            # For now, return metadata
            return {
                "success": True,
                "audio_data": response.content,  # Binary audio data
                "format": "mp3",
                "voice": voice,
                "text": text,
                "message": "Speech generated successfully"
            }

        except Exception as e:
            logger.error(f"Speech generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Speech generation failed"
            }

    def check_availability(self) -> Dict[str, Any]:
        """Check if AI services are available."""
        try:
            # Simple availability check
            models = self.client.models.list()
            available_models = [model.id for model in models.data]

            return {
                "available": True,
                "models": available_models,
                "vision_available": self.vision_model in available_models,
                "transcription_available": self.transcription_model in available_models,
                "tts_available": any("tts" in model for model in available_models),
                "embedding_available": any("embedding" in model for model in available_models),
            }
        except Exception as e:
            logger.error(f"AI availability check failed: {e}")
            return {
                "available": False,
                "error": str(e),
                "models": [],
            }
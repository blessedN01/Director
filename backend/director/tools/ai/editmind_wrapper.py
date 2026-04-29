import requests
import os
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class EditMindWrapper:
    def __init__(self):
        self.ml_host = os.getenv("EDITMIND_ML_HOST", "http://localhost:8765")
        self.background_host = os.getenv("EDITMIND_BACKGROUND_HOST", "http://localhost:4000")
        self.chroma_host = os.getenv("EDITMIND_CHROMA_HOST", "http://localhost:8000")

    def get_transcript(self, video_path: str) -> Optional[str]:
        """Get transcript for video using EditMind ML service."""
        try:
            # Assume ML service has /transcribe endpoint
            response = requests.post(
                f"{self.ml_host}/transcribe",
                json={"video_path": video_path},
                timeout=120
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("transcript")
            else:
                logger.error(f"Failed to get transcript: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error getting transcript: {e}")
            return None

    def index_scenes(self, video_path: str) -> List[Dict[str, Any]]:
        """Index scenes using EditMind detection."""
        try:
            # Assume /index_scenes endpoint
            response = requests.post(
                f"{self.ml_host}/index_scenes",
                json={"video_path": video_path},
                timeout=120
            )
            if response.status_code == 200:
                return response.json().get("scenes", [])
            else:
                logger.error(f"Failed to index scenes: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error indexing scenes: {e}")
            return []

    def semantic_search(self, query: str, video_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Perform semantic search using EditMind ChromaDB."""
        try:
            # Use ChromaDB API or assume endpoint
            # For simplicity, assume background has /search
            payload = {"query": query, "limit": limit}
            if video_id:
                payload["video_id"] = video_id
            response = requests.post(
                f"{self.background_host}/search",
                json=payload,
                timeout=30
            )
            if response.status_code == 200:
                return response.json().get("results", [])
            else:
                logger.error(f"Failed to search: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
"""REST API for Local VideoDB using FastAPI."""

import os
import logging
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

from director.tools.ai.videodb_local_tool import LocalVideoDBTool

logger = logging.getLogger(__name__)

app = FastAPI(title="Local VideoDB API")

tool = LocalVideoDBTool(collection_id="default")


class CollectionRequest(BaseModel):
    name: str
    description: str = ""


class VideoProcessRequest(BaseModel):
    url: str
    format_type: str = "tiktok"
    language: str = "en"


class SubtitleRequest(BaseModel):
    style: Optional[dict] = None
    save_at: Optional[str] = None


class TranslateRequest(BaseModel):
    language: str
    additional_notes: Optional[str] = None


class DubRequest(BaseModel):
    language_code: str


class TimelineRequest(BaseModel):
    segments: List[list]


class BrandkitRequest(BaseModel):
    intro_video_id: Optional[str] = None
    outro_video_id: Optional[str] = None
    brand_image_id: Optional[str] = None


class GenerateVoiceRequest(BaseModel):
    text: str
    voice_name: str = "alloy"
    config: dict = {}
    save_at: Optional[str] = None


class GenerateMusicRequest(BaseModel):
    prompt: str
    duration: float = 10.0
    save_at: Optional[str] = None


class GenerateSoundEffectRequest(BaseModel):
    prompt: str
    duration: float = 5.0
    config: dict = {}


class GenerateVideoRequest(BaseModel):
    prompt: str
    duration: float = 5.0
    save_at: Optional[str] = None


class GenerateImageRequest(BaseModel):
    prompt: str
    aspect_ratio: str = "16:9"
    save_at: Optional[str] = None


# --- Collection endpoints ---

@app.post("/collections")
def create_collection(request: CollectionRequest):
    return tool.create_collection(request.name, request.description)


@app.get("/collections")
def get_collections():
    return tool.get_collections()


@app.get("/collections/{collection_id}")
def get_collection(collection_id: str):
    old_id = tool.collection_id
    tool.collection_id = collection_id
    try:
        return tool.get_collection()
    finally:
        tool.collection_id = old_id


@app.delete("/collections/{collection_id}")
def delete_collection(collection_id: str):
    old_id = tool.collection_id
    tool.collection_id = collection_id
    try:
        return tool.delete_collection()
    finally:
        tool.collection_id = old_id


# --- Asset listing endpoints ---

@app.get("/collections/{collection_id}/assets")
def get_assets(collection_id: str, type: Optional[str] = Query(None)):
    old_id = tool.collection_id
    tool.collection_id = collection_id
    try:
        if type == "video":
            return tool.get_videos()
        elif type == "audio":
            return tool.get_audios()
        elif type == "image":
            return tool.get_images()
        else:
            videos = tool.get_videos()
            audios = tool.get_audios()
            images = tool.get_images()
            return {"videos": videos, "audios": audios, "images": images}
    finally:
        tool.collection_id = old_id


# --- Upload endpoint ---

@app.post("/assets/upload")
async def upload_asset(
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
    media_type: str = Form("video"),
    name: Optional[str] = Form(None)
):
    if file:
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        try:
            result = tool.upload(temp_path, source_type="file", media_type=media_type, name=name or file.filename)
            return result
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    elif url:
        return tool.upload(url, source_type="url", media_type=media_type, name=name)
    else:
        raise HTTPException(status_code=400, detail="Either file or url must be provided")


# --- Video endpoints ---

@app.get("/videos")
def list_videos():
    return tool.get_videos()


@app.get("/videos/{video_id}")
def get_video(video_id: str):
    try:
        return tool.get_video(video_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/videos/{video_id}")
def delete_video(video_id: str):
    try:
        return tool.delete_video(video_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/videos/{video_id}/process")
def process_video(video_id: str, request: VideoProcessRequest):
    video_info = tool.get_video(video_id)
    transcript = tool.get_transcript(video_id, text=True)
    scenes = tool.index_scenes(video_id)

    return {
        "video_id": video_id,
        "subtitles_generated": bool(transcript),
        "scenes_detected": len(scenes),
        "video_info": video_info,
    }


@app.get("/videos/{video_id}/transcript")
def get_transcript(video_id: str, text: bool = True):
    try:
        result = tool.get_transcript(video_id, text=text)
        if text:
            return {"video_id": video_id, "transcript": result}
        return {"video_id": video_id, "transcript": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/videos/{video_id}/index-scenes")
def index_scenes(video_id: str):
    try:
        scenes = tool.index_scenes(video_id)
        return {"video_id": video_id, "scenes": scenes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/videos/{video_id}/scene-index")
def list_scene_index(video_id: str):
    return {"video_id": video_id, "scenes": tool.list_scene_index(video_id)}


@app.post("/videos/{video_id}/index-spoken-words")
def index_spoken_words(video_id: str):
    try:
        return tool.index_spoken_words(video_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/videos/{video_id}/extract-frame")
def extract_frame(video_id: str, timestamp: float = Query(5.0)):
    try:
        return tool.extract_frame(video_id, timestamp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/videos/{video_id}/add-subtitle")
def add_subtitle(video_id: str, request: SubtitleRequest):
    try:
        return tool.add_subtitle(video_id, style=request.style, save_at=request.save_at)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/videos/{video_id}/translate")
def translate_transcript(video_id: str, request: TranslateRequest):
    try:
        return tool.translate_transcript(video_id, request.language, request.additional_notes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/videos/{video_id}/dub")
def dub_video(video_id: str, request: DubRequest):
    try:
        return tool.dub_video(video_id, request.language_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/videos/{video_id}/stream")
def generate_video_stream(video_id: str, request: TimelineRequest):
    try:
        timeline = [tuple(seg) for seg in request.segments]
        return tool.generate_video_stream(video_id, timeline)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/videos/{video_id}/brandkit")
def add_brandkit(video_id: str, request: BrandkitRequest):
    try:
        return tool.add_brandkit(
            video_id,
            intro_video_id=request.intro_video_id,
            outro_video_id=request.outro_video_id,
            brand_image_id=request.brand_image_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Audio endpoints ---

@app.get("/audios")
def list_audios():
    return tool.get_audios()


@app.get("/audios/{audio_id}")
def get_audio(audio_id: str):
    try:
        return tool.get_audio(audio_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/audios/{audio_id}")
def delete_audio(audio_id: str):
    try:
        return tool.delete_audio(audio_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/audios/{audio_id}/url")
def generate_audio_url(audio_id: str):
    try:
        url = tool.generate_audio_url(audio_id)
        return {"url": url}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# --- Image endpoints ---

@app.get("/images")
def list_images():
    return tool.get_images()


@app.get("/images/{image_id}")
def get_image(image_id: str):
    try:
        return tool.get_image(image_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/images/{image_id}")
def delete_image(image_id: str):
    try:
        return tool.delete_image(image_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/images/{image_id}/url")
def generate_image_url(image_id: str):
    try:
        url = tool.generate_image_url(image_id)
        return {"url": url}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# --- Search endpoints ---

@app.post("/search")
def search(query: str, type: str = "semantic", video_id: Optional[str] = None):
    if type == "semantic":
        return tool.semantic_search(query, video_id=video_id)
    elif type == "keyword":
        return tool.keyword_search(query, video_id=video_id)
    else:
        raise HTTPException(status_code=400, detail="Invalid search type. Use 'semantic' or 'keyword'.")


# --- Generation endpoints ---

@app.post("/generate/video")
def generate_video(request: GenerateVideoRequest):
    try:
        return tool.generate_video(request.prompt, request.duration, save_at=request.save_at)
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/image")
def generate_image(request: GenerateImageRequest):
    try:
        return tool.generate_image(request.prompt, request.aspect_ratio, save_at=request.save_at)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/voice")
def generate_voice(request: GenerateVoiceRequest):
    try:
        save_at = request.save_at or os.path.join(
            "director/downloads", f"voice_{int(time.time())}.mp3"
        )
        return tool.generate_voice(request.text, request.voice_name, request.config, save_at)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/music")
def generate_music(request: GenerateMusicRequest):
    try:
        save_at = request.save_at or os.path.join(
            "director/downloads", f"music_{int(time.time())}.mp3"
        )
        return tool.generate_music(request.prompt, request.duration, save_at)
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/sound-effect")
def generate_sound_effect(request: GenerateSoundEffectRequest):
    try:
        save_at = os.path.join(
            "director/downloads", f"sfx_{int(time.time())}.mp3"
        )
        return tool.generate_sound_effect(request.prompt, request.duration, request.config, save_at)
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- YouTube endpoint ---

@app.post("/youtube/search")
def youtube_search(query: str, count: int = 5, duration: Optional[str] = None):
    try:
        return tool.youtube_search(query, count=count, duration=duration)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Download endpoint ---

@app.post("/download")
def download(stream_link: str, name: Optional[str] = None):
    try:
        return tool.download(stream_link, name=name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Stream endpoint ---

@app.get("/assets/{asset_id}/stream")
def get_asset_stream(asset_id: str):
    try:
        asset_info = tool.get_video(asset_id)
        file_path = asset_info.get("file_path")

        if file_path and os.path.exists(file_path):
            return FileResponse(file_path, media_type="video/mp4")
        else:
            raise HTTPException(status_code=404, detail="Asset not found")
    except ValueError:
        try:
            asset_info = tool.get_audio(asset_id)
            file_path = asset_info.get("file_path")
            if file_path and os.path.exists(file_path):
                return FileResponse(file_path, media_type="audio/mpeg")
        except ValueError:
            pass
        raise HTTPException(status_code=404, detail="Asset not found")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


if __name__ == "__main__":
    import time
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

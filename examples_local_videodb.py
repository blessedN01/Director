#!/usr/bin/env python3
"""
Local VideoDB Usage Examples

This script demonstrates practical usage of the local VideoDB implementation.
"""

import os
import sys
import tempfile

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from director.tools.local_videodb_tool import LocalVideoDBTool

def main():
    print("🚀 Local VideoDB Examples")
    print("=" * 50)

    # Initialize tool
    tool = LocalVideoDBTool(collection_id="examples")

    print("📁 Created collection:", tool.collection_id)

    # Example 1: Basic CRUD
    print("\n1. Basic CRUD Operations")
    print("-" * 30)

    # Create temporary files
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as vf:
        vf.write(b"fake video content")
        video_path = vf.name

    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as af:
        af.write(b"fake audio content")
        audio_path = af.name

    try:
        # Upload assets
        video = tool.upload(video_path, source_type="file", media_type="video", name="demo.mp4")
        audio = tool.upload(audio_path, source_type="file", media_type="audio", name="demo.mp3")

        print(f"✓ Uploaded video: {video['id']}")
        print(f"✓ Uploaded audio: {audio['id']}")

        # Get assets
        v_info = tool.get_video(video['id'])
        a_info = tool.get_audio(audio['id'])

        print(f"✓ Retrieved video: {v_info['name']}")
        print(f"✓ Retrieved audio: {a_info['name']}")

        # List assets
        videos = tool.get_videos()
        audios = tool.get_audios()

        print(f"✓ Collection has {len(videos)} videos, {len(audios)} audios")

        # Generate URLs
        audio_url = tool.generate_audio_url(audio['id'])
        print(f"✓ Audio URL: {audio_url}")

        # Clean up
        tool.delete_video(video['id'])
        tool.delete_audio(audio['id'])
        print("✓ Assets deleted")

    finally:
        # Clean up temp files
        for path in [video_path, audio_path]:
            if os.path.exists(path):
                os.unlink(path)

    print("\n2. Available Features")
    print("-" * 30)
    print("✓ Collection management (create, list, delete)")
    print("✓ Asset CRUD (videos, audios, images)")
    print("✓ Video processing (transcripts, scenes, subtitles)")
    print("✓ Search (semantic and keyword)")
    print("✓ Media generation (images, videos, audio, music)")
    print("✓ YouTube integration (search, download)")
    print("✓ Timeline composition")
    print("✓ REST API (40+ endpoints)")
    print("✓ CLI tool")

    print("\n3. Getting Started")
    print("-" * 30)
    print("• Set OPENAI_API_KEY for AI features")
    print("• Install FFmpeg: apt install ffmpeg (Linux)")
    print("• Install yt-dlp: pip install yt-dlp")
    print("• Run: python local_videodb_api.py")
    print("• API docs: http://localhost:8000/docs")

    print("\n4. Example Commands")
    print("-" * 30)
    print("# CLI usage")
    print("python local_videodb_cli.py collection create my_videos")
    print("python local_videodb_cli.py asset upload video.mp4 --type video")
    print("python local_videodb_cli.py search 'meeting notes'")
    print()
    print("# Python API")
    print("from director.tools.local_videodb_tool import LocalVideoDBTool")
    print("tool = LocalVideoDBTool()")
    print("video = tool.upload('file.mp4', source_type='file', media_type='video')")
    print("transcript = tool.get_transcript(video['id'])")

    print("\n✅ Examples completed successfully!")
    print("\n📖 See README_LOCAL_VIDEODB.md for detailed documentation")

if __name__ == "__main__":
    main()</content>
<parameter name="filePath">C:\Users\ASUS PC\Desktop\Projects\Director\examples_local_videodb.py
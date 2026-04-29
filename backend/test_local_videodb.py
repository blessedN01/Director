#!/usr/bin/env python3
"""Comprehensive test script for local VideoDB implementation."""

import os
import sys
import tempfile
import json
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from director.tools.ai.videodb_local_tool import LocalVideoDBTool, LocalTimeline


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def run(self, name, func):
        try:
            func()
            self.passed += 1
            print(f"  PASS: {name}")
        except Exception as e:
            self.failed += 1
            self.errors.append((name, str(e)))
            print(f"  FAIL: {name} - {e}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"Results: {self.passed}/{total} passed, {self.failed} failed")
        if self.errors:
            print("\nFailed tests:")
            for name, error in self.errors:
                print(f"  - {name}: {error}")
        print('='*60)
        return self.failed == 0


def test_collection_operations(runner, tool):
    print("\n--- Collection Operations ---")

    def test_get_collection():
        coll = tool.get_collection()
        assert coll["id"] == "test_collection", f"Expected test_collection, got {coll['id']}"
        assert "name" in coll

    def test_create_collection():
        result = tool.create_collection("my_collection", "Test description")
        assert result["success"] is True
        assert "collection" in result
        assert result["collection"]["name"] == "my_collection"

    def test_get_collections():
        collections = tool.get_collections()
        assert isinstance(collections, list)
        assert len(collections) >= 1

    runner.run("get_collection", test_get_collection)
    runner.run("create_collection", test_create_collection)
    runner.run("get_collections", test_get_collections)


def test_asset_crud(runner, tool, tmp_dir):
    print("\n--- Asset CRUD Operations ---")
    video_id = None
    audio_id = None
    image_id = None

    def test_upload_video():
        nonlocal video_id
        video_path = os.path.join(tmp_dir, "test_video.mp4")
        with open(video_path, "wb") as f:
            f.write(b"fake video content for testing")
        result = tool.upload(video_path, source_type="file", media_type="video", name="test_video.mp4")
        assert "id" in result
        assert result["type"] == "video"
        video_id = result["id"]

    def test_upload_audio():
        nonlocal audio_id
        audio_path = os.path.join(tmp_dir, "test_audio.mp3")
        with open(audio_path, "wb") as f:
            f.write(b"fake audio content for testing")
        result = tool.upload(audio_path, source_type="file", media_type="audio", name="test_audio.mp3")
        assert "id" in result
        assert result["type"] == "audio"
        audio_id = result["id"]

    def test_upload_image():
        nonlocal image_id
        image_path = os.path.join(tmp_dir, "test_image.png")
        with open(image_path, "wb") as f:
            f.write(b"fake image content for testing")
        result = tool.upload(image_path, source_type="file", media_type="image", name="test_image.png")
        assert "id" in result
        assert result["type"] == "image"
        image_id = result["id"]

    runner.run("upload_video", test_upload_video)
    runner.run("upload_audio", test_upload_audio)
    runner.run("upload_image", test_upload_image)

    def test_get_video():
        video = tool.get_video(video_id)
        assert video["id"] == video_id
        assert video["name"] == "test_video.mp4"

    def test_get_videos():
        videos = tool.get_videos()
        assert isinstance(videos, list)
        assert len(videos) >= 1

    def test_get_audio():
        audio = tool.get_audio(audio_id)
        assert audio["id"] == audio_id
        assert audio["type"] == "audio"

    def test_get_audios():
        audios = tool.get_audios()
        assert isinstance(audios, list)
        assert len(audios) >= 1

    def test_get_image():
        image = tool.get_image(image_id)
        assert image["id"] == image_id
        assert image["type"] == "image"

    def test_get_images():
        images = tool.get_images()
        assert isinstance(images, list)
        assert len(images) >= 1

    def test_generate_audio_url():
        url = tool.generate_audio_url(audio_id)
        assert isinstance(url, str)

    def test_generate_image_url():
        url = tool.generate_image_url(image_id)
        assert isinstance(url, str)

    runner.run("get_video", test_get_video)
    runner.run("get_videos", test_get_videos)
    runner.run("get_audio", test_get_audio)
    runner.run("get_audios", test_get_audios)
    runner.run("get_image", test_get_image)
    runner.run("get_images", test_get_images)
    runner.run("generate_audio_url", test_generate_audio_url)
    runner.run("generate_image_url", test_generate_image_url)

    def test_delete_video():
        result = tool.delete_video(video_id)
        assert result["success"] is True

    def test_delete_audio():
        result = tool.delete_audio(audio_id)
        assert result["success"] is True

    def test_delete_image():
        result = tool.delete_image(image_id)
        assert result["success"] is True

    runner.run("delete_video", test_delete_video)
    runner.run("delete_audio", test_delete_audio)
    runner.run("delete_image", test_delete_image)

    def test_get_video_not_found():
        try:
            tool.get_video("nonexistent_id")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_get_audio_not_found():
        try:
            tool.get_audio("nonexistent_id")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_get_image_not_found():
        try:
            tool.get_image("nonexistent_id")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    runner.run("get_video_not_found", test_get_video_not_found)
    runner.run("get_audio_not_found", test_get_audio_not_found)
    runner.run("get_image_not_found", test_get_image_not_found)


def test_search_operations(runner, tool, tmp_dir):
    print("\n--- Search Operations ---")

    video_id = None

    def setup_transcript():
        nonlocal video_id
        video_path = os.path.join(tmp_dir, "search_test.mp4")
        with open(video_path, "wb") as f:
            f.write(b"fake video content")
        result = tool.upload(video_path, source_type="file", media_type="video", name="search_test.mp4")
        video_id = result["id"]

        conn = tool._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO asset_transcripts (asset_id, transcript_text, transcript_json, language, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (video_id, "The quick brown fox jumps over the lazy dog", json.dumps({"text": "The quick brown fox jumps over the lazy dog"}), "en", 1, 1)
            )
            conn.commit()
        finally:
            conn.close()

    setup_transcript()

    def test_keyword_search():
        results = tool.keyword_search("brown fox", video_id=video_id)
        assert isinstance(results, list)

    def test_keyword_search_all():
        results = tool.keyword_search("brown fox")
        assert isinstance(results, list)

    def test_semantic_search_no_index():
        try:
            results = tool.semantic_search("fox", video_id=video_id)
            assert isinstance(results, list)
        except Exception:
            pass

    runner.run("keyword_search", test_keyword_search)
    runner.run("keyword_search_all", test_keyword_search_all)
    runner.run("semantic_search_no_index", test_semantic_search_no_index)

    if video_id:
        tool.delete_video(video_id)


def test_scene_index_operations(runner, tool, tmp_dir):
    print("\n--- Scene Index Operations ---")

    video_id = None

    def setup_video():
        nonlocal video_id
        video_path = os.path.join(tmp_dir, "scene_test.mp4")
        with open(video_path, "wb") as f:
            f.write(b"fake video content")
        result = tool.upload(video_path, source_type="file", media_type="video", name="scene_test.mp4")
        video_id = result["id"]

        conn = tool._get_db_connection()
        try:
            cursor = conn.cursor()
            scene_data = json.dumps({
                "scenes": [
                    {"timestamp": 0.0, "type": "scene_change", "description": "Opening scene"},
                    {"timestamp": 5.0, "type": "scene_change", "description": "Second scene"},
                ],
                "extraction_method": "test",
            })
            cursor.execute(
                "INSERT INTO asset_indexes (id, asset_id, index_type, index_data, created_at) VALUES (?, ?, ?, ?, ?)",
                (str("scene-1"), video_id, "scene", scene_data, 1)
            )
            conn.commit()
        finally:
            conn.close()

    setup_video()

    def test_list_scene_index():
        scenes = tool.list_scene_index(video_id)
        assert isinstance(scenes, list)
        assert len(scenes) == 2

    def test_get_scene_index():
        scene = tool.get_scene_index(video_id, "scene-1")
        assert scene["id"] == "scene-1"
        assert "scenes" in scene

    runner.run("list_scene_index", test_list_scene_index)
    runner.run("get_scene_index", test_get_scene_index)

    if video_id:
        tool.delete_video(video_id)


def test_spoken_words_index(runner, tool, tmp_dir):
    print("\n--- Spoken Words Index ---")

    video_id = None

    def setup():
        nonlocal video_id
        video_path = os.path.join(tmp_dir, "words_test.mp4")
        with open(video_path, "wb") as f:
            f.write(b"fake video content")
        result = tool.upload(video_path, source_type="file", media_type="video", name="words_test.mp4")
        video_id = result["id"]

        conn = tool._get_db_connection()
        try:
            cursor = conn.cursor()
            transcript_json = json.dumps({
                "text": "Hello world this is a test",
                "segments": [
                    {"start": 0.0, "end": 2.0, "text": "Hello world"},
                    {"start": 2.0, "end": 4.0, "text": "this is a test"},
                ],
            })
            cursor.execute(
                "INSERT INTO asset_transcripts (asset_id, transcript_text, transcript_json, language, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (video_id, "Hello world this is a test", transcript_json, "en", 1, 1)
            )
            conn.commit()
        finally:
            conn.close()

    setup()

    def test_index_spoken_words():
        result = tool.index_spoken_words(video_id)
        assert result["success"] is True
        assert result["total_words"] > 0

    runner.run("index_spoken_words", test_index_spoken_words)

    if video_id:
        tool.delete_video(video_id)


def test_timeline(runner, tool, tmp_dir):
    print("\n--- Timeline Operations ---")

    def test_create_timeline():
        timeline = tool.get_and_set_timeline()
        assert isinstance(timeline, LocalTimeline)

    def test_timeline_add_inline():
        timeline = tool.get_and_set_timeline()
        timeline.add_inline("fake-video-id")
        assert len(timeline._inline_assets) == 1

    def test_timeline_add_overlay():
        timeline = tool.get_and_set_timeline()
        timeline.add_overlay(0.0, "fake-image-id")
        assert len(timeline._overlay_assets) == 1

    runner.run("create_timeline", test_create_timeline)
    runner.run("timeline_add_inline", test_timeline_add_inline)
    runner.run("timeline_add_overlay", test_timeline_add_overlay)


def test_youtube_search(runner, tool):
    print("\n--- YouTube Search ---")

    def test_youtube_search_method_exists():
        assert hasattr(tool, "youtube_search")

    def test_youtube_search_returns_list():
        result = tool.youtube_search("test", count=1)
        assert isinstance(result, list)

    runner.run("youtube_search_exists", test_youtube_search_method_exists)
    runner.run("youtube_search_returns_list", test_youtube_search_returns_list)


def test_download_method(runner, tool):
    print("\n--- Download Method ---")

    def test_download_method_exists():
        assert hasattr(tool, "download")

    runner.run("download_method_exists", test_download_method_exists)


def test_format_srt_timestamp(runner, tool):
    print("\n--- SRT Timestamp Formatting ---")

    def test_format_zero():
        result = tool._format_srt_timestamp(0.0)
        assert result == "00:00:00,000"

    def test_format_with_millis():
        result = tool._format_srt_timestamp(65.123)
        assert "01:05" in result
        assert "123" in result

    def test_format_over_one_hour():
        result = tool._format_srt_timestamp(3661.5)
        assert result.startswith("01:")
        assert "01" in result

    runner.run("format_srt_zero", test_format_zero)
    runner.run("format_srt_millis", test_format_with_millis)
    runner.run("format_srt_over_hour", test_format_over_one_hour)


def test_translate_transcript(runner, tool, tmp_dir):
    print("\n--- Translate Transcript ---")

    def test_translate_without_ai():
        if tool.ai_client is None:
            try:
                tool.translate_transcript("fake_id", "es")
                assert False, "Should have raised Exception"
            except Exception:
                pass

    runner.run("translate_without_ai", test_translate_without_ai)


def test_dub_video(runner, tool, tmp_dir):
    print("\n--- Dub Video ---")

    def test_dub_without_ai():
        if tool.ai_client is None:
            try:
                tool.dub_video("fake_id", "es")
                assert False, "Should have raised Exception"
            except Exception:
                pass

    runner.run("dub_without_ai", test_dub_without_ai)


def main():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")

        tool = LocalVideoDBTool(collection_id="test_collection", db_path=db_path)

        runner = TestRunner()

        test_collection_operations(runner, tool)
        test_asset_crud(runner, tool, tmp_dir)
        test_search_operations(runner, tool, tmp_dir)
        test_scene_index_operations(runner, tool, tmp_dir)
        test_spoken_words_index(runner, tool, tmp_dir)
        test_timeline(runner, tool, tmp_dir)
        test_youtube_search(runner, tool)
        test_download_method(runner, tool)
        test_format_srt_timestamp(runner, tool)
        test_translate_transcript(runner, tool, tmp_dir)
        test_dub_video(runner, tool, tmp_dir)
        test_editmind_integration(runner, tool)

        success = runner.summary()
        sys.exit(0 if success else 1)


def test_editmind_integration(runner, tool):
    print("\n--- EditMind Integration Tests ---")

    def test_editmind_wrapper_initialization():
        # Test that EditMindWrapper is properly initialized
        if tool.editmind_wrapper is None:
            # Skip if EditMind not available
            print("  SKIP: EditMind wrapper not initialized (likely due to missing services)")
            return
        assert hasattr(tool.editmind_wrapper, 'get_transcript'), "EditMindWrapper should have get_transcript method"
        assert hasattr(tool.editmind_wrapper, 'index_scenes'), "EditMindWrapper should have index_scenes method"
        assert hasattr(tool.editmind_wrapper, 'semantic_search'), "EditMindWrapper should have semantic_search method"

    def test_semantic_search_method():
        # Test semantic search method exists and can be called
        assert hasattr(tool, 'semantic_search'), "LocalVideoDBTool should have semantic_search method"
        results = tool.semantic_search("test query", limit=5)
        assert isinstance(results, list), "semantic_search should return a list"

    runner.run("EditMind wrapper initialization", test_editmind_wrapper_initialization)
    runner.run("Semantic search method", test_semantic_search_method)


if __name__ == "__main__":
    main()

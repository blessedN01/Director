#!/usr/bin/env python3
"""CLI tool for Local VideoDB operations."""

import argparse
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from director.tools.ai.videodb_local_tool import LocalVideoDBTool


def main():
    parser = argparse.ArgumentParser(description="Local VideoDB CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # --- Collection commands ---
    collection_parser = subparsers.add_parser("collection", help="Manage collections")
    collection_subparsers = collection_parser.add_subparsers(dest="subcommand")

    create_coll = collection_subparsers.add_parser("create", help="Create a collection")
    create_coll.add_argument("name", help="Collection name")
    create_coll.add_argument("--description", help="Collection description", default="")

    list_coll = collection_subparsers.add_parser("list", help="List all collections")

    delete_coll = collection_subparsers.add_parser("delete", help="Delete a collection")
    delete_coll.add_argument("collection_id", help="Collection ID")

    # --- Asset commands ---
    asset_parser = subparsers.add_parser("asset", help="Manage assets")
    asset_subparsers = asset_parser.add_subparsers(dest="subcommand")

    upload_asset = asset_subparsers.add_parser("upload", help="Upload a file")
    upload_asset.add_argument("file", help="Path to file to upload")
    upload_asset.add_argument("--collection", help="Collection ID", default="default")
    upload_asset.add_argument("--type", choices=["video", "audio", "image"], default="video", help="Media type")
    upload_asset.add_argument("--name", help="Asset name", default=None)

    list_assets = asset_subparsers.add_parser("list", help="List assets")
    list_assets.add_argument("--collection", help="Collection ID", default="default")
    list_assets.add_argument("--type", choices=["video", "audio", "image"], default=None, help="Filter by type")

    delete_asset = asset_subparsers.add_parser("delete", help="Delete an asset")
    delete_asset.add_argument("asset_id", help="Asset ID")
    delete_asset.add_argument("--type", choices=["video", "audio", "image"], default="video", help="Asset type")

    # --- Video commands ---
    video_parser = subparsers.add_parser("video", help="Video operations")
    video_subparsers = video_parser.add_subparsers(dest="subcommand")

    video_info = video_subparsers.add_parser("info", help="Get video info")
    video_info.add_argument("video_id", help="Video ID")

    video_process = video_subparsers.add_parser("process", help="Process a video")
    video_process.add_argument("video_id", help="Video ID")
    video_process.add_argument("--ai", action="store_true", help="Use AI features")

    video_transcript = video_subparsers.add_parser("transcript", help="Get transcript")
    video_transcript.add_argument("video_id", help="Video ID")
    video_transcript.add_argument("--json", action="store_true", help="Output as JSON")

    video_subtitle = video_subparsers.add_parser("subtitle", help="Add subtitles to video")
    video_subtitle.add_argument("video_id", help="Video ID")
    video_subtitle.add_argument("--save-at", help="Output path", default=None)

    video_translate = video_subparsers.add_parser("translate", help="Translate transcript")
    video_translate.add_argument("video_id", help="Video ID")
    video_translate.add_argument("language", help="Target language")
    video_translate.add_argument("--notes", help="Additional translation notes", default=None)

    video_dub = video_subparsers.add_parser("dub", help="Dub video to another language")
    video_dub.add_argument("video_id", help="Video ID")
    video_dub.add_argument("language_code", help="Target language code (e.g. es, fr)")

    video_frame = video_subparsers.add_parser("extract-frame", help="Extract a frame from video")
    video_frame.add_argument("video_id", help="Video ID")
    video_frame.add_argument("--timestamp", type=float, default=5.0, help="Timestamp in seconds")

    video_scenes = video_subparsers.add_parser("index-scenes", help="Index scenes in video")
    video_scenes.add_argument("video_id", help="Video ID")

    video_list_scenes = video_subparsers.add_parser("list-scenes", help="List scene index")
    video_list_scenes.add_argument("video_id", help="Video ID")

    video_index_words = video_subparsers.add_parser("index-words", help="Index spoken words")
    video_index_words.add_argument("video_id", help="Video ID")

    video_stream = video_subparsers.add_parser("stream", help="Generate video stream from timeline")
    video_stream.add_argument("video_id", help="Video ID")
    video_stream.add_argument("--segments", help="Timeline segments as JSON list, e.g. [[0,10],[20,30]]", required=True)

    video_brandkit = video_subparsers.add_parser("brandkit", help="Add brand kit to video")
    video_brandkit.add_argument("video_id", help="Video ID")
    video_brandkit.add_argument("--intro", help="Intro video ID", default=None)
    video_brandkit.add_argument("--outro", help="Outro video ID", default=None)
    video_brandkit.add_argument("--brand-image", help="Brand image ID", default=None)

    # --- Search commands ---
    search_parser = subparsers.add_parser("search", help="Search assets")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--type", choices=["semantic", "keyword"], default="semantic", help="Search type")
    search_parser.add_argument("--video-id", help="Specific video ID to search in")

    # --- YouTube commands ---
    yt_parser = subparsers.add_parser("youtube", help="YouTube search")
    yt_parser.add_argument("query", help="Search query")
    yt_parser.add_argument("--count", type=int, default=5, help="Number of results")
    yt_parser.add_argument("--duration", help="Duration filter", default=None)

    # --- Download command ---
    dl_parser = subparsers.add_parser("download", help="Download a video from URL")
    dl_parser.add_argument("url", help="URL to download")
    dl_parser.add_argument("--name", help="File name", default=None)

    # --- Generate commands ---
    gen_parser = subparsers.add_parser("generate", help="Generate media")
    gen_subparsers = gen_parser.add_subparsers(dest="subcommand")

    gen_image = gen_subparsers.add_parser("image", help="Generate image from prompt")
    gen_image.add_argument("prompt", help="Image prompt")
    gen_image.add_argument("--aspect-ratio", default="16:9", help="Aspect ratio")
    gen_image.add_argument("--save-at", default=None, help="Save path")

    gen_video = gen_subparsers.add_parser("video", help="Generate video from prompt")
    gen_video.add_argument("prompt", help="Video prompt")
    gen_video.add_argument("--duration", type=float, default=5.0, help="Duration in seconds")
    gen_video.add_argument("--save-at", default=None, help="Save path")

    gen_voice = gen_subparsers.add_parser("voice", help="Generate voice from text")
    gen_voice.add_argument("text", help="Text to speak")
    gen_voice.add_argument("--voice", default="alloy", help="Voice name")
    gen_voice.add_argument("--save-at", required=True, help="Save path")

    gen_music = gen_subparsers.add_parser("music", help="Generate music from prompt")
    gen_music.add_argument("prompt", help="Music prompt")
    gen_music.add_argument("--duration", type=float, default=10.0, help="Duration in seconds")
    gen_music.add_argument("--save-at", required=True, help="Save path")

    gen_sfx = gen_subparsers.add_parser("sound-effect", help="Generate sound effect")
    gen_sfx.add_argument("prompt", help="Sound effect prompt")
    gen_sfx.add_argument("--duration", type=float, default=5.0, help="Duration in seconds")
    gen_sfx.add_argument("--save-at", required=True, help="Save path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        tool = LocalVideoDBTool(collection_id="default")

        if args.command == "collection":
            if args.subcommand == "create":
                result = tool.create_collection(args.name, args.description)
                print(f"Collection created: {result['collection']['id']}")
            elif args.subcommand == "list":
                collections = tool.get_collections()
                for coll in collections:
                    print(f"{coll['id']}: {coll['name']} - {coll.get('description', '')}")
            elif args.subcommand == "delete":
                tool.collection_id = args.collection_id
                result = tool.delete_collection()
                print(result["message"])
            else:
                collection_parser.print_help()

        elif args.command == "asset":
            if args.subcommand == "upload":
                tool.collection_id = args.collection
                result = tool.upload(args.file, source_type="file", media_type=args.type, name=args.name)
                print(f"Asset uploaded: {result['id']}")
                print(f"  File: {result.get('file_path', 'N/A')}")
            elif args.subcommand == "list":
                tool.collection_id = args.collection
                if args.type == "video" or args.type is None:
                    for v in tool.get_videos():
                        print(f"  [video] {v['id']}: {v['name']} ({v.get('length', 0):.1f}s)")
                if args.type == "audio" or args.type is None:
                    for a in tool.get_audios():
                        print(f"  [audio] {a['id']}: {a['name']} ({a.get('length', 0):.1f}s)")
                if args.type == "image" or args.type is None:
                    for i in tool.get_images():
                        print(f"  [image] {i['id']}: {i['name']}")
            elif args.subcommand == "delete":
                if args.type == "video":
                    result = tool.delete_video(args.asset_id)
                elif args.type == "audio":
                    result = tool.delete_audio(args.asset_id)
                elif args.type == "image":
                    result = tool.delete_image(args.asset_id)
                else:
                    result = tool.delete_video(args.asset_id)
                print(result["message"])
            else:
                asset_parser.print_help()

        elif args.command == "video":
            if args.subcommand == "info":
                video = tool.get_video(args.video_id)
                print(f"ID: {video['id']}")
                print(f"Name: {video['name']}")
                print(f"Length: {video.get('length', 0):.1f}s")
                print(f"File: {video.get('file_path', 'N/A')}")
            elif args.subcommand == "process":
                video_info = tool.get_video(args.video_id)
                print(f"Processing video: {video_info['name']}")

                transcript = tool.get_transcript(args.video_id, text=True)
                print(f"Transcript generated: {len(transcript)} characters")

                scenes = tool.index_scenes(args.video_id)
                print(f"Scenes detected: {len(scenes)}")
            elif args.subcommand == "transcript":
                result = tool.get_transcript(args.video_id, text=not args.json)
                if args.json:
                    print(json.dumps(result, indent=2))
                else:
                    print(result)
            elif args.subcommand == "subtitle":
                result = tool.add_subtitle(args.video_id, save_at=args.save_at)
                print(f"Subtitled video: {result.get('file_path', 'N/A')}")
            elif args.subcommand == "translate":
                result = tool.translate_transcript(args.video_id, args.language, args.notes)
                print(f"Translated to {result['language']}:")
                print(result["text"][:500])
            elif args.subcommand == "dub":
                result = tool.dub_video(args.video_id, args.language_code)
                print(f"Dubbed video: {result.get('file_path', 'N/A')}")
            elif args.subcommand == "extract-frame":
                result = tool.extract_frame(args.video_id, args.timestamp)
                print(f"Frame extracted: {result.get('url', 'N/A')}")
            elif args.subcommand == "index-scenes":
                scenes = tool.index_scenes(args.video_id)
                print(f"Indexed {len(scenes)} scenes")
                for scene in scenes:
                    print(f"  {scene.get('timestamp', 'N/A')}s: {scene.get('description', 'N/A')}")
            elif args.subcommand == "list-scenes":
                scenes = tool.list_scene_index(args.video_id)
                print(f"Found {len(scenes)} scenes")
                for scene in scenes:
                    print(f"  {scene.get('timestamp', 'N/A')}s: {scene.get('description', 'N/A')}")
            elif args.subcommand == "index-words":
                result = tool.index_spoken_words(args.video_id)
                print(f"Indexed {result.get('total_words', 0)} words")
            elif args.subcommand == "stream":
                segments = json.loads(args.segments)
                timeline = [tuple(s) for s in segments]
                result = tool.generate_video_stream(args.video_id, timeline)
                print(f"Stream generated: {result.get('stream_url', 'N/A')}")
            elif args.subcommand == "brandkit":
                result = tool.add_brandkit(
                    args.video_id,
                    intro_video_id=args.intro,
                    outro_video_id=args.outro,
                    brand_image_id=args.brand_image,
                )
                print(f"Branded video: {result.get('stream_url', 'N/A')}")
            else:
                video_parser.print_help()

        elif args.command == "search":
            if args.type == "semantic":
                results = tool.semantic_search(args.query, video_id=args.video_id)
            else:
                results = tool.keyword_search(args.query, video_id=args.video_id)

            print(f"Found {len(results)} results:")
            for res in results:
                if "score" in res:
                    print(f"  [score={res['score']:.3f}] {res.get('text', res)}")
                else:
                    print(f"  {res}")

        elif args.command == "youtube":
            results = tool.youtube_search(args.query, count=args.count, duration=args.duration)
            print(f"Found {len(results)} results:")
            for r in results:
                print(f"  {r['id']}: {r['title']} ({r.get('duration', 'N/A')}) - {r.get('channel', 'N/A')}")
                print(f"    URL: {r['url']}")

        elif args.command == "download":
            result = tool.download(args.url, name=args.name)
            print(f"Downloaded to: {result['file_path']}")

        elif args.command == "generate":
            if args.subcommand == "image":
                result = tool.generate_image(args.prompt, args.aspect_ratio, save_at=args.save_at)
                print(f"Image generated: {result.get('url', 'N/A')}")
            elif args.subcommand == "video":
                result = tool.generate_video(args.prompt, args.duration, save_at=args.save_at)
                print(f"Video generated: {result.get('stream_url', result.get('url', 'N/A'))}")
            elif args.subcommand == "voice":
                result = tool.generate_voice(args.text, args.voice, {}, args.save_at)
                print(f"Voice generated: {result.get('url', 'N/A')}")
            elif args.subcommand == "music":
                result = tool.generate_music(args.prompt, args.duration, args.save_at)
                print(f"Music generated: {result.get('url', 'N/A')}")
            elif args.subcommand == "sound-effect":
                result = tool.generate_sound_effect(args.prompt, args.duration, {}, args.save_at)
                print(f"Sound effect generated: {result.get('url', 'N/A')}")
            else:
                gen_parser.print_help()

    except NotImplementedError as e:
        print(f"Not implemented: {e}")
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

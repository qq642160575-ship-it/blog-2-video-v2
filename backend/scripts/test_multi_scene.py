#!/usr/bin/env python3
"""
Test Multi-Scene Video Rendering
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.task_queue import TaskQueue
from app.services.subtitle_service import SubtitleService
from app.core.config import get_settings

settings = get_settings()


def test_multi_scene():
    print("=" * 70)
    print("Test Multi-Scene Video Rendering")
    print("=" * 70)
    print()

    # Create a test manifest with multiple scenes
    test_project_id = "test_multi_scene"

    scenes = [
        {
            "scene_id": "sc_multi_001",
            "order": 1,
            "template_type": "HookTitle",
            "start_ms": 0,
            "end_ms": 5000,
            "screen_text": ["场景 1", "这是第一个场景"],
            "voiceover": "这是第一个场景的旁白。",
            "template_props": {
                "screen_text": {
                    "title": "场景 1",
                    "subtitle": "这是第一个场景"
                }
            }
        },
        {
            "scene_id": "sc_multi_002",
            "order": 2,
            "template_type": "HookTitle",
            "start_ms": 5000,
            "end_ms": 10000,
            "screen_text": ["场景 2", "这是第二个场景"],
            "voiceover": "这是第二个场景的旁白。",
            "template_props": {
                "screen_text": {
                    "title": "场景 2",
                    "subtitle": "这是第二个场景"
                }
            }
        },
        {
            "scene_id": "sc_multi_003",
            "order": 3,
            "template_type": "HookTitle",
            "start_ms": 10000,
            "end_ms": 15000,
            "screen_text": ["场景 3", "这是第三个场景"],
            "voiceover": "这是第三个场景的旁白。",
            "template_props": {
                "screen_text": {
                    "title": "场景 3",
                    "subtitle": "这是第三个场景"
                }
            }
        }
    ]

    # Create manifest
    manifest = {
        "project_id": test_project_id,
        "total_duration": 15000,
        "scenes": scenes
    }

    # Save manifest
    manifest_dir = os.path.join(settings.storage_path, "manifests")
    os.makedirs(manifest_dir, exist_ok=True)
    manifest_path = os.path.join(manifest_dir, f"{test_project_id}_manifest.json")

    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"✓ Test manifest created: {manifest_path}")
    print(f"  Scenes: {len(scenes)}")
    print(f"  Total duration: 15s")
    print()

    # Generate subtitles for all scenes
    print("Generating subtitles for all scenes...")
    subtitle_service = SubtitleService()

    for scene in scenes:
        try:
            scene_subtitles = subtitle_service.generate_scene_subtitles(
                scene_id=scene["scene_id"],
                voiceover=scene["voiceover"],
                duration_sec=(scene["end_ms"] - scene["start_ms"]) // 1000
            )
            srt_path = subtitle_service.export_srt(scene_subtitles)
            print(f"  ✓ {scene['scene_id']}: {srt_path}")
        except Exception as e:
            print(f"  ⚠ {scene['scene_id']}: Failed - {e}")

    print()

    # Push to render queue
    print("Pushing render task to queue...")
    task_queue = TaskQueue()
    task_queue.push_render_task(
        job_id="test_multi_scene_job_001",
        project_id=test_project_id,
        manifest_url=manifest_path
    )
    print("  ✓ Render task queued")
    print()

    print("-" * 70)
    print("✓ Test setup complete!")
    print()
    print("Next steps:")
    print("1. Make sure Render Worker is running:")
    print("   cd render-worker && npm start")
    print()
    print("2. The worker will:")
    print("   - Render 3 scenes individually")
    print("   - Concatenate them into a single video")
    print("   - Clean up temporary scene videos")
    print()
    print("3. Check the output video at:")
    print(f"   backend/storage/videos/{test_project_id}/{test_project_id}.mp4")
    print("-" * 70)


if __name__ == "__main__":
    test_multi_scene()

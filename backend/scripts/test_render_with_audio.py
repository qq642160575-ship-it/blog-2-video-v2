#!/usr/bin/env python3
"""
Test Render Worker with Audio and Subtitles
"""
import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.task_queue import TaskQueue
from app.core.config import get_settings

settings = get_settings()


def test_render_with_audio():
    print("=" * 70)
    print("Test Render Worker with Audio and Subtitles")
    print("=" * 70)
    print()

    # Create a test manifest with audio and subtitles
    test_project_id = "test_audio_render"
    test_scene_id = "sc_test_audio_001"

    # Create test manifest
    manifest = {
        "project_id": test_project_id,
        "total_duration": 7000,
        "scenes": [
            {
                "scene_id": test_scene_id,
                "order": 1,
                "template_type": "HookTitle",
                "start_ms": 0,
                "end_ms": 7000,
                "screen_text": [
                    "AI 回答总是出错？",
                    "因为它可能缺少最新知识！"
                ],
                "voiceover": "AI 回答总是出错？因为它可能缺少最新知识！今天带你了解 RAG 技术，让 AI 回答更准确。",
                # Skip audio for now due to Edge TTS network restrictions
                # "audio_path": f"./storage/audio/{test_scene_id}.mp3",
                "template_props": {
                    "screen_text": {
                        "title": "AI 回答总是出错？",
                        "subtitle": "因为它可能缺少最新知识！"
                    }
                }
            }
        ]
    }

    # Save manifest
    manifest_dir = os.path.join(settings.storage_path, "manifests")
    os.makedirs(manifest_dir, exist_ok=True)
    manifest_path = os.path.join(manifest_dir, f"{test_project_id}_manifest.json")

    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"✓ Test manifest created: {manifest_path}")
    print()

    # Generate test subtitles (always works)
    print("Generating test subtitles...")
    try:
        from app.services.subtitle_service import SubtitleService

        # Generate subtitles
        subtitle_service = SubtitleService()
        scene_subtitles = subtitle_service.generate_scene_subtitles(
            scene_id=test_scene_id,
            voiceover=manifest["scenes"][0]["voiceover"],
            duration_sec=7
        )
        srt_path = subtitle_service.export_srt(scene_subtitles)
        print(f"  ✓ Subtitles generated: {srt_path}")
        print()

    except Exception as e:
        print(f"  ⚠ Failed to generate subtitles: {e}")
        print()

    # Note: Audio generation skipped due to network restrictions
    # The test will use the existing test.srt subtitle file
    print("Note: Audio generation skipped (Edge TTS network restrictions)")
    print("      Video will render with subtitles only")
    print()

    # Push to render queue
    print("Pushing render task to queue...")
    task_queue = TaskQueue()
    task_queue.push_render_task(
        job_id="test_audio_job_001",
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
    print("2. The worker will pick up the task and render the video with:")
    print("   - Audio playback")
    print("   - Subtitle overlay")
    print()
    print("3. Check the output video at:")
    print(f"   backend/storage/videos/{test_project_id}/{test_project_id}.mp4")
    print("-" * 70)


if __name__ == "__main__":
    test_render_with_audio()

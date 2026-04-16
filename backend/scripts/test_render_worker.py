#!/usr/bin/env python3
"""
Test Render Worker
Manually push a render task to the queue and verify the worker processes it
"""
import json
import redis
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings

def test_render_worker():
    print("=" * 70)
    print("Test Render Worker")
    print("=" * 70)
    print()

    # Connect to Redis
    r = redis.from_url(settings.redis_url)

    # Create a test render task
    test_task = {
        "job_id": "job_test_render",
        "project_id": "proj_test_123",
        "manifest_url": "storage/manifests/proj_test_123_manifest.json"
    }

    print("Step 1: Creating test manifest...")

    # Create test manifest
    manifest_dir = os.path.join(os.path.dirname(__file__), '..', 'storage', 'manifests')
    os.makedirs(manifest_dir, exist_ok=True)

    manifest_path = os.path.join(manifest_dir, 'proj_test_123_manifest.json')

    test_manifest = {
        "project_id": "proj_test_123",
        "job_id": "job_test_render",
        "scenes": [
            {
                "scene_id": "sc_proj_test_123_001",
                "scene_order": 1,
                "template_type": "hook_title",
                "duration_sec": 6,
                "screen_text": {
                    "title": "测试渲染",
                    "subtitle": "Render Worker 测试"
                },
                "voiceover": "这是一个测试渲染",
                "visual_params": {}
            }
        ]
    }

    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(test_manifest, f, ensure_ascii=False, indent=2)

    print(f"  ✓ Manifest created: {manifest_path}")
    print()

    print("Step 2: Pushing render task to queue...")
    r.lpush("render_queue", json.dumps(test_task))
    print("  ✓ Task pushed to render_queue")
    print()

    print("=" * 70)
    print("✓ Test setup complete!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Start the Render Worker:")
    print("     cd render-worker && npm start")
    print()
    print("  2. Watch the worker process the task")
    print()
    print("  3. Check the output video:")
    print("     ls -lh backend/storage/videos/proj_test_123/")
    print()

if __name__ == "__main__":
    try:
        test_render_worker()
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

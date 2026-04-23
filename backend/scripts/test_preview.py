#!/usr/bin/env python3
"""Test script for preview generation functionality"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.preview_service import PreviewService
from app.core.logging_config import get_logger

logger = get_logger("test")


async def test_preview_generation():
    """Test preview generation with sample data"""

    print("=" * 60)
    print("Testing Preview Generation")
    print("=" * 60)

    # Initialize service
    preview_service = PreviewService()

    # Test data for HookTitle template
    scene_data = {
        "scene_id": "test_scene_001",
        "template_type": "hook_title",
        "voiceover": "什么是 RAG？",
        "screen_text": ["什么是 RAG？", "检索增强生成技术解析"],
        "duration_sec": 6,
        "timeline_data": {},
        "visual_params": {}
    }

    print(f"\n📝 Scene Data:")
    print(f"  Template: {scene_data['template_type']}")
    print(f"  Title: {scene_data['screen_text'][0]}")
    print(f"  Subtitle: {scene_data['screen_text'][1]}")
    print(f"  Duration: {scene_data['duration_sec']}s")

    print(f"\n🎬 Generating preview...")

    try:
        preview_url = await preview_service.generate_preview(
            scene_id="test_scene_001",
            scene_data=scene_data,
            start_time=0,
            end_time=None,
            quality="low"
        )

        if preview_url:
            print(f"\n✅ Preview generated successfully!")
            print(f"   URL: {preview_url}")

            # Check if file exists
            preview_path = preview_service.preview_dir / "test_scene_001_preview.mp4"
            if preview_path.exists():
                file_size = preview_path.stat().st_size / 1024 / 1024  # MB
                print(f"   File: {preview_path}")
                print(f"   Size: {file_size:.2f} MB")
            else:
                print(f"   ⚠️  File not found at expected location")
        else:
            print(f"\n❌ Preview generation failed")
            print(f"   Check logs for details")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)


async def test_all_templates():
    """Test all template types"""

    print("\n" + "=" * 60)
    print("Testing All Template Types")
    print("=" * 60)

    preview_service = PreviewService()

    test_cases = [
        {
            "scene_id": "test_hook_title",
            "template_type": "hook_title",
            "screen_text": ["什么是 RAG？", "检索增强生成技术"],
            "voiceover": "什么是 RAG？",
            "duration_sec": 6,
            "visual_params": {}
        },
        {
            "scene_id": "test_bullet_explain",
            "template_type": "bullet_explain",
            "screen_text": ["RAG 核心流程", "检索相关资料", "筛选可信内容", "生成答案"],
            "voiceover": "RAG 的核心流程包括三个步骤",
            "duration_sec": 7,
            "visual_params": {"accent_color": "#f97316"}
        },
        {
            "scene_id": "test_compare",
            "template_type": "compare_process",
            "screen_text": ["普通大模型 vs RAG"],
            "voiceover": "让我们对比一下",
            "duration_sec": 7,
            "visual_params": {
                "left_title": "普通回答",
                "right_title": "RAG 回答",
                "left_points": ["知识可能过期", "来源不可见"],
                "right_points": ["知识可更新", "引用可追溯"],
                "footer_text": "核心差别：先检索，再生成"
            }
        }
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] Testing {test_case['template_type']}...")

        try:
            preview_url = await preview_service.generate_preview(
                scene_id=test_case["scene_id"],
                scene_data=test_case,
                start_time=0,
                end_time=None,
                quality="low"
            )

            if preview_url:
                print(f"  ✅ Success: {preview_url}")
                results.append((test_case['template_type'], True))
            else:
                print(f"  ❌ Failed")
                results.append((test_case['template_type'], False))

        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append((test_case['template_type'], False))

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    success_count = sum(1 for _, success in results if success)
    total_count = len(results)

    for template_type, success in results:
        status = "✅" if success else "❌"
        print(f"  {status} {template_type}")

    print(f"\nTotal: {success_count}/{total_count} passed")
    print("=" * 60)


if __name__ == "__main__":
    print("\n🎬 Preview Generation Test Suite\n")

    # Run basic test
    asyncio.run(test_preview_generation())

    # Ask if user wants to test all templates
    print("\n" + "=" * 60)
    response = input("Test all templates? (y/n): ")

    if response.lower() == 'y':
        asyncio.run(test_all_templates())

    print("\n✨ Test complete!\n")

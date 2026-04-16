#!/usr/bin/env python3
"""
Test Subtitle Service
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.subtitle_service import SubtitleService


def test_subtitle():
    print("=" * 70)
    print("Test Subtitle Service")
    print("=" * 70)
    print()

    # Test text
    test_text = "你好，这是一个字幕生成测试。RAG 技术通过结合检索和生成，显著提升了 AI 系统的准确性。它解决了知识更新和引用可信的问题。"

    print("Test text:")
    print("-" * 70)
    print(test_text)
    print("-" * 70)
    print()

    try:
        service = SubtitleService()

        # Test 1: Split text by punctuation
        print("Test 1: Split text by punctuation")
        segments = service.split_text_by_punctuation(test_text)
        print(f"✓ Split into {len(segments)} segments:")
        for i, seg in enumerate(segments, 1):
            print(f"  {i}. {seg}")
        print()

        # Test 2: Generate subtitles
        print("Test 2: Generate subtitles (8 seconds)")
        duration_ms = 8000
        subtitles = service.generate_subtitles(test_text, duration_ms)
        print(f"✓ Generated {len(subtitles)} subtitle segments:")
        for i, sub in enumerate(subtitles, 1):
            start_sec = sub.start_ms / 1000
            end_sec = sub.end_ms / 1000
            print(f"  {i}. [{start_sec:.2f}s - {end_sec:.2f}s] {sub.text}")
        print()

        # Test 3: Generate scene subtitles
        print("Test 3: Generate scene subtitles")
        scene_subtitles = service.generate_scene_subtitles(
            scene_id="sc_test_001",
            voiceover="AI 回答总是出错？因为它可能缺少最新知识！今天带你了解 RAG 技术，让 AI 回答更准确。",
            duration_sec=7
        )
        print(f"✓ Scene: {scene_subtitles.scene_id}")
        print(f"  Total duration: {scene_subtitles.total_duration_ms}ms")
        print(f"  Segments: {len(scene_subtitles.segments)}")
        for i, seg in enumerate(scene_subtitles.segments, 1):
            print(f"    {i}. [{seg.start_ms}ms - {seg.end_ms}ms] {seg.text}")
        print()

        # Test 4: Export to SRT
        print("Test 4: Export to SRT format")
        srt_path = service.export_srt(scene_subtitles, "test.srt")
        print(f"✓ SRT file saved: {srt_path}")
        print()
        print("SRT content:")
        print("-" * 70)
        with open(srt_path, 'r', encoding='utf-8') as f:
            print(f.read())
        print("-" * 70)
        print()

        # Test 5: Batch generation
        print("Test 5: Batch subtitle generation")
        scenes = [
            {
                "scene_id": "sc_batch_001",
                "voiceover": "第一个场景的旁白文本。",
                "duration_sec": 3
            },
            {
                "scene_id": "sc_batch_002",
                "voiceover": "第二个场景的旁白文本，内容稍微长一些。",
                "duration_sec": 4
            },
            {
                "scene_id": "sc_batch_003",
                "voiceover": "第三个场景的旁白文本，这是最后一个测试场景。",
                "duration_sec": 5
            }
        ]

        results = service.generate_batch(scenes)
        print(f"✓ Generated subtitles for {len(results)} scenes:")
        for scene_id, subtitles in results.items():
            print(f"  - {scene_id}: {len(subtitles.segments)} segments")
        print()

        print("-" * 70)
        print("✓ All tests completed successfully!")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_subtitle()

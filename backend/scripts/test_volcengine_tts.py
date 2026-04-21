#!/usr/bin/env python3
"""
Test Volcengine TTS Service
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.tts_service import TTSService


def test_volcengine_tts():
    print("=" * 70)
    print("Test Volcengine TTS Service")
    print("=" * 70)
    print()

    # Test text
    test_text = "你好，这是火山云语音合成测试。RAG 技术通过结合检索和生成，显著提升了 AI 系统的准确性。"

    print("Test text:")
    print("-" * 70)
    print(test_text)
    print("-" * 70)
    print()

    print("Synthesizing speech with Volcengine TTS...")
    print()

    try:
        # Create TTS service with volcengine provider
        service = TTSService(provider="volcengine")

        # Test 1: Basic synthesis
        print("Test 1: Basic synthesis (normal speed)")
        audio_path = service.synthesize_speech(
            text=test_text,
            output_filename="test_volcengine_normal.mp3"
        )
        print(f"✓ Audio generated: {audio_path}")
        print()

        # Test 2: Fast pace
        print("Test 2: Fast pace synthesis")
        audio_path_fast = service.synthesize_speech(
            text=test_text,
            output_filename="test_volcengine_fast.mp3",
            speaking_rate=1.2
        )
        print(f"✓ Audio generated: {audio_path_fast}")
        print()

        # Test 3: Slow pace
        print("Test 3: Slow pace synthesis")
        audio_path_slow = service.synthesize_speech(
            text=test_text,
            output_filename="test_volcengine_slow.mp3",
            speaking_rate=0.85
        )
        print(f"✓ Audio generated: {audio_path_slow}")
        print()

        # Test 4: Scene audio
        print("Test 4: Scene audio synthesis")
        scene_audio = service.synthesize_scene_audio(
            scene_id="sc_volcengine_test_001",
            voiceover="AI 回答总是出错？因为它可能缺少最新知识！今天带你了解 RAG 技术。",
            pace="fast"
        )
        print(f"✓ Scene audio generated: {scene_audio}")
        print()

        # Test 5: Batch synthesis
        print("Test 5: Batch synthesis")
        scenes = [
            {
                "scene_id": "sc_volcengine_batch_001",
                "voiceover": "第一个场景的旁白文本。",
                "pace": "fast"
            },
            {
                "scene_id": "sc_volcengine_batch_002",
                "voiceover": "第二个场景的旁白文本。",
                "pace": "medium"
            },
            {
                "scene_id": "sc_volcengine_batch_003",
                "voiceover": "第三个场景的旁白文本。",
                "pace": "slow"
            }
        ]

        results = service.synthesize_batch(scenes)
        print(f"✓ Generated {len(results)} audio files:")
        for scene_id, path in results.items():
            print(f"  - {scene_id}: {path}")
        print()

        print("-" * 70)
        print("✓ All tests completed successfully!")
        print()
        print("Audio files saved to: storage/audio/")
        print()
        print("Note: Volcengine TTS requires valid credentials in .env file")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_volcengine_tts()

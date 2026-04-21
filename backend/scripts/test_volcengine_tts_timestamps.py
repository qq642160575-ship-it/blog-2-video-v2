"""
Test script for Volcengine TTS word-level timestamps extraction

This script tests the updated VolcengineTTSService to verify:
1. TTS synthesis works correctly
2. Word-level timestamps are extracted from the response
3. Metadata structure matches expected format
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.tts.volcengine_tts_service import VolcengineTTSService
from app.core.config import get_settings
from app.core.logging_config import get_logger

logger = get_logger("test")
settings = get_settings()


def test_volcengine_tts_timestamps():
    """Test Volcengine TTS with timestamp extraction"""

    print("=" * 80)
    print("Testing Volcengine TTS Word-Level Timestamps")
    print("=" * 80)

    # Check if credentials are configured
    if not settings.volcengine_app_id or not settings.volcengine_access_token:
        print("\n❌ Error: Volcengine credentials not configured")
        print("Please set VOLCENGINE_APP_ID and VOLCENGINE_ACCESS_TOKEN in .env file")
        return False

    print(f"\n✓ Volcengine credentials found")
    print(f"  App ID: {settings.volcengine_app_id[:10]}...")
    print(f"  Cluster: {settings.volcengine_cluster}")

    # Initialize service
    try:
        tts_service = VolcengineTTSService()
        print("\n✓ VolcengineTTSService initialized successfully")
    except Exception as e:
        print(f"\n❌ Failed to initialize service: {e}")
        return False

    # Test text
    test_text = "这个方法可以提高工作效率三倍。"
    print(f"\n📝 Test text: {test_text}")

    # Synthesize speech
    try:
        print("\n🔊 Synthesizing speech...")
        audio_path, tts_metadata = tts_service.synthesize_speech(
            text=test_text,
            output_filename="test_timestamps.mp3",
            voice_name="BV700_streaming",
            speaking_rate=1.0
        )

        print(f"✓ Speech synthesized successfully")
        print(f"  Audio file: {audio_path}")

        # Check if file exists
        if os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path)
            print(f"  File size: {file_size} bytes")
        else:
            print(f"  ⚠️  Warning: Audio file not found at {audio_path}")

    except Exception as e:
        print(f"\n❌ Failed to synthesize speech: {e}")
        return False

    # Verify metadata
    print("\n📊 Analyzing TTS Metadata:")
    print("-" * 80)

    if tts_metadata is None:
        print("❌ No metadata returned (tts_metadata is None)")
        return False

    print(f"✓ Metadata returned")

    # Check duration
    if "duration" in tts_metadata:
        duration_ms = tts_metadata["duration"]
        duration_sec = float(duration_ms) / 1000 if duration_ms else 0
        print(f"  Duration: {duration_ms} ms ({duration_sec:.2f} seconds)")
    else:
        print("  ⚠️  No duration field")

    # Check word timestamps
    if "word_timestamps" in tts_metadata:
        word_timestamps = tts_metadata["word_timestamps"]
        print(f"\n✓ Word timestamps extracted: {len(word_timestamps)} words")

        if len(word_timestamps) > 0:
            print("\n  Word-level timestamps:")
            print("  " + "-" * 76)
            print(f"  {'Word':<15} {'Start (s)':<12} {'End (s)':<12} {'Duration (s)':<12}")
            print("  " + "-" * 76)

            for i, word_info in enumerate(word_timestamps[:10]):  # Show first 10
                word = word_info.get("word", "")
                start = word_info.get("start_time", 0)
                end = word_info.get("end_time", 0)
                duration = end - start
                print(f"  {word:<15} {start:<12.3f} {end:<12.3f} {duration:<12.3f}")

            if len(word_timestamps) > 10:
                print(f"  ... and {len(word_timestamps) - 10} more words")

            print("  " + "-" * 76)
        else:
            print("  ⚠️  Word timestamps array is empty")
    else:
        print("  ❌ No word_timestamps field in metadata")
        return False

    # Check phonemes (optional)
    if "phonemes" in tts_metadata:
        phonemes = tts_metadata["phonemes"]
        print(f"\n✓ Phoneme timestamps extracted: {len(phonemes)} phonemes")

    # Print full metadata structure
    print("\n📋 Full Metadata Structure:")
    print("-" * 80)
    print(json.dumps(tts_metadata, indent=2, ensure_ascii=False))
    print("-" * 80)

    print("\n" + "=" * 80)
    print("✅ Test completed successfully!")
    print("=" * 80)

    return True


if __name__ == "__main__":
    try:
        success = test_volcengine_tts_timestamps()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

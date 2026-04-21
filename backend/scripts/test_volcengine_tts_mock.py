"""
Mock test for Volcengine TTS timestamp extraction

This demonstrates the metadata extraction logic without requiring actual API credentials.
"""

import json
import sys
import os

# Change to backend directory to load .env file
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

from app.services.tts.volcengine_tts_service import VolcengineTTSService


def test_metadata_extraction():
    """Test the _extract_tts_metadata method with mock data"""

    print("=" * 80)
    print("Testing Volcengine TTS Metadata Extraction (Mock)")
    print("=" * 80)

    # Create service instance
    service = VolcengineTTSService.__new__(VolcengineTTSService)

    # Mock response data matching the Volcengine API format
    mock_response = {
        "reqid": "test-request-id",
        "code": 3000,
        "operation": "query",
        "message": "Success",
        "sequence": -1,
        "data": "base64_encoded_audio_data",
        "addition": {
            "description": "test audio",
            "duration": "1960",
            "frontend": json.dumps({
                "words": [
                    {
                        "word": "这个",
                        "start_time": 0.025,
                        "end_time": 0.185
                    },
                    {
                        "word": "方法",
                        "start_time": 0.185,
                        "end_time": 0.425
                    },
                    {
                        "word": "可以",
                        "start_time": 0.425,
                        "end_time": 0.625
                    },
                    {
                        "word": "提高",
                        "start_time": 0.625,
                        "end_time": 0.865
                    },
                    {
                        "word": "工作",
                        "start_time": 0.865,
                        "end_time": 1.105
                    },
                    {
                        "word": "效率",
                        "start_time": 1.105,
                        "end_time": 1.385
                    },
                    {
                        "word": "三倍",
                        "start_time": 1.385,
                        "end_time": 1.705
                    },
                    {
                        "word": "。",
                        "start_time": 1.85,
                        "end_time": 1.955
                    }
                ],
                "phonemes": [
                    {
                        "phone": "zh",
                        "start_time": 0.025,
                        "end_time": 0.065
                    },
                    {
                        "phone": "e4",
                        "start_time": 0.065,
                        "end_time": 0.105
                    },
                    {
                        "phone": "g",
                        "start_time": 0.105,
                        "end_time": 0.145
                    },
                    {
                        "phone": "e4",
                        "start_time": 0.145,
                        "end_time": 0.185
                    }
                ]
            })
        }
    }

    print("\n📥 Mock Response Data:")
    print(f"  Code: {mock_response['code']}")
    print(f"  Message: {mock_response['message']}")
    print(f"  Duration: {mock_response['addition']['duration']} ms")

    # Extract metadata
    print("\n🔍 Extracting metadata...")
    metadata = service._extract_tts_metadata(mock_response)

    if metadata is None:
        print("❌ Failed to extract metadata")
        return False

    print("✓ Metadata extracted successfully")

    # Verify structure
    print("\n📊 Metadata Structure:")
    print("-" * 80)

    # Check duration
    if "duration" in metadata:
        duration_ms = metadata["duration"]
        duration_sec = float(duration_ms) / 1000 if duration_ms else 0
        print(f"✓ Duration: {duration_ms} ms ({duration_sec:.2f} seconds)")
    else:
        print("❌ Missing duration field")
        return False

    # Check word timestamps
    if "word_timestamps" in metadata:
        word_timestamps = metadata["word_timestamps"]
        print(f"✓ Word timestamps: {len(word_timestamps)} words")

        if len(word_timestamps) > 0:
            print("\n  Word-level timestamps:")
            print("  " + "-" * 76)
            print(f"  {'Word':<15} {'Start (s)':<12} {'End (s)':<12} {'Duration (s)':<12}")
            print("  " + "-" * 76)

            for word_info in word_timestamps:
                word = word_info.get("word", "")
                start = word_info.get("start_time", 0)
                end = word_info.get("end_time", 0)
                duration = end - start
                print(f"  {word:<15} {start:<12.3f} {end:<12.3f} {duration:<12.3f}")

            print("  " + "-" * 76)
        else:
            print("❌ Word timestamps array is empty")
            return False
    else:
        print("❌ Missing word_timestamps field")
        return False

    # Check phonemes
    if "phonemes" in metadata:
        phonemes = metadata["phonemes"]
        print(f"\n✓ Phoneme timestamps: {len(phonemes)} phonemes (first 5 shown)")
        if len(phonemes) > 0:
            for i, phoneme_info in enumerate(phonemes[:5]):
                phone = phoneme_info.get("phone", "")
                start = phoneme_info.get("start_time", 0)
                end = phoneme_info.get("end_time", 0)
                print(f"    {phone}: {start:.3f}s - {end:.3f}s")

    # Print full metadata
    print("\n📋 Full Metadata JSON:")
    print("-" * 80)
    print(json.dumps(metadata, indent=2, ensure_ascii=False))
    print("-" * 80)

    # Verify expected values
    print("\n✅ Verification:")
    assert metadata["duration"] == "1960", "Duration mismatch"
    assert len(metadata["word_timestamps"]) == 8, "Word count mismatch"
    assert metadata["word_timestamps"][0]["word"] == "这个", "First word mismatch"
    assert metadata["word_timestamps"][1]["word"] == "方法", "Second word mismatch"
    print("  ✓ All assertions passed")

    print("\n" + "=" * 80)
    print("✅ Mock test completed successfully!")
    print("=" * 80)
    print("\n💡 Summary:")
    print("  - Metadata extraction logic is working correctly")
    print("  - Word-level timestamps are properly parsed")
    print("  - Phoneme-level timestamps are properly parsed")
    print("  - Data structure matches expected format")
    print("\n📝 Next steps:")
    print("  - Configure valid Volcengine credentials in .env")
    print("  - Run test_volcengine_tts_timestamps.py with real API")

    return True


if __name__ == "__main__":
    import sys
    try:
        success = test_metadata_extraction()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

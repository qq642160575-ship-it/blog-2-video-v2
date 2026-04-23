#!/usr/bin/env python3
"""Add mock TTS metadata to a scene for testing timeline features"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import get_db
from app.models.scene import Scene

def add_mock_tts_metadata(scene_id: str):
    """Add mock TTS metadata to a scene"""

    db = next(get_db())

    try:
        scene = db.query(Scene).filter(Scene.id == scene_id).first()

        if not scene:
            print(f"❌ 场景 {scene_id} 未找到")
            return False

        # Mock TTS metadata with word-level timestamps
        scene.tts_metadata = {
            "word_timestamps": [
                {"word": "为什么", "start_time": 0.0, "end_time": 0.4},
                {"word": "同样", "start_time": 0.4, "end_time": 0.7},
                {"word": "的", "start_time": 0.7, "end_time": 0.8},
                {"word": "AI", "start_time": 0.82, "end_time": 0.9},
                {"word": "模型", "start_time": 0.9, "end_time": 0.974},
                {"word": "，", "start_time": 1.1, "end_time": 1.15},
                {"word": "有人", "start_time": 1.5, "end_time": 1.8},
                {"word": "能", "start_time": 1.8, "end_time": 2.0},
                {"word": "写出", "start_time": 2.0, "end_time": 2.3},
                {"word": "惊艳", "start_time": 2.32, "end_time": 2.449},
                {"word": "的", "start_time": 2.5, "end_time": 2.6},
                {"word": "文案", "start_time": 2.6, "end_time": 2.9},
                {"word": "，", "start_time": 3.0, "end_time": 3.05},
                {"word": "有人", "start_time": 3.3, "end_time": 3.6},
                {"word": "却", "start_time": 3.6, "end_time": 3.8},
                {"word": "只能", "start_time": 3.8, "end_time": 4.1},
                {"word": "得到", "start_time": 4.1, "end_time": 4.3},
                {"word": "平庸", "start_time": 4.362, "end_time": 4.57},
                {"word": "的", "start_time": 4.6, "end_time": 4.7},
                {"word": "回答", "start_time": 4.7, "end_time": 5.0},
                {"word": "？", "start_time": 5.0, "end_time": 5.1}
            ]
        }

        db.commit()
        db.refresh(scene)

        print(f"✅ TTS 元数据已添加到场景 {scene_id}")
        print(f"   包含 {len(scene.tts_metadata['word_timestamps'])} 个词的时间戳")
        print(f"\n现在可以设置关键词：")
        print(f"curl -X PUT 'http://localhost:8000/scenes/{scene_id}/timeline' \\")
        print(f"  -H 'Content-Type: application/json' \\")
        print(f"  -d '{{\"emphasis_words\": [\"AI模型\", \"惊艳\", \"平庸\"]}}'")

        return True

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    scene_id = sys.argv[1] if len(sys.argv) > 1 else "sc_proj_21c89dcb_001"
    add_mock_tts_metadata(scene_id)

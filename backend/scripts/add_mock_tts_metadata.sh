#!/bin/bash
# 为场景添加模拟的 TTS 元数据

SCENE_ID="sc_proj_21c89dcb_001"

echo "为场景 $SCENE_ID 添加 TTS 元数据..."

# 注意：这需要直接操作数据库或通过支持的 API
# 由于当前 API 不支持直接更新 tts_metadata，我们需要创建一个临时脚本

python3 << 'EOF'
from app.core.db import get_db
from app.models.scene import Scene
import json

db = next(get_db())

scene = db.query(Scene).filter(Scene.id == "sc_proj_21c89dcb_001").first()

if scene:
    # 模拟的 TTS 元数据
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
    print(f"✅ TTS 元数据已添加到场景 {scene.id}")
    print(f"   包含 {len(scene.tts_metadata['word_timestamps'])} 个词的时间戳")
else:
    print(f"❌ 场景未找到")

db.close()
EOF

echo ""
echo "现在可以设置关键词了："
echo "curl -X PUT 'http://localhost:8000/scenes/$SCENE_ID/timeline' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"emphasis_words\": [\"AI模型\", \"惊艳\", \"平庸\"]}'"

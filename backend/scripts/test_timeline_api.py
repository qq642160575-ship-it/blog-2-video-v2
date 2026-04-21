#!/usr/bin/env python3
"""
测试时间轴 API
验证 PUT /scenes/{scene_id}/timeline 和 POST /scenes/{scene_id}/preview
"""
import sys
import os

# Change to backend directory
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.core.db import get_db, engine
from app.models.scene import Scene
from sqlalchemy.orm import Session

client = TestClient(app)


def test_timeline_api():
    """测试时间轴 API"""
    print("=" * 80)
    print("测试时间轴 API")
    print("=" * 80)
    print()

    # 获取数据库中的第一个场景
    db: Session = next(get_db())
    scene = db.query(Scene).first()

    if not scene:
        print("❌ 数据库中没有场景，请先运行视频生成流程")
        return False

    scene_id = scene.id
    print(f"✓ 找到测试场景: scene_id={scene_id}")
    print(f"  当前 emphasis_words: {scene.emphasis_words}")
    print(f"  当前 timeline_data: {scene.timeline_data is not None}")
    print()

    # 测试1: 更新 emphasis_words（自动重新计算时间轴）
    print("测试1: 更新 emphasis_words（自动重新计算时间轴）")
    print("-" * 80)

    new_emphasis_words = ["测试", "关键词", "更新"]
    response = client.put(
        f"/scenes/{scene_id}/timeline",
        json={"emphasis_words": new_emphasis_words}
    )

    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")

    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        assert data["scene_id"] == scene_id
        assert "updated_at" in data
        print("✓ 测试1通过: emphasis_words 更新成功")
    else:
        print(f"❌ 测试1失败: {response.json()}")
        return False
    print()

    # 测试2: 手动更新 timeline_data
    print("测试2: 手动更新 timeline_data")
    print("-" * 80)

    manual_timeline = {
        "keyframes": [
            {"time": 0.5, "element": "测试", "action": "pop", "duration": 0.3},
            {"time": 1.5, "element": "手动", "action": "pop", "duration": 0.3},
        ],
        "stats": {"total_keyframes": 2}
    }

    response = client.put(
        f"/scenes/{scene_id}/timeline",
        json={"timeline_data": manual_timeline}
    )

    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")

    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        assert data["timeline_data"] == manual_timeline
        print("✓ 测试2通过: timeline_data 手动更新成功")
    else:
        print(f"❌ 测试2失败: {response.json()}")
        return False
    print()

    # 测试3: 同时更新 emphasis_words 和 timeline_data
    print("测试3: 同时更新 emphasis_words 和 timeline_data")
    print("-" * 80)

    response = client.put(
        f"/scenes/{scene_id}/timeline",
        json={
            "emphasis_words": ["新", "关键词"],
            "timeline_data": manual_timeline
        }
    )

    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")

    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        print("✓ 测试3通过: 同时更新成功")
    else:
        print(f"❌ 测试3失败: {response.json()}")
        return False
    print()

    # 测试4: 请求预览（预期失败，因为未实现）
    print("测试4: 请求预览视频")
    print("-" * 80)

    response = client.post(
        f"/scenes/{scene_id}/preview",
        json={"quality": "low"}
    )

    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")

    if response.status_code == 200:
        data = response.json()
        # 预期 success=False，因为预览功能未完全实现
        if not data["success"]:
            print("✓ 测试4通过: 预览 API 返回预期的未实现消息")
        else:
            print("⚠ 测试4: 预览功能已实现")
    else:
        print(f"❌ 测试4失败: {response.json()}")
        return False
    print()

    # 测试5: 错误场景 - 场景不存在
    print("测试5: 错误场景 - 场景不存在")
    print("-" * 80)

    response = client.put(
        "/scenes/999999/timeline",
        json={"emphasis_words": ["测试"]}
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 404:
        print("✓ 测试5通过: 正确返回 404")
    else:
        print(f"❌ 测试5失败: 预期 404，实际 {response.status_code}")
        return False
    print()

    # 测试6: 错误场景 - 缺少参数
    print("测试6: 错误场景 - 缺少参数")
    print("-" * 80)

    response = client.put(
        f"/scenes/{scene_id}/timeline",
        json={}
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 400:
        print("✓ 测试6通过: 正确返回 400")
    else:
        print(f"❌ 测试6失败: 预期 400，实际 {response.status_code}")
        return False
    print()

    print("=" * 80)
    print("✅ 所有测试通过！时间轴 API 工作正常。")
    print("=" * 80)
    print()

    return True


if __name__ == "__main__":
    try:
        success = test_timeline_api()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

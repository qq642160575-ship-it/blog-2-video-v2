#!/usr/bin/env python3
"""
测试渲染清单生成
验证 timeline_data 是否正确传递到 manifest
"""
import sys
import os
import json

# Change to backend directory
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

from app.services.template_mapping_service import TemplateMappingService


def test_manifest_with_timeline():
    """测试带有 timeline_data 的 manifest 生成"""
    print("=" * 80)
    print("测试渲染清单生成（含 timeline_data）")
    print("=" * 80)
    print()

    # 创建服务实例
    service = TemplateMappingService()
    print("✓ TemplateMappingService 初始化成功")
    print()

    # Mock scene data with timeline_data
    scene_data = {
        "scene_id": "scene_001",
        "template_type": "hook_title",
        "goal": "开场钩子",
        "voiceover": "这个方法可以提高工作效率三倍",
        "screen_text": ["提高效率", "三倍增长"],
        "duration_sec": 8,
        "pace": "fast",
        "transition": "fade",
        "emphasis_words": ["方法", "效率", "三倍"],
        "timeline_data": {
            "keyframes": [
                {
                    "time": 0.085,
                    "element": "方法",
                    "action": "pop",
                    "duration": 0.3,
                    "word_start": 0.185,
                    "word_end": 0.425
                },
                {
                    "time": 1.005,
                    "element": "效率",
                    "action": "pop",
                    "duration": 0.3,
                    "word_start": 1.105,
                    "word_end": 1.385
                },
                {
                    "time": 1.285,
                    "element": "三倍",
                    "action": "pop",
                    "duration": 0.3,
                    "word_start": 1.385,
                    "word_end": 1.705
                }
            ],
            "stats": {
                "total_emphasis_words": 3,
                "matched_words": 3,
                "match_rate": 1.0
            }
        }
    }

    print("测试数据:")
    print(f"  场景ID: {scene_data['scene_id']}")
    print(f"  模板类型: {scene_data['template_type']}")
    print(f"  重点词: {scene_data['emphasis_words']}")
    print(f"  关键帧数: {len(scene_data['timeline_data']['keyframes'])}")
    print()

    # 生成 manifest scene
    print("生成 manifest scene...")
    manifest_scene = service.build_manifest_scene(
        scene=scene_data,
        start_ms=0,
        end_ms=8000,
        audio_url="http://example.com/audio/scene_001.mp3"
    )

    print("✓ Manifest scene 生成成功")
    print()

    # 显示结果
    print("Manifest Scene 数据:")
    print("-" * 80)
    print(json.dumps(manifest_scene, indent=2, ensure_ascii=False))
    print("-" * 80)
    print()

    # 验证结果
    print("验证结果:")
    checks = [
        ("scene_id", "scene_id" in manifest_scene),
        ("template_type", "template_type" in manifest_scene),
        ("composition_id", "composition_id" in manifest_scene),
        ("audio_url", "audio_url" in manifest_scene),
        ("timeline_data", "timeline_data" in manifest_scene),
        ("timeline_data.keyframes",
         "timeline_data" in manifest_scene and
         "keyframes" in manifest_scene.get("timeline_data", {})),
        ("keyframes count",
         len(manifest_scene.get("timeline_data", {}).get("keyframes", [])) == 3),
    ]

    all_passed = True
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}: {result}")
        if not result:
            all_passed = False

    print()

    if all_passed:
        print("=" * 80)
        print("✅ 所有测试通过！")
        print("=" * 80)
        print()
        print("timeline_data 已成功传递到 manifest，渲染器可以使用它来触发关键词强调动效。")
        print()
        return True
    else:
        print("=" * 80)
        print("❌ 部分测试失败")
        print("=" * 80)
        return False


def test_manifest_without_timeline():
    """测试没有 timeline_data 的场景（向后兼容）"""
    print("=" * 80)
    print("测试向后兼容性（无 timeline_data）")
    print("=" * 80)
    print()

    service = TemplateMappingService()

    # Scene without timeline_data
    scene_data = {
        "scene_id": "scene_002",
        "template_type": "bullet_explain",
        "goal": "要点说明",
        "voiceover": "这里是要点说明",
        "screen_text": ["要点1", "要点2", "要点3"],
        "duration_sec": 10,
    }

    manifest_scene = service.build_manifest_scene(
        scene=scene_data,
        start_ms=8000,
        end_ms=18000
    )

    print("Manifest Scene 数据:")
    print("-" * 80)
    print(json.dumps(manifest_scene, indent=2, ensure_ascii=False))
    print("-" * 80)
    print()

    # 验证 timeline_data 不存在（向后兼容）
    has_timeline = "timeline_data" in manifest_scene
    print(f"验证: timeline_data 不存在 = {not has_timeline}")

    if not has_timeline:
        print("✓ 向后兼容性测试通过")
        print()
        return True
    else:
        print("✗ 向后兼容性测试失败")
        print()
        return False


if __name__ == "__main__":
    try:
        test1 = test_manifest_with_timeline()
        test2 = test_manifest_without_timeline()

        if test1 and test2:
            print("=" * 80)
            print("🎉 所有测试通过！渲染层适配完成。")
            print("=" * 80)
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

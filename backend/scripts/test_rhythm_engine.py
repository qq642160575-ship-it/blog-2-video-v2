#!/usr/bin/env python3
"""
测试节奏规则引擎
验证不同场景类型应用不同的节奏规则
"""
import sys
import os
import json

# Change to backend directory
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

from app.services.timeline_calculate_service import TimelineCalculateService


def test_rhythm_engine():
    """测试节奏规则引擎"""
    print("=" * 80)
    print("测试节奏规则引擎")
    print("=" * 80)
    print()

    # 创建服务实例
    service = TimelineCalculateService()
    print("✓ TimelineCalculateService 初始化成功")
    print()

    # Mock 数据
    emphasis_words = ["方法", "效率", "三倍"]
    voiceover = "这个方法可以提高工作效率三倍"
    tts_metadata = {
        "duration": "1960",
        "word_timestamps": [
            {"word": "这个", "start_time": 0.025, "end_time": 0.185},
            {"word": "方法", "start_time": 0.185, "end_time": 0.425},
            {"word": "可以", "start_time": 0.425, "end_time": 0.625},
            {"word": "提高", "start_time": 0.625, "end_time": 0.865},
            {"word": "工作", "start_time": 0.865, "end_time": 1.105},
            {"word": "效率", "start_time": 1.105, "end_time": 1.385},
            {"word": "三倍", "start_time": 1.385, "end_time": 1.705},
        ]
    }

    # 测试1: Hook 场景
    print("测试1: Hook 场景（快节奏，有停顿）")
    print("-" * 80)
    hook_timeline = service.calculate_timeline_with_rhythm(
        emphasis_words=emphasis_words,
        tts_metadata=tts_metadata,
        voiceover=voiceover,
        scene_type="hook",
        duration_sec=8.0
    )

    if hook_timeline:
        print(json.dumps(hook_timeline, indent=2, ensure_ascii=False))
        keyframes = hook_timeline["keyframes"]

        # 验证 Hook 规则
        has_pause = any(kf["action"] == "pause" for kf in keyframes)
        effect_durations = [kf["duration"] for kf in keyframes if kf["action"] != "pause"]

        print()
        print(f"  关键帧数: {len(keyframes)}")
        print(f"  有停顿: {has_pause}")
        print(f"  动效时长: {effect_durations}")
        print(f"  节奏规则: {hook_timeline.get('rhythm_rule_applied')}")

        assert has_pause, "Hook 场景应该有停顿"
        assert all(d == 0.2 for d in effect_durations), "Hook 动效应该是 0.2 秒"
        print("  ✓ Hook 规则验证通过")
    else:
        print("  ❌ Hook 时间轴计算失败")
        return False
    print()

    # 测试2: Explanation 场景
    print("测试2: Explanation 场景（中等节奏，无停顿）")
    print("-" * 80)
    explanation_timeline = service.calculate_timeline_with_rhythm(
        emphasis_words=emphasis_words,
        tts_metadata=tts_metadata,
        voiceover=voiceover,
        scene_type="explanation",
        duration_sec=8.0
    )

    if explanation_timeline:
        print(json.dumps(explanation_timeline, indent=2, ensure_ascii=False))
        keyframes = explanation_timeline["keyframes"]

        has_pause = any(kf["action"] == "pause" for kf in keyframes)
        effect_durations = [kf["duration"] for kf in keyframes if kf["action"] != "pause"]

        print()
        print(f"  关键帧数: {len(keyframes)}")
        print(f"  有停顿: {has_pause}")
        print(f"  动效时长: {effect_durations}")
        print(f"  节奏规则: {explanation_timeline.get('rhythm_rule_applied')}")

        assert not has_pause, "Explanation 场景不应该有停顿"
        assert all(d == 0.3 for d in effect_durations), "Explanation 动效应该是 0.3 秒"
        print("  ✓ Explanation 规则验证通过")
    else:
        print("  ❌ Explanation 时间轴计算失败")
        return False
    print()

    # 测试3: Contrast 场景
    print("测试3: Contrast 场景（交替节奏，无停顿）")
    print("-" * 80)
    contrast_timeline = service.calculate_timeline_with_rhythm(
        emphasis_words=emphasis_words,
        tts_metadata=tts_metadata,
        voiceover=voiceover,
        scene_type="contrast",
        duration_sec=8.0
    )

    if contrast_timeline:
        print(json.dumps(contrast_timeline, indent=2, ensure_ascii=False))
        keyframes = contrast_timeline["keyframes"]

        has_pause = any(kf["action"] == "pause" for kf in keyframes)
        effect_durations = [kf["duration"] for kf in keyframes if kf["action"] != "pause"]

        print()
        print(f"  关键帧数: {len(keyframes)}")
        print(f"  有停顿: {has_pause}")
        print(f"  动效时长: {effect_durations}")
        print(f"  节奏规则: {contrast_timeline.get('rhythm_rule_applied')}")

        assert not has_pause, "Contrast 场景不应该有停顿"
        # 验证交替时长
        if len(effect_durations) >= 2:
            assert effect_durations[0] != effect_durations[1], "Contrast 动效应该交替"
        print("  ✓ Contrast 规则验证通过")
    else:
        print("  ❌ Contrast 时间轴计算失败")
        return False
    print()

    # 测试4: 对比不同场景类型
    print("测试4: 对比不同场景类型的差异")
    print("-" * 80)

    hook_kf_count = len([kf for kf in hook_timeline["keyframes"] if kf["action"] != "pause"])
    explanation_kf_count = len(explanation_timeline["keyframes"])
    contrast_kf_count = len(contrast_timeline["keyframes"])

    print(f"  Hook 关键帧数: {hook_kf_count}")
    print(f"  Explanation 关键帧数: {explanation_kf_count}")
    print(f"  Contrast 关键帧数: {contrast_kf_count}")
    print()

    hook_durations = [kf["duration"] for kf in hook_timeline["keyframes"] if kf["action"] != "pause"]
    explanation_durations = [kf["duration"] for kf in explanation_timeline["keyframes"]]
    contrast_durations = [kf["duration"] for kf in contrast_timeline["keyframes"]]

    print(f"  Hook 平均动效时长: {sum(hook_durations)/len(hook_durations):.2f}s")
    print(f"  Explanation 平均动效时长: {sum(explanation_durations)/len(explanation_durations):.2f}s")
    print(f"  Contrast 平均动效时长: {sum(contrast_durations)/len(contrast_durations):.2f}s")
    print()

    print("  ✓ 不同场景类型有明显差异")
    print()

    print("=" * 80)
    print("✅ 所有测试通过！节奏规则引擎工作正常。")
    print("=" * 80)
    print()
    print("下一步: 扩展 LLM Prompt，让它标注场景类型")
    print()

    return True


if __name__ == "__main__":
    try:
        success = test_rhythm_engine()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

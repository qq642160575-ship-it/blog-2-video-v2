#!/usr/bin/env python3
"""
测试节奏规则配置
验证配置文件是否正确加载
"""
import sys
import os

# Change to backend directory
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

from app.config.rhythm_rules import RHYTHM_RULES, get_rhythm_rule, get_available_scene_types


def test_rhythm_rules():
    """测试节奏规则配置"""
    print("=" * 80)
    print("测试节奏规则配置")
    print("=" * 80)
    print()

    # 测试1: 检查所有场景类型
    print("测试1: 检查所有场景类型")
    scene_types = get_available_scene_types()
    print(f"  可用场景类型: {scene_types}")
    assert len(scene_types) == 3, "应该有 3 种场景类型"
    assert "hook" in scene_types, "应该包含 hook 类型"
    assert "explanation" in scene_types, "应该包含 explanation 类型"
    assert "contrast" in scene_types, "应该包含 contrast 类型"
    print("  ✓ 场景类型检查通过")
    print()

    # 测试2: 检查 Hook 规则
    print("测试2: 检查 Hook 规则")
    hook_rule = get_rhythm_rule("hook")
    print(f"  emphasis_density: {hook_rule['emphasis_density']}")
    print(f"  effect_speed: {hook_rule['effect_speed']}")
    print(f"  pause_after: {hook_rule['pause_after']}")
    print(f"  min_interval: {hook_rule['min_interval']}s")
    print(f"  effect_duration: {hook_rule['effect_duration']}s")

    assert hook_rule['emphasis_density'] == "high", "Hook 应该是高密度"
    assert hook_rule['effect_speed'] == "fast", "Hook 应该是快速动效"
    assert hook_rule['pause_after'] == True, "Hook 应该有停顿"
    assert hook_rule['effect_duration'] == 0.2, "Hook 动效应该是 0.2 秒"
    print("  ✓ Hook 规则检查通过")
    print()

    # 测试3: 检查 Explanation 规则
    print("测试3: 检查 Explanation 规则")
    explanation_rule = get_rhythm_rule("explanation")
    print(f"  emphasis_density: {explanation_rule['emphasis_density']}")
    print(f"  effect_speed: {explanation_rule['effect_speed']}")
    print(f"  pause_after: {explanation_rule['pause_after']}")
    print(f"  min_interval: {explanation_rule['min_interval']}s")
    print(f"  effect_duration: {explanation_rule['effect_duration']}s")

    assert explanation_rule['emphasis_density'] == "medium", "Explanation 应该是中等密度"
    assert explanation_rule['effect_speed'] == "medium", "Explanation 应该是中速动效"
    assert explanation_rule['pause_after'] == False, "Explanation 不应该有停顿"
    assert explanation_rule['effect_duration'] == 0.3, "Explanation 动效应该是 0.3 秒"
    print("  ✓ Explanation 规则检查通过")
    print()

    # 测试4: 检查 Contrast 规则
    print("测试4: 检查 Contrast 规则")
    contrast_rule = get_rhythm_rule("contrast")
    print(f"  emphasis_density: {contrast_rule['emphasis_density']}")
    print(f"  effect_speed: {contrast_rule['effect_speed']}")
    print(f"  pause_after: {contrast_rule['pause_after']}")
    print(f"  min_interval: {contrast_rule['min_interval']}s")
    print(f"  alternating_durations: {contrast_rule['alternating_durations']}")

    assert contrast_rule['emphasis_density'] == "paired", "Contrast 应该是成对密度"
    assert contrast_rule['effect_speed'] == "alternating", "Contrast 应该是交替动效"
    assert contrast_rule['pause_after'] == False, "Contrast 不应该有停顿"
    assert "alternating_durations" in contrast_rule, "Contrast 应该有交替时长"
    print("  ✓ Contrast 规则检查通过")
    print()

    # 测试5: 检查默认规则
    print("测试5: 检查默认规则（未知类型）")
    default_rule = get_rhythm_rule("unknown_type")
    print(f"  未知类型返回: {default_rule['emphasis_density']} 规则")
    assert default_rule == explanation_rule, "未知类型应该返回 explanation 规则"
    print("  ✓ 默认规则检查通过")
    print()

    # 测试6: 验证规则差异
    print("测试6: 验证规则差异")
    print(f"  Hook 动效时长: {hook_rule['effect_duration']}s")
    print(f"  Explanation 动效时长: {explanation_rule['effect_duration']}s")
    print(f"  差异: {(explanation_rule['effect_duration'] - hook_rule['effect_duration']) / hook_rule['effect_duration'] * 100:.0f}%")

    print(f"  Hook 最小间隔: {hook_rule['min_interval']}s")
    print(f"  Explanation 最小间隔: {explanation_rule['min_interval']}s")
    print(f"  差异: {(explanation_rule['min_interval'] - hook_rule['min_interval']) / hook_rule['min_interval'] * 100:.0f}%")

    assert hook_rule['effect_duration'] < explanation_rule['effect_duration'], "Hook 应该比 Explanation 快"
    assert hook_rule['min_interval'] < explanation_rule['min_interval'], "Hook 间隔应该比 Explanation 短"
    print("  ✓ 规则差异检查通过")
    print()

    print("=" * 80)
    print("✅ 所有测试通过！节奏规则配置正确。")
    print("=" * 80)
    print()
    print("下一步: 扩展 Scene 模型，增加 scene_type 字段")
    print()

    return True


if __name__ == "__main__":
    try:
        success = test_rhythm_rules()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

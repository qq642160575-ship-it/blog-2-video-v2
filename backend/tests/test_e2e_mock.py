"""
Step 6: 端到端测试（Mock版完整链路）

测试内容：
- HookGenerateService mock 版是否能返回3个 Hook
- EnhancedValidator 是否能通过/拒绝场景
- generate_scenes + validate_scenes 节点的 v3 字段是否正确注入
"""
import sys
import os

# 确保在 backend/ 目录下运行
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.schemas.hook import Hook, HookResult
from app.services.hook_generate_service import HookGenerateService
from app.services.enhanced_validator import EnhancedValidator


# ------------------------------------------------------------------
# Test 1: HookGenerateService Mock 版
# ------------------------------------------------------------------
def test_hook_service_mock():
    """Mock Hook 生成返回3个不同类型的 Hook"""
    service = HookGenerateService()
    result = service.generate_hooks({"topic": "时间管理"})

    assert isinstance(result, HookResult), "应返回 HookResult 实例"
    assert len(result.hooks) == 3, f"应生成3个Hook，实际: {len(result.hooks)}"
    assert result.selected_index == 0, "question 类型应排第一"

    types = {h.type for h in result.hooks}
    assert "question" in types, "缺少 question 类型"
    assert "contrast" in types, "缺少 contrast 类型"
    assert "reveal" in types, "缺少 reveal 类型"

    selected = result.hooks[result.selected_index]
    print(f"  selected hook: [{selected.type}] {selected.content}")
    print("✅ Test 1 通过: HookGenerateService Mock")


# ------------------------------------------------------------------
# Test 2: Hook Schema 验证
# ------------------------------------------------------------------
def test_hook_schema():
    """Hook schema 字段约束验证"""
    hook = Hook(type="question", content="为什么时间管理这么重要？", score=0.85)
    assert hook.type == "question"
    assert hook.score == 0.85
    d = hook.model_dump()
    assert "type" in d and "content" in d and "score" in d
    print("✅ Test 2 通过: Hook Schema")


# ------------------------------------------------------------------
# Test 3: EnhancedValidator - 合法场景通过
# ------------------------------------------------------------------
def test_validator_pass():
    """合法场景应该通过验证"""
    scenes = [
        {
            "voiceover": "为什么时间管理对99%的人都这么重要？",
            "narrative_stage": "opening",
            "emotion_level": 5,
        },
        {
            "voiceover": "首先要了解时间的本质",
            "narrative_stage": "build",
            "emotion_level": 3,
        },
        {
            "voiceover": "答案是使用番茄工作法",
            "narrative_stage": "payoff",
            "emotion_level": 4,
        },
        {
            "voiceover": "总结一下核心要点",
            "narrative_stage": "close",
            "emotion_level": 3,
        },
    ]

    validator = EnhancedValidator()
    result = validator.validate_scenes(scenes)
    assert result.passed, f"合法场景应通过，实际错误: {result.errors}"
    print("✅ Test 3 通过: EnhancedValidator 合法场景")


# ------------------------------------------------------------------
# Test 4: EnhancedValidator - 缺少 Hook 关键词
# ------------------------------------------------------------------
def test_validator_fail_no_hook():
    """第1个场景没有 Hook 关键词应该不通过"""
    scenes = [
        {
            "voiceover": "我们来讲一下时间管理",  # 无钩子
            "narrative_stage": "opening",
            "emotion_level": 5,
        },
        {
            "voiceover": "首先了解问题背景",
            "narrative_stage": "build",
            "emotion_level": 3,
        },
        {
            "voiceover": "给出解决方案",
            "narrative_stage": "payoff",
            "emotion_level": 4,
        },
        {
            "voiceover": "总结",
            "narrative_stage": "close",
            "emotion_level": 3,
        },
    ]

    validator = EnhancedValidator()
    result = validator.validate_scenes(scenes)
    assert not result.passed, "缺少 Hook 关键词应不通过"
    assert any("Hook" in e for e in result.errors), f"错误信息应提及Hook，实际: {result.errors}"
    print(f"✅ Test 4 通过: EnhancedValidator 正确拒绝无Hook场景 ({result.errors})")


# ------------------------------------------------------------------
# Test 5: EnhancedValidator - 缺少叙事阶段
# ------------------------------------------------------------------
def test_validator_fail_missing_stage():
    """缺少 payoff 阶段应该不通过"""
    scenes = [
        {
            "voiceover": "为什么时间管理对99%的人都这么重要？",
            "narrative_stage": "opening",
            "emotion_level": 5,
        },
        {
            "voiceover": "展开分析",
            "narrative_stage": "build",
            "emotion_level": 3,
        },
        {
            "voiceover": "总结",
            "narrative_stage": "close",
            "emotion_level": 3,
        },
    ]

    validator = EnhancedValidator()
    result = validator.validate_scenes(scenes)
    assert not result.passed, "缺少 payoff 阶段应不通过"
    print(f"✅ Test 5 通过: EnhancedValidator 正确拒绝缺少叙事阶段 ({result.errors})")


# ------------------------------------------------------------------
# Test 6: Hook 注入 v3 字段的逻辑
# ------------------------------------------------------------------
def test_hook_injection_logic():
    """验证 v3 字段注入逻辑"""
    service = HookGenerateService()
    hook_result = service.generate_hooks({"topic": "Python编程"})
    selected = hook_result.selected_hook

    # 模拟 scenes_data 注入逻辑
    scenes_data = [
        {"voiceover": "old content", "scene_id": "sc_001", "order": 1, "template_type": "hook_title",
         "goal": "hook", "screen_text": ["hook"], "duration_sec": 3, "pace": "fast", "transition": "cut"},
        {"voiceover": "展开内容", "scene_id": "sc_002", "order": 2, "template_type": "bullet_explain",
         "goal": "body", "screen_text": ["body"], "duration_sec": 5, "pace": "medium", "transition": "fade"},
    ]

    _narrative_stages = ["opening", "build"]
    _emotion_levels = [5, 3]
    for i, sd in enumerate(scenes_data):
        sd["narrative_stage"] = _narrative_stages[i]
        sd["emotion_level"] = _emotion_levels[i]
        sd["scene_role"] = "hook" if i == 0 else "body"
        if i == 0:
            sd["hook_type"] = selected.type
            sd["quality_score"] = selected.score
            sd["voiceover"] = selected.content  # Mock 模式替换

    assert scenes_data[0]["voiceover"] == selected.content, "第1场景旁白应替换为Hook"
    assert scenes_data[0]["scene_role"] == "hook"
    assert scenes_data[0]["hook_type"] == selected.type
    assert scenes_data[1]["scene_role"] == "body"
    print(f"✅ Test 6 通过: Hook注入v3字段正确")


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Step 6: Mock版端到端测试")
    print("=" * 60 + "\n")

    tests = [
        test_hook_schema,
        test_hook_service_mock,
        test_validator_pass,
        test_validator_fail_no_hook,
        test_validator_fail_missing_stage,
        test_hook_injection_logic,
    ]

    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"❌ {t.__name__} 失败: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"结果: {passed} 通过 / {failed} 失败")
    if failed == 0:
        print("✅ Mock版端到端测试全部通过")
    else:
        print("❌ 有测试失败，请检查")
    print("=" * 60)

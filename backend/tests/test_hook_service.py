"""
Step 13 & 15: 单元测试集合（Hook服务 + Validator）

运行方式:
    cd backend
    source venv/bin/activate
    python tests/test_hook_service.py
    # 或用 pytest:
    # pytest tests/test_hook_service.py -v
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
from app.schemas.hook import Hook, HookResult
from app.services.hook_generate_service import HookGenerateService
from app.services.enhanced_validator import EnhancedValidator


# ===================================================
# HookGenerateService 单元测试
# ===================================================

def test_hook_generation_mock():
    """Mock 模式返回3个Hook"""
    service = HookGenerateService()
    result = service._generate_hooks_mock({"topic": "时间管理"})

    assert len(result.hooks) == 3
    assert result.selected_index >= 0
    assert result.selected_index < len(result.hooks)
    print("✅ test_hook_generation_mock")


def test_hook_selection_prefers_question():
    """优先选 question 类型"""
    service = HookGenerateService()
    hooks = [
        Hook(type="reveal", content="揭秘...", score=0.9),
        Hook(type="question", content="为什么...", score=0.8),
        Hook(type="contrast", content="对比...", score=0.7),
    ]
    idx = service._select_best(hooks)
    assert idx == 1, f"应选question(idx=1)，实际选了{idx}"
    print("✅ test_hook_selection_prefers_question")


def test_hook_selection_fallback_to_contrast():
    """没有 question 时选 contrast"""
    service = HookGenerateService()
    hooks = [
        Hook(type="reveal", content="揭秘...", score=0.9),
        Hook(type="contrast", content="对比...", score=0.8),
    ]
    idx = service._select_best(hooks)
    assert idx == 1, f"应选contrast(idx=1)，实际选了{idx}"
    print("✅ test_hook_selection_fallback_to_contrast")


def test_hook_selection_fallback_to_first():
    """只有 reveal 时选第0个"""
    service = HookGenerateService()
    hooks = [
        Hook(type="reveal", content="揭秘...", score=0.9),
    ]
    idx = service._select_best(hooks)
    assert idx == 0
    print("✅ test_hook_selection_fallback_to_first")


def test_default_hook_on_failure():
    """LLM 全部失败时返回默认 Hook"""
    service = HookGenerateService()
    with patch.object(service, 'generate_hooks', side_effect=Exception("LLM超时")):
        result = service.generate_hooks_with_retry({"topic": "测试话题"}, max_retries=1)
    assert result.hooks[0].type == "reveal"
    assert "测试话题" in result.hooks[0].content
    print("✅ test_default_hook_on_failure")


def test_fix_json():
    """JSON 修复逻辑正常工作"""
    service = HookGenerateService()
    broken = '{"hooks": [{"type": "question", "content": "为什么?",}]}'
    fixed = service._fix_json(broken)
    # 去除了尾随逗号
    import json
    data = json.loads(fixed)
    assert "hooks" in data
    print("✅ test_fix_json")


def test_parse_response_valid():
    """解析正常 LLM JSON 响应"""
    service = HookGenerateService()
    response = '''```json
{
  "hooks": [
    {"type": "question", "content": "为什么时间管理这么重要？", "score": 0.85},
    {"type": "contrast", "content": "你以为很简单？其实大部分人都错了", "score": 0.78},
    {"type": "reveal", "content": "90%的人不知道的秘密", "score": 0.72}
  ]
}
```'''
    hooks = service._parse_response(response)
    assert len(hooks) == 3
    assert hooks[0].type == "question"
    print("✅ test_parse_response_valid")


# ===================================================
# EnhancedValidator 单元测试
# ===================================================

def test_validator_pass_full():
    """完整合规场景应通过验证"""
    scenes = [
        {"voiceover": "为什么时间管理对99%的人都这么重要？", "narrative_stage": "opening", "emotion_level": 5},
        {"voiceover": "首先要了解时间的本质", "narrative_stage": "build", "emotion_level": 3},
        {"voiceover": "答案是使用番茄工作法，25分钟专注", "narrative_stage": "payoff", "emotion_level": 4},
        {"voiceover": "总结一下核心要点", "narrative_stage": "close", "emotion_level": 3},
    ]
    validator = EnhancedValidator()
    result = validator.validate_scenes(scenes)
    assert result.passed == True, f"应通过，错误: {result.errors}"
    print("✅ test_validator_pass_full")


def test_validator_empty_scenes():
    """空场景列表应不通过"""
    validator = EnhancedValidator()
    result = validator.validate_scenes([])
    assert result.passed == False
    print("✅ test_validator_empty_scenes")


def test_validator_no_hook_keyword():
    """第1场景无 Hook 关键词应不通过"""
    scenes = [
        {"voiceover": "今天来讲时间管理", "narrative_stage": "opening", "emotion_level": 5},
        {"voiceover": "第一点很重要", "narrative_stage": "build", "emotion_level": 3},
        {"voiceover": "番茄工作法就是答案", "narrative_stage": "payoff", "emotion_level": 4},
        {"voiceover": "总结", "narrative_stage": "close", "emotion_level": 3},
    ]
    validator = EnhancedValidator()
    result = validator.validate_scenes(scenes)
    assert not result.passed
    assert any("Hook" in e for e in result.errors)
    print("✅ test_validator_no_hook_keyword")


def test_validator_duplicate_detection():
    """相邻场景高度相似应检测到重复"""
    scenes = [
        {"voiceover": "为什么时间管理这么重要？掌握方法", "narrative_stage": "opening", "emotion_level": 5},
        {"voiceover": "为什么时间管理这么重要？掌握方法", "narrative_stage": "build", "emotion_level": 3},
        {"voiceover": "番茄工作法是答案", "narrative_stage": "payoff", "emotion_level": 4},
        {"voiceover": "总结", "narrative_stage": "close", "emotion_level": 3},
    ]
    validator = EnhancedValidator()
    result = validator.validate_scenes(scenes)
    assert not result.passed
    assert any("重复" in e for e in result.errors)
    print("✅ test_validator_duplicate_detection")


def test_validator_missing_stage():
    """缺少必要叙事阶段应不通过"""
    scenes = [
        {"voiceover": "为什么时间管理这么重要？99%的人都不知道", "narrative_stage": "opening", "emotion_level": 5},
        {"voiceover": "展开分析", "narrative_stage": "build", "emotion_level": 3},
        {"voiceover": "总结", "narrative_stage": "close", "emotion_level": 3},
    ]
    validator = EnhancedValidator()
    result = validator.validate_scenes(scenes)
    assert not result.passed
    assert any("叙事阶段" in e for e in result.errors)
    print("✅ test_validator_missing_stage")


def test_validator_all_same_emotion():
    """所有情绪都是3（平淡）应有 warning"""
    scenes = [
        {"voiceover": "为什么时间管理这么重要？99%的", "narrative_stage": "opening", "emotion_level": 3},
        {"voiceover": "展开", "narrative_stage": "build", "emotion_level": 3},
        {"voiceover": "番茄工作法", "narrative_stage": "payoff", "emotion_level": 3},
        {"voiceover": "总结", "narrative_stage": "close", "emotion_level": 3},
    ]
    validator = EnhancedValidator()
    result = validator.validate_scenes(scenes)
    # 节奏问题是 warning 不是 error，所以 passed 仍可能为 True（取决于其他checks）
    assert len(result.warnings) > 0, "应有节奏 warning"
    print(f"✅ test_validator_all_same_emotion (warnings: {result.warnings})")


# ===================================================
# Main
# ===================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Step 13 & 15: 单元测试 (HookService + Validator)")
    print("=" * 60 + "\n")

    tests = [
        test_hook_generation_mock,
        test_hook_selection_prefers_question,
        test_hook_selection_fallback_to_contrast,
        test_hook_selection_fallback_to_first,
        test_default_hook_on_failure,
        test_fix_json,
        test_parse_response_valid,
        test_validator_pass_full,
        test_validator_empty_scenes,
        test_validator_no_hook_keyword,
        test_validator_duplicate_detection,
        test_validator_missing_stage,
        test_validator_all_same_emotion,
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
        print("✅ 所有单元测试通过")
    print("=" * 60)

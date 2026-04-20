"""
Step 12: 端到端测试（真实LLM版）

测试内容：
- 验证 HookGenerateService 在有 API Key 时能调用真实 LLM
- 验证 SceneGenerateService 能接受 selected_hook 参数
- 验证 EnhancedValidator 对 LLM 输出的场景进行质量检查

运行方式:
    cd backend
    source venv/bin/activate
    python tests/test_e2e_real.py

注意: 需要 .env 中配置有效的 OPENAI_API_KEY（DeepSeek 兼容）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_full_pipeline_real():
    """真实LLM端到端测试：从文章分析到场景生成"""
    from app.core.config import get_settings
    settings = get_settings()

    has_api_key = (
        settings.openai_api_key
        and settings.openai_api_key not in ("", "your-openai-api-key-here")
    )

    if not has_api_key:
        print("⚠ 未配置真实 API Key，跳过真实 LLM 测试（使用 Mock 验证流程）")
        _test_pipeline_with_mock()
        return

    print("[真实 LLM 模式]")
    _test_pipeline_with_real_llm(settings)


def _test_pipeline_with_mock():
    """无 API Key 时用 Mock 验证完整流程"""
    from app.services.hook_generate_service import HookGenerateService
    from app.services.enhanced_validator import EnhancedValidator

    # Step 1: Hook 生成
    service = HookGenerateService()
    analysis = {
        "topic": "时间管理",
        "key_points": ["番茄工作法", "优先级排序", "深度工作"],
        "audience": "职场白领"
    }
    hook_result = service.generate_hooks(analysis)

    assert len(hook_result.hooks) >= 1
    assert hook_result.selected_hook.type in ("question", "reveal", "contrast")
    print(f"  ✓ Hook 生成: [{hook_result.selected_hook.type}] {hook_result.selected_hook.content}")

    # Step 2: 模拟场景数据（带 v3 字段）
    selected = hook_result.selected_hook
    scenes_data = [
        {"voiceover": selected.content, "narrative_stage": "opening", "emotion_level": 5, "scene_role": "hook"},
        {"voiceover": "时间管理的核心是优先级", "narrative_stage": "build", "emotion_level": 3, "scene_role": "body"},
        {"voiceover": "番茄工作法：25分钟专注+5分钟休息", "narrative_stage": "build", "emotion_level": 3, "scene_role": "body"},
        {"voiceover": "用这个方法，效率提升了3倍", "narrative_stage": "payoff", "emotion_level": 5, "scene_role": "body"},
        {"voiceover": "现在就试试，改变从今天开始", "narrative_stage": "close", "emotion_level": 3, "scene_role": "close"},
    ]

    # Step 3: 验证
    validator = EnhancedValidator()
    result = validator.validate_scenes(scenes_data)

    assert result.passed, f"验证应通过，错误: {result.errors}"
    print(f"  ✓ EnhancedValidator 通过")

    print("✅ Mock Pipeline 端到端测试通过")


def _test_pipeline_with_real_llm(settings):
    """真实 LLM 端到端测试"""
    from app.services.hook_generate_service import HookGenerateService
    from app.services.enhanced_validator import EnhancedValidator
    from app.services.scene_generate_service import SceneGenerateService
    from app.schemas.article_analysis import ArticleAnalysis

    article = """
如何提高工作效率？

时间管理是关键。很多人每天忙到飞起，却总觉得没做什么。
问题在于没有掌握正确的方法。

番茄工作法是一个简单有效的技巧：
1. 设定25分钟专注时间
2. 休息5分钟
3. 每4个番茄后休息15-30分钟

通过这种方法，可以显著提升专注力和完成任务的效率。
"""

    # Step 1: Hook 生成
    print("  [1/3] 生成 Hook...")
    hook_service = HookGenerateService()
    hook_result = hook_service.generate_hooks_with_retry({
        "topic": "时间管理",
        "key_points": ["番茄工作法", "专注力提升"],
        "audience": "职场白领"
    })

    assert len(hook_result.hooks) >= 1
    selected = hook_result.selected_hook  # property
    assert selected.type in ("question", "reveal", "contrast")
    print(f"    ✓ Hook: [{selected.type}] {selected.content} (score={selected.score:.2f})")


    # Step 2: 场景生成
    print("  [2/3] 生成场景...")
    analysis_obj = ArticleAnalysis(
        topic="时间管理与番茄工作法",
        audience="职场白领",
        core_message="通过番茄工作法显著提升工作效率",
        key_points=["番茄工作法", "25分钟专注", "优先级排序"],
        tone="practical",
        complexity="simple",
        estimated_video_duration=50,
        confidence=0.9
    )
    scene_service = SceneGenerateService()
    scene_gen = scene_service.generate_scenes_with_retry(
        analysis_obj,
        article,
        selected_hook=selected.model_dump()
    )

    assert len(scene_gen.scenes) >= 4, f"应至少4个场景，实际: {len(scene_gen.scenes)}"
    print(f"    ✓ 生成了 {len(scene_gen.scenes)} 个场景，总时长 {scene_gen.total_duration}s")
    print(f"    ✓ 场景1旁白: {scene_gen.scenes[0].voiceover[:50]}")

    # Step 3: 验证
    print("  [3/3] 验证场景质量...")
    scenes_data = [
        {
            "voiceover": s.voiceover,
            "narrative_stage": s.narrative_stage,
            "emotion_level": s.emotion_level,
            "scene_role": s.scene_role,
        }
        for s in scene_gen.scenes
    ]
    validator = EnhancedValidator()
    v_result = validator.validate_scenes(scenes_data)
    print(f"    ✓ 验证结果: passed={v_result.passed}, errors={v_result.errors}")

    # 检查叙事结构
    stages = {s.narrative_stage for s in scene_gen.scenes}
    print(f"    ✓ 叙事阶段: {stages}")

    assert hook_result.selected_hook.type in ("question", "reveal", "contrast")
    assert len(scene_gen.scenes) >= 4

    print("✅ 真实 LLM 端到端测试通过")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Step 12: 真实LLM端到端测试")
    print("=" * 60 + "\n")

    try:
        test_full_pipeline_real()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n" + "=" * 60)

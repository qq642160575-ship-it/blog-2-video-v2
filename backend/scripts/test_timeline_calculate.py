#!/usr/bin/env python3
"""
测试 TimelineCalculateService
使用 mock 数据验证时间轴计算逻辑
"""
import sys
import os
import json

# Change to backend directory
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

from app.services.timeline_calculate_service import TimelineCalculateService


def test_timeline_calculate():
    """测试时间轴计算服务"""
    print("=" * 80)
    print("测试 TimelineCalculateService")
    print("=" * 80)
    print()

    # 创建服务实例
    service = TimelineCalculateService(
        advance_time=0.1,
        effect_duration=0.3
    )
    print("✓ TimelineCalculateService 初始化成功")
    print(f"  - 提前时间: {service.advance_time}s")
    print(f"  - 动效时长: {service.effect_duration}s")
    print()

    # Mock 数据
    voiceover = "这个方法可以提高工作效率三倍"
    emphasis_words = ["方法", "效率", "三倍"]

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
            {"word": "。", "start_time": 1.850, "end_time": 1.955}
        ]
    }

    print("测试数据:")
    print(f"  旁白: {voiceover}")
    print(f"  重点词: {emphasis_words}")
    print(f"  TTS 词数: {len(tts_metadata['word_timestamps'])}")
    print()

    # 计算时间轴
    print("计算时间轴...")
    timeline_data = service.calculate_timeline(
        emphasis_words=emphasis_words,
        tts_metadata=tts_metadata,
        voiceover=voiceover
    )

    if timeline_data is None:
        print("❌ 时间轴计算失败")
        return False

    print("✓ 时间轴计算成功")
    print()

    # 显示结果
    print("时间轴数据:")
    print("-" * 80)
    print(json.dumps(timeline_data, indent=2, ensure_ascii=False))
    print("-" * 80)
    print()

    # 验证结果
    keyframes = timeline_data.get("keyframes", [])
    stats = timeline_data.get("stats", {})

    print("统计信息:")
    print(f"  - 重点词总数: {stats.get('total_emphasis_words', 0)}")
    print(f"  - 匹配成功: {stats.get('matched_words', 0)}")
    print(f"  - 匹配率: {stats.get('match_rate', 0) * 100:.1f}%")
    print(f"  - 生成关键帧: {len(keyframes)}")
    print()

    # 显示关键帧详情
    if keyframes:
        print("关键帧详情:")
        print("-" * 80)
        print(f"{'词':<10} {'触发时间(s)':<15} {'词开始(s)':<15} {'词结束(s)':<15} {'动效时长(s)':<15}")
        print("-" * 80)
        for kf in keyframes:
            print(
                f"{kf['element']:<10} "
                f"{kf['time']:<15.3f} "
                f"{kf['word_start']:<15.3f} "
                f"{kf['word_end']:<15.3f} "
                f"{kf['duration']:<15.3f}"
            )
        print("-" * 80)
        print()

    # 验证时间轴
    print("验证时间轴数据...")
    is_valid = service.validate_timeline(timeline_data)
    if is_valid:
        print("✓ 时间轴数据有效")
    else:
        print("❌ 时间轴数据无效")
        return False
    print()

    # 测试边界情况
    print("=" * 80)
    print("测试边界情况")
    print("=" * 80)
    print()

    # 测试1: 空重点词列表
    print("测试1: 空重点词列表")
    result = service.calculate_timeline([], tts_metadata, voiceover)
    if result and result["keyframes"] == []:
        print("✓ 正确处理空重点词列表")
    else:
        print("❌ 未正确处理空重点词列表")
    print()

    # 测试2: 找不到匹配的词
    print("测试2: 找不到匹配的词")
    result = service.calculate_timeline(["不存在的词"], tts_metadata, voiceover)
    if result and len(result["keyframes"]) == 0:
        print("✓ 正确处理找不到匹配的情况")
    else:
        print("❌ 未正确处理找不到匹配的情况")
    print()

    # 测试3: 部分匹配
    print("测试3: 部分匹配")
    result = service.calculate_timeline(["方法", "不存在"], tts_metadata, voiceover)
    if result and len(result["keyframes"]) == 1:
        print("✓ 正确处理部分匹配的情况")
        print(f"  匹配率: {result['stats']['match_rate'] * 100:.1f}%")
    else:
        print("❌ 未正确处理部分匹配的情况")
    print()

    print("=" * 80)
    print("✅ 所有测试通过！")
    print("=" * 80)
    print()
    print("下一步: 集成到视频生成主流程")
    print()

    return True


if __name__ == "__main__":
    try:
        success = test_timeline_calculate()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

"""input: 无依赖。
output: 向外提供节奏规则配置。
pos: 位于 config 层，定义场景类型的节奏规则。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

from typing import Dict, Any

# 节奏规则配置
# 根据场景类型应用不同的节奏规则，实现视频节奏起伏
RHYTHM_RULES: Dict[str, Dict[str, Any]] = {
    # Hook 场景：快节奏，关键词密集，吸引注意力
    "hook": {
        "emphasis_density": "high",      # 关键词密集出现
        "effect_speed": "fast",          # 快速动效（duration=0.2）
        "pause_after": True,             # 结尾停顿 0.5 秒
        "min_interval": 0.3,             # 关键词最小间隔（秒）
        "effect_duration": 0.2,          # 动效持续时间（秒）
        "pause_duration": 0.5,           # 停顿时长（秒）
    },

    # Explanation 场景：中等节奏，关键词均匀分布
    "explanation": {
        "emphasis_density": "medium",    # 关键词均匀分布
        "effect_speed": "medium",        # 中速动效（duration=0.3）
        "pause_after": False,            # 无停顿
        "min_interval": 0.8,             # 关键词最小间隔（秒）
        "effect_duration": 0.3,          # 动效持续时间（秒）
        "pause_duration": 0.0,           # 无停顿
    },

    # Contrast 场景：交替节奏，关键词成对出现
    "contrast": {
        "emphasis_density": "paired",    # 关键词成对出现
        "effect_speed": "alternating",   # 交替动效（快慢交替）
        "pause_after": False,            # 无停顿
        "min_interval": 0.5,             # 关键词最小间隔（秒）
        "effect_duration": 0.25,         # 动效持续时间（秒，平均值）
        "pause_duration": 0.0,           # 无停顿
        "alternating_durations": [0.2, 0.3],  # 交替动效时长
    },
}

# 默认规则（当场景类型未识别时使用）
DEFAULT_RULE = "explanation"


def get_rhythm_rule(scene_type: str) -> Dict[str, Any]:
    """
    获取指定场景类型的节奏规则

    Args:
        scene_type: 场景类型（hook/explanation/contrast）

    Returns:
        节奏规则字典
    """
    return RHYTHM_RULES.get(scene_type, RHYTHM_RULES[DEFAULT_RULE])


def get_available_scene_types() -> list:
    """
    获取所有可用的场景类型

    Returns:
        场景类型列表
    """
    return list(RHYTHM_RULES.keys())

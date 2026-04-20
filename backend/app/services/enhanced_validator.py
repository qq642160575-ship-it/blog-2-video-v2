"""input: 依赖分镜数据 (scenes_data dicts) 进行质量检查。
output: 向外提供 ValidationResult 和场景验证能力。
pos: 位于 service 层，负责生成质量门禁。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

import re
import logging
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import List, Dict, Any

logger = logging.getLogger("app")


@dataclass
class ValidationResult:
    """场景验证结果"""
    passed: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    forced: bool = False  # 是否降低标准强制通过


class EnhancedValidator:
    """
    增强版场景验证器，执行4项检查：
    1. Hook 验证（第1场景是否有钩子）
    2. 重复度检查（相邻场景相似度）
    3. 结构完整性（叙事阶段是否完整）
    4. 节奏检查（情绪曲线是否有起伏）
    """

    def validate_scenes(self, scenes_data: List[Dict[str, Any]]) -> ValidationResult:
        """
        验证场景列表质量

        Args:
            scenes_data: 场景字典列表，每个字典包含 voiceover、narrative_stage、emotion_level 等字段

        Returns:
            ValidationResult
        """
        errors = []
        warnings = []

        if not scenes_data:
            return ValidationResult(passed=False, errors=["场景列表为空"])

        # 检查1: Hook 验证（第1场景）
        if not self._validate_hook(scenes_data[0]):
            errors.append("第1个场景缺少有效Hook（需要含疑问/数字/关键词）")

        # 检查2: 重复度检查
        duplicate_pairs = self._check_duplicate(scenes_data)
        if duplicate_pairs:
            errors.append(f"场景间内容重复（场景对: {duplicate_pairs}）")

        # 检查3: 结构完整性
        missing_stages = self._check_structure(scenes_data)
        if missing_stages:
            errors.append(f"缺少必要的叙事阶段: {missing_stages}")

        # 检查4: 节奏检查
        if not self._check_rhythm(scenes_data):
            warnings.append("情绪曲线过于平淡，建议增加高能量场景")

        passed = len(errors) == 0
        return ValidationResult(passed=passed, errors=errors, warnings=warnings)

    def _validate_hook(self, scene_data: Dict[str, Any]) -> bool:
        """
        验证第1个场景是否有效 Hook
        规则：疑问词/关键词 + 问号 + 数字，满足2项即通过
        """
        text = scene_data.get("voiceover", "")
        hook_keywords = [
            '为什么', '你知道吗', '原来', '竟然', '没想到',
            '真相', '秘密', '误区', '方法', '技巧'
        ]
        has_keyword = any(kw in text for kw in hook_keywords)
        has_question = '?' in text or '？' in text
        has_number = bool(re.search(r'\d+', text))

        score = sum([has_keyword, has_question, has_number])
        return score >= 2

    def _check_duplicate(self, scenes_data: List[Dict[str, Any]]) -> List[str]:
        """
        检查相邻场景是否重复（相似度 > 0.7）
        返回重复的场景对描述列表
        """
        duplicate_pairs = []
        for i in range(len(scenes_data) - 1):
            v1 = scenes_data[i].get("voiceover", "")
            v2 = scenes_data[i + 1].get("voiceover", "")
            similarity = SequenceMatcher(None, v1, v2).ratio()
            if similarity > 0.7:
                duplicate_pairs.append(f"场景{i+1}-{i+2}(相似度:{similarity:.2f})")
        return duplicate_pairs

    def _check_structure(self, scenes_data: List[Dict[str, Any]]) -> List[str]:
        """
        检查叙事结构完整性，必须包含4个阶段
        返回缺失的阶段列表
        """
        stages = {s.get("narrative_stage") for s in scenes_data}
        required = {"opening", "build", "payoff", "close"}
        missing = required - stages
        return list(missing)

    def _check_rhythm(self, scenes_data: List[Dict[str, Any]]) -> bool:
        """
        检查节奏：emotion_level 不能全为3，且至少有1个 ≥ 4 的场景
        """
        levels = [s.get("emotion_level", 3) for s in scenes_data]
        all_same = all(e == 3 for e in levels)
        has_high = any(e >= 4 for e in levels)
        return not all_same and has_high

"""input: 依赖 Scene 模型、TTS metadata 和节奏规则配置。
output: 向外提供时间轴计算服务，根据重点词和 TTS 时间戳生成动效时间轴，支持节奏规则。
pos: 位于 service 层，负责计算关键词强调的时间轴。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

from typing import List, Dict, Optional
from app.core.logging_config import get_logger
from app.config.rhythm_rules import get_rhythm_rule

logger = get_logger("app")


class TimelineCalculateService:
    """
    时间轴计算服务

    根据 emphasis_words 和 TTS word-level timestamps 计算动效时间轴
    """

    def __init__(self, advance_time: float = 0.1, effect_duration: float = 0.3):
        """
        初始化时间轴计算服务

        Args:
            advance_time: 动效提前时间（秒），在词开始前触发
            effect_duration: 动效持续时间（秒）
        """
        self.advance_time = advance_time
        self.effect_duration = effect_duration

    def calculate_timeline(
        self,
        emphasis_words: List[str],
        tts_metadata: Dict,
        voiceover: str
    ) -> Optional[Dict]:
        """
        计算时间轴数据

        Args:
            emphasis_words: 需要强调的关键词列表
            tts_metadata: TTS 返回的元数据，包含 word_timestamps
            voiceover: 原始旁白文本（用于调试）

        Returns:
            时间轴数据字典，包含 keyframes 列表
            如果计算失败返回 None
        """
        try:
            if not emphasis_words:
                logger.debug("No emphasis words provided, returning empty timeline")
                return {"keyframes": []}

            if not tts_metadata or "word_timestamps" not in tts_metadata:
                logger.warning("No word_timestamps in TTS metadata")
                return None

            word_timestamps = tts_metadata["word_timestamps"]
            if not word_timestamps:
                logger.warning("word_timestamps is empty")
                return None

            logger.info(f"Calculating timeline for {len(emphasis_words)} emphasis words")

            keyframes = []
            matched_count = 0

            for emphasis_word in emphasis_words:
                # 查找匹配的词时间戳
                timestamp_info = self._find_word_timestamp(
                    emphasis_word,
                    word_timestamps
                )

                if timestamp_info:
                    # 计算动效触发时间（提前一点）
                    trigger_time = max(0, timestamp_info["start_time"] - self.advance_time)

                    keyframe = {
                        "time": trigger_time,
                        "element": emphasis_word,
                        "action": "pop",
                        "duration": self.effect_duration,
                        "word_start": timestamp_info["start_time"],
                        "word_end": timestamp_info["end_time"]
                    }

                    keyframes.append(keyframe)
                    matched_count += 1

                    logger.debug(
                        f"Matched '{emphasis_word}': "
                        f"trigger={trigger_time:.3f}s, "
                        f"word_time={timestamp_info['start_time']:.3f}s-{timestamp_info['end_time']:.3f}s"
                    )
                else:
                    logger.warning(f"Could not find timestamp for emphasis word: '{emphasis_word}'")

            # 按时间排序
            keyframes.sort(key=lambda x: x["time"])

            logger.info(
                f"Timeline calculation completed: "
                f"{matched_count}/{len(emphasis_words)} words matched, "
                f"{len(keyframes)} keyframes generated"
            )

            return {
                "keyframes": keyframes,
                "stats": {
                    "total_emphasis_words": len(emphasis_words),
                    "matched_words": matched_count,
                    "match_rate": matched_count / len(emphasis_words) if emphasis_words else 0
                }
            }

        except Exception as e:
            logger.error(f"Failed to calculate timeline: {e}")
            return None

    def _find_word_timestamp(
        self,
        target_word: str,
        word_timestamps: List[Dict]
    ) -> Optional[Dict]:
        """
        在 word_timestamps 中查找目标词的时间戳

        Args:
            target_word: 目标词
            word_timestamps: TTS 返回的词级时间戳列表

        Returns:
            匹配的时间戳信息，包含 start_time 和 end_time
            如果未找到返回 None
        """
        # 精确匹配
        for word_info in word_timestamps:
            word = word_info.get("word", "")
            if word == target_word:
                return {
                    "start_time": word_info.get("start_time", 0),
                    "end_time": word_info.get("end_time", 0)
                }

        # 模糊匹配：目标词包含在 TTS 词中
        for word_info in word_timestamps:
            word = word_info.get("word", "")
            if target_word in word or word in target_word:
                logger.debug(f"Fuzzy match: '{target_word}' matched with '{word}'")
                return {
                    "start_time": word_info.get("start_time", 0),
                    "end_time": word_info.get("end_time", 0)
                }

        # 未找到匹配
        return None

    def validate_timeline(self, timeline_data: Dict) -> bool:
        """
        验证时间轴数据的有效性

        Args:
            timeline_data: 时间轴数据

        Returns:
            是否有效
        """
        if not timeline_data or "keyframes" not in timeline_data:
            return False

        keyframes = timeline_data["keyframes"]
        if not isinstance(keyframes, list):
            return False

        # 验证每个 keyframe 的结构
        for keyframe in keyframes:
            required_fields = ["time", "element", "action", "duration"]
            if not all(field in keyframe for field in required_fields):
                return False

            # 验证时间值
            if keyframe["time"] < 0 or keyframe["duration"] <= 0:
                return False

        return True

    def calculate_timeline_with_rhythm(
        self,
        emphasis_words: List[str],
        tts_metadata: Dict,
        voiceover: str,
        scene_type: str = "explanation",
        duration_sec: float = 8.0
    ) -> Optional[Dict]:
        """
        根据场景类型应用节奏规则计算时间轴

        Args:
            emphasis_words: 需要强调的关键词列表
            tts_metadata: TTS 返回的元数据
            voiceover: 原始旁白文本
            scene_type: 场景类型（hook/explanation/contrast）
            duration_sec: 场景总时长（秒）

        Returns:
            应用节奏规则后的时间轴数据
        """
        # 获取节奏规则
        rule = get_rhythm_rule(scene_type)
        logger.info(f"Applying rhythm rule for scene_type: {scene_type}")

        # 基础时间轴计算
        timeline = self.calculate_timeline(emphasis_words, tts_metadata, voiceover)
        if not timeline:
            return None

        # 应用节奏规则
        timeline = self._apply_rhythm_rule(timeline, rule, duration_sec)

        return timeline

    def _apply_rhythm_rule(
        self,
        timeline: Dict,
        rule: Dict,
        duration_sec: float
    ) -> Dict:
        """
        应用节奏规则调整时间轴

        Args:
            timeline: 基础时间轴数据
            rule: 节奏规则
            duration_sec: 场景总时长

        Returns:
            调整后的时间轴数据
        """
        keyframes = timeline.get("keyframes", [])
        if not keyframes:
            return timeline

        # 1. 调整动效速度
        effect_duration = rule.get("effect_duration", 0.3)

        if rule["effect_speed"] == "alternating":
            # 对比场景：交替动效
            alternating_durations = rule.get("alternating_durations", [0.2, 0.3])
            for i, kf in enumerate(keyframes):
                kf["duration"] = alternating_durations[i % len(alternating_durations)]
        else:
            # 统一动效时长
            for kf in keyframes:
                kf["duration"] = effect_duration

        # 2. 调整关键词间隔（如果需要）
        min_interval = rule.get("min_interval", 0.5)
        keyframes = self._adjust_intervals(keyframes, min_interval)

        # 3. 添加结尾停顿（如果需要）
        if rule.get("pause_after", False):
            pause_duration = rule.get("pause_duration", 0.5)
            pause_time = max(0, duration_sec - pause_duration)

            # 确保停顿不与最后一个关键帧重叠
            if keyframes:
                last_kf = keyframes[-1]
                last_kf_end = last_kf["time"] + last_kf["duration"]
                if pause_time < last_kf_end:
                    pause_time = last_kf_end

            keyframes.append({
                "time": pause_time,
                "element": "",
                "action": "pause",
                "duration": pause_duration,
                "word_start": pause_time,
                "word_end": pause_time + pause_duration
            })

        timeline["keyframes"] = keyframes
        timeline["rhythm_rule_applied"] = rule["effect_speed"]

        logger.info(
            f"Rhythm rule applied: {rule['effect_speed']} speed, "
            f"{len(keyframes)} keyframes, "
            f"pause_after={rule.get('pause_after', False)}"
        )

        return timeline

    def _adjust_intervals(
        self,
        keyframes: List[Dict],
        min_interval: float
    ) -> List[Dict]:
        """
        调整关键帧间隔，确保不小于最小间隔

        Args:
            keyframes: 关键帧列表
            min_interval: 最小间隔（秒）

        Returns:
            调整后的关键帧列表
        """
        if len(keyframes) <= 1:
            return keyframes

        adjusted = [keyframes[0]]

        for i in range(1, len(keyframes)):
            prev_kf = adjusted[-1]
            curr_kf = keyframes[i]

            # 计算前一个关键帧结束时间
            prev_end = prev_kf["time"] + prev_kf["duration"]

            # 如果当前关键帧太近，跳过
            if curr_kf["time"] - prev_end < min_interval:
                logger.debug(
                    f"Skipping keyframe '{curr_kf['element']}' due to min_interval constraint"
                )
                continue

            adjusted.append(curr_kf)

        return adjusted

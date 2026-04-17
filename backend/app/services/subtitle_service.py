"""input: 依赖音频或文本时间轴信息和文件系统。
output: 向外提供字幕生成、转换和导出能力。
pos: 位于 service 层，负责字幕处理。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

import os
import re
from typing import List, Optional
from app.schemas.subtitle import SubtitleSegment, SceneSubtitles
from app.core.config import get_settings

settings = get_settings()


class SubtitleService:
    """Service for generating subtitles from text"""

    def __init__(self):
        """Initialize subtitle service"""
        self.storage_path = settings.storage_path

        # Create subtitles directory
        self.subtitle_dir = os.path.join(self.storage_path, "subtitles")
        os.makedirs(self.subtitle_dir, exist_ok=True)

    def split_text_by_punctuation(self, text: str) -> List[str]:
        """
        Split text into segments by punctuation

        Args:
            text: Text to split

        Returns:
            List of text segments
        """
        # Split by Chinese and English punctuation
        # Keep the punctuation with the segment
        segments = re.split(r'([。！？,.!?])', text)

        # Combine text with punctuation
        result = []
        i = 0
        while i < len(segments):
            if segments[i].strip():
                # If next item is punctuation, combine
                if i + 1 < len(segments) and segments[i + 1] in '。！？,.!?':
                    result.append(segments[i] + segments[i + 1])
                    i += 2
                else:
                    result.append(segments[i])
                    i += 1
            else:
                i += 1

        return [s.strip() for s in result if s.strip()]

    def generate_subtitles(
        self,
        text: str,
        duration_ms: int,
        min_segment_ms: int = 1000,
        max_segment_ms: int = 3000
    ) -> List[SubtitleSegment]:
        """
        Generate subtitle segments from text

        Args:
            text: Text to generate subtitles for
            duration_ms: Total duration in milliseconds
            min_segment_ms: Minimum segment duration (default: 1000ms)
            max_segment_ms: Maximum segment duration (default: 3000ms)

        Returns:
            List of SubtitleSegment
        """
        # Split text into segments
        segments = self.split_text_by_punctuation(text)

        if not segments:
            return []

        # Calculate time per character
        total_chars = sum(len(s) for s in segments)
        if total_chars == 0:
            return []

        ms_per_char = duration_ms / total_chars

        # Generate subtitle segments
        subtitles = []
        current_time = 0

        for segment_text in segments:
            # Calculate segment duration based on character count
            segment_chars = len(segment_text)
            segment_duration = int(segment_chars * ms_per_char)

            # Clamp to min/max duration
            segment_duration = max(min_segment_ms, min(segment_duration, max_segment_ms))

            # Ensure we don't exceed total duration
            if current_time + segment_duration > duration_ms:
                segment_duration = duration_ms - current_time

            if segment_duration > 0:
                subtitles.append(SubtitleSegment(
                    text=segment_text,
                    start_ms=current_time,
                    end_ms=current_time + segment_duration
                ))

                current_time += segment_duration

            # Stop if we've reached the end
            if current_time >= duration_ms:
                break

        return subtitles

    def generate_scene_subtitles(
        self,
        scene_id: str,
        voiceover: str,
        duration_sec: int
    ) -> SceneSubtitles:
        """
        Generate subtitles for a scene

        Args:
            scene_id: Scene ID
            voiceover: Voiceover text
            duration_sec: Scene duration in seconds

        Returns:
            SceneSubtitles object
        """
        duration_ms = duration_sec * 1000

        segments = self.generate_subtitles(voiceover, duration_ms)

        return SceneSubtitles(
            scene_id=scene_id,
            segments=segments,
            total_duration_ms=duration_ms
        )

    def generate_batch(
        self,
        scenes: list
    ) -> dict:
        """
        Generate subtitles for multiple scenes

        Args:
            scenes: List of scene dicts with scene_id, voiceover, duration_sec

        Returns:
            Dict mapping scene_id to SceneSubtitles
        """
        results = {}

        for scene in scenes:
            scene_id = scene.get("scene_id")
            voiceover = scene.get("voiceover")
            duration_sec = scene.get("duration_sec")

            try:
                subtitles = self.generate_scene_subtitles(
                    scene_id=scene_id,
                    voiceover=voiceover,
                    duration_sec=duration_sec
                )
                results[scene_id] = subtitles
            except Exception as e:
                print(f"Warning: Failed to generate subtitles for {scene_id}: {e}")

        return results

    def export_srt(
        self,
        scene_subtitles: SceneSubtitles,
        output_filename: Optional[str] = None
    ) -> str:
        """
        Export subtitles to SRT format

        Args:
            scene_subtitles: SceneSubtitles object
            output_filename: Optional output filename

        Returns:
            Path to SRT file
        """
        if not output_filename:
            output_filename = f"{scene_subtitles.scene_id}.srt"

        output_path = os.path.join(self.subtitle_dir, output_filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(scene_subtitles.segments, 1):
                # Convert ms to SRT time format (HH:MM:SS,mmm)
                start_time = self._ms_to_srt_time(segment.start_ms)
                end_time = self._ms_to_srt_time(segment.end_ms)

                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{segment.text}\n")
                f.write("\n")

        return output_path

    def _ms_to_srt_time(self, ms: int) -> str:
        """
        Convert milliseconds to SRT time format

        Args:
            ms: Milliseconds

        Returns:
            Time string in format HH:MM:SS,mmm
        """
        hours = ms // 3600000
        ms %= 3600000
        minutes = ms // 60000
        ms %= 60000
        seconds = ms // 1000
        milliseconds = ms % 1000

        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

from pydantic import BaseModel, Field
from typing import List


class SubtitleSegment(BaseModel):
    """Single subtitle segment"""

    text: str = Field(description="字幕文本")
    start_ms: int = Field(description="开始时间（毫秒）", ge=0)
    end_ms: int = Field(description="结束时间（毫秒）", ge=0)


class SceneSubtitles(BaseModel):
    """Subtitles for a scene"""

    scene_id: str = Field(description="场景 ID")
    segments: List[SubtitleSegment] = Field(description="字幕片段列表")
    total_duration_ms: int = Field(description="总时长（毫秒）", ge=0)

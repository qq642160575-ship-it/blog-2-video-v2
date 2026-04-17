"""input: 依赖 Pydantic 和字幕字段约定。
output: 向外提供字幕结构与导出结构。
pos: 位于 schema 层，约束字幕数据。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

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

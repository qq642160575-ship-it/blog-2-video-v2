from pydantic import BaseModel, Field
from typing import List, Optional


class ArticleAnalysis(BaseModel):
    """Article analysis result from LLM"""

    topic: str = Field(
        description="文章的核心主题，简洁明了（5-15字）"
    )

    audience: str = Field(
        description="目标受众群体，如：技术开发者、产品经理、普通用户等"
    )

    core_message: str = Field(
        description="文章的核心信息或观点（一句话总结）"
    )

    key_points: List[str] = Field(
        description="文章的关键要点列表（3-5个要点）",
        min_items=3,
        max_items=5
    )

    tone: str = Field(
        description="文章的语气风格：professional（专业）、casual（轻松）、educational（教育）等"
    )

    complexity: str = Field(
        description="内容复杂度：beginner（入门）、intermediate（中级）、advanced（高级）"
    )

    estimated_video_duration: int = Field(
        description="建议的视频时长（秒），范围 45-60",
        ge=45,
        le=60
    )

    confidence: float = Field(
        description="分析结果的置信度（0-1）",
        ge=0.0,
        le=1.0
    )

    reasoning: Optional[str] = Field(
        default=None,
        description="分析推理过程（可选）"
    )

from pydantic import BaseModel, Field
from typing import List, Optional


class SceneData(BaseModel):
    """Single scene data from LLM"""

    template_type: str = Field(
        description="场景模板类型：hook_title/bullet_explain/compare_process/quote_highlight/summary_cta"
    )

    goal: str = Field(
        description="场景目标，如：开头钩子、核心概念解释、对比优势等"
    )

    voiceover: str = Field(
        description="旁白文本，需要口语化、简洁"
    )

    screen_text: List[str] = Field(
        description="屏幕文字列表，2-4个关键词或短句",
        min_items=1,
        max_items=5
    )

    duration_sec: int = Field(
        description="场景时长（秒），范围 5-10",
        ge=5,
        le=10
    )

    pace: str = Field(
        description="节奏：fast（快速）、medium（中等）、slow（慢速）"
    )

    transition: str = Field(
        description="转场效果：cut（切换）、fade（淡入淡出）、slide（滑动）"
    )

    visual_params: Optional[dict] = Field(
        default=None,
        description="视觉参数，如强调文字、对比类型等"
    )


class SceneGeneration(BaseModel):
    """Scene generation result from LLM"""

    scenes: List[SceneData] = Field(
        description="场景列表，6-10个场景",
        min_items=6,
        max_items=10
    )

    total_duration: int = Field(
        description="总时长（秒），范围 45-60",
        ge=45,
        le=60
    )

    narrative_flow: str = Field(
        description="叙事流程说明，如：钩子→概念→优势→应用→总结"
    )

    confidence: float = Field(
        description="生成置信度（0-1）",
        ge=0.0,
        le=1.0
    )

    reasoning: Optional[str] = Field(
        default=None,
        description="生成推理过程（可选）"
    )

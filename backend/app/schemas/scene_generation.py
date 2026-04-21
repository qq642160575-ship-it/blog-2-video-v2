"""input: 依赖 Pydantic 和分镜生成字段约定（含 v3 叙事质量字段）。
output: 向外提供 SceneGeneration 与场景结构。
pos: 位于 schema 层，约束分镜生成结果。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

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

    # v3: 叙事质量字段
    scene_role: str = Field(
        default="body",
        description="场景角色：hook | body | close"
    )
    narrative_stage: str = Field(
        default="build",
        description="叙事阶段：opening | build | payoff | close"
    )
    emotion_level: int = Field(
        default=3,
        ge=1, le=5,
        description="情绪强度：1（低）-5（高）"
    )

    # v4: 表达力与节奏字段
    emphasis_words: Optional[List[str]] = Field(
        default=None,
        description="需要强调的关键词，2-3个最重要的词",
        max_items=3
    )

    # v5: 节奏规则字段（阶段2）
    scene_type: str = Field(
        default="explanation",
        description="场景类型：hook（开场吸引）| explanation（解释说明）| contrast（对比场景）"
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

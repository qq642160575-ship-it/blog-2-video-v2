"""input: 依赖 Pydantic BaseModel。
output: 向外提供 Hook 和 HookResult 数据结构。
pos: 位于 schema 层，定义 Hook 生成的输入输出契约。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

from pydantic import BaseModel, Field
from typing import List, Literal


class Hook(BaseModel):
    """单个开场 Hook"""
    type: Literal["question", "reveal", "contrast"] = Field(
        ..., description="Hook 类型：疑问/揭秘/对比"
    )
    content: str = Field(..., description="Hook 文本内容，用于第1场景的旁白")
    score: float = Field(..., ge=0.0, le=1.0, description="Hook 质量评分 0.0-1.0")


class HookResult(BaseModel):
    """Hook 生成结果，包含3个候选 Hook 和选中索引"""
    hooks: List[Hook] = Field(..., min_length=1, description="候选 Hook 列表（通常3个）")
    selected_index: int = Field(0, ge=0, description="最优 Hook 的索引")

    @property
    def selected_hook(self) -> Hook:
        """获取被选中的 Hook"""
        return self.hooks[self.selected_index]

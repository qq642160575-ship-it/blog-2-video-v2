"""input: 依赖 LLM 客户端、Hook schema 和文章分析结果。
output: 向外提供 Hook 生成能力（真实LLM版，含 mock 兜底）。
pos: 位于 service 层，负责开场 Hook 的生成与选优。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

import os
import time
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.schemas.hook import HookResult
from app.core.config import get_settings
from app.core.logging_config import get_logger

settings = get_settings()
logger = get_logger("app")


class HookGenerateService:
    """
    开场 Hook 生成服务（v4 - 使用 with_structured_output）。
    - 使用 LangChain 结构化输出，自动解析为 Pydantic 模型
    - LLM 不可用时自动降级为 Mock
    - 支持最多 max_retries 次重试
    """

    def __init__(self):
        self._llm = None  # 懒加载
        self._prompt = None  # 懒加载

    def _get_llm(self):
        """懒加载 LLM 客户端（避免 import 时就需要 API Key）"""
        if self._llm is None:
            try:
                if os.environ.get("ALL_PROXY", "").startswith("socks://"):
                    os.environ.pop("ALL_PROXY", None)

                self._llm = ChatOpenAI(
                    model="deepseek-chat",
                    temperature=0.7,
                    openai_api_key=settings.openai_api_key,
                    openai_api_base=settings.openai_base_url,
                    request_timeout=30,
                ).with_structured_output(schema=HookResult, method="function_calling")
            except Exception as e:
                logger.warning(f"LLM 初始化失败，将使用 Mock: {e}")
        return self._llm

    def _get_prompt(self):
        """懒加载 Prompt 模板"""
        if self._prompt is None:
            self._prompt = ChatPromptTemplate.from_messages([
                ("system", """你是短视频Hook专家。基于用户提供的信息，生成3个不同类型的开场Hook。

要求：
1. 生成3个Hook，类型分别为：question（疑问）、contrast（对比）、reveal（揭秘）
2. 每个Hook必须在3秒内制造好奇缺口
3. 不能夸大或偏离主题
4. 每个Hook给出质量评分（0.0-1.0）
5. 自动选择最佳Hook（优先 question，其次 contrast）

返回格式：
- hooks: Hook列表（3个）
  - type: question|contrast|reveal
  - content: Hook文本内容
  - score: 质量评分（0.0-1.0）
- selected_index: 选中的Hook索引（0-2）"""),
                ("user", """请根据以下信息生成3个开场Hook：

主题: {theme}
关键点: {key_points}
目标受众: {audience}

请生成3个不同类型的Hook，并自动选择最佳的一个。""")
            ])
        return self._prompt

    # ------------------------------------------------------------------
    # 公开接口
    # ------------------------------------------------------------------

    def generate_hooks(self, analysis: dict) -> HookResult:
        """
        生成3个开场 Hook。
        优先调用真实 LLM；LLM 不可用时降级到 Mock。

        Args:
            analysis: 文章分析结果，包含 theme/topic、key_points、target_audience 等

        Returns:
            HookResult
        """
        # 判断是否有有效 API Key
        has_api_key = (
            settings.openai_api_key
            and settings.openai_api_key not in ("", "your-openai-api-key-here")
        )

        if has_api_key:
            try:
                return self._generate_hooks_real(analysis)
            except Exception as e:
                logger.warning(f"真实 LLM Hook 生成失败，降级到 Mock: {e}")

        return self._generate_hooks_mock(analysis)

    def generate_hooks_with_retry(
        self, analysis: dict, max_retries: int = 3
    ) -> HookResult:
        """带重试和兜底的 Hook 生成"""
        for attempt in range(max_retries):
            try:
                logger.info(f"开始生成Hook (尝试 {attempt+1}/{max_retries})")
                result = self.generate_hooks(analysis)
                logger.info(
                    f"Hook生成成功: [{result.selected_hook.type}] {result.selected_hook.content}"
                )
                return result
            except Exception as e:
                logger.warning(f"Hook生成失败 (尝试 {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    logger.error("Hook生成全部失败，使用默认Hook")
                    return self._get_default_hook(analysis)

    # ------------------------------------------------------------------
    # 真实 LLM 实现（使用 with_structured_output）
    # ------------------------------------------------------------------

    def _generate_hooks_real(self, analysis: dict) -> HookResult:
        """调用真实 LLM 生成 Hook（使用结构化输出）"""
        llm = self._get_llm()
        if llm is None:
            raise RuntimeError("LLM 客户端不可用")

        prompt = self._get_prompt()

        # 提取分析数据
        theme = analysis.get("theme") or analysis.get("topic") or "未知主题"
        key_points = analysis.get("key_points") or []
        audience = analysis.get("target_audience") or analysis.get("audience") or "普通大众"

        key_points_text = "、".join(key_points) if key_points else "无"

        # 构建 chain 并调用
        chain = prompt | llm
        result = chain.invoke({
            "theme": theme,
            "key_points": key_points_text,
            "audience": audience,
        })

        # result 已经是 HookResult 对象，直接返回
        return result

    # ------------------------------------------------------------------
    # Mock 实现（兜底）
    # ------------------------------------------------------------------

    def _generate_hooks_mock(self, analysis: dict) -> HookResult:
        """Mock 版本：返回固定模板 Hook"""
        from app.schemas.hook import Hook

        theme = analysis.get("theme") or analysis.get("topic") or "未知主题"
        hooks = [
            Hook(type="question", content=f"为什么{theme}这么重要？", score=0.85),
            Hook(type="contrast", content=f"你以为{theme}很简单？其实大部分人都错了", score=0.78),
            Hook(type="reveal", content=f"90%的人不知道的{theme}秘密", score=0.72),
        ]
        return HookResult(hooks=hooks, selected_index=0)

    def _get_default_hook(self, analysis: dict) -> HookResult:
        """最终兜底 Hook（所有重试均失败时使用）"""
        from app.schemas.hook import Hook

        theme = analysis.get("theme") or analysis.get("topic") or "这个话题"
        hook = Hook(
            type="reveal",
            content=f"接下来我要分享{theme}的关键方法",
            score=0.5
        )
        return HookResult(hooks=[hook], selected_index=0)

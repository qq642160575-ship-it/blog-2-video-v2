"""input: 依赖 LLM 客户端、Hook schema 和文章分析结果。
output: 向外提供 Hook 生成能力（真实LLM版，含 mock 兜底）。
pos: 位于 service 层，负责开场 Hook 的生成与选优。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

import os
import re
import json
import time
import logging
from typing import Optional, List

from app.schemas.hook import Hook, HookResult

logger = logging.getLogger("app")


class HookGenerateService:
    """
    开场 Hook 生成服务（v3）。
    - 优先调用真实 LLM（DeepSeek）
    - LLM 不可用时自动降级为 Mock
    - 支持最多 max_retries 次重试
    """

    def __init__(self):
        self._llm = None  # 懒加载

    def _get_llm(self):
        """懒加载 LLM 客户端（避免 import 时就需要 API Key）"""
        if self._llm is None:
            try:
                from langchain_openai import ChatOpenAI
                from app.core.config import get_settings
                settings = get_settings()

                if os.environ.get("ALL_PROXY", "").startswith("socks://"):
                    os.environ.pop("ALL_PROXY", None)

                self._llm = ChatOpenAI(
                    model="deepseek-chat",
                    temperature=0.7,
                    openai_api_key=settings.openai_api_key,
                    openai_api_base=settings.openai_base_url,
                    request_timeout=30,
                )
            except Exception as e:
                logger.warning(f"LLM 初始化失败，将使用 Mock: {e}")
        return self._llm

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
        from app.core.config import get_settings
        settings = get_settings()

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
    # 真实 LLM 实现
    # ------------------------------------------------------------------

    def _generate_hooks_real(self, analysis: dict) -> HookResult:
        """调用真实 LLM 生成 Hook"""
        llm = self._get_llm()
        if llm is None:
            raise RuntimeError("LLM 客户端不可用")

        prompt = self._build_prompt(analysis)
        response = llm.invoke(prompt)
        response_text = response.content if hasattr(response, "content") else str(response)

        hooks = self._parse_response(response_text)
        selected_index = self._select_best(hooks)
        return HookResult(hooks=hooks, selected_index=selected_index)

    def _build_prompt(self, analysis: dict) -> str:
        theme = analysis.get("theme") or analysis.get("topic") or "未知主题"
        key_points = analysis.get("key_points") or []
        audience = analysis.get("target_audience") or analysis.get("audience") or "普通大众"

        key_points_text = "、".join(key_points) if key_points else "无"

        return f"""你是短视频Hook专家。基于以下信息，生成3个不同类型的开场Hook。

主题: {theme}
关键点: {key_points_text}
目标受众: {audience}

要求：
1. 生成3个Hook，类型分别为：question（疑问）、contrast（对比）、reveal（揭秘）
2. 每个Hook必须在3秒内制造好奇缺口
3. 不能夸大或偏离主题
4. 每个Hook给出质量评分（0.0-1.0）

只返回 JSON，不要任何解释：
{{
  "hooks": [
    {{"type": "question", "content": "为什么...", "score": 0.85}},
    {{"type": "contrast", "content": "你以为...其实...", "score": 0.78}},
    {{"type": "reveal", "content": "90%的人不知道...", "score": 0.72}}
  ]
}}"""

    def _parse_response(self, response_text: str) -> List[Hook]:
        """解析 LLM 响应（带 JSON 修复）"""
        # 提取 JSON 块
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        text = json_match.group(0) if json_match else response_text

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            text = self._fix_json(text)
            data = json.loads(text)

        hooks_raw = data.get("hooks", [])
        if not hooks_raw:
            raise ValueError("LLM 响应中没有 hooks 字段")

        hooks = []
        for h in hooks_raw:
            try:
                hooks.append(Hook(
                    type=h["type"],
                    content=h["content"],
                    score=float(h.get("score", 0.7))
                ))
            except Exception as e:
                logger.warning(f"跳过无效 Hook: {h} ({e})")

        if not hooks:
            raise ValueError("未能解析出任何有效 Hook")

        return hooks

    def _select_best(self, hooks: List[Hook]) -> int:
        """选优：优先 question，其次 contrast"""
        for i, hook in enumerate(hooks):
            if hook.type == "question":
                return i
        for i, hook in enumerate(hooks):
            if hook.type == "contrast":
                return i
        return 0

    # ------------------------------------------------------------------
    # Mock 实现（兜底）
    # ------------------------------------------------------------------

    def _generate_hooks_mock(self, analysis: dict) -> HookResult:
        """Mock 版本：返回固定模板 Hook"""
        theme = analysis.get("theme") or analysis.get("topic") or "未知主题"
        hooks = [
            Hook(type="question", content=f"为什么{theme}这么重要？", score=0.85),
            Hook(type="contrast", content=f"你以为{theme}很简单？其实大部分人都错了", score=0.78),
            Hook(type="reveal", content=f"90%的人不知道的{theme}秘密", score=0.72),
        ]
        return HookResult(hooks=hooks, selected_index=0)

    def _get_default_hook(self, analysis: dict) -> HookResult:
        """最终兜底 Hook（所有重试均失败时使用）"""
        theme = analysis.get("theme") or analysis.get("topic") or "这个话题"
        hook = Hook(
            type="reveal",
            content=f"接下来我要分享{theme}的关键方法",
            score=0.5
        )
        return HookResult(hooks=[hook], selected_index=0)

    @staticmethod
    def _fix_json(text: str) -> str:
        """修复常见 LLM JSON 格式错误"""
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)
        text = re.sub(r'//.*?\n', '\n', text)
        return text

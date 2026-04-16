import json
import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.schemas.article_analysis import ArticleAnalysis
from app.core.config import get_settings

settings = get_settings()


class ArticleParseService:
    """Service for parsing articles using LLM"""

    def __init__(self):
        # Some environments export ALL_PROXY=socks://..., which openai/httpx
        # rejects. Remove the unsupported value and keep HTTP(S)_PROXY.
        if os.environ.get("ALL_PROXY", "").startswith("socks://"):
            os.environ.pop("ALL_PROXY", None)

        self.llm = ChatOpenAI(
            model="deepseek-chat",
            temperature=0.3,
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.openai_base_url
        )

        self.parser = JsonOutputParser()

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的内容分析师，擅长分析技术文章并提取关键信息。

你的任务是分析用户提供的文章，并返回结构化的分析结果。

请仔细阅读文章内容，理解其核心主题、目标受众、关键要点等信息。

你必须返回一个 JSON 对象，包含以下字段：
- topic: 文章的核心主题（5-15字）
- audience: 目标受众群体
- core_message: 核心信息或观点（一句话）
- key_points: 关键要点列表（3-5个）
- tone: 语气风格（professional/casual/educational）
- complexity: 内容复杂度（beginner/intermediate/advanced）
- estimated_video_duration: 建议视频时长（45-60秒）
- confidence: 分析置信度（0-1）
- reasoning: 分析推理过程（可选）

请确保返回的 JSON 格式正确，可以被解析。"""),
            ("user", "请分析以下文章：\n\n{article_content}")
        ])

    def parse_article(self, article_content: str) -> ArticleAnalysis:
        """
        Parse article content and extract structured information

        Args:
            article_content: The article text to analyze

        Returns:
            ArticleAnalysis object with extracted information

        Raises:
            ValueError: If parsing fails or LLM returns invalid data
        """
        try:
            # Create chain
            chain = self.prompt | self.llm | self.parser

            # Invoke LLM
            result = chain.invoke({"article_content": article_content})

            # Validate and create ArticleAnalysis object
            analysis = ArticleAnalysis(**result)

            return analysis

        except Exception as e:
            raise ValueError(f"Failed to parse article: {str(e)}")

    def parse_article_with_retry(
        self,
        article_content: str,
        max_retries: int = 3
    ) -> ArticleAnalysis:
        """
        Parse article with retry logic

        Args:
            article_content: The article text to analyze
            max_retries: Maximum number of retry attempts

        Returns:
            ArticleAnalysis object

        Raises:
            ValueError: If all retry attempts fail
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                return self.parse_article(article_content)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    print(f"Parse attempt {attempt + 1} failed: {e}. Retrying...")
                    continue
                else:
                    break

        raise ValueError(
            f"Failed to parse article after {max_retries} attempts. "
            f"Last error: {last_error}"
        )

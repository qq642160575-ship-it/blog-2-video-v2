"""input: 依赖 LLM、分镜 schema 和 AI 日志服务（v3：含 Hook 和叙事质量字段）。
output: 向外提供分镜生成与重试能力。
pos: 位于 service 层，负责分镜脚本生成。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

import json
import os
import time
from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.schemas.scene_generation import SceneGeneration
from app.schemas.article_analysis import ArticleAnalysis
from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.services.ai_logger_service import create_ai_logger

settings = get_settings()
logger = get_logger("app")


class SceneGenerateService:
    """Service for generating video scenes using LLM"""

    def __init__(self):
        if os.environ.get("ALL_PROXY", "").startswith("socks://"):
            os.environ.pop("ALL_PROXY", None)

        self.llm = ChatOpenAI(
            model="deepseek-chat",
            temperature=0.5,
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.openai_base_url,
            request_timeout=60
        ).with_structured_output(schema=SceneGeneration)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的视频脚本编剧，擅长将文章内容转化为短视频分镜脚本。

你的任务是根据文章分析结果和提供的Hook，生成 6-10 个视频场景（scenes）。

## 场景模板类型
- hook_title: 开头钩子，吸引注意力
- bullet_explain: 要点解释，逐条说明
- compare_process: 对比说明，展示优势
- quote_highlight: 引用高亮，强调关键信息
- summary_cta: 总结收尾，引导行动

## 【v3强制约束】叙事结构
1. 第1场景必须使用提供的Hook作为旁白开场
2. 叙事阶段分配：
   - 场景1-2: opening（高能量4-5，抛出Hook，建立好奇）
   - 场景3-5: build（中能量2-3，展开问题，铺垫信息）
   - 场景6-7: payoff（高能量4-5，给出答案，交付价值）
   - 最后1场景: close（中能量3，总结收束）
3. 禁止场景间内容重复（相似度不超过30%）
4. 总时长控制在 45-60 秒
5. 旁白要口语化、简洁，避免书面语

## 返回格式
必须返回纯 JSON，包含以下字段：
- scenes: 场景列表（6-10个）
  - template_type: 模板类型
  - goal: 场景目标
  - voiceover: 旁白文本
  - screen_text: 屏幕文字列表（2-4个）
  - duration_sec: 时长（5-10秒）
  - pace: 节奏（fast/medium/slow）
  - transition: 转场（cut/fade/slide）
  - scene_role: hook|body|close
  - narrative_stage: opening|build|payoff|close
  - emotion_level: 1-5
- total_duration: 总时长（45-60秒）
- narrative_flow: 叙事流程说明
- confidence: 生成置信度（0-1）

请确保返回的 JSON 格式正确，可以被解析。"""),
            ("user", """请根据以下信息，生成视频分镜脚本：

文章主题：{topic}
目标受众：{audience}
核心信息：{core_message}
关键要点：
{key_points}
语气风格：{tone}
复杂度：{complexity}

【必须使用的开场Hook】
Hook类型: {hook_type}
Hook内容: {hook_content}

请生成 6-10 个场景的视频脚本，第1场景旁白必须使用上面提供的Hook内容。""")
        ])

    def generate_scenes(
        self,
        article_analysis: ArticleAnalysis,
        article_content: Optional[str] = None,
        job_id: str = None,
        project_id: str = None,
        selected_hook: Optional[dict] = None,  # v3: Hook dict {type, content, score}
        feedback: Optional[str] = None,        # v3: 重试时的错误反馈
    ) -> SceneGeneration:
        """
        Generate video scenes based on article analysis

        Args:
            article_analysis: Article analysis result
            article_content: Optional original article content for reference
            job_id: Optional job ID for logging
            project_id: Optional project ID for logging

        Returns:
            SceneGeneration object with scene list

        Raises:
            ValueError: If generation fails or LLM returns invalid data
        """
        start_time = time.time()

        try:
            logger.info(f"Starting scene generation - Job: {job_id}, Project: {project_id}")
            logger.debug(f"Article topic: {article_analysis.topic}")

            # Format key points
            key_points_text = "\n".join([
                f"{i+1}. {point}"
                for i, point in enumerate(article_analysis.key_points)
            ])

            # v3: Hook 信息（无 Hook 时使用占位符）
            hook_type = selected_hook.get("type", "question") if selected_hook else "question"
            hook_content = selected_hook.get("content", "请用一句引人入胜的话开场") if selected_hook else "请用一句引人入胜的话开场"

            # 构建调用参数
            invoke_params = {
                "topic": article_analysis.topic,
                "audience": article_analysis.audience,
                "core_message": article_analysis.core_message,
                "key_points": key_points_text,
                "tone": article_analysis.tone,
                "complexity": article_analysis.complexity,
                "hook_type": hook_type,
                "hook_content": hook_content,
            }

            # v3: 如果有重试反馈，追加到 user message 中
            if feedback:
                invoke_params["topic"] = f"{article_analysis.topic}\n\n【重试反馈】{feedback}"

            # Create chain
            chain = self.prompt | self.llm
            prompt_value = self.prompt.format_prompt(**invoke_params)
            prompt_text = prompt_value.to_string()

            # Invoke LLM
            result = chain.invoke(invoke_params)

            duration_ms = int((time.time() - start_time) * 1000)
            logger.info(f"Scene generation completed in {duration_ms}ms")
            logger.debug(f"Generated {len(result.scenes)} scenes")

            # result is already a SceneGeneration object
            create_ai_logger().log_ai_call(
                operation="scene_generation",
                model="deepseek-chat",
                prompt=prompt_text,
                response=result.model_dump_json(),
                job_id=job_id,
                project_id=project_id,
                duration_ms=duration_ms,
                status="success"
            )

            return result

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Failed to generate scenes after {duration_ms}ms: {str(e)}")
            try:
                create_ai_logger().log_ai_call(
                    operation="scene_generation",
                    model="deepseek-chat",
                    prompt=locals().get("prompt_text", json.dumps(article_analysis.model_dump(), ensure_ascii=False)),
                    response="",
                    job_id=job_id,
                    project_id=project_id,
                    duration_ms=duration_ms,
                    status="error",
                    error_message=str(e)
                )
            except Exception:
                logger.exception("Failed to write AI error log")
            raise ValueError(f"Failed to generate scenes: {str(e)}")

    def generate_scenes_with_retry(
        self,
        article_analysis: ArticleAnalysis,
        article_content: Optional[str] = None,
        job_id: str = None,
        project_id: str = None,
        max_retries: int = 3,
        selected_hook: Optional[dict] = None,  # v3
    ) -> SceneGeneration:
        """
        Generate scenes with retry logic

        Args:
            article_analysis: Article analysis result
            article_content: Optional original article content
            max_retries: Maximum number of retry attempts
            selected_hook: v3 selected Hook dict

        Returns:
            SceneGeneration object

        Raises:
            ValueError: If all retry attempts fail
        """
        last_error = None

        for attempt in range(max_retries):
            feedback = None
            if attempt > 0 and last_error:
                feedback = f"上次生成失败原因: {last_error}"
            try:
                return self.generate_scenes(
                    article_analysis,
                    article_content,
                    job_id=job_id,
                    project_id=project_id,
                    selected_hook=selected_hook,
                    feedback=feedback,
                )
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    print(f"Scene generation attempt {attempt + 1} failed: {e}. Retrying...")
                    continue
                else:
                    break

        raise ValueError(
            f"Failed to generate scenes after {max_retries} attempts. "
            f"Last error: {last_error}"
        )

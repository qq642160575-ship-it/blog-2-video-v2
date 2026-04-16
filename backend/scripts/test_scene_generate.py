#!/usr/bin/env python3
"""
Test Scene Generate Service with Real LLM
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.article_parse_service import ArticleParseService
from app.services.scene_generate_service import SceneGenerateService


def test_scene_generate():
    print("=" * 70)
    print("Test Scene Generate Service (Real LLM)")
    print("=" * 70)
    print()

    # Test article
    article = """# 什么是 RAG

RAG（Retrieval-Augmented Generation）是一种结合了检索和生成的 AI 技术，它通过将外部知识库与大语言模型相结合，显著提升了 AI 系统的准确性和可信度。

## 核心概念

RAG 的核心价值在于解决知识更新和引用可信问题。传统的大语言模型存在知识截止日期的限制，而 RAG 通过外部知识库检索，可以获取最新信息。这种架构使得 AI 系统能够访问实时数据，并提供可追溯的信息来源。

## 工作原理

RAG 系统的工作流程包含以下几个关键步骤：

1. 用户提出问题或查询请求
2. 系统从预先构建的知识库中检索相关文档片段
3. 将检索到的上下文信息与用户问题一起输入大语言模型
4. 模型基于检索到的真实内容生成准确的答案
5. 系统返回答案并附带信息来源引用

这种方法确保了生成内容的准确性和可验证性。

## 技术优势

RAG 技术相比传统 LLM 具有多个显著优势：

- 知识可更新：无需重新训练模型即可更新知识库
- 答案可溯源：每个回答都能追溯到具体的文档来源
- 减少幻觉问题：基于真实文档生成，降低模型编造信息的风险
- 成本效益高：相比持续微调模型，维护知识库成本更低
- 领域适应性强：可以快速适配不同行业和场景

## 应用场景

RAG 技术在企业级应用中展现出强大的实用价值，特别适合需要准确性和可追溯性的场景，如客户服务、技术文档查询、法律咨询等领域。这使得 RAG 成为企业级 AI 应用的重要技术选择。"""

    print("Article content:")
    print("-" * 70)
    print(article[:200] + "...")
    print("-" * 70)
    print()

    # Check if OpenAI API key is set
    from app.core.config import get_settings
    settings = get_settings()
    if not settings.openai_api_key or settings.openai_api_key == "your-openai-api-key-here":
        print("⚠️  OpenAI API key not configured!")
        print("   Please set OPENAI_API_KEY in .env file")
        print()
        print("Skipping LLM test...")
        return

    print("Step 1: Parsing article with LLM...")
    print()

    try:
        # Step 1: Parse article
        parse_service = ArticleParseService()
        analysis = parse_service.parse_article_with_retry(article)

        print("✓ Article parsed successfully!")
        print()
        print(f"Topic: {analysis.topic}")
        print(f"Audience: {analysis.audience}")
        print(f"Core Message: {analysis.core_message}")
        print(f"Key Points: {len(analysis.key_points)} points")
        print()

        # Step 2: Generate scenes
        print("Step 2: Generating scenes with LLM...")
        print()

        scene_service = SceneGenerateService()
        scene_generation = scene_service.generate_scenes_with_retry(analysis, article)

        print("✓ Scenes generated successfully!")
        print()
        print("Scene Generation Result:")
        print("-" * 70)
        print(f"Total Scenes: {len(scene_generation.scenes)}")
        print(f"Total Duration: {scene_generation.total_duration}s")
        print(f"Narrative Flow: {scene_generation.narrative_flow}")
        print(f"Confidence: {scene_generation.confidence:.2f}")
        print()

        print("Scenes:")
        for i, scene in enumerate(scene_generation.scenes, 1):
            print(f"\n  Scene {i}:")
            print(f"    Template: {scene.template_type}")
            print(f"    Goal: {scene.goal}")
            print(f"    Duration: {scene.duration_sec}s")
            print(f"    Pace: {scene.pace}")
            print(f"    Voiceover: {scene.voiceover[:60]}...")
            print(f"    Screen Text: {', '.join(scene.screen_text)}")

        if scene_generation.reasoning:
            print()
            print(f"Reasoning: {scene_generation.reasoning}")

        print()
        print("-" * 70)
        print()
        print("✓ Test completed successfully!")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_scene_generate()

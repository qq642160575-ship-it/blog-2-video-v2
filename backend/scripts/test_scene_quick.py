#!/usr/bin/env python3
"""
Quick test for scene generation
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.scene_generate_service import SceneGenerateService
from app.schemas.article_analysis import ArticleAnalysis


def test_quick():
    print("Testing scene generation...")

    # Mock article analysis
    analysis = ArticleAnalysis(
        topic="RAG技术原理与应用",
        audience="AI技术初学者",
        core_message="RAG通过结合检索与生成技术，提升AI回答的准确性",
        key_points=[
            "RAG通过外部知识库检索补充大语言模型",
            "工作流程包括检索相关文档、结合上下文生成答案",
            "相比传统LLM，具有知识可更新、答案可溯源等优势",
            "适用于客户服务、技术文档等场景"
        ],
        tone="educational",
        complexity="beginner",
        estimated_video_duration=55,
        confidence=0.95
    )

    print(f"Article Analysis: {analysis.topic}")
    print("Generating scenes...")

    service = SceneGenerateService()
    result = service.generate_scenes(analysis)

    print(f"\n✓ Generated {len(result.scenes)} scenes")
    print(f"Total duration: {result.total_duration}s")
    print(f"Confidence: {result.confidence}")

    for i, scene in enumerate(result.scenes, 1):
        print(f"\nScene {i}: {scene.template_type} - {scene.goal}")
        print(f"  Duration: {scene.duration_sec}s, Pace: {scene.pace}")
        print(f"  Voiceover: {scene.voiceover[:50]}...")


if __name__ == "__main__":
    test_quick()

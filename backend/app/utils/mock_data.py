"""
Mock data generators for testing
"""
import json
from typing import List, Dict, Any


def generate_mock_article_analysis(project_id: str) -> Dict[str, Any]:
    """Generate mock article analysis"""
    return {
        "project_id": project_id,
        "version": 1,
        "topic": "RAG 基础概念",
        "audience": "对大模型应用有基础认知的技术读者",
        "core_message": "RAG 的核心价值在于解决知识更新和引用可信问题",
        "key_points": ["知识更新", "引用可信", "减少幻觉"],
        "tone": "educational",
        "complexity": "intermediate",
        "estimated_video_duration": 50,
        "visualizable_points": ["知识库检索", "答案生成", "引用溯源"],
        "discarded_parts": ["背景铺垫"],
        "content_type": "tutorial",
        "confidence": 0.86
    }


def generate_mock_scenes(project_id: str) -> List[Dict[str, Any]]:
    """Generate mock scene specifications"""
    return [
        {
            "scene_id": f"sc_{project_id}_001",
            "order": 1,
            "template_type": "hook_title",
            "goal": "开头钩子",
            "voiceover": "你以为 RAG 只是知识库？其实它解决的是知识更新和引用可信。",
            "screen_text": ["RAG 不只是知识库", "它解决引用可信"],
            "duration_sec": 6,
            "pace": "fast",
            "transition": "cut",
            "visual_params": {"emphasis": "RAG"}
        },
        {
            "scene_id": f"sc_{project_id}_002",
            "order": 2,
            "template_type": "bullet_explain",
            "goal": "核心概念解释",
            "voiceover": "RAG 结合了检索和生成两个步骤。先从知识库检索相关内容，再让大模型基于检索结果生成答案。",
            "screen_text": ["检索相关内容", "生成准确答案"],
            "duration_sec": 8,
            "pace": "medium",
            "transition": "fade",
            "visual_params": {"bullet_style": "animated"}
        },
        {
            "scene_id": f"sc_{project_id}_003",
            "order": 3,
            "template_type": "compare_process",
            "goal": "对比优势",
            "voiceover": "相比传统大模型，RAG 可以实时更新知识，答案可以追溯来源，大大减少了幻觉问题。",
            "screen_text": ["实时更新", "可追溯来源", "减少幻觉"],
            "duration_sec": 7,
            "pace": "medium",
            "transition": "slide",
            "visual_params": {"comparison_type": "side_by_side"}
        }
    ]


def generate_mock_render_manifest(project_id: str, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate mock render manifest"""
    return {
        "project_id": project_id,
        "resolution": "1080x1920",
        "fps": 30,
        "scenes": [
            {
                "scene_id": scene["scene_id"],
                "start_ms": sum([s["duration_sec"] * 1000 for s in scenes[:i]]),
                "end_ms": sum([s["duration_sec"] * 1000 for s in scenes[:i+1]]),
                "template_type": scene["template_type"],
                "template_props": {
                    "voiceover": scene["voiceover"],
                    "screen_text": scene["screen_text"],
                    "visual_params": scene.get("visual_params", {})
                },
                "audio_url": f"/storage/audio/{scene['scene_id']}.mp3"
            }
            for i, scene in enumerate(scenes)
        ],
        "subtitles": [],
        "total_duration_ms": sum([s["duration_sec"] * 1000 for s in scenes])
    }

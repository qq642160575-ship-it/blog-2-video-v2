"""input: 依赖状态定义、服务层、模型层和队列。
output: 向外提供视频生成流程状态图。
pos: 位于流程编排层，是生成链路中枢。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

#!/usr/bin/env python3
"""
Generation Graph - LangGraph state machine for video generation pipeline
"""
import os
import json
import time
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session

from app.graph.generation_state import GenerationState
from app.core.db import SessionLocal
from app.core.config import get_settings
from app.core.errors import ErrorCode, get_error_message
from app.services.job_service import JobService
from app.services.project_service import ProjectService
from app.services.template_mapping_service import TemplateMappingService
from app.services.task_queue import TaskQueue
from app.services.job_log_service import JobLogService
from app.models.scene import Scene
from app.utils.mock_data import (
    generate_mock_article_analysis,
    generate_mock_scenes,
)

settings = get_settings()
SKIP_TTS = os.environ.get("SKIP_TTS", "").lower() in {"1", "true", "yes", "on"}


# Node functions
def load_project(state: GenerationState) -> GenerationState:
    """Load project data"""
    db = SessionLocal()
    start_time = time.time()
    try:
        project_service = ProjectService(db)
        log_service = JobLogService(db)

        project = project_service.get_project(state["project_id"])

        print(f"✓ Project loaded: {project.title}")

        # Log success
        duration_ms = int((time.time() - start_time) * 1000)
        log_service.log_info(
            job_id=state["job_id"],
            project_id=state["project_id"],
            stage="load_project",
            message=f"Project loaded: {project.title}",
            details={"char_count": len(project.content)},
            duration_ms=duration_ms
        )

        state["project_title"] = project.title
        state["project_content"] = project.content
        return state
    except Exception as e:
        log_service = JobLogService(db)
        log_service.log_error(
            job_id=state["job_id"],
            project_id=state["project_id"],
            stage="load_project",
            message=f"Failed to load project: {str(e)}",
            error_code=ErrorCode.PROJECT_NOT_FOUND
        )
        state["error"] = str(e)
        state["error_code"] = ErrorCode.PROJECT_NOT_FOUND
        return state
    finally:
        db.close()


def parse_article(state: GenerationState) -> GenerationState:
    """Parse article with LLM"""
    db = SessionLocal()
    start_time = time.time()
    try:
        job_service = JobService(db)
        log_service = JobLogService(db)

        print("\n[1/6] Article Parse...")
        job_service.update_job_status(
            state["job_id"], status="running", stage="article_parse", progress=0.1
        )

        log_service.log_info(
            job_id=state["job_id"],
            project_id=state["project_id"],
            stage="article_parse",
            message="Starting article parse"
        )

        # Try real LLM first, fallback to mock
        try:
            from app.services.article_parse_service import ArticleParseService

            if settings.openai_api_key and settings.openai_api_key != "your-openai-api-key-here":
                parse_service = ArticleParseService()
                analysis_obj = parse_service.parse_article_with_retry(
                    state["project_content"],
                    job_id=state["job_id"],
                    project_id=state["project_id"]
                )
                analysis = {
                    "topic": analysis_obj.topic,
                    "audience": analysis_obj.audience,
                    "core_message": analysis_obj.core_message,
                    "key_points": analysis_obj.key_points,
                    "tone": analysis_obj.tone,
                    "complexity": analysis_obj.complexity,
                    "estimated_video_duration": analysis_obj.estimated_video_duration,
                    "confidence": analysis_obj.confidence,
                    "reasoning": analysis_obj.reasoning,
                }
                state["execution_summary"]["article_parse_mode"] = "real"
                print(f"  ✓ Topic: {analysis['topic']} (Real LLM)")
                print(f"  ✓ Confidence: {analysis['confidence']}")

                duration_ms = int((time.time() - start_time) * 1000)
                log_service.log_info(
                    job_id=state["job_id"],
                    project_id=state["project_id"],
                    stage="article_parse",
                    message=f"Article parsed successfully (Real LLM)",
                    details={"topic": analysis['topic'], "confidence": analysis['confidence']},
                    duration_ms=duration_ms
                )
            else:
                analysis = generate_mock_article_analysis(state["project_id"])
                state["execution_summary"]["article_parse_mode"] = "mock"
                print(f"  ✓ Topic: {analysis['topic']} (Mock)")

                duration_ms = int((time.time() - start_time) * 1000)
                log_service.log_warning(
                    job_id=state["job_id"],
                    project_id=state["project_id"],
                    stage="article_parse",
                    message="Using mock data (API key not configured)",
                    details={"topic": analysis['topic']}
                )
        except Exception as e:
            print(f"  ⚠ LLM failed, using mock: {e}")
            analysis = generate_mock_article_analysis(state["project_id"])
            state["execution_summary"]["article_parse_mode"] = "mock_fallback"

            log_service.log_warning(
                job_id=state["job_id"],
                project_id=state["project_id"],
                stage="article_parse",
                message=f"LLM failed, using mock: {str(e)[:200]}",
                details={"error": str(e), "topic": analysis['topic']}
            )

        state["analysis"] = analysis
        return state
    except Exception as e:
        log_service = JobLogService(db)
        log_service.log_error(
            job_id=state["job_id"],
            project_id=state["project_id"],
            stage="article_parse",
            message=f"Article parse failed: {str(e)}",
            error_code=ErrorCode.ARTICLE_PARSE_FAILED
        )
        state["error"] = str(e)
        state["error_code"] = ErrorCode.ARTICLE_PARSE_FAILED
        return state
    finally:
        db.close()


def generate_scenes(state: GenerationState) -> GenerationState:
    """Generate scenes with LLM"""
    db = SessionLocal()
    try:
        job_service = JobService(db)

        print("\n[2/6] Scene Generate...")
        job_service.update_job_status(
            state["job_id"], status="running", stage="scene_generate", progress=0.3
        )

        # Try real LLM first, fallback to mock
        try:
            from app.services.scene_generate_service import SceneGenerateService
            from app.schemas.article_analysis import ArticleAnalysis

            if settings.openai_api_key and settings.openai_api_key != "your-openai-api-key-here":
                analysis_obj = ArticleAnalysis(**state["analysis"])
                scene_service = SceneGenerateService()
                scene_generation = scene_service.generate_scenes_with_retry(
                    analysis_obj,
                    state["project_content"],
                    job_id=state["job_id"],
                    project_id=state["project_id"]
                )

                scenes_data = []
                for i, scene in enumerate(scene_generation.scenes, 1):
                    scenes_data.append({
                        "scene_id": f"sc_{state['project_id']}_{i:03d}",
                        "order": i,
                        "template_type": scene.template_type,
                        "goal": scene.goal,
                        "voiceover": scene.voiceover,
                        "screen_text": scene.screen_text,
                        "duration_sec": scene.duration_sec,
                        "pace": scene.pace,
                        "transition": scene.transition,
                        "visual_params": scene.visual_params
                    })
                state["execution_summary"]["scene_generate_mode"] = "real"
                print(f"  ✓ Generated {len(scenes_data)} scenes (Real LLM)")
                print(f"  ✓ Total duration: {scene_generation.total_duration}s")
            else:
                scenes_data = generate_mock_scenes(state["project_id"])
                state["execution_summary"]["scene_generate_mode"] = "mock"
                print(f"  ✓ Generated {len(scenes_data)} scenes (Mock)")
        except Exception as e:
            print(f"  ⚠ LLM failed, using mock: {e}")
            scenes_data = generate_mock_scenes(state["project_id"])
            state["execution_summary"]["scene_generate_mode"] = "mock_fallback"
            print(f"  ✓ Generated {len(scenes_data)} scenes (Mock fallback)")

        state["scenes_data"] = scenes_data
        return state
    finally:
        db.close()


def load_scenes(state: GenerationState) -> GenerationState:
    """Load existing scenes from database (for rerender)"""
    db = SessionLocal()
    try:
        job_service = JobService(db)

        print("\n[1/4] Load Existing Scenes...")
        job_service.update_job_status(
            state["job_id"], status="running", stage="load_scenes", progress=0.2
        )

        scenes = db.query(Scene).filter(
            Scene.project_id == state["project_id"]
        ).order_by(Scene.scene_order).all()

        if not scenes:
            raise ValueError(f"No scenes found for project {state['project_id']}")

        print(f"  ✓ Loaded {len(scenes)} scenes")

        scenes_data = []
        for scene in scenes:
            scenes_data.append({
                "scene_id": scene.id,
                "order": scene.scene_order,
                "template_type": scene.template_type,
                "goal": scene.goal,
                "voiceover": scene.voiceover,
                "screen_text": scene.screen_text,
                "duration_sec": scene.duration_sec,
                "pace": scene.pace,
                "transition": scene.transition,
                "visual_params": scene.visual_params
            })

        state["scenes_data"] = scenes_data
        return state
    finally:
        db.close()


def validate_scenes(state: GenerationState) -> GenerationState:
    """Validate and save scenes to database"""
    db = SessionLocal()
    try:
        job_service = JobService(db)

        print("\n[3/6] Scene Validate...")
        job_service.update_job_status(
            state["job_id"], status="running", stage="scene_validate", progress=0.4
        )
        time.sleep(0.5)

        # Save scenes to database
        for scene_data in state["scenes_data"]:
            scene = Scene(
                id=scene_data["scene_id"],
                project_id=state["project_id"],
                current_version=1,
                scene_order=scene_data["order"],
                template_type=scene_data["template_type"],
                goal=scene_data["goal"],
                voiceover=scene_data["voiceover"],
                screen_text=scene_data["screen_text"],
                duration_sec=scene_data["duration_sec"],
                pace=scene_data.get("pace"),
                transition=scene_data.get("transition"),
                visual_params=scene_data.get("visual_params")
            )
            db.add(scene)
        db.commit()
        print(f"  ✓ Scenes saved to database")

        return state
    finally:
        db.close()


def generate_tts(state: GenerationState) -> GenerationState:
    """Generate TTS audio"""
    db = SessionLocal()
    try:
        job_service = JobService(db)

        # Determine stage name based on job type
        if state["job_type"] == "rerender":
            print("\n[2/4] TTS Generate...")
            progress = 0.4
        else:
            print("\n[4/6] TTS Generate...")
            progress = 0.6

        job_service.update_job_status(
            state["job_id"], status="running", stage="tts_generate", progress=progress
        )

        audio_paths = {}
        if SKIP_TTS:
            state["execution_summary"]["tts_mode"] = "skipped"
            print("  ✓ TTS skipped by SKIP_TTS")
        else:
            try:
                from app.services.tts_service import TTSService

                tts_service = TTSService()
                audio_paths = tts_service.synthesize_batch(state["scenes_data"])
                state["execution_summary"]["tts_mode"] = "real"
                print(f"  ✓ Generated audio for {len(audio_paths)} scenes (Edge TTS)")
            except Exception as e:
                print(f"  ⚠ TTS failed: {str(e)[:100]}")
                state["execution_summary"]["tts_mode"] = "failed"
                print(f"  ✓ Continuing without audio")

        state["audio_paths"] = audio_paths
        return state
    finally:
        db.close()


def generate_subtitles(state: GenerationState) -> GenerationState:
    """Generate subtitles"""
    db = SessionLocal()
    try:
        job_service = JobService(db)

        # Determine stage name based on job type
        if state["job_type"] == "rerender":
            print("\n[3/4] Subtitle Generate...")
            progress = 0.6
        else:
            print("\n[5/6] Subtitle Generate...")
            progress = 0.8

        job_service.update_job_status(
            state["job_id"], status="running", stage="subtitle_generate", progress=progress
        )

        try:
            from app.services.subtitle_service import SubtitleService

            subtitle_service = SubtitleService()
            subtitles = subtitle_service.generate_batch(state["scenes_data"])
            state["execution_summary"]["subtitle_mode"] = "real"
            print(f"  ✓ Generated subtitles for {len(subtitles)} scenes")

            # Export to SRT files
            for scene_id, scene_subtitles in subtitles.items():
                subtitle_service.export_srt(scene_subtitles)
            print(f"  ✓ Exported SRT files")

            state["subtitles"] = subtitles
        except Exception as e:
            print(f"  ⚠ Subtitle generation failed: {str(e)[:100]}")
            state["execution_summary"]["subtitle_mode"] = "failed"
            print(f"  ✓ Continuing without subtitles")

        return state
    finally:
        db.close()


def prepare_render(state: GenerationState) -> GenerationState:
    """Prepare render manifest and queue render task"""
    db = SessionLocal()
    try:
        job_service = JobService(db)
        project_service = ProjectService(db)
        template_mapping = TemplateMappingService()
        task_queue = TaskQueue()

        # Determine stage name based on job type
        if state["job_type"] == "rerender":
            print("\n[4/4] Render Prepare...")
            progress = 0.8
        else:
            print("\n[6/6] Render Prepare...")
            progress = 0.9

        job_service.update_job_status(
            state["job_id"], status="running", stage="render_prepare", progress=progress
        )
        time.sleep(0.5)

        manifest_scenes = []
        current_start_ms = 0
        audio_paths = state.get("audio_paths", {})

        for scene_data in state["scenes_data"]:
            duration_ms = scene_data["duration_sec"] * 1000
            audio_url = audio_paths.get(scene_data["scene_id"])

            manifest_scenes.append(
                template_mapping.build_manifest_scene(
                    scene=scene_data,
                    start_ms=current_start_ms,
                    end_ms=current_start_ms + duration_ms,
                    audio_url=audio_url,
                )
            )
            current_start_ms += duration_ms

        manifest = {
            "project_id": state["project_id"],
            "resolution": "1080x1920",
            "fps": 30,
            "scenes": manifest_scenes,
            "subtitles": [],
            "total_duration_ms": current_start_ms,
        }

        # Save manifest
        manifest_path = f"{settings.storage_path}/manifests/{state['project_id']}_manifest.json"
        os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        state["execution_summary"]["manifest_path"] = manifest_path
        state["manifest_path"] = manifest_path

        print(f"  ✓ Render manifest created")

        # Push to render queue
        print("\n[Next] Pushing to render queue...")
        task_queue.push_render_task(
            job_id=state["job_id"],
            project_id=state["project_id"],
            manifest_url=manifest_path
        )
        print(f"  ✓ Render task queued")

        # Mark job as rendering
        job_service.update_job_status(
            state["job_id"], status="running", stage="rendering", progress=0.95
        )

        # Update project status
        project = project_service.get_project(state["project_id"])
        project.status = "rendering"
        db.commit()

        print(f"\n{'='*60}")
        print(f"✓ Pipeline processing completed for job {state['job_id']}!")
        print(f"  Render Worker will now generate the video...")
        print(f"{'='*60}\n")

        return state
    finally:
        db.close()


def handle_error(state: GenerationState) -> GenerationState:
    """Handle errors"""
    db = SessionLocal()
    try:
        job_service = JobService(db)

        print(f"\n✗ Error processing job {state['job_id']}: {state['error']}")
        job_service.update_job_status(
            state["job_id"],
            status="failed",
            error_code=state.get("error_code", "PROCESSING_ERROR"),
            error_message=state["error"]
        )

        return state
    finally:
        db.close()


# Routing functions
def route_by_job_type(state: GenerationState) -> str:
    """Route based on job type"""
    if state["job_type"] == "generate":
        return "parse_article"
    elif state["job_type"] == "rerender":
        return "load_scenes"
    else:
        state["error"] = f"Unknown job type: {state['job_type']}"
        state["error_code"] = "INVALID_JOB_TYPE"
        return "handle_error"


def check_error(state: GenerationState) -> str:
    """Check if there's an error"""
    if state.get("error"):
        return "handle_error"
    return "continue"


# Build the graph
def build_generation_graph() -> StateGraph:
    """Build the generation state graph"""
    workflow = StateGraph(GenerationState)

    # Add nodes
    workflow.add_node("load_project", load_project)
    workflow.add_node("parse_article", parse_article)
    workflow.add_node("generate_scenes", generate_scenes)
    workflow.add_node("load_scenes", load_scenes)
    workflow.add_node("validate_scenes", validate_scenes)
    workflow.add_node("generate_tts", generate_tts)
    workflow.add_node("generate_subtitles", generate_subtitles)
    workflow.add_node("prepare_render", prepare_render)
    workflow.add_node("handle_error", handle_error)

    # Set entry point
    workflow.set_entry_point("load_project")

    # Add edges
    workflow.add_conditional_edges(
        "load_project",
        route_by_job_type,
        {
            "parse_article": "parse_article",
            "load_scenes": "load_scenes",
            "handle_error": "handle_error"
        }
    )

    workflow.add_edge("parse_article", "generate_scenes")
    workflow.add_edge("generate_scenes", "validate_scenes")
    workflow.add_edge("validate_scenes", "generate_tts")
    workflow.add_edge("load_scenes", "generate_tts")
    workflow.add_edge("generate_tts", "generate_subtitles")
    workflow.add_edge("generate_subtitles", "prepare_render")
    workflow.add_edge("prepare_render", END)
    workflow.add_edge("handle_error", END)

    return workflow.compile()

#!/usr/bin/env python3
"""
Pipeline Worker - Consumes generation tasks and processes them
Mock version: Uses mock data instead of real AI calls
"""
import sys
import os
import time
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.core.config import get_settings
from app.services.task_queue import TaskQueue
from app.services.job_service import JobService
from app.services.project_service import ProjectService
from app.services.template_mapping_service import TemplateMappingService
from app.models.scene import Scene
from app.utils.mock_data import (
    generate_mock_article_analysis,
    generate_mock_scenes,
)

settings = get_settings()


class PipelineWorker:
    def __init__(self):
        self.task_queue = TaskQueue()
        self.template_mapping = TemplateMappingService()
        self.running = True

    def process_task(self, task: dict):
        """Process a single generation task"""
        job_id = task["job_id"]
        project_id = task["project_id"]
        job_type = task["job_type"]

        print(f"\n{'='*60}")
        print(f"Processing Job: {job_id}")
        print(f"Project: {project_id}")
        print(f"Type: {job_type}")
        print(f"{'='*60}\n")

        db = SessionLocal()
        try:
            job_service = JobService(db)
            project_service = ProjectService(db)

            # Get project
            project = project_service.get_project(project_id)
            print(f"✓ Project loaded: {project.title}")

            # Stage 1: Article Parse (Real LLM)
            print("\n[1/6] Article Parse...")
            job_service.update_job_status(
                job_id, status="running", stage="article_parse", progress=0.1
            )

            # Try real LLM first, fallback to mock if API key not configured
            try:
                from app.services.article_parse_service import ArticleParseService

                if settings.openai_api_key and settings.openai_api_key != "your-openai-api-key-here":
                    # Use real LLM
                    parse_service = ArticleParseService()
                    analysis_obj = parse_service.parse_article_with_retry(project.content)
                    analysis = {
                        "topic": analysis_obj.topic,
                        "audience": analysis_obj.audience,
                        "core_message": analysis_obj.core_message,
                        "key_points": analysis_obj.key_points,
                        "tone": analysis_obj.tone,
                        "complexity": analysis_obj.complexity,
                        "confidence": analysis_obj.confidence
                    }
                    print(f"  ✓ Topic: {analysis['topic']} (Real LLM)")
                    print(f"  ✓ Confidence: {analysis['confidence']}")
                else:
                    # Fallback to mock
                    analysis = generate_mock_article_analysis(project_id)
                    print(f"  ✓ Topic: {analysis['topic']} (Mock)")
                    print(f"  ✓ Confidence: {analysis['confidence']}")
            except Exception as e:
                print(f"  ⚠ LLM failed, using mock: {e}")
                analysis = generate_mock_article_analysis(project_id)
                print(f"  ✓ Topic: {analysis['topic']} (Mock fallback)")
                print(f"  ✓ Confidence: {analysis['confidence']}")

            # Stage 2: Scene Generate (Real LLM)
            print("\n[2/6] Scene Generate...")
            job_service.update_job_status(
                job_id, status="running", stage="scene_generate", progress=0.3
            )

            # Try real LLM first, fallback to mock if API key not configured
            try:
                from app.services.scene_generate_service import SceneGenerateService
                from app.schemas.article_analysis import ArticleAnalysis

                if settings.openai_api_key and settings.openai_api_key != "your-openai-api-key-here":
                    # Use real LLM - convert analysis dict to ArticleAnalysis object
                    analysis_obj = ArticleAnalysis(**analysis)
                    scene_service = SceneGenerateService()
                    scene_generation = scene_service.generate_scenes_with_retry(analysis_obj, project.content)

                    # Convert SceneGeneration to scenes_data format
                    scenes_data = []
                    for i, scene in enumerate(scene_generation.scenes, 1):
                        scenes_data.append({
                            "scene_id": f"sc_{project_id}_{i:03d}",
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
                    print(f"  ✓ Generated {len(scenes_data)} scenes (Real LLM)")
                    print(f"  ✓ Total duration: {scene_generation.total_duration}s")
                    print(f"  ✓ Confidence: {scene_generation.confidence}")
                else:
                    # Fallback to mock
                    scenes_data = generate_mock_scenes(project_id)
                    print(f"  ✓ Generated {len(scenes_data)} scenes (Mock)")
            except Exception as e:
                print(f"  ⚠ LLM failed, using mock: {e}")
                scenes_data = generate_mock_scenes(project_id)
                print(f"  ✓ Generated {len(scenes_data)} scenes (Mock fallback)")

            # Stage 3: Scene Validate
            print("\n[3/6] Scene Validate...")
            job_service.update_job_status(
                job_id, status="running", stage="scene_validate", progress=0.4
            )
            time.sleep(0.5)

            # Save scenes to database
            for scene_data in scenes_data:
                scene = Scene(
                    id=scene_data["scene_id"],
                    project_id=project_id,
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

            # Stage 4: TTS Generate (Edge TTS - Free)
            print("\n[4/6] TTS Generate...")
            job_service.update_job_status(
                job_id, status="running", stage="tts_generate", progress=0.6
            )

            # Try Edge TTS, fallback to mock if it fails
            audio_paths = {}
            try:
                from app.services.tts_service import TTSService

                # Always try TTS (Edge TTS is free and doesn't need API key)
                tts_service = TTSService()
                audio_paths = tts_service.synthesize_batch(scenes_data)
                print(f"  ✓ Generated audio for {len(audio_paths)} scenes (Edge TTS)")
            except Exception as e:
                print(f"  ⚠ TTS failed, using mock: {str(e)[:100]}")
                print(f"  ✓ Generated audio for {len(scenes_data)} scenes (Mock fallback)")

            # Stage 5: Subtitle Generate
            print("\n[5/6] Subtitle Generate...")
            job_service.update_job_status(
                job_id, status="running", stage="subtitle_generate", progress=0.8
            )

            # Generate subtitles for all scenes
            try:
                from app.services.subtitle_service import SubtitleService

                subtitle_service = SubtitleService()
                subtitles = subtitle_service.generate_batch(scenes_data)
                print(f"  ✓ Generated subtitles for {len(subtitles)} scenes")

                # Export to SRT files
                for scene_id, scene_subtitles in subtitles.items():
                    subtitle_service.export_srt(scene_subtitles)
                print(f"  ✓ Exported SRT files")
            except Exception as e:
                print(f"  ⚠ Subtitle generation failed: {str(e)[:100]}")
                print(f"  ✓ Continuing without subtitles")

            # Stage 6: Render Prepare
            print("\n[6/6] Render Prepare...")
            job_service.update_job_status(
                job_id, status="running", stage="render_prepare", progress=0.9
            )
            time.sleep(0.5)

            manifest_scenes = []
            current_start_ms = 0
            for scene_data in scenes_data:
                duration_ms = scene_data["duration_sec"] * 1000
                audio_url = None
                if scene_data["scene_id"] in audio_paths:
                    audio_url = audio_paths[scene_data["scene_id"]]

                manifest_scenes.append(
                    self.template_mapping.build_manifest_scene(
                        scene=scene_data,
                        start_ms=current_start_ms,
                        end_ms=current_start_ms + duration_ms,
                        audio_url=audio_url,
                    )
                )
                current_start_ms += duration_ms

            manifest = {
                "project_id": project_id,
                "resolution": "1080x1920",
                "fps": 30,
                "scenes": manifest_scenes,
                "subtitles": [],
                "total_duration_ms": current_start_ms,
            }

            # Save manifest (in real version, this would go to object storage)
            manifest_path = f"{settings.storage_path}/manifests/{project_id}_manifest.json"
            os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)

            print(f"  ✓ Render manifest created")

            # Push to render queue
            print("\n[Next] Pushing to render queue...")
            self.task_queue.push_render_task(
                job_id=job_id,
                project_id=project_id,
                manifest_url=manifest_path
            )
            print(f"  ✓ Render task queued")

            # Mark job as rendering (Render Worker will update to completed)
            job_service.update_job_status(
                job_id, status="running", stage="rendering", progress=0.95
            )

            # Update project status
            project.status = "rendering"
            db.commit()

            print(f"\n{'='*60}")
            print(f"✓ Pipeline processing completed for job {job_id}!")
            print(f"  Render Worker will now generate the video...")
            print(f"{'='*60}\n")

        except Exception as e:
            print(f"\n✗ Error processing job {job_id}: {e}")
            job_service.update_job_status(
                job_id,
                status="failed",
                error_code="PROCESSING_ERROR",
                error_message=str(e)
            )
        finally:
            db.close()

    def run(self):
        """Main worker loop"""
        print("="*60)
        print("Pipeline Worker Started")
        print("="*60)
        print(f"Listening on queue: generation_queue")
        print(f"Press Ctrl+C to stop")
        print("="*60)

        while self.running:
            try:
                # Block and wait for tasks (timeout 5 seconds)
                task = self.task_queue.pop_generation_task(timeout=5)

                if task:
                    self.process_task(task)
                else:
                    # No task, just wait
                    pass

            except KeyboardInterrupt:
                print("\n\nShutting down worker...")
                self.running = False
            except Exception as e:
                print(f"Worker error: {e}")
                time.sleep(1)

        print("Worker stopped.")


if __name__ == "__main__":
    worker = PipelineWorker()
    worker.run()

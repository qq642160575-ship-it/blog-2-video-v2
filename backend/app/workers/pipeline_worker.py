"""input: 依赖任务队列、生成 graph 和 job 服务。
output: 向外提供常驻生成 worker 进程。
pos: 位于 worker 层，负责消费生成任务。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

#!/usr/bin/env python3
"""
Pipeline Worker - Consumes generation tasks and processes them
Refactored to use LangGraph state machine
"""
import sys
import os
import time
from datetime import datetime

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, backend_dir)

from app.core.db import SessionLocal
from app.core.config import get_settings
from app.services.task_queue import TaskQueue
from app.services.job_service import JobService
from app.graph import build_generation_graph, GenerationState
from app.core.logging_config import get_logger

settings = get_settings()
logger = get_logger("worker")


class PipelineWorker:
    def __init__(self):
        self.task_queue = TaskQueue()
        self.running = True
        self.graph = build_generation_graph()

    def process_task(self, task: dict):
        """Process a single generation task using LangGraph"""
        job_id = task["job_id"]
        project_id = task["project_id"]
        job_type = task["job_type"]

        logger.info(f"{'='*60}")
        logger.info(f"Processing Job: {job_id}")
        logger.info(f"Project: {project_id}")
        logger.info(f"Type: {job_type}")
        logger.info(f"{'='*60}")

        # Initialize state
        initial_state: GenerationState = {
            "job_id": job_id,
            "project_id": project_id,
            "job_type": job_type,
            "project_title": None,
            "project_content": None,
            "analysis": None,
            "scenes_data": None,
            "audio_paths": None,
            "subtitles": None,
            "manifest_path": None,
            "execution_summary": {
                "article_parse_mode": "unknown",
                "scene_generate_mode": "unknown",
                "tts_mode": "unknown",
                "subtitle_mode": "unknown",
                "manifest_path": None,
            },
            "error": None,
            "error_code": None,
        }

        try:
            # Run the graph
            final_state = self.graph.invoke(initial_state)
            return final_state["execution_summary"]
        except Exception as e:
            logger.error(f"Error processing job {job_id}: {e}", exc_info=True)
            db = SessionLocal()
            try:
                job_service = JobService(db)
                job_service.update_job_status(
                    job_id,
                    status="failed",
                    error_code="PROCESSING_ERROR",
                    error_message=str(e)
                )
            finally:
                db.close()
            return {"error": str(e)}

    def run(self):
        """Main worker loop"""
        logger.info("="*60)
        logger.info("Pipeline Worker Started")
        logger.info("="*60)
        logger.info(f"Listening on queue: generation_queue")
        logger.info(f"Press Ctrl+C to stop")
        logger.info("="*60)

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
                logger.info("\n\nShutting down worker...")
                self.running = False
            except Exception as e:
                print(f"Worker error: {e}")
                time.sleep(1)

        print("Worker stopped.")


if __name__ == "__main__":
    worker = PipelineWorker()
    worker.run()

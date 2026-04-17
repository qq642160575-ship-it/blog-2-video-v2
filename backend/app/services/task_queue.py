import json
from typing import Dict, Any, Optional
from app.core.redis import get_redis

# Queue names
GENERATION_QUEUE = "generation_queue"
RENDER_QUEUE = "render_queue"


class TaskQueue:
    def __init__(self):
        self.redis = get_redis()

    def push_generation_task(self, job_id: str, project_id: str, job_type: str) -> None:
        """Push a generation task to the queue"""
        task_data = {
            "job_id": job_id,
            "project_id": project_id,
            "job_type": job_type
        }
        self.redis.lpush(GENERATION_QUEUE, json.dumps(task_data))

    def pop_generation_task(self, timeout: int = 0) -> Optional[Dict[str, Any]]:
        """Pop a generation task from the queue (blocking)"""
        result = self.redis.brpop(GENERATION_QUEUE, timeout=timeout)
        if result:
            _, task_json = result
            return json.loads(task_json)
        return None

    def push_render_task(self, job_id: str, project_id: str, manifest_url: str) -> None:
        """Push a render task to the queue"""
        task_data = {
            "job_id": job_id,
            "project_id": project_id,
            "manifest_url": manifest_url
        }
        self.redis.lpush(RENDER_QUEUE, json.dumps(task_data))

    def pop_render_task(self, timeout: int = 0) -> Optional[Dict[str, Any]]:
        """Pop a render task from the queue (blocking)"""
        result = self.redis.brpop(RENDER_QUEUE, timeout=timeout)
        if result:
            _, task_json = result
            return json.loads(task_json)
        return None

    def get_queue_length(self, queue_name: str) -> int:
        """Get the length of a queue"""
        return self.redis.llen(queue_name)

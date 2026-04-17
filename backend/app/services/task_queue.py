"""input: 依赖 Redis 和队列键规则。
output: 向外提供生成队列与渲染队列操作能力。
pos: 位于 service 层，负责异步任务排队。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

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

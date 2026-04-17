"""input: 依赖数据库、队列或锁相关能力。
output: 向外提供任务并发控制能力。
pos: 位于 service 层，负责并发治理。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

"""
Concurrency Manager - Manages concurrent job execution limits
"""
import redis
from typing import Optional
from app.core.config import get_settings

settings = get_settings()


class ConcurrencyManager:
    """Manages concurrency limits for job execution"""

    def __init__(self):
        # Parse redis_url to get host and port
        redis_url = settings.redis_url
        if redis_url.startswith("redis://"):
            redis_url = redis_url[8:]  # Remove redis:// prefix

        # Remove database suffix if present (e.g., /0)
        if "/" in redis_url:
            redis_url = redis_url.split("/")[0]

        # Split host:port
        if ":" in redis_url:
            host, port = redis_url.split(":")
            port = int(port)
        else:
            host = redis_url
            port = 6379

        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=0,
            decode_responses=True
        )
        self.max_concurrent_renders = 3
        self.render_lock_key = "concurrent_renders"
        self.project_lock_prefix = "project_lock:"

    def can_start_render(self) -> bool:
        """Check if a new render job can start"""
        current_count = self.get_concurrent_render_count()
        return current_count < self.max_concurrent_renders

    def acquire_render_slot(self, job_id: str) -> bool:
        """Acquire a render slot for a job"""
        if not self.can_start_render():
            return False

        # Add job to the set of running renders
        self.redis_client.sadd(self.render_lock_key, job_id)
        return True

    def release_render_slot(self, job_id: str):
        """Release a render slot"""
        self.redis_client.srem(self.render_lock_key, job_id)

    def get_concurrent_render_count(self) -> int:
        """Get the current number of concurrent renders"""
        return self.redis_client.scard(self.render_lock_key)

    def get_running_renders(self) -> list:
        """Get list of currently running render job IDs"""
        return list(self.redis_client.smembers(self.render_lock_key))

    def acquire_project_lock(self, project_id: str, job_id: str, ttl: int = 3600) -> bool:
        """
        Acquire a lock for a project to prevent multiple jobs

        Args:
            project_id: The project ID
            job_id: The job ID trying to acquire the lock
            ttl: Lock time-to-live in seconds (default 1 hour)

        Returns:
            True if lock acquired, False if project is already locked
        """
        lock_key = f"{self.project_lock_prefix}{project_id}"

        # Try to set the lock with NX (only if not exists)
        acquired = self.redis_client.set(lock_key, job_id, nx=True, ex=ttl)
        return bool(acquired)

    def release_project_lock(self, project_id: str, job_id: str) -> bool:
        """
        Release a project lock (only if owned by this job)

        Args:
            project_id: The project ID
            job_id: The job ID trying to release the lock

        Returns:
            True if lock released, False if not owned by this job
        """
        lock_key = f"{self.project_lock_prefix}{project_id}"

        # Only release if the lock is owned by this job
        current_owner = self.redis_client.get(lock_key)
        if current_owner == job_id:
            self.redis_client.delete(lock_key)
            return True
        return False

    def get_project_lock_owner(self, project_id: str) -> Optional[str]:
        """Get the job ID that owns the project lock"""
        lock_key = f"{self.project_lock_prefix}{project_id}"
        return self.redis_client.get(lock_key)

    def is_project_locked(self, project_id: str) -> bool:
        """Check if a project is currently locked"""
        lock_key = f"{self.project_lock_prefix}{project_id}"
        return self.redis_client.exists(lock_key) > 0

    def force_release_project_lock(self, project_id: str):
        """Force release a project lock (admin operation)"""
        lock_key = f"{self.project_lock_prefix}{project_id}"
        self.redis_client.delete(lock_key)

    def cleanup_stale_locks(self):
        """Clean up any stale locks (called periodically)"""
        # Redis TTL handles this automatically, but we can add additional cleanup logic here
        pass

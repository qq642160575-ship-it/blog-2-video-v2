"""input: 依赖 Redis 和缓存键规则。
output: 向外提供缓存读写、键构造和失效能力。
pos: 位于 service 层，负责缓存抽象。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

"""
Cache Service - Redis-based caching layer for performance optimization
"""
import json
import redis
from typing import Optional, Any, Callable
from functools import wraps
from app.core.config import get_settings
from app.core.logging_config import get_logger

settings = get_settings()
logger = get_logger("app")


class CacheService:
    """Service for caching frequently accessed data"""

    def __init__(self):
        # Parse redis_url to get host and port
        redis_url = settings.redis_url
        if redis_url.startswith("redis://"):
            redis_url = redis_url[8:]

        # Remove database suffix if present
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
            db=1,  # Use db 1 for cache (db 0 for queues/locks)
            decode_responses=True
        )

        # Default TTL values (in seconds)
        self.DEFAULT_TTL = 300  # 5 minutes
        self.SHORT_TTL = 60  # 1 minute
        self.LONG_TTL = 3600  # 1 hour

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)
            logger.debug(f"Cache miss: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        try:
            ttl = ttl or self.DEFAULT_TTL
            serialized = json.dumps(value)
            self.redis_client.setex(key, ttl, serialized)
            logger.debug(f"Cache set: {key} (ttl: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            self.redis_client.delete(key)
            logger.debug(f"Cache delete: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                count = self.redis_client.delete(*keys)
                logger.info(f"Cache delete pattern: {pattern} ({count} keys deleted)")
                return count
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error for {pattern}: {e}")
            return 0

    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False

    def get_ttl(self, key: str) -> int:
        """Get remaining TTL for key"""
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Cache get_ttl error for key {key}: {e}")
            return -1

    def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter"""
        try:
            result = self.redis_client.incrby(key, amount)
            logger.debug(f"Cache increment: {key} by {amount} = {result}")
            return result
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return 0

    def clear_all(self) -> bool:
        """Clear all cache (use with caution!)"""
        try:
            self.redis_client.flushdb()
            logger.warning("Cache cleared all keys in database")
            return True
        except Exception as e:
            logger.error(f"Cache clear_all error: {e}")
            return False


# Cache key generators
class CacheKeys:
    """Cache key generators for different entities"""

    @staticmethod
    def project(project_id: str) -> str:
        return f"project:{project_id}"

    @staticmethod
    def project_list(page: int = 1, limit: int = 10) -> str:
        return f"projects:list:page:{page}:limit:{limit}"

    @staticmethod
    def job(job_id: str) -> str:
        return f"job:{job_id}"

    @staticmethod
    def job_status(job_id: str) -> str:
        return f"job:{job_id}:status"

    @staticmethod
    def project_jobs(project_id: str) -> str:
        return f"project:{project_id}:jobs"

    @staticmethod
    def project_assets(project_id: str, asset_type: Optional[str] = None) -> str:
        if asset_type:
            return f"project:{project_id}:assets:{asset_type}"
        return f"project:{project_id}:assets"

    @staticmethod
    def job_assets(job_id: str, asset_type: Optional[str] = None) -> str:
        if asset_type:
            return f"job:{job_id}:assets:{asset_type}"
        return f"job:{job_id}:assets"

    @staticmethod
    def storage_stats() -> str:
        return "storage:stats"

    @staticmethod
    def concurrency_stats() -> str:
        return "concurrency:stats"


# Cache decorator
def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator to cache function results

    Usage:
        @cached(ttl=300, key_prefix="my_function")
        def my_function(arg1, arg2):
            return expensive_operation(arg1, arg2)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = CacheService()

            # Generate cache key from function name and arguments
            key_parts = [key_prefix or func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)

            return result

        return wrapper
    return decorator


# Cache invalidation helpers
class CacheInvalidator:
    """Helper class for cache invalidation"""

    def __init__(self):
        self.cache = CacheService()

    def invalidate_project(self, project_id: str):
        """Invalidate all cache related to a project"""
        patterns = [
            CacheKeys.project(project_id),
            f"project:{project_id}:*",
            "projects:list:*"  # Invalidate project lists
        ]
        for pattern in patterns:
            self.cache.delete_pattern(pattern)

    def invalidate_job(self, job_id: str, project_id: Optional[str] = None):
        """Invalidate all cache related to a job"""
        patterns = [
            CacheKeys.job(job_id),
            CacheKeys.job_status(job_id),
            f"job:{job_id}:*"
        ]

        if project_id:
            patterns.append(CacheKeys.project_jobs(project_id))

        for pattern in patterns:
            self.cache.delete_pattern(pattern)

    def invalidate_assets(self, project_id: Optional[str] = None, job_id: Optional[str] = None):
        """Invalidate asset cache"""
        patterns = []

        if project_id:
            patterns.append(f"project:{project_id}:assets*")

        if job_id:
            patterns.append(f"job:{job_id}:assets*")

        patterns.append(CacheKeys.storage_stats())

        for pattern in patterns:
            self.cache.delete_pattern(pattern)

    def invalidate_stats(self):
        """Invalidate statistics cache"""
        patterns = [
            CacheKeys.storage_stats(),
            CacheKeys.concurrency_stats()
        ]
        for pattern in patterns:
            self.cache.delete(pattern)

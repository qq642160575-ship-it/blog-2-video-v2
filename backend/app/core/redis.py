"""input: 依赖 Redis 配置和 redis 客户端。
output: 向外提供 Redis 连接与基础访问能力。
pos: 位于基础设施层，负责队列和缓存底座。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

import redis
from app.core.config import get_settings

settings = get_settings()

redis_client = redis.from_url(settings.redis_url, decode_responses=True)


def get_redis():
    return redis_client

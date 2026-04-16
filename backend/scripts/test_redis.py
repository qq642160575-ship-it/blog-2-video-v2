#!/usr/bin/env python3
"""
Test Redis and Task Queue
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.redis import redis_client
from app.services.task_queue import TaskQueue


def test_redis_connection():
    """Test Redis connection"""
    print("Testing Redis connection...")
    try:
        redis_client.ping()
        print("✓ Redis connection successful")
        return True
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        return False


def test_task_queue():
    """Test task queue operations"""
    print("\nTesting task queue...")

    queue = TaskQueue()

    # Test push
    print("  - Pushing test task...")
    queue.push_generation_task("test_job_001", "test_proj_001", "generate")

    # Test queue length
    length = queue.get_queue_length("generation_queue")
    print(f"  - Queue length: {length}")

    # Test pop
    print("  - Popping task...")
    task = queue.pop_generation_task(timeout=1)

    if task:
        print(f"  - Task received: {task}")
        print("✓ Task queue working")
        return True
    else:
        print("✗ Failed to pop task")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("Redis and Task Queue Test")
    print("=" * 50)
    print()

    redis_ok = test_redis_connection()

    if redis_ok:
        queue_ok = test_task_queue()
    else:
        print("\nSkipping queue test (Redis not available)")
        queue_ok = False

    print("\n" + "=" * 50)
    if redis_ok and queue_ok:
        print("✓ All tests passed")
    else:
        print("✗ Some tests failed")
    print("=" * 50)

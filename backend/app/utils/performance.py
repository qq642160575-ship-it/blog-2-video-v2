"""
Performance Monitoring Utilities
"""
import time
import functools
from typing import Callable, Any
from contextlib import contextmanager


class PerformanceMonitor:
    """Monitor and log performance metrics"""

    def __init__(self):
        self.metrics = {}

    def record_metric(self, name: str, value: float, unit: str = "ms"):
        """Record a performance metric"""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append({"value": value, "unit": unit, "timestamp": time.time()})

    def get_metrics(self, name: str = None):
        """Get recorded metrics"""
        if name:
            return self.metrics.get(name, [])
        return self.metrics

    def get_average(self, name: str) -> float:
        """Get average value for a metric"""
        metrics = self.metrics.get(name, [])
        if not metrics:
            return 0.0
        return sum(m["value"] for m in metrics) / len(metrics)

    def clear_metrics(self, name: str = None):
        """Clear metrics"""
        if name:
            self.metrics.pop(name, None)
        else:
            self.metrics.clear()


# Global performance monitor instance
perf_monitor = PerformanceMonitor()


def measure_time(metric_name: str = None):
    """
    Decorator to measure function execution time

    Usage:
        @measure_time("my_function")
        def my_function():
            # do something
            pass
    """
    def decorator(func: Callable) -> Callable:
        name = metric_name or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed_ms = (time.time() - start_time) * 1000
                perf_monitor.record_metric(name, elapsed_ms, "ms")
                print(f"⏱ {name}: {elapsed_ms:.2f}ms")

        return wrapper
    return decorator


@contextmanager
def timer(name: str):
    """
    Context manager to measure execution time

    Usage:
        with timer("database_query"):
            # do something
            pass
    """
    start_time = time.time()
    try:
        yield
    finally:
        elapsed_ms = (time.time() - start_time) * 1000
        perf_monitor.record_metric(name, elapsed_ms, "ms")
        print(f"⏱ {name}: {elapsed_ms:.2f}ms")


class QueryCounter:
    """Count database queries"""

    def __init__(self):
        self.count = 0
        self.queries = []

    def increment(self, query: str = ""):
        """Increment query count"""
        self.count += 1
        if query:
            self.queries.append(query)

    def reset(self):
        """Reset counter"""
        self.count = 0
        self.queries.clear()

    def get_count(self) -> int:
        """Get query count"""
        return self.count

    def get_queries(self) -> list:
        """Get list of queries"""
        return self.queries


# Global query counter
query_counter = QueryCounter()


def log_slow_query(threshold_ms: float = 100):
    """
    Decorator to log slow queries

    Usage:
        @log_slow_query(threshold_ms=100)
        def my_query():
            # execute query
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed_ms = (time.time() - start_time) * 1000

            if elapsed_ms > threshold_ms:
                print(f"⚠ Slow query detected: {func.__name__} took {elapsed_ms:.2f}ms")

            query_counter.increment(func.__name__)
            return result

        return wrapper
    return decorator

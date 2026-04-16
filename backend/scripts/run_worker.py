#!/usr/bin/env python3
"""
Run Pipeline Worker
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.workers.pipeline_worker import PipelineWorker

if __name__ == "__main__":
    worker = PipelineWorker()
    worker.run()

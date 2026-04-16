#!/usr/bin/env python3
"""
End-to-End Integration Test
Tests the complete pipeline: Article -> Scenes -> TTS -> Subtitles -> Video
"""
import sys
import os
import time
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.models.project import Project
from app.models.generation_job import GenerationJob
from app.services.task_queue import TaskQueue


def test_e2e():
    print("=" * 70)
    print("End-to-End Integration Test")
    print("=" * 70)
    print()

    # Test article about RAG technology
    test_article = """
RAG技术：让AI回答更准确

你是否遇到过这样的情况：向AI提问，得到的答案却是错误的或过时的？这是因为传统的大语言模型只能基于训练时的知识来回答问题。

RAG（Retrieval-Augmented Generation，检索增强生成）技术应运而生。它通过结合检索和生成两种方式，显著提升了AI系统的准确性。

RAG的工作原理很简单：当用户提问时，系统首先从知识库中检索相关信息，然后将这些信息作为上下文提供给大语言模型，让模型基于最新、最准确的信息来生成答案。

这种方法解决了两个关键问题：一是知识更新问题，二是引用可信问题。企业可以将自己的文档、数据库等作为知识源，让AI基于企业自己的知识来回答问题。

RAG技术已经在客服、知识管理、智能问答等场景中得到广泛应用，成为企业AI应用的重要基础设施。
    """.strip()

    db = SessionLocal()
    try:
        # Generate unique IDs
        project_id = uuid.uuid4().hex[:32]
        job_id = uuid.uuid4().hex[:32]

        # Create project
        print("[1/6] Creating project...")
        project = Project(
            id=project_id,
            title="RAG技术介绍",
            source_type="text",
            content=test_article,
            char_count=len(test_article),
            language="zh-CN",
            status="pending"
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        print(f"  ✓ Project created: {project.id}")
        print(f"  Title: {project.title}")
        print()

        # Create job
        print("[2/6] Creating job...")
        job = GenerationJob(
            id=job_id,
            project_id=project.id,
            job_type="generate",
            status="pending"
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        print(f"  ✓ Job created: {job.id}")
        print()

        # Push to generation queue
        print("[3/6] Pushing to generation queue...")
        task_queue = TaskQueue()
        task_queue.push_generation_task(
            job_id=job.id,
            project_id=project.id,
            job_type="generate"
        )
        print(f"  ✓ Task queued")
        print()

        print("-" * 70)
        print("✓ Test setup complete!")
        print()
        print("Next steps:")
        print()
        print("1. Start Pipeline Worker (Terminal 1):")
        print("   cd backend")
        print("   source venv/bin/activate")
        print("   python scripts/run_worker.py")
        print()
        print("2. Start Render Worker (Terminal 2):")
        print("   cd render-worker")
        print("   npm start")
        print()
        print("3. Monitor progress:")
        print(f"   Project ID: {project.id}")
        print(f"   Job ID: {job.id}")
        print()
        print("4. Expected pipeline:")
        print("   [Pipeline Worker]")
        print("   - Article Parse (DeepSeek LLM)")
        print("   - Scene Generate (DeepSeek LLM)")
        print("   - Scene Validate")
        print("   - TTS Generate (Edge TTS or Mock)")
        print("   - Subtitle Generate")
        print("   - Render Prepare")
        print()
        print("   [Render Worker]")
        print("   - Render all scenes")
        print("   - Concatenate videos")
        print("   - Export final video")
        print()
        print("5. Check output:")
        print(f"   Video: backend/storage/videos/{project.id}/{project.id}.mp4")
        print(f"   Subtitles: backend/storage/subtitles/sc_{project.id}_*.srt")
        print()
        print("-" * 70)

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_e2e()

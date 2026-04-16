#!/usr/bin/env python3
"""
End-to-End Test with Worker
Tests the complete flow: Create Project -> Create Job -> Worker Processes -> Check Result
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"


def test_e2e_with_worker():
    print("=" * 70)
    print("End-to-End Test with Pipeline Worker")
    print("=" * 70)
    print()
    print("⚠️  Make sure the Pipeline Worker is running:")
    print("   cd backend && source venv/bin/activate && python scripts/run_worker.py")
    print()
    input("Press Enter when worker is ready...")
    print()

    # Step 1: Create Project
    print("Step 1: Creating project...")
    project_data = {
        "title": "什么是 RAG",
        "source_type": "markdown",
        "content": """# 什么是 RAG

RAG（Retrieval-Augmented Generation）是一种结合了检索和生成的 AI 技术。

## 核心概念

RAG 的核心价值在于解决知识更新和引用可信问题。传统的大语言模型存在知识截止日期的限制，而 RAG 通过外部知识库检索，可以获取最新信息。

## 工作原理

1. 用户提出问题
2. 系统从知识库检索相关文档
3. 将检索结果和问题一起输入大模型
4. 模型基于检索内容生成答案

## 优势

- 知识可更新
- 答案可溯源
- 减少幻觉问题

这使得 RAG 成为企业级 AI 应用的重要技术选择。"""
    }

    response = requests.post(f"{BASE_URL}/projects", json=project_data)
    if response.status_code != 200:
        print(f"✗ Failed to create project: {response.text}")
        return

    result = response.json()
    project_id = result["project_id"]
    print(f"✓ Project created: {project_id}")
    print()

    # Step 2: Create Generation Job
    print("Step 2: Creating generation job...")
    response = requests.post(f"{BASE_URL}/projects/{project_id}/jobs/generate")
    if response.status_code != 200:
        print(f"✗ Failed to create job: {response.text}")
        return

    result = response.json()
    job_id = result["job_id"]
    print(f"✓ Job created: {job_id}")
    print(f"  Initial status: {result['status']}")
    print()

    # Step 3: Monitor Job Progress
    print("Step 3: Monitoring job progress...")
    print("  (Worker should pick up the task and process it)")
    print()

    max_polls = 30
    poll_interval = 2

    for i in range(max_polls):
        response = requests.get(f"{BASE_URL}/jobs/{job_id}")
        if response.status_code != 200:
            print(f"✗ Failed to get job status: {response.text}")
            return

        result = response.json()
        status = result["status"]
        stage = result["stage"]
        progress = result["progress"]

        print(f"  Poll {i+1:2d}: Status={status:12s} Stage={stage or 'N/A':20s} Progress={progress:.0%}")

        if status == "completed":
            print()
            print("✓ Job completed successfully!")
            break
        elif status == "failed":
            print()
            print(f"✗ Job failed: {result.get('error')}")
            return

        time.sleep(poll_interval)
    else:
        print()
        print("⚠️  Job did not complete within timeout")
        return

    # Step 4: Check Results
    print()
    print("Step 4: Checking results...")

    # Get project
    response = requests.get(f"{BASE_URL}/projects/{project_id}")
    if response.status_code == 200:
        project = response.json()
        print(f"  ✓ Project status: {project['status']}")

    # Get scenes
    response = requests.get(f"{BASE_URL}/projects/{project_id}/scenes")
    if response.status_code == 200:
        scenes = response.json()
        print(f"  ✓ Scenes generated: {len(scenes)}")
        for scene in scenes:
            print(f"    - Scene {scene['scene_order']}: {scene['template_type']}")
    else:
        print(f"  Note: Scenes endpoint not yet implemented")

    print()
    print("=" * 70)
    print("✓ End-to-End Test Completed!")
    print("=" * 70)
    print()
    print("Summary:")
    print(f"  - Project ID: {project_id}")
    print(f"  - Job ID: {job_id}")
    print(f"  - Status: Completed")
    print()
    print("Next Steps:")
    print("  - Implement Remotion templates (Step 8)")
    print("  - Implement Render Worker (Step 9)")
    print("  - Complete end-to-end video generation (Step 10)")


if __name__ == "__main__":
    try:
        test_e2e_with_worker()
    except requests.exceptions.ConnectionError:
        print("✗ Error: Cannot connect to API server")
        print("  Please start the server: uvicorn app.main:app --reload")
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

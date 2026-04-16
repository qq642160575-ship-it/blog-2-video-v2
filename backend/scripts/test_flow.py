#!/usr/bin/env python3
"""
Comprehensive API test for Steps 3-6
Tests: Create Project -> Create Job -> Query Job Status
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"


def test_full_flow():
    print("=" * 60)
    print("Testing Full API Flow (Steps 3-6)")
    print("=" * 60)
    print()

    # Step 3: Create Project
    print("Step 3: Testing POST /projects...")
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
    print(f"  Status: {response.status_code}")

    if response.status_code != 200:
        print(f"  ✗ Failed: {response.text}")
        return

    result = response.json()
    project_id = result["project_id"]
    print(f"  ✓ Project created: {project_id}")
    print(f"  Char count: {result['article_stats']['char_count']}")
    print()

    # Step 5: Create Generation Job
    print("Step 5: Testing POST /projects/{project_id}/jobs/generate...")
    response = requests.post(f"{BASE_URL}/projects/{project_id}/jobs/generate")
    print(f"  Status: {response.status_code}")

    if response.status_code != 200:
        print(f"  ✗ Failed: {response.text}")
        return

    result = response.json()
    job_id = result["job_id"]
    print(f"  ✓ Job created: {job_id}")
    print(f"  Initial status: {result['status']}")
    print()

    # Step 6: Query Job Status
    print("Step 6: Testing GET /jobs/{job_id}...")
    for i in range(3):
        response = requests.get(f"{BASE_URL}/jobs/{job_id}")
        print(f"  Poll {i+1} - Status: {response.status_code}")

        if response.status_code != 200:
            print(f"  ✗ Failed: {response.text}")
            return

        result = response.json()
        print(f"    Job status: {result['status']}")
        print(f"    Stage: {result['stage']}")
        print(f"    Progress: {result['progress']}")

        if i < 2:
            time.sleep(1)

    print()
    print("  ✓ Job status query working")
    print()

    print("=" * 60)
    print("✓ All API tests passed (Steps 3-6)")
    print("=" * 60)
    print()
    print("Summary:")
    print(f"  - Project ID: {project_id}")
    print(f"  - Job ID: {job_id}")
    print()
    print("Next: Implement Pipeline Worker (Step 7)")


if __name__ == "__main__":
    try:
        test_full_flow()
    except requests.exceptions.ConnectionError:
        print("✗ Error: Cannot connect to API server")
        print("  Please start the server: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"✗ Error: {e}")

#!/usr/bin/env python3
"""
End-to-End Test - Complete Mock Flow (Milestone 1)
Tests: Create Project -> Generate Job -> Pipeline Worker -> Render Worker -> Get Result
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"


def test_complete_flow():
    print("=" * 70)
    print("End-to-End Test - Complete Mock Flow (Milestone 1)")
    print("=" * 70)
    print()
    print("⚠️  Make sure the following are running:")
    print("   1. API Server: cd backend && uvicorn app.main:app --reload")
    print("   2. Pipeline Worker: cd backend && python scripts/run_worker.py")
    print("   3. Render Worker: cd render-worker && npm start")
    print()
    input("Press Enter when all services are ready...")
    print()

    # Step 1: Create Project
    print("Step 1: Creating project...")
    project_data = {
        "title": "什么是 RAG",
        "source_type": "markdown",
        "content": """# 什么是 RAG

RAG（Retrieval-Augmented Generation）是一种结合了检索和生成的 AI 技术，它通过将外部知识库与大语言模型相结合，显著提升了 AI 系统的准确性和可信度。

## 核心概念

RAG 的核心价值在于解决知识更新和引用可信问题。传统的大语言模型存在知识截止日期的限制，而 RAG 通过外部知识库检索，可以获取最新信息。这种架构使得 AI 系统能够访问实时数据，并提供可追溯的信息来源。

## 工作原理

RAG 系统的工作流程包含以下几个关键步骤：

1. 用户提出问题或查询请求
2. 系统从预先构建的知识库中检索相关文档片段
3. 将检索到的上下文信息与用户问题一起输入大语言模型
4. 模型基于检索到的真实内容生成准确的答案
5. 系统返回答案并附带信息来源引用

这种方法确保了生成内容的准确性和可验证性。

## 技术优势

RAG 技术相比传统 LLM 具有多个显著优势：

- 知识可更新：无需重新训练模型即可更新知识库
- 答案可溯源：每个回答都能追溯到具体的文档来源
- 减少幻觉问题：基于真实文档生成，降低模型编造信息的风险
- 成本效益高：相比持续微调模型，维护知识库成本更低
- 领域适应性强：可以快速适配不同行业和场景

## 应用场景

RAG 技术在企业级应用中展现出强大的实用价值，特别适合需要准确性和可追溯性的场景，如客户服务、技术文档查询、法律咨询等领域。这使得 RAG 成为企业级 AI 应用的重要技术选择。"""
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
    print("  (Pipeline Worker and Render Worker will process the task)")
    print()

    max_polls = 60
    poll_interval = 3

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

    # Step 4: Get Result
    print()
    print("Step 4: Getting result...")

    response = requests.get(f"{BASE_URL}/projects/{project_id}/result")
    if response.status_code == 200:
        result = response.json()
        print(f"  ✓ Project status: {result['status']}")
        print(f"  ✓ Video URL: {result.get('video_url')}")
    else:
        print(f"  ✗ Failed to get result: {response.text}")

    print()
    print("=" * 70)
    print("✓ End-to-End Test Completed!")
    print("=" * 70)
    print()
    print("🎉 Milestone 1 Achieved!")
    print()
    print("Summary:")
    print(f"  - Project ID: {project_id}")
    print(f"  - Job ID: {job_id}")
    print(f"  - Status: Completed")
    print(f"  - Video: backend{result.get('video_url', 'N/A')}")
    print()
    print("Next Steps:")
    print("  - Step 11: Integrate real LLM for article parsing")
    print("  - Step 12: Integrate real LLM for scene generation")
    print("  - Step 13: Integrate real TTS service")


if __name__ == "__main__":
    try:
        test_complete_flow()
    except requests.exceptions.ConnectionError:
        print("✗ Error: Cannot connect to API server")
        print("  Please start the server: uvicorn app.main:app --reload")
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

#!/usr/bin/env python3
"""
Test script for Project API
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_create_project():
    print("Testing POST /projects...")

    data = {
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

    response = requests.post(f"{BASE_URL}/projects", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    if response.status_code == 200:
        project_id = response.json()["project_id"]
        print(f"\n✓ Project created: {project_id}")
        return project_id
    else:
        print("\n✗ Failed to create project")
        return None


def test_get_project(project_id):
    print(f"\nTesting GET /projects/{project_id}...")

    response = requests.get(f"{BASE_URL}/projects/{project_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    if response.status_code == 200:
        print(f"\n✓ Project retrieved successfully")
    else:
        print("\n✗ Failed to get project")


if __name__ == "__main__":
    print("=" * 50)
    print("Project API Test")
    print("=" * 50)
    print()

    # Test create
    project_id = test_create_project()

    # Test get
    if project_id:
        test_get_project(project_id)

    print("\n" + "=" * 50)
    print("Test completed")
    print("=" * 50)

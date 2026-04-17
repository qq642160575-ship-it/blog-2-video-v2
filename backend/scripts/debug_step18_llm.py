#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Narrow debugging for Step 18 LLM calls.

Runs article parsing and scene generation separately with timing output,
so we can see exactly which call blocks or fails.
"""
import json
import os
import sys
import time

for proxy_key in ("ALL_PROXY", "all_proxy"):
    if os.environ.get(proxy_key, "").startswith("socks://"):
        os.environ.pop(proxy_key, None)

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.article_parse_service import ArticleParseService
from app.services.scene_generate_service import SceneGenerateService
from app.schemas.article_analysis import ArticleAnalysis


TEST_ARTICLE = """
# RAG 技术为什么能让 AI 回答更可靠

很多团队在接入大模型以后，最先遇到的问题不是模型不会回答，而是回答看起来很像对的，但其实已经过时，或者根本没有依据。

RAG，也就是检索增强生成，核心思路并不复杂。它不是让模型单独凭记忆作答，而是先去知识库里检索相关资料，再把这些资料作为上下文交给模型生成答案。

这样做直接解决了两个痛点。第一，知识可以动态更新。企业只要更新知识库，不需要重新训练整套模型。第二，回答可以带来源，用户能看到答案依据了哪些文档，这会显著提升可信度。
""".strip()


def main() -> None:
    print("=== Step 18 LLM Debug ===")
    print(f"OPENAI_BASE_URL={os.environ.get('OPENAI_BASE_URL', '')}")
    print(f"HTTP_PROXY={os.environ.get('HTTP_PROXY', '')}")
    print(f"HTTPS_PROXY={os.environ.get('HTTPS_PROXY', '')}")
    print(f"ALL_PROXY={os.environ.get('ALL_PROXY', '')}")
    print()

    print("[1/2] Article parse")
    parse_started = time.time()
    try:
        parse_service = ArticleParseService()
        analysis = parse_service.parse_article_with_retry(TEST_ARTICLE, max_retries=1)
        parse_elapsed = time.time() - parse_started
        print(f"OK in {parse_elapsed:.2f}s")
        print(json.dumps(analysis.model_dump(), ensure_ascii=False, indent=2))
    except Exception as e:
        parse_elapsed = time.time() - parse_started
        print(f"FAILED in {parse_elapsed:.2f}s")
        print(str(e))
        return

    print()
    print("[2/2] Scene generate")
    scene_started = time.time()
    try:
        scene_service = SceneGenerateService()
        scene_generation = scene_service.generate_scenes_with_retry(
            ArticleAnalysis(**analysis.model_dump()),
            TEST_ARTICLE,
            max_retries=1,
        )
        scene_elapsed = time.time() - scene_started
        print(f"OK in {scene_elapsed:.2f}s")
        print(json.dumps(scene_generation.model_dump(), ensure_ascii=False, indent=2))
    except Exception as e:
        scene_elapsed = time.time() - scene_started
        print(f"FAILED in {scene_elapsed:.2f}s")
        print(str(e))


if __name__ == "__main__":
    main()

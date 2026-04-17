#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 18 real end-to-end flow test.

Runs the real pipeline in-process:
Article -> LLM scene generation -> TTS -> subtitles -> render manifest -> Remotion render
"""
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

for proxy_key in ("ALL_PROXY", "all_proxy"):
    if os.environ.get(proxy_key, "").startswith("socks://"):
        os.environ.pop(proxy_key, None)

os.environ.setdefault("SKIP_TTS", "1")

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.models.generation_job import GenerationJob
from app.models.project import Project
from app.services.job_service import JobService
from app.workers.pipeline_worker import PipelineWorker


TEST_ARTICLE = """
# RAG 技术为什么能让 AI 回答更可靠

很多团队在接入大模型以后，最先遇到的问题不是模型不会回答，而是回答看起来很像对的，但其实已经过时，或者根本没有依据。

RAG，也就是检索增强生成，核心思路并不复杂。它不是让模型单独凭记忆作答，而是先去知识库里检索相关资料，再把这些资料作为上下文交给模型生成答案。

这样做直接解决了两个痛点。第一，知识可以动态更新。企业只要更新知识库，不需要重新训练整套模型。第二，回答可以带来源，用户能看到答案依据了哪些文档，这会显著提升可信度。

从系统结构上看，RAG 一般包括查询改写、文档检索、结果重排、上下文拼接和答案生成几个阶段。不同业务场景会在召回策略和重排模型上做优化，但底层逻辑都是先找到信息，再组织信息。

对于客服、知识助手、内部搜索、合规问答这些场景，RAG 的价值尤其明显。因为这些业务最怕的不是回答慢，而是回答错。

所以如果你想把大模型真正用于生产环境，RAG 往往不是一个可选增强，而是第一层基础设施。
""".strip()


def print_section(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def ensure_env(settings) -> None:
    missing = []
    if not settings.database_url:
        missing.append("DATABASE_URL")
    if not settings.redis_url:
        missing.append("REDIS_URL")
    if not settings.openai_api_key:
        missing.append("OPENAI_API_KEY")

    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")


def create_project_and_job():
    db = SessionLocal()
    try:
        project_id = uuid.uuid4().hex[:32]
        job_id = uuid.uuid4().hex[:32]

        project = Project(
            id=project_id,
            title="Step 18 真实流程测试",
            source_type="markdown",
            content=TEST_ARTICLE,
            char_count=len(TEST_ARTICLE),
            language="zh-CN",
            status="pending",
        )
        db.add(project)

        job = GenerationJob(
            id=job_id,
            project_id=project_id,
            job_type="generate",
            status="pending",
        )
        db.add(job)
        db.commit()

        return project_id, job_id
    finally:
        db.close()


def fetch_job_status(job_id: str):
    db = SessionLocal()
    try:
        job = JobService(db).get_job(job_id)
        return {
            "status": job.status,
            "stage": job.stage,
            "progress": float(job.progress) if job.progress is not None else 0.0,
            "video_url": job.result_video_url,
            "subtitle_url": job.result_subtitle_url,
        }
    finally:
        db.close()


def run_pipeline(job_id: str, project_id: str) -> None:
    worker = PipelineWorker()
    return worker.process_task(
        {
            "job_id": job_id,
            "project_id": project_id,
            "job_type": "generate",
        }
    )


def run_render_worker(project_root: Path) -> None:
    render_worker_dir = project_root / "render-worker"
    result = subprocess.run(
        ["node", "index.js", "--once"],
        cwd=str(render_worker_dir),
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Render worker exited with code {result.returncode}")


def collect_outputs(project_root: Path, project_id: str) -> dict:
    storage_dir = project_root / "backend" / "storage"
    manifest_path = storage_dir / "manifests" / f"{project_id}_manifest.json"
    video_path = storage_dir / "videos" / project_id / f"{project_id}.mp4"
    audio_dir = storage_dir / "audio"
    subtitle_dir = storage_dir / "subtitles"

    if not manifest_path.exists():
        raise RuntimeError(f"Manifest not found: {manifest_path}")
    if not video_path.exists():
        raise RuntimeError(f"Video not found: {video_path}")

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    scene_ids = [scene["scene_id"] for scene in manifest["scenes"]]
    audio_files = [audio_dir / f"{scene_id}.mp3" for scene_id in scene_ids]
    subtitle_files = [subtitle_dir / f"{scene_id}.srt" for scene_id in scene_ids]

    missing_audio = [str(path) for path in audio_files if not path.exists()]
    missing_subtitles = [str(path) for path in subtitle_files if not path.exists()]

    return {
        "manifest_path": str(manifest_path),
        "video_path": str(video_path),
        "video_url": f"/storage/videos/{project_id}/{project_id}.mp4",
        "scene_count": len(scene_ids),
        "audio_files": [str(path) for path in audio_files if path.exists()],
        "subtitle_files": [str(path) for path in subtitle_files if path.exists()],
        "missing_audio": missing_audio,
        "missing_subtitles": missing_subtitles,
    }


def finalize_job_and_project(job_id: str, project_id: str, outputs: dict) -> None:
    db = SessionLocal()
    try:
        job_service = JobService(db)
        job_service.update_job_status(
            job_id=job_id,
            status="completed",
            stage="export",
            progress=1.0,
        )
        job_service.update_job_result(
            job_id=job_id,
            video_url=outputs["video_url"],
        )

        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.status = "completed"
            project.latest_job_id = job_id
            db.commit()
    finally:
        db.close()


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    settings = get_settings()

    print_section("Step 18 Real Flow Test")
    ensure_env(settings)

    print("Storage path:", settings.storage_path)
    print("OpenAI base URL:", settings.openai_base_url)
    print("Skip TTS:", os.environ.get("SKIP_TTS"))

    print_section("1. Create Project And Job")
    project_id, job_id = create_project_and_job()
    print("Project ID:", project_id)
    print("Job ID:", job_id)

    print_section("2. Run Pipeline Worker In Process")
    pipeline_summary = run_pipeline(job_id, project_id)
    pipeline_status = fetch_job_status(job_id)
    print("Pipeline status:", pipeline_status)
    print("Pipeline summary:", json.dumps(pipeline_summary, ensure_ascii=False, indent=2))

    print_section("3. Run Render Worker Once")
    run_render_worker(project_root)

    print_section("4. Collect Outputs")
    outputs = collect_outputs(project_root, project_id)
    finalize_job_and_project(job_id, project_id, outputs)
    final_status = fetch_job_status(job_id)
    print(json.dumps(outputs, ensure_ascii=False, indent=2))
    print("Final job status:", final_status)

    if outputs["missing_audio"]:
        print("Warning: Missing audio files")
        for path in outputs["missing_audio"]:
            print("  -", path)

    if outputs["missing_subtitles"]:
        print("Warning: Missing subtitle files")
        for path in outputs["missing_subtitles"]:
            print("  -", path)

    print_section("Step 18 Result")
    print(f"✓ Article parse: {pipeline_summary['article_parse_mode']}")
    print(f"✓ Scene generate: {pipeline_summary['scene_generate_mode']}")
    print(f"✓ TTS: {pipeline_summary['tts_mode']}")
    print(f"✓ Subtitles: {pipeline_summary['subtitle_mode']}")
    print("✓ Video rendered")
    print("Output video:", outputs["video_path"])


if __name__ == "__main__":
    main()

"""input: 依赖 FastAPI、路由模块、静态目录和日志配置。
output: 向外提供可启动的 FastAPI app。
pos: 位于后端入口层，负责装配 HTTP 应用。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

import os
import time
import traceback
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import projects, jobs, scenes, job_logs, assets, logs, timeline, stats
from app.core.logging_config import get_logger

app = FastAPI(title="Blog to Video API", version="1.0.0")
api_logger = get_logger("api")
error_logger = get_logger("error")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for video storage
storage_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
if os.path.exists(storage_path):
    app.mount("/storage", StaticFiles(directory=storage_path), name="storage")

# Register routers
app.include_router(projects.router)
app.include_router(jobs.router)
app.include_router(scenes.router)
app.include_router(scenes.project_router)
app.include_router(job_logs.router)
app.include_router(assets.router)
app.include_router(logs.router)
app.include_router(timeline.router)
app.include_router(stats.router)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = uuid4().hex[:12]
    start_time = time.time()
    client_host = request.client.host if request.client else "unknown"

    api_logger.info(
        f"[request_id={request_id}] started {request.method} {request.url.path} "
        f"from={client_host}"
    )

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = int((time.time() - start_time) * 1000)
        error_logger.exception(
            f"[request_id={request_id}] unhandled exception {request.method} "
            f"{request.url.path} duration_ms={duration_ms}"
        )
        raise

    duration_ms = int((time.time() - start_time) * 1000)
    response.headers["X-Request-ID"] = request_id
    api_logger.info(
        f"[request_id={request_id}] completed {request.method} {request.url.path} "
        f"status={response.status_code} duration_ms={duration_ms}"
    )
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = uuid4().hex[:12]
    error_logger.error(
        f"[request_id={request_id}] fatal error on {request.method} {request.url.path}: {exc}\n"
        f"{traceback.format_exc()}"
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": request_id,
        },
    )


@app.get("/")
def read_root():
    return {"message": "Blog to Video API", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}

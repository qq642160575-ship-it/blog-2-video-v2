from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import projects, jobs, scenes, job_logs, assets
import os

app = FastAPI(title="Blog to Video API", version="1.0.0")

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
app.include_router(job_logs.router)
app.include_router(assets.router)


@app.get("/")
def read_root():
    return {"message": "Blog to Video API", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}

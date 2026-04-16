from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import projects, jobs, scenes

app = FastAPI(title="Blog to Video API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(projects.router)
app.include_router(jobs.router)
app.include_router(scenes.router)


@app.get("/")
def read_root():
    return {"message": "Blog to Video API", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}

"""input: 依赖 FastAPI、数据库会话和 scene 相关服务。
output: 向外提供分镜查询与编辑接口。
pos: 位于 API 层，负责分镜操作入口。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.scene import Scene
from app.services.scene_service import SceneService
from app.services.preview_service import get_preview_service
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(tags=["scenes"])

# Router for project-scoped scene operations
project_router = APIRouter(prefix="/projects", tags=["scenes"])


class SceneUpdateRequest(BaseModel):
    voiceover: Optional[str] = None
    screen_text: Optional[List[str]] = None
    duration_sec: Optional[int] = None
    pace: Optional[str] = None
    transition: Optional[str] = None
    visual_params: Optional[dict] = None


@project_router.get("/{project_id}/scenes")
def get_project_scenes(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all scenes for a project
    """
    try:
        scene_service = SceneService(db)
        scenes = scene_service.get_project_scenes(project_id)

        return [
            {
                "scene_id": scene.id,
                "version": scene.current_version,
                "order": scene.scene_order,
                "template_type": scene.template_type,
                "goal": scene.goal,
                "voiceover": scene.voiceover,
                "screen_text": scene.screen_text,
                "duration_sec": scene.duration_sec,
                "pace": scene.pace,
                "transition": scene.transition,
                "visual_params": scene.visual_params
            }
            for scene in scenes
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/scenes/{scene_id}")
def get_scene(
    scene_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a single scene by ID
    """
    try:
        scene_service = SceneService(db)
        scene = scene_service.get_scene(scene_id)

        if not scene:
            raise HTTPException(status_code=404, detail=f"Scene {scene_id} not found")

        return {
            "scene_id": scene.id,
            "version": scene.current_version,
            "order": scene.scene_order,
            "template_type": scene.template_type,
            "goal": scene.goal,
            "voiceover": scene.voiceover,
            "screen_text": scene.screen_text,
            "duration_sec": scene.duration_sec,
            "pace": scene.pace,
            "transition": scene.transition,
            "visual_params": scene.visual_params
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.patch("/scenes/{scene_id}")
def update_scene(
    scene_id: str,
    updates: SceneUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update a scene and create a version history entry
    """
    try:
        scene_service = SceneService(db)

        # Convert to dict and remove None values
        update_dict = {k: v for k, v in updates.model_dump().items() if v is not None}

        if not update_dict:
            raise HTTPException(status_code=400, detail="No updates provided")

        # Update scene
        scene = scene_service.update_scene(scene_id, update_dict)

        return {
            "scene_id": scene.id,
            "version": scene.current_version,
            "order": scene.scene_order,
            "template_type": scene.template_type,
            "goal": scene.goal,
            "voiceover": scene.voiceover,
            "screen_text": scene.screen_text,
            "duration_sec": scene.duration_sec,
            "pace": scene.pace,
            "transition": scene.transition,
            "visual_params": scene.visual_params,
            "message": f"Scene updated to version {scene.current_version}"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/scenes/{scene_id}/versions")
def get_scene_versions(
    scene_id: str,
    db: Session = Depends(get_db)
):
    """
    Get version history for a scene
    """
    try:
        scene_service = SceneService(db)
        versions = scene_service.get_scene_versions(scene_id)

        return [
            {
                "version": v.version,
                "voiceover": v.voiceover,
                "screen_text": v.screen_text,
                "duration_sec": v.duration_sec,
                "created_at": v.created_at.isoformat()
            }
            for v in versions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/scenes/{scene_id}/preview")
async def preview_scene(
    scene_id: str,
    start_time: float = 0,
    end_time: Optional[float] = None,
    quality: str = "low",
    db: Session = Depends(get_db)
):
    """
    Generate preview video for a scene

    Args:
        scene_id: Scene ID
        start_time: Preview start time in seconds (default: 0)
        end_time: Preview end time in seconds (default: full scene)
        quality: Preview quality - "low" (640x360) or "medium" (854x480)

    Returns:
        Preview video URL and duration
    """
    try:
        # Get scene data
        scene_service = SceneService(db)
        scene = scene_service.get_scene(scene_id)

        if not scene:
            raise HTTPException(status_code=404, detail=f"Scene {scene_id} not found")

        # Prepare scene data
        scene_data = {
            "template_type": scene.template_type,
            "voiceover": scene.voiceover,
            "screen_text": scene.screen_text,
            "duration_sec": scene.duration_sec,
            "timeline_data": scene.timeline_data,
            "audio_url": scene.audio_url,
            "visual_params": scene.visual_params
        }

        # Generate preview
        preview_service = get_preview_service()
        preview_url = await preview_service.generate_preview(
            scene_id=scene_id,
            scene_data=scene_data,
            start_time=start_time,
            end_time=end_time,
            quality=quality
        )

        if not preview_url:
            raise HTTPException(status_code=500, detail="Failed to generate preview")

        # Calculate duration
        if end_time is None:
            end_time = scene.duration_sec
        duration = end_time - start_time

        return {
            "preview_url": preview_url,
            "duration": duration,
            "quality": quality,
            "scene_id": scene_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

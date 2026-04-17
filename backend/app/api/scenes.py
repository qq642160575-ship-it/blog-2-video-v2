from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.scene import Scene
from app.services.scene_service import SceneService
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/projects", tags=["scenes"])


class SceneUpdateRequest(BaseModel):
    voiceover: Optional[str] = None
    screen_text: Optional[List[str]] = None
    duration_sec: Optional[int] = None
    pace: Optional[str] = None
    transition: Optional[str] = None
    visual_params: Optional[dict] = None


@router.get("/{project_id}/scenes")
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

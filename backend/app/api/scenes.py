from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.scene import Scene
from typing import List

router = APIRouter(prefix="/projects", tags=["scenes"])


@router.get("/{project_id}/scenes")
def get_project_scenes(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all scenes for a project
    """
    try:
        scenes = db.query(Scene).filter(
            Scene.project_id == project_id
        ).order_by(Scene.scene_order).all()

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

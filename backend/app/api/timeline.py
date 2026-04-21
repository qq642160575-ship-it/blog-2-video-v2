"""Timeline API endpoints for visual editor
Provides APIs to update timeline data and generate preview videos
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.db import get_db
from app.models.scene import Scene
from app.services.timeline_calculate_service import TimelineCalculateService
from app.services.preview_service import get_preview_service
from app.core.logging_config import get_logger

logger = get_logger("app")
router = APIRouter(prefix="/scenes", tags=["timeline"])


class UpdateTimelineRequest(BaseModel):
    """Request body for updating timeline data"""
    emphasis_words: Optional[List[str]] = Field(
        None,
        description="Updated emphasis words (2-3 words)",
        max_items=3
    )
    timeline_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Manually adjusted timeline data"
    )


class UpdateTimelineResponse(BaseModel):
    """Response for timeline update"""
    success: bool
    scene_id: str
    updated_at: str
    timeline_data: Optional[Dict[str, Any]] = None


class PreviewRequest(BaseModel):
    """Request body for preview generation"""
    start_time: Optional[float] = Field(None, description="Preview start time in seconds")
    end_time: Optional[float] = Field(None, description="Preview end time in seconds")
    quality: Optional[str] = Field("low", description="Preview quality: low/medium")


class PreviewResponse(BaseModel):
    """Response for preview generation"""
    success: bool
    scene_id: str
    preview_url: Optional[str] = None
    duration: Optional[float] = None
    message: Optional[str] = None


@router.put("/{scene_id}/timeline", response_model=UpdateTimelineResponse)
async def update_timeline(
    scene_id: str,
    request: UpdateTimelineRequest,
    db: Session = Depends(get_db)
):
    """Update timeline data for a scene

    This endpoint allows updating emphasis_words and/or timeline_data.
    If only emphasis_words is provided, timeline will be recalculated automatically.
    If timeline_data is provided directly, it will be used as-is (manual adjustment).
    """
    # Find scene
    scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scene {scene_id} not found"
        )

    logger.info(f"Updating timeline for scene {scene_id}")

    # Case 1: Manual timeline_data provided (direct update)
    if request.timeline_data is not None:
        scene.timeline_data = request.timeline_data
        if request.emphasis_words is not None:
            scene.emphasis_words = request.emphasis_words
        db.commit()
        db.refresh(scene)

        logger.info(f"Timeline manually updated for scene {scene_id}")
        return UpdateTimelineResponse(
            success=True,
            scene_id=scene_id,
            updated_at=scene.updated_at.isoformat(),
            timeline_data=scene.timeline_data
        )

    # Case 2: Only emphasis_words provided (recalculate timeline)
    if request.emphasis_words is not None:
        scene.emphasis_words = request.emphasis_words

        # Recalculate timeline if we have TTS metadata
        if scene.tts_metadata and scene.voiceover:
            timeline_service = TimelineCalculateService()
            scene_type = scene.scene_type or "explanation"
            duration_sec = scene.duration_sec or 8.0

            new_timeline = timeline_service.calculate_timeline_with_rhythm(
                emphasis_words=request.emphasis_words,
                tts_metadata=scene.tts_metadata,
                voiceover=scene.voiceover,
                scene_type=scene_type,
                duration_sec=duration_sec
            )

            if new_timeline:
                scene.timeline_data = new_timeline
                logger.info(f"Timeline recalculated for scene {scene_id}")
            else:
                logger.warning(f"Failed to recalculate timeline for scene {scene_id}")

        db.commit()
        db.refresh(scene)

        return UpdateTimelineResponse(
            success=True,
            scene_id=scene_id,
            updated_at=scene.updated_at.isoformat(),
            timeline_data=scene.timeline_data
        )

    # Case 3: No updates provided
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Either emphasis_words or timeline_data must be provided"
    )


@router.post("/{scene_id}/preview", response_model=PreviewResponse)
async def generate_preview(
    scene_id: str,
    request: PreviewRequest,
    db: Session = Depends(get_db)
):
    """Generate preview video for a scene

    This endpoint generates a low-resolution preview video for testing timeline adjustments.
    """
    # Find scene
    scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scene {scene_id} not found"
        )

    logger.info(f"Preview requested for scene {scene_id}")

    # Validate scene has required data
    if not scene.timeline_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scene has no timeline data"
        )

    # Prepare scene data
    scene_data = {
        "scene_id": scene_id,
        "template_type": scene.template_type,
        "voiceover": scene.voiceover,
        "screen_text": scene.screen_text,
        "duration_sec": scene.duration_sec,
        "timeline_data": scene.timeline_data,
        "visual_params": scene.visual_params,
    }

    # Generate preview
    preview_service = get_preview_service()
    preview_url = await preview_service.generate_preview(
        scene_id=scene_id,
        scene_data=scene_data,
        start_time=request.start_time or 0,
        end_time=request.end_time,
        quality=request.quality or "low"
    )

    if preview_url:
        duration = request.end_time - (request.start_time or 0) if request.end_time else scene.duration_sec
        return PreviewResponse(
            success=True,
            scene_id=scene_id,
            preview_url=preview_url,
            duration=duration
        )
    else:
        return PreviewResponse(
            success=False,
            scene_id=scene_id,
            message="Preview generation failed. Please check logs for details."
        )

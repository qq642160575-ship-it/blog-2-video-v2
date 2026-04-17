from sqlalchemy.orm import Session
from app.models.scene import Scene
from app.models.scene_version import SceneVersion
from typing import Dict, List, Optional


class SceneService:
    def __init__(self, db: Session):
        self.db = db

    def get_project_scenes(self, project_id: str) -> List[Scene]:
        """Get all scenes for a project"""
        return self.db.query(Scene).filter(
            Scene.project_id == project_id
        ).order_by(Scene.scene_order).all()

    def get_scene(self, scene_id: str) -> Optional[Scene]:
        """Get a single scene by ID"""
        return self.db.query(Scene).filter(Scene.id == scene_id).first()

    def validate_scene_update(self, updates: Dict) -> List[str]:
        """Validate scene update data"""
        errors = []

        # Validate voiceover length
        if "voiceover" in updates:
            voiceover = updates["voiceover"]
            if len(voiceover) > 90:
                errors.append(f"Voiceover too long: {len(voiceover)} chars (max 90)")

        # Validate screen_text
        if "screen_text" in updates:
            screen_text = updates["screen_text"]
            if not isinstance(screen_text, list):
                errors.append("screen_text must be a list")
            elif len(screen_text) > 3:
                errors.append(f"Too many screen_text items: {len(screen_text)} (max 3)")
            else:
                for i, text in enumerate(screen_text):
                    if len(text) > 18:
                        errors.append(f"screen_text[{i}] too long: {len(text)} chars (max 18)")

        # Validate duration
        if "duration_sec" in updates:
            duration = updates["duration_sec"]
            if duration < 4 or duration > 9:
                errors.append(f"Duration out of range: {duration}s (must be 4-9)")

        return errors

    def update_scene(self, scene_id: str, updates: Dict) -> Scene:
        """Update a scene and create a version history entry"""
        scene = self.get_scene(scene_id)
        if not scene:
            raise ValueError(f"Scene {scene_id} not found")

        # Validate updates
        errors = self.validate_scene_update(updates)
        if errors:
            raise ValueError(f"Validation errors: {', '.join(errors)}")

        # Save current version to history
        version = SceneVersion(
            scene_id=scene.id,
            version=scene.current_version,
            project_id=scene.project_id,
            template_type=scene.template_type,
            goal=scene.goal,
            voiceover=scene.voiceover,
            screen_text=scene.screen_text,
            duration_sec=scene.duration_sec,
            pace=scene.pace,
            transition=scene.transition,
            visual_params=scene.visual_params
        )
        self.db.add(version)

        # Update scene
        for key, value in updates.items():
            if hasattr(scene, key):
                setattr(scene, key, value)

        # Increment version
        scene.current_version += 1

        self.db.commit()
        self.db.refresh(scene)

        return scene

    def get_scene_versions(self, scene_id: str) -> List[SceneVersion]:
        """Get version history for a scene"""
        return self.db.query(SceneVersion).filter(
            SceneVersion.scene_id == scene_id
        ).order_by(SceneVersion.version.desc()).all()

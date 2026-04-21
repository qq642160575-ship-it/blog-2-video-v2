"""Preview rendering service for timeline editor
Generates low-resolution preview videos for quick feedback
"""
import os
import json
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, Any
from app.core.config import get_settings
from app.core.logging_config import get_logger

settings = get_settings()
logger = get_logger("app")


class PreviewService:
    """Service for generating preview videos"""

    def __init__(self):
        self.remotion_dir = Path(__file__).parent.parent.parent.parent / "remotion"
        self.storage_dir = Path(__file__).parent.parent.parent.parent / "backend" / "storage"
        self.preview_dir = self.storage_dir / "previews"
        self.preview_dir.mkdir(parents=True, exist_ok=True)

    async def generate_preview(
        self,
        scene_id: str,
        scene_data: Dict[str, Any],
        start_time: float = 0,
        end_time: Optional[float] = None,
        quality: str = "low"
    ) -> Optional[str]:
        """
        Generate preview video for a scene

        Args:
            scene_id: Scene ID
            scene_data: Scene data including timeline_data, voiceover, etc.
            start_time: Preview start time in seconds
            end_time: Preview end time in seconds (None = full scene)
            quality: Preview quality (low/medium)

        Returns:
            Preview video URL or None if failed
        """
        try:
            logger.info(f"Generating preview for scene {scene_id}")

            # Prepare preview manifest
            preview_manifest = self._create_preview_manifest(
                scene_id, scene_data, start_time, end_time
            )

            # Save preview manifest
            manifest_path = self.preview_dir / f"{scene_id}_preview_manifest.json"
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(preview_manifest, f, ensure_ascii=False, indent=2)

            # Render preview video
            output_path = self.preview_dir / f"{scene_id}_preview.mp4"

            success = await self._render_preview(
                manifest_path, output_path, quality
            )

            if success and output_path.exists():
                # Return relative URL
                preview_url = f"/storage/previews/{scene_id}_preview.mp4"
                logger.info(f"Preview generated: {preview_url}")
                return preview_url
            else:
                logger.error(f"Preview generation failed for scene {scene_id}")
                return None

        except Exception as e:
            logger.error(f"Error generating preview for scene {scene_id}: {e}")
            return None

    def _create_preview_manifest(
        self,
        scene_id: str,
        scene_data: Dict[str, Any],
        start_time: float,
        end_time: Optional[float]
    ) -> Dict[str, Any]:
        """Create preview manifest for single scene"""

        duration_sec = scene_data.get("duration_sec", 8)
        if end_time is None:
            end_time = duration_sec

        # Calculate frame range
        fps = 30
        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)
        duration_frames = end_frame - start_frame

        manifest = {
            "project_id": f"preview_{scene_id}",
            "total_duration_ms": int((end_time - start_time) * 1000),
            "fps": fps,
            "scenes": [
                {
                    "scene_id": scene_id,
                    "template_type": scene_data.get("template_type", "hook_title"),
                    "start_ms": 0,
                    "end_ms": int((end_time - start_time) * 1000),
                    "voiceover": scene_data.get("voiceover", ""),
                    "screen_text": scene_data.get("screen_text", []),
                    "timeline_data": scene_data.get("timeline_data"),
                    "audio_url": scene_data.get("audio_url"),
                    "visual_params": scene_data.get("visual_params", {}),
                }
            ]
        }

        return manifest

    async def _render_preview(
        self,
        manifest_path: Path,
        output_path: Path,
        quality: str
    ) -> bool:
        """Render preview video using Remotion"""

        try:
            # Set quality parameters
            if quality == "low":
                width = 640
                height = 360
                crf = 28
            else:  # medium
                width = 854
                height = 480
                crf = 23

            # Remotion render command
            cmd = [
                "npx",
                "remotion",
                "render",
                "src/index.ts",
                "VideoComposition",
                str(output_path),
                "--props",
                str(manifest_path),
                "--width",
                str(width),
                "--height",
                str(height),
                "--codec",
                "h264",
                "--crf",
                str(crf),
                "--overwrite"
            ]

            logger.info(f"Running Remotion render: {' '.join(cmd)}")

            # Run render process
            process = subprocess.Popen(
                cmd,
                cwd=str(self.remotion_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for completion (with timeout)
            try:
                stdout, stderr = process.communicate(timeout=60)  # 60 second timeout

                if process.returncode == 0:
                    logger.info("Preview render completed successfully")
                    return True
                else:
                    logger.error(f"Preview render failed: {stderr}")
                    return False

            except subprocess.TimeoutExpired:
                process.kill()
                logger.error("Preview render timeout")
                return False

        except Exception as e:
            logger.error(f"Error rendering preview: {e}")
            return False


# Singleton instance
_preview_service = None


def get_preview_service() -> PreviewService:
    """Get preview service singleton"""
    global _preview_service
    if _preview_service is None:
        _preview_service = PreviewService()
    return _preview_service

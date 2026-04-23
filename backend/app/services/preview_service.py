"""Preview rendering service for timeline editor
Generates low-resolution preview videos for quick feedback
"""
import os
import json
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from app.core.config import get_settings
from app.core.logging_config import get_logger

settings = get_settings()
logger = get_logger("app")


class PreviewService:
    """Service for generating preview videos"""

    def __init__(self):
        # Get project root directory
        backend_dir = Path(__file__).parent.parent.parent
        project_root = backend_dir.parent

        self.remotion_dir = project_root / "remotion"
        self.storage_dir = backend_dir / "storage"
        self.preview_dir = self.storage_dir / "previews"
        self.preview_dir.mkdir(parents=True, exist_ok=True)

        # Verify remotion directory exists
        if not self.remotion_dir.exists():
            logger.error(f"Remotion directory not found: {self.remotion_dir}")
        else:
            logger.info(f"Remotion directory: {self.remotion_dir}")

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

    def _get_composition_id(self, template_type: str) -> str:
        """Map template_type to Remotion Composition ID"""
        mapping = {
            "hook_title": "HookTitle",
            "bullet_explain": "BulletExplain",
            "compare_process": "CompareProcess"
        }
        return mapping.get(template_type, "HookTitle")

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

        template_type = scene_data.get("template_type", "hook_title")
        composition_id = self._get_composition_id(template_type)

        # Prepare props based on template type
        visual_params = scene_data.get("visual_params", {})
        screen_text = scene_data.get("screen_text", [])

        if template_type == "hook_title":
            props = {
                "title": screen_text[0] if screen_text else scene_data.get("voiceover", ""),
                "subtitle": screen_text[1] if len(screen_text) > 1 else "",
                "timeline": scene_data.get("timeline_data"),
                "subtitles": self._generate_subtitles_from_voiceover(
                    scene_data.get("voiceover", ""),
                    scene_data.get("tts_metadata"),
                    duration_sec
                )
            }
        elif template_type == "bullet_explain":
            props = {
                "title": screen_text[0] if screen_text else "标题",
                "bullets": screen_text[1:] if len(screen_text) > 1 else [],
                "accentColor": visual_params.get("accent_color", "#f97316")
            }
        elif template_type == "compare_process":
            props = {
                "title": screen_text[0] if screen_text else "对比",
                "leftTitle": visual_params.get("left_title", "方案A"),
                "rightTitle": visual_params.get("right_title", "方案B"),
                "leftPoints": visual_params.get("left_points", []),
                "rightPoints": visual_params.get("right_points", []),
                "footerText": visual_params.get("footer_text", "")
            }
        else:
            props = {}

        manifest = {
            "compositionId": composition_id,
            "durationInFrames": duration_frames,
            "fps": fps,
            "props": props
        }

        return manifest

    def _generate_subtitles_from_voiceover(
        self,
        voiceover: str,
        tts_metadata: Optional[Dict[str, Any]],
        duration_sec: float
    ) -> List[Dict[str, Any]]:
        """
        Generate subtitle data from voiceover and TTS metadata

        Args:
            voiceover: Voiceover text
            tts_metadata: TTS metadata with word timestamps
            duration_sec: Scene duration in seconds

        Returns:
            List of subtitle segments with timing
        """
        if not voiceover:
            return []

        # If we have TTS metadata with word timestamps, use them
        if tts_metadata and "word_timestamps" in tts_metadata:
            word_timestamps = tts_metadata["word_timestamps"]
            if word_timestamps:
                # Group words into subtitle segments (every 5-8 words or by punctuation)
                subtitles = []
                current_segment = []
                segment_start = 0

                for i, word_info in enumerate(word_timestamps):
                    word = word_info.get("word", "")
                    start_time = word_info.get("start_time", 0)
                    end_time = word_info.get("end_time", 0)

                    if not current_segment:
                        segment_start = start_time

                    current_segment.append(word)

                    # Create segment on punctuation or every 6 words
                    is_punctuation = word.endswith(('。', '？', '！', '，', '.', '?', '!', ','))
                    should_break = is_punctuation or len(current_segment) >= 6
                    is_last = i == len(word_timestamps) - 1

                    if should_break or is_last:
                        subtitles.append({
                            "text": "".join(current_segment),
                            "start_ms": int(segment_start * 1000),
                            "end_ms": int(end_time * 1000)
                        })
                        current_segment = []

                return subtitles

        # Fallback: split voiceover into segments by punctuation
        import re
        segments = re.split(r'([。？！，.?!,])', voiceover)

        subtitles = []
        time_per_char = duration_sec / len(voiceover) if voiceover else 0
        current_time = 0

        for i in range(0, len(segments) - 1, 2):
            text = segments[i] + (segments[i + 1] if i + 1 < len(segments) else "")
            text = text.strip()

            if text:
                segment_duration = len(text) * time_per_char
                subtitles.append({
                    "text": text,
                    "start_ms": int(current_time * 1000),
                    "end_ms": int((current_time + segment_duration) * 1000)
                })
                current_time += segment_duration

        return subtitles

    async def _render_preview(
        self,
        manifest_path: Path,
        output_path: Path,
        quality: str
    ) -> bool:
        """Render preview video using Remotion"""

        try:
            # Load manifest to get composition info
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)

            composition_id = manifest.get("compositionId", "HookTitle")
            props_json = json.dumps(manifest.get("props", {}))

            # Set quality parameters
            if quality == "low":
                scale = 0.5  # 540x960 for vertical video
                crf = 28
            else:  # medium
                scale = 0.75  # 810x1440
                crf = 23

            # Remotion render command
            cmd = [
                "npx",
                "remotion",
                "render",
                "src/index.tsx",
                composition_id,
                str(output_path),
                "--props",
                props_json,
                "--scale",
                str(scale),
                "--codec",
                "h264",
                "--crf",
                str(crf),
                "--overwrite"
            ]

            logger.info(f"Running Remotion render: {' '.join(cmd)}")
            logger.info(f"Composition: {composition_id}, Props: {props_json}")

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
                stdout, stderr = process.communicate(timeout=120)  # 120 second timeout

                if process.returncode == 0:
                    logger.info("Preview render completed successfully")
                    logger.debug(f"Render output: {stdout}")
                    return True
                else:
                    logger.error(f"Preview render failed with code {process.returncode}")
                    logger.error(f"Stderr: {stderr}")
                    logger.error(f"Stdout: {stdout}")
                    return False

            except subprocess.TimeoutExpired:
                process.kill()
                logger.error("Preview render timeout (120s)")
                return False

        except Exception as e:
            logger.error(f"Error rendering preview: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False


# Singleton instance
_preview_service = None


def get_preview_service() -> PreviewService:
    """Get preview service singleton"""
    global _preview_service
    if _preview_service is None:
        _preview_service = PreviewService()
    return _preview_service

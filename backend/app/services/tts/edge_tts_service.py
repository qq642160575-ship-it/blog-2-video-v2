"""input: 依赖 Edge TTS SDK、文件系统。
output: 向外提供基于 Edge TTS 的语音合成能力。
pos: 位于 service 层，实现 Edge TTS 提供商。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

import os
import uuid
import asyncio
from typing import Optional
import edge_tts
from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.services.tts.base import BaseTTSService

settings = get_settings()
logger = get_logger("app")


class EdgeTTSService(BaseTTSService):
    """Edge TTS implementation (Free)"""

    def __init__(self):
        """Initialize Edge TTS"""
        self.storage_path = settings.storage_path
        self.audio_dir = os.path.join(self.storage_path, "audio")
        os.makedirs(self.audio_dir, exist_ok=True)

    async def _synthesize_async(
        self,
        text: str,
        output_path: str,
        voice_name: str = "zh-CN-XiaoxiaoNeural",
        speaking_rate: str = "+0%"
    ):
        """
        Async synthesize speech using Edge TTS

        Args:
            text: Text to synthesize
            output_path: Output file path
            voice_name: Voice name
            speaking_rate: Speaking rate (e.g., "+20%", "-15%")
        """
        communicate = edge_tts.Communicate(text, voice_name, rate=speaking_rate)
        await communicate.save(output_path)

    def synthesize_speech(
        self,
        text: str,
        output_filename: Optional[str] = None,
        voice_name: Optional[str] = None,
        speaking_rate: float = 1.0
    ) -> str:
        """
        Synthesize speech from text using Edge TTS

        Args:
            text: Text to synthesize
            output_filename: Optional output filename (without path)
            voice_name: Edge TTS voice name (default: zh-CN-XiaoxiaoNeural)
            speaking_rate: Speaking rate (0.5-2.0, default: 1.0)

        Returns:
            Path to generated audio file

        Raises:
            ValueError: If synthesis fails
        """
        try:
            if voice_name is None:
                voice_name = "zh-CN-XiaoxiaoNeural"

            logger.info(f"Synthesizing speech: {len(text)} chars, voice: {voice_name}, rate: {speaking_rate}")

            if not output_filename:
                output_filename = f"audio_{uuid.uuid4().hex[:12]}.mp3"

            output_path = os.path.join(self.audio_dir, output_filename)

            # Convert speaking_rate to percentage
            rate_percent = int((speaking_rate - 1.0) * 100)
            rate_str = f"{rate_percent:+d}%"

            # Run async synthesis
            asyncio.run(self._synthesize_async(
                text=text,
                output_path=output_path,
                voice_name=voice_name,
                speaking_rate=rate_str
            ))

            logger.info(f"Speech synthesized successfully: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to synthesize speech: {str(e)}")
            raise ValueError(f"Failed to synthesize speech: {str(e)}")

    def synthesize_scene_audio(
        self,
        scene_id: str,
        voiceover: str,
        pace: str = "medium"
    ) -> str:
        """
        Synthesize audio for a scene

        Args:
            scene_id: Scene ID
            voiceover: Voiceover text
            pace: Scene pace (fast/medium/slow)

        Returns:
            Path to generated audio file
        """
        logger.debug(f"Synthesizing audio for scene {scene_id}, pace: {pace}")

        pace_map = {
            "fast": 1.2,
            "medium": 1.0,
            "slow": 0.85
        }
        speaking_rate = pace_map.get(pace, 1.0)

        filename = f"{scene_id}.mp3"

        return self.synthesize_speech(
            text=voiceover,
            output_filename=filename,
            speaking_rate=speaking_rate
        )

    def synthesize_batch(
        self,
        scenes: list,
        voice_name: Optional[str] = None
    ) -> dict:
        """
        Synthesize audio for multiple scenes

        Args:
            scenes: List of scene dicts with scene_id, voiceover, pace
            voice_name: Edge TTS voice name

        Returns:
            Dict mapping scene_id to audio file path
        """
        logger.info(f"Starting batch synthesis for {len(scenes)} scenes")
        results = {}
        errors = []

        for scene in scenes:
            scene_id = scene.get("scene_id")
            voiceover = scene.get("voiceover")
            pace = scene.get("pace", "medium")

            try:
                audio_path = self.synthesize_scene_audio(
                    scene_id=scene_id,
                    voiceover=voiceover,
                    pace=pace
                )
                results[scene_id] = audio_path
            except Exception as e:
                error_msg = f"Scene {scene_id}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"Failed to synthesize scene {scene_id}: {e}")

        if errors:
            logger.error(f"Batch synthesis completed with {len(errors)} errors")
            raise ValueError(f"Failed to synthesize some scenes: {'; '.join(errors)}")

        logger.info(f"Batch synthesis completed successfully for {len(results)} scenes")
        return results

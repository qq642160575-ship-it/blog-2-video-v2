"""input: 依赖 TTS 供应商配置、文件系统和字幕链路。
output: 向外提供旁白转音频能力（兼容层）。
pos: 位于 service 层，负责语音生成（向后兼容的包装器）。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

from typing import Optional
from app.services.tts.factory import TTSFactory
from app.core.logging_config import get_logger

logger = get_logger("app")


class TTSService:
    """
    Backward-compatible TTS Service wrapper

    This class maintains backward compatibility with existing code
    while delegating to the new pluggable TTS architecture.
    """

    def __init__(self, provider: Optional[str] = None):
        """
        Initialize TTS Service

        Args:
            provider: TTS provider name ('edge', 'volcengine')
                     If None, uses settings.tts_provider
        """
        self._service = TTSFactory.create(provider)
        logger.info(f"TTSService initialized with provider: {type(self._service).__name__}")

    def synthesize_speech(
        self,
        text: str,
        output_filename: Optional[str] = None,
        voice_name: Optional[str] = None,
        speaking_rate: float = 1.0
    ) -> str:
        """
        Synthesize speech from text

        Args:
            text: Text to synthesize
            output_filename: Optional output filename (without path)
            voice_name: Voice name (provider-specific)
            speaking_rate: Speaking rate (0.5-2.0, default: 1.0)

        Returns:
            Path to generated audio file

        Raises:
            ValueError: If synthesis fails
        """
        return self._service.synthesize_speech(
            text=text,
            output_filename=output_filename,
            voice_name=voice_name,
            speaking_rate=speaking_rate
        )

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
        return self._service.synthesize_scene_audio(
            scene_id=scene_id,
            voiceover=voiceover,
            pace=pace
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
            voice_name: Voice name (provider-specific)

        Returns:
            Dict mapping scene_id to audio file path
        """
        return self._service.synthesize_batch(
            scenes=scenes,
            voice_name=voice_name
        )

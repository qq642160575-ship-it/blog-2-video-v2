"""input: 无外部依赖。
output: 向外提供 TTS 服务抽象基类。
pos: 位于 service 层，定义 TTS 服务接口。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

from abc import ABC, abstractmethod
from typing import Optional


class BaseTTSService(ABC):
    """Abstract base class for TTS services"""

    @abstractmethod
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
            voice_name: Voice name/ID (provider-specific)
            speaking_rate: Speaking rate (0.5-2.0, default: 1.0)

        Returns:
            Path to generated audio file

        Raises:
            ValueError: If synthesis fails
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def synthesize_batch(
        self,
        scenes: list,
        voice_name: Optional[str] = None
    ) -> dict:
        """
        Synthesize audio for multiple scenes

        Args:
            scenes: List of scene dicts with scene_id, voiceover, pace
            voice_name: Voice name/ID (provider-specific)

        Returns:
            Dict mapping scene_id to audio file path
        """
        pass

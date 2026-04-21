"""input: 依赖配置系统。
output: 向外提供 TTS 服务工厂，根据配置创建对应的 TTS 服务实例。
pos: 位于 service 层，负责 TTS 服务实例化。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

from typing import Optional
from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.services.tts.base import BaseTTSService

# Optional imports
try:
    from app.services.tts.edge_tts_service import EdgeTTSService
except ImportError:
    EdgeTTSService = None

from app.services.tts.volcengine_tts_service import VolcengineTTSService

settings = get_settings()
logger = get_logger("app")


class TTSFactory:
    """Factory for creating TTS service instances"""

    @staticmethod
    def create(provider: Optional[str] = None) -> BaseTTSService:
        """
        Create a TTS service instance based on provider

        Args:
            provider: TTS provider name ('edge', 'volcengine', 'azure')
                     If None, uses settings.tts_provider

        Returns:
            TTS service instance

        Raises:
            ValueError: If provider is not supported
        """
        if provider is None:
            provider = getattr(settings, "tts_provider", "edge").lower()

        logger.info(f"Creating TTS service with provider: {provider}")

        if provider == "edge":
            if EdgeTTSService is None:
                raise ValueError("EdgeTTS provider is not available. Install edge-tts package.")
            return EdgeTTSService()
        elif provider == "volcengine":
            return VolcengineTTSService(
                app_id=getattr(settings, "volcengine_app_id", None),
                access_token=getattr(settings, "volcengine_access_token", None),
                cluster=getattr(settings, "volcengine_cluster", "volcano_tts"),
                api_key=getattr(settings, "volcengine_api_key", None)
            )
        else:
            raise ValueError(f"Unsupported TTS provider: {provider}")

    @staticmethod
    def get_available_providers() -> list:
        """
        Get list of available TTS providers

        Returns:
            List of provider names
        """
        return ["edge", "volcengine"]

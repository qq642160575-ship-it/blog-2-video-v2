"""TTS Services Package"""

from app.services.tts.base import BaseTTSService

# Optional imports - only import if dependencies are available
try:
    from app.services.tts.edge_tts_service import EdgeTTSService
except ImportError:
    EdgeTTSService = None

from app.services.tts.volcengine_tts_service import VolcengineTTSService
from app.services.tts.factory import TTSFactory

__all__ = [
    "BaseTTSService",
    "EdgeTTSService",
    "VolcengineTTSService",
    "TTSFactory",
]

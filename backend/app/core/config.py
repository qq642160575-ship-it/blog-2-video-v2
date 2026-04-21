"""input: 依赖环境变量和 pydantic settings。
output: 向外提供全局 Settings 和配置读取函数。
pos: 位于基础设施层，负责统一配置。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

import os
from pydantic_settings import BaseSettings
from functools import lru_cache


def _sanitize_proxy_env() -> None:
    for key in ("ALL_PROXY", "all_proxy"):
        value = os.environ.get(key, "")
        if value.startswith("socks://"):
            os.environ.pop(key, None)


_sanitize_proxy_env()


class Settings(BaseSettings):
    # Environment
    environment: str = "development"

    # Database
    database_url: str

    # Redis
    redis_url: str

    # OpenAI Compatible API
    openai_api_key: str
    openai_base_url: str = "https://api.openai.com/v1"

    # Azure Speech
    azure_speech_key: str = ""
    azure_speech_region: str = "eastus"

    # TTS Provider Configuration
    tts_provider: str = "edge"  # Options: 'edge', 'volcengine'

    # Volcengine TTS Configuration
    volcengine_app_id: str = ""
    volcengine_access_token: str = ""
    volcengine_cluster: str = "volcano_tts"
    volcengine_api_key: str = ""

    # Storage
    storage_path: str = "./storage"

    # v3 功能开关
    v3_enabled: bool = False
    v3_traffic_percentage: int = 0

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()

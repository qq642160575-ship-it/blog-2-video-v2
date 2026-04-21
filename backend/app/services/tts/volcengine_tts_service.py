"""input: 依赖火山云 TTS API、文件系统。
output: 向外提供基于火山云的语音合成能力。
pos: 位于 service 层，实现火山云 TTS 提供商。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

import os
import uuid
import json
import base64
from typing import Optional
import requests
from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.services.tts.base import BaseTTSService

settings = get_settings()
logger = get_logger("app")


class VolcengineTTSService(BaseTTSService):
    """Volcengine (火山云) TTS implementation"""

    def __init__(
        self,
        app_id: Optional[str] = None,
        access_token: Optional[str] = None,
        cluster: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize Volcengine TTS

        Args:
            app_id: Volcengine app ID
            access_token: Volcengine access token
            cluster: Volcengine cluster
            api_key: Volcengine API key (optional, for future use)
        """
        self.storage_path = settings.storage_path
        self.audio_dir = os.path.join(self.storage_path, "audio")
        os.makedirs(self.audio_dir, exist_ok=True)

        # Load credentials from settings or parameters
        self.app_id = app_id or getattr(settings, "volcengine_app_id", None)
        self.access_token = access_token or getattr(settings, "volcengine_access_token", None)
        self.cluster = cluster or getattr(settings, "volcengine_cluster", "volcano_tts")
        self.api_key = api_key or getattr(settings, "volcengine_api_key", None)

        if not self.app_id or not self.access_token:
            raise ValueError("Volcengine app_id and access_token are required")

        self.host = "openspeech.bytedance.com"
        self.api_url = f"https://{self.host}/api/v1/tts"

    def _extract_tts_metadata(self, response_data: dict) -> Optional[dict]:
        """
        Extract TTS metadata including word-level timestamps from API response

        Args:
            response_data: Raw API response from Volcengine TTS

        Returns:
            Dictionary containing duration and word_timestamps, or None if extraction fails
        """
        try:
            if "addition" not in response_data:
                logger.warning("No 'addition' field in TTS response")
                return None

            addition = response_data["addition"]
            metadata = {
                "duration": addition.get("duration")
            }

            # Extract word-level timestamps from frontend data
            if "frontend" in addition:
                frontend_str = addition["frontend"]
                frontend_data = json.loads(frontend_str)

                # Extract word timestamps
                if "words" in frontend_data:
                    metadata["word_timestamps"] = frontend_data["words"]

                # Extract phoneme timestamps (optional)
                if "phonemes" in frontend_data:
                    metadata["phonemes"] = frontend_data["phonemes"]

            return metadata

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse frontend JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to extract TTS metadata: {e}")
            return None

    def synthesize_speech(
        self,
        text: str,
        output_filename: Optional[str] = None,
        voice_name: Optional[str] = None,
        speaking_rate: float = 1.0
    ) -> tuple[str, Optional[dict]]:
        """
        Synthesize speech from text using Volcengine TTS

        Args:
            text: Text to synthesize
            output_filename: Optional output filename (without path)
            voice_name: Volcengine voice type (default: BV700_streaming)
            speaking_rate: Speaking rate (0.2-3.0, default: 1.0)

        Returns:
            Tuple of (audio_file_path, tts_metadata)
            - audio_file_path: Path to generated audio file
            - tts_metadata: Dictionary containing duration and word_timestamps

        Raises:
            ValueError: If synthesis fails
        """
        try:
            if voice_name is None:
                voice_name = "BV700_streaming"

            logger.info(f"Synthesizing speech with Volcengine: {len(text)} chars, voice: {voice_name}, rate: {speaking_rate}")

            if not output_filename:
                output_filename = f"audio_{uuid.uuid4().hex[:12]}.mp3"

            output_path = os.path.join(self.audio_dir, output_filename)

            # Prepare request
            header = {"Authorization": f"Bearer;{self.access_token}"}

            request_json = {
                "app": {
                    "appid": self.app_id,
                    "token": self.access_token,
                    "cluster": self.cluster
                },
                "user": {
                    "uid": str(uuid.uuid4())
                },
                "audio": {
                    "voice_type": voice_name,
                    "encoding": "mp3",
                    "speed_ratio": speaking_rate,
                    "volume_ratio": 1.0,
                    "pitch_ratio": 1.0,
                },
                "request": {
                    "reqid": str(uuid.uuid4()),
                    "text": text,
                    "text_type": "plain",
                    "operation": "query",
                    "with_frontend": 1,
                    "frontend_type": "unitTson"
                }
            }

            # Make request
            resp = requests.post(self.api_url, json.dumps(request_json), headers=header, timeout=60)
            resp_data = resp.json()

            # Check response
            if resp_data.get("code") != 3000:
                error_msg = resp_data.get("message", "Unknown error")
                logger.error(f"Volcengine TTS failed: {error_msg}")
                raise ValueError(f"Volcengine TTS failed: {error_msg}")

            # Extract metadata (including timestamps)
            tts_metadata = self._extract_tts_metadata(resp_data)

            # Save audio data
            if "data" in resp_data:
                audio_data = base64.b64decode(resp_data["data"])
                with open(output_path, "wb") as f:
                    f.write(audio_data)

                logger.info(f"Speech synthesized successfully: {output_path}")
                if tts_metadata and "word_timestamps" in tts_metadata:
                    logger.info(f"Extracted {len(tts_metadata['word_timestamps'])} word timestamps")
                return output_path, tts_metadata
            else:
                raise ValueError("No audio data in response")

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during Volcengine TTS: {str(e)}")
            raise ValueError(f"Network error during Volcengine TTS: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to synthesize speech with Volcengine: {str(e)}")
            raise ValueError(f"Failed to synthesize speech with Volcengine: {str(e)}")

    def synthesize_scene_audio(
        self,
        scene_id: str,
        voiceover: str,
        pace: str = "medium"
    ) -> tuple[str, Optional[dict]]:
        """
        Synthesize audio for a scene

        Args:
            scene_id: Scene ID
            voiceover: Voiceover text
            pace: Scene pace (fast/medium/slow)

        Returns:
            Tuple of (audio_file_path, tts_metadata)
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
            voice_name: Volcengine voice type

        Returns:
            Dict mapping scene_id to tuple of (audio_file_path, tts_metadata)
        """
        logger.info(f"Starting batch synthesis for {len(scenes)} scenes")
        results = {}
        errors = []

        for scene in scenes:
            scene_id = scene.get("scene_id")
            voiceover = scene.get("voiceover")
            pace = scene.get("pace", "medium")

            try:
                audio_path, tts_metadata = self.synthesize_scene_audio(
                    scene_id=scene_id,
                    voiceover=voiceover,
                    pace=pace
                )
                results[scene_id] = (audio_path, tts_metadata)
            except Exception as e:
                error_msg = f"Scene {scene_id}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"Failed to synthesize scene {scene_id}: {e}")

        if errors:
            logger.error(f"Batch synthesis completed with {len(errors)} errors")
            raise ValueError(f"Failed to synthesize some scenes: {'; '.join(errors)}")

        logger.info(f"Batch synthesis completed successfully for {len(results)} scenes")
        return results

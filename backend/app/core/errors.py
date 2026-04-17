"""input: 依赖系统错误码定义需求。
output: 向外提供错误码枚举和错误文案映射。
pos: 位于基础设施层，负责统一错误语义。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

"""
Error Codes - Standardized error codes for the system
"""
from enum import Enum


class ErrorCode(str, Enum):
    """Standardized error codes"""

    # General errors
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"

    # Project errors
    PROJECT_NOT_FOUND = "PROJECT_NOT_FOUND"
    PROJECT_CONTENT_TOO_SHORT = "PROJECT_CONTENT_TOO_SHORT"
    PROJECT_CONTENT_TOO_LONG = "PROJECT_CONTENT_TOO_LONG"

    # Job errors
    JOB_NOT_FOUND = "JOB_NOT_FOUND"
    JOB_ALREADY_RUNNING = "JOB_ALREADY_RUNNING"
    JOB_FAILED = "JOB_FAILED"
    INVALID_JOB_TYPE = "INVALID_JOB_TYPE"

    # Article parse errors
    ARTICLE_PARSE_FAILED = "ARTICLE_PARSE_FAILED"
    ARTICLE_PARSE_TIMEOUT = "ARTICLE_PARSE_TIMEOUT"
    ARTICLE_PARSE_INVALID_RESPONSE = "ARTICLE_PARSE_INVALID_RESPONSE"

    # Scene generation errors
    SCENE_GENERATE_FAILED = "SCENE_GENERATE_FAILED"
    SCENE_GENERATE_TIMEOUT = "SCENE_GENERATE_TIMEOUT"
    SCENE_GENERATE_INVALID_RESPONSE = "SCENE_GENERATE_INVALID_RESPONSE"
    SCENE_VALIDATION_FAILED = "SCENE_VALIDATION_FAILED"
    NO_SCENES_GENERATED = "NO_SCENES_GENERATED"

    # TTS errors
    TTS_FAILED = "TTS_FAILED"
    TTS_TIMEOUT = "TTS_TIMEOUT"
    TTS_AUDIO_GENERATION_FAILED = "TTS_AUDIO_GENERATION_FAILED"

    # Subtitle errors
    SUBTITLE_GENERATION_FAILED = "SUBTITLE_GENERATION_FAILED"
    SUBTITLE_EXPORT_FAILED = "SUBTITLE_EXPORT_FAILED"

    # Render errors
    RENDER_MANIFEST_CREATION_FAILED = "RENDER_MANIFEST_CREATION_FAILED"
    RENDER_FAILED = "RENDER_FAILED"
    RENDER_TIMEOUT = "RENDER_TIMEOUT"
    RENDER_OUTPUT_INVALID = "RENDER_OUTPUT_INVALID"

    # Rerender errors
    RERENDER_NO_SCENES = "RERENDER_NO_SCENES"
    RERENDER_FAILED = "RERENDER_FAILED"

    # LLM errors
    LLM_API_KEY_MISSING = "LLM_API_KEY_MISSING"
    LLM_API_ERROR = "LLM_API_ERROR"
    LLM_RATE_LIMIT = "LLM_RATE_LIMIT"
    LLM_TIMEOUT = "LLM_TIMEOUT"
    LLM_INVALID_RESPONSE = "LLM_INVALID_RESPONSE"

    # Database errors
    DATABASE_ERROR = "DATABASE_ERROR"
    DATABASE_CONNECTION_FAILED = "DATABASE_CONNECTION_FAILED"

    # Queue errors
    QUEUE_ERROR = "QUEUE_ERROR"
    QUEUE_PUSH_FAILED = "QUEUE_PUSH_FAILED"
    QUEUE_POP_FAILED = "QUEUE_POP_FAILED"

    # Storage errors
    STORAGE_ERROR = "STORAGE_ERROR"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_WRITE_FAILED = "FILE_WRITE_FAILED"
    FILE_READ_FAILED = "FILE_READ_FAILED"


# Error messages mapping
ERROR_MESSAGES = {
    ErrorCode.UNKNOWN_ERROR: "An unknown error occurred",
    ErrorCode.INVALID_INPUT: "Invalid input provided",
    ErrorCode.RESOURCE_NOT_FOUND: "Resource not found",

    ErrorCode.PROJECT_NOT_FOUND: "Project not found",
    ErrorCode.PROJECT_CONTENT_TOO_SHORT: "Project content is too short (minimum 500 characters)",
    ErrorCode.PROJECT_CONTENT_TOO_LONG: "Project content is too long (maximum 10000 characters)",

    ErrorCode.JOB_NOT_FOUND: "Job not found",
    ErrorCode.JOB_ALREADY_RUNNING: "A job is already running for this project",
    ErrorCode.JOB_FAILED: "Job execution failed",
    ErrorCode.INVALID_JOB_TYPE: "Invalid job type",

    ErrorCode.ARTICLE_PARSE_FAILED: "Failed to parse article",
    ErrorCode.ARTICLE_PARSE_TIMEOUT: "Article parsing timed out",
    ErrorCode.ARTICLE_PARSE_INVALID_RESPONSE: "Invalid response from article parser",

    ErrorCode.SCENE_GENERATE_FAILED: "Failed to generate scenes",
    ErrorCode.SCENE_GENERATE_TIMEOUT: "Scene generation timed out",
    ErrorCode.SCENE_GENERATE_INVALID_RESPONSE: "Invalid response from scene generator",
    ErrorCode.SCENE_VALIDATION_FAILED: "Scene validation failed",
    ErrorCode.NO_SCENES_GENERATED: "No scenes were generated",

    ErrorCode.TTS_FAILED: "TTS generation failed",
    ErrorCode.TTS_TIMEOUT: "TTS generation timed out",
    ErrorCode.TTS_AUDIO_GENERATION_FAILED: "Failed to generate audio",

    ErrorCode.SUBTITLE_GENERATION_FAILED: "Subtitle generation failed",
    ErrorCode.SUBTITLE_EXPORT_FAILED: "Failed to export subtitles",

    ErrorCode.RENDER_MANIFEST_CREATION_FAILED: "Failed to create render manifest",
    ErrorCode.RENDER_FAILED: "Video rendering failed",
    ErrorCode.RENDER_TIMEOUT: "Video rendering timed out",
    ErrorCode.RENDER_OUTPUT_INVALID: "Render output is invalid",

    ErrorCode.RERENDER_NO_SCENES: "No scenes found for rerender",
    ErrorCode.RERENDER_FAILED: "Rerender failed",

    ErrorCode.LLM_API_KEY_MISSING: "LLM API key is missing",
    ErrorCode.LLM_API_ERROR: "LLM API error",
    ErrorCode.LLM_RATE_LIMIT: "LLM API rate limit exceeded",
    ErrorCode.LLM_TIMEOUT: "LLM request timed out",
    ErrorCode.LLM_INVALID_RESPONSE: "Invalid response from LLM",

    ErrorCode.DATABASE_ERROR: "Database error",
    ErrorCode.DATABASE_CONNECTION_FAILED: "Failed to connect to database",

    ErrorCode.QUEUE_ERROR: "Queue error",
    ErrorCode.QUEUE_PUSH_FAILED: "Failed to push task to queue",
    ErrorCode.QUEUE_POP_FAILED: "Failed to pop task from queue",

    ErrorCode.STORAGE_ERROR: "Storage error",
    ErrorCode.FILE_NOT_FOUND: "File not found",
    ErrorCode.FILE_WRITE_FAILED: "Failed to write file",
    ErrorCode.FILE_READ_FAILED: "Failed to read file",
}


def get_error_message(error_code: ErrorCode) -> str:
    """Get human-readable error message for an error code"""
    return ERROR_MESSAGES.get(error_code, ERROR_MESSAGES[ErrorCode.UNKNOWN_ERROR])

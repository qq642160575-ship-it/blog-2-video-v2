"""input: 依赖 typing 状态结构约定。
output: 向外提供 LangGraph 共享状态定义（含 v3 Hook 和验证字段）。
pos: 位于流程编排层，约束节点间共享数据。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

#!/usr/bin/env python3
"""
Generation State - State definition for LangGraph state machine
"""
from typing import TypedDict, Optional, Dict, List, Any


class GenerationState(TypedDict):
    """State for the generation pipeline"""
    # Job info
    job_id: str
    project_id: str
    job_type: str  # "generate" or "rerender"

    # Project data
    project_title: Optional[str]
    project_content: Optional[str]

    # Article analysis
    analysis: Optional[Dict[str, Any]]

    # v3: Hook generation
    hook_result: Optional[Dict[str, Any]]    # HookResult serialized
    selected_hook: Optional[Dict[str, Any]]  # Selected Hook serialized

    # Scene data
    scenes_data: Optional[List[Dict[str, Any]]]

    # v3: Enhanced validation
    validation_result: Optional[Dict[str, Any]]  # ValidationResult serialized
    validation_passed: Optional[bool]
    retry_count: Optional[int]  # 重试次数

    # Audio paths
    audio_paths: Optional[Dict[str, str]]

    # Subtitles
    subtitles: Optional[Dict[str, List[Dict[str, Any]]]]

    # Manifest
    manifest_path: Optional[str]

    # Execution summary
    execution_summary: Dict[str, Any]

    # Error handling
    error: Optional[str]
    error_code: Optional[str]

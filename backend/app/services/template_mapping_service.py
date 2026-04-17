"""input: 依赖分镜数据和 Remotion 模板约定。
output: 向外提供模板选择与参数映射能力。
pos: 位于 service 层，负责模板绑定。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

from typing import Any, Dict, List


class TemplateMappingService:
    """Map scene records to Remotion composition ids and props."""

    COMPOSITION_MAP = {
        "hook_title": "HookTitle",
        "bullet_explain": "BulletExplain",
        "compare_process": "CompareProcess",
    }

    def get_composition_id(self, template_type: str) -> str:
        return self.COMPOSITION_MAP.get(template_type, "HookTitle")

    def build_template_props(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        template_type = scene["template_type"]
        screen_text = self._normalize_screen_text(scene.get("screen_text"))
        visual_params = scene.get("visual_params") or {}

        if template_type == "bullet_explain":
            bullets = screen_text[:4] or [scene["voiceover"]]
            return {
                "title": scene.get("goal") or "核心要点",
                "bullets": bullets,
                "accentColor": visual_params.get("accent_color", "#f97316"),
            }

        if template_type == "compare_process":
            points = screen_text[:]
            midpoint = max(1, len(points) // 2)
            left_points = points[:midpoint] or ["传统方式"]
            right_points = points[midpoint:] or points[:1] or ["RAG 方式"]
            return {
                "title": scene.get("goal") or "对比说明",
                "leftTitle": visual_params.get("left_title", "传统方式"),
                "rightTitle": visual_params.get("right_title", "优化方式"),
                "leftPoints": left_points,
                "rightPoints": right_points,
                "footerText": visual_params.get("footer_text", scene["voiceover"]),
            }

        return {
            "title": screen_text[0] if screen_text else scene.get("goal", "视频标题"),
            "subtitle": screen_text[1] if len(screen_text) > 1 else scene["voiceover"],
        }

    def build_manifest_scene(
        self,
        scene: Dict[str, Any],
        start_ms: int,
        end_ms: int,
        audio_url: str | None = None,
    ) -> Dict[str, Any]:
        manifest_scene = {
            "scene_id": scene["scene_id"],
            "start_ms": start_ms,
            "end_ms": end_ms,
            "template_type": scene["template_type"],
            "composition_id": self.get_composition_id(scene["template_type"]),
            "screen_text": self._normalize_screen_text(scene.get("screen_text")),
            "template_props": self.build_template_props(scene),
        }

        if audio_url:
            manifest_scene["audio_url"] = audio_url

        return manifest_scene

    def _normalize_screen_text(self, value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(item) for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return []

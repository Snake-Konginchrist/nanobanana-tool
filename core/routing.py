from __future__ import annotations


RESTORE_HINTS = (
    "restore",
    "repair",
    "enhance",
    "upscale",
    "denoise",
    "scratch",
    "tear",
    "fix",
    "修复",
    "还原",
    "增强",
    "去噪",
    "高清",
    "超分",
    "划痕",
    "破损",
    "老照片",
)
ICON_HINTS = (
    "icon",
    "favicon",
    "logo",
    "app icon",
    "ui element",
    "图标",
    "应用图标",
    "网站图标",
    "logo 设计",
    "ui 图标",
)
PATTERN_HINTS = (
    "pattern",
    "texture",
    "wallpaper",
    "background texture",
    "seamless",
    "图案",
    "纹理",
    "贴图",
    "壁纸",
    "背景纹理",
)
DIAGRAM_HINTS = (
    "diagram",
    "flowchart",
    "architecture",
    "wireframe",
    "mindmap",
    "database schema",
    "network diagram",
    "sequence diagram",
    "流程图",
    "架构图",
    "脑图",
    "思维导图",
    "原型图",
    "时序图",
    "数据库图",
)
STORY_HINTS = (
    "story",
    "timeline",
    "tutorial",
    "step-by-step",
    "sequence",
    "comic",
    "分镜",
    "故事",
    "时间线",
    "教程图",
    "连续画面",
)


def route_natural_language(
    request_text: str,
    file_arg: str | None = None,
) -> tuple[str, dict[str, object]]:
    """按原项目 nanobanana 的职责，只在已有命令之间做选路。"""

    normalized_text = request_text.strip()
    lowered = normalized_text.lower()

    if file_arg and _contains_any(lowered, RESTORE_HINTS):
        return "restore", {"prompt": normalized_text, "file": file_arg}
    if file_arg:
        return "edit", {"prompt": normalized_text, "file": file_arg}
    if _contains_any(lowered, ICON_HINTS):
        return "icon", {"prompt": normalized_text}
    if _contains_any(lowered, PATTERN_HINTS):
        return "pattern", {"prompt": normalized_text}
    if _contains_any(lowered, DIAGRAM_HINTS):
        return "diagram", {"prompt": normalized_text}
    if _contains_any(lowered, STORY_HINTS):
        return "story", {"prompt": normalized_text, "steps": 4}
    return "generate", {"prompt": normalized_text, "count": 1, "format": "separate"}


def _contains_any(lowered_text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in lowered_text for keyword in keywords)

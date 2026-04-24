from __future__ import annotations

from typing import Any

from .models import ImageRequest


def build_icon_prompt(args: dict[str, Any]) -> str:
    """把 icon 参数拼成更适合图像模型的 prompt。"""

    base_prompt = args.get("prompt") or "app icon"
    icon_type = args.get("type") or "app-icon"
    style = args.get("style") or "modern"
    background = args.get("background") or "transparent"
    corners = args.get("corners") or "rounded"

    prompt = f"{base_prompt}, {style} style {icon_type}"
    if icon_type == "app-icon":
        prompt += f", {corners} corners"
    if background != "transparent":
        prompt += f", {background} background"
    prompt += ", clean design, high quality, professional"
    return prompt


def build_pattern_prompt(args: dict[str, Any]) -> str:
    """把 pattern 参数拼成更适合图像模型的 prompt。"""

    base_prompt = args.get("prompt") or "abstract pattern"
    pattern_type = args.get("type") or "seamless"
    style = args.get("style") or "abstract"
    density = args.get("density") or "medium"
    colors = args.get("colors") or "colorful"
    size = args.get("size") or "256x256"

    prompt = (
        f"{base_prompt}, {style} style {pattern_type} pattern, "
        f"{density} density, {colors} colors"
    )
    if pattern_type == "seamless":
        prompt += ", tileable, repeating pattern"
    prompt += f", {size} tile size, high quality"
    return prompt


def build_diagram_prompt(args: dict[str, Any]) -> str:
    """把 diagram 参数拼成更适合图像模型的 prompt。"""

    base_prompt = args.get("prompt") or "system diagram"
    diagram_type = args.get("type") or "flowchart"
    style = args.get("style") or "professional"
    layout = args.get("layout") or "hierarchical"
    complexity = args.get("complexity") or "detailed"
    colors = args.get("colors") or "accent"
    annotations = args.get("annotations") or "detailed"

    prompt = f"{base_prompt}, {diagram_type} diagram, {style} style, {layout} layout"
    prompt += f", {complexity} level of detail, {colors} color scheme"
    prompt += f", {annotations} annotations and labels"
    prompt += ", clean technical illustration, clear visual hierarchy"
    return prompt


def build_batch_prompts(request: ImageRequest) -> list[str]:
    """按 styles / variations / count 生成实际请求列表。"""

    if not request.styles and not request.variations and request.output_count <= 1:
        return [request.prompt]

    prompts = _apply_styles(request.prompt, request.styles)
    prompts = _apply_variations(request.prompt, prompts, request.variations)

    if not prompts and request.output_count > 1:
        prompts = [request.prompt for _ in range(request.output_count)]
    if request.output_count and len(prompts) > request.output_count:
        prompts = prompts[: request.output_count]
    return prompts or [request.prompt]


def build_text_parts(prompt: str, seed: int | None) -> list[dict[str, Any]]:
    """构造 Gemini API 所需的文本 parts。"""

    if seed is None:
        return [{"text": prompt}]
    return [{"text": f"{prompt}\n\nSeed: {seed}"}]


def _apply_styles(base_prompt: str, styles: list[str] | None) -> list[str]:
    if not styles:
        return []
    return [f"{base_prompt}, {style} style" for style in styles]


def _apply_variations(
    base_prompt: str,
    prompts: list[str],
    variations: list[str] | None,
) -> list[str]:
    if not variations:
        return prompts

    base_prompts = prompts[:] if prompts else [base_prompt]
    varied: list[str] = []
    for current in base_prompts:
        for variation in variations:
            varied.extend(_expand_variation(current, variation))
    return varied or prompts


def _expand_variation(base_prompt: str, variation: str) -> list[str]:
    mapping = {
        "lighting": [f"{base_prompt}, dramatic lighting", f"{base_prompt}, soft lighting"],
        "angle": [f"{base_prompt}, from above", f"{base_prompt}, close-up view"],
        "color-palette": [f"{base_prompt}, warm color palette", f"{base_prompt}, cool color palette"],
        "composition": [f"{base_prompt}, centered composition", f"{base_prompt}, rule of thirds composition"],
        "mood": [f"{base_prompt}, cheerful mood", f"{base_prompt}, dramatic mood"],
        "season": [f"{base_prompt}, in spring", f"{base_prompt}, in winter"],
        "time-of-day": [f"{base_prompt}, at sunrise", f"{base_prompt}, at sunset"],
    }
    return mapping.get(variation, [base_prompt])

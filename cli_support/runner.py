from __future__ import annotations

from typing import Any

from ..core.models import ImageRequest
from ..core.prompts import build_diagram_prompt, build_icon_prompt, build_pattern_prompt
from ..core.service import NanoBananaService


def execute_command(
    service: NanoBananaService,
    command: str,
    raw: dict[str, Any],
) -> Any:
    """把 CLI 参数映射为统一的 service 调用。"""

    if command == "generate":
        return service.generate_text_to_image(
            ImageRequest(
                prompt=raw["prompt"],
                output_count=raw["count"],
                mode="generate",
                reference_image=raw.get("reference"),
                output_dir=raw.get("output_dir"),
                output_name=raw.get("output_name"),
                styles=raw.get("styles"),
                variations=raw.get("variations"),
                output_format=raw["format"],
                seed=raw.get("seed"),
                preview=raw.get("preview", False),
            )
        )
    if command in {"edit", "restore"}:
        return service.edit_image(
            ImageRequest(
                prompt=raw["prompt"],
                input_image=raw["file"],
                mode=command,
                output_dir=raw.get("output_dir"),
                output_name=raw.get("output_name"),
                preview=raw.get("preview", False),
            )
        )
    if command == "icon":
        return service.generate_text_to_image(
            ImageRequest(
                prompt=build_icon_prompt(raw),
                output_count=len(raw.get("sizes") or [256]),
                mode="generate",
                reference_image=raw.get("reference"),
                output_dir=raw.get("output_dir"),
                output_name=raw.get("output_name"),
                file_format=raw["format"],
                preview=raw.get("preview", False),
            )
        )
    if command == "pattern":
        return service.generate_text_to_image(
            ImageRequest(
                prompt=build_pattern_prompt(raw),
                output_count=1,
                mode="generate",
                reference_image=raw.get("reference"),
                output_dir=raw.get("output_dir"),
                output_name=raw.get("output_name"),
                preview=raw.get("preview", False),
            )
        )
    if command == "story":
        request = ImageRequest(
            prompt=raw["prompt"],
            output_count=raw["steps"],
            mode="generate",
            reference_image=raw.get("reference"),
            output_dir=raw.get("output_dir"),
            output_name=raw.get("output_name"),
            preview=raw.get("preview", False),
        )
        return service.generate_story_sequence(request, raw)
    if command == "diagram":
        return service.generate_text_to_image(
            ImageRequest(
                prompt=build_diagram_prompt(raw),
                output_count=1,
                mode="generate",
                reference_image=raw.get("reference"),
                output_dir=raw.get("output_dir"),
                output_name=raw.get("output_name"),
                preview=raw.get("preview", False),
            )
        )
    raise ValueError(f"Unsupported command: {command}")


def print_response(response: Any) -> int:
    """统一输出执行结果。"""

    if response.success:
        print(response.message)
        if response.generated_files:
            print()
            print("Generated files:")
            for file_path in response.generated_files:
                print(f"- {file_path}")
        return 0

    print(f"Error: {response.error or response.message}")
    return 1

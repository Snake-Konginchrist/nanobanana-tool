from __future__ import annotations

from dataclasses import dataclass


DEFAULT_MODEL = "gemini-3.1-flash-image-preview"


@dataclass
class ImageRequest:
    """统一承载一次图片任务需要的参数。"""

    prompt: str
    mode: str
    input_image: str | None = None
    reference_image: str | None = None
    output_dir: str | None = None
    output_name: str | None = None
    output_count: int = 1
    styles: list[str] | None = None
    variations: list[str] | None = None
    output_format: str = "separate"
    file_format: str = "png"
    seed: int | None = None
    aspect_ratio: str | None = None
    image_size: str | None = None
    preview: bool = False


@dataclass
class ImageResponse:
    """统一返回执行结果，方便 CLI 层打印。"""

    success: bool
    message: str
    generated_files: list[str]
    error: str | None = None

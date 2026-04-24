from __future__ import annotations

from pathlib import Path
import base64
import mimetypes
import re


OUTPUT_DIR_NAME = "nanobanana-output"
# 兼容原项目常见的输入文件搜索位置。
SEARCH_PATHS = (
    Path.cwd(),
    Path.cwd() / "images",
    Path.cwd() / "input",
    Path.cwd() / OUTPUT_DIR_NAME,
    Path.home() / "Downloads",
    Path.home() / "Desktop",
)


def ensure_output_directory(output_dir: str | Path | None = None) -> Path:
    """确保输出目录存在，并返回目录路径。"""

    resolved = _resolve_output_dir(output_dir)
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def find_input_file(filename: str) -> tuple[Path | None, list[str]]:
    """按原项目习惯搜索输入图片。"""

    candidate = Path(filename).expanduser()
    if candidate.exists():
        return candidate.resolve(), []

    searched = [str(path) for path in SEARCH_PATHS]
    for base in SEARCH_PATHS:
        full_path = (base / filename).expanduser()
        if full_path.exists():
            return full_path, searched

    return None, searched


def generate_filename(
    prompt: str,
    file_format: str = "png",
    index: int = 0,
    output_dir: str | Path | None = None,
) -> str:
    """把 prompt 变成相对友好的输出文件名，并避免重名覆盖。"""

    base_name = re.sub(r"[^a-z0-9\s]", "", prompt.lower())
    base_name = re.sub(r"\s+", "_", base_name).strip("_")[:32]
    if not base_name:
        base_name = "generated_image"

    extension = "jpg" if file_format == "jpeg" else "png"
    output_dir = ensure_output_directory(output_dir)
    filename = f"{base_name}.{extension}"
    counter = index if index > 0 else 1
    while (output_dir / filename).exists():
        filename = f"{base_name}_{counter}.{extension}"
        counter += 1
    return filename


def save_image_from_base64(
    base64_data: str,
    filename: str,
    output_dir: str | Path | None = None,
) -> Path:
    """把 Gemini 返回的 base64 图片写入输出目录。"""

    output_dir = ensure_output_directory(output_dir)
    full_path = output_dir / filename
    full_path.write_bytes(base64.b64decode(base64_data))
    return full_path


def read_image_as_base64(file_path: Path) -> str:
    """把本地图片编码成 base64，供编辑/修复接口上传。"""

    return base64.b64encode(file_path.read_bytes()).decode("utf-8")


def guess_mime_type(file_path: Path) -> str:
    """尽量给上传图片带上正确的 MIME 类型。"""

    mime_type, _ = mimetypes.guess_type(file_path.name)
    return mime_type or "image/png"


def _resolve_output_dir(output_dir: str | Path | None) -> Path:
    if output_dir is None:
        return Path.cwd() / OUTPUT_DIR_NAME

    resolved = Path(output_dir).expanduser()
    if not resolved.is_absolute():
        resolved = Path.cwd() / resolved
    return resolved

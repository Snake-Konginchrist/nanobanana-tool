from __future__ import annotations

import base64
import subprocess
import sys
from typing import Any

from ..io.file_handler import (
    find_input_file,
    generate_filename,
    guess_mime_type,
    read_image_as_base64,
    save_image_from_base64,
)
from ..io.gemini_client import GeminiImageClient
from .models import DEFAULT_MODEL, ImageRequest, ImageResponse
from .prompts import build_batch_prompts, build_text_parts
from .routing import route_natural_language


class NanoBananaService:
    """封装与 Gemini 图像接口交互的核心流程。"""

    def __init__(self, client: GeminiImageClient) -> None:
        self.client = client

    @classmethod
    def from_environment(cls, api_key: str) -> "NanoBananaService":
        import os

        model_name = os.environ.get("NANOBANANA_MODEL", DEFAULT_MODEL)
        return cls(GeminiImageClient(api_key=api_key, model_name=model_name))

    def route_natural_language(
        self,
        request_text: str,
        file_arg: str | None = None,
    ) -> tuple[str, dict[str, object]]:
        return route_natural_language(request_text, file_arg)

    def generate_text_to_image(self, request: ImageRequest) -> ImageResponse:
        generated_files: list[str] = []
        first_error: str | None = None

        for index, current_prompt in enumerate(build_batch_prompts(request), start=1):
            try:
                response = self.client.generate_content(
                    self._build_generation_parts(current_prompt, request),
                )
                image_data = self._extract_image_base64(response)
                if not image_data:
                    first_error = first_error or "No image data found in response."
                    continue
                base_name = request.output_name or request.prompt
                if (request.styles or request.variations) and not request.output_name:
                    base_name = current_prompt
                filename = generate_filename(
                    base_name,
                    request.file_format,
                    index - 1,
                    request.output_dir,
                )
                generated_files.append(
                    str(save_image_from_base64(image_data, filename, request.output_dir))
                )
            except Exception as error:
                first_error = first_error or str(error)

        self._handle_preview(generated_files, request.preview)
        if not generated_files:
            return ImageResponse(False, "Failed to generate any images.", [], first_error)
        return ImageResponse(
            True,
            f"Successfully generated {len(generated_files)} image variation(s).",
            generated_files,
        )

    def edit_image(self, request: ImageRequest) -> ImageResponse:
        if not request.input_image:
            return ImageResponse(False, "Input image file is required.", [], "Missing input image.")

        input_file, searched_paths = find_input_file(request.input_image)
        if input_file is None:
            error = f"Searched in: {', '.join(searched_paths)}"
            return ImageResponse(False, f"Input image not found: {request.input_image}", [], error)

        image_base64 = read_image_as_base64(input_file)
        mime_type = guess_mime_type(input_file)
        parts = [
            {"text": request.prompt},
            {"inlineData": {"mimeType": mime_type, "data": image_base64}},
        ]

        try:
            response = self.client.generate_content(parts)
            result_image = self._extract_image_base64(response)
            if not result_image:
                return ImageResponse(False, f"Failed to {request.mode} image.", [], "No image data in response.")

            filename = generate_filename(
                request.output_name or f"{request.mode}_{request.prompt}",
                "png",
                0,
                request.output_dir,
            )
            generated = [
                str(save_image_from_base64(result_image, filename, request.output_dir))
            ]
            self._handle_preview(generated, request.preview)
            return ImageResponse(True, f"Successfully {request.mode}d image.", generated)
        except Exception as error:
            return ImageResponse(False, f"Failed to {request.mode} image.", [], str(error))

    def generate_story_sequence(
        self,
        request: ImageRequest,
        args: dict[str, Any],
    ) -> ImageResponse:
        generated_files: list[str] = []
        steps = request.output_count
        first_error: str | None = None

        for step_number in range(1, steps + 1):
            step_prompt = _build_story_step_prompt(request.prompt, step_number, steps, args)
            try:
                response = self.client.generate_content(
                    self._build_generation_parts(step_prompt, request),
                )
                image_data = self._extract_image_base64(response)
                if not image_data:
                    first_error = first_error or "No image data found in response."
                    continue
                filename = generate_filename(
                    request.output_name or f"story_step_{step_number}_{request.prompt}",
                    "png",
                    step_number - 1,
                    request.output_dir,
                )
                generated_files.append(
                    str(save_image_from_base64(image_data, filename, request.output_dir))
                )
            except Exception as error:
                first_error = first_error or str(error)

        self._handle_preview(generated_files, request.preview)
        if not generated_files:
            return ImageResponse(False, "Failed to generate any story sequence images.", [], first_error)
        return ImageResponse(True, _build_story_message(len(generated_files), steps, args), generated_files)

    def _extract_image_base64(self, response: dict[str, Any]) -> str | None:
        candidates = response.get("candidates") or []
        if not candidates:
            return None
        content = candidates[0].get("content") or {}
        for part in content.get("parts") or []:
            inline_data = part.get("inlineData") or {}
            if inline_data.get("data"):
                return inline_data["data"]
            text = part.get("text")
            if isinstance(text, str) and _is_valid_base64_image_data(text):
                return text
        return None

    def _handle_preview(self, files: list[str], preview: bool) -> None:
        if not preview:
            return
        for file_path in files:
            _open_image_preview(file_path)

    def _build_generation_parts(
        self,
        prompt: str,
        request: ImageRequest,
    ) -> list[dict[str, Any]]:
        parts = build_text_parts(prompt, request.seed)
        if not request.reference_image:
            return parts

        reference_file, searched_paths = find_input_file(request.reference_image)
        if reference_file is None:
            searched = ", ".join(searched_paths)
            raise FileNotFoundError(
                f"Reference image not found: {request.reference_image}. Searched in: {searched}"
            )

        parts.append(
            {
                "inlineData": {
                    "mimeType": guess_mime_type(reference_file),
                    "data": read_image_as_base64(reference_file),
                }
            }
        )
        return parts


def _build_story_step_prompt(
    prompt: str,
    step_number: int,
    total_steps: int,
    args: dict[str, Any],
) -> str:
    sequence_type = args.get("type", "story")
    style = args.get("style", "consistent")
    transition = args.get("transition", "smooth")
    step_prompt = f"{prompt}, step {step_number} of {total_steps}"

    if sequence_type == "story":
        step_prompt += f", narrative sequence, {style} art style"
    elif sequence_type == "process":
        step_prompt += ", procedural step, instructional illustration"
    elif sequence_type == "tutorial":
        step_prompt += ", tutorial step, educational diagram"
    elif sequence_type == "timeline":
        step_prompt += ", chronological progression, timeline visualization"
    if step_number > 1:
        step_prompt += f", {transition} transition from previous step"
    return step_prompt


def _build_story_message(done_steps: int, total_steps: int, args: dict[str, Any]) -> str:
    sequence_type = args.get("type", "story")
    if done_steps == total_steps:
        return f"Successfully generated complete {total_steps}-step {sequence_type} sequence."
    missing = total_steps - done_steps
    return (
        f"Generated {done_steps} out of {total_steps} requested "
        f"{sequence_type} steps ({missing} steps failed)."
    )


def _is_valid_base64_image_data(data: str) -> bool:
    if not data or len(data) < 1000:
        return False
    try:
        base64.b64decode(data, validate=True)
    except Exception:
        return False
    return True


def _open_image_preview(file_path: str) -> None:
    if sys.platform == "darwin":
        command = ["open", file_path]
    elif sys.platform.startswith("win"):
        command = ["cmd", "/c", "start", "", file_path]
    else:
        command = ["xdg-open", file_path]
    try:
        subprocess.Popen(command)
    except OSError:
        pass

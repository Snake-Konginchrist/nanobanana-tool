from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


DEFAULT_API_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent?key={api_key}"
)


class GeminiClientError(RuntimeError):
    """统一封装 Gemini 接口错误。"""

    pass


@dataclass(frozen=True)
class AuthConfig:
    api_key: str


def _load_env_file() -> None:
    """自动查找并加载最近的 .env 文件。"""

    cursor = Path.cwd()
    for parent in [cursor] + list(cursor.parents):
        env_path = parent / ".env"
        if env_path.exists():
            _parse_and_set_env(env_path)
            return
        env_path = parent / "nanobanana_tool" / ".env"
        if env_path.exists():
            _parse_and_set_env(env_path)
            return


def _parse_and_set_env(env_path: Path) -> None:
    """解析 .env 文件并设置环境变量。"""
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            if key and value:
                os.environ.setdefault(key, value)


def validate_authentication() -> AuthConfig:
    """按原项目的优先级读取 API Key。"""
    _load_env_file()

    for name in (
        "NANOBANANA_API_KEY",
        "NANOBANANA_GEMINI_API_KEY",
        "NANOBANANA_GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
    ):
        value = os.environ.get(name)
        if value:
            return AuthConfig(api_key=value)

    raise GeminiClientError(
        "No API key found. Set NANOBANANA_API_KEY, NANOBANANA_GEMINI_API_KEY, "
        "NANOBANANA_GOOGLE_API_KEY, GEMINI_API_KEY, or GOOGLE_API_KEY."
    )


class GeminiImageClient:
    def __init__(self, api_key: str, model_name: str) -> None:
        self.api_key = api_key
        self.model_name = model_name

    def generate_content(
        self,
        parts: list[dict[str, Any]],
        *,
        aspect_ratio: str | None = None,
        image_size: str | None = None,
    ) -> dict[str, Any]:
        """直接调用 Gemini generateContent 接口。"""

        url = self._resolve_api_endpoint().format(
            model=quote(self.model_name, safe=""),
            api_key=quote(self.api_key, safe=""),
        )
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": parts,
                }
            ]
        }
        image_config = _build_image_config(aspect_ratio, image_size)
        if image_config:
            payload["generationConfig"] = {"imageConfig": image_config}
        request = Request(
            url=url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            raise GeminiClientError(self._format_http_error(error.code, body)) from error
        except URLError as error:
            raise GeminiClientError(f"Failed to reach Gemini API: {error.reason}") from error

    @staticmethod
    def _resolve_api_endpoint() -> str:
        """允许通过环境变量覆盖官方接口地址或代理端点。"""

        proxy_endpoint = os.environ.get("NANOBANANA_PROXY_ENDPOINT")
        if proxy_endpoint:
            return proxy_endpoint

        base_url = os.environ.get("NANOBANANA_API_BASE_URL")
        if base_url:
            return (
                base_url.rstrip("/")
                + "/models/{model}:generateContent?key={api_key}"
            )

        return DEFAULT_API_ENDPOINT

    @staticmethod
    def _format_http_error(status_code: int, body: str) -> str:
        """把常见 HTTP 错误转成更可读的信息。"""

        body_lower = body.lower()
        if "api key not valid" in body_lower:
            return "Authentication failed: invalid API key."
        if "permission denied" in body_lower:
            return "Authentication failed: API key lacks required permissions."
        if "quota" in body_lower and "exceeded" in body_lower:
            return "API quota exceeded."
        if status_code == 400:
            return f"Bad request to Gemini API: {body}"
        if status_code == 403:
            return f"Authentication failed: {body}"
        if status_code >= 500:
            return f"Gemini API temporary server error: {body}"
        return f"Gemini API request failed with status {status_code}: {body}"


def _build_image_config(
    aspect_ratio: str | None,
    image_size: str | None,
) -> dict[str, str] | None:
    image_config: dict[str, str] = {}
    if aspect_ratio:
        image_config["aspectRatio"] = aspect_ratio
    if image_size:
        image_config["imageSize"] = image_size
    return image_config or None

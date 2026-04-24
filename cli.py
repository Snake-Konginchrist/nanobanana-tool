from __future__ import annotations

from .cli_support.parser import build_parser
from .cli_support.runner import execute_command, print_response
from .cli_support.validators import validate_command
from .core.service import NanoBananaService
from .io.gemini_client import GeminiClientError, validate_authentication


def main(argv: list[str] | None = None) -> int:
    """CLI 入口。"""

    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 1

    command = args.command.lstrip("/")
    if command == "nanobanana":
        return _run_natural_language(
            args.request,
            args.file,
            args.reference,
            args.output_dir,
            args.output_name,
            args.preview,
        )
    return _run_structured_command(command, args)


def _run_structured_command(command: str, args: object) -> int:
    validate_command(command, args)
    service = _build_service()
    response = execute_command(service, command, vars(args))
    return print_response(response)


def _run_natural_language(
    request: str,
    file_arg: str | None,
    reference: str | None,
    output_dir: str | None,
    output_name: str | None,
    preview: bool,
) -> int:
    service = _build_service()
    routed_command, routed_args = service.route_natural_language(request, file_arg)
    routed_args["reference"] = reference
    routed_args["output_dir"] = output_dir
    routed_args["output_name"] = output_name
    routed_args["preview"] = preview
    response = execute_command(service, routed_command, routed_args)
    return print_response(response)


def _build_service() -> NanoBananaService:
    try:
        auth = validate_authentication()
    except GeminiClientError as error:
        raise SystemExit(f"Error: {error}") from error
    return NanoBananaService.from_environment(auth.api_key)

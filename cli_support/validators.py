from __future__ import annotations

import argparse


VALID_STYLES = [
    "photorealistic",
    "watercolor",
    "oil-painting",
    "sketch",
    "pixel-art",
    "anime",
    "vintage",
    "modern",
    "abstract",
    "minimalist",
]
VALID_VARIATIONS = [
    "lighting",
    "angle",
    "color-palette",
    "composition",
    "mood",
    "season",
    "time-of-day",
]
VALID_ICON_SIZES = [16, 32, 64, 128, 256, 512, 1024]


def validate_command(command: str, args: argparse.Namespace) -> None:
    validator = COMMAND_VALIDATORS[command]
    validator(args)


def validate_generate(args: argparse.Namespace) -> None:
    if not 1 <= args.count <= 8:
        raise SystemExit("Error: --count must be between 1 and 8.")
    _ensure_valid_subset(args.styles, VALID_STYLES, "--styles")
    _ensure_valid_subset(args.variations, VALID_VARIATIONS, "--variations")


def validate_edit(_: argparse.Namespace) -> None:
    return


def validate_restore(_: argparse.Namespace) -> None:
    return


def validate_icon(args: argparse.Namespace) -> None:
    if args.sizes is None:
        return
    invalid = [size for size in args.sizes if size not in VALID_ICON_SIZES]
    if invalid:
        raise SystemExit(
            f"Error: invalid --sizes values: {invalid}. Valid sizes: {VALID_ICON_SIZES}."
        )


def validate_pattern(args: argparse.Namespace) -> None:
    if "x" not in args.size.lower():
        raise SystemExit("Error: --size must look like 256x256.")


def validate_story(args: argparse.Namespace) -> None:
    if not 2 <= args.steps <= 8:
        raise SystemExit("Error: --steps must be between 2 and 8.")


def validate_diagram(_: argparse.Namespace) -> None:
    return


COMMAND_VALIDATORS = {
    "generate": validate_generate,
    "edit": validate_edit,
    "restore": validate_restore,
    "icon": validate_icon,
    "pattern": validate_pattern,
    "story": validate_story,
    "diagram": validate_diagram,
}


def _ensure_valid_subset(values: list[str] | None, allowed: list[str], option_name: str) -> None:
    if not values:
        return
    invalid = [value for value in values if value not in allowed]
    if invalid:
        raise SystemExit(
            f"Error: invalid {option_name} values: {invalid}. Valid values: {allowed}."
        )

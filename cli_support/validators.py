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
VALID_ASPECT_RATIOS = [
    "1:1",
    "1:4",
    "4:1",
    "1:8",
    "8:1",
    "2:3",
    "3:2",
    "3:4",
    "4:3",
    "4:5",
    "5:4",
    "9:16",
    "16:9",
    "21:9",
]
VALID_IMAGE_SIZES = ["512", "1K", "2K", "4K"]


def validate_command(command: str, args: argparse.Namespace) -> None:
    validator = COMMAND_VALIDATORS[command]
    validator(args)


def validate_generate(args: argparse.Namespace) -> None:
    if not 1 <= args.count <= 8:
        raise SystemExit("Error: --count must be between 1 and 8.")
    _ensure_valid_subset(args.styles, VALID_STYLES, "--styles")
    _ensure_valid_subset(args.variations, VALID_VARIATIONS, "--variations")
    _validate_image_config(args)


def validate_edit(args: argparse.Namespace) -> None:
    _validate_image_config(args)


def validate_restore(args: argparse.Namespace) -> None:
    _validate_image_config(args)


def validate_icon(args: argparse.Namespace) -> None:
    if args.sizes is None:
        _validate_image_config(args)
        return
    invalid = [size for size in args.sizes if size not in VALID_ICON_SIZES]
    if invalid:
        raise SystemExit(
            f"Error: invalid --sizes values: {invalid}. Valid sizes: {VALID_ICON_SIZES}."
        )
    _validate_image_config(args)


def validate_pattern(args: argparse.Namespace) -> None:
    if "x" not in args.size.lower():
        raise SystemExit("Error: --size must look like 256x256.")
    _validate_image_config(args)


def validate_story(args: argparse.Namespace) -> None:
    if not 2 <= args.steps <= 8:
        raise SystemExit("Error: --steps must be between 2 and 8.")
    _validate_image_config(args)


def validate_diagram(args: argparse.Namespace) -> None:
    _validate_image_config(args)


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


def _validate_image_config(args: argparse.Namespace) -> None:
    if getattr(args, "aspect_ratio", None) not in (None, *VALID_ASPECT_RATIOS):
        raise SystemExit(
            "Error: invalid --aspect value: "
            f"{args.aspect_ratio}. Valid values: {VALID_ASPECT_RATIOS}."
        )
    if getattr(args, "image_size", None) not in (None, *VALID_IMAGE_SIZES):
        raise SystemExit(
            "Error: invalid --image-size value: "
            f"{args.image_size}. Valid values: {VALID_IMAGE_SIZES}."
        )

from __future__ import annotations

import argparse

from ..meta.command_specs import load_command_specs


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数定义，并复用原项目命令描述。"""

    specs = load_command_specs()
    parser = argparse.ArgumentParser(
        prog="python -m nanobanana_tool",
        description="Standalone Nano Banana-style image tool.",
    )
    subparsers = parser.add_subparsers(dest="command")

    _add_generate_parser(subparsers, specs["generate"].description)
    _add_edit_parser(subparsers, specs["edit"].description)
    _add_restore_parser(subparsers, specs["restore"].description)
    _add_icon_parser(subparsers, specs["icon"].description)
    _add_pattern_parser(subparsers, specs["pattern"].description)
    _add_story_parser(subparsers, specs["story"].description)
    _add_diagram_parser(subparsers, specs["diagram"].description)
    _add_natural_parser(subparsers, specs["nanobanana"].description)

    for alias in ("/generate", "/edit", "/restore", "/icon", "/pattern", "/story", "/diagram", "/nanobanana"):
        subparsers.add_parser(alias, add_help=False, parents=[subparsers.choices[alias[1:]]])
    return parser


def parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_sizes(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def _add_generate_parser(subparsers: argparse._SubParsersAction, help_text: str) -> None:
    parser = subparsers.add_parser("generate", help=help_text)
    parser.add_argument("prompt")
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--styles", type=parse_csv)
    parser.add_argument("--variations", type=parse_csv)
    parser.add_argument("--reference")
    parser.add_argument("--output-dir")
    parser.add_argument("--output-name")
    parser.add_argument("--format", choices=["grid", "separate"], default="separate")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--preview", action="store_true")


def _add_edit_parser(subparsers: argparse._SubParsersAction, help_text: str) -> None:
    parser = subparsers.add_parser("edit", help=help_text)
    parser.add_argument("file")
    parser.add_argument("prompt")
    parser.add_argument("--output-dir")
    parser.add_argument("--output-name")
    parser.add_argument("--preview", action="store_true")


def _add_restore_parser(subparsers: argparse._SubParsersAction, help_text: str) -> None:
    parser = subparsers.add_parser("restore", help=help_text)
    parser.add_argument("file")
    parser.add_argument("prompt")
    parser.add_argument("--output-dir")
    parser.add_argument("--output-name")
    parser.add_argument("--preview", action="store_true")


def _add_icon_parser(subparsers: argparse._SubParsersAction, help_text: str) -> None:
    parser = subparsers.add_parser("icon", help=help_text)
    parser.add_argument("prompt")
    parser.add_argument("--sizes", type=parse_sizes)
    parser.add_argument("--reference")
    parser.add_argument("--output-dir")
    parser.add_argument("--output-name")
    parser.add_argument("--type", choices=["app-icon", "favicon", "ui-element"], default="app-icon")
    parser.add_argument("--style", choices=["flat", "skeuomorphic", "minimal", "modern"], default="modern")
    parser.add_argument("--format", choices=["png", "jpeg"], default="png")
    parser.add_argument("--background", default="transparent")
    parser.add_argument("--corners", choices=["rounded", "sharp"], default="rounded")
    parser.add_argument("--preview", action="store_true")


def _add_pattern_parser(subparsers: argparse._SubParsersAction, help_text: str) -> None:
    parser = subparsers.add_parser("pattern", help=help_text)
    parser.add_argument("prompt")
    parser.add_argument("--reference")
    parser.add_argument("--output-dir")
    parser.add_argument("--output-name")
    parser.add_argument("--size", default="256x256")
    parser.add_argument("--type", choices=["seamless", "texture", "wallpaper"], default="seamless")
    parser.add_argument("--style", choices=["geometric", "organic", "abstract", "floral", "tech"], default="abstract")
    parser.add_argument("--density", choices=["sparse", "medium", "dense"], default="medium")
    parser.add_argument("--colors", choices=["mono", "duotone", "colorful"], default="colorful")
    parser.add_argument("--repeat", choices=["tile", "mirror"], default="tile")
    parser.add_argument("--preview", action="store_true")


def _add_story_parser(subparsers: argparse._SubParsersAction, help_text: str) -> None:
    parser = subparsers.add_parser("story", help=help_text)
    parser.add_argument("prompt")
    parser.add_argument("--reference")
    parser.add_argument("--output-dir")
    parser.add_argument("--output-name")
    parser.add_argument("--steps", type=int, default=4)
    parser.add_argument("--type", choices=["story", "process", "tutorial", "timeline"], default="story")
    parser.add_argument("--style", choices=["consistent", "evolving"], default="consistent")
    parser.add_argument("--layout", choices=["separate", "grid", "comic"], default="separate")
    parser.add_argument("--transition", choices=["smooth", "dramatic", "fade"], default="smooth")
    parser.add_argument("--format", choices=["storyboard", "individual"], default="individual")
    parser.add_argument("--preview", action="store_true")


def _add_diagram_parser(subparsers: argparse._SubParsersAction, help_text: str) -> None:
    parser = subparsers.add_parser("diagram", help=help_text)
    parser.add_argument("prompt")
    parser.add_argument("--reference")
    parser.add_argument("--output-dir")
    parser.add_argument("--output-name")
    parser.add_argument("--type", choices=["flowchart", "architecture", "network", "database", "wireframe", "mindmap", "sequence"], default="flowchart")
    parser.add_argument("--style", choices=["professional", "clean", "hand-drawn", "technical"], default="professional")
    parser.add_argument("--layout", choices=["horizontal", "vertical", "hierarchical", "circular"], default="hierarchical")
    parser.add_argument("--complexity", choices=["simple", "detailed", "comprehensive"], default="detailed")
    parser.add_argument("--colors", choices=["mono", "accent", "categorical"], default="accent")
    parser.add_argument("--annotations", choices=["minimal", "detailed"], default="detailed")
    parser.add_argument("--preview", action="store_true")


def _add_natural_parser(subparsers: argparse._SubParsersAction, help_text: str) -> None:
    parser = subparsers.add_parser("nanobanana", help=help_text)
    parser.add_argument("request")
    parser.add_argument("--file")
    parser.add_argument("--reference")
    parser.add_argument("--output-dir")
    parser.add_argument("--output-name")
    parser.add_argument("--preview", action="store_true")

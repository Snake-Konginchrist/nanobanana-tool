from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parent.parent.parent
COMMANDS_DIR = ROOT / "nanobanana" / "commands"


@dataclass(frozen=True)
class CommandSpec:
    """保存命令名和说明，供 CLI 帮助信息复用。"""

    name: str
    description: str


def load_command_specs() -> dict[str, CommandSpec]:
    """读取原项目 commands 目录下的 toml 描述。"""

    specs: dict[str, CommandSpec] = {}
    for path in sorted(COMMANDS_DIR.glob("*.toml")):
        with path.open("rb") as handle:
            data = tomllib.load(handle)
        specs[path.stem] = CommandSpec(
            name=path.stem,
            description=data.get("description", path.stem),
        )
    return specs

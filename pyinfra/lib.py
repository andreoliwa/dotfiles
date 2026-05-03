"""Shared pyinfra utilities: task discovery and extra-tasks-dirs parsing."""

import ast
import os
from dataclasses import dataclass
from pathlib import Path

# Root of the dotfiles repo — derived from this file's location.
# Cannot import DOTFILES_PATH from src/dotf/ops.py: pyinfra tasks run under the
# pyinfra CLI in a separate process with no dotf package on sys.path.
DOTFILES_PATH = Path(__file__).parent.parent


@dataclass
class TasksDir:
    """Tasks directory and its properties."""

    # Callers must pass absolute paths via DOTF_EXTRA_TASKS_DIRS.
    absolute_path: Path
    # Label appended to symlink names to avoid collisions across repos.
    # Empty string for the primary dotfiles repo (no suffix).
    label: str


def parse_extra_tasks_dirs() -> list[TasksDir]:
    """Parse DOTF_EXTRA_TASKS_DIRS env var into a list of TasksDir."""
    extra = os.environ.get("DOTF_EXTRA_TASKS_DIRS", "")
    return [TasksDir(absolute_path=Path(p), label=Path(p).parent.parent.name) for p in extra.split(":") if p]


def discover_tasks(tasks_dir: Path, extra_dirs: list[TasksDir]) -> dict[str, Path]:
    """Return mapping of tool name → absolute .py path.

    Tool name is the file stem (e.g. "mise", "pipx").
    Excludes __init__.py and shell.py (shell.py is the entry point, not a tool).
    When the same stem appears in both dotfiles and an extra dir,
    the extra dir wins (private override).
    """
    excluded = {"__init__"}
    result: dict[str, Path] = {}

    # dotfiles tasks first (lower priority)
    for py_file in sorted(tasks_dir.glob("*/*.py")):
        if py_file.stem not in excluded:
            result[py_file.stem] = py_file.resolve()

    # extra dirs second (higher priority — override dotfiles)
    for tasks in extra_dirs:
        if not tasks.absolute_path.is_dir():
            continue
        for py_file in sorted(tasks.absolute_path.glob("*/*.py")):
            if py_file.stem not in excluded:
                result[py_file.stem] = py_file.resolve()

    return result


def filter_tasks(all_tasks: dict[str, Path], tools: list[str]) -> dict[str, Path]:
    """Return only the tasks whose names appear in *tools*, preserving order.

    ``shell`` is excluded because it is handled separately by the entry point.
    Unknown tool names (not in *all_tasks*) are silently skipped here; callers
    are responsible for warning about them if desired.
    """
    return {name: all_tasks[name] for name in tools if name in all_tasks}


def read_module_docstring(py_file: Path) -> str:
    """Extract module-level docstring from a .py file without importing it."""
    try:
        tree = ast.parse(py_file.read_text())
        return ast.get_docstring(tree) or ""
    except (SyntaxError, OSError):
        return ""

"""Deploy shell.d fragments to ~/.config/shell.d/."""

import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from pyinfra.connectors.local import LocalConnector
from pyinfra.operations import files

from pyinfra import host


@dataclass
class TasksDir:
    """Tasks directory and its properties."""

    # Callers must pass absolute paths via DOTF_EXTRA_TASKS_DIRS.
    absolute_path: Path
    # Label appended to symlink names to avoid collisions across repos.
    # Empty string for the primary dotfiles repo (no suffix).
    label: str


# Shell fragments live alongside their tool's Python code under tasks/<tool>/
TASKS_DIR = Path(__file__).parent

# DOTF_EXTRA_TASKS_DIRS: colon-separated absolute paths to extra tasks directories.
_extra = os.environ.get("DOTF_EXTRA_TASKS_DIRS", "")
EXTRA_TASKS_DIRS: list[TasksDir] = [
    TasksDir(absolute_path=Path(p), label=Path(p).parent.parent.name) for p in _extra.split(":") if p
]

SHELL_D = str(Path.home() / ".config" / "shell.d")


def _symlink_name(fragment: Path, repo_label: str) -> str:
    """Build collision-safe symlink name: {stem}-{task}[-{repo}].sh.

    Example:
        tasks/git/40-alias.sh (dotfiles)        → 40-alias-git.sh
        my-private-repo/pyinfra/tasks/git/40-alias.sh    → 40-alias-git-my-private-repo.sh
    """
    task = fragment.parent.name
    suffix = f"-{repo_label}" if repo_label else ""
    return f"{fragment.stem}-{task}{suffix}.sh"


def assemble_shell_d(use_symlinks: bool) -> str:
    """Glob tasks/**/*.sh, populate temp dir sorted by filename for load order.

    On local hosts, creates symlinks so edits to the originals take effect
    immediately in new shells without re-running dotf.
    On remote hosts, copies files.
    """
    tmp_dir = tempfile.mkdtemp(prefix="shell_d_")

    all_dirs = [TasksDir(absolute_path=TASKS_DIR, label=""), *EXTRA_TASKS_DIRS]
    for tasks_dir in all_dirs:
        if not tasks_dir.absolute_path.is_dir():
            continue
        fragments = sorted(tasks_dir.absolute_path.rglob("*.sh"), key=lambda p: p.name)
        for fragment in fragments:
            dest = os.path.join(tmp_dir, _symlink_name(fragment, tasks_dir.label))
            if use_symlinks:
                os.symlink(fragment.resolve(), dest)
            else:
                shutil.copy2(fragment, dest)

    return tmp_dir


assembled = assemble_shell_d(use_symlinks=isinstance(host.connector, LocalConnector))

files.directory(
    name="Reset ~/.config/shell.d",
    path=SHELL_D,
    present=False,
)

files.directory(
    name="Ensure ~/.config/shell.d exists",
    path=SHELL_D,
    present=True,
)

files.sync(
    name="Sync shell.d fragments (delete orphans)",
    src=assembled,
    dest=SHELL_D,
    delete=True,
)

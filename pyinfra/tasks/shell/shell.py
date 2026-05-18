"""Deploy shell.d fragments to ~/.config/shell.d/."""

import shutil
import sys
import tempfile
from pathlib import Path

from pyinfra.connectors.local import LocalConnector
from pyinfra.facts.server import Home
from pyinfra.operations import files

from pyinfra import host

# lib.py lives one level up from tasks/ — add its directory to sys.path so it
# can be imported regardless of the working directory pyinfra was launched from.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib import TasksDir, parse_extra_tasks_dirs

# Shell fragments live alongside their tool's Python code under tasks/<tool>/
TASKS_DIR = Path(__file__).parent.parent

EXTRA_TASKS_DIRS: list[TasksDir] = parse_extra_tasks_dirs()

# Use the remote Home fact, not Path.home() — Path.home() resolves on the control machine
# and would deploy to the wrong path on remote hosts. Tilde strings don't work either
# because pyinfra passes them quoted to the shell, suppressing expansion.
SHELL_D = str(Path(host.get_fact(Home)) / ".config" / "shell.d")


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
        # Only pick up fragments named NN-*.sh (two leading digits + dash).
        # Convention doubles as a load-order prefix and prevents accidental
        # globbing of helper scripts like brew/askpass.sh.
        fragments = sorted(
            (p for p in tasks_dir.absolute_path.rglob("[0-9][0-9]-*.sh")),
            key=lambda p: p.name,
        )
        for fragment in fragments:
            dest = Path(tmp_dir) / _symlink_name(fragment, tasks_dir.label)
            if use_symlinks:
                dest.symlink_to(fragment.resolve())
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

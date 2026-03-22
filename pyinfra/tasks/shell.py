"""Deploy shell.d fragments to ~/.config/shell.d/."""

import os
import shutil
import tempfile
from pathlib import Path

from pyinfra.operations import files

# Shell fragments live alongside their tool's Python code under tasks/<tool>/
TASKS_DIR = Path(__file__).parent

# Optional extra tasks directories. Callers set DOTF_EXTRA_TASKS_DIRS env var (colon-separated paths).
_extra = os.environ.get("DOTF_EXTRA_TASKS_DIRS", "")
EXTRA_TASKS_DIRS: list[Path] = [Path(p) for p in _extra.split(":") if p]

SHELL_D = str(Path.home() / ".config" / "shell.d")


def assemble_shell_d() -> str:
    """Glob tasks/**/*.sh, copy to temp dir sorted by filename for load order."""
    tmp_dir = tempfile.mkdtemp(prefix="shell_d_")

    for tasks_dir in [TASKS_DIR, *EXTRA_TASKS_DIRS]:
        if not tasks_dir.is_dir():
            continue
        # Sort by filename (not full path) so numeric prefixes control load order
        # regardless of which subdirectory a fragment lives in.
        fragments = sorted(tasks_dir.rglob("*.sh"), key=lambda p: p.name)
        for fragment in fragments:
            shutil.copy2(fragment, os.path.join(tmp_dir, fragment.name))

    return tmp_dir


assembled = assemble_shell_d()

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

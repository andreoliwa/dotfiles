"""dotf ops — subprocess and path operations, no CLI framework."""

import os
import subprocess
from pathlib import Path

DOTFILES = Path.home() / "dotfiles"

_ENV_DOTF_REPO = "DOTF_REPO"


def run(cmd: list[str], **kwargs: object) -> int:
    """Print and execute a shell command, returning its exit code."""
    print(f"→ {' '.join(cmd)}")
    return subprocess.call(cmd, **kwargs)  # type: ignore[arg-type]  # noqa: S603


def _private_pyinfra(private_repo: Path | None) -> Path | None:
    """Return the private pyinfra directory if it exists, else None."""
    if private_repo is not None:
        candidate = private_repo / "pyinfra"
        return candidate if candidate.is_dir() else None
    env_val = os.environ.get(_ENV_DOTF_REPO)
    if env_val:
        candidate = Path(env_val).expanduser().resolve() / "pyinfra"
        return candidate if candidate.is_dir() else None
    return None


def _chezmoi_apply_source(source: Path) -> None:
    """Apply a single chezmoi source dir, then offer merge-all if MM conflicts exist."""
    run(["chezmoi", "apply", "--verbose", "--source", str(source)])
    status = subprocess.check_output(["chezmoi", "status", "--source", str(source)], text=True)  # noqa: S603 S607
    mm_files = [line for line in status.splitlines() if line[:2] == "MM"]
    if not mm_files:
        return
    print("Files modified in both source and destination:")
    for line in mm_files:
        print(f"  {line}")
    answer = input("Run 'chezmoi merge-all' for this source? [y/N] ").strip()
    if answer.lower() in {"y", "yes"}:
        run(["chezmoi", "merge-all", "--source", str(source)])


def apply_chezmoi(private_repo: Path | None) -> None:
    """Apply chezmoi from the public source, then private source if available."""
    _chezmoi_apply_source(DOTFILES / "chezmoi")
    # Resolve private repo: explicit arg > $DOTF_REPO env var
    if private_repo is None:
        env_val = os.environ.get(_ENV_DOTF_REPO)
        if env_val:
            private_repo = Path(env_val).expanduser().resolve()
    if private_repo is not None:
        private_chezmoi = private_repo / "chezmoi"
        if private_chezmoi.is_dir():
            _chezmoi_apply_source(private_chezmoi)


def apply_pyinfra(
    private_pyinfra: Path | None,
    server: str,
    tools: list[str] | None,
) -> None:
    """Run pyinfra from the first directory that has both inventory.py and deploy.py.

    Searches private repo first, falls back to the public dotfiles pyinfra dir.
    """
    candidates = [private_pyinfra, DOTFILES / "pyinfra"] if private_pyinfra else [DOTFILES / "pyinfra"]
    workdir = next(
        (d for d in candidates if d is not None and (d / "inventory.py").exists() and (d / "deploy.py").exists()),
        None,
    )
    if workdir is None:
        print("Error: no inventory.py + deploy.py found in private or public pyinfra dir")
        raise SystemExit(1)
    extra: list[str] = ["--limit", server]
    if tools:
        extra += ["--data", f"tools={','.join(tools)}"]
    run(["pyinfra", "inventory.py", "deploy.py", *extra], cwd=str(workdir))

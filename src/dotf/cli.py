"""dotf CLI — Typer subcommand wiring."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003
from typing import Annotated

import typer

from dotf.ops import _private_pyinfra, apply_chezmoi, apply_pyinfra

app = typer.Typer(help="Dotfiles provisioning wrapper.", no_args_is_help=True)


@app.command()
def apply(
    server: Annotated[
        str, typer.Option("-s", "--server", metavar="SERVER", help="Target server (default: @local).")
    ] = "@local",
    tools: Annotated[
        str | None,
        typer.Option(
            "-t", "--tools", metavar="TOOL[,TOOL...]", help="Comma-separated tools to provision (default: all)."
        ),
    ] = None,
    repo: Annotated[
        Path | None, typer.Option("-r", "--repo", metavar="PATH", help="Path to private repo root.")
    ] = None,
) -> None:
    """Apply chezmoi + pyinfra (full provisioning)."""
    tools_list: list[str] | None = [t for t in (s.strip() for s in tools.split(",")) if t] if tools else None
    private_pyinfra = _private_pyinfra(repo)
    apply_chezmoi(repo)
    apply_pyinfra(private_pyinfra, server, tools_list)


@app.command()
def chezmoi(
    repo: Annotated[
        Path | None, typer.Option("-r", "--repo", metavar="PATH", help="Path to private repo root.")
    ] = None,
) -> None:
    """Apply chezmoi only (skip pyinfra)."""
    apply_chezmoi(repo)


if __name__ == "__main__":
    app()

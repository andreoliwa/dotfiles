"""dotf CLI — Typer subcommand wiring."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

import typer

from dotf.ops import (
    _chezmoi_remote_diff,
    _print_green,
    _print_yellow,
    _private_pyinfra,
    apply_chezmoi,
    apply_pyinfra,
    list_provision,
    resolve_server,
)

app = typer.Typer(
    help="Dotfiles provisioning wrapper.",
    no_args_is_help=True,
    rich_markup_mode=None,
    pretty_exceptions_enable=False,
)


@app.callback()
def main(
    debug: Annotated[bool, typer.Option("--debug", "-d", help="Enable debug output (passes -v to pyinfra).")] = False,
    yes: Annotated[bool, typer.Option("-y", "--yes", help="Skip all confirmation prompts.")] = False,
) -> None:
    """Dotfiles provisioning wrapper."""
    if debug:
        os.environ["DOTF_DEBUG"] = "1"
    if yes:
        os.environ["DOTF_YES"] = "1"


def _yes() -> bool:
    return bool(os.environ.get("DOTF_YES"))


def _provision_impl(
    server: str,
    tools: str | None,
    start_from: str | None,
    repo: Path | None,
) -> None:
    tools_list: list[str] | None = [t for t in (s.strip() for s in tools.split(",")) if t] if tools else None
    if tools_list:
        from dotf.ops import resolve_tools

        tools_list = resolve_tools(tools_list, repo)

    resolved_server = resolve_server(server, repo)
    if server != "@local":
        _print_green(f"Server: {resolved_server}")

    if start_from:
        from dotf.ops import _discover_all_tasks, _load_servers

        servers = _load_servers(repo)
        # Match by name first; fall back to host (handles default "@local").
        server_obj = next((s for s in servers if s.name == resolved_server), None)
        if server_obj is None:
            server_obj = next((s for s in servers if s.host == resolved_server), None)
        raw_tools = list(server_obj.tools) if server_obj else (tools_list or [])

        # Use DAG-computed execution order (not raw inventory list, which is
        # alphabetical). Otherwise --start-from slices at the wrong position.
        import sys
        from pathlib import Path as _Path

        from dotf.ops import DOTFILES_PATH as _DOTFILES_PATH

        _pyinfra_lib = _DOTFILES_PATH / "pyinfra"
        if str(_pyinfra_lib) not in sys.path:
            sys.path.insert(0, str(_pyinfra_lib))
        from lib import compute_task_order  # noqa: PLC0415

        all_tasks = _discover_all_tasks(repo)
        ordered, _ = compute_task_order(raw_tools, all_tasks)
        order = [name for name, _tier in ordered]

        if start_from not in order:
            typer.echo(f"--start-from '{start_from}' not in server '{resolved_server}' tools: {order}", err=True)
            raise typer.Exit(1)
        idx = order.index(start_from)
        sliced = order[idx:]
        tools_list = [t for t in tools_list if t in sliced] if tools_list else sliced
        _print_green(f"Starting from: {start_from} (order: {', '.join(sliced)})")

    if tools_list:
        _print_green(f"Tools:  {', '.join(tools_list)}")

    private_pyinfra = _private_pyinfra(repo)

    chezmoi_in_tools = tools_list is None or "chezmoi" in tools_list
    if resolved_server == "@local":
        apply_chezmoi(repo, yes=_yes())
    elif chezmoi_in_tools:
        confirmed = _chezmoi_remote_diff(resolved_server, repo, yes=_yes())
        if not confirmed:
            tools_list = [t for t in (tools_list or []) if t != "chezmoi"]

    _print_yellow("Tip: run `dotf tail` in another terminal to follow server.shell output.")
    apply_pyinfra(private_pyinfra, resolved_server, tools_list, yes=_yes())


@app.command("provision")
def provision(
    tools: Annotated[
        str | None,
        typer.Argument(metavar="TOOL[,TOOL...]", help="Comma-separated tools to provision (default: all)."),
    ] = None,
    server: Annotated[
        str, typer.Option("-s", "--server", metavar="SERVER", help="Target server (default: @local).")
    ] = "@local",
    start_from: Annotated[
        str | None,
        typer.Option(
            "--start-from",
            metavar="TOOL",
            help="Skip tools that come before this one in the server's inventory order.",
        ),
    ] = None,
    repo: Annotated[
        Path | None, typer.Option("-r", "--repo", metavar="PATH", help="Path to private repo root.")
    ] = None,
) -> None:
    """Apply chezmoi + pyinfra (full provisioning)."""
    _provision_impl(server, tools, start_from, repo)


@app.command("list")
@app.command("ls")
def list_cmd(
    repo: Annotated[
        Path | None, typer.Option("-r", "--repo", metavar="PATH", help="Path to private repo root.")
    ] = None,
) -> None:
    """List configured servers and available tools."""
    list_provision(repo)


@app.command()
def chezmoi(
    repo: Annotated[
        Path | None, typer.Option("-r", "--repo", metavar="PATH", help="Path to private repo root.")
    ] = None,
) -> None:
    """Apply chezmoi only (skip pyinfra)."""
    apply_chezmoi(repo, yes=_yes())


@app.command()
def tail() -> None:
    """Follow the pyinfra provisioning log (~/.cache/dotf/provision.log)."""
    import subprocess

    log = Path.home() / ".cache" / "dotf" / "provision.log"
    if not log.exists():
        log.parent.mkdir(parents=True, exist_ok=True)
        log.touch()
    subprocess.run(["tail", "-f", "-n", "50", str(log)], check=False)  # noqa: S603, S607


if __name__ == "__main__":
    app()

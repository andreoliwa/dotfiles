# Copyright 2026

"""dotf CLI — Typer subcommand wiring."""

from __future__ import annotations

import os
import shlex
import subprocess
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer

from dotf.ops import (
    _chezmoi_remote_diff,
    _print_green,
    _print_yellow,
    _private_pyinfra,
    _resolve_ssh_target,
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


def _completion_repo(ctx: typer.Context) -> Path | None:
    """Return the private repository selected for this completion request."""
    repo = ctx.params.get("repo")
    return repo if isinstance(repo, Path) else None


def _complete_servers(ctx: typer.Context, _param: typer.CallbackParam, incomplete: str) -> list[str]:
    """Complete server names and aliases from the current inventory."""
    from dotf.ops import _load_servers

    return [
        candidate
        for server in _load_servers(_completion_repo(ctx))
        for candidate in [server.name, *server.aliases]
        if candidate.startswith(incomplete)
    ]


def _complete_tools(ctx: typer.Context, _param: typer.CallbackParam, incomplete: str) -> list[str]:
    """Complete comma-separated task names from the public and private task directories."""
    from dotf.ops import _discover_all_tasks

    prefix, separator, query = incomplete.rpartition(",")
    completed_prefix = f"{prefix}{separator}"
    return [
        f"{completed_prefix}{name}"
        for name in sorted(_discover_all_tasks(_completion_repo(ctx)))
        if name.startswith(query)
    ]


def _apply_start_from(
    start_from: str,
    resolved_server: str,
    tools_list: list[str] | None,
    repo: Path | None,
) -> list[str]:
    import sys

    from dotf.ops import DOTFILES_PATH as _DOTFILES_PATH
    from dotf.ops import _discover_all_tasks, _load_servers

    servers = _load_servers(repo)
    server_obj = next((s for s in servers if s.name == resolved_server), None)
    if server_obj is None:
        server_obj = next((s for s in servers if s.host == resolved_server), None)
    raw_tools = list(server_obj.tools) if server_obj else (tools_list or [])

    # Use DAG-computed execution order (not raw inventory list, which is
    # alphabetical). Otherwise --start-from slices at the wrong position.
    _pyinfra_lib = _DOTFILES_PATH / "pyinfra"
    if str(_pyinfra_lib) not in sys.path:
        sys.path.insert(0, str(_pyinfra_lib))
    from lib import compute_task_order

    all_tasks = _discover_all_tasks(repo)
    ordered, _ = compute_task_order(raw_tools, all_tasks)
    order = [name for name, _tier in ordered]

    if start_from not in order:
        typer.echo(f"--start-from '{start_from}' not in server '{resolved_server}' tools: {order}", err=True)
        raise typer.Exit(1)
    idx = order.index(start_from)
    sliced = order[idx:]
    result = [t for t in tools_list if t in sliced] if tools_list else sliced
    _print_green(f"Starting from: {start_from} (order: {', '.join(sliced)})")
    return result


def _without_chezmoi(tools: list[str] | None, server: str, repo: Path | None) -> list[str]:
    """Return the requested tools, excluding chezmoi even for a full provision."""
    if tools is not None:
        return [tool for tool in tools if tool != "chezmoi"]

    from dotf.ops import _load_servers

    config = next((item for item in _load_servers(repo) if item.name == server), None)
    return [tool for tool in config.tools if tool != "chezmoi"] if config else []


def _provision_impl(
    server: str,
    tools: list[str] | None,
    start_from: str | None,
    repo: Path | None,
) -> None:
    tools_list = (
        [part for tool in tools for part in (name.strip() for name in tool.split(",")) if part] if tools else None
    )
    if tools_list:
        from dotf.ops import resolve_tools

        tools_list = resolve_tools(tools_list, repo)

    resolved_server = resolve_server(server, repo)
    if server != "@local":
        _print_green(f"Server: {resolved_server}")

    if start_from:
        tools_list = _apply_start_from(start_from, resolved_server, tools_list, repo)

    if tools_list:
        _print_green(f"Tools:  {', '.join(tools_list)}")

    private_pyinfra = _private_pyinfra(repo)

    chezmoi_in_tools = tools_list is None or "chezmoi" in tools_list
    if resolved_server == "@local":
        apply_chezmoi(repo, yes=_yes())
    elif chezmoi_in_tools:
        confirmed = _chezmoi_remote_diff(resolved_server, repo, yes=_yes())
        if not confirmed:
            tools_list = _without_chezmoi(tools_list, resolved_server, repo)

    tip = "dotf watch" if resolved_server == "@local" else f"dotf watch --server {resolved_server}"
    _print_yellow(f"Tip: run `{tip}` in another terminal to follow provisioning progress.")
    apply_pyinfra(private_pyinfra, resolved_server, tools_list, yes=_yes())


@app.command("provision")
def provision(
    tools: Annotated[
        list[str] | None,
        typer.Argument(
            metavar="TOOL...",
            help="Tools to provision, separated by spaces or commas (default: all).",
            shell_complete=_complete_tools,
        ),
    ] = None,
    server: Annotated[
        str,
        typer.Option(
            "-s",
            "--server",
            metavar="SERVER",
            help="Target server (default: @local).",
            shell_complete=_complete_servers,
        ),
    ] = "@local",
    start_from: Annotated[
        str | None,
        typer.Option(
            "-f",
            "--from",
            metavar="TOOL",
            help="Skip tools that come before this one in the server's execution order.",
            shell_complete=_complete_tools,
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


class ProgressView(StrEnum):
    """Provisioning progress display modes."""

    BOTH = "both"
    LOGS = "logs"
    ACTIVITY = "activity"


def _progress_dashboard(view: ProgressView, interval: int) -> str:
    """Return the shell loop for a refreshing progress dashboard."""
    sections = ["while :; do", "  clear", '  printf "Provisioning progress - %s\n" "$(date)"']
    if view != ProgressView.ACTIVITY:
        sections.extend(
            [
                '  printf "\nLogs\n----\n"',
                '  tail -n 25 "$HOME/.cache/dotf/provision.log" 2>/dev/null || true',
            ],
        )
    if view != ProgressView.LOGS:
        sections.extend(
            [
                '  printf "\nActivity\n--------\n"',
                "  uptime",
                "  free -h",
                '  df -h "$HOME"',
                "  top -b -n 1 -o %CPU | head -n 20",
            ],
        )
    sections.extend([f"  sleep {interval}", "done"])
    return "\n".join(sections)


@app.command()
def watch(
    server: Annotated[
        str,
        typer.Option(
            "-s",
            "--server",
            metavar="SERVER",
            help="Target server (default: @local).",
            shell_complete=_complete_servers,
        ),
    ] = "@local",
    view: Annotated[
        ProgressView,
        typer.Option("--view", help="Display both logs and activity, only logs, or only activity."),
    ] = ProgressView.BOTH,
    interval: Annotated[
        int,
        typer.Option("-n", "--interval", min=1, help="Dashboard refresh interval in seconds."),
    ] = 2,
    repo: Annotated[
        Path | None, typer.Option("-r", "--repo", metavar="PATH", help="Path to private repo root.")
    ] = None,
) -> None:
    """Show provisioning logs and activity for a local or remote host."""
    resolved_server = resolve_server(server, repo)
    log = Path.home() / ".cache" / "dotf" / "provision.log"

    if resolved_server == "@local":
        if view == ProgressView.LOGS:
            log.parent.mkdir(parents=True, exist_ok=True)
            log.touch(exist_ok=True)
            subprocess.run(["tail", "-f", "-n", "50", str(log)], check=False)  # noqa: S603, S607
            return
        subprocess.run(["bash", "-c", _progress_dashboard(view, interval)], check=False)  # noqa: S603, S607
        return

    target = _resolve_ssh_target(resolved_server, repo)
    if target is None:
        typer.echo(f"Unknown remote server: {server}", err=True)
        raise typer.Exit(1)
    ssh_target, _ = target
    typer.echo(f"Connecting to {server}...")

    if view == ProgressView.LOGS:
        # ssh_target comes from the configured server, not user-provided shell input.
        subprocess.run(  # noqa: S603
            ["ssh", ssh_target, "tail -f -n 50 ~/.cache/dotf/provision.log"],  # noqa: S607
            check=False,
        )
        return

    # The dashboard clears and redraws the terminal, so the remote command needs a TTY.
    dashboard = _progress_dashboard(view, interval)
    subprocess.run(  # noqa: S603
        ["ssh", "-tt", ssh_target, f"bash -lc {shlex.quote(dashboard)}"],  # noqa: S607
        check=False,
    )


if __name__ == "__main__":
    app()

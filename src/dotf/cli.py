"""dotf CLI — Typer subcommand wiring."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

import typer

from dotf.ops import (
    _SUPPORTED_SHELLS,
    _chezmoi_remote_diff,
    _print_green,
    _private_pyinfra,
    apply_chezmoi,
    apply_pyinfra,
    cache_shell_scripts,
    list_provision,
    resolve_server,
    run_legacy,
)

app = typer.Typer(help="Dotfiles provisioning wrapper.", no_args_is_help=True, rich_markup_mode=None)


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
    repo: Path | None,
) -> None:
    tools_list: list[str] | None = [t for t in (s.strip() for s in tools.split(",")) if t] if tools else None
    if tools_list:
        from dotf.ops import resolve_tools

        tools_list = resolve_tools(tools_list, repo)

    resolved_server = resolve_server(server)
    if server != "@local":
        _print_green(f"Server: {resolved_server}")
    if tools_list:
        _print_green(f"Tools:  {', '.join(tools_list)}")

    private_pyinfra = _private_pyinfra(repo)

    chezmoi_in_tools = tools_list is None or "chezmoi" in tools_list
    if resolved_server == "@local":
        apply_chezmoi(repo, yes=_yes())
    elif chezmoi_in_tools:
        confirmed = _chezmoi_remote_diff(resolved_server, private_pyinfra, repo, yes=_yes())
        if not confirmed:
            tools_list = [t for t in (tools_list or []) if t != "chezmoi"]

    apply_pyinfra(private_pyinfra, resolved_server, tools_list, yes=_yes())


@app.command("provision")
def provision(
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
    _provision_impl(server, tools, repo)


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
def cache(
    debug: Annotated[bool, typer.Option("--debug", "-d", help="Debug mode.")] = False,
) -> None:
    """Regenerate the cached shell-script sourced by .bashrc / .xonshrc.

    The shell is detected automatically from the SHELL environment variable.
    """
    shell_name = Path(os.environ.get("SHELL", "/bin/bash")).name
    if shell_name not in _SUPPORTED_SHELLS:
        typer.echo(f"Unsupported shell: {shell_name}. Supported: {', '.join(sorted(_SUPPORTED_SHELLS))}", err=True)
        raise typer.Exit(1)
    cache_shell_scripts(shell_name, debug=debug)


@app.command()
def legacy(  # noqa: PLR0913
    dry: Annotated[bool, typer.Option("--dry", help="Dry-run mode.")] = False,
    task: Annotated[
        str | None, typer.Option("--task", "-t", metavar="START_AT_TASK", help="Start the playbook at this task.")
    ] = None,
    debug: Annotated[bool, typer.Option("--debug", "-d", help="Debug mode.")] = False,
    galaxy: Annotated[bool, typer.Option("--galaxy", "-g", help="Install Ansible Galaxy roles.")] = False,
    bootstrap: Annotated[bool, typer.Option("--bootstrap", "-b", help="Bootstrap the dev machine.")] = False,
    status: Annotated[bool, typer.Option("--status", "-s", help="Display status of Vagrant VMs.")] = False,
    virtual_machine: Annotated[
        str | None,
        typer.Option("--provision", "-p", metavar="VIRTUAL_MACHINE", help="Provision a Vagrant virtual machine."),
    ] = None,
    reload: Annotated[bool, typer.Option("--reload", "-l", help="Reload the VM.")] = False,
    gui: Annotated[
        bool,
        typer.Option("--gui", "--ui", "-u", help="Start the VM with a GUI."),
    ] = False,
    verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="Verbose mode (-v, -vv, -vvv...).")] = 0,
    sudo: Annotated[bool, typer.Option("--sudo", help="Ask become password.")] = False,
    remote: Annotated[
        str | None,
        typer.Option("--remote", "-r", metavar="TARGET", help="Setup remote server (pi, aws, ocean, hetzner)."),
    ] = None,
    tags: Annotated[list[str] | None, typer.Argument(metavar="TAG", help="Ansible role tags.")] = None,
) -> None:
    """Run the Ansible playbook (legacy dotfiles-setup behaviour)."""
    run_legacy(
        dry=dry,
        task=task,
        debug=debug,
        galaxy=galaxy,
        bootstrap=bootstrap,
        status=status,
        virtual_machine=virtual_machine,
        reload=reload,
        gui=gui,
        verbose=verbose,
        sudo=sudo,
        remote=remote,
        tags=tags,
    )


if __name__ == "__main__":
    app()

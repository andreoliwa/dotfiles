"""dotf CLI — Typer subcommand wiring."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

import typer

from dotf.ops import _SUPPORTED_SHELLS, _private_pyinfra, apply_chezmoi, apply_pyinfra, cache_shell_scripts, run_legacy

app = typer.Typer(help="Dotfiles provisioning wrapper.", no_args_is_help=True, rich_markup_mode=None)


@app.command()
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
    yes: Annotated[bool, typer.Option("-y", "--yes", help="Pass -y to pyinfra, skipping confirmation prompt.")] = False,
) -> None:
    """Apply chezmoi + pyinfra (full provisioning)."""
    tools_list: list[str] | None = [t for t in (s.strip() for s in tools.split(",")) if t] if tools else None
    private_pyinfra = _private_pyinfra(repo)
    apply_chezmoi(repo)
    apply_pyinfra(private_pyinfra, server, tools_list, yes=yes)


@app.command()
def chezmoi(
    repo: Annotated[
        Path | None, typer.Option("-r", "--repo", metavar="PATH", help="Path to private repo root.")
    ] = None,
) -> None:
    """Apply chezmoi only (skip pyinfra)."""
    apply_chezmoi(repo)


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

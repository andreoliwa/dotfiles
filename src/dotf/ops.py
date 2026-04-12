"""dotf ops — subprocess and path operations, no CLI framework."""

import os
import re
import subprocess
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path
from pprint import pprint

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
    *,
    yes: bool = False,
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
    if yes:
        extra.append("-y")
    pyinfra_bin = Path(sys.executable).parent / "pyinfra"
    run([str(pyinfra_bin), "inventory.py", "deploy.py", *extra], cwd=str(workdir))


# ---------------------------------------------------------------------------
# dotf cache — ported from bin/dotfiles-cache-shell-scripts
# ---------------------------------------------------------------------------

CACHE_DIR = Path.home() / ".cache/dotfiles"
CACHED_SCRIPT = CACHE_DIR / "cached_script.sh"

_SUPPORTED_SHELLS = {"bash", "xonsh"}


class _ScriptInfo:
    def __init__(self) -> None:
        self.role = ""
        self.suffixes: set[str] = set()


def _find_shell_files(debug: bool, extensions: list[str]) -> tuple[set[Path], set[Path]]:
    shell_files: set[Path] = set()
    bin_dirs: set[Path] = set()
    for dotfile_role_dir in Path.home().glob("dotfiles*/roles"):
        bin_dirs.add(Path(dotfile_role_dir).parent / "bin")
        for ext in extensions:
            shell_files.update(dotfile_role_dir.glob(f"**/*.{ext}"))
    if debug:
        print("\nShell files:")
        pprint(shell_files)  # noqa: T203
    return shell_files, bin_dirs


def _parse_roles(debug: bool) -> OrderedDict:
    roles: OrderedDict[str, list] = OrderedDict()
    playbook_path = Path("~/dotfiles/playbook_local.yml").expanduser()
    if playbook_path.exists():
        import yaml

        playbook_yml = yaml.safe_load(playbook_path.read_text())
        for item in playbook_yml[0]["roles"]:
            role_name = item["role"]
            roles[role_name] = []
    if debug:
        print("\nRoles:")
        pprint(roles)  # noqa: T203
    return roles


def cache_shell_scripts(shell_name: str, *, debug: bool = False) -> None:
    """Find shell scripts under ~/dotfiles* and write a cached source script."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    extensions = ["xsh", "sh"] if shell_name == "xonsh" else ["sh", "zsh"]

    role_regex = re.compile(r"roles/(?P<role>.+)/")
    content = [f"#!/usr/bin/env {shell_name}"]

    shell_files, bin_dirs = _find_shell_files(debug, extensions)
    roles = _parse_roles(debug)

    mapping: defaultdict[str, _ScriptInfo] = defaultdict(_ScriptInfo)
    for shell_file in sorted(shell_files):
        shell_path = Path(shell_file)
        parent_plus_stem = str(shell_path.parent / shell_path.stem)
        match = role_regex.search(parent_plus_stem)
        role_from_shell_file = match.groupdict().get("role") if match else None
        if role_from_shell_file is not None and role_from_shell_file in roles:
            script_info = mapping[parent_plus_stem]
            script_info.role = role_from_shell_file
            script_info.suffixes.add(shell_path.suffix)
        else:
            content.append(
                f"# Role {role_from_shell_file}: script {shell_file!s}"
                " won't be loaded because the role is not defined in the playbook"
            )

    for parent_stem in sorted(mapping):
        script_partial_path = Path(parent_stem)
        script_info = mapping[parent_stem]
        first_extension = f".{extensions[0]}"
        if first_extension in script_info.suffixes:
            chosen_suffix = first_extension
        else:
            chosen_suffix = sorted(script_info.suffixes).pop()
        script_path = script_partial_path.with_suffix(chosen_suffix)
        roles[script_info.role].append(script_path)

    for chosen_scripts in roles.values():
        for chosen_script in chosen_scripts:
            if chosen_script.name.startswith("_"):
                content.append(f"# Script with _ won't be loaded: {chosen_script}")
                continue
            source_command = "source"
            if shell_name == "xonsh" and not str(chosen_script).endswith(".xsh"):
                source_command = "source-bash --interactive False"
            content.append(f"{source_command} {chosen_script}")

    path_parts = ["export PATH=$PATH"]
    path_parts.extend([str(bin_dir) for bin_dir in bin_dirs])
    content.append(":".join(path_parts))

    CACHED_SCRIPT.write_text("\n".join(content))
    print(f"{CACHED_SCRIPT} created")


# ---------------------------------------------------------------------------
# dotf legacy — ported from bin/dotfiles-setup
# ---------------------------------------------------------------------------


def _notify_legacy(title: str, message: str) -> None:
    check = "which" if sys.platform == "linux" else "command -v"
    try:
        terminal_notifier_path = subprocess.run(  # noqa: S602
            f"{check} terminal-notifier",
            shell=True,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except subprocess.CalledProcessError:
        terminal_notifier_path = ""
    if terminal_notifier_path:
        run(
            [
                "terminal-notifier",
                "-title",
                f"dotf legacy: {title} complete",
                "-message",
                f"Successfully {message} dev environment.",
            ]
        )


def _get_ansible_python() -> str:
    result = subprocess.run(  # noqa: S602
        "ansible --version | grep 'ansible python' |"  # noqa: S607
        r" sed -E -e 's#/site.+##g' -e 's#.+ (/opt)#\1#g' -e 's#.+ (/usr)#\1#g' -e 's#/lib/#/bin/#g'",
        shell=True,
        capture_output=True,
        text=True,
        check=False,
    )
    interpreter = result.stdout.strip().split("\n")[0] if result.stdout.strip() else ""
    print("Using this Python interpreter:", interpreter)
    return interpreter


def run_legacy(  # noqa: C901, PLR0912, PLR0913, PLR0915
    *,
    dry: bool = False,
    task: str | None = None,
    debug: bool = False,
    galaxy: bool = False,
    bootstrap: bool = False,
    status: bool = False,
    virtual_machine: str | None = None,
    reload: bool = False,
    gui: bool = False,
    verbose: int = 0,
    sudo: bool = False,
    remote: str | None = None,
    tags: list[str] | None = None,
) -> None:
    """Run an Ansible playbook to set up a dev machine (legacy dotfiles-setup behaviour)."""

    def _shell(command_line: str, *, quiet: bool = False) -> subprocess.CompletedProcess[str]:
        if not quiet:
            print(f"$ {command_line}")
        return subprocess.run(command_line, shell=True, text=True, check=False)  # noqa: S602

    def _shell_lines(command_line: str, *, quiet: bool = False) -> list[str]:
        if not quiet:
            print(f"$ {command_line}")
        completed = subprocess.run(command_line, shell=True, text=True, check=False, stdout=subprocess.PIPE)  # noqa: S602
        stdout = completed.stdout.strip().strip("\n")
        return stdout.split("\n") if stdout else []

    os.chdir(str(Path.home() / "dotfiles"))
    os.environ["ANSIBLE_ENABLE_TASK_DEBUGGER"] = str(debug)

    if status:
        _shell("vagrant status {}".format(virtual_machine or ""))
        return

    if galaxy:
        print("Installing Galaxy roles...")
        _shell("ansible-galaxy install -r ~/dotfiles/galaxy_roles.yml --roles-path ~/dotfiles/roles_galaxy")

    if gui:
        os.environ["MULTI_DEV_MACHINE_GUI"] = "True"

    verbose_option = " -{}".format("v" * verbose) if verbose else ""
    if verbose_option:
        os.environ["MULTI_DEV_MACHINE_VERBOSE"] = verbose_option.strip()

    tags_with_comma = ",".join(tags) if tags else ""
    tags_option = f" --tags {tags_with_comma}" if tags_with_comma else ""
    if tags_with_comma:
        os.environ["MULTI_DEV_MACHINE_TAGS"] = tags_with_comma

    playbook_file = remote or "local"
    command_parts = ["ansible-playbook"]

    if not remote:
        command_parts.append(f"-e ansible_python_interpreter={_get_ansible_python()}")

    if dry:
        command_parts.append("--check")

    command_parts.extend(
        [
            "--vault-id dotfiles@~/.config/dotfiles/vault_password.txt",
            "--inventory ~/dotfiles/hosts",
            f"~/dotfiles/playbook_{playbook_file}.yml",
        ]
    )

    if task:
        fzf_parts = command_parts.copy()
        fzf_parts.extend(
            [
                "--list-tasks",
                "2>/dev/null",
                "| tail -n +6",
                "| sort | uniq",
                "| fzf --height 50% --reverse --inline-info --select-1 --exit-0 --cycle",
                f"--query={task!r}",
            ]
        )
        selected = _shell_lines(" ".join(fzf_parts), quiet=True)
        if not selected:
            print("No task was chosen")
            raise SystemExit(-1)
        role_task = selected[0].split("\t")[0]
        task_parts = role_task.split(" :", 1)
        chosen_task = task_parts[1].strip() if len(task_parts) > 1 else role_task
        command_parts.append(f"--start-at-task {chosen_task!r}")

    playbook_command = " ".join(command_parts)
    if virtual_machine:
        print(f"Provisioning the Vagrant virtual machine {virtual_machine}...")
        if reload:
            _shell(f"vagrant reload {virtual_machine}")
            up_command = ""
        else:
            result = _shell(f"vagrant status {virtual_machine}")
            lines = result.stdout.strip().split("\n")
            if len(lines) < 3:  # noqa: PLR2004
                return
            up_command = "up --" if " running " not in lines[2] else ""
        _shell(f"vagrant {up_command}provision {virtual_machine}")
        _notify_legacy("Vagrant provision", "provisioned")
    elif bootstrap:
        print(f"Setting up local dev environment...{tags_option}")
        _shell(f"{playbook_command} --ask-become-pass{verbose_option}{tags_option}")
        _notify_legacy("Bootstrap", "set up")
    else:
        ask_password_option = " --ask-become-pass" if sys.platform == "linux" or sudo else ""
        print(f"Updating local dev environment...{tags_option}")
        _shell(f"{playbook_command} --skip-tags 'bootstrap'{verbose_option}{ask_password_option}{tags_option}")
        _notify_legacy("Update", "updated")

"""dotf ops — subprocess and path operations, no CLI framework.

Chezmoi apply — local vs remote split
--------------------------------------
Local apply (macbook/@local):
  _chezmoi_apply_source() in this file — `chezmoi diff` (built-in pager), interactive
  prompt, then apply. No delta dependency.

Remote apply (other servers from the private inventory.py):
  1. _chezmoi_remote_diff() in this file SSHes into the host, runs `chezmoi diff` there,
     pipes the output through local delta (falls back to raw stdout if delta is missing),
     and prompts for confirmation. Delta renders the SSH'd diff nicely on the local Mac;
     the remote host does not need delta installed.
  2. Only if confirmed: apply_pyinfra() runs pyinfra, which includes
     pyinfra/tasks/chezmoi/chezmoi.py — that task archives the local chezmoi source,
     uploads it, and runs `chezmoi apply` unconditionally on the remote.

This file owns all interactive logic (diff preview + prompt) for both local and remote.
pyinfra/tasks/chezmoi/chezmoi.py is intentionally unconditional — it trusts that ops.py
already obtained confirmation before pyinfra was invoked.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib import Server

# Cannot import DOTFILES_PATH from pyinfra/lib.py: pyinfra tasks run in a separate
# process under the pyinfra CLI, which has no knowledge of the dotf package.
DOTFILES_PATH = Path(__file__).parent.parent.parent

# Mirrors lib.LOCAL_HOST — duplicated here to avoid a sys.path import at module level.
# Keep in sync with dotfiles/pyinfra/lib.py.
_LOCAL_HOST = "@local"


def _load_servers(private_repo: Path | None = None) -> "list":
    """Return the Server list, loading from DOTF_SERVERS if set, else from inventory.py.

    DOTF_SERVERS is populated by deploy.py when pyinfra runs. For commands like
    'dotf ls' that run outside pyinfra, we fall back to importing inventory.py directly
    from the private repo so the server list is always current without any manual sync.
    """
    _pyinfra_lib = DOTFILES_PATH / "pyinfra"
    if str(_pyinfra_lib) not in sys.path:
        sys.path.insert(0, str(_pyinfra_lib))
    from lib import Server

    raw = os.environ.get("DOTF_SERVERS", "")
    if raw:
        return Server.decode_all(raw)

    # Fallback: import inventory.py from the private repo directly.
    private_pyinfra = _private_pyinfra(private_repo)
    if private_pyinfra is None:
        return []
    inv_path = private_pyinfra / "inventory.py"
    if not inv_path.exists():
        return []
    import importlib.util

    if str(private_pyinfra) not in sys.path:
        sys.path.insert(0, str(private_pyinfra))
    spec = importlib.util.spec_from_file_location("_inventory", inv_path)
    if spec is None or spec.loader is None:
        return []
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return list(getattr(mod, "_servers", []))


def resolve_server(query: str, private_repo: Path | None = None) -> str:
    """Resolve a server query to a canonical inventory group name.

    Exact match wins. Otherwise, substring-matches against server names and aliases.
    If ambiguous, prompts via iterfzf. Falls back to raw query if no match.
    """
    servers = _load_servers(private_repo)

    if any(s.name == query for s in servers):
        return query

    matches = [s.name for s in servers if any(query in alias for alias in s.aliases) or query in s.name]

    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        from iterfzf import iterfzf

        chosen = iterfzf(iter(matches), prompt=f"Multiple servers match '{query}': ")
        return chosen or query

    return query


def resolve_tools(tokens: list[str], private_repo: Path | None) -> list[str]:
    """Resolve tool name tokens to canonical tool names via iterfzf.

    Exact matches are returned as-is. Partial tokens trigger iterfzf selection.
    """
    import sys

    _pyinfra_lib = DOTFILES_PATH / "pyinfra"
    sys.path.insert(0, str(_pyinfra_lib))
    from lib import TasksDir, discover_tasks

    dotfiles_tasks = DOTFILES_PATH / "pyinfra" / "tasks"
    extra_env = os.environ.get("DOTF_EXTRA_TASKS_DIRS", "")
    extra_dirs = [TasksDir(absolute_path=Path(p), label=Path(p).parent.parent.name) for p in extra_env.split(":") if p]
    private_pyinfra = _private_pyinfra(private_repo)
    if private_pyinfra:
        extra_dirs.append(TasksDir(absolute_path=private_pyinfra / "tasks", label=""))

    all_tool_names = sorted(discover_tasks(dotfiles_tasks, extra_dirs).keys())
    resolved = []

    for token in tokens:
        if token in all_tool_names:
            resolved.append(token)
            continue
        from iterfzf import iterfzf

        chosen = iterfzf(
            iter(all_tool_names),
            query=token,
            prompt=f"Select tool for '{token}': ",
            cycle=True,
            __extra__=["--select-1", "--height=~40%", "--reverse", "--no-unicode", "--no-separator"],
        )
        if chosen:
            resolved.append(chosen)

    return resolved


# keep-sorted start
_BLUE = "\033[94m"
_ENV_DOTF_REPO = "DOTF_REPO"
_GREEN = "\033[92m"
_RED = "\033[31m"
_RESET = "\033[0m"
_WARN = "\033[33m"
_YELLOW = "\033[93m"
# keep-sorted end


def _print_blue(msg: str) -> None:
    print(f"{_BLUE}{msg}{_RESET}")


def _print_green(msg: str) -> None:
    print(f"{_GREEN}{msg}{_RESET}")


def _print_yellow(msg: str) -> None:
    print(f"{_YELLOW}{msg}{_RESET}")


def run(cmd: list[str], **kwargs: object) -> int:
    """Print and execute a shell command, returning its exit code."""
    _print_blue(f"→ {' '.join(cmd)}")
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


def _chezmoi_repo_name(source: Path) -> str:
    """Return the repo name for a chezmoi source dir (parent of the 'chezmoi' component)."""
    for parent in source.parents:
        if parent.name == "chezmoi":
            return parent.parent.name
    if source.name == "chezmoi":
        return source.parent.name
    return source.name


def _chezmoi_apply_source(source: Path, *, yes: bool = False) -> None:
    """Diff then apply a chezmoi source dir, offering merge-all on MM conflicts."""
    source_args = ["--source", str(source)]
    repo_name = f"{_chezmoi_repo_name(source)}/chezmoi"

    # chezmoi diff always exits 0; capture with --no-pager to check for changes
    probe = subprocess.run(["chezmoi", "diff", "--no-pager", *source_args], text=True, capture_output=True, check=False)  # noqa: S603 S607
    if not probe.stdout.strip():
        print(f"No changes from {repo_name}.")
        return

    # Built-in `chezmoi diff` only; delta is a remote-diff renderer, not a
    # local dependency. Avoids breaking fresh installs that haven't run pyinfra yet.
    subprocess.run(["chezmoi", "diff", *source_args], check=False)  # noqa: S603 S607

    if not yes:
        answer = input(f"Apply changes from {repo_name}? [y/N] ").strip()
        if answer.lower() not in {"y", "yes"}:
            print(f"Skipped {repo_name}.")
            return

    run(["chezmoi", "apply", "--verbose", *source_args])

    # chezmoi status exits 1 when it finds MM differences — capture regardless
    result = subprocess.run(["chezmoi", "status", *source_args], text=True, capture_output=True, check=False)  # noqa: S603 S607
    mm_files = [line for line in result.stdout.splitlines() if line[:2] == "MM"]
    if not mm_files:
        return
    print("Files modified in both source and destination:")
    for line in mm_files:
        print(f"  {line}")
    if not yes:
        answer = input(f"Run 'chezmoi merge-all' for {repo_name}? [y/N] ").strip()
        if answer.lower() not in {"y", "yes"}:
            return
    run(["chezmoi", "merge-all", *source_args])


def apply_chezmoi(private_repo: Path | None, *, yes: bool = False) -> None:
    """Apply chezmoi from the public source, then private source if available."""
    _chezmoi_apply_source(DOTFILES_PATH / "chezmoi", yes=yes)
    # Resolve private repo: explicit arg > $DOTF_REPO env var
    if private_repo is None:
        env_val = os.environ.get(_ENV_DOTF_REPO)
        if env_val:
            private_repo = Path(env_val).expanduser().resolve()
    if private_repo is not None:
        private_chezmoi = private_repo / "chezmoi" / "local"
        if private_chezmoi.is_dir():
            _chezmoi_apply_source(private_chezmoi, yes=yes)


def _discover_all_tasks(private_repo: Path | None) -> dict[str, Path]:
    """Discover all task .py files across dotfiles + private overlay.

    Used by both `list_provision` and `_compute_ordered_tools` so they see the
    same task universe.
    """
    import sys

    _pyinfra_lib = DOTFILES_PATH / "pyinfra"
    if str(_pyinfra_lib) not in sys.path:
        sys.path.insert(0, str(_pyinfra_lib))
    from lib import TasksDir, discover_tasks

    private_pyinfra = _private_pyinfra(private_repo)
    dotfiles_tasks = DOTFILES_PATH / "pyinfra" / "tasks"
    extra_env = os.environ.get("DOTF_EXTRA_TASKS_DIRS", "")
    extra_dirs = [TasksDir(absolute_path=Path(p), label=Path(p).parent.parent.name) for p in extra_env.split(":") if p]
    if private_pyinfra:
        extra_dirs.append(TasksDir(absolute_path=private_pyinfra / "tasks", label=""))
    return discover_tasks(dotfiles_tasks, extra_dirs)


def _print_server_order(s: "Server", all_tasks: dict, phantom_total: list, claimed: set) -> None:
    from collections import defaultdict

    from lib import Tier, compute_task_order

    print()
    print(f"Computed execution order for {s.name}:")
    order, phantom = compute_task_order(s.tools, all_tasks)
    phantom_total.extend((s.name, ph) for ph in phantom)
    claimed.update(name for name, _ in order)
    by_tier: dict[Tier, list[str]] = defaultdict(list)
    for name, tier in order:
        by_tier[tier].append(name)
    for tier in Tier:
        names = by_tier.get(tier, [])
        if names:
            print(f"  {tier.name:<12} {', '.join(names)}")


def _print_validation(all_tasks: dict, claimed: set, phantom_total: list) -> bool:
    from lib import read_meta_toml

    orphans = sorted(set(all_tasks) - claimed)
    missing_meta = sorted(name for name, path in all_tasks.items() if read_meta_toml(path) is None)
    print()
    print("Validation:")
    had_issues = False
    for tool_name in orphans:
        print(f"  {_WARN}WARN{_RESET}: task `{tool_name}` is not used by any server (orphan)")
        had_issues = True
    for tool_name in missing_meta:
        print(f"  {_RED}ERROR{_RESET}: task `{tool_name}` has no meta.toml (add requires + tier)")
        had_issues = True
    for server_name, tool in phantom_total:
        print(f"  {_RED}ERROR{_RESET}: server `{server_name}` lists `{tool}` but no task module exists (phantom)")
        had_issues = True
    if not had_issues:
        print("  OK")
    return bool(phantom_total or missing_meta)


def list_provision(private_repo: Path | None) -> None:
    """Print configured servers and available tools, then exit."""
    import sys

    _pyinfra_lib = DOTFILES_PATH / "pyinfra"
    if str(_pyinfra_lib) not in sys.path:
        sys.path.insert(0, str(_pyinfra_lib))
    from lib import read_module_docstring

    all_tasks = _discover_all_tasks(private_repo)
    servers = _load_servers(private_repo)

    # -- Servers ---------------------------------------------------------------
    print("Servers:")
    if servers:
        for s in servers:
            aliases = f" ({', '.join(s.aliases)})" if s.aliases else ""
            label = f"{s.name}{aliases}"
            print(f"  {label:<35}{s.host:<20}{len(s.tools)} tools")
    else:
        print("  (no private repo configured — set DOTF_REPO or pass -r)")

    # -- Computed execution order per server -----------------------------------
    phantom_total: list[tuple[str, str]] = []
    claimed: set[str] = set()
    for s in servers:
        _print_server_order(s, all_tasks, phantom_total, claimed)

    # -- All tools reference ---------------------------------------------------
    print()
    print("All tools (one-line docs):")
    for tool_name in sorted(all_tasks):
        doc = read_module_docstring(all_tasks[tool_name])
        first_line = doc.split("\n")[0] if doc else ""
        print(f"  {tool_name:<14}{first_line}")

    # -- Validation ------------------------------------------------------------
    if _print_validation(all_tasks, claimed, phantom_total):
        raise SystemExit(1)


def _resolve_ssh_target(server: str, private_repo: Path | None) -> tuple[str, str] | None:
    """Return (user@host, remote_chezmoi_src_dir) for a named inventory group, or None.

    Looks up the server in DOTF_SERVERS (or inventory.py fallback) to get the SSH host and user.
    remote_chezmoi_src_dir is the path on the remote where the source dir will be rsynced
    (matches the path used in pyinfra/tasks/chezmoi/chezmoi.py).
    Returns None for @local or if the server is not found.
    """
    if server == _LOCAL_HOST:
        return None
    for s in _load_servers(private_repo):
        if s.name == server:
            if s.host == _LOCAL_HOST:
                return None
            target = f"{s.ssh_user}@{s.host}" if s.ssh_user else s.host
            return target, "/tmp/chezmoi-src"  # noqa: S108
    return None


def _chezmoi_remote_diff(server: str, private_repo: Path | None, *, yes: bool = False) -> bool:
    """Rsync the chezmoi source dir to the remote, run chezmoi diff there, show via local delta, prompt.

    Returns True if the user confirmed (or --yes was passed), False if skipped.

    Flow mirrors _chezmoi_apply_source for local hosts:
      1. Rsync the raw chezmoi source dir (dot_-prefixed layout) to a temp dir on the remote.
         chezmoi diff/apply require the source directory, not a rendered archive — `chezmoi
         archive` produces the target state (rendered home files), not a source dir.
      2. SSH in: run `chezmoi diff --source=<remote_src_dir>`, pipe output through local delta.
      3. Prompt. If confirmed, return True so the caller proceeds with pyinfra.

    pyinfra/tasks/chezmoi/chezmoi.py is unconditional — it trusts this function ran first
    and that /tmp/chezmoi-src is already on the remote.
    """
    ssh_info = _resolve_ssh_target(server, private_repo)
    if ssh_info is None:
        return True

    ssh_target, remote_src_dir = ssh_info

    if private_repo is None:
        env_val = os.environ.get(_ENV_DOTF_REPO)
        if env_val:
            private_repo = Path(env_val).expanduser().resolve()
    if private_repo is None:
        return True

    chezmoi_src = private_repo / "chezmoi" / server
    if not chezmoi_src.is_dir():
        print(f"No chezmoi source for {server} at {chezmoi_src}, skipping remote diff.")
        return True

    repo_label = f"{private_repo.name}/chezmoi/{server}"

    # Rsync the source directory (trailing slash = sync contents, not the dir itself)
    run(["rsync", "-a", "--delete", f"{chezmoi_src}/", f"{ssh_target}:{remote_src_dir}/"])

    probe = subprocess.run(  # noqa: S603
        ["ssh", ssh_target, f"chezmoi diff --no-pager --source={remote_src_dir}"],  # noqa: S607
        text=True,
        capture_output=True,
        check=False,
    )
    if not probe.stdout.strip():
        print(f"No changes from {repo_label}.")
        return True

    # Pipe diff through delta when available; otherwise print raw (chezmoi diff
    # already includes ANSI colors).
    if shutil.which("delta"):
        delta = subprocess.Popen(["delta"], stdin=subprocess.PIPE)  # noqa: S607
        delta.communicate(probe.stdout.encode())
    else:
        sys.stdout.write(probe.stdout)
        sys.stdout.flush()

    if not yes:
        answer = input(f"Apply changes from {repo_label} to {server}? [y/N] ").strip()
        if answer.lower() not in {"y", "yes"}:
            print(f"Skipped {repo_label}.")
            return False
    _print_yellow("Changes not applied yet — pyinfra will apply them via 'Apply chezmoi from source dir'.")
    return True


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
    candidates = [private_pyinfra, DOTFILES_PATH / "pyinfra"] if private_pyinfra else [DOTFILES_PATH / "pyinfra"]
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
    if os.environ.get("DOTF_DEBUG"):
        extra.append("-vv")
    _repo_root = private_pyinfra.parent if private_pyinfra is not None else None
    is_local = server == _LOCAL_HOST or any(
        s.name == server and s.host == _LOCAL_HOST for s in _load_servers(_repo_root)
    )
    pyinfra_bin = Path(sys.executable).parent / "pyinfra" if is_local else _ensure_system_pyinfra()
    # Run from $HOME so pyinfra's relative-path display does not contain `../`s.
    # inventory.py + deploy.py are passed as absolute paths.
    run(
        [str(pyinfra_bin), str(workdir / "inventory.py"), str(workdir / "deploy.py"), *extra],
        cwd=str(Path.home()),
    )


def _homebrew_prefix() -> Path:
    """Return the Homebrew prefix, using $HOMEBREW_PREFIX if set, else `brew --prefix`."""
    env_val = os.environ.get("HOMEBREW_PREFIX")
    if env_val:
        return Path(env_val)
    return Path(subprocess.check_output(["brew", "--prefix"], text=True).strip())  # noqa: S607


def _system_python() -> Path | None:
    """Return the first system Python found outside this tool's venv.

    Remote provisioning runs pyinfra outside this tool's venv, so we need a
    system-level Python that SSH can invoke on the control machine without
    activating any virtualenv. Tries Homebrew 3.14 → 3.13 → 3.12, then
    falls back to /usr/bin/python3.
    """
    prefix = _homebrew_prefix()
    candidates = [
        prefix / "bin" / "python3.14",
        prefix / "bin" / "python3.13",
        prefix / "bin" / "python3.12",
        Path("/usr/bin/python3"),
    ]
    return next((p for p in candidates if p.exists()), None)


def _ensure_system_pyinfra() -> Path:
    """Install/upgrade pyinfra into the system Python if needed, return its pyinfra path.

    --break-system-packages is intentional: we're installing into the system
    Python (not a venv) so that pyinfra is available system-wide for remote
    SSH sessions, which don't inherit this tool's venv.
    """
    python = _system_python()
    if python is None:
        msg = "No system Python found; cannot provision remote hosts"
        raise SystemExit(msg)
    pyinfra_bin = python.parent / "pyinfra"
    print(f"→ Ensuring pyinfra is installed in {python} ...")
    run([str(python), "-m", "pip", "install", "--upgrade", "--break-system-packages", "pyinfra"])
    if not pyinfra_bin.exists():
        msg = f"pyinfra not found at {pyinfra_bin} after install"
        raise SystemExit(msg)
    return pyinfra_bin

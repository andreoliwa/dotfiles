"""Shared pyinfra utilities: task discovery, extra-tasks-dirs parsing, and server inventory."""

import ast
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

# Root of the dotfiles repo — derived from this file's location.
# Cannot import DOTFILES_PATH from src/dotf/ops.py: pyinfra tasks run under the
# pyinfra CLI in a separate process with no dotf package on sys.path.
DOTFILES_PATH = Path(__file__).parent.parent

_ENV_DOTF_SERVERS = "DOTF_SERVERS"
LOCAL_HOST = "@local"


@dataclass
class Server:
    """A provisioning target: local machine or remote SSH host."""

    name: str
    host: str  # IP, hostname, or LOCAL_HOST
    tools: list[str]
    aliases: list[str] = field(default_factory=list)
    ssh_user: str = ""
    mise_compile: bool = False
    brew_variant: str = "company"
    uv_packages: list[str] = field(default_factory=list)
    uv_extra_args: dict[str, list[str]] = field(default_factory=dict)
    pipx_packages: list[str] = field(default_factory=list)
    pipx_injects: dict[str, list[str]] = field(default_factory=dict)
    conjuring_mode: str = "personal"
    apt_packages: list[str] = field(default_factory=list)

    @property
    def ssh_allow_agent(self) -> bool:
        """True when an ssh_user is set — agent forwarding is always needed for remote hosts."""
        return bool(self.ssh_user)

    def encode(self) -> dict:
        """Serialize to a JSON-compatible dict."""
        return {
            "name": self.name,
            "host": self.host,
            "tools": self.tools,
            "aliases": self.aliases,
            "ssh_user": self.ssh_user,
            "mise_compile": self.mise_compile,
            "brew_variant": self.brew_variant,
            "uv_packages": self.uv_packages,
            "uv_extra_args": self.uv_extra_args,
            "pipx_packages": self.pipx_packages,
            "pipx_injects": self.pipx_injects,
            "conjuring_mode": self.conjuring_mode,
            "apt_packages": self.apt_packages,
        }

    @classmethod
    def decode(cls, data: dict) -> "Server":
        """Deserialize from a dict; raises ValueError on missing required fields."""
        required = ("name", "host", "tools")
        missing = [k for k in required if k not in data]
        if missing:
            _msg = f"Server dict missing required fields: {missing!r}"
            raise ValueError(_msg)
        return cls(
            name=data["name"],
            host=data["host"],
            tools=data["tools"],
            aliases=data.get("aliases", []),
            ssh_user=data.get("ssh_user", ""),
            mise_compile=data.get("mise_compile", False),
            brew_variant=data.get("brew_variant", "company"),
            uv_packages=data.get("uv_packages", []),
            uv_extra_args=data.get("uv_extra_args", {}),
            pipx_packages=data.get("pipx_packages", []),
            pipx_injects=data.get("pipx_injects", {}),
            conjuring_mode=data.get("conjuring_mode", "personal"),
            apt_packages=data.get("apt_packages", []),
        )

    @classmethod
    def decode_all(cls, json_str: str) -> "list[Server]":
        """Decode a JSON string produced by encode_servers(); aborts on parse error."""
        try:
            items = json.loads(json_str)
        except json.JSONDecodeError as exc:
            _msg = f"DOTF_SERVERS is not valid JSON: {exc}"
            raise SystemExit(_msg) from exc
        if not isinstance(items, list):
            _msg = "DOTF_SERVERS must be a JSON array"
            raise SystemExit(_msg)
        servers = []
        for i, item in enumerate(items):
            try:
                servers.append(cls.decode(item))
            except ValueError as exc:
                _msg = f"DOTF_SERVERS[{i}]: {exc}"
                raise SystemExit(_msg) from exc
        return servers

    def to_pyinfra_host(self) -> tuple[str, dict]:
        """Return a (host, data_dict) tuple suitable for a pyinfra inventory list."""
        data: dict = {"tools": ",".join(self.tools)}
        if self.ssh_user:
            data["ssh_user"] = self.ssh_user
            data["ssh_allow_agent"] = True
        if self.mise_compile:
            data["mise_compile"] = self.mise_compile
        if self.brew_variant != "company":
            data["brew_variant"] = self.brew_variant
        # Pass package lists as JSON strings; tasks json.loads them.
        if self.uv_packages:
            data["uv_packages"] = json.dumps(self.uv_packages)
        if self.uv_extra_args:
            data["uv_extra_args"] = json.dumps(self.uv_extra_args)
        if self.pipx_packages:
            data["pipx_packages"] = json.dumps(self.pipx_packages)
        if self.pipx_injects:
            data["pipx_injects"] = json.dumps(self.pipx_injects)
        if self.conjuring_mode != "personal":
            data["conjuring_mode"] = self.conjuring_mode
        if self.apt_packages:
            data["apt_packages"] = json.dumps(self.apt_packages)
        return self.host, data


def encode_servers(servers: "list[Server]") -> str:
    """Encode a list of Server instances to a JSON string for DOTF_SERVERS."""
    return json.dumps([s.encode() for s in servers])


@dataclass
class TasksDir:
    """Tasks directory and its properties."""

    # Callers must pass absolute paths via DOTF_EXTRA_TASKS_DIRS.
    absolute_path: Path
    # Label appended to symlink names to avoid collisions across repos.
    # Empty string for the primary dotfiles repo (no suffix).
    label: str


def parse_extra_tasks_dirs() -> list[TasksDir]:
    """Parse DOTF_EXTRA_TASKS_DIRS env var into a list of TasksDir."""
    extra = os.environ.get("DOTF_EXTRA_TASKS_DIRS", "")
    return [TasksDir(absolute_path=Path(p), label=Path(p).parent.parent.name) for p in extra.split(":") if p]


def discover_tasks(tasks_dir: Path, extra_dirs: list[TasksDir]) -> dict[str, Path]:
    """Return mapping of tool name → absolute .py path.

    Tool name is the file stem (e.g. "mise", "pipx").
    Excludes __init__.py and shell.py (shell.py is the entry point, not a tool).
    When the same stem appears in both dotfiles and an extra dir,
    the extra dir wins (private override).
    """
    excluded = {"__init__"}
    result: dict[str, Path] = {}

    # dotfiles tasks first (lower priority)
    for py_file in sorted(tasks_dir.glob("*/*.py")):
        if py_file.stem not in excluded:
            result[py_file.stem] = py_file.resolve()

    # extra dirs second (higher priority — override dotfiles)
    for tasks in extra_dirs:
        if not tasks.absolute_path.is_dir():
            continue
        for py_file in sorted(tasks.absolute_path.glob("*/*.py")):
            if py_file.stem not in excluded:
                result[py_file.stem] = py_file.resolve()

    return result


def filter_tasks(all_tasks: dict[str, Path], tools: list[str]) -> dict[str, Path]:
    """Return only the tasks whose names appear in *tools*, preserving order.

    ``shell`` is excluded because it is handled separately by the entry point.
    Unknown tool names (not in *all_tasks*) are silently skipped here; callers
    are responsible for warning about them if desired.
    """
    return {name: all_tasks[name] for name in tools if name in all_tasks}


def read_module_docstring(py_file: Path) -> str:
    """Extract module-level docstring from a .py file without importing it."""
    try:
        tree = ast.parse(py_file.read_text())
        return ast.get_docstring(tree) or ""
    except (SyntaxError, OSError):
        return ""

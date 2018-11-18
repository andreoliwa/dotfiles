"""Utilities for other scripts in this project."""
import json
import sys
from argparse import ArgumentTypeError
from pathlib import Path
from subprocess import PIPE, CalledProcessError, run
from time import sleep
from typing import Any, Dict, List, Optional

JsonDict = Dict[str, Any]

CONFIG_DIR = Path("~/.config/dotfiles/").expanduser()


def shell(command_line, quiet=False, return_lines=False, **kwargs):
    """Print and run a shell command."""
    if not quiet:
        print("$ {}".format(command_line))
    if return_lines:
        kwargs.setdefault("stdout", PIPE)

    completed_process = run(command_line, shell=True, universal_newlines=True, **kwargs)
    if not return_lines:
        return completed_process

    stdout = completed_process.stdout.strip().strip("\n")
    return stdout.split("\n") if stdout else []


def shell_find(command_line, **kwargs):
    """Run a find command using the shell, and return its output as a list."""
    if not command_line.startswith("find"):
        command_line = f"find {command_line}"
    kwargs.setdefault("quiet", True)
    kwargs.setdefault("check", True)
    return shell(command_line, return_lines=True, **kwargs)


def notify(title, message):
    """If terminal-notifier is installed, use it to display a notification."""
    check = "which" if sys.platform == "linux" else "command -v"
    try:
        terminal_notifier_path = shell("{} terminal-notifier".format(check), check=True, stdout=PIPE).stdout.strip()
    except CalledProcessError:
        terminal_notifier_path = ""
    if terminal_notifier_path:
        shell(
            'terminal-notifier -title "{}: {} complete" -message "Successfully {} dev environment."'.format(
                Path(__file__).name, title, message
            )
        )


def _check_type(full_path, method, msg):
    """Check a path, raise an error if it's not valid."""
    obj = Path(full_path)
    if not method(obj):
        raise ArgumentTypeError(f"{full_path} is not a valid existing {msg}")
    return obj


def existing_directory_type(directory):
    """Convert the string to a Path object, raising an error if it's not a directory. Use with argparse."""
    return _check_type(directory, Path.is_dir, "directory")


def existing_file_type(file):
    """Convert the string to a Path object, raising an error if it's not a file. Use with argparse."""
    return _check_type(file, Path.is_file, "file")


def wait_for_process(process_name: str) -> None:
    """Wait for a process to finish.

    https://stackoverflow.com/questions/1058047/wait-for-any-process-to-finish
    """
    pid = shell(f"pidof {process_name}", quiet=True, stdout=PIPE).stdout.strip()
    if not pid:
        return

    pid_path = Path(f"/proc/{pid}")
    while pid_path.exists():
        sleep(0.5)


class JsonConfig:
    """A JSON config file."""

    def __init__(self, partial_path):
        """Create or get a JSON config file inside the config directory."""
        self.full_path = CONFIG_DIR / partial_path
        self.full_path.parent.mkdir(parents=True, exist_ok=True)

    def _generic_load(self, default):
        """Try to load file data, and use a default when there is no data."""
        try:
            data = json.loads(self.full_path.read_text())
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            data = default
        return data

    def load_set(self):
        """Load file data as a set."""
        return set(self._generic_load(set()))

    def dump(self, new_data):
        """Dump new JSON data in the config file."""
        if isinstance(new_data, set):
            new_data = list(new_data)
        self.full_path.write_text(json.dumps(new_data))


class DatabaseServer:
    """A database server URI parser."""

    uri: str
    protocol: str
    user: Optional[str]
    password: Optional[str]
    server: str
    port: Optional[int]

    def __init__(self, uri):
        """Parser the server URI and extract needed parts."""
        self.uri = uri
        protocol_user_password, server_port = uri.split("@")
        self.protocol, user_password = protocol_user_password.split("://")
        if ":" in user_password:
            self.user, self.password = user_password.split(":")
        else:
            self.user, self.password = None, None
        if ":" in server_port:
            self.server, self.port = server_port.split(":")
            self.port = int(self.port)
        else:
            self.server, self.port = server_port, None

    @property
    def uri_without_port(self):
        """Return the URI without the port."""
        parts = self.uri.split(":")
        if len(parts) != 4:
            # Return the unmodified URI if we don't have port.
            return self.uri
        return ":".join(parts[:-1])


class PostgreSQLServer(DatabaseServer):
    """A PostgreSQL database server URI parser and more stuff."""

    databases: List[str] = []
    inside_docker = False
    psql: str = ""
    pg_dump: str = ""

    def __init__(self, *args, **kwargs):
        """Determine which psql executable exists on this machine."""
        super().__init__(*args, **kwargs)

        self.psql = shell("which psql", quiet=True, capture_output=True).stdout
        if not self.psql:
            self.psql = "psql_docker"
            self.inside_docker = True

        self.pg_dump = shell("which pg_dump", quiet=True, capture_output=True).stdout
        if not self.pg_dump:
            self.pg_dump = "pg_dump_docker"
            self.inside_docker = True

    @property
    def docker_uri(self):
        """Return a URI without port if we are inside Docker."""
        return self.uri_without_port if self.inside_docker else self.uri

    def list_databases(self) -> "PostgreSQLServer":
        """List databases."""
        process = shell(
            f"{self.psql} -c 'SELECT datname FROM pg_database WHERE datistemplate = false' "
            f"--tuples-only {self.docker_uri}",
            quiet=True,
            capture_output=True,
        )
        if process.returncode:
            print(f"Error while listing databases.\nstdout={process.stdout}\nstderr={process.stderr}")
            exit(10)

        self.databases = sorted(db.strip() for db in process.stdout.strip().split())
        return self


class DockerContainer:
    """A helper for Docker containers."""

    def __init__(self, container_name: str) -> None:
        """Init instance."""
        self.container_name = container_name
        self.inspect_json: List[JsonDict] = []

    def inspect(self) -> "DockerContainer":
        """Inspect a Docker container and save its JSON info."""
        if not self.inspect_json:
            raw_info = shell(f"docker inspect {self.container_name}", quiet=True, capture_output=True).stdout
            self.inspect_json = json.loads(raw_info)
        return self

    def replace_mount_dir(self, path: Path) -> Path:
        """Replace a mounted dir on a file/dir path inside a Docker container."""
        self.inspect()
        for mount in self.inspect_json[0]["Mounts"]:
            source = mount["Source"]
            if str(path).startswith(source):
                new_path = str(path).replace(source, mount["Destination"])
                return Path(new_path)
        return path

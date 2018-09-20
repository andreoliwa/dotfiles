"""Utilities for other scripts in this project."""
import json
import sys
from argparse import ArgumentTypeError
from pathlib import Path
from subprocess import PIPE, CalledProcessError, run
from typing import List, Optional

CONFIG_DIR = Path("~/.config/dotfiles/").expanduser()


def shell(command_line, quiet=False, **kwargs):
    """Print and run a shell command."""
    if not quiet:
        print("$ {}".format(command_line))
    return run(command_line, shell=True, universal_newlines=True, **kwargs)


def shell_find(command_line, **kwargs):
    """Run a find command using the shell, and return its output as a list."""
    if not command_line.startswith("find"):
        command_line = f"find {command_line}"
    kwargs.setdefault("quiet", True)
    kwargs.setdefault("check", True)
    kwargs.setdefault("stdout", PIPE)
    stdout = shell(command_line, **kwargs).stdout.strip().strip("\n")
    return stdout.split("\n") if stdout else []


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


class PostgreSQLServer(DatabaseServer):
    """A PostgreSQL database server URI parser and more stuff."""

    databases: List[str] = []

    def list_databases(self):
        """List databases."""
        raw_stdout = shell(
            "psql -c 'SELECT datname FROM pg_database WHERE datistemplate = false' "
            "--tuples-only {uri}".format(uri=self.uri),
            quiet=True,
            stdout=PIPE,
        ).stdout
        self.databases = sorted(db.strip() for db in raw_stdout.strip().split())
        return self

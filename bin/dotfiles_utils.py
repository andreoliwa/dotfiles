"""Utilities for other scripts in this project."""
import json
import sys
from argparse import ArgumentTypeError
from pathlib import Path
from subprocess import PIPE, CalledProcessError, run

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


def existing_directory_type(directory):
    """Convert the string to a Path object, raising an error if it's not a directory. Use with argparse."""
    obj = Path(directory)
    if not obj.is_dir():
        raise ArgumentTypeError(f"{directory} is not an existing directory")
    return obj


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

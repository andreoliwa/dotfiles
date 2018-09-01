"""Utilities for other scripts in this project."""
import sys
from pathlib import Path
from subprocess import PIPE, CalledProcessError, run


def shell(command_line, **kwargs):
    """Print and run a shell command."""
    print("$ {}".format(command_line))
    return run(command_line, shell=True, universal_newlines=True, **kwargs)


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

"""Filter to run a task only after a expected number of minutes (default 60).

`Developing plugins <https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html#filter-plugins>`_.
"""
from datetime import datetime
from pathlib import Path

CACHE_DIR = Path.home() / ".cache/dotfiles/run_only_after"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def run_only_after(task_identifier, expected_minutes=60):
    """Filter to run a task only after a expected number of minutes (default 60).

    Usage:
    ``when: "'a unique task identifier here' | run_only_after"``

    A file named after ``task_identifier`` is touched if it doesn't exist.
    If the files exists, the function checks if enough time has passed since the last modification time.
    """
    file_name = task_identifier.strip().replace(" ", "_").lower()
    file_path = CACHE_DIR / file_name
    if file_path.exists():
        now = datetime.now().timestamp()
        modification = file_path.stat().st_mtime
        diff_minutes = (now - modification) / 60
        if diff_minutes < expected_minutes:
            return False

    file_path.touch()
    return True


class FilterModule(object):
    """Ansible filter plugin.

    `Plugin examples <https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/filter/core.py>`_.
    """

    def filters(self):
        """Add those functions as filters on Ansible."""
        return {"run_only_after": run_only_after}

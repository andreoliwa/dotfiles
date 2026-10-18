# Copyright 2026
# ruff: noqa: PT009

"""Regressions for Calibre version selection and installer shell failures."""

import runpy
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from pyinfra.facts.server import Command, Kernel, LinuxName

TASK = Path(__file__).resolve().parents[1] / "pyinfra/tasks/calibre/calibre.py"


def plan(installed: str = "", latest: bytes = b"9.16.0") -> tuple[str, dict]:
    """Capture the Ubuntu installer command without network or package-manager access."""
    facts = {Kernel: "Linux", LinuxName: "Ubuntu", Command: installed}
    with (
        patch("pyinfra.host", MagicMock(get_fact=lambda fact, **_kw: facts[fact])),
        patch("pyinfra.operations.apt.packages"),
        patch("urllib.request.urlopen") as lookup,
        patch("shared.shell") as shell,
    ):
        lookup.return_value.__enter__.return_value.read.return_value = latest
        runpy.run_path(str(TASK))
    options = dict(shell.call_args.kwargs) if shell.called else {}
    return " && ".join(options.get("commands", [])), options


class CalibreTests(TestCase):
    """Exercise custom decisions and the shell that caused the sudo regression."""

    def test_version_comparison(self) -> None:
        """Upgrade older/broken binaries, normalize patches, and never downgrade."""
        for installed, latest, upgrade in [
            ("calibre (calibre 9.15)", b"9.16.0", True),
            ("calibre (calibre 9.9)", b"9.16.0", True),
            ("calibre (calibre 9.16)", b"9.16.1", True),
            ("calibre (calibre 9.16)", b"9.16.0", False),
            ("calibre (calibre 9.16.0)", b"9.16.0", False),
            ("calibre (calibre 10.0)", b"9.16.0", False),
            ("", b"9.16.0", True),
            ("unparseable", b"9.16.0", True),
        ]:
            with self.subTest(installed=installed, latest=latest):
                command, _options = plan(installed, latest)
                self.assertEqual(bool(command), upgrade)
                if upgrade:
                    self.assertIn("version=" + latest.decode(), command)

    def test_installer_preserves_failures_and_always_cleans_up(self) -> None:
        """Download, install, and post-install probe errors must all fail."""
        import os
        import subprocess
        from tempfile import TemporaryDirectory

        from pyinfra.connectors.util import make_unix_command

        command, options = plan()
        for mode in ["download-fails", "install-fails", "incomplete", "success"]:
            with self.subTest(mode=mode), TemporaryDirectory() as directory:
                root = Path(directory)
                binary = root / "calibre"
                downloads = root / "downloads"
                downloads.mkdir()
                wget = root / "wget"
                wget.write_text(
                    '#!/bin/sh\n[ "$1" = -nv ] && [ "$2" = -O ] || exit 80\n'
                    '[ "$4" = https://download.calibre-ebook.com/linux-installer.sh ] || exit 81\n'
                    'echo "$3" > "$ROOT/download-path"\n'
                    'if [ "$MODE" = download-fails ]; then echo partial > "$3"; exit 7; fi\n'
                    "cat > \"$3\" <<'INSTALL'\n"
                    '[ "$1" = version=9.16.0 ] || exit 84\n'
                    'echo ran > "$ROOT/installer-ran"\n'
                    '[ "$MODE" != install-fails ] || exit 8\n'
                    '[ "$MODE" != incomplete ] || exit 0\n'
                    'printf \'#!/bin/sh\\necho "calibre stub"\\n\' > "$ROOT/calibre"\n'
                    'chmod +x "$ROOT/calibre"\n'
                    "INSTALL\n",
                )
                wget.chmod(0o700)
                sudo = root / "sudo"
                sudo.write_text(
                    '#!/bin/sh\n[ "$1" = -H ] && [ "$2" = -n ] || exit 82\n'
                    'shift 2\n[ "$1" != -i ] || { echo "unexpected sudo login shell" >&2; exit 83; }\n'
                    'exec "$@"\n',
                )
                sudo.chmod(0o700)
                wrapped = make_unix_command(
                    command.replace("/opt/calibre/calibre", str(binary)),
                    _sudo=options["_sudo"],
                    _use_sudo_login=options.get("_use_sudo_login", True),
                    _shell_executable="bash",
                ).get_raw_value()
                result = subprocess.run(  # noqa: S603 - only local stubs execute
                    ["/bin/bash", "-c", wrapped],
                    env={
                        **os.environ,
                        "PATH": f"{root}:{os.defpath}",
                        "TMPDIR": str(downloads),
                        "ROOT": str(root),
                        "MODE": mode,
                    },
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertNotEqual(result.returncode, 83, result.stderr)
                self.assertEqual(result.returncode == 0, mode == "success", result.stderr)
                self.assertEqual((root / "installer-ran").exists(), mode != "download-fails")
                self.assertEqual(binary.exists(), mode == "success")
                self.assertFalse(Path((root / "download-path").read_text().strip()).exists())

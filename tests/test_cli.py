# Copyright 2026
# ruff: noqa: PT009

"""Tests for dotf CLI diagnostic commands."""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from dotf.cli import app


class ProgressCommandTests(TestCase):
    """Verify local and remote provisioning diagnostics."""

    def test_logs_view_follows_the_local_provision_log(self) -> None:
        """The logs view preserves the old local tail behavior."""
        with (
            TemporaryDirectory() as temp_dir,
            patch("dotf.cli.Path.home", return_value=Path(temp_dir)),
            patch("dotf.cli.subprocess.run") as run,
        ):
            result = CliRunner().invoke(app, ["watch", "--view", "logs"])

        self.assertEqual(result.exit_code, 0, result.output)
        run.assert_called_once_with(
            ["tail", "-f", "-n", "50", str(Path(temp_dir) / ".cache" / "dotf" / "provision.log")],
            check=False,
        )

    def test_logs_view_follows_the_selected_server_log(self) -> None:
        """The server flag follows the remote host's provisioning log."""
        with (
            patch("dotf.cli.subprocess.run") as run,
            patch("dotf.cli.resolve_server", return_value="rpi"),
            patch("dotf.cli._resolve_ssh_target", return_value=("osmc@192.168.178.35", "source")),
        ):
            result = CliRunner().invoke(app, ["watch", "--server", "styx", "--view", "logs"])

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("Connecting to styx...", result.output)
        run.assert_called_once_with(
            [
                "ssh",
                "osmc@192.168.178.35",
                "tail -f -n 50 ~/.cache/dotf/provision.log",
            ],
            check=False,
        )

    @patch("dotf.cli.subprocess.run")
    def test_default_view_redraws_logs_and_activity(self, run: MagicMock) -> None:
        """The default view combines recent logs with a CPU activity snapshot."""
        result = CliRunner().invoke(app, ["watch", "-n", "3"])

        self.assertEqual(result.exit_code, 0, result.output)
        command = run.call_args.args[0]
        self.assertEqual(command[:2], ["bash", "-c"])
        self.assertIn("tail -n 25", command[2])
        self.assertIn("top -b -n 1 -o %CPU", command[2])
        self.assertIn("sleep 3", command[2])


class ProvisionCommandTests(TestCase):
    """Verify provisioning command options."""

    @patch("dotf.cli._provision_impl")
    def test_from_option_selects_the_starting_task(self, provision: MagicMock) -> None:
        """The concise --from option passes one task to the provision implementation."""
        result = CliRunner().invoke(app, ["provision", "--from", "docker"])

        self.assertEqual(result.exit_code, 0, result.output)
        provision.assert_called_once_with("@local", None, "docker", None)

# Copyright 2026
# ruff: noqa: S101

"""Check one-way SSH enrollment without contacting a real server."""

import json
import shutil
import subprocess
from pathlib import Path
from typing import Literal, TypedDict, Unpack

import pytest
from typer.testing import CliRunner

from dotf.cli import app


class _RunOptions(TypedDict, total=False):
    """Describe subprocess options used by the enrollment commands."""

    check: bool
    stdout: int
    text: Literal[True]


@pytest.fixture
def enrollment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, list[list[str]]]:
    """Use a real inventory and key files, replacing only external commands."""
    monkeypatch.setenv(
        "DOTF_SERVERS",
        json.dumps(
            [
                {"name": "media", "host": "192.0.2.10", "ssh_user": "viewer", "aliases": ["screen"], "tools": []},
                {"name": "laptop", "host": "@local", "aliases": ["desk"], "tools": []},
            ]
        ),
    )
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(shutil, "which", lambda command: f"/usr/bin/{command}")
    calls = []

    def run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        if command[0] == "ssh-keygen" and "-y" not in command:
            key = Path(command[command.index("-f") + 1])
            key.write_text("local secret")
            key.with_suffix(".pub").write_text("ssh-rsa public-test-key\n")
        if command[0] == "ssh" and "-G" in command:
            return subprocess.CompletedProcess(
                command,
                0,
                stdout="host example\nuser viewer\nhostname 192.0.2.10\nport 2222\nproxyjump gateway\n"
                "identityfile /unrelated/authorized-key\nidentityfile ~/.ssh/id_rsa\n"
                "identitiesonly no\ncertificatefile /unrelated/certificate.pub\ncontrolpath /tmp/shared-ssh\n",
            )
        return subprocess.CompletedProcess(command, 0, stdout="ssh-rsa recovered-key\n")

    monkeypatch.setattr(subprocess, "run", run)
    return tmp_path / ".ssh" / "id_rsa", calls


def test_enrolls_only_selected_alias(enrollment: tuple[Path, list[list[str]]]) -> None:
    """The alias chooses one destination, and only the public key gets copied."""
    key, calls = enrollment
    result = CliRunner().invoke(app, ["ssh-copy-id", "-s", "screen"])
    assert result.exit_code == 0, result.output
    assert key.read_text() == "local secret"
    copy = next(command for command in calls if command[0] == "ssh-copy-id")
    assert copy[:3] == ["ssh-copy-id", "-i", str(key) + ".pub"]
    assert copy[-1] == "viewer@192.0.2.10"
    verify = calls[-1]
    assert verify[0] == "ssh"
    assert verify[-2:] == ["viewer@192.0.2.10", "true"]
    assert verify[verify.index("-i") + 1] == str(key)
    assert "BatchMode=yes" in verify
    assert "PreferredAuthentications=publickey" in verify
    assert "ControlPath=none" in verify


def test_rerun_preserves_existing_keys(enrollment: tuple[Path, list[list[str]]]) -> None:
    """Enrollment must not replace the source's established identity."""
    key, calls = enrollment
    key.parent.mkdir()
    key.write_text("keep secret")
    Path(str(key) + ".pub").write_text("ssh-rsa keep-public\n")
    for _ in range(2):
        result = CliRunner().invoke(app, ["ssh-copy-id", "-s", "media"])
        assert result.exit_code == 0, result.output
    assert key.read_text() == "keep secret"
    assert Path(str(key) + ".pub").read_text() == "ssh-rsa keep-public\n"
    assert all(command[0] != "ssh-keygen" for command in calls)


def test_recovers_missing_public_key(enrollment: tuple[Path, list[list[str]]]) -> None:
    """An existing private key needs its public half recovered, not replacement."""
    key, calls = enrollment
    key.parent.mkdir()
    key.write_text("keep secret")
    result = CliRunner().invoke(app, ["ssh-copy-id", "-s", "media"])
    assert result.exit_code == 0, result.output
    assert key.read_text() == "keep secret"
    assert Path(str(key) + ".pub").read_text() == "ssh-rsa recovered-key\n"
    assert calls[0] == ["ssh-keygen", "-y", "-f", str(key)]


@pytest.mark.parametrize("target", ["@local", "laptop", "desk", "missing"])
def test_rejects_invalid_destination(target: str, enrollment: tuple[Path, list[list[str]]]) -> None:
    """Local and unknown destinations must fail before creating or enrolling keys."""
    key, calls = enrollment
    result = CliRunner().invoke(app, ["ssh-copy-id", "-s", target])
    assert "No such command" not in result.output
    assert result.exit_code != 0
    assert not key.exists()
    assert calls == []


def test_requires_destination(enrollment: tuple[Path, list[list[str]]]) -> None:
    """Omitting a destination must not silently select a server."""
    _key, calls = enrollment
    result = CliRunner().invoke(app, ["ssh-copy-id"])
    assert "No such command" not in result.output
    assert result.exit_code != 0
    assert calls == []


@pytest.mark.parametrize("failure", ["ssh-keygen", "ssh-copy-id", "ssh"])
def test_command_failure_stops_enrollment(
    failure: str,
    enrollment: tuple[Path, list[list[str]]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failed generation, copy, or verification must not report success."""
    _key, calls = enrollment
    original = subprocess.run

    def run(command: list[str], **kwargs: Unpack[_RunOptions]) -> subprocess.CompletedProcess[str]:
        if command[0] == failure and "-G" not in command:
            calls.append(command)
            raise subprocess.CalledProcessError(23, command)
        return original(command, **kwargs)

    monkeypatch.setattr(subprocess, "run", run)
    result = CliRunner().invoke(app, ["ssh-copy-id", "-s", "media"])
    assert "No such command" not in result.output
    assert result.exit_code != 0
    assert calls[-1][0] == failure
    assert "verified" not in result.output.lower()


def test_orphan_public_key_is_not_overwritten(enrollment: tuple[Path, list[list[str]]]) -> None:
    """A lost private key must not cause its remaining public key to be replaced."""
    key, calls = enrollment
    key.parent.mkdir()
    public = Path(str(key) + ".pub")
    public.write_text("keep-public")
    result = CliRunner().invoke(app, ["ssh-copy-id", "-s", "media"])
    assert "No such command" not in result.output
    assert result.exit_code != 0
    assert public.read_text() == "keep-public"
    assert calls == []


def test_uses_selected_identity(enrollment: tuple[Path, list[list[str]]]) -> None:
    """An explicit identity must select the same public and private key pair."""
    key, calls = enrollment
    selected = key.parent.parent / "other-key"
    selected.write_text("selected secret")
    Path(str(selected) + ".pub").write_text("ssh-ed25519 selected-public\n")
    result = CliRunner().invoke(app, ["ssh-copy-id", "-s", "screen", "-i", str(selected)])
    assert result.exit_code == 0, result.output
    assert not key.exists()
    copy = next(command for command in calls if command[0] == "ssh-copy-id")
    assert copy[:3] == ["ssh-copy-id", "-i", str(selected) + ".pub"]
    assert copy[-1] == "viewer@192.0.2.10"
    assert calls[-1][calls[-1].index("-i") + 1] == str(selected)
    assert selected.read_text() == "selected secret"


def test_missing_tool_fails_before_key_creation(
    enrollment: tuple[Path, list[list[str]]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An unavailable enrollment tool should leave the computer unchanged."""
    key, calls = enrollment
    original = shutil.which
    monkeypatch.setattr(shutil, "which", lambda name: None if name == "ssh-copy-id" else original(name))
    result = CliRunner().invoke(app, ["ssh-copy-id", "-s", "media"])
    assert "No such command" not in result.output
    assert result.exit_code != 0
    assert "ssh-copy-id is required" in result.output
    assert not key.exists()
    assert calls == []


def test_recovers_real_public_key_without_changing_private_key(tmp_path: Path) -> None:
    """Public-key recovery must work with actual OpenSSH key material."""
    from dotf.ssh import _ensure_identity

    key = tmp_path / "identity"
    subprocess.run(  # noqa: S603
        ["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)],  # noqa: S607
        check=True,
    )
    secret = key.read_bytes()
    public = Path(str(key) + ".pub")
    original = public.read_text().split()[:2]
    public.unlink()
    assert _ensure_identity(key) == public
    assert public.read_text().split()[:2] == original
    assert key.read_bytes() == secret


def test_isolates_selected_key_and_keeps_connection_settings(
    enrollment: tuple[Path, list[list[str]]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Another authorized identity must not make enrollment skip the selected key."""
    key, _calls = enrollment
    key.parent.mkdir()
    (key.parent / "config").write_text(
        "Host gateway\n  HostName 192.0.2.20\n  User tunnel\n  Port 2200\n  IdentityFile ~/.ssh/gateway-key\n",
    )
    original = subprocess.run
    configs = []

    def run(command: list[str], **kwargs: Unpack[_RunOptions]) -> subprocess.CompletedProcess[str]:
        if "-F" in command:
            config = command[command.index("-F") + 1]
            # Ask OpenSSH itself which identities and transport settings it will use.
            with subprocess.Popen(  # noqa: S603
                ["ssh", "-F", config, "-G", "viewer@192.0.2.10"],  # noqa: S607
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            ) as process:
                output, error = process.communicate()
            assert process.returncode == 0, error
            lines = output.splitlines()
            assert [line for line in lines if line.startswith("identityfile ")] == [f"identityfile {key}"]
            assert "identitiesonly yes" in lines
            assert "port 2222" in lines
            assert "proxyjump gateway" in lines
            assert not any(line.startswith("certificatefile /unrelated") for line in lines)
            assert "controlpath /tmp/shared-ssh" not in lines
            with subprocess.Popen(  # noqa: S603
                ["ssh", "-F", config, "-G", "gateway"],  # noqa: S607
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            ) as process:
                output, error = process.communicate()
            assert process.returncode == 0, error
            assert "hostname 192.0.2.20" in output.splitlines()
            assert "user tunnel" in output.splitlines()
            assert "port 2200" in output.splitlines()
            assert "proxyjump gateway" not in output.splitlines()
            configs.append(config)
        return original(command, **kwargs)

    monkeypatch.setattr(subprocess, "run", run)
    result = CliRunner().invoke(app, ["ssh-copy-id", "-s", "media"])
    assert result.exit_code == 0, result.output
    copy_config, verify_config = configs
    assert copy_config == verify_config
    assert not Path(configs[0]).exists()

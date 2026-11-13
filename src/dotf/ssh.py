# Copyright 2026

"""Enroll the current computer's public key on one SSH destination."""

import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path


def _ensure_identity(identity: Path) -> Path:
    """Require an existing private key and recover its public half when missing."""
    public = Path(str(identity) + ".pub")
    if not identity.is_file():
        message = f"Private key not found: {identity}. Restore an existing key or select it with -i."
        raise FileNotFoundError(message)
    if not public.exists():
        result = subprocess.run(  # noqa: S603
            ["ssh-keygen", "-y", "-f", str(identity)],  # noqa: S607
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )
        # Exclusive creation preserves any file that appeared while deriving the key.
        with public.open("x") as output:
            output.write(result.stdout)
    return public


def copy_ssh_key(target: str, identity: Path) -> None:
    """Install only the selected public key, then check non-interactive SSH access."""
    for command in ("ssh-keygen", "ssh-copy-id", "ssh"):
        if shutil.which(command) is None:
            message = f"{command} is required. Install the OpenSSH client tools first."
            raise FileNotFoundError(message)
    identity = identity.expanduser().absolute()
    public = _ensure_identity(identity)
    settings = subprocess.run(  # noqa: S603
        ["ssh", "-G", target],  # noqa: S607
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout
    # IdentityFile options accumulate, even with -i and IdentitiesOnly=yes.
    # Keep resolved connection settings, but exclude other keys and shared sessions.
    excluded = {
        "host",
        "identityfile",
        "certificatefile",
        "identitiesonly",
        "controlpath",
        "controlmaster",
        "controlpersist",
        "remotecommand",
        "requesttty",
        "clearallforwardings",
    }
    settings = "\n".join(line for line in settings.splitlines() if line.split(maxsplit=1)[0].lower() not in excluded)
    quoted_identity = str(identity).replace("%", "%%").replace("\\", "\\\\").replace('"', '\\"')
    target_host = target.rsplit("@", 1)[-1]
    user_config = shlex.quote(str(Path.home() / ".ssh" / "config"))
    with tempfile.TemporaryDirectory(prefix="dotf-ssh-") as directory:
        config = Path(directory) / "config"
        config.write_text(
            f'Host {target_host}\nIdentityFile "{quoted_identity}"\nIdentitiesOnly yes\n'
            "ControlPath none\nControlMaster no\nControlPersist no\n"
            "RemoteCommand none\nRequestTTY no\nClearAllForwardings yes\n" + settings + "\n"
            # Jump-host subprocesses inherit -F; retain their normal configuration.
            f"Host * !{target_host}\nInclude {user_config} /etc/ssh/ssh_config\n",
        )
        subprocess.run(  # noqa: S603
            ["ssh-copy-id", "-i", str(public), "-F", str(config), target],  # noqa: S607
            check=True,
        )
        subprocess.run(  # noqa: S603
            [  # noqa: S607
                "ssh",
                "-F",
                str(config),
                "-i",
                str(identity),
                "-o",
                "BatchMode=yes",
                "-o",
                "IdentitiesOnly=yes",
                "-o",
                "PreferredAuthentications=publickey",
                "-o",
                "ControlPath=none",
                "-o",
                "ConnectTimeout=10",
                target,
                "true",
            ],
            check=True,
        )

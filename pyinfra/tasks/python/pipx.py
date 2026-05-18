"""Install pipx and manage pipx-installed packages from inventory.

Reads ``host.data.pipx_packages`` (list[str]) and ``host.data.pipx_injects``
(dict[str, list[str]]) - both JSON-encoded by Server.to_pyinfra_host().
"""

import json

from pyinfra.operations import server

from pyinfra import host

_BREW_PATH = "/opt/homebrew/bin:/usr/local/bin:/home/linuxbrew/.linuxbrew/bin"
_ENV = {"PATH": f"$HOME/.local/bin:{_BREW_PATH}:/usr/bin:/bin"}

server.shell(
    name="Install pipx via pip",
    commands=["python3 -m pip install -U --user pipx"],
    _env=_ENV,
)

server.shell(
    name="Ensure pipx is on PATH",
    commands=["pipx ensurepath"],
    _env=_ENV,
    _ignore_errors=True,
)


def _decode(raw: object, default: object) -> object:
    if isinstance(raw, str) and raw:
        return json.loads(raw)
    return raw or default


_packages: list[str] = _decode(host.data.get("pipx_packages", "[]"), [])  # type: ignore[assignment]
_injects: dict[str, list[str]] = _decode(host.data.get("pipx_injects", "{}"), {})  # type: ignore[assignment]

for _pkg in _packages:
    server.shell(
        name=f"pipx install {_pkg}",
        commands=[f"pipx install --force --include-deps {_pkg}"],
        _env=_ENV,
    )
    for _inject in _injects.get(_pkg, []):
        server.shell(
            name=f"pipx inject {_pkg} <- {_inject}",
            commands=[f"pipx inject --force -e {_pkg} {_inject}"],
            _env=_ENV,
        )

"""Node.js global npm packages.

Node itself is provided by mise (see ~/.config/mise/config.toml). Picks a
company/personal package list based on host.data.brew_variant (defaults to
company).
"""

from pyinfra.operations import server

from pyinfra import host

_BREW_PATH = "/opt/homebrew/bin:/usr/local/bin:/home/linuxbrew/.linuxbrew/bin"
_ENV = {"PATH": f"$HOME/.local/share/mise/shims:{_BREW_PATH}:/usr/bin:/bin"}

_COMMON: list[str] = ["prettier"]
_PERSONAL: list[str] = []
_COMPANY: list[str] = []

_variant = host.data.get("brew_variant", "company")
_packages = _COMMON + (_PERSONAL if _variant == "personal" else _COMPANY)

for _pkg in _packages:
    server.shell(
        name=f"npm install -g {_pkg}",
        commands=[f"npm install -g --silent {_pkg}"],
        _env=_ENV,
    )

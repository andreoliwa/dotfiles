"""Node.js global npm packages.

Node itself is provided by mise (see ~/.config/mise/config.toml). Picks a
company/personal package list based on host.data.brew_variant (defaults to
company).
"""

from shared import home_path, make_env, shell

from pyinfra import host

_ENV = make_env(home_path(".local/share/mise/shims"))

shell(
    name="mise install node",
    commands=["mise install node"],
    _env=_ENV,
)

shell(
    name="mise install pnpm",
    commands=["mise install pnpm"],
    _env=_ENV,
)

_COMMON: list[str] = ["prettier"]
_PERSONAL: list[str] = []
_COMPANY: list[str] = []

# Packages to uninstall globally (legacy / no longer needed).
_REMOVE: list[str] = [
    # keep-sorted start
    "@commitlint/cli",
    "@commitlint/config-conventional",
    "@sentry/cli",
    "aws-es-kibana",
    "babel-eslint",
    "codeowners",
    "commitizen",
    "conventional-changelog-cli",
    "eslint",
    "eslint-config-airbnb",
    "eslint-plugin-react",
    "np",
    "remark-cli",
    "remark-preset-lint-markdown-style-guide",
    "remark-preset-lint-recommended",
    "semantic-release-cli",
    "webpack",
    # keep-sorted end
]

_variant = host.data.get("brew_variant", "company")
_packages = _COMMON + (_PERSONAL if _variant == "personal" else _COMPANY)

for _pkg in _packages:
    shell(
        name=f"npm install -g {_pkg}",
        commands=[f"npm install -g --silent {_pkg}"],
        _env=_ENV,
    )

for _pkg in _REMOVE:
    shell(
        name=f"npm uninstall -g {_pkg}",
        commands=[f"npm uninstall -g --silent {_pkg}"],
        _env=_ENV,
        _ignore_errors=True,
    )

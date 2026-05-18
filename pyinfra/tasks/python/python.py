"""Install versions via mise. Versions defined in ~/.config/mise/config.toml."""

from shared import shell

from pyinfra import host

if host.data.get("mise_compile"):
    # Workaround: mise 2026.4.x crashes on 32-bit ARM (bytesize panic) when cloning
    # pyenv via its internal gix library. Pre-seeding the cache bypasses this.
    # Bug: https://github.com/jdx/mise/issues (search: bytesize arm)
    shell(
        name="Pre-clone pyenv into mise cache (ARM gix workaround)",
        commands=[
            "mkdir -p ~/.cache/mise/python",
            "[ -d ~/.cache/mise/python/pyenv/.git ] || "
            "git clone https://github.com/pyenv/pyenv.git ~/.cache/mise/python/pyenv",
        ],
    )

_mise_cmd = "MISE_PYTHON_COMPILE=1 mise install python" if host.data.get("mise_compile") else "mise install python"
shell(
    name="Install Python versions via mise",
    commands=[_mise_cmd],
)

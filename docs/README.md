# Dotfiles (pyinfra + chezmoi)

Personal macOS development environment.

Provisioned by [pyinfra](https://pyinfra.com) for installs/setup and
[chezmoi](https://chezmoi.io) for dotfile placement. Driven by the `dotf` CLI.

## Quick install (new machine)

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/). Then:

```bash
curl -fsSL https://raw.githubusercontent.com/andreoliwa/dotfiles/master/bootstrap.sh | sh
```

The bootstrap script:

1. Installs Xcode Command Line Tools (macOS).
2. Installs Homebrew and `uv`.
3. Clones this repo to `~/dotfiles`.
4. Installs `dotf` + `pyinfra` as a uv tool.

Provision the machine with:

```bash
dotf provision -s <server-name>
```

A private overlay repo can supply machine-specific config (inventory, secrets,
private dotfiles). Point pyinfra at its `tasks/` dir by setting
`DOTF_EXTRA_TASKS_DIRS`, and run `dotf` from the overlay repo's `pyinfra/`
directory.

## dotf CLI

```
dotf provision [TOOLS] [-s SERVER] [--start-from TOOL] [--list]  # chezmoi apply + pyinfra
dotf list | dotf ls                                              # list servers + tools
dotf chezmoi                                                     # chezmoi apply only
dotf tail                                                        # follow ~/.cache/dotf/provision.log
```

Global flags: `--debug` / `-d` (pass `-v` to pyinfra), `--yes` / `-y` (skip
confirmations).

## Repo layout

```
dotfiles/
├── chezmoi/        # chezmoi source dir (public dotfiles, dot_* prefix convention)
├── pyinfra/
│   ├── shared.py   # helpers shared by tasks (home_path, make_env, shell)
│   ├── lib.py      # Server dataclass, task discovery
│   └── tasks/      # one dir per tool; *.py = pyinfra operations; *.sh = shell.d fragments
├── src/dotf/       # Typer-based dotf CLI
├── bin/            # PATH scripts shipped with the repo (added to PATH by shell/10-path.sh)
├── bootstrap.sh    # bootstrap entry point (curl-pipe-safe)
```

## Shell fragments (`~/.config/shell.d/`)

`.bashrc` / `.bash_profile` source every `~/.config/shell.d/*.sh` in numeric
order. Fragments are assembled from `pyinfra/tasks/*/NN-*.sh` in this repo and
any overlay repo, then synced (with `delete=True`) so removed fragments disappear
from the target.

Number ranges: `0x` env, `1x` PATH, `2x` aliases, `3x+` completions/inits.

## License

[MIT](http://sloria.mit-license.org/)

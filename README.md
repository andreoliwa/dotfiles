# Dotfiles (powered by pyinfra + chezmoi)

Personal macOS development environment.

**Currently migrating from Ansible to [pyinfra](https://pyinfra.com) + [chezmoi](https://chezmoi.io).**

## Quick install (new machine)

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/). Then:

```bash
curl -fsSL https://raw.githubusercontent.com/andreoliwa/dotfiles/master/install.sh | sh
```

Installs `dotf` and `pyinfra` globally. No need to clone the repo first.

## dotf CLI

`dotf` is the provisioning wrapper. It lives in `src/dotf/` and is installed via the `install.sh` script above.

```bash
dotf --help
```

Internally calls pyinfra and chezmoi. Source is pulled directly from this repo's `master` branch — not published to
PyPI.

## Decisions

- **pyinfra over Ansible**: gradual migration, Ansible roles remain in place until fully replaced.
- **chezmoi for dotfiles**: manages `~/` files; source directory is `~/dotfiles/chezmoi/`.
- **uv as installer**: `uv tool install` gives pyinfra and dotf a shared isolated venv with both CLIs on PATH.
- **Git-only distribution**: `dotf` is installed from `git+https://github.com/andreoliwa/dotfiles.git`, not PyPI.
- **Two-repo setup**: `~/dotfiles/` (public) + private repo for machine-specific config. The public repo has zero
  references to private machines or paths.

---

## Legacy Ansible setup

> The sections below describe the original Ansible-based setup. They remain accurate but are progressively being
> replaced by the pyinfra + chezmoi workflow above.

### A few neat features

- [xonsh](https://xon.sh) (Python-powered shell)
- zsh configured with [prezto](https://github.com/sorin-ionescu/prezto).
- nice fonts for the terminal and coding.
- iterm2 profile (w/ hotkey, themes, etc.)
- a tmux.conf that's pretty neat.
- [tmuxp](https://tmuxp.git-pull.com/en/latest/) for tmux session management
- Mac packages installed with [homebrew][]. Mac apps installed with [homebrew-cask][].
- Useful git aliases
- Optional git commit signing with GPG

### Prerequisites

- [macOS: upgrade to the latest version possible](https://support.apple.com/macos)
- HomeBrew: [macOS requirements](https://docs.brew.sh/Installation#macos-requirements) first (e.g.:
  `xcode-select --install`)
- [Install HomeBrew](https://brew.sh/)
- ansible >= 2.4: `brew install ansible`
- If you're installing a new computer, copy or create these files/directories:
  - GPG config: `~/.gnupg/`
  - Ansible Vault password: `~/.config/dotfiles/vault_password.txt`

### Install

- Clone the repo to `~/dotfiles`.
- Update variables in `group_vars/local` (git identity, github username, email).
- Run:
  ```bash
  dotf legacy --galaxy --bootstrap
  ```

### Updating

```bash
dotf legacy
# or with specific roles:
dotf legacy git python macos
```

### Architecture

- `roles/` — Custom Ansible roles (each role = one tool/concern)
- `roles_galaxy/` — Third-party roles from Ansible Galaxy
- `group_vars/all.yml` — Central config: package lists, tool versions
- `group_vars/local` — Machine-specific overrides
- `playbook_local.yml` — Main playbook; roles are tagged for selective execution
- `chezmoi/` — Chezmoi-managed dotfiles (`dot_` prefix convention)
- `bin/` — Scripts on `$PATH`

Package lists in `group_vars/all.yml` use a `common` / `personal_laptop` / `company_laptop` / `remove` structure,
maintained in alphabetical order within `# keep-sorted` markers.

### Notes

**iterm2**: go to preferences → enable "Load preferences from custom folder" → select `misc/iterm2/`.

**macOS keyboard**: manually set key repeat to max and map Caps Lock to Ctrl.

### Troubleshooting

If you get an error about Xcode command-line tools:

```bash
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
```

[homebrew]: http://brew.sh/
[homebrew-cask]: https://github.com/caskroom/homebrew-cask

## License

[MIT Licensed](http://sloria.mit-license.org/).

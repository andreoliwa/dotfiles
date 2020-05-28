# dotfiles

[sloria's dotfiles](https://github.com/sloria/dotfiles-old), rewritten as Ansible roles. Sets up a full local development environment with a **single command.**

Fully supports macOS. Red Hat and Debian support is good but not as complete.

## a few neat features

-   [xonsh](https://xon.sh) (Python-powered shell)
-   zsh configured with [prezto](https://github.com/sorin-ionescu/prezto).
-   nice fonts for the terminal and coding.
-   iterm2 profile (w/ hotkey, themes, etc.)
-   python2, python3, pyenv (for managing Python versions), and pyenv-virtualenv (for managing virtualenvs)
-   alternative Python configuration with pyenv, pip, virtualenv
-   a tmux.conf that's pretty neat.
-   [tmuxp](https://tmuxp.git-pull.com/en/latest/) for tmux session management
-   vim with [vim-plug](https://github.com/junegunn/vim-plug) for plugin management. All configuration in a single file [.vimrc](https://github.com/sloria/dotfiles/blob/master/roles/vim/files/vimrc).
-   pluggable. Everything is optional. Fork this. Remove what you don't use. Configure what you do use.
-   Mac packages installed with [homebrew][]. Mac apps installed with [homebrew-cask][].
-   Useful git aliases
-   Optional git commit signing with GPG
-   Preview the setup on Linux machines using Vagrant's virtual machines

## prerequisites (install these first)

-   [macOS: upgrade to the latest version possible](https://support.apple.com/macos)
-   HomeBrew: [macOS requirements](https://docs.brew.sh/Installation#macos-requirements) first (e.g.: XCode), then [install HomeBrew](https://brew.sh/)
-   ansible >= 2.4:
    -   macOS: `brew install ansible`;
    -   Linux: [get the latest PPA](http://docs.ansible.com/ansible/latest/intro_installation.html#installing-the-control-machine).
-   Tools to start working on this repo: `brew install ansible git python vim fzf`
-   Run `xcode-select --install`
-   If you're installing a new computer, copy these files/directories:
    -   `~/.gnupg`
    -   `~/.config/dotfiles/local.env`, set `export COMPANY_LAPTOP=` variable

## install

-   [Fork](https://github.com/sloria/dotfiles/fork) this repo.
-   Clone your fork.
    ```bash
    # Replace git url with your fork
    # NOTE: It is important that you clone to ~/dotfiles
    git clone https://github.com/YOU/dotfiles.git ~/dotfiles
    cd ~/dotfiles
    ```
-   Update the following variables in `group_vars/local` (at a minimum)
    -   `full_name`: Your name, which will be attached to commit messages, e.g. "Steven Loria"
    -   `git_user`: Your Github username.
    -   `git_email`: Your git email address.
-   Optional, but recommended: Update `group_vars/local` with the programs you want installed by [homebrew][], [homebrew-cask][], and npm.
    -   `mac_homebrew_packages`: Utilities that don't get installed by the roles.
    -   `mac_cask_packages`: Mac Apps you want installed with [homebrew-cask][].
-   Edit `playbook_local.yml` as you see fit. Remove any roles you don't use. Edit roles that you do use.
-   Run the installation script.
    Comment out private roles (they will fail on first execution).
    ```bash
    ~/dotfiles/bin/multi-dev-machine --galaxy --bootstrap
    ```

## updating your local environment

Once you have the dotfiles installed you can run the following command to rerun the ansible playbook:

```bash
multi-dev-machine
```

You can optionally pass role names

```bash
multi-dev-machine git python
```

## updating your dotfiles repo

To keep your fork up to date with the `sloria` fork:

```
git remote add sloria https://github.com/sloria/dotfiles.git
git pull sloria master
```

## command

There is a script `multi-dev-machine` in the `bin` directory for setting up and updating development environments:

-   bootstrap/updates the local environment
-   install Galaxy roles
-   run Ansible on Vagrant VMs

Type `multi-dev-machine -h` to see all possibilities.

## special files

All configuration is done in `~/dotfiles`. Each role may contain (in addition to the typical ansible directories and files) a number of special files

-   **role/\*.zsh**: Any files ending in `.zsh` get loaded into your environment.
-   for xonsh: **role/\*.xsh**: Any files ending in `.xsh` get loaded into your environment.
-   **bin/**: Anything in `bin/` will get added to your `$PATH` and be made available everywhere.

## notes

**iterm2**

To import the iterm2 profile, go to your iterm2 preferences, and enable "Load preferences from custom folder" and select the iterm2 folder in the `misc/` directory.

![iterm2 profile](https://user-images.githubusercontent.com/2379650/34223487-859f2752-e58d-11e7-8024-9e6af5c1ec4e.png)

**macOS keyboard settings**

There are a few keyboard customizations that must be done manually:

-   Turning repeat speed up to 11.

![Keyboard settings](https://user-images.githubusercontent.com/2379650/34223505-91f95072-e58d-11e7-9b36-78aec4203b0d.png "Key repeat settings")

-   Mapping Caps Lock to Ctrl.

![Modifier keys](https://user-images.githubusercontent.com/2379650/34223523-a2c8e4e4-e58d-11e7-9532-d74b95d8408a.png)

## what if I only want your vim?

First make sure you have a sane vim compiled. On macOS, the following will do:

```
brew install macvim --HEAD --with-override-system-vim
```

The following commands will install vim-plug and download my `.vimrc`.

After backing up your `~/.vim` directory and `~/.vimrc`:

```
mkdir -p ~/.vim/autoload
curl -fLo ~/.vim/autoload/plug.vim https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
curl -fLo ~/.vimrc https://raw.githubusercontent.com/sloria/dotfiles/master/roles/vim/files/vimrc
```

You will now be able to open vim and run `:PlugInstall` to install all plugins.

## troubleshooting

If you get an error about Xcode command-line tools, you may need to run

```
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
```

## todo

-   Full Debian and Red Hat support

[homebrew]: http://brew.sh/
[homebrew-cask]: https://github.com/caskroom/homebrew-cask

## license

[MIT Licensed](http://sloria.mit-license.org/).

git_pyenv
=========

Clone a git repository with an optional pyenv virtualenv.

See [defaults/main.yml](defaults/main.yml) for parameter details.

In a playbook file:

```
  roles:
    - role: git_pyenv
      vars:
        repo: "https://github.com/andreoliwa/dotfiles.git"
        dir: dotfiles-andreoliwa
        update: yes
        create_env: no
```

In a task file:

```
- import_role: name=git_pyenv
  vars:
    repo: "https://github.com/andreoliwa/dotfiles.git"
    dir: dotfiles-andreoliwa
    update: yes
    create_env: no
```

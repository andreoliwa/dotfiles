# python_repo

Clone a git repository with an optional pyenv virtualenv.

See [defaults/main.yml](defaults/main.yml) for parameter details.

In a playbook file:

```
  roles:
    - role: python_repo
      vars:
        repo: "https://github.com/andreoliwa/dotfiles.git"
        dir: dotfiles-andreoliwa
        update: yes
```

In a task file:

```
- import_role: name=python_repo
  vars:
    repo: "https://github.com/some-user/some-python-repo.git"
    dir: some-dir
    update: yes
    python_version: 3.7
```

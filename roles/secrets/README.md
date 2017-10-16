# Secrets

Installing secrets/private files using Vaults.

- Create a `keys.yml file` with the structure:

```yaml
---
filename: |
  filevalue
filename_ii: |
  filevalue
```

- Run `ansible-vault encrypt key.yml` to encrypt before pushing it to the repo.
- Run `ansible-vault decrypt --ask-vault-pass keys.yml` to decrpyt the file.

You can add other files as vars and encrypt them similarly and add a copy task in the main.yml. A pre-commit hook is there to avoid commiting un-encrypted files into the repo (<https://gist.github.com/ralovely/9367737>)

# git

Installs and configures git.

## Signing commits with GPG

Follow the instructions [here](https://github.com/pstadler/keybase-gpg-github) to create a GPG on keybase and set it up to use with GitHub.

Then, in `group_vars/all.yml`, set `git_personal.user_signingkey` to the ID of the GPG key you use to sign commits.

```bash
$ gpg --list-secret-keys
# /Users/sloria/.gnupg/secring.gpg
# ----------------------------------
# sec   4096R/E870EE00 2016-04-06 [expires: 2032-04-02]
# uid                  Steven Loria <sloria1@gmail.com>
# ssb   4096R/F9E3E72E 2016-04-06
```

```yaml
# In group_vars/all.yml

git_personal:
  user_signingkey: E870EE00
```

If you do **not** wish to sign commits with GPG, just set `git_personal.user_signingkey` to a blank variable.

```yaml
# No GPG signing
# In group_vars/all.yml

git_personal:
  user_signingkey:
```

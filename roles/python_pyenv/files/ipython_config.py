"""Config for the default iPython profile.

See https://ipython.readthedocs.io/en/stable/config/intro.html
"""
c.TerminalInteractiveShell.confirm_exit = False  # type: ignore # noqa: F821

c.AliasManager.user_aliases = [("la", "ls -al")]  # type: ignore # noqa: F821

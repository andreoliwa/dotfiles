def _gu():
    gitup . && echo 'Running git bclean...' && gitup --exec 'git bclean' .
aliases["gu"] = _gu

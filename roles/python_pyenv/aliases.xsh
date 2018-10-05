aliases["jpnb"] = "jupyter notebook"
aliases["pyserv2"] = "python2 -m SimpleHTTPServer"
aliases["pyserv"] = "python3 -m http.server"
aliases["nt"] = "nosetests"
aliases["mn"] = "python manage.py"

def _getpip():
    wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py && rm get-pip.py
aliases["getpip"] = _getpip

aliases["pf"] = 'pip freeze'

def _pfg(args):
    pip freeze | rg @(' '.join(args))
aliases["pfg"] = _pfg

aliases["pv"] = 'pyenv version'
aliases["pvs"] = 'pyenv versions --bare'
aliases["f"] = "flask"

def _ve():
    echo PYENV_VERSION: $PYENV_VERSION
    echo VIRTUAL_ENV: $VIRTUAL_ENV
    echo pyenv version:
    pyenv version
aliases["ve"] = _ve

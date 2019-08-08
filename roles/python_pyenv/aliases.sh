alias jpnb="jupyter notebook"
alias pyserv2="python2 -m SimpleHTTPServer"
alias pyserv="python3 -m http.server"
alias nt="nosetests"
alias mn="python manage.py"
alias ipy="ipython"

alias getpip="wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py && rm get-pip.py"

alias pf='pip freeze'

alias pfg="pip freeze | rg"

alias py='python3'
alias pv='pyenv version'
alias pvs='pyenv versions --bare'
alias f="flask"

function ve() {
    echo PYENV_VERSION: ${PYENV_VERSION-<undefined>}
    echo VIRTUAL_ENV: ${VIRTUAL_ENV-<undefined>}
    echo pyenv version:
    pyenv version
}

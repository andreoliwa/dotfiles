alias py="python"
alias py3="python3"
alias ipy="ipython"
alias ipynb="ipython notebook"
alias jpnb="jupyter notebook"
alias pyserv2="python2 -m SimpleHTTPServer"
alias pyserv="python3 -m http.server"
alias pt="py.test"
alias nt="nosetests"
alias mn="python manage.py"
alias pipgrep="pip freeze | grep -i "
alias getpip="wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py && rm get-pip.py"

# Conda environments
alias condaclean="conda clean -tipsy"
alias mkenv="conda create python=3 ipython jupyter pip -n "
alias mkenv2="conda create python=2 ipython jupyter pip -n "
alias rmenv="conda remove --all --name "
alias lsenv="conda info -e"
alias wo="source activate"
alias de="source deactivate"

alias pf='pip freeze'
alias wk=workon

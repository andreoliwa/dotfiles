#!/bin/bash
usage() {
	echo "Usage: $(basename $0) [options]
Type here your brief description of the shell script.

OPTIONS
-h  Help"
	exit $1
}

while getopts "h" V_ARG ; do
	case $V_ARG in
	h)	usage 1 ;;
	?)	usage 2 ;;
	esac
done

cd ~/src
mv myflaskapp/.git ./xxx
rm -rf myflaskapp
cookiecutter cookiecutter-flask --no-input
mv ./xxx myflaskapp/.git

# chain = ls['-A1'] | grep['-v', '^\.git$']
# ls -A1 | grep -v '^\.git$' | xargs -L 1 rm -rf

# mv myflaskapp old_myflaskapp
# ls -la

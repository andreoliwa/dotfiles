#!/usr/bin/env bash
usage() {
	echo "Usage: $(basename $0) <MINUTES> <CACHE_FILE> <COMMAND AND ARGUMENTS>
Run <COMMAND AND ARGUMENTS> if <CACHE_FILE> does not exist or hasn't been touched in for <MINUTES> minutes."
	exit $1
}

DEBUG=

[[ -n $DEBUG ]] && echo "   >> Number of arguments = $#"
MINUTES=$1
shift
CACHE_FILE=$1
shift
COMMAND_WITH_ARGS="$*"
[[ -n $DEBUG ]] && echo "   >> Minutes = $MINUTES"
[[ -n $DEBUG ]] && echo "   >> Cache file = $CACHE_FILE"
[[ -n $DEBUG ]] && echo "   >> Command = $COMMAND_WITH_ARGS"

BASENAME=$(basename $CACHE_FILE)
DIRNAME=$(dirname $CACHE_FILE)

SHOULD_RUN=
if [[ ! -f $CACHE_FILE ]]; then
    [[ -n $DEBUG ]] && echo "   >> Cache file does not exist, will run command"
    SHOULD_RUN=1
elif [[ -n "$(find $DIRNAME -maxdepth 1 -iname $BASENAME -cmin +$MINUTES)" ]]; then
    [[ -n $DEBUG ]] && echo "   >> Cache file is older than $MINUTES minutes, will run command"
    SHOULD_RUN=1
else
    [[ -n $DEBUG ]] && echo "   >> Not enough time has passed since last run"
fi

if [[ -n $SHOULD_RUN ]]; then
    [[ -n $DEBUG ]] && echo "   >> Run the command with arguments"
    eval "$COMMAND_WITH_ARGS"

    RESULT=$?
    if [[ $RESULT -eq 0 ]]; then
        [[ -n $DEBUG ]] && echo "   >> Command was successful, touch the file"
        touch $CACHE_FILE
    else
        [[ -n $DEBUG ]] && echo "   >> Command failed, file stays the same, return the failed result"
        exit $RESULT
    fi
fi
[[ -n $DEBUG ]] && ls -l $CACHE_FILE
exit 0

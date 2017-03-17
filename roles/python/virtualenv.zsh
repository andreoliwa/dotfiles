# https://github.com/zsh-users/prezto/tree/master/modules/python
export PROJECT_HOME="$HOME/Code"

# http://virtualenvwrapper.readthedocs.io/en/latest/tips.html#automatically-run-workon-when-entering-a-directory
# https://hmarr.com/2010/jan/19/making-virtualenv-play-nice-with-git/
# https://gist.github.com/gibatronic/de66e3841b981798e6c1#file-workit-bash-L4
function check_for_virtual_env {
  [ -d .git ] || git rev-parse --git-dir &> /dev/null

  if [ $? -eq 0 ]; then
    local ENV_NAME=`basename \`pwd\``

    if [ "${VIRTUAL_ENV##*/}" != $ENV_NAME ] && [ -e $WORKON_HOME/$ENV_NAME/bin/activate ]; then
      workon $ENV_NAME && export CD_VIRTUAL_ENV=$ENV_NAME
    fi
  elif [ $CD_VIRTUAL_ENV ]; then
    deactivate && unset CD_VIRTUAL_ENV
  fi
}

function cd {
  builtin cd "$@" && check_for_virtual_env
}

check_for_virtual_env

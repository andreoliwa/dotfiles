alias dk="docker "
alias dklog="docker logs -f --tail 100 "
alias dkl="docker logs -f --tail 100 "
alias dkdf="dk system df"
# Stop and remove a single container
alias dkrm='docker rm -f '
# Stop and remove all running containers
alias dkrm!='docker rm -f $(docker ps -a -q)'

alias d="docker"
alias dp="docker ps"

alias dc="docker-compose"
alias dcup="docker-compose up -d "
alias dcrun="docker-compose run --rm "
function dcdebug {
  docker-compose kill $1
  docker-compose run --service-ports $1
}
# Stop and recreate a container
alias dcre="docker-compose up -d --force-recreate --no-deps "
alias dcl="docker-compose logs -f --tail 100 "

alias ds="docker-sync"
alias dss="docker-sync start"
alias dsx="docker-sync stop"

alias dcbomb!="docker-compose down -v"

# Open bash in a container. Pass docker-compose name
function dcbash {
  docker-compose exec $1 /bin/bash
}

# Open bash in a container. Pass container name
function dkbash {
  docker exec -it $1 /bin/bash
}

# If the time difference assertion fails, your Mac VM clock might be out of sync.
# To sync the clock again:
# - Open a terminal inside the HyperKit VM under MacOS:
#     screen ~/Library/Containers/com.docker.docker/Data/com.docker.driver.amd64-linux/tty
# - Sync the current time:
#     ntpd -d -q -n -p pool.ntp.org

# - To finish it, press Control + A then, k and confirm with `y`
# - To detach the session and keep it running in the background, press Control + A, then D.
#   And to re-attach use screen -r without the socket file (if you use it multiple screens will run and mess up)
#   with how you read data.

# Example of output when the clock is out of sync:
# linuxkit-025000000001:~# ntpd -d -q -n -p pool.ntp.org
# ntpd: sending query to 213.202.247.29
# ntpd: reply from 213.202.247.29: offset:-13.070072 delay:0.015113 status:0x24 strat:2 refid:0x08119582
#     rootdelay:0.013642 reach:0x01
# ntpd: sending query to 213.202.247.29
# ntpd: reply from 213.202.247.29: offset:-13.070861 delay:0.015031 status:0x24 strat:2 refid:0x08119582
#     rootdelay:0.013642 reach:0x03
# ntpd: setting time to 2018-01-29 14:40:34.016203 (offset -13.070861s)

# See https://stackoverflow.com/a/38133871/1391315

function docker_tty {
  cmd="screen $(find ~/Library/Containers/com.docker.docker -name tty)"
  echo $cmd
  echo
  echo "To finish the session, press Control + A then, k and confirm with 'y'"
  echo "To detach the session and keep it running in the background, press Control + A, then D."
  echo
  echo "Press any key to open screen or Ctrl-C to stop"
  read -n 1 -s
  $cmd
}
alias docker-tty="docker_tty"

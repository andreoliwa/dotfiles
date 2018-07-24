aliases["dk"] = "docker "
aliases["dklog"] = "docker logs -f --tail 100 "
aliases["dkl"] = "docker logs -f --tail 100 "
aliases["dkdf"] = "dk system df"

aliases["dc"] = "docker-compose"
aliases["dcup"] = "docker-compose up -d "
aliases["dcrun"] = "docker-compose run --rm "

def _dcdebug(args):
  docker-compose kill @(args[0])
  docker-compose run --service-ports @(args[0])
aliases["dcdebug"] = _dcdebug

# Stop and recreate a container
aliases["dcreup"] = "docker-compose up -d --force-recreate --no-deps "
aliases["dclog"] = "docker-compose logs -f --tail 100 "
aliases["dcl"] = "docker-compose logs -f --tail 100 "

aliases["ds"] = "docker-sync"
aliases["dss"] = "docker-sync start"
aliases["dsx"] = "docker-sync stop"

aliases["dcbomb!"] = "docker-compose down -v"

# Stop running containers and remove them
aliases["dclean"] = "docker-clean --stop --containers"

# Open bash in a container. Pass docker-compose name
def _dcbash(args):
  docker-compose exec @(args[0]) /bin/bash
aliases["dcbash"] = _dcbash

# Open bash in a container. Pass container name
def _dkbash(args):
  docker exec -it @(args[0]) /bin/bash
aliases["dkbash"] = _dkbash

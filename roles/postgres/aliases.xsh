def _mydb_start():
    echo "More info about initialization: https://store.docker.com/images/postgres"
    docker-compose -f ~/dotfiles/roles/postgres/docker-compose.yml up -d
    docker ps
aliases["mydb_start"] = _mydb_start

def _mydb_stop():
    docker-compose -f ~/dotfiles/roles/postgres/docker-compose.yml stop
    docker ps
aliases["mydb_stop"] = _mydb_stop

def _mydb_backup():
    mkdir -p ~/Backup
    docker run --rm --volumes-from postgres-96 -v ~/Backup:/backup busybox tar cvf "/backup/postgres-96_$(date -u +"%Y-%m-%d_%H-%M-%S").tar" /var/lib/postgresql/data
aliases["mydb_backup"] = _mydb_backup

def _mydb_restore():
    echo 'Manual process. See https://stackoverflow.com/a/23778599/1391315'
    echo 'sudo docker run --rm --volumes-from DATA2 -v $(pwd):/backup busybox tar xvf /backup/backup.tar'
aliases["mydb_restore"] = _mydb_restore

def _mydb_psql(args):
    docker exec -it postgres-96 psql -U postgres @(' '.join(args))
aliases["mydb_psql"] = _mydb_psql

# If the real psql client is not installed on this host, create an alias
if !(which psql 1>/dev/null 2>&1).returncode:
    aliases["psql"] = _mydb_psql

def _mydb_create(args):
    user_name = args[0]
    if not user_name:
        echo 'Provide a username. E.g.: mydb_create my_user'
        return

    echo "Paste these commands in psql below:"
    echo
    echo "CREATE USER ${user_name};"
    echo "ALTER USER ${user_name} WITH PASSWORD '${user_name}';"
    echo "CREATE DATABASE ${user_name};"
    echo "GRANT ALL PRIVILEGES ON DATABASE ${user_name} TO ${user_name};"
    echo
    mydb_psql
aliases["mydb_create"] = _mydb_create


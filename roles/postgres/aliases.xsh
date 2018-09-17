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
    print(f"CREATE USER {user_name};")
    print(f"ALTER USER {user_name} WITH PASSWORD '{user_name}';")
    print(f"CREATE DATABASE {user_name};")
    print(f"GRANT ALL PRIVILEGES ON DATABASE {user_name} TO {user_name};")
    echo
    mydb_psql
aliases["mydb_create"] = _mydb_create


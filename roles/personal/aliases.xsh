aliases['pc'] = "pycharm-cli"

def _mydb_create(args):
    # TODO feat: create a command: postgresx user
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
    cd ~/container-apps
    invoke db-connect --psql
aliases["mydb_create"] = _mydb_create

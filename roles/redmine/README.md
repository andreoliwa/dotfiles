# Redmine

-   Docker Hub: https://hub.docker.com/_/redmine
-   GitHub: https://github.com/docker-library/redmine
-   Docs: https://github.com/docker-library/docs/tree/master/redmine

# Setup

-   Spin up the [shared PostgreSQL](../postgres/docker-compose.yml) instance with `docker-find yml postgres up -d`
-   Run `mydb_create redmine`
-   `pgcli postgresql://postgres:$POSTGRES_PASSWORD@localhost:7710`
-   Create the redmine user with:
    ```sql
    CREATE USER redmine;
    ALTER USER redmine WITH PASSWORD 'redmine';
    CREATE DATABASE redmine;
    GRANT ALL PRIVILEGES ON DATABASE redmine TO redmine;
    ```
-   Spin up Redmine with `docker-compose up` or `docker-find yml redmine up`
-   Wait for the server to come up, then [login with the default admin/admin user/pass](https://github.com/docker-library/docs/tree/master/redmine#accessing-the-application)
-   Start using Redmine: Change the password, create users, create projects...

# https://git.tt-rss.org/fox/tt-rss/wiki/InstallationNotes

# https://github.com/docker-library/docs/blob/master/php/README.md#with-apache
FROM php:7.2-apache
RUN apt-get update
ENV TERM xterm-256color

# Install PostgreSQL PDO https://github.com/docker-library/php/issues/221#issuecomment-254153971
RUN apt-get install -y libpq-dev cron sudo && \
    docker-php-ext-configure pgsql -with-pgsql=/usr/local/pgsql && \
    docker-php-ext-install pdo pdo_pgsql pgsql && \
    groupadd ttrss -g 1001 && \
    useradd ttrss -m -u 1001 -g ttrss

# https://github.com/docker-library/php/blob/d97098c8c6af46ae1211e65ff052278ab39ba45c/7.2/stretch/apache/Dockerfile
ENV APACHE_RUN_GROUP=ttrss
ENV APACHE_RUN_USER=ttrss

# https://git.tt-rss.org/fox/tt-rss/wiki/UpdatingFeeds
# https://serverfault.com/questions/449651/why-is-my-crontab-not-working-and-how-can-i-troubleshoot-it
COPY ./cron.allow /etc/
COPY ./cron-update-feeds /etc/cron.d/
COPY ./start-cron-apache.sh /usr/local/bin/

COPY --chown=ttrss:ttrss . /var/www/html/

CMD ["start-cron-apache.sh"]

FROM redmine:4

# Use custom themes (manually downloaded to the themes/ subdir)
COPY themes/ /usr/src/redmine/public/custom-themes/

# Add custom themes to existing ones
RUN mv /usr/src/redmine/public/custom-themes/* /usr/src/redmine/public/themes/ && \
    chown -R redmine:redmine /usr/src/redmine/public/

# https://nodered.org/docs/platforms/docker
FROM nodered/node-red-docker:latest

# Local forked nodes are in this directory
COPY var/nodes /usr/src/nodes/

# https://github.com/oliverlorenz/node-red-trello
RUN npm install node-red-contrib-trello \
    # https://flows.nodered.org/node/node-red-contrib-python3-function
    node-red-contrib-python3-function \
    # https://github.com/GMBN/node-red-contrib-readdir
    /usr/src/nodes/node-red-contrib-readdir

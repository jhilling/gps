#!/bin/bash

# James Hilling September 2018

# Tool to provide some abstractions around running the gps-server(s)
# docker containers / associated components
# e.g. gpsserver start|stop|status
# Call with no args to get a full list of commands

# Make sure you have built the Docker image first (see Makefile)

IMAGE="gps-server:latest"

VOLUME="gps-data"
VOLUME_DEST="/root/GPS_Tracks"

# The native port the server is listening on
DP=5000

PORT="$DP:$DP"

TESTFILE="./sample-data/trk 2018-09-05 18-04-59-1 - ACTIVE LOG.GPX"


build() {
	exec docker build --no-cache --tag "$IMAGE"  .
}


# Check have the docker image, build it if not
if ! docker inspect "$IMAGE" >& /dev/null ; then
    echo "ERROR: $IMAGE not found - will try to build it now"
    build
fi


# Start single server on ephemeral port
start() {

	if [ $# -eq 0 ] ; then
		echo "Start server on ephemeral port"
		exec docker run --rm --detach --volume "$VOLUME:$VOLUME_DEST" -P "$IMAGE"
		
	elif [ $1 == "default" ] ; then
		echo "Start server on default port $DP"
		exec docker run --rm --detach --volume "$VOLUME:$VOLUME_DEST" -p "$DP:$DP" "$IMAGE"
	else
		echo "Start server on port $1"
		exec docker run --rm --detach --volume "$VOLUME:$VOLUME_DEST" -p "$1:$DP" "$IMAGE"
	fi
}

# Stop all gps-server containers
stop() {
	exec docker stop $(docker ps --filter="ancestor=$IMAGE" --filter="status=running" --format "{{.ID}}")
}

status() {
	echo "gps-server containers"
	exec docker ps --filter="ancestor=$IMAGE"
}

# Port mappings of all gps-server containers
port() {
	exec docker ps --filter="ancestor=$IMAGE" --filter="status=running" --format "{{.ID}} {{.Ports}}"
}

# List containers using the data volume
list-data() {
	echo "Containers using $VOLUME"
	exec docker ps --filter="volume=$VOLUME"
}

# Execute a query using curl against ONE of the running gps-servers
# Supply port and optional count
curl() {
	# Find a container to send the request to
	#GPX_PORT=$(docker ps --filter="ancestor=$IMAGE" --filter="status=running" --format "{{.Ports}}" | sed -e 's|.*:\(.*\)->.*|\1|' | head -1)

	GPX_PORT="$1"
	COUNT="${2:-1}"

	echo "Selected port $GPX_PORT"
	echo "Selected count $COUNT"

	# Can do application/json or text
	#FORMAT="application/json"
	FORMAT="text"

	for ((i=0;i<$COUNT;i++))
	do 
		command curl -X GET -H "accept: $FORMAT" -H "Content-Type: application/xml" \
			--data "@$TESTFILE" \
			"http://127.0.0.1:$GPX_PORT/text" &
	done

	wait
	
	echo "$COUNT requests done"
}

inspect-data() {
	echo "Start container to inspect state of persistent volume"
	exec docker run --rm -it --volume "$VOLUME:$VOLUME_DEST" --workdir "$VOLUME_DEST" ubuntu:latest
}

proxy() {
	exec docker run --rm -d -v $PWD/haproxy:/usr/local/etc/haproxy:ro -p 80:80 \
		-p 443:443 --name web-gateway haproxy:latest
}

# Check configuration of proxy
proxy-check() {
	exec docker run --rm -it -d -v $PWD/haproxy:/usr/local/etc/haproxy:ro haproxy:latest -c -f /usr/local/etc/haproxy/haproxy.cfg
}

# Create a load balanced swarm of servers using the compose file
# Optional instance name can be passed, defaults to 'test'
swarm() {
	NAME=${1:-test}

	docker swarm init
	docker stack deploy --compose-file=docker-compose.yml "$NAME"

	echo "Deployed stack $NAME"
}

# update the proxy container
# e.g. to change the port
# gpsserver swarm-update test --publish-rm  80
# gpsserver swarm-update test --publish-add 8000:80
# see: docker service update --help
swarm-update() {

	NAME="$1"
	shift

	docker service update ${NAME}_proxy "$@"
	docker service ls
}

# Scale the number of workers up or down
# e.g. gpsserver swarm-scale test 12
swarm-scale() {
	NAME="$1"
	shift
	docker service scale ${NAME}_gps-server=$1
	docker service ls
}

########################################################################

if [ $# -eq 0 ] ; then

cat << EOF
Please supply a command:
EOF

	# List what we can do by listing the functions in this file
	compgen -A function

else
	# Here we (try and) call a function with the name of the arg
	# passed in

	CMD="$1"
	shift

	# Call the command with any args
	"$CMD" "$@"
fi



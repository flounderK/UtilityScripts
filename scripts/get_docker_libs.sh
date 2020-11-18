#!/bin/sh

# This is a quick script to pull the ld-linux.so and libc.so libraries out of a docker container
#

usage () {
	echo -e "Usage: $0 <docker_image>"
}


if [ -z "$1" ]; then
	usage $@
	exit
fi

cont_id=$(docker run -dit $1)

ld_path=$(docker exec -it $cont_id bash -c 'ls /lib/**/ld-*.so' | tr -d '\r')
ld_file=$(echo $ld_path | grep --color=never -Po '(?<=/)[^/]+\.so')
libc_path=$(docker exec -it $cont_id bash -c 'ls /lib/**/libc-*.so' | tr -d '\r')
libc_file=$(echo $libc_path | grep --color=never -Po '(?<=/)[^/]+\.so')

cont_name=$(docker ps --filter="id=$cont_id" --format='{{.Names}}')

docker cp "$cont_id:$ld_path" $ld_file
docker cp "$cont_id:$libc_path" $libc_file

docker container stop $cont_id >/dev/null
docker container rm $cont_id >/dev/null



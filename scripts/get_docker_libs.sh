#!/bin/sh

# This is a quick script to pull the ld-linux.so and libc.so libraries out of a docker container
#

usage () {
	echo "Usage: $0 <docker_image>"
	echo "    example: $0 'ubuntu:18.04'"
}


if [ -z "$1" ]; then
	usage $@
	exit
fi

cont_id=$(docker run -dit $1)

ld_path=$(docker exec -it $cont_id sh -c 'ls -1 /lib/**/ld-*.so* /usr/lib/**/ld-*.so* 2>/dev/null | head -n1' | tr -d '\r')
ld_file=$(echo $ld_path | grep --color=never -Po '(?<=/)[^/]+\.so(\.[^/]+)?')
libc_path=$(docker exec -it $cont_id sh -c 'ls -1 /lib/**/libc-*.so* /lib/**/libc.so* /usr/lib/**/libc-*.so* /usr/lib/**/libc.so* 2>/dev/null | head -n1' | tr -d '\r')
libc_file=$(echo $libc_path | grep --color=never -Po '(?<=/)[^/]+\.so(\.[^/]+)?')

cont_name=$(docker ps --filter="id=$cont_id" --format='{{.Names}}')
echo "ld $ld_path"
echo "libc $libc_path"

docker cp "$cont_id:$ld_path" $ld_file
docker cp "$cont_id:$libc_path" $libc_file

docker container stop $cont_id >/dev/null
docker container rm $cont_id >/dev/null



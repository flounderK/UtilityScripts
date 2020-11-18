#!/bin/sh


usage ()
{
	echo "Usage: $0 <binary> [interpreter]"
}


if [ -z "$1" ]; then
	usage $@
	exit
fi

if [ ! -z "$2" ]; then
	interpreter=$2
else
	interpreter=$(ls ld-*.so)
fi


patchelf --set-interpreter "$interpreter" "$1"

ln -s libc-*.so libc.so.6

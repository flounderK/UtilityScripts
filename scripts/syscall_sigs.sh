#!/bin/sh

if [ "$#" -lt 1 ];then
	echo "Search the linux source tree for syscall definitions"
	echo "Usage: $0 <path to linux source>"
	exit 0
fi


find $1 -type f -iname '*.c' -o -iname '*.h' | xargs sed -nr '/SYSCALL_DEFINE[[:digit:]]+[(]/{
        :a
        /[)]/{
            p;
            d;
        };
        N;
        s/\n//g;
        s/\t+/ /g;
        s/ +/ /g;
        ba
}' | grep -v '^#define' | grep -v 'foobar' | grep -v 'SYSCALL_DEFINE0()'


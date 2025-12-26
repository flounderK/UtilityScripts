#!/bin/bash


function find_elf_files () {
	if [ $# -lt 1 ]; then
		POSITIONAL=(".")
	else
		POSITIONAL=("${@}")
	fi
	find ${POSITIONAL[@]} -type f | xargs -d '\n' -I{} bash -c 'A=$(head -c4 "{}" | grep "ELF"); if [ ! -z "$A" ]; then echo "{}"; fi'
}

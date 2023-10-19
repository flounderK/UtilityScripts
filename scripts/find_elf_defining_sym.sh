#!/bin/bash

function _sym_name_in_elf () {
	if [ $# -lt 2 ]; then
		echo "Usage: _sym_name_in_elf <file-path> <SYM_NAME> [VERBOSE]"
		return
	fi

	FILE_PATH="$1"
	SYM_NAME="$2"
	READELF_LINES="$(readelf -sW "$FILE_PATH" 2>/dev/null | grep "$SYM_NAME")"
	if [ $# -ge 3 ] && [ "$3" = "VERBOSE" ]; then
		PRINT_SYMS=1
	else
		PRINT_SYMS=0
	fi

	if [ $PRINT_SYMS -eq 1 ] && [ ! -z "$READELF_LINES" ]; then
		echo "$FILE_PATH"
	fi

	# echo "$READELF_LINES"
	OLD_IFS=$IFS
	# separate by newline instead of default for the loop
	IFS=$'\n'
	WAS_FOUND=0
	for READELF_LINE in $(echo "$READELF_LINES" | tr -s " "); do
		# echo "readelf line: '$READELF_LINE'"
		# extract the symbol offset from the readelf line
		SYM_OFF_STR=$(echo "$READELF_LINE" | cut -d " " -f3)
		# echo "Sym off str: '$SYM_OFF_STR'"
		SYM_OFF=$((0x$SYM_OFF_STR))
		if [ "$SYM_OFF" != 0 ]; then
			WAS_FOUND=1
			if [ $PRINT_SYMS -eq 1 ]; then
				echo "$READELF_LINE"
			else
				break;
			fi
		fi
	done

	if [ $WAS_FOUND -eq 1 ] && [ $PRINT_SYMS -eq 0 ]; then
		echo "$FILE_PATH"
	fi
	IFS=$OLD_IFS
}

function find_elf_defining_sym () {
	if [ $# -lt 1 ]; then
		echo "Usage: find_elf_defining_sym <sym_name> [VERBOSE]"
		return
	fi
	SYM_NAME="$1"

	# export the function _sym_name_in_elf to make it available tobash started by xargs
	export -f _sym_name_in_elf
	# find files that contain the sym name first with grep and gawk,
	# then run _sym_name_in_elf for each file using xargs
	# gawk 'match($0, /Binary file (.+) matches/, a) { print a[1] }'
	# it turns out that regular expressions being run against error output is unstable and non-portable, who knew?
	find . -type f | xargs -d '\n' grep -l "$SYM_NAME" 2>/dev/null | xargs -d '\n' -I{} bash -c '_sym_name_in_elf $@' bash {} $@
}

find_elf_defining_sym $@

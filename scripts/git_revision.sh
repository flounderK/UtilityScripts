#!/bin/bash


COMMIT_DATE=$(git show -s --format=%ci)

ORIGINAL_DIR=$(pwd)

# needed to make find work correctly with spaces in the path names.
# Also has to be bash now
PATHS=()
while IFS=  read -r -d $'\0'; do
    PATHS+=("$REPLY")
done < <(find . -mindepth 2 -type d -name '.git' -print0)

for DIRECTORY in "${PATHS[@]}"; do
	DIRPATH="$(dirname "$DIRECTORY")"
	echo "DBGLOG: $DIRECTORY"
	echo "DBGLOG: changing to '$DIRPATH'"
	echo ""
	cd "$DIRPATH"
	# TODO: might need to pick tags if present
	COMMIT_HASH=$(git rev-list --max-count=1 --all --before="$COMMIT_DATE")
	git checkout "$COMMIT_HASH"
	# TODO: might want to do an aggressive git clean here
	# git status

	cd "$ORIGINAL_DIR"
done

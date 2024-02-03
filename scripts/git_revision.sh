#!/bin/bash

# This script is supposed to sync git revisions correctly for projects like chromium that have git repos that aren't git submodules, but are underneath one main repo. It tries to sync by date right now, but is still a work in progress
COMMIT_DATE=$(git show -s --format=%ci)

ORIGINAL_DIR=$(pwd)

# needed to make find work correctly with spaces in the path names.
# Also has to be bash now
PATHS=()
while IFS=  read -r -d $'\0' -u 9; do
	echo "$REPLY"
    PATHS+=("$REPLY")
done 9< <(find . -mindepth 2 -type d -name '.git' -print0)

for DIRECTORY in "${PATHS[@]}"; do
	DIRPATH="$(dirname "$DIRECTORY")"
	echo "DBGLOG: $DIRECTORY"
	echo "DBGLOG: changing to '$DIRPATH'"
	echo ""
	cd "$DIRPATH"
	# TODO: might need to pick tags if present
	COMMIT_HASH=$(git rev-list --max-count=1 --all --before="$COMMIT_DATE")
	echo "found hash ${COMMIT_HASH}"
	git checkout "$COMMIT_HASH"
	# TODO: might want to do an aggressive git clean here
	# git status

	cd "$ORIGINAL_DIR"
done

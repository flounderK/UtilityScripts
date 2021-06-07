#!/bin/sh

install ./scripts/* ~/.local/bin/
git submodule init
git submodule update
find . -mindepth 2 -type f -iname 'install.sh' | xargs -I '{}' sh -c "{}"

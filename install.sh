#!/bin/sh

install ./scripts/* ~/.local/bin/
find . -mindepth 2 -type f -iname 'install.sh' | xargs -I '{}' sh -c "{}"

# UtilityScripts
Scripts that I use frequently. You know, like utilities.

simplescraper:
    A very basic webscraper. Intended for archiving websites including all of the content/media/scripts that the site is hosting for that specific page. *note*, archiving medium.com posts is doable, but one of the js scripts changes the page to a 404 error if the site is not actually being hosted on medium.

syscall_lookup:
    Utilizes pwntools to lookup which syscall a value maps to. Multiple architectures are supported using the -a flag

get_docker_libs.sh:
    Pull down the specified docker container and copy its ld-x.xx.so and libc-x.xx.so to your current directory.

ld_patch.sh:
    Patch the specified binary to use the ld-*.so in your current directory. Just remember to LD_PRELOAD or LD_LOAD_LIBRARY the correct libc when launching the binary.


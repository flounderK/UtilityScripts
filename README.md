# UtilityScripts
Scripts that I use frequently. You know, like utilities.

To install all of them, just run 
```bash
./install.sh
```

### __syscall_lookup__
Utilizes pwntools to lookup which syscall a value maps to. Multiple architectures are supported using the -a flag

### __get_docker_libs.sh__
Pull down the specified docker container and copy its ld-x.xx.so and libc-x.xx.so to your current directory.

### __ld_patch.sh__
Patch the specified binary to use the ld-*.so in your current directory. Just remember to LD_PRELOAD or LD_LOAD_LIBRARY the correct libc when launching the binary.


## __SimpleScraper__
A very basic webscraper. Intended for archiving websites including all of the content/media/scripts that the site is hosting for that specific page. *note*, archiving medium.com posts is doable, but one of the js scripts changes the page to a 404 error if the site is not actually being hosted on medium.


## __TypeConverter__
A basic script to perform c type conversions from the command line.


## __mktemplate__
General purpose file templating tool that utilizes the Jinja2 templating module.

I find myself needing to make scripts that are fairly boilerplate with a few variables that need to be changed, especially when making scripts for CTF solutions. Here is my attempt to streamline the process.


To install just run
```bash
./install.sh
```


```bash
Examples:
        mktemplate -o ./someone_elses_templates/ install pretty_template1 pretty_template2
        mktemplate copy pwn --binary-path binary --remote-host=abc.xyz
        mktemplate create newtemplate
        mktemplate list
        mktemplate -t ./someone_elses_templates/ list
```

For examples of template directories, check out https://github.com/flounderk/mytemplates


## __BinClipper__
Modify binary files from the command line

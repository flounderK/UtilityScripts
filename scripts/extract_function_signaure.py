
import subprocess
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()

proc = subprocess.run(["/usr/bin/clang", "-E", args.file],
                      capture_output=True, timeout=5)

c = proc.stdout
c = c.decode()

# cut newlines
c = re.sub("\n", " ", c)

# squeeze spacing
c = re.sub("\s+", " ", c)

# remove headers
c = re.sub('#\s+\d+\s+"[^"]+"(\s+\d+)*', "", c)

# TODO: extern check might not always be accurate
lines = [i for i in c.split(";") if i.find("extern") != -1 and i != '']


sig_lines = []
for line in lines:
    line = re.sub("__(asm|attribute)__\s*\([^)]+\)+", "", line)
    line = re.sub("__(extension|inline)__", "", line)
    line = re.sub("__restrict", "", line)
    # squeeze spacing
    line = re.sub("\s+", " ", line)
    sig_lines.append(line.strip())

for line in sig_lines:
    print(line)

import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("old_filepath", help="path to old dpkg -l output")
parser.add_argument("new_filepath", help="path to new dpkg -l output")
args = parser.parse_args()

dpkg_rexp = re.compile("^(?P<STATUS>\S+)\s+(?P<NAME>\S+)\s+(?P<VERSION>\S+)\s+(?P<ARCH>\S+)\s+(?P<DESC>.+)$")


old_filepath = args.old_filepath
new_filepath = args.new_filepath

with open(old_filepath, "r") as f:
    old_package_lines = f.read().splitlines()

with open(new_filepath, "r") as f:
    new_package_lines = f.read().splitlines()


old_matches = [re.match(dpkg_rexp, a) for a in old_package_lines]
old_entries = [i.groupdict() for i in old_matches if i is not None]

new_matches = [re.match(dpkg_rexp, a) for a in new_package_lines]
new_entries = [i.groupdict() for i in new_matches if i is not None]

old_names = set([i['NAME'] for i in old_entries])
new_names = set([i['NAME'] for i in new_entries])

diff = list(old_names.difference(new_names))
diff.sort()
for i in diff:
    print(i)

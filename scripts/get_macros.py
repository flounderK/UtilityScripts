#!/usr/bin/env python3
import re
import argparse
import os
import json

parser = argparse.ArgumentParser()

parser.add_argument("path", help="path to a file to get macros from")
parser.add_argument("-s", "--singleline", default=False, action="store_true",
                    help="print singleline macros")
parser.add_argument("-m", "--multiline", default=False, action="store_true",
                    help="print multiline macros")
parser.add_argument("-j", "--dump-json", default=False, action="store_true",
                    help="dump out macros as json")
parser.add_argument("-p", "--python-assignments", default=False, action="store_true",
                    help="print out single line macros as assignments")
args = parser.parse_args()

# (?m)  -- inline MULTILINE FLAG
# ^#define  -- start of string and literal values
# (   -- group
# (?:  -- non captured group
#    .*\\\r?\n   -- any value 0 or more times, literal \, optional \r, literal \n
# )*  -- 0 or more of non captured group
# .*)$  -- the rest of the macro after '#define' if it is single line, or
#         the rest of the last line of the macro if it is multi line
rexp = re.compile(r'(?m)^#define ((?:.*\\\r?\n)*.*)$')
with open(os.path.expanduser(args.path), 'r') as f:
    content = f.read()


matches = [i.groups()[0] for i in re.finditer(rexp, content)]
matches = [re.sub(r'(\t| +)', ' ', i) for i in matches]
split_matches = [i.split(' ', 1) for i in matches]
macro_map = dict([i if len(i) > 1 else i + [""] for i in split_matches])
single_line_macro_map = {k: v for k, v in macro_map.items() if '\n' not in v}

singleline = []
multiline = []
for i in matches:
    if '\n' in i:
        multiline.append(i)
    else:
        singleline.append(i)

if args.singleline is True:
    for i in singleline:
        print(i)
    print()

if args.multiline is True:
    for i in multiline:
        print(i)

if args.dump_json is True:
    print(json.dumps(macro_map, indent=2))

if args.python_assignments is True:
    for k, v in single_line_macro_map.items():
        if v == "":
            v = "None"
        print("%s = %s" % (k, v))



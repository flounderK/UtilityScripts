#!/usr/bin/env python3
import re
import argparse
import os
import json

parser = argparse.ArgumentParser()

parser.add_argument("path", help="path to a file to get macros from",
                    type=os.path.expanduser)
parser.add_argument("-s", "--singleline",
                    default=False, action="store_true",
                    help="print singleline macros")
parser.add_argument("-m", "--multiline",
                    default=False, action="store_true",
                    help="print multiline macros")
parser.add_argument("-j", "--dump-json",
                    default=False, action="store_true",
                    help="dump out macros as json")
parser.add_argument("-p", "--python-assignments",
                    default=False, action="store_true",
                    help="print out single line macros as assignments "
                         "compatible with python. strips comments")
parser.add_argument("-c", "--keep-comments",
                    default=False, action="store_true",
                    help="Don't strip comments from output ")
parser.add_argument("-d", "--keep-defines",
                    default=False, action="store_true",
                    help="Keep in '#defines'. Ignored for python")
args = parser.parse_args()


# (?m)  -- inline MULTILINE FLAG
# ^#define  -- start of string and literal values
# (   -- group
# (?:  -- non captured group
#    .*\\\r?\n   -- any value 0 or more times, literal \, optional \r, literal \n
# )*  -- 0 or more of non captured group
# .*)$  -- the rest of the macro after '#define' if it is single line, or
#         the rest of the last line of the macro if it is multi line
rexp = re.compile(r'(?m)^#define\s+((?:.*\\\r?\n)*.*)$')
multiline_comment_regex = re.compile(r"/\*[^*]*\*+(?:[^/*][^*]*\*+)*/")
with open(args.path, 'r') as f:
    content = f.read()


matches = [i.groups()[0] for i in re.finditer(rexp, content)]
# remove most of the whitespace that is present
matches = [re.sub(r'\\*\s+', ' ', i) for i in matches]
if args.keep_comments is False:
    matches = [re.sub(multiline_comment_regex, '', i) for i in matches]

# separate out the function like macros from the object like
split_matches = []
function_like = []
for i in matches:
    splt = i.split(' ', 1)
    if splt[0].find('(') > -1:
        function_like.append(i)
    else:
        split_matches.append(splt)

# split_matches = [i.split(' ', 1) for i in matches]
macro_map = dict([i if len(i) > 1 else i + [""] for i in split_matches])
python_repr_macro_map = {k: v for k, v in macro_map.items() if '\n' not in v}

define_string = ''
if args.keep_defines is True:
    define_string = '#define '

singleline = []
multiline = []
for i in matches:
    macrostring = define_string + i
    if '\n' in i:
        multiline.append(macrostring)
    else:
        singleline.append(macrostring)

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
    for k, v in python_repr_macro_map.items():
        if v == "":
            v = "None"
        print("%s = %s" % (k, v))
    print("\n# Function like macros")
    for i in function_like:
        print("# %s" % i)



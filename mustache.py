import json
import re
import sys

#
# Replace all template variables in input file with configured values
# from the JSON config. Template variables are distiguished by enclosing
# double braces. eg {{ template.variable }}. This would match templatevalue
# in JSON config {"template": {"variable": "templatevalue"}}
#
exitstatus = 0

def usage(rc =0):
    print(f'Usage: python3 {sys.argv[0]} jsonconfigfile inputfile')
    exit(rc)

# Just return the original key if no match
# Remember that you failed at exit time, exiting with status of 1
def badkey():
    global exitstatus
    exitstatus = 1
    return(f'{{{{ {keystr} }}}}')

def lookup(keylist, bat):
    car = keylist[0]
    if type(bat) is not dict or car not in bat:
        return badkey()

    if len(keylist) == 1:
        if type(bat[car]) is not str:
            return badkey()
        return bat[car]
    else:
        return lookup(keylist[1:], bat[car])

def repl(matchobj):
    global keystr
    keystr = matchobj.group(1)
    return lookup(keystr.split('.'), config)

def readfile(filename, readfunc, errorstr):
    try:
        with open(filename) as f:
            return readfunc(f)
    except Exception as ex:
        print(errorstr % filename)
        print(ex)
        usage(1)

if len(sys.argv) == 2 and sys.argv[1] == '-help':
    usage()

if len(sys.argv) != 3:
    usage(1)

config = readfile(sys.argv[1],
            lambda f: json.load(f),
            "Could not read json config file %s") 
moustache = readfile(sys.argv[2],
            lambda f: f.read(),
            "Could not read input file %s") 

#Echo the contents of the input file with the keys replaced with
#values from the json config
print(re.sub(r'\{\{\s*([\w\.]+)\s*\}\}',
            repl,
            moustache))

exit(exitstatus)

import json
import sys
import re
from datetime import datetime

#
# Merge any config items from fromConfig into toConfig that are not
# already in toConfig.
# Do not override any entries already present in toConfig
# Return the new toConfig that now includes all old items plus any new
# items from toConfig.
# JSONs must be compatible. You cannot assign new keys to a terminal string.
# Also maintain history of when you added a key to toConfig
#
exitstatus = 0
history_ts = datetime.now().replace(microsecond=0).isoformat()

def usage(rc =0):
    print(f'Usage: python3 {sys.argv[0]} fromconfigfile toconfigfile')
    exit(rc)

def prefix_str(prefix, key):
    return f"{prefix}.{key}" if prefix else key

def add_history(section, item, prefix):
    global to_config_dict
    if "history" not in to_config_dict:
        to_config_dict["history"] = {}
    if history_ts not in to_config_dict["history"]:
        to_config_dict["history"][history_ts] = {}
    if section not in to_config_dict["history"][history_ts]:
        to_config_dict["history"][history_ts][section] = {}
    to_config_dict["history"][history_ts][section] \
        [prefix_str(prefix, item[0])] = item[1]

def incompatible(item, prefix):
    global exitstatus
    add_history("incompatible", item, prefix)
    exitstatus = 1

def add_missing_item(to_config, item, prefix):
    add_history("insertions", item, prefix)
    to_config[item[0]] = item[1]

def merge(from_config_items, to_config, prefix):
    if len(from_config_items) == 0:
        return
    cat = from_config_items[0]

    if type(to_config) is not dict:
        #Attempting to insert a dict item in place of a string
        #We don't do restructuring (too confusing)
        incompatible(cat, prefix)
    elif cat[0] not in to_config:
        #Add item not found in to_config
        add_missing_item(to_config, cat, prefix)
    elif type(cat[1]) is dict:
        #Merge dicts if keys match
        merge(list(cat[1].items()), to_config[cat[0]], \
            prefix_str(prefix, cat[0]))
    elif type(to_config[cat[0]]) is dict:
        #Can't insert a string in place of a dict
        #Again, we complain when structures differ
        incompatible(cat, prefix)

    #Lather, rinse, repeat
    merge(from_config_items[1:], to_config, prefix)

def readfile(filename, readfunc, errorstr):
    try:
        with open(filename) as f:
            return readfunc(f)
    except Exception as ex:
        print(errorstr % filename)
        print(ex)
        usage(1)

# -h, -help, h, help all match
if len(sys.argv) == 2 and re.match('^-?h(elp)?$', sys.argv[1]) != None:
    usage()

if len(sys.argv) != 3:
    usage(1)

from_config_dict = readfile(sys.argv[1],
            lambda f: json.load(f),
            "Could not read json config file %s") 
to_config_dict = readfile(sys.argv[2],
            lambda f: json.load(f),
            "Could not read json config file %s") 

merge(list(from_config_dict.items()), to_config_dict, "")

print(json.dumps(to_config_dict,
            indent=2,
            sort_keys=True))
   
exit(exitstatus)

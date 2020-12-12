import json
import os
import os.path as osp

jsf = open("./spec2017_cmds.json")
js = json.load(jsf)
print(js)

new_js = dict()

source_dir = '/home/zyy/research-data/spec2017_20201126/benchspec/CPU/'

dirs = os.listdir(source_dir)

for d in dirs:
    for k, cmd in js.items():
        b = k.split('_')[0] + '_r'
        if b in d:
            new_js[k] = dict()
            new_js[k]['id'] = d
            new_js[k]['cmd'] = cmd

print(new_js)
with open("./spec2017_ids_cmds.json", 'w') as njsf:
    json.dump(new_js, njsf, indent=4, sort_keys=True)

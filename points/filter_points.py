import json
import sys


ver = '06'
weight_file = f"./resources/simpoint_cpt_desc/simpoints{ver}.json"
tag = 'icache_sensitive'
white_list = f"./points/{tag}.lst"

with open(weight_file) as f:
    js = dict(json.load(f))

new_js = {}
with open(white_list) as f:
    for line in f:
        workload, point = line.strip().split('/')
        print(workload,point)
        if workload not in new_js:
            new_js[workload] = {}
        new_js[workload][point] = js[workload][point]

print(new_js)
with open(f'resources/simpoint_cpt_desc/simpoints{ver}_{tag}.json', 'w') as f:
    json.dump(new_js, f, indent=4)

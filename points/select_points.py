import json

count_limit = 100
coverage_limit = 0.5

weight_file = "./resources/simpoint_cpt_desc/simpoints06.json"

with open(weight_file) as f:
    js = json.load(f)

new_js = {}

for workload, weights in js.items():
    cumm_weight = 0.0
    count = 0
    for point, weight in weights.items():
        cumm_weight += float(weight)
        count += 1
        print(workload, point, weight)
        if workload not in new_js:
            new_js[workload] = {}
        new_js[workload][point] = weight

        if count >= count_limit or cumm_weight >= coverage_limit:
            break
with open('./resources/simpoint_cpt_desc/simpoints06_cover0.5.json', 'w') as outf:
    json.dump(new_js, outf, indent=4)

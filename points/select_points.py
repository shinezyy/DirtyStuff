import json

count_limit = 2
coverage_limit = 0.5

ver = '06'
weight_file = f"./resources/simpoint_cpt_desc/simpoints{ver}.json"
test_set = 'int'

with open(weight_file) as f:
    js = json.load(f)

new_js = {}
files = []

bmks = []
if len(test_set):
    with open(f'points/spec{ver}_{test_set}.txt') as f:
        for line in f:
            bmks.append(line.strip())

for workload, weights in js.items():
    bmk = workload.split("_")[0]
    if len(bmks) and bmk not in bmks:
        continue
    cumm_weight = 0.0
    count = 0

    for point, weight in weights.items():
        cumm_weight += float(weight)
        count += 1
        print(workload, point, weight)
        files.append(f'{workload}_{point} {workload}_{point}_{weight}/0/')
        if workload not in new_js:
            new_js[workload] = {}
        new_js[workload][point] = weight

        if count >= count_limit or cumm_weight >= coverage_limit:
            break

n_chunks = 1
chunk_size = len(files) // n_chunks
for i in range(n_chunks):
    chunk = files[:chunk_size]
    with open(f'./resources/simpoint_cpt_desc/simpoints06{test_set}_cover{coverage_limit:.2f}_top{count_limit}.lst.{i}', 'w') \
            as outf:
        outf.write('\n'.join(chunk))
    files = files[chunk_size:]

with open(f'./resources/simpoint_cpt_desc/simpoints06{test_set}_cover{coverage_limit:.2f}_top{count_limit}.json', 'w') as outf:
    json.dump(new_js, outf, indent=4)

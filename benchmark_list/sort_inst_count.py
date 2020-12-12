import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', type=str, action='store', required=True)

args = parser.parse_args()

pairs = {}
with open(args.input) as f:
    for line in f:
        b, insts = line.strip().split(' ')
        pairs[b] = insts
sorted_pairs = {k: v for k, v in sorted(pairs.items(), key=lambda item: item[1])}
for pair, v in sorted_pairs.items():
    print(pair, v)


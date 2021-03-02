import os
import platform
import json


machine_config = '/home/zyy/.config/machine_state/dispatch.json'

def get_machine_hash(task='xiangshan'):
    hash_ids = {}
    with open(machine_config) as f:
        js = json.load(f)[task]
    cursor = 0
    for host in js:
        hash_ids[host] = []
        for i in range(0, js[host]['load']):
            hash_ids[host].append(cursor)
            cursor += 1
        print(host, hash_ids[host])
    hostname = platform.node()
    return hash_ids[hostname], cursor

def get_machine_threads(task='xiangshan'):
    with open(machine_config) as f:
        js = json.load(f)[task]
    hostname = platform.node()
    print(js)
    return int(js[hostname]["threads"])



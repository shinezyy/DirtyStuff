import sh
import os
import sys
import re
import os.path as osp
import argparse
from pprint import pprint
from multiprocessing import Pool

from common.simulator_task import SimulatorTask, task_wrapper
from common.task_tree import task_tree_to_batch_task
from common.simpoint_parser import parse_simpoint_analysis_file
from gem5tasks.typical_o3_config import TypicalO3Config

# NEMU batch

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--spec-version', help='`06` or `17`',
        type=str, action='store', required=True, choices=['06', '17'])
args = parser.parse_args()
ver = args.spec_version

TaskSummary = {}

exe = '/home51/zyy/projects/NEMU/build/riscv64-nemu-interpreter'
simpoint_dir = f'/home51/zyy/expri_results/simpoint_profile_{ver}'
avail_cpt_dir = f'/bigdata/zyy/checkpoints_profiles/betapoint_profile_{ver}'
top_output_dir = '/home51/zyy/expri_results/' # cpt dir
batch_task_name = f'nemu_take_simpoint_cpt_{ver}'
cpt_dir_pattern = re.compile(r'\d+')


def find_simpoint_analysis_files(d: str):
    for workload in os.listdir(d):
        point = osp.join(d, workload, 'simpoints0')
        weight = osp.join(d, workload, 'weights0')
        yield (workload, point, weight)

def get_avail_cpts(d):
    cpt_pattern = re.compile(r"_(\d+)_\.gz")
    avail_cpts = {}
    for workload in os.listdir(d):
        avail_cpts[workload] = {}
        workload_path = osp.join(d, workload)
        for cpt in os.listdir(workload_path):
            cpt_path = osp.join(workload_path, cpt)
            if not osp.isdir(cpt_path):
                continue
            cpt_files = os.listdir(cpt_path)
            if not len(cpt_files):
                continue
            cpt_file = cpt_files[0]
            m = cpt_pattern.match(cpt_file)
            assert m is not None
            insts_taken = int(m.group(1))
            avail_cpts[workload][insts_taken] = osp.join(cpt_path, cpt_file)
    return avail_cpts

avail_cpts = get_avail_cpts(avail_cpt_dir)
# print(avail_cpts)

batch_tasks = []
for workload, point_file, weight_file in \
        find_simpoint_analysis_files(simpoint_dir):
    workload_cpts = avail_cpts[workload]
    print(workload)
    with_cpt = 0
    without_cpt = 0
    for interval, weight, start, actual_warmup in parse_simpoint_analysis_file(
            point_file, weight_file,
            interval_length=50*10**6,
            warmup_length=50*10**6,
            ):
        phased_workload = f'{workload}_{start}_{weight}'
        if start == 0:
            start = 1000
        task = SimulatorTask(exe, top_output_dir,
                task_name=batch_task_name,
                workload=phased_workload,
                sub_phase=start,
                avoid_repeat=True,
                )
        task.workload_level_path_format()
        task.set_trivial_workdir()
        task.add_direct_options([
            f'/home51/zyy/projects/NEMU/bbl_kernel_gen/spec{ver}_bbl/{workload}.bbl.bin',
            ])
        task.add_dict_options({
            '-D': top_output_dir,
            '-C': batch_task_name,
            '-w': phased_workload,
            '--sdcard-img': '/home51/zyy/projects/NEMU/rv-debian-spec-6G-fix-sphinx.img',
            })
        task.add_list_options([
            '-b',
            ])

        # print(start)
        last = 0
        for k in reversed(sorted(workload_cpts.keys())):
            if k <= start:
                # print(f'To gen cpt@{start}, we start @{k} with {workload_cpts[k]}')
                last = k
                break
        if last == 0:
            without_cpt += 1
            pass
        else:
            with_cpt += 1
            task.add_dict_options({
                '-c': workload_cpts[last]
                })

        task.add_dict_options({  # How many instructions have to execute before take cpt
            '--checkpoint-interval': start - last + 1000,
            '--max-insts': start - last + 1500,
            })

        task.format_options(space=True)
        task.dry_run = False
        batch_tasks.append(task)
    print(f'{with_cpt} tasks with cpt, {without_cpt} tasks without cpt, {with_cpt + without_cpt} in total')

debug = False
if debug:
    task_wrapper(batch_tasks[0])
    # results = map(task_wrapper, batch_tasks[:10])
    # for res in results:
    #     print(res)
else:
    p = Pool(80)

    results = p.map(task_wrapper, batch_tasks, chunksize=1)

    count = 0
    for res in results:
        print(res)
        count += 1

    print(f'Finished {count} simulations')
    p.close()

import sh
import os
import re
import sys
import os.path as osp
from pprint import pprint
from multiprocessing import Pool

from common.simulator_task import SimulatorTask, task_wrapper
from common.task_tree import task_tree_to_batch_task
from gem5tasks.typical_o3_config import TypicalO3Config

# `GEM5` 自动化测试

TaskSummary = {}

ver = '17'
exe = '/home51/zyy/projects/gcpt-gem5/build/RISCV/gem5.opt'
fs_script = '/home51/zyy/projects/gcpt-gem5/configs/example/fs.py'
data_dir = f'/home51/zyy/expri_results/nemu_take_simpoint_cpt_{ver}/' # cpt dir
top_output_dir = '/home51/zyy/expri_results/' # cpt dir
task_name = f'gem5_ooo/spec{ver}_run_simpoints'
cpt_dir_pattern = re.compile(r'\d+')


def find_nemu_cpts(d: str):
    for workload in os.listdir(d):
        workload_dir = osp.join(d, workload)
        if not osp.isdir(workload_dir):
            continue
        TaskSummary[workload] = {}
        for cpt in os.listdir(workload_dir):
            cpt_dir = osp.join(workload_dir, cpt)
            if not cpt_dir_pattern.match(cpt) or not osp.isdir(cpt_dir):
                continue
            cpt_file = os.listdir(cpt_dir)[0]
            cpt_file = osp.join(cpt_dir, cpt_file)
            assert osp.isfile(cpt_file)

            TaskSummary[workload][cpt] = cpt_file
    return TaskSummary


def find_nemu_simpoint_cpts(d: str):
    for simpoint in os.listdir(d):
        segments = simpoint.split('_')
        inst_count = segments[-2]
        workload = segments[:-2]
        workload = '_'.join(workload)
        point_dir = osp.join(d, simpoint)
        if not osp.isdir(point_dir):
            continue
        if workload not in TaskSummary:
            TaskSummary[workload] = {}
        cpt = '0'
        cpt_dir = osp.join(point_dir, cpt)
        if not cpt_dir_pattern.match(cpt) or not osp.isdir(cpt_dir):
            continue
        cpt_file = os.listdir(cpt_dir)[0]
        cpt_file = osp.join(cpt_dir, cpt_file)
        assert osp.isfile(cpt_file)

        TaskSummary[workload][int(inst_count)] = cpt_file
    return TaskSummary


task_tree = find_nemu_simpoint_cpts(data_dir)
# pprint(task_tree)

tasks = task_tree_to_batch_task(TypicalO3Config, task_tree, exe, top_output_dir, task_name)
for task in tasks:
    # task.dry_run = True
    task.sub_workload_level_path_format()
    task.set_trivial_workdir()
    task.avoid_repeat = True

    cpt_file = task_tree[task.workload][task.sub_phase_id]

    task.direct_options += [fs_script]
    task.add_dict_options({
        '--mem-size': '8GB',
        '--generic-rv-cpt': cpt_file,
        # '--benchmark-stdout': osp.join(task.log_dir, 'workload_out.txt'),
        # '--benchmark-stderr': osp.join(task.log_dir, 'workload_err.txt'),
        '--maxinsts': str(100*10**6),
        '--gcpt-warmup': str(50*10**6),
        # '--gcpt-repeat-interval': str(10**4),
    })
    task.format_options()

debug = False

if debug:
    task_wrapper(tasks[0])
else:
    p = Pool(60)

    results = p.imap(task_wrapper, tasks, chunksize=1)
    count = 0
    for res in results:
        print(res)
        count += 1

    print(f'Finished {count} simulations')
    p.close()

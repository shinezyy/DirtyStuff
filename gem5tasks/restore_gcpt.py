import sh
import os
import re
import sys
import os.path as osp
import random
import argparse
import json
from pprint import pprint
from multiprocessing import Pool

from common.simulator_task import SimulatorTask, task_wrapper
from common.task_tree import task_tree_to_batch_task
from common import find_nemu_simpoint_cpts, find_nemu_cpts
from common import local_config as lc
import gem5tasks.typical_o3_config as tc

# `GEM5` 自动化测试

parser = argparse.ArgumentParser()
parser.add_argument('-T', '--task', action='store')
parser.add_argument('-t', '--debug-tick', action='store', type=int)
parser.add_argument('-C', '--config', action='store', type=str)
args = parser.parse_args()

# CurConf = TypicalO3Config
# CurConf = tc.OmegaH1S1G1Config
# CurConf = tc.OmegaH1S1G2Config
# CurConf = tc.OmegaH1S1G2CL0Config
# CurConf = tc.OmegaH1S1G1B8Config
# CurConf = FullWindowO3Config

# CurConf = tc.FF128G2Config
# CurConf = tc.FFH1Config
# CurConf = tc.FFG2Config
# CurConf = tc.FFG2CL0CG1Config
if args.config is not None:
    CurConf = eval(f'tc.{args.config}')
else:
    CurConf = tc.FullWindowO3Config
num_threads = 55

ver = '17'
gem5_base = '/home51/zyy/projects/omegaflow'
exe = f'{gem5_base}/build/RISCV/gem5.opt'
fs_script = f'{gem5_base}/configs/example/fs.py'
data_dir = f'/home51/zyy/expri_results/nemu_take_simpoint_cpt_{ver}/' # cpt dir
top_output_dir = '/home51/zyy/expri_results/' # cpt dir
task_name = f'omegaflow_spec{ver}/{CurConf.__name__}'
cpt_dir_pattern = re.compile(r'\d+')

workload_filter = []

task_whitlelist = []
with open (lc.simpoints_file[ver]) as jf:
    simpoints = json.load(jf)
for workload in simpoints:
    for key in simpoints[workload]:
        task_whitlelist.append(f'{workload}_{key}')

task_blacklist = [
        'x264_pass1/354300000000',
        'x264_pass1/458350000000',
        'x264_pass1/246500000000',
        'x264_pass1/249550000000',
        'x264_pass1/126650000000',
        'leela/0',
        'x264_pass2/697300000000',
        'x264_pass2/435050000000',
        'x264_pass2/530500000000',
        'blender/5100000000',
        'x264_seek/185200000000',
        'x264_seek/1221050000000',
        'cactuBSSN/50000000',
        ]
inst_flags =    ['DynInst']
mem_flags =     ['LSQUnit', 'LSQ', 'MemDepUnit', 'FFLSQ']
dq_flags =      ['DQWake', 'DQ', 'DQPair', 'DQV2', 'DQGOF']
fetch_flags =   ['Branch', 'Fetch', 'LoopBuffer']
exec_flags =    ['FUW', 'ObExec']
check_flags =   ['ValueCommit']
nosq_flags =    ['NoSQSMB', 'NoSQPred']
omega_flags =   ['FFCPU', 'DAllocation', 'FFSquash', 'DIEWC', 'FFExec', 'Commit', 'FFCommit',
        'FFInit', 'Rename', 'IEW', 'FFDisp']
fault_flags = ['RiscvMisc', 'Fault', 'PageTableWalker', 'TLB']

backend_flags = omega_flags + check_flags + mem_flags + nosq_flags + dq_flags + exec_flags + \
        inst_flags + fault_flags
frontend_flags = fetch_flags + fault_flags + inst_flags

debug_flags = []
debug_tick = None
task_filter = []

if args.task is not None:
    task_filter = [args.task]
    if args.debug_tick is not None:
        debug_tick = args.debug_tick
        debug_flags = frontend_flags + backend_flags


task_tree = find_nemu_simpoint_cpts(data_dir)
# pprint(task_tree)
# sys.exit(0)

tasks = task_tree_to_batch_task(CurConf, task_tree, exe, top_output_dir, task_name)
task_filter = [f.replace('/', '_') for f in task_filter]
task_blacklist = [f.replace('/', '_') for f in task_blacklist]
for task in tasks:
    # task.dry_run = True
    cpt_file = task_tree[task.workload][task.sub_phase_id]
    task.cpt_file = cpt_file

    if len(task_blacklist):
        if task.code_name in task_blacklist:
            task.valid = False
            continue

    if len(task_whitlelist):
        if task.code_name not in task_whitlelist:
            task.valid = False
            continue

    if len(workload_filter):
        if task.workload not in workload_filter:
            task.valid = False
            continue

    elif len(task_filter):
        task.valid = False
        for task_f in task_filter:
            if task_f in task.cpt_file:
                task.valid = True
        if not task.valid:
            continue

    task.sub_workload_level_path_format()
    task.set_trivial_workdir()
    task.avoid_repeat = True


    if len(debug_flags):
        df_str = '--debug-flags=' + ','.join(debug_flags)
        task.add_direct_options([df_str])

    if debug_tick is not None:
        start = max(0, debug_tick - 40000 * 500)
        end =          debug_tick + 10000 * 500
        task.add_direct_options([
            f'--debug-start={start}',
            f'--debug-end={end}',
            ])

    task.add_direct_options([fs_script])
    task.add_dict_options({
        '--mem-size': '8GB',
        '--generic-rv-cpt': cpt_file,
        '--gcpt-restorer': '/home/zyy/projects/NEMU/resource/gcpt_restore/build/gcpt.bin',
        # '--benchmark-stdout': osp.join(task.log_dir, 'workload_out.txt'),
        # '--benchmark-stderr': osp.join(task.log_dir, 'workload_err.txt'),
        '--maxinsts': str(100*10**6),
        '--gcpt-warmup': str(50*10**6),
        # '--gcpt-repeat-interval': str(10**4),
    })
    task.format_options()

random.shuffle(tasks)

debug = False

if debug:
    task_wrapper(tasks[0])
else:
    p = Pool(num_threads)

    results = p.map(task_wrapper, tasks, chunksize=1)
    count = 0
    for res in results:
        if res is not None:
            print(res)
            count += 1

    print(f'Finished {count} simulations')
    p.close()

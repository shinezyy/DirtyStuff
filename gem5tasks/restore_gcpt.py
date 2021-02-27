import os
import sys
import os.path as osp

from common import local_config as lc
from cptdesc import CptBatchDescription
import gem5tasks.typical_o3_config as tc

# `GEM5` 自动化测试

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

debug = False
num_threads = 1

ver = '17'
gem5_base = '/home51/zyy/projects/omegaflow'
exe = f'{gem5_base}/build/RISCV/gem5.opt'
fs_script = f'{gem5_base}/configs/example/fs.py'
data_dir = f'/home51/zyy/expri_results/nemu_take_simpoint_cpt_{ver}/' # cpt dir
top_output_dir = '/home51/zyy/expri_results/' # cpt dir

workload_filter = []

cpt_desc = CptBatchDescription(data_dir, exe, top_output_dir, ver,
        is_simpoint=True,
        simpoints_file=lc.simpoints_file[ver])

parser = cpt_desc.parser

parser.add_argument('-t', '--debug-tick', action='store', type=int)
parser.add_argument('-C', '--config', action='store', type=str)

args = cpt_desc.parse_args()

if args.config is not None:
    CurConf = eval(f'tc.{args.config}')
else:
    CurConf = tc.FullWindowO3Config
task_name = f'test_new_wrapper{ver}/{CurConf.__name__}'
cpt_desc.set_task_filter()
cpt_desc.set_conf(CurConf, task_name)
cpt_desc.filter_tasks()


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

if args.debug_tick is not None:
    debug_tick = args.debug_tick
    debug_flags = frontend_flags + backend_flags


for task in cpt_desc.tasks:
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
        '--generic-rv-cpt': task.cpt_file,
        '--gcpt-restorer': '/home/zyy/projects/NEMU/resource/gcpt_restore/build/gcpt.bin',
        # '--benchmark-stdout': osp.join(task.log_dir, 'workload_out.txt'),
        # '--benchmark-stderr': osp.join(task.log_dir, 'workload_err.txt'),
        '--maxinsts': str(100*10**6),
        '--gcpt-warmup': str(50*10**6),
        # '--gcpt-repeat-interval': str(10**4),
    })
    task.format_options()

cpt_desc.run(num_threads, debug)


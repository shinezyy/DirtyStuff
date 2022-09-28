import os
import sys
import os.path as osp
import sh

from common import local_config as lc
from cptdesc import CptBatchDescription
import gem5tasks.typical_o3_config as tc

# `GEM5` Batch execution
# Known issue: Ctrl+C will not kill the python script but not GEM5 threads;
# So, when you want to stop batch running
# 1. Ctrl + C to kill the script
# 2. killall -15 gem5.opt or gem5.fast to kill all launched threads

debug = False

# The number of threads
num_threads = 20

# SPEC 17 or 06
ver = '06'

# The root dir of GEM5
# gem5_base = '/nfs-nvme/home/zhouyaoyang/projects/xs-gem5'
gem5_base = '/nfs-nvme/home/zhouyaoyang/projects/xs-gem5-frontend'
exe = f'{gem5_base}/build/RISCV/gem5.opt'
fs_script = f'{gem5_base}/configs/example/fs.py'

# The root dir of RISC-V Generic checkpoints
# The RISC-V Generic checkpoint format is defined by Xiangshan Team
# Brief introduction here:
# https://github.com/OpenXiangShan/XiangShan-doc/blob/main/tutorial/others/Checkpoint%E7%9A%84%E7%94%9F%E6%88%90.md
data_dir = '/nfs-nvme/home/share/checkpoints_profiles/spec06_rv64gc_o2_50m/take_cpt' # cpt dir

# The directory to store GEM5 outputs (logs, configs, and stats)
top_output_dir = '/nfs-nvme/home/zhouyaoyang/gem5-results' # output dir

cpt_desc = CptBatchDescription(data_dir, exe, top_output_dir, ver,
        is_simpoint=True,  # Set it True when you are using checkpoints taken with NEMU and SimPoint method
        is_uniform=False,  # Set it False unless you carefully read the source code of this project

        # This option chooses the checkpoint filter
        # The checkpoint filter indicates whick checkpoints should be executed
        # The checkpoint filter is loaded from a json file, to local_config.py to see details
        # simpoints_file="resources/simpoint_cpt_desc/simpoints06_branch_picks.json",
        # simpoints_file="resources/simpoint_cpt_desc/simpoints06_cover0.50_top5.json",
        simpoints_file="resources/simpoint_cpt_desc/simpoints06_icache_sensitive.json",
        )

parser = cpt_desc.parser

parser.add_argument('-t', '--debug-tick', action='store', type=int)
parser.add_argument('-C', '--config', action='store', type=str)

args = cpt_desc.parse_args()

if args.config is not None:
    # You can input the config from command line
    # Example configs are defined in typical_o3_config.py
    CurConf = eval(f'tc.{args.config}')
else:
    CurConf = tc.NanhuNoL3

cwd = os.getcwd()
os.chdir(gem5_base)
tag = sh.git('rev-parse --short HEAD'.split(' ')).strip()

task_name = f'frontend_{ver}/{CurConf.__name__}-{tag}'
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

    task.add_direct_options([fs_script]) # direct_options are passed to gem5.opt

    # dict_options are passed to fs.py
    task.add_dict_options({
        '--mem-size': '8GB',
        '--generic-rv-cpt': task.cpt_file,

        # This option provides us a method to override the "GCPT restorer" when loading
        # the RISC-V generic checkpoint.
        # resource/gcpt_restore can be found in https://github.com/OpenXiangShan/NEMU/tree/cpp-gem5
        '--gcpt-restorer': '/nfs-nvme/home/zhouyaoyang/projects/gem5-ref-sd-nemu/resource/gcpt_restore/build/gcpt.bin',

        # '--benchmark-stdout': osp.join(task.log_dir, 'workload_out.txt'),
        # '--benchmark-stderr': osp.join(task.log_dir, 'workload_err.txt'),
        '--maxinsts': str(100*10**6),
        '--warmup-insts-no-switch': str(50*10**6),
        # '--gcpt-repeat-interval': str(10**4),
    })
    task.format_options()

cpt_desc.run(num_threads, debug)


import os
import sys
import os.path as osp

from common import local_config as lc
from cptdesc import CptBatchDescription
from emutasks import EmuTasksConfig

# `GEM5` 自动化测试

debug = False
num_threads = 30

ver = '06'
# exe = f'/bigdata/ljw/xs-emus/emu'
exe = f'/home/zyy/task_bins/emu'
data_dir = f'{lc.cpt_top}/nemu_take_simpoint_cpt_{ver}/' # cpt dir
top_output_dir = '/home/zyy/expri_results/' # output dir

workload_filter = []

cpt_desc = CptBatchDescription(data_dir, exe, top_output_dir, ver,
        is_simpoint=True,
        simpoints_file=lc.simpoints_file_short[ver])

parser = cpt_desc.parser

parser.add_argument('-t', '--debug-tick', action='store', type=int)
parser.add_argument('-C', '--config', action='store', type=str)

args = cpt_desc.parse_args()

CurConf = EmuTasksConfig
task_name = f'xs_simpoint_batch/SPEC{ver}_{CurConf.__name__}'
cpt_desc.set_task_filter()
cpt_desc.set_conf(CurConf, task_name)
cpt_desc.filter_tasks(hashed=True, n_machines=3)

debug_tick = None

if args.debug_tick is not None:
    debug_tick = args.debug_tick
    debug_flags = frontend_flags + backend_flags


for task in cpt_desc.tasks:
    task.sub_workload_level_path_format()
    task.set_trivial_workdir()
    task.avoid_repeat = True

    task.add_direct_options([])
    task.add_dict_options({
        '-W': str(10*10**6),
        '-I': str(30*10**6),
        '-i': task.cpt_file,
        # '--gcpt-restorer': '/home/zyy/projects/NEMU/resource/gcpt_restore/build/gcpt.bin',
        # '--gcpt-warmup': str(50*10**6),
    })
    task.format_options(space=True)
print(f'Output dir {top_output_dir}/{task_name}')
print(len(cpt_desc.tasks))

cpt_desc.run(num_threads, debug)


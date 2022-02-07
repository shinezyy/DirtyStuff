import os
import sys
import os.path as osp
import numpy as np

from common import local_config as lc
from cptdesc import CptBatchDescription
from emutasks import EmuTasksConfig

debug = False

''' Example usage:
export PYTHONPATH=`pwd`:$PYTHONPATH
python3 emutasks/dump_cache.py

Note that the number of numa nodes and emu threads is hard-cored in function init_numactl_prefixes
'''
ver = '06'
xs_base = '/local_storage/hanboyang/xs-env/XiangShan'
exe = f'{xs_base}/build/emu'
data_dir = f'/nfs/home/share/checkpoints_profiles/spec{ver}_rv64gc_o2_50m/take_cpt' # cpt dir
top_output_dir = f'/local_storage/zhouyaoyang/dump-results/' # output dir

workload_filter = []

cpt_desc = CptBatchDescription(data_dir, exe, top_output_dir, ver,
        is_simpoint=True,
        simpoints_file='/nfs/home/zhouyaoyang/simpoint_cache.json',
        is_uniform=False)

parser = cpt_desc.parser

parser.add_argument('-t', '--debug-tick', action='store', type=int)
parser.add_argument('-C', '--config', action='store', type=str)

args = cpt_desc.parse_args()

CurConf = EmuTasksConfig

sample_len = 2

task_name = f'cache_dump{ver}/{CurConf.__name__}_{sample_len}M'
cpt_desc.set_task_filter()
cpt_desc.set_conf(CurConf, task_name)
cpt_desc.filter_tasks()
print(len(cpt_desc.tasks))
# sys.exit(0)


for task in cpt_desc.tasks:
    task.sub_workload_level_path_format()
    task.set_trivial_workdir()
    task.avoid_repeat = True
    task.extra_dir = osp.join(task.work_dir, 'build/trace')
    # Toggle this to check your configuration before real execution
    # task.dry_run = True

    task.add_direct_options(['--no-diff'])

    task.add_dict_options({
        '-b': 0,
        '-e': 0,
        '-I': sample_len*10**6,
        '-i': task.cpt_file,
    })
    task.format_options(space=True)


# the number of numa nodes and emu threads is hard-cored in function init_numactl_prefixes
cpt_desc.set_numactl(st_emu_with_smt_warmup=False, selected_cores=np.arange(64, 99, 1))
cpt_desc.numactl_run()


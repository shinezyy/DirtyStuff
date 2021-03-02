import os
import sys
import os.path as osp

import load_balance as lb
from common import local_config as lc
from cptdesc import CptBatchDescription
import gem5tasks.typical_o3_config as tc

debug = False

ver = '06'
gem5_base = '/home51/zyy/projects/omegaflow'
exe = f'/home/zyy/task_bins/gem5.opt'
fs_script = f'/home/zyy/task_bins/gem5_configs/example/fs.py'
data_dir = f'/home51/zyy/expri_results/nemu_take_uniform_cpt_{ver}/' # cpt dir
top_output_dir = '/home/zyy/expri_results/shotgun/' # output

workload_filter = []

cpt_desc = CptBatchDescription(data_dir, exe, top_output_dir, ver,
        is_simpoint=False)

parser = cpt_desc.parser

parser.add_argument('-C', '--config', action='store', type=str)

args = cpt_desc.parse_args()

if args.config is not None:
    CurConf = eval(f'tc.{args.config}')
else:
    CurConf = tc.FullWindowO3Config
task_name = f'gem5_shotgun_cont_{ver}/{CurConf.__name__}'
cpt_desc.set_task_filter()
cpt_desc.set_conf(CurConf, task_name)
cpt_desc.filter_tasks(hashed=True, task_type='gem5')

for task in cpt_desc.tasks:
    task.sub_workload_level_path_format()
    task.set_trivial_workdir()
    task.avoid_repeat = True

    task.add_direct_options([fs_script])
    task.add_dict_options({
        '--mem-size': '8GB',
        '--generic-rv-cpt': task.cpt_file,
        '--gcpt-restorer': '/home/zyy/projects/NEMU/resource/gcpt_restore/build/gcpt.bin',
        '--maxinsts': str(50*10**6 + 16*50*10**6),
        '--gcpt-warmup': str(50*10**6),
        '--gcpt-repeat-interval': str(50*10**6),
    })
    task.format_options()
    task.dry_run=True

cpt_desc.run(lb.get_machine_threads('gem5'), debug)


import os
import sys
import os.path as osp
import numpy as np

from common import local_config as lc
from cptdesc import CptBatchDescription
import gem5tasks.typical_o3_config as tc

debug = False

ver = '06'
gem5_base = '/home/zyy/projects/ff'
exe = f'{gem5_base}/build/RISCV/gem5.opt'
fs_script = f'{gem5_base}/configs/example/fs.py'
data_dir = f'/bigdata/zyy/checkpoints_profiles/nemu_take_simpoint_cpt_{ver}/' # cpt dir
top_output_dir = f'{lc.local_result_top}/xs_func_warmup/' # output dir

workload_filter = []

cpt_desc = CptBatchDescription(data_dir, exe, top_output_dir, ver,
        is_simpoint=True,
        simpoints_file='./resources/simpoint_cpt_desc/simpoints06_max2.json',
        is_uniform=False)

parser = cpt_desc.parser

parser.add_argument('-t', '--debug-tick', action='store', type=int)
parser.add_argument('-C', '--config', action='store', type=str)

args = cpt_desc.parse_args()

if args.config is not None:
    CurConf = eval(f'tc.{args.config}')
else:
    CurConf = tc.Functional4XSConfig

func_len = 48
sample_len = 1

detail_len = 50 - func_len

task_name = f'func_warmup{ver}/{CurConf.__name__}_{func_len}M_{detail_len}M_{sample_len}M'
cpt_desc.set_task_filter()
cpt_desc.set_conf(CurConf, task_name)
cpt_desc.filter_tasks()


if args.debug_tick is not None:
    debug_tick = args.debug_tick
    debug_flags = frontend_flags + backend_flags

for task in cpt_desc.tasks:
    task.sub_workload_level_path_format()
    task.set_trivial_workdir()
    task.avoid_repeat = True

    task.add_direct_options([fs_script])
    task.add_dict_options({
        '--generic-rv-cpt': task.cpt_file,
        '--gcpt-restorer': '/home/zyy/projects/NEMU/resource/gcpt_restore/build/gcpt.bin',
        '--maxinsts': func_len*10**6,
        # '--benchmark-stdout': osp.join(task.log_dir, 'workload_out.txt'),
        # '--benchmark-stderr': osp.join(task.log_dir, 'workload_err.txt'),
    })
    task.format_options()
    task.second_exe = '/home/zyy/projects/XiangShan/build/emu'
    task.second_in_numactl = True
    task.second_dir = 'non-trivial-caches'

    img = '../backed_mem_for_cpt'
    warmup = detail_len * 10**6
    sample = warmup + sample_len * 10**6
    diff_so = '/home/zyy/projects/xs-nemu/build/riscv64-nemu-interpreter-so'
    task.second_option = f'-i {img} -W {warmup} -I {sample} --diff {diff_so} -M'.split(' ')

    task.clean_up_list = [img, task.second_dir, 'trivial-caches']

cpt_desc.set_numactl(st_emu_with_smt_warmup=False, selected_cores=np.arange(0, 64, 1))
cpt_desc.numactl_run()


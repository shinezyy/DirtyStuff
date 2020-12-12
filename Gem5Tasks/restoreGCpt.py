import sh
import os
import re
import os.path as osp
from pprint import pprint
from multiprocessing import Pool

from common.SimulatorTask import SimulatorTask, task_wrapper
from common.TaskTree import task_tree_to_batch_task


TaskSummary = {}

exe = '/home/zyy/projects/DirtyStuff/gem5.opt'
data_dir = '/home51/zyy/projects/NEMU/outputs3/take_simpoint_checkpoint_06' # cpt dir
top_output_dir = '/home51/zyy/projects/NEMU/outputs3' # cpt dir
cpt_dir_pattern = re.compile(r'\d+')


def find_task(d: str):
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


task_tree = find_task(data_dir)
# pprint(task_tree)

tasks = task_tree_to_batch_task(task_tree, exe, top_output_dir, 'gem5_run_spec06_cpt')
for task in tasks:
    # task.dry_run = True
    task.sub_workload_level_path_format()
    task.set_trivial_workdir()

    cpt_file = task_tree[task.workload][task.sub_phase_id]

    task.direct_options += ['/home/zyy/projects/gem5-latest-stable/configs/example/fs.py']
    task.add_dict_options({
        '--mem-size': '8GB',
        '--generic-rv-cpt': cpt_file,
        # '--benchmark-stdout': osp.join(task.log_dir, 'workload_out.txt'),
        # '--benchmark-stderr': osp.join(task.log_dir, 'workload_err.txt'),
        '--maxinsts': str(50*10**6),
    })
    task.format_options()

p = Pool(40)

results = p.imap(task_wrapper, tasks, chunksize=1)
count = 0
for res in results:
    print(res)
    count += 1

print(f'Finished {count} simulations')
p.close()

# task_wrapper(tasks[0])

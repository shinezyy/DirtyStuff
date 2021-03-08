import argparse
import json
import random
from multiprocessing import Pool

import load_balance as lb
from common import task_blacklist
from common import *
from common.task_tree import task_tree_to_batch_task
from common.simulator_task import task_wrapper

class CptBatchDescription:
    def __init__(self, data_dir, exe, top_output_dir, ver,
            is_simpoint=False,
            simpoints_file=None,
            is_uniform=True,
            is_sparse_uniform=False,
            ):

        self.task_whitelist = []

        self.data_dir = data_dir
        self.exe = exe
        self.top_output_dir = top_output_dir
        self.ver = ver

        self.is_uniform = is_uniform
        self.is_sparse_uniform = is_sparse_uniform

        self.is_simpoint = is_simpoint
        self.simpoints_file = simpoints_file

        if is_simpoint:
            with open (simpoints_file) as jf:
                simpoints = json.load(jf)
            for workload in simpoints:
                for key in simpoints[workload]:
                    self.task_whitelist.append(f'{workload}_{key}')

        self._tasks = None
        self.tasks = []

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-T', '--task', action='store')
        self.parser.add_argument('-W', '--workload', action='store', nargs='+')
        self.parser.add_argument('-D', '--dry-run', action='store_true')

        self.workload_filter = []

        self.task_filter = []
        self.task_blacklist = [f.replace('/', '_') for f in task_blacklist[ver]]

        self.args = None

    def parse_args(self):
        self.args = self.parser.parse_args()
        return self.args

    def set_conf(self, Conf, task_name):
        self.task_name = task_name
        if self.is_simpoint:
            assert not self.is_uniform
            self.task_tree = find_nemu_simpoint_cpts(self.data_dir)
        else:
            assert self.is_uniform
            if self.is_sparse_uniform:
                self.task_tree = find_nemu_sparse_uniform_cpts(self.data_dir, self.workload_filter)
            else:
                self.task_tree = find_nemu_uniform_cpts(self.data_dir, self.workload_filter)

        self._tasks = task_tree_to_batch_task(Conf,
                self.task_tree,
                self.exe,
                self.top_output_dir,
                self.task_name)

    def set_task_filter(self):
        if self.args.task is not None:
            self.task_filter = [args.task]
        self.task_filter = [f.replace('/', '_') for f in self.task_filter]

        if self.args.workload is not None:
            self.workload_filter = self.args.workload
            print(self.workload_filter)

    def filter_tasks(self, hashed=False, n_machines=0, task_type='xiangshan'):
        for task in self._tasks:
            task.cpt_file = self.task_tree[task.workload][task.sub_phase_id]

            if len(self.task_blacklist):
                if task.code_name in self.task_blacklist:
                    task.valid = False
                    continue

            if len(self.task_whitelist):
                if task.code_name not in self.task_whitelist:
                    task.valid = False
                    continue

            if len(self.workload_filter):
                if task.workload not in self.workload_filter:
                    print(task.workload)
                    print(self.workload_filter)
                    task.valid = False
                    continue

            elif len(self.task_filter):
                task.valid = False
                for task_f in self.task_filter:
                    if task_f in task.cpt_file:
                        task.valid = True
                if not task.valid:
                    continue

            if hashed:
                hash_buckets, n_buckets = lb.get_machine_hash(task_type)
                if hash(task) % n_buckets in hash_buckets:
                    task.valid = True
                else:
                    continue

            if self.args.dry_run:
                task.dry_run = True
            self.tasks.append(task)
        random.shuffle(self.tasks)

    def run(self, num_threads, debug=False):
        print(f'Run {len(self.tasks)} tasks with {num_threads} threads')
        if num_threads <= 0:
            return
        if debug:
            task_wrapper(tasks[0])
        else:
            p = Pool(num_threads)

            results = p.map(task_wrapper, self.tasks, chunksize=1)
            phases = []
            count = 0
            for res in results:
                if res is not None:
                    print(res)
                    # phases.append(res[1])
                    count += 1
            # print(sorted(phases))
            print(f'Finished {count} simulations')
            p.close()


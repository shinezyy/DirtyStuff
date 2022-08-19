import sh
import subprocess
import signal
import sys
import os
import os.path as osp
from pprint import pprint
import hashlib
import random
import time


class SimulatorTask:
    def __init__(
            self, exe: str, top_data_dir: str,
            task_name: str, workload: str, sub_phase: int,
            avoid_repeat: bool = False, extra_env: dict = {},
            ):
        # options passing to simulator
        self.direct_options = []
        # options passing to python parser
        self.dict_options = dict()
        self.list_options = set()
        self.final_options = []

        self.work_dir = None
        self.log_dir = None
        self.extra_dir = None

        # print(top_data_dir)
        assert osp.isdir(top_data_dir)
        self.top_data_dir = top_data_dir
        self.task_name = task_name

        self.workload = workload
        self.sub_phase_id = sub_phase
        self.code_name = f'{workload}_{sub_phase}'

        self.exe = exe
        assert osp.isfile(exe)

        self.dry_run = False
        self.avoid_repeat = avoid_repeat
        self.cpt_file = None
        self.valid = True

        self.use_numactl = False
        self.numa_node = 0
        self.cores = None

        self.second_exe = None
        self.second_dir = None  # relative path
        self.second_option = None
        self.second_in_numactl = False
        self.clean_up_list = []

        self.append_env(extra_env)

    def append_env(self, extra_env):
        self.env = os.environ.copy()
        for k, v in extra_env.items():
            if k in self.env:
                self.env[k] = v + ':' + self.env[k]

    def __hash__(self):
        info = f"{self.code_name}"
        return int(hashlib.sha256(info.encode()).hexdigest(), base=16)

    def __str__(self):
        info = f'Task Codename: {self.code_name}, ELF: {self.exe}, Workdir: {self.work_dir},\nNumaCtl: {self.use_numactl}, '
        if self.use_numactl:
            info += f'Numa node: {self.numa_node}, core: {self.cores}\n'
        info += f'Options: {self.final_options}\n'
        return info

    def set_workload(self, workload: str):
        self.workload = workload

    def add_direct_options(self, options: list):
        self.direct_options += options

    def add_dict_options(self, options: dict, replace=True):
        for k, v in options.items():
            if replace or k not in self.dict_options:
                self.dict_options[k] = v

    def add_list_options(self, options: list):
        for x in options:
            self.list_options.add(x)

    def format_options(self, space=False):
        self.final_options = self.direct_options
        self.final_options += list(self.list_options)
        for k, v in self.dict_options.items():
            if space:
                self.final_options.append(str(k))
                self.final_options.append(str(v))
            else:
                self.final_options.append(f'{k}={v}')

    def workload_level_path_format(self):
        self.log_dir = f'{self.top_data_dir}/{self.task_name}/{self.workload}/'

    def sub_workload_level_path_format(self):
        self.log_dir = f'{self.top_data_dir}/{self.task_name}/{self.workload}/{self.sub_phase_id}/'

    def set_trivial_workdir(self):
        self.work_dir = self.log_dir

    def check_and_makedir(self, d):
        if not osp.isdir(d):
            assert not osp.isfile(d)
            os.makedirs(d)

    def bake_numa_cmd(self):
        print(f'numactl -m {self.numa_node} -C {self.cores}:')
        return sh.numactl.bake('-m', self.numa_node, '-C', self.cores)

    def run(self):
        assert self.work_dir is not None
        assert self.log_dir is not None

        # pprint(self.exe)
        # print(self)
        # print('log_dir: ', self.log_dir)
        if self.dry_run:
            print(self.__str__())
            return
        self.check_and_makedir(self.log_dir)
        self.check_and_makedir(self.work_dir)
        if self.extra_dir is not None:
            self.check_and_makedir(self.extra_dir)

        os.chdir(self.work_dir)

        if self.avoid_repeat and osp.isfile(osp.join(self.log_dir, 'completed')):
            print(f'{self.workload}_{self.sub_phase_id} has completed')
            return
        if self.avoid_repeat and osp.isfile(osp.join(self.log_dir, 'running')):
            print(f'{self.workload}_{self.sub_phase_id} is running')
            return

        subprocess.run(['rm', '-f', osp.join(self.log_dir, 'aborted')]);
        subprocess.run(['rm', '-f', osp.join(self.log_dir, 'completed')]);
        subprocess.run(['touch', osp.join(self.log_dir, 'running')]);

        self.abort = False
        try:
            runCommand = self.exe + " " + " ".join(self.final_options)
            print('Command:', runCommand)

            def signal_handler_wrapper(proc):
                def signal_handler(signal, frame):
                    self.abort = True
                    if osp.isfile(osp.join(self.log_dir, 'running')):
                        os.remove(osp.join(self.log_dir, 'running'))
                    if not osp.isfile(osp.join(self.log_dir, 'aborted')):
                        os.mknod(osp.join(self.log_dir, 'aborted'))
                    print("kill process successfully!")
                    print(os.getpgid(proc.pid))
                    os.killpg(os.getpgid(proc.pid), 15)
                    return
                return signal_handler


            if self.use_numactl:
                runCommand = "numactl" + f" -m {self.numa_node} -C {self.cores} " + runCommand

            print(runCommand)
            main_out = open(osp.join(self.log_dir, 'main_out.txt'), "w")
            main_err = open(osp.join(self.log_dir, 'main_err.txt'), "w")
            proc = subprocess.Popen(
                runCommand,
                stdout=main_out,
                stderr=main_err,
                shell=True,
                preexec_fn=os.setsid,
                env=self.env
            )

            signal.signal(signal.SIGINT, signal_handler_wrapper(proc))
            signal.signal(signal.SIGTERM, signal_handler_wrapper(proc))
            proc.wait()

            if self.second_exe is not None:
                os.chdir(self.second_dir)
                emu = sh.Command(self.second_exe)
                print('Secondary command:', self.second_exe, self.second_option)
                if self.second_in_numactl:
                    numa = self.bake_numa_cmd()
                    numa(
                        emu,
                        _out=osp.join(self.log_dir, 'second_out.txt'),
                        _err=osp.join(self.log_dir, 'second_err.txt'),
                        *self.second_option,
                    )
                else:
                    emu(
                       _out=osp.join(self.log_dir, 'second_out.txt'),
                       _err=osp.join(self.log_dir, 'second_err.txt'),
                       *self.second_option,
                    )

        except Exception as e:
            print(e)
            self.abort = True

        os.chdir(self.work_dir)

        for dirty_file in self.clean_up_list:
            if osp.isfile(dirty_file) or osp.isdir(dirty_file):
                subprocess.run(['rm', '-rf', dirty_file]);

        if osp.isfile(osp.join(self.log_dir, 'running')):
            subprocess.run(['rm', osp.join(self.log_dir, 'running')]);

        if not self.abort:
            subprocess.run(['touch', osp.join(self.log_dir, 'completed')]);
        else:
            subprocess.run(['touch', osp.join(self.log_dir, 'aborted')]);
        return


def task_wrapper(task: SimulatorTask):
    if task.valid:
        # print(task.exe)
        task.run()
        return task.workload, task.sub_phase_id
    else:
        return None

def task_wrapper_with_numactl(task: SimulatorTask, node_idx, dry=False):
    if task.valid:
        try:
            task.run()
            # st = random.randint(0,2)
            # time.sleep(st)
            # print("returning from task wrapper")
            return (task.workload, task.sub_phase_id, node_idx)
        except Exception as e:
            print(e)
            return (None, None, node_idx)
    else:
        return (None, None, node_idx)

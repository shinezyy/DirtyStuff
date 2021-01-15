import sh
import os
import os.path as osp
from pprint import pprint


class SimulatorTask:
    def __init__(
            self, exe: str, top_data_dir: str,
            task_name: str, workload: str, sub_phase: int,
            avoid_repeat: bool = False,
            ):
        # options passing to simulator
        self.direct_options = []
        # options passing to python parser
        self.dict_options = dict()
        self.list_options = set()
        self.final_options = []

        self.work_dir = None
        self.log_dir = None

        assert osp.isdir(top_data_dir)
        self.top_data_dir = top_data_dir
        self.task_name = task_name

        self.workload = workload
        self.sub_phase_id = sub_phase

        self.exe = exe
        assert osp.isfile(exe)

        self.dry_run = False
        self.avoid_repeat = avoid_repeat

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

    def run(self):
        assert self.work_dir is not None
        assert self.log_dir is not None

        self.check_and_makedir(self.log_dir)
        self.check_and_makedir(self.work_dir)

        # pprint(self.exe)
        pprint(self.final_options)
        print('log_dir: ', self.log_dir)
        if self.dry_run:
            return

        os.chdir(self.work_dir)

        cmd = sh.Command(self.exe)

        if self.avoid_repeat and osp.isfile(osp.join(self.log_dir, 'completed')):
            print(f'{self.workload}_{self.sub_phase_id} has completed')
            return
        if self.avoid_repeat and osp.isfile(osp.join(self.log_dir, 'running')):
            print(f'{self.workload}_{self.sub_phase_id} is running')
            return

        sh.rm(['-f', osp.join(self.log_dir, 'aborted')])
        sh.rm(['-f', osp.join(self.log_dir, 'completed')])

        sh.touch(osp.join(self.log_dir, 'running'))
        try:
            cmd(
                _out=osp.join(self.log_dir, 'simulator_out.txt'),
                _err=osp.join(self.log_dir, 'simulator_err.txt'),
                *self.final_options
            )
        except Exception as e:
            print(e)
            if osp.isfile(osp.join(self.log_dir, 'running')):
                sh.rm(osp.join(self.log_dir, 'running'))
            sh.touch(osp.join(self.log_dir, 'aborted'))
            return
        if osp.isfile(osp.join(self.log_dir, 'running')):
            sh.rm(osp.join(self.log_dir, 'running'))
        sh.touch(osp.join(self.log_dir, 'completed'))
        return


def task_wrapper(task: SimulatorTask):
    task.run()
    return task.workload, task.sub_phase_id

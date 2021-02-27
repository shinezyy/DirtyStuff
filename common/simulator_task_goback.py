import sh
import os
import os.path as osp
from pprint import pprint
from multiprocessing import Lock

class SimulatorTaskGoBack:
    def __init__(
            self, exe: str, top_data_dir: str,
            task_name: str, workload: str, sub_phase: int,
            avoid_repeat: bool = False,
            ):
        super().__init__(exe, top_data_dir, task_name, workload, sub_phase, avoid_repeat)

    def insert_direct_options(self, options: list, index: int):
        assert(index < len(self.direct_options))
        insert_index = index
        for op in options:
            self.direct_options.insert(insert_index, op)
            insert_index += 1

    def run(self, is_goback):
        assert self.work_dir is not None
        assert self.log_dir is not None

        self.check_and_makedir(self.log_dir)
        self.check_and_makedir(self.work_dir)
        self.check_and_makedir(osp.join(self.log_dir, 'build'))

        if self.dry_run:
            pprint(self.exe)
            pprint(self.final_options)
            print('log_dir: ', self.log_dir)
            return 0

        os.chdir(self.work_dir)

        cmd = sh.Command(self.exe)

        # sh.rm(['-f', osp.join(self.log_dir, 'aborted')])
        # sh.rm(['-f', osp.join(self.log_dir, 'completed')])

        # sh.rm(['-f', osp.join(self.log_dir, 'aborted_back')])
        # sh.rm(['-f', osp.join(self.log_dir, 'completed_back')])
        sh.touch(osp.join(self.log_dir, 'running'))
        out_path = 'simulator_out.txt' if not is_goback else 'simulator_out_back.txt'
        err_path = 'simulator_err.txt' if not is_goback else 'simulator_err_back.txt'
        aborted_signal = 'aborted' if not is_goback else 'aborted_back'
        completed_signal = 'completed' if not is_goback else 'completed_back'
        print(self.final_options)
        try:
            cmd(
                _out = osp.join(self.log_dir, out_path),
                _err = osp.join(self.log_dir, err_path),
                _env = {"NOOP_HOME": self.log_dir} if is_goback else {"NOOP_HOME": "/home/ccc/XiangShan"},
                *self.final_options
            )
        except sh.ErrorReturnCode_1 as e:
            # TODO
            pass
        except sh.ErrorReturnCode_2 as e:
            print(e)
            sh.rm(osp.join(self.log_dir, 'running'))
            sh.touch(osp.join(self.log_dir, aborted_signal))
            cycle_cnt = check_simulator(osp.join(self.log_dir, out_path))
            assert(cycle_cnt != -1)
            return cycle_cnt
        except sh.ErrorReturnCode_3 as e:
            # TODO
            pass

        sh.rm(osp.join(self.log_dir, 'running'))
        sh.touch(osp.join(self.log_dir, completed_signal))
        return 0

def check_simulator(simulator_out_path: str):
    with open(simulator_out_path, 'r') as f:
        is_aborted = False
        for line in file.readlines():
            if line.find('cycleCnt') != -1:
                words = line.split(' ')
                cycle_cnt_index = 0
                for word in words:
                    if word == 'cycleCnt':
                        assert(len(words) >= cycle_cnt_index + 3)
                        words = words[cycle_cnt_index + 2].split(',')
                        assert(len(words) == 2)
                        assert(words[1] == '')
                        return int(words[0])
                    else:
                        cycle_cnt_index += 1
    return -1

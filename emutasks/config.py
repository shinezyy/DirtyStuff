from common.simulator_task_goback import SimulatorTaskGoBack
from common.simulator_task import SimulatorTask

class EmuTasksConfig(SimulatorTask):
    def __init__(self, exe: str, top_data_dir: str, task_name: str, workload: str, sub_phase: int):
        super().__init__(exe, top_data_dir, task_name, workload, sub_phase)
        self.list_conf = [
            # '-i'
        ]

        self.core_dict = {
            # TODO
        }

        self.mem_dict = {
            # TODO
        }

        self.dict_options = {
            **self.dict_options,
            **self.core_dict,
            **self.mem_dict,
        }

        self.add_list_options(self.list_conf)

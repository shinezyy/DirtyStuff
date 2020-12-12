from common.SimulatorTask import SimulatorTask


class TypicalO3Config(SimulatorTask):
    def __init__(self, exe: str, top_data_dir: str, task_name: str, workload: str, sub_phase: int):
        super().__init__(exe, top_data_dir, task_name, workload, sub_phase)

        self.window_size = 192

        self.add_direct_options([
            '--debug-flags=AddrRanges,Fault,Commit,ExecAll',
        ])

        self.list_conf = [
            '--caches',
            '--l2cache',
        ]

        self.core_dict = {
            '--cpu-type': 'DerivO3CPU',
            # '--num-ROB': self.window_size,
            # '--num-PhysReg': self.window_size,
            # '--num-IQ': round(0.417 * self.window_size),
            # '--num-LQ': round(0.32 * self.window_size),
            # '--num-SQ': round(0.25 * self.window_size),
        }

        self.mem_dict = {
            '--mem-type': 'DDR3_1600_8x8',
            '--cacheline_size': '64',

            '--l1i_size': '32kB',
            '--l1i_assoc': '8',

            '--l1d_size': '32kB',
            '--l1d_assoc': '8',

            '--l2_size': '4MB',
            '--l2_assoc': '8',
        }

        self.dict_options = {
            **self.dict_options,
            **self.core_dict,
            **self.mem_dict,
        }

        self.add_list_options(self.list_conf)

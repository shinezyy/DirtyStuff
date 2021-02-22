from common.simulator_task import SimulatorTask


class TypicalCoreConfig(SimulatorTask):
    def __init__(self, exe: str, top_data_dir: str, task_name: str, workload: str, sub_phase: int):
        super().__init__(exe, top_data_dir, task_name, workload, sub_phase)

        self.window_size = 192

        self.list_conf = [
            '--caches',
            '--l2cache',
            '--l3_cache',
            '--enable-loop-buffer',
        ]

        self.core_dict = {
            '--branch-trace-file': 'useless_branch.protobuf.gz',
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


class FullWindowO3Config(TypicalCoreConfig):
    def __init__(self, exe: str, top_data_dir: str, task_name: str, workload: str, sub_phase: int):
        super().__init__(exe, top_data_dir, task_name, workload, sub_phase)
        self.o3_dict = {
                '--cpu-type': 'DerivO3CPU',
                '--num-ROB': self.window_size,
                '--num-PhysReg': self.window_size,
                '--num-IQ': self.window_size,
                '--num-LQ': round(0.375 * self.window_size),
                '--num-SQ': round(0.25 * self.window_size),
                }
        self.add_dict_options(self.o3_dict)


class TypicalO3Config(TypicalCoreConfig):
    def __init__(self, exe: str, top_data_dir: str, task_name: str, workload: str, sub_phase: int):
        super().__init__(exe, top_data_dir, task_name, workload, sub_phase)
        self.o3_dict = {
                '--cpu-type': 'DerivO3CPU',
                '--num-ROB': self.window_size,
                '--num-PhysReg': self.window_size,
                '--num-IQ': round(0.416 * self.window_size),
                '--num-LQ': round(0.375 * self.window_size),
                '--num-SQ': round(0.25 * self.window_size),
                }
        self.add_dict_options(self.o3_dict)


class TypicalFFConfig(TypicalCoreConfig):
    def __init__(self, exe: str, top_data_dir: str, task_name: str, workload: str, sub_phase: int):
        super().__init__(exe, top_data_dir, task_name, workload, sub_phase)
        self.omega_dict = {
                '--cpu-type': 'DerivFFCPU',
                '--dq-groups': 1,
                '--narrow-xbar-wk': 1,
                '--xbar-wk': 0,
                '--min-wk': 0,
                '--mem-squash-factor': 3,

                '--num-LQ': self.window_size,
                '--num-SQ': self.window_size,
                }
        self.add_dict_options(self.omega_dict)
        self.omega_list = [
                '--rand-op-position',
                ]
        self.add_list_options(self.omega_list)


class FF128Config(TypicalFFConfig):
    def __init__(self, exe: str, top_data_dir: str, task_name: str, workload: str, sub_phase: int):
        self.window_size = 128
        super().__init__(exe, top_data_dir, task_name, workload, sub_phase)
        self.omega_dict = {
                '--dq-depth': 32,
                }
        self.add_dict_options(self.omega_dict)


class FFH1Config(TypicalFFConfig):
    def __init__(self, exe: str, top_data_dir: str, task_name: str, workload: str, sub_phase: int):
        super().__init__(exe, top_data_dir, task_name, workload, sub_phase)
        self.omega_list = [
                '--ready-hint',
                ]
        self.add_list_options(self.omega_list)


class FFG2Config(TypicalFFConfig):
    def __init__(self, exe: str, top_data_dir: str, task_name: str, workload: str, sub_phase: int):
        super().__init__(exe, top_data_dir, task_name, workload, sub_phase)
        self.omega_dict = {
                '--dq-groups': 2,
                '--num-LQ': self.window_size * 2,
                '--num-SQ': self.window_size * 2,
                '--num-ROB': self.window_size * 2,
                '--num-IQ': self.window_size * 2,
                '--num-PhysReg': self.window_size * 2,
                }
        self.add_dict_options(self.omega_dict)

class FFG2CL0CG1Config(FFG2Config):  # O2+
    def __init__(self, exe: str, top_data_dir: str, task_name: str, workload: str, sub_phase: int):
        super().__init__(exe, top_data_dir, task_name, workload, sub_phase)
        self.omega_dict = {
                '--cross-group-latency': 1,
                }
        self.add_dict_options(self.omega_dict)
        self.omega_list = [
                '--no-mg-center-latency',
                ]
        self.add_list_options(self.omega_list)


class FF128G2Config(FFG2Config):
    def __init__(self, exe: str, top_data_dir: str, task_name: str, workload: str, sub_phase: int):
        self.window_size = 128
        super().__init__(exe, top_data_dir, task_name, workload, sub_phase)
        self.omega_dict = {
                '--dq-depth': 32,
                }
        self.add_dict_options(self.omega_dict)


class OmegaBaseConfig(TypicalCoreConfig):
    def __init__(self, exe: str, top_data_dir: str, task_name: str, workload: str, sub_phase: int):
        super().__init__(exe, top_data_dir, task_name, workload, sub_phase)
        self.omega_dict = {
                '--cpu-type': 'DerivFFCPU',
                '--dq-groups': 1,
                '--narrow-xbar-wk': 0,
                '--xbar-wk': 0,
                '--min-wk': 1,
                '--mem-squash-factor': 3,

                '--num-LQ': self.window_size,
                '--num-SQ': self.window_size,
                }
        self.add_dict_options(self.omega_dict)


class OmegaH1S0G1Config(OmegaBaseConfig):  # O1 no shuffle
    def __init__(self, exe: str, top_data_dir: str, task_name: str, workload: str, sub_phase: int):
        super().__init__(exe, top_data_dir, task_name, workload, sub_phase)
        self.omega_list = [
                '--ready-hint',
                ]
        self.add_list_options(self.omega_list)


class OmegaH1S1G1Config(OmegaBaseConfig):  # O1
    def __init__(self, exe: str, top_data_dir: str, task_name: str, workload: str, sub_phase: int):
        super().__init__(exe, top_data_dir, task_name, workload, sub_phase)
        self.omega_list = [
                '--rand-op-position',
                '--ready-hint',
                ]
        self.add_list_options(self.omega_list)


class XOmegaH1S1G1Config(OmegaH1S1G1Config):  # O1 + xbar
    def __init__(self, exe: str, top_data_dir: str, task_name: str, workload: str, sub_phase: int):
        super().__init__(exe, top_data_dir, task_name, workload, sub_phase)
        self.omega_dict = {
                '--xbar-wk': 1,
                '--min-wk': 0,
                }
        self.add_dict_options(self.omega_dict)


class OmegaH1S1G2Config(OmegaBaseConfig):  # O2
    def __init__(self, exe: str, top_data_dir: str, task_name: str, workload: str, sub_phase: int):
        super().__init__(exe, top_data_dir, task_name, workload, sub_phase)
        self.omega_list = [
                '--rand-op-position',
                '--ready-hint',
                ]
        self.add_list_options(self.omega_list)

        self.omega_dict = {
                '--dq-groups': 2,
                '--num-LQ': self.window_size * 2,
                '--num-SQ': self.window_size * 2,
                '--num-ROB': self.window_size * 2,
                '--num-IQ': self.window_size * 2,
                '--num-PhysReg': self.window_size * 2,
                }
        self.add_dict_options(self.omega_dict)


class OmegaH1S1G2CL0Config(OmegaH1S1G2Config):  # O2+
    def __init__(self, exe: str, top_data_dir: str, task_name: str, workload: str, sub_phase: int):
        super().__init__(exe, top_data_dir, task_name, workload, sub_phase)
        self.omega_list = [
                '--no-mg-center-latency',
                ]
        self.add_list_options(self.omega_list)


class OmegaH1S1G2CL0CG1Config(OmegaH1S1G2CL0Config):  # O2+
    def __init__(self, exe: str, top_data_dir: str, task_name: str, workload: str, sub_phase: int):
        super().__init__(exe, top_data_dir, task_name, workload, sub_phase)
        self.omega_dict = {
                '--cross-group-latency': 1,
                }
        self.add_dict_options(self.omega_dict)


class OmegaH0S0G1ConfigTest(OmegaBaseConfig):  # O1* without shuffle
    pass

class OmegaH0S1G1Config(OmegaBaseConfig):  # O1*
    def __init__(self, exe: str, top_data_dir: str, task_name: str, workload: str, sub_phase: int):
        super().__init__(exe, top_data_dir, task_name, workload, sub_phase)
        self.omega_list = [
                '--rand-op-position',
                ]
        self.add_list_options(self.omega_list)


class OmegaH1S1G1B8Config(OmegaH1S1G1Config):  # O1 B8
    def __init__(self, exe: str, top_data_dir: str, task_name: str, workload: str, sub_phase: int):
        super().__init__(exe, top_data_dir, task_name, workload, sub_phase)
        self.omega_dict = {
                '--dq-banks': 8,
                }
        self.add_dict_options(self.omega_dict)

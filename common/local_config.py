import os
import platform


# /path/to/spec2006/benchspec/CPU2006
spec_cpu_2006_dir = os.environ['cpu_2006_dir']
# /path/to/spec2017/benchspec/CPU
spec_cpu_2017_dir = os.environ['cpu_2017_dir']

gathered_spec2017_data_dir = os.environ['spec2017_run_dir']

gathered_spec2006_data_dir = os.environ['spec2006_run_dir']

simpoints_file = {
        '17': '/home51/zyy/expri_results/simpoints17.json',
        '06': '/home51/zyy/expri_results/simpoints06.json',
        }

simpoints_file_short = {
        '17': '/ehrtheorgoag/',
        '06': '/home51/zyy/expri_results/simpoints06_cover0.5.json', # 231 points
        }

hash_ids = {
        'xiangshan-50': 0,
        'xiangshan-52': 1,
        'xiangshan-53': 2,
        'xiangshan-00': 3,
        'xiangshan-51': 4,
        }

def get_machine_hash():
    return hash_ids[platform.node()]

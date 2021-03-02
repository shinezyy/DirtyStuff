import os
import os.path as osp
import re

def find_nemu_sparse_uniform_cpts(d: str, workload_filter=None):
    cpt_dir_pattern = re.compile(r'\d+')
    TaskSummary = {}
    for workload in os.listdir(d):
        workload_dir = osp.join(d, workload)
        if not osp.isdir(workload_dir):
            continue
        if workload not in workload_filter:
            continue
        TaskSummary[workload] = {}
        for cpt in os.listdir(workload_dir):
            cpt_dir = osp.join(workload_dir, cpt)
            if not cpt_dir_pattern.match(cpt) or not osp.isdir(cpt_dir):
                continue
            cpt_file = os.listdir(cpt_dir)[0]
            cpt_file = osp.join(cpt_dir, cpt_file)
            assert osp.isfile(cpt_file)

            TaskSummary[workload][int(cpt)] = cpt_file
    return TaskSummary


def find_nemu_uniform_cpts(d: str, workload_filter=None,
        max_phase_per_workload=20*160, point_size=50*10**6):
    cpt_dir_pattern = re.compile(r'\d+')
    cpt_gz_pattern = re.compile(r'_(\d+)_\.gz')
    TaskSummary = {}
    for workload_phase in os.listdir(d):
        workload_phase_dir = osp.join(d, workload_phase)
        phase = int(workload_phase.split('_')[-1])
        if phase > max_phase_per_workload * point_size:
            print(f'Skip {workload_phase}')
            continue

        workload = '_'.join(workload_phase.split('_')[:-1])
        if not osp.isdir(workload_phase_dir):
            continue
        if len(workload_filter) and workload not in workload_filter:
            continue
        if workload not in TaskSummary:
            TaskSummary[workload] = {}
        for sub_phase in os.listdir(workload_phase_dir):
            cpt_dir = osp.join(workload_phase_dir, sub_phase)
            if not cpt_dir_pattern.match(sub_phase) or not osp.isdir(cpt_dir):
                continue
            cpt_basename = os.listdir(cpt_dir)[0]
            cpt_file = osp.join(cpt_dir, cpt_basename)
            assert osp.isfile(cpt_file)
            m = cpt_gz_pattern.match(cpt_basename)
            assert m is not None
            sub_phase_offset = int(m.group(1))
            assert phase + sub_phase_offset not in TaskSummary[workload]
            TaskSummary[workload][phase + sub_phase_offset] = cpt_file
    return TaskSummary


def find_nemu_simpoint_cpts(d: str):
    TaskSummary = {}
    for simpoint in os.listdir(d):
        segments = simpoint.split('_')
        inst_count = segments[-2]
        workload = segments[:-2]
        workload = '_'.join(workload)
        point_dir = osp.join(d, simpoint)
        if not osp.isdir(point_dir):
            continue
        if workload not in TaskSummary:
            TaskSummary[workload] = {}
        cpt = '0'
        cpt_dir = osp.join(point_dir, cpt)
        if not osp.isdir(cpt_dir):
            continue
        cpt_file = os.listdir(cpt_dir)[0]
        cpt_file = osp.join(cpt_dir, cpt_file)
        assert osp.isfile(cpt_file)

        TaskSummary[workload][int(inst_count)] = cpt_file
    return TaskSummary


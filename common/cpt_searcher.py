import os
import os.path as osp
import re

def find_nemu_cpts(d: str, workload_filter=None):
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


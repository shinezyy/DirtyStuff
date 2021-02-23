# BatchTaskTemplate
Python scripts to manage parallelism and input resources for simulation tasks.

We will support or have supported these features:

- [X] Multiple [GEM5](https://github.com/RISCVERS/GEM5-GCPT) instances on single machine restoring from the Generic checkpoint for RISC-V
- [X] Multiple [NEMU](https://github.com/RISCVERS/NEMU)(private repo) instances on single machine restoring from the Generic checkpoint for RISC-V
- [X] Generate checkpoint by resuming from the nearest checkpoint with [NEMU](https://github.com/RISCVERS/NEMU)
- [X] Multiple [Verilator simulation of Xiangshan](https://github.com/RISCVERS/XiangShan) instances on single machine restoring from the Generic checkpoint for RISC-V
- [X] Bug ''generation'', bug info gathering and VCD gathering for Xiangshan
- [ ] Stats gathering for GEM5


We might support, but will not support in the near future:

- [ ] Distributed version


## Getting started

We use `sh` package to call simulators:
``` shell
pip install sh
```

We will use GEM5 as an Example. We have a modified version of GEM5 [here](https://github.com/RISCVERS/GEM5-GCPT) that supports current MMIO space and Generic Checkpoint.
A full GEM5 tutorial can be found [here](http://learning.gem5.org/).

### Install dependency
First, install dependent packages.

For debian family:
``` shell
sudo apt install gcc g++ python3 zlib1g-dev m4 libprotobuf-dev git swig python-dev protobuf-compiler libgoogle-perftools-dev libevent-dev make libncurses5-dev build-essential autoconf
```

If scons is 2.x on your machine,
you can manually download scons 3 from [sourceforge](https://sourceforge.net/projects/scons/files/scons/3.1.2/).
Then expose the script to PATH in bashrc/zshrc/xxrc:
``` shell
export PATH=/the/path/to/scons-3.1.2/src/script:$PATH
```
Note that `scons` is still the old scons, while `scons.py` is the newly installed one.
``` shell
# Do to forget to source
source ~/.blablarc
```

### build
``` shell
cd /where/gem5/is/cloned
scons.py build/RISCV/gem5.opt -j 40
```
Wait a few minutes.

### set executable, data, and script paths
[Up-to-date instructions for running GEM5 with GCPT](gem5-gcpt.md)

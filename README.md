# DirtyStuff
An individual repo to contain all the tools that I created for arch research.

We will support or have supported these features:

- [X] Multiple [GEM5](https://github.com/RISCVERS/GEM5-GCPT) instances on single machine restoring from the Generic checkpoint for RISC-V
- [ ] Multiple [NEMU](https://github.com/RISCVERS/NEMU)(private repo) instances on single machine restoring from the Generic checkpoint for RISC-V
- [ ] Multiple [Verilator simulation of Xiangshan](https://github.com/RISCVERS/XiangShan) instances on single machine restoring from the Generic checkpoint for RISC-V
- [ ] Bug ''generation'', bug info gathering and VCD gathering for Xiangshan
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

For an old centos (newer RPM family might provide most of them):
``` shell
No package g++ available. --> gcc-g++
No package zlib1g-dev available.  --> zlib

No package libprotobuf-dev available.  --> manully install:
wget http://cbs.centos.org/kojifiles/packages/protobuf/2.5.0/10.el7.centos/x86_64/protobuf-2.5.0-10.el7.centos.x86_64.rpm
wget http://cbs.centos.org/kojifiles/packages/protobuf/2.5.0/10.el7.centos/x86_64/protobuf-devel-2.5.0-10.el7.centos.x86_64.rpm
wget http://cbs.centos.org/kojifiles/packages/protobuf/2.5.0/10.el7.centos/x86_64/protobuf-compiler-2.5.0-10.el7.centos.x86_64.rpm
sudo yum -y install protobuf-2.5.0-10.el7.centos.x86_64.rpm \
protobuf-compiler-2.5.0-10.el7.centos.x86_64.rpm \
protobuf-devel-2.5.0-10.el7.centos.x86_64.rpm

No package python-dev available.  --> python-devel
No package libgoogle-perftools-dev available.  --> google-perftools google-perftools-devel
No package libevent-dev available. --> ?
No package libncurses5-dev available. --> ?
```

Prepare scons 3 manually, the default scons installed are often scons 2 or are frozen to be scons 2 for oldder version of GEM5. So for newer versions of GEM5, we manually download scons 3 from [sourceforge](https://sourceforge.net/projects/scons/files/scons/3.1.2/).
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

``` shell
cd /this/repo
```

In `gem5tasks/restore_gcpt.py`, modify there variables:

``` Python
exe = The gem5.opt file
data_dir = where generic checkpoint files reside
top_output_dir = where you want to store output stats and logs
```

``` Python
task.direct_options += ['/path/toconfigs/example/fs.py']
```

### run
``` shell
python3 ./gem5tasks/restore_gcpt.py
```

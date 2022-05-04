nemu=$n/projects/rv-linux/NEMU/build/riscv64-nemu-interpreter
ref_so=$n/projects/xs-ref-nemu/build/riscv64-nemu-interpreter-so
gem5_home=$n/projects/ff-reshape
gem5=$gem5_home/build/RISCV/gem5.opt
dumper=$n/projects/tl-test/build/tlc_test
replay_gen=$n/projects/xs-dump/build/replayer.sh
xsemu=$n/projects/xs-restore/emu

icount=10800
cpt=$lz/cpts/namd129.cpt
work_dir=$(pwd)
echo $work_dir

date +%Y-%m-%d--%H:%M:%S > time.log
echo $(date -u)
time $nemu $cpt -I $icount -b --restore --etrace-inst ./inst.pbuf --etrace-data ./data.pbuf

date +%Y-%m-%d--%H:%M:%S >> time.log
time $gem5 $gem5_home/configs/example/etrace_replay.py \
    --cpu-type=TraceCPU --caches \
    --inst-trace-file=./inst.pbuf --data-trace-file=./data.pbuf \
    --mem-type=SimpleMemory --mem-size=8GB --l2cache --l3cache --dump-caches

date +%Y-%m-%d--%H:%M:%S >> time.log
rm -rf ./build/trace && mkdir -p ./build/trace
source $replay_gen
time $dumper -i $cpt

date +%Y-%m-%d--%H:%M:%S >> time.log
time $xsemu -I $icount -i $cpt --diff $ref_so -- +LOAD_SRAM 2> xs_err.txt

date +%Y-%m-%d--%H:%M:%S >> time.log

verilator_coverage coverage.dat --rank --annotate anno
date +%Y-%m-%d--%H:%M:%S >> time.log

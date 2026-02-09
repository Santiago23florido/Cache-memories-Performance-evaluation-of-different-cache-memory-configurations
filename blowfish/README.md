# Blowfish (RISC-V + gem5)

**Prerequisites**
- `riscv64-linux-gnu-gcc`
- `riscv64-linux-gnu-ar`
- `riscv64-linux-gnu-ranlib`
- gem5 built for RISC-V: `build/RISCV/gem5.opt`

**RISC-V build**
```bash
cd /home/santiago/archmic/Tp4/blowfish
make clean
make CC=riscv64-linux-gnu-gcc AR=riscv64-linux-gnu-ar RANLIB=riscv64-linux-gnu-ranlib \
  CFLAG="-O2 -static -fno-lto"
```

**Cortex-A7 simulation**
```bash
cd /home/santiago/archmic/Tp4/blowfish
rm -rf m5out
/home/santiago/archmic/gem5/build/RISCV/gem5.opt -d /home/santiago/archmic/Tp4/blowfish/m5out \
  /home/santiago/archmic/Tp4/CortexA7.py \
  --cmd=/home/santiago/archmic/Tp4/blowfish/bf \
  --args="e /home/santiago/archmic/Tp4/blowfish/input_large.asc \
     /home/santiago/archmic/Tp4/blowfish/output_large.enc \
     1234567890abcdeffedcba0987654321" \
  --cpu-type=MinorCPU --caches

grep -E "simInsts|numLoadInsts|numStoreInsts|numBranches|numIntInsts|numFpInsts" m5out/stats.txt
```

**Cortex-A15 simulation**
```bash
cd /home/santiago/archmic/Tp4/blowfish
rm -rf m5out
/home/santiago/archmic/gem5/build/RISCV/gem5.opt -d /home/santiago/archmic/Tp4/blowfish/m5out \
  /home/santiago/archmic/Tp4/CortexA15.py \
  --cmd=/home/santiago/archmic/Tp4/blowfish/bf \
  --args="e /home/santiago/archmic/Tp4/blowfish/input_large.asc \
     /home/santiago/archmic/Tp4/blowfish/output_large.enc \
     1234567890abcdeffedcba0987654321" \
  --cpu-type=O3 --caches

grep -E "simInsts|numLoadInsts|numStoreInsts|numBranches|numIntInsts|numFpInsts" m5out/stats.txt
```

Notes:
- After the RISC-V build, the executable is still named `bf` (but now it is RISC-V). If you prefer, rename it to `bf.riscv` and update `--cmd` accordingly.
- To use the small input, replace `input_large.asc` with `input_small.asc` and the output with `output_small.enc`.

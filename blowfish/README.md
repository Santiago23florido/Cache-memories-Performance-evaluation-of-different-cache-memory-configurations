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
make 
```

**Cortex-A7 simulation**
```bash
cd /home/santiago/archmic/Tp4/blowfish
rm -rf m5bfA7
/home/santiago/archmic/gem5/build/RISCV/gem5.opt -d //home/santiago/archmic/Tp4/blowfish/m5bfA7 \
  /home/santiago/archmic/Tp4/CortexA7.py \
  --cmd=/home/santiago/archmic/Tp4/blowfish/bf.riscv \
  --options /home/santiago/archmic/Tp4/blowfish/input.dat
grep -E '^system\.cpu\.executeStats[0-9]+\.(numInsts|numOps|ipc|cpi|numMemRefs|numLoadInsts|numStoreInsts|numBranches|numIntInsts|numFpInsts)\b' m5bfA7/stats.txt
```

**Cortex-A15 simulation**
```bash
cd /home/santiago/archmic/Tp4/blowfish
rm -rf m5bfA15
/home/santiago/archmic/gem5/build/RISCV/gem5.opt -d //home/santiago/archmic/Tp4/blowfish/m5bfA15 \
  /home/santiago/archmic/Tp4/CortexA15.py \
  --cmd=/home/santiago/archmic/Tp4/blowfish/bf.riscv \
  --options /home/santiago/archmic/Tp4/blowfish/input.dat
grep -E '^system\.cpu\.executeStats[0-9]+\.(numInsts|numOps|ipc|cpi|numMemRefs|numLoadInsts|numStoreInsts|numBranches|numIntInsts|numFpInsts)\b' m5bfA15/stats.txt
```

Notes:
- After the RISC-V build, the executable is still named `bf` (but now it is RISC-V). If you prefer, rename it to `bf.riscv` and update `--cmd` accordingly.
- To use the small input, replace `input_large.asc` with `input_small.asc` and the output with `output_small.enc`.
- `CortexA7.py` and `CortexA15.py` already configure the CPU model and caches internally, so extra flags like `--cpu-type` or `--caches` are not supported.

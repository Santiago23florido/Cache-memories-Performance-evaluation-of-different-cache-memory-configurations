# Dijkstra (RISC-V + gem5)

**Prerequisites**
- `riscv64-linux-gnu-gcc`
- gem5 built for RISC-V: `build/RISCV/gem5.opt`

**RISC-V build**
```bash
cd /home/santiago/archmic/Tp4/dijkstra
make clean
make CC=riscv64-linux-gnu-gcc CFLAGS="-O2 -static -fno-lto"
```

**Cortex-A7 simulation**
```bash
cd /home/santiago/archmic/Tp4/dijkstra
rm -rf m5out
/home/santiago/archmic/gem5/build/RISCV/gem5.opt -d /home/santiago/archmic/Tp4/dijkstra/m5out \
  /home/santiago/archmic/Tp4/CortexA7.py \
  --cmd=/home/santiago/archmic/Tp4/dijkstra/dijkstra_large.riscv \
  --options /home/santiago/archmic/Tp4/dijkstra/input.dat

grep -E "simInsts|numLoadInsts|numStoreInsts|numBranches|numIntInsts|numFpInsts" m5out/stats.txt
```

**Cortex-A15 simulation**
```bash
cd /home/santiago/archmic/Tp4/dijkstra
rm -rf m5out
/home/santiago/archmic/gem5/build/RISCV/gem5.opt -d /home/santiago/archmic/Tp4/dijkstra/m5out \
  /home/santiago/archmic/Tp4/CortexA15.py \
  --cmd=/home/santiago/archmic/Tp4/dijkstra/dijkstra_large.riscv \
  --options /home/santiago/archmic/Tp4/dijkstra/input.dat

grep -E "simInsts|numLoadInsts|numStoreInsts|numBranches|numIntInsts|numFpInsts" m5out/stats.txt
```

Notes:
- If you build with the RISC-V toolchain, the outputs are `dijkstra_large` and `dijkstra_small` (both RISC-V). Replace the `--cmd` path accordingly.
- To run the small input, replace the binary with `dijkstra_small` (or build a `dijkstra_small.riscv`).
- `CortexA7.py` and `CortexA15.py` already configure the CPU model and caches internally, so extra flags like `--cpu-type` or `--caches` are not supported.

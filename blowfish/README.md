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

**Cortex-A7 simulation (single run - small)**
```bash
cd /home/santiago/archmic/Tp4/blowfish
rm -rf m5bfA7_small
/home/santiago/archmic/gem5/build/RISCV/gem5.opt -d //home/santiago/archmic/Tp4/blowfish/m5bfA7_small \
  /home/santiago/archmic/Tp4/CortexA7.py \
  --cmd=/home/santiago/archmic/Tp4/blowfish/bf.riscv \
  --options e /home/santiago/archmic/Tp4/blowfish/input_small.asc /home/santiago/archmic/Tp4/blowfish/m5bfA7_small/output_small.enc 1234567890abcdeffedcba0987654321
grep -E '^system\.cpu\.executeStats[0-9]+\.(numInsts|numOps|ipc|cpi|numMemRefs|numLoadInsts|numStoreInsts|numBranches|numIntInsts|numFpInsts)\b' m5bfA7_small/stats.txt
```

**Cortex-A7 simulation (single run - large)**
```bash
cd /home/santiago/archmic/Tp4/blowfish
rm -rf m5bfA7_large
/home/santiago/archmic/gem5/build/RISCV/gem5.opt -d //home/santiago/archmic/Tp4/blowfish/m5bfA7_large \
  /home/santiago/archmic/Tp4/CortexA7.py \
  --cmd=/home/santiago/archmic/Tp4/blowfish/bf.riscv \
  --options e /home/santiago/archmic/Tp4/blowfish/input_large.asc /home/santiago/archmic/Tp4/blowfish/m5bfA7_large/output_large.enc 1234567890abcdeffedcba0987654321
grep -E '^system\.cpu\.executeStats[0-9]+\.(numInsts|numOps|ipc|cpi|numMemRefs|numLoadInsts|numStoreInsts|numBranches|numIntInsts|numFpInsts)\b' m5bfA7_large/stats.txt
```

**Cortex-A15 simulation (single run - small)**
```bash
cd /home/santiago/archmic/Tp4/blowfish
rm -rf m5bfA15_small
/home/santiago/archmic/gem5/build/RISCV/gem5.opt -d //home/santiago/archmic/Tp4/blowfish/m5bfA15_small \
  /home/santiago/archmic/Tp4/CortexA15.py \
  --cmd=/home/santiago/archmic/Tp4/blowfish/bf.riscv \
  --options e /home/santiago/archmic/Tp4/blowfish/input_small.asc /home/santiago/archmic/Tp4/blowfish/m5bfA15_small/output_small.enc 1234567890abcdeffedcba0987654321
grep -E '^system\.cpu\.executeStats[0-9]+\.(numInsts|numOps|ipc|cpi|numMemRefs|numLoadInsts|numStoreInsts|numBranches|numIntInsts|numFpInsts)\b' m5bfA15_small/stats.txt
```

**Cortex-A15 simulation (single run - large)**
```bash
cd /home/santiago/archmic/Tp4/blowfish
rm -rf m5bfA15_large
/home/santiago/archmic/gem5/build/RISCV/gem5.opt -d //home/santiago/archmic/Tp4/blowfish/m5bfA15_large \
  /home/santiago/archmic/Tp4/CortexA15.py \
  --cmd=/home/santiago/archmic/Tp4/blowfish/bf.riscv \
  --options e /home/santiago/archmic/Tp4/blowfish/input_large.asc /home/santiago/archmic/Tp4/blowfish/m5bfA15_large/output_large.enc 1234567890abcdeffedcba0987654321
grep -E '^system\.cpu\.executeStats[0-9]+\.(numInsts|numOps|ipc|cpi|numMemRefs|numLoadInsts|numStoreInsts|numBranches|numIntInsts|numFpInsts)\b' m5bfA15_large/stats.txt
```

Notes:
- After the RISC-V build, the executable is still named `bf` (but now it is RISC-V). If you prefer, rename it to `bf.riscv` and update `--cmd` accordingly.
- The small/large commands above already point to the correct input/output names (same key).
- Single run outputs: `output_small.enc` o `output_large.enc` quedan dentro de `m5bfA7_small/`, `m5bfA7_large/`, `m5bfA15_small/`, `m5bfA15_large/` (y las stats en esas mismas carpetas).
- Sweep outputs: cada run crea su propia carpeta con el dataset en el nombre, por ejemplo `runs_L1_A7/blowfish_small_L1_1kB/output_small.enc` y `runs_L1_A7/blowfish_large_L1_1kB/output_large.enc` (lo mismo para `runs_L1_A15/`). El CSV guarda esa ruta en la columna `dossier_sortie`.
- `CortexA7.py` and `CortexA15.py` already configure the CPU model and caches internally, so extra flags like `--cpu-type` or `--caches` are not supported.

**L1 sweep (small + large)**
```bash
cd /home/santiago/archmic/Tp4/blowfish
bash run_A7L1_sweep.sh
bash run_A15L1_sweep.sh
```

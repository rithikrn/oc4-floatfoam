#!/usr/bin/env bash
set -euo pipefail

case_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$case_dir"

dict_nprocs="$(awk '/numberOfSubdomains/ {gsub(/;/, "", $2); print $2; exit}' system/decomposeParDict)"
nprocs="${NPROCS:-$dict_nprocs}"

if [[ "$nprocs" != "$dict_nprocs" ]]; then
    echo "ERROR: NPROCS=$nprocs but system/decomposeParDict has numberOfSubdomains=$dict_nprocs" >&2
    echo "Edit system/decomposeParDict or rerun with NPROCS=$dict_nprocs." >&2
    exit 2
fi

if [[ ! -d processor0 ]]; then
    decomposePar -force 2>&1 | tee log.decomposePar.solve
fi

if [[ "${USE_SRUN:-0}" == "1" && -n "${SLURM_JOB_ID:-}" ]]; then
    srun interFoam -parallel 2>&1 | tee log.interFoam
else
    mpirun -np "$nprocs" interFoam -parallel 2>&1 | tee log.interFoam
fi

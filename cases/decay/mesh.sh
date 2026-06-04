#!/usr/bin/env bash
set -euo pipefail

case_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$case_dir/../.." && pwd)"
cd "$case_dir"

dict_nprocs="$(awk '/numberOfSubdomains/ {gsub(/;/, "", $2); print $2; exit}' system/decomposeParDict)"
nprocs="${NPROCS:-$dict_nprocs}"

if [[ "$nprocs" != "$dict_nprocs" ]]; then
    echo "ERROR: NPROCS=$nprocs but system/decomposeParDict has numberOfSubdomains=$dict_nprocs" >&2
    echo "Edit system/decomposeParDict or rerun with NPROCS=$dict_nprocs." >&2
    exit 2
fi

variant="${GEOMETRY_VARIANT:-base}"

if [[ -n "${GEOMETRY_FILE:-}" ]]; then
    if [[ "$GEOMETRY_FILE" = /* ]]; then
        geom_file="$GEOMETRY_FILE"
    else
        geom_file="$case_dir/$GEOMETRY_FILE"
    fi
else
    geom_file="$repo_dir/geometry/float-${variant}.stl"
fi

if [[ ! -f "$geom_file" ]]; then
    echo "ERROR: geometry file not found: $geom_file" >&2
    echo "Use GEOMETRY_VARIANT=base/hollow/custom for geometry/float-<variant>.stl," >&2
    echo "or set GEOMETRY_FILE=/absolute/path/to/yourGeometry.stl." >&2
    exit 1
fi

mkdir -p constant/triSurface
ln -sfn "$geom_file" constant/triSurface/float.stl

rm -rf processor* postProcessing log.* 0 constant/polyMesh constant/extendedFeatureEdgeMesh constant/triSurface/float.eMesh
cp -r 0.orig 0

blockMesh 2>&1 | tee log.blockMesh
surfaceFeatureExtract 2>&1 | tee log.surfaceFeatureExtract
decomposePar -force 2>&1 | tee log.decomposePar.mesh

if [[ "${USE_SRUN:-0}" == "1" && -n "${SLURM_JOB_ID:-}" ]]; then
    srun snappyHexMesh -parallel -overwrite 2>&1 | tee log.snappyHexMesh
    srun checkMesh -parallel -constant 2>&1 | tee log.checkMesh.parallel
else
    mpirun -np "$nprocs" snappyHexMesh -parallel -overwrite 2>&1 | tee log.snappyHexMesh
    mpirun -np "$nprocs" checkMesh -parallel -constant 2>&1 | tee log.checkMesh.parallel
fi

reconstructParMesh -constant 2>&1 | tee log.reconstructParMesh
rm -rf processor*
rm -rf 0
cp -r 0.orig 0
setFields 2>&1 | tee log.setFields
decomposePar -force 2>&1 | tee log.decomposePar.solve

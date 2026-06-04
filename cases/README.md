# Cases overview

`cases/` contains the three runnable OpenFOAM cases:

- [`decay/`](decay/README.md): still-water baseline.
- [`regular/`](regular/README.md): deterministic `StokesII` wave.
- [`irregular/`](irregular/README.md): Pierson–Moskowitz irregular wave realization.

All cases use the same script names so the workflow is consistent.

---

## Common structure

```text
case-name/
├── README.md
├── 0.orig/          # clean initial and boundary fields copied to 0/
├── constant/        # physics, dynamic mesh, STL link, waveProperties if needed
├── system/          # meshing, solver, schemes, decomposition
├── mesh.sh          # links STL, meshes, initializes, decomposes
├── run.sh           # runs interFoam -parallel
├── reconstruct.sh   # reconstructs results
└── submit.slurm     # batch-template wrapper
```

Generated folders are intentionally not tracked: `0/`, `processor*/`, `postProcessing/`, `constant/polyMesh/`, logs, and time directories.

---

## Standard workflow

From any case directory:

```bash
module load openfoam
chmod +x mesh.sh run.sh reconstruct.sh

./mesh.sh
./run.sh
./reconstruct.sh
```

Or with Slurm:

```bash
sbatch submit.slurm
```

The Slurm scripts also work from the repository root:

```bash
sbatch cases/regular/submit.slurm
```

---

## What the scripts do

### `mesh.sh`

1. Selects an STL and links it as `constant/triSurface/float.stl`.
2. Cleans old mesh/run artifacts.
3. Copies `0.orig/` to `0/`.
4. Runs `blockMesh`.
5. Runs `surfaceFeatureExtract`.
6. Runs `decomposePar`.
7. Runs `snappyHexMesh -parallel -overwrite`.
8. Runs `checkMesh -parallel -constant`.
9. Reconstructs the mesh with `reconstructParMesh -constant`.
10. Re-initializes `0/` and applies `setFields`.
11. Runs `decomposePar` again for the solver run.

### `run.sh`

Runs:

```bash
interFoam -parallel
```

It uses `mpirun` by default. Set `USE_SRUN=1` to use `srun` inside a Slurm allocation.

### `reconstruct.sh`

Runs:

```bash
reconstructPar
```

Optional cleanup:

```bash
DELETE_PROCESSORS_AFTER_RECONSTRUCT=1 ./reconstruct.sh
```

---

## Important environment variables

```bash
NPROCS=96                                  # must match system/decomposeParDict
USE_SRUN=1                                 # use srun instead of mpirun
GEOMETRY_VARIANT=base                      # geometry/float-base.stl
GEOMETRY_VARIANT=hollow                    # geometry/float-hollow.stl only
GEOMETRY_FILE=/absolute/path/to/body.stl   # external STL override
DELETE_PROCESSORS_AFTER_RECONSTRUCT=1
```

`NPROCS` is intentionally checked against `system/decomposeParDict`. If they do not match, the scripts stop with an error instead of launching a mismatched parallel run.

---

## Which case should I start with?

Start with `decay/` when checking a new STL, new mass properties, new mesh settings, or new restraint values. It removes wave forcing and makes geometry/mesh-motion problems easier to diagnose.

Use `regular/` after decay is stable. It has one deterministic wave and is the cleanest wave-response test.

Use `irregular/` last, after decay and regular cases are reliable. It adds a generated PM wave realization and more post-processing outputs.

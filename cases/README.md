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
└── submit.slurm     # batch-template wrapper (includes reconstruction)
```

Generated folders are intentionally not tracked: `0/`, `processor*/`, `postProcessing/`, `constant/polyMesh/`, logs, and time directories.

---

## Standard workflow

### Local execution

From any case directory:

```bash
module load openfoam
chmod +x mesh.sh run.sh

./mesh.sh
./run.sh
```

After the run finishes, use OpenFOAM's reconstruction tool directly if needed:

```bash
reconstructPar
```

### Slurm HPC execution

Submit from inside the case directory:

```bash
cd cases/regular
module load openfoam

./mesh.sh
sbatch submit.slurm
```

The Slurm script also works from the repository root:

```bash
sbatch cases/regular/submit.slurm
```

In the Slurm workflow, `submit.slurm` automatically handles both the solver run and parallel reconstruction, including optional cleanup of processor directories.

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

It uses `mpirun` by default. Set `USE_SRUN=1` to use `srun` inside a Slurm allocation:

```bash
USE_SRUN=1 ./run.sh
```

### `submit.slurm`

Slurm batch script that:

1. Loads the OpenFOAM module.
2. Runs `interFoam -parallel` with `mpirun` (respecting `SLURM_NTASKS`).
3. Logs output to `log.interFoam`.
4. Automatically reconstructs parallel results using `reconstructPar`.
5. Optionally deletes processor directories on successful reconstruction.

Edit the Slurm resource directives before submission:

```bash
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=24
#SBATCH --time=0-00:00:00
#SBATCH --mem=64G
```

---

## Important environment variables

```bash
NPROCS=96                                  # must match system/decomposeParDict
USE_SRUN=1                                 # use srun instead of mpirun (local runs)
GEOMETRY_VARIANT=base                      # use geometry/float-base.stl (default)
GEOMETRY_VARIANT=hollow                    # use geometry/float-hollow.stl
GEOMETRY_FILE=/absolute/path/to/body.stl   # external STL override
```

`NPROCS` is intentionally checked against `system/decomposeParDict`. If they do not match, the scripts stop with an error instead of launching a mismatched parallel run.

---

## Reconstruction after local runs

If you run `./mesh.sh && ./run.sh` locally (not via Slurm), reconstruct the parallel result manually:

```bash
# Reconstruct all time steps
reconstructPar

# Reconstruct only selected time steps
reconstructPar -time 0,5,10

# Clean up processor directories after reconstruction
rm -rf processor*
```

Check the OpenFOAM documentation for additional `reconstructPar` options.

---

## Which case should I start with?

Start with `decay/` when checking a new STL, new mass properties, new mesh settings, or new restraint values. It removes wave forcing and makes geometry/mesh-motion problems easier to diagnose.

Use `regular/` after decay is stable. It has one deterministic wave and is the cleanest wave-response test.

Use `irregular/` last, after decay and regular cases are reliable. It adds a generated PM wave realization and more post-processing outputs.

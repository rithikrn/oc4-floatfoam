# oc4-floatfoam

![OpenFOAM](https://img.shields.io/badge/OpenFOAM-ESI%20v2206-blue)
![Solver](https://img.shields.io/badge/solver-interFoam-blue)
![Motion](https://img.shields.io/badge/motion-sixDoF%20dynamic%20mesh-blue)
![License](https://img.shields.io/badge/license-MIT-green)

`oc4-floatfoam` is a deployable OpenFOAM case repository for wave–structure interaction simulations of an OC4-DeepCwind-class floating semisubmersible. It includes still-water decay, regular-wave, and Pierson–Moskowitz irregular-wave cases using `interFoam`, VOF free-surface flow, `dynamicMotionSolverFvMesh`, and `sixDoFRigidBodyMotion`.

The repository also works as a starting template for other semisubmersibles: replace the STL, then update the mesh domain, mass properties, restraints, waterline, and force reference values. The geometry-swap checklist is in [`geometry/README.md`](geometry/README.md).

---

## Start here

For a first test, run the regular-wave case:

```bash
git clone https://github.com/rithikrn/oc4-floatfoam.git
cd oc4-floatfoam/cases/regular

module load openfoam
chmod +x mesh.sh run.sh reconstruct.sh

./mesh.sh
./run.sh
./reconstruct.sh
```

Open the reconstructed case:

```bash
touch regular.foam
paraFoam -case .
```

If you are on a Slurm cluster:
Submit each job from inside its case directory so Slurm sets `SLURM_SUBMIT_DIR` correctly:

```bash
cd cases/regular
sbatch submit.slurm
```

Before changing the processor count, make `NPROCS`, Slurm tasks, and `system/decomposeParDict` agree.

---

## What is included

| Folder | Purpose |
|---|---|
| [`cases/decay/`](cases/decay/README.md) | Still-water baseline for mesh motion, hydrostatics, rigid-body properties, and restraint checks. |
| [`cases/regular/`](cases/regular/README.md) | Deterministic regular-wave case using OpenFOAM `StokesII` in `constant/waveProperties`. |
| [`cases/irregular/`](cases/irregular/README.md) | PM-spectrum irregular-wave case using generated `constant/waveProperties`. |
| [`tools/`](tools/README.md) | Python generator used only by the irregular PM case. |
| [`geometry/`](geometry/README.md) | Shared STL files and instructions for swapping to another semisubmersible geometry. |

---

## Repository structure

```text
oc4-floatfoam/
├── README.md
├── LICENSE
├── requirements.txt
├── geometry/
│   ├── README.md
│   ├── float-base.stl
│   └── float-hollow.stl
├── tools/
│   ├── README.md
│   └── generate-pm-waveproperties.py
└── cases/
    ├── README.md
    ├── decay/
    │   ├── README.md
    │   ├── 0.orig/
    │   ├── constant/
    │   ├── system/
    │   ├── mesh.sh
    │   ├── run.sh
    │   ├── reconstruct.sh
    │   └── submit.slurm
    ├── regular/
    │   ├── README.md
    │   ├── 0.orig/
    │   ├── constant/waveProperties
    │   ├── system/
    │   ├── mesh.sh
    │   ├── run.sh
    │   ├── reconstruct.sh
    │   └── submit.slurm
    └── irregular/
        ├── README.md
        ├── 0.orig/
        ├── constant/waveProperties
        ├── system/
        ├── prepare-waves.sh
        ├── mesh.sh
        ├── run.sh
        ├── reconstruct.sh
        └── submit.slurm
```

Generated OpenFOAM outputs such as `0/`, `processor*/`, `postProcessing/`, `constant/polyMesh/`, logs, `.foam` files, and time folders are intentionally ignored by Git.

---

## Requirements

### OpenFOAM

Target environment: **ESI/OpenCFD OpenFOAM v2206**.

Required commands:

```text
interFoam, blockMesh, surfaceFeatureExtract, snappyHexMesh, checkMesh,
setFields, decomposePar, reconstructPar, reconstructParMesh
```

Quick check:

```bash
module avail openfoam
module load openfoam
which interFoam
interFoam -help | head
```

### Python

Python is needed **only** for the irregular PM-wave generator. Decay and regular-wave cases do not need Python.

```bash
cd oc4-floatfoam
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`numpy` is required for wave generation. `matplotlib` is only needed for the optional PM verification plot.

---

## Case workflows

All cases use the same basic workflow:

```bash
./mesh.sh          # links STL, builds mesh, initializes alpha.water, decomposes
./run.sh           # runs interFoam -parallel
./reconstruct.sh   # reconstructs processor fields
```

Read the case-specific guide before editing a case:

- [`cases/README.md`](cases/README.md) — common script behavior and environment variables.
- [`cases/decay/README.md`](cases/decay/README.md) — still-water baseline.
- [`cases/regular/README.md`](cases/regular/README.md) — StokesII regular wave.
- [`cases/irregular/README.md`](cases/irregular/README.md) — PM irregular waves.

Common run variables:

```bash
NPROCS=96                                  # must match system/decomposeParDict
USE_SRUN=1                                 # use srun instead of mpirun inside Slurm
GEOMETRY_VARIANT=base                      # geometry/float-base.stl
GEOMETRY_VARIANT=hollow                    # geometry/float-hollow.stl, geometry only
GEOMETRY_FILE=/absolute/path/to/body.stl   # one-off external STL
DELETE_PROCESSORS_AFTER_RECONSTRUCT=1      # clean processor folders after reconstruction
```

The scripts now stop early if `NPROCS` does not match `system/decomposeParDict`. This prevents the common mistake where `decomposePar` creates one number of processor folders but `mpirun`/`srun` launches a different number of ranks.

---

## Irregular PM generator

The Python generator is only for:

```text
cases/irregular/constant/waveProperties
```

It is **not** used by the regular-wave case. Regular waves are defined directly in [`cases/regular/constant/waveProperties`](cases/regular/constant/waveProperties) using OpenFOAM `StokesII`.

Regenerate the default irregular-wave file:

```bash
cd cases/irregular
./prepare-waves.sh
```

Change sea-state inputs:

```bash
HS=5.49 TS=11.3 NCOMP=100 SEED=42 F_LO=0.5 F_HI=4.0 RAMP=4 ./prepare-waves.sh
```

Write the optional spectrum plot:

```bash
PLOT=1 ./prepare-waves.sh
```

Formula, assumptions, and command-line options are documented in [`tools/README.md`](tools/README.md).

---

## Base-to-hollow conversion

The shipped runnable setup is the **base** semisubmersible case. The hollow STL is included for geometry comparison, but a production hollow-physics run requires verified hollow properties.

Geometry-only hollow mesh:

```bash
cd cases/regular
GEOMETRY_VARIANT=hollow ./mesh.sh
```

Before trusting hollow results, update:

- `constant/dynamicMeshDict`: mass, centre of mass, moment of inertia, restraints, spring anchor/reference point.
- `system/controlDict`: force and moment centre `CofR`.
- `system/snappyHexMeshDict`: refinement near modified/hollow columns if needed.
- Hydrostatic equilibrium: displaced volume, draft, waterline, and restoring behavior.

Inline `// HOLLOW:` comments mark the main dictionary locations.

---

## Geometry and STL handling

Every case expects a local STL named:

```text
constant/triSurface/float.stl
```

`mesh.sh` creates this as a symlink from `geometry/` or from `GEOMETRY_FILE`.

Use another semisubmersible STL:

```bash
cd cases/decay
GEOMETRY_FILE=/absolute/path/to/my-semisub.stl ./mesh.sh
```

Minimum changes for a new platform:

1. Start with `cases/decay/`, not the wave cases.
2. Confirm STL units are meters and the body is correctly oriented.
3. Keep the patch name as `float`, or update all patch references.
4. Update tank size, refinement boxes, `locationInMesh`, and water initialization.
5. Update mass, COM, inertia, restraints, and `forces.CofR`.
6. Run decay first; move to regular waves only after decay is stable.

The full checklist is in [`geometry/README.md`](geometry/README.md).

---

## Post-processing outputs

All cases write:

```text
postProcessing/forces/
postProcessing/sixDoFRigidBodyState/
```

The irregular case also writes interface-height probes and selected field-function-object outputs from `system/controlDict`.

Quick checks after a run starts:

```bash
find postProcessing -maxdepth 3 -type f | sort | head
grep -n "Courant Number" log.interFoam | tail
grep -n "sixDoFRigidBodyMotion" log.interFoam | head
```

---

## HPC and Slurm notes

Each case includes a Slurm template. Edit resources before submitting:

```bash
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=24
#SBATCH --time=4-00:00:00
#SBATCH --mem=64G
```

Email directives are commented out by default so the script does not fail with a placeholder address. Add your real email if needed.

The Slurm scripts are safe to submit either from the case directory or from the repository root, for example:

```bash
sbatch cases/regular/submit.slurm
```

For clusters that require Slurm-native MPI launch:

```bash
USE_SRUN=1 sbatch cases/regular/submit.slurm
```

For irregular waves, regenerate `waveProperties` inside the batch job only when needed:

```bash
PREPARE_WAVES=1 sbatch cases/irregular/submit.slurm
```

---

## Troubleshooting

- **`float.stl` not found:** run `./mesh.sh` from a case directory, check `geometry/float-base.stl`, or pass `GEOMETRY_FILE=/path/to/body.stl`.
- **`float.eMesh` not found:** inspect `log.surfaceFeatureExtract`; feature extraction failed before `snappyHexMesh`.
- **Processor-count mismatch:** make `system/decomposeParDict`, `NPROCS`, and Slurm task count agree.
- **Regular wave fails:** inspect `cases/regular/constant/waveProperties`; do not use the PM generator for this case.
- **Irregular wave fails:** regenerate with `cd cases/irregular && ./prepare-waves.sh`.
- **Courant number blows up:** reduce time step/Courant settings, inspect mesh quality, lengthen wave ramp, and verify mass/inertia/restraints.
- **Forces or moments look shifted:** update `forces.CofR`, especially after changing geometry or COM.

---

## References and citation

Suggested citation:

```text
Nambiar, R. R. (2026). oc4-floatfoam: OpenFOAM wave cases for floating semisubmersible simulations. GitHub repository. https://github.com/rithikrn/oc4-floatfoam
```

References:

- Robertson, A., Jonkman, J., Goupee, A., Coulling, A., and Luan, C. *Definition of the Semisubmersible Floating System for Phase II of OC4*. NREL/TP-5000-60601, 2014. DOI: `10.2172/1155123`.
- Pierson, W. J., Jr., and Moskowitz, L. *A proposed spectral form for fully developed wind seas based on the similarity theory of S. A. Kitaigorodskii*. Journal of Geophysical Research, 1964. DOI: `10.1029/JZ069i024p05181`.
- OpenFOAM / OpenCFD documentation for `interFoam`, wave boundary conditions, dynamic mesh motion, function objects, and `sixDoFRigidBodyMotion`: `https://doc.openfoam.com/`.
- Higuera, P., Lara, J. L., and Losada, I. J. *Realistic wave generation and active wave absorption for Navier-Stokes models: Application to OpenFOAM*. Coastal Engineering, 2013. DOI: `10.1016/j.coastaleng.2012.07.002`.
- Jacobsen, N. G., Fuhrman, D. R., and Fredsøe, J. *A wave generation toolbox for the open-source CFD library: OpenFOAM*. International Journal for Numerical Methods in Fluids, 2012. DOI: `10.1002/fld.2726`.

---

## License

This repository is distributed under the MIT License. See [`LICENSE`](LICENSE).

Before a formal archival release, confirm that the STL geometry and any external data can be redistributed under the selected license.

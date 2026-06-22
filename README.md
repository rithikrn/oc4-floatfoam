# oc4-floatfoam

`oc4-floatfoam` is an OpenFOAM case repository for wave–structure interaction simulations of an OC4-DeepCwind-class floating semisubmersible platform.

The repository includes three case types:

* still-water decay,
* regular-wave response,
* Pierson–Moskowitz irregular-wave response.

The repository showcases the OC4-DeepCwind semisubmersible setup used in this work, but it can also be used as a starting point for other semisubmersible geometries. To use another floating platform, replace the STL geometry and update the mesh domain, refinement regions, mass properties, centre of mass, inertia, restraints, waterline, and force/moment reference values.

---

## Start here

For a first run, start with the regular-wave case:

```bash
git clone https://github.com/rithikrn/oc4-floatfoam.git
cd oc4-floatfoam/cases/regular

module load openfoam

cp ../../geometry/float-base.stl constant/triSurface/float.stl   # stage geometry
chmod +x mesh.sh run.sh
./mesh.sh
./run.sh
```

For local post-processing after a parallel run, reconstruct the case manually:

```bash
reconstructPar
```

Open the reconstructed case:

```bash
touch regular.foam
paraFoam -case .
```

On Slurm, mesh first, then submit the solver job. Reconstruction is handled inside `submit.slurm`.

```bash
cd oc4-floatfoam/cases/regular

module load openfoam
./mesh.sh

sbatch submit.slurm
```

---

## What is included

| Path                                            | Purpose                                                                                                   |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| [`cases/decay/`](cases/decay/README.md)         | Still-water case for checking hydrostatics, dynamic mesh motion, mass properties, and restraint behavior. |
| [`cases/regular/`](cases/regular/README.md)     | Deterministic regular-wave case using OpenFOAM `StokesII`.                                                |
| [`cases/irregular/`](cases/irregular/README.md) | Pierson–Moskowitz irregular-wave case using generated `waveProperties`.                                   |
| [`tools/`](tools/README.md)                     | Python PM wave generator used only by the irregular case.                                                 |
| [`geometry/`](geometry/README.md)               | Shared STL files and guidance for swapping to another semisubmersible geometry.                           |

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
│   ├── environment.yml
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
    │   └── submit.slurm
    ├── regular/
    │   ├── README.md
    │   ├── 0.orig/
    │   ├── constant/
    │   ├── system/
    │   ├── mesh.sh
    │   ├── run.sh
    │   └── submit.slurm
    └── irregular/
        ├── README.md
        ├── 0.orig/
        ├── constant/
        ├── system/
        ├── prepare-waves.sh
        ├── mesh.sh
        ├── run.sh
        └── submit.slurm
```

Generated OpenFOAM outputs are not tracked by Git. Expect these to appear after meshing/running:

```text
0/
processor*/
postProcessing/
constant/polyMesh/
log.*
time directories
```

---

## Requirements

### OpenFOAM

Target environment:

```text
ESI/OpenCFD OpenFOAM v2206
```

Required OpenFOAM tools:

```text
interFoam
blockMesh
surfaceFeatureExtract
snappyHexMesh
checkMesh
setFields
decomposePar
reconstructPar
reconstructParMesh
```

Quick environment check:

```bash
module avail openfoam
module load openfoam
which interFoam
interFoam -help | head
```

### Python

Python is required only for the irregular PM wave generator.

Recommended Conda setup:

```bash
cd oc4-floatfoam
conda env create -f tools/environment.yml
conda activate oc4-floatfoam-pm
```

Pip fallback:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The regular-wave case does not require Python.

---

## Case workflows

Each case follows the same basic local workflow:

```bash
./mesh.sh
./run.sh
reconstructPar
```

For Slurm runs:

```bash
./mesh.sh
sbatch submit.slurm
```

In the Slurm workflow, reconstruction is already included in `submit.slurm`.

Read the case-specific documentation before editing:

* [`cases/README.md`](cases/README.md)
* [`cases/decay/README.md`](cases/decay/README.md)
* [`cases/regular/README.md`](cases/regular/README.md)
* [`cases/irregular/README.md`](cases/irregular/README.md)

The repository tracks `0.orig/`, not generated `0/`. The `mesh.sh` script prepares `0/`, applies `setFields`, builds the mesh, and decomposes the case for parallel solving.

---

## Motion model

The shipped setup is not a fully free six-DOF/moored model.

The active `sixDoFRigidBodyMotion` setup is constrained to:

* heave using `fixedLine` in the vertical direction `(0 0 1)`,
* pitch using `fixedAxis` about the transverse axis `(0 1 0)`.

Sway, surge, roll, and yaw are locked. The active restraint is a vertical `linearSpring`; no explicit mooring-line model is included.

This is intentional for head-sea heave/pitch response studies. If you want a fully moored six-DOF model, you must modify `constant/dynamicMeshDict`, update the restraints/mooring representation, and verify the mass properties, inertia tensor, centre of mass, and force/moment reference point.

---

## Irregular PM generator

The Python generator is used only for:

```text
cases/irregular/constant/waveProperties
```

It is not used by the regular-wave case. The regular case uses OpenFOAM `StokesII` directly in:

```text
cases/regular/constant/waveProperties
```

Generate the default PM realization:

```bash
cd cases/irregular
./prepare-waves.sh
```

Change sea-state inputs:

```bash
HS=5.49 TS=11.3 NCOMP=100 SEED=42 F_LO=0.5 F_HI=4.0 RAMP=4 ./prepare-waves.sh
```

Optional plot:

```bash
PLOT=1 ./prepare-waves.sh
```

More detail is in [`tools/README.md`](tools/README.md).

---

## Geometry and STL handling

Each case expects a local STL named:

```text
constant/triSurface/float.stl
```

Stage this file manually before meshing — see [geometry/README.md](geometry/README.md).

To test another semisubmersible STL:

```bash
cd cases/decay
cp /absolute/path/to/my-semisub.stl constant/triSurface/float.stl
./mesh.sh
```

Minimum changes for a new platform:

1. Start with `cases/decay/`.
2. Confirm the STL units are meters.
3. Keep the patch name as `float`, or update every patch reference.
4. Update the domain size, refinement boxes, `locationInMesh`, and water initialization.
5. Update mass, centre of mass, inertia, restraints, and `forces.CofR`.
6. Run decay first.
7. Move to regular waves only after decay behaves correctly.
8. Move to irregular waves last.

Full geometry guidance is in [`geometry/README.md`](geometry/README.md).

---

## Base-to-hollow conversion

The shipped runnable setup should be treated as the base semisubmersible case.

The hollow STL is included for geometry comparison, but a trustworthy hollow-physics run requires updating:

* body mass,
* centre of mass,
* moment of inertia,
* spring/restraint points,
* hydrostatic equilibrium,
* displaced volume assumptions,
* `forces.CofR`,
* local mesh refinement near hollow columns.

Geometry-only hollow mesh:

```bash
cd cases/regular
cp ../../geometry/float-hollow.stl constant/triSurface/float.stl
./mesh.sh
```

Do not treat this as a validated hollow-physics case until the physical properties are updated.

---

## Post-processing outputs

All cases write:

```text
postProcessing/forces/
postProcessing/sixDoFRigidBodyState/
```

The irregular case also writes wave/interface-height and selected field-function-object outputs, depending on `system/controlDict`.

Quick checks:

```bash
find postProcessing -maxdepth 3 -type f | sort | head
grep -n "Courant Number" log.interFoam | tail
grep -n "sixDoFRigidBodyMotion" log.interFoam | head
```

Useful outputs include:

* force and moment histories from the `forces` function object,
* rigid-body displacement/rotation from `sixDoFRigidBodyState`,
* wave/interface measurements in the irregular case,
* solver logs for Courant number, residuals, and mesh-motion behavior.

---

## HPC and Slurm notes

Each case has a `submit.slurm` file. The intended workflow is:

```bash
cd cases/regular
module load openfoam
cp ../../geometry/float-base.stl constant/triSurface/float.stl
./mesh.sh

sbatch submit.slurm
```

In this workflow, `submit.slurm` runs the solver and reconstructs the parallel result.

Before submission, edit the Slurm resource lines for your cluster:

```text
#SBATCH --nodes=
#SBATCH --ntasks-per-node=
#SBATCH --time=
#SBATCH --mem=
```

The total Slurm task count should match the decomposition used by the case.

If your cluster prefers `srun` instead of `mpirun`, replace the solver line in `submit.slurm` according to your local OpenFOAM/MPI module guidance.

Typical Slurm monitoring commands:

```bash
squeue -u $USER
tail -f oc4-regular.out
tail -f oc4-regular.err
```

---

## Troubleshooting

### `float.stl` not found

Check that the shared geometry exists:

```bash
ls geometry/
```

or, from a case directory:

```bash
ls ../../geometry/
```

You must stage it before meshing:

```bash
cp ../../geometry/float-base.stl constant/triSurface/float.stl
```

### `float.eMesh` not found

Inspect the feature-extraction log:

```bash
cat log.surfaceFeatureExtract
```

Then confirm the STL path and the entry in `system/surfaceFeatureExtractDict`.

### Case starts but crashes quickly

Check:

```bash
grep -n "Courant Number" log.interFoam | tail
grep -n "Floating point exception" log.interFoam
grep -n "sixDoFRigidBodyMotion" log.interFoam | head
```

Common causes are poor mesh quality, excessive time step, wrong mass/inertia values, wrong centre of mass, or unstable restraint settings.

### No `postProcessing/` folder

Confirm that `interFoam` actually started and that function objects are enabled in `system/controlDict`.

### Regular wave problem

Edit:

```text
cases/regular/constant/waveProperties
```

Do not use the PM generator for the regular case.

### Irregular wave problem

Regenerate the PM wave dictionary:

```bash
cd cases/irregular
./prepare-waves.sh
```

Then check:

```bash
head constant/waveProperties
```

### Forces or moments look shifted

Check `forces.CofR`, especially after changing geometry, centre of mass, or the STL reference coordinate system.

---

## References and citation
Suggested citation of my masters thesis:

```bibtex
@mastersthesis{nambiar2026modeling,
  title={Modeling and Analysis of an OWC-Integrated Floating Offshore Wind Turbine Platform},
  author={Nambiar, Rithik Ramachandran},
  year={2026},
  school={Iowa State University}
}
```

Suggested repository citation:

```text
Nambiar, R. R. (2026). oc4-floatfoam: OpenFOAM wave cases for floating semisubmersible simulations. GitHub repository. https://github.com/rithikrn/oc4-floatfoam
```
```bibtex
@mastersthesis{nambiar2026modeling,
  title={Modeling and Analysis of an OWC-Integrated Floating Offshore Wind Turbine Platform},
  author={Nambiar, Rithik Ramachandran},
  year={2026},
  school={Iowa State University}
}
```

References:

* Robertson, A., Jonkman, J., Goupee, A., Coulling, A., and Luan, C. *Definition of the Semisubmersible Floating System for Phase II of OC4*. NREL/TP-5000-60601, 2014. DOI: `10.2172/1155123`.
* Pierson, W. J., Jr., and Moskowitz, L. *A proposed spectral form for fully developed wind seas based on the similarity theory of S. A. Kitaigorodskii*. Journal of Geophysical Research, 1964. DOI: `10.1029/JZ069i024p05181`.
* OpenFOAM / OpenCFD documentation for `interFoam`, wave boundary conditions, dynamic mesh motion, function objects, and `sixDoFRigidBodyMotion`: `https://doc.openfoam.com/`.

---

## License

This repository is distributed under the MIT License. See [`LICENSE`](LICENSE).

Before a formal archival release, confirm that the STL geometry and any external data can be redistributed under the selected license.

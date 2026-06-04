# Decay case

This is the still-water baseline. Use it first when checking geometry, mesh quality, hydrostatics, rigid-body properties, or the vertical spring restraint.

---

## What this case does

- Runs `interFoam` with air–water VOF physics.
- Uses dynamic mesh motion and `sixDoFRigidBodyMotion` on patch `float`.
- Uses no incident-wave model and no `constant/waveProperties` file.
- Initializes the still-water level with `system/setFieldsDict`.
- Writes force/moment and six-DOF state outputs.

---

## Run

```bash
cd cases/decay
module load openfoam

./mesh.sh
./run.sh
./reconstruct.sh
```

Slurm:

```bash
sbatch submit.slurm
```

---

## When to use this case

Use decay before the wave cases when you:

- switch to another STL;
- change mass, centre of mass, or inertia;
- retune the spring/restraint;
- change mesh refinement or tank size;
- need to isolate body-motion problems before wave excitation.

If this case is unstable, do not trust the regular or irregular cases yet.

---

## Main files to inspect

- `constant/dynamicMeshDict`: mass, COM, inertia, constraints, restraint.
- `system/snappyHexMeshDict`: STL meshing and refinement.
- `system/setFieldsDict`: still-water initialization.
- `system/controlDict`: runtime, forces, six-DOF state output.
- `0.orig/pointDisplacement`: moving-wall displacement setup.

---

## New semisubmersible geometry

Start here for a new platform:

```bash
GEOMETRY_FILE=/absolute/path/to/your-semisub.stl ./mesh.sh
```

Then update `constant/dynamicMeshDict` and `system/controlDict` to match the new body mass properties and force/moment reference point.

---

## Quick checks

```bash
find postProcessing -maxdepth 3 -type f | sort | head
grep -n "sixDoFRigidBodyMotion" log.interFoam | head
grep -n "Courant Number" log.interFoam | tail
```

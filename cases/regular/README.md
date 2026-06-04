# Regular-wave case

This case applies a deterministic regular wave using OpenFOAM `StokesII`. It does **not** use the Python PM generator.

---

## What this case does

- Runs `interFoam` with dynamic mesh motion and `sixDoFRigidBodyMotion`.
- Reads regular-wave settings from `constant/waveProperties`.
- Uses wave boundary conditions in `0.orig/U` and `0.orig/alpha.water`.
- Uses `shallowWaterAbsorption` at the outlet.
- Writes force/moment and six-DOF state outputs.

---

## Default wave setup

The shipped case uses:

```text
waveModel       StokesII
waveHeight      2.44 m
wavePeriod      8.1 s
waveAngle       0.0 deg
rampTime        32.4 s
activeAbsorption yes
outlet          shallowWaterAbsorption
```

Edit `constant/waveProperties` directly for a different regular wave.

---

## Motion constraints

This case uses a constrained `sixDoFRigidBodyMotion` setup, not a fully free six-DOF/moored model:

- `fixedLine` direction `(0 0 1)` allows heave.
- `fixedAxis` axis `(0 1 0)` allows pitch.
- sway, surge, roll, and yaw are locked.
- the active restraint is a vertical `linearSpring`; no explicit mooring-line model is enabled.

The generated `0/` directory is not tracked in Git. Always run `./mesh.sh` first on a fresh clone; it copies `0.orig/` to `0/`, applies `setFields`, and decomposes the initialized fields.

---

## Run

```bash
cd cases/regular
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

## Important distinction from irregular waves

Do not run `tools/generate-pm-waveproperties.py` for this case. Regular-wave forcing is fully defined by:

```text
cases/regular/constant/waveProperties
```

The Python generator belongs only to `cases/irregular/`.

---

## Main files to inspect

- `constant/waveProperties`: regular-wave height, period, direction, ramp, absorption.
- `0.orig/U`: wave velocity boundary conditions.
- `0.orig/alpha.water`: wave phase-fraction boundary conditions.
- `constant/dynamicMeshDict`: rigid-body motion and restraint.
- `system/controlDict`: runtime and post-processing outputs.

---

## Quick checks

```bash
grep -n "Courant Number" log.interFoam | tail
grep -n "wave" log.interFoam | head -20
find postProcessing -maxdepth 3 -type f | sort | head
```

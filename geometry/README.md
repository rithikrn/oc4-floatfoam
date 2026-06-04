# Geometry and STL handling

This folder stores shared STL geometry used by all cases.

```text
geometry/
├── float-base.stl
└── float-hollow.stl
```

The OpenFOAM dictionaries always look for one local file inside each case:

```text
cases/<case>/constant/triSurface/float.stl
```

Copy one of the STLs below into that path before meshing (the file is gitignored and not created automatically).

---

## Selecting a geometry

Run from a case directory, before `./mesh.sh`. Base (solid):

```bash
cd cases/regular
cp ../../geometry/float-base.stl constant/triSurface/float.stl
./mesh.sh
```

Hollow (4 m OWC) — swaps only the STL. It does **not** update mass, centre of
mass, inertia, hydrostatic equilibrium, restraints, or force reference values:

```bash
cp ../../geometry/float-hollow.stl constant/triSurface/float.stl
./mesh.sh
```

Your own STL — add it to `geometry/` (e.g. `geometry/float-my-design.stl`) or
copy from anywhere:

```bash
cp /absolute/path/to/my-semisub.stl constant/triSurface/float.stl
./mesh.sh
```

## Geometry-swap checklist

A new STL changes both the mesh and the physics. Check all items below before trusting results.

### 1. STL quality

- Use meters.
- Confirm body orientation relative to OpenFOAM `x`, `y`, `z`.
- Align the draft with the intended still-water level.
- Remove non-manifold surfaces, holes, duplicate triangles, and inverted normals.
- Keep enough geometric detail for the physics, but avoid unnecessary triangle density.

### 2. Patch name

The current cases expect the floating body patch to be:

```text
float
```

If you rename it, update:

```text
0.orig/*
constant/dynamicMeshDict
system/controlDict
system/snappyHexMeshDict
system/surfaceFeatureExtractDict
```

### 3. Mesh and waterline

Update these when the platform size, draft, or location changes:

```text
system/blockMeshDict
system/snappyHexMeshDict
system/surfaceFeatureExtractDict
system/setFieldsDict
```

Pay special attention to:

- tank length, width, and depth;
- inlet/outlet distance from the body;
- refinement boxes;
- surface refinement levels;
- `locationInMesh`;
- still-water level in `setFieldsDict`.

### 4. Rigid-body physics

Update real platform values in:

```text
constant/dynamicMeshDict
system/controlDict
```

Minimum values to verify:

- total mass;
- centre of mass;
- moment of inertia;
- spring/restraint anchor and reference point;
- allowed motion constraints;
- force and moment centre `CofR`;
- hydrostatic equilibrium and displaced-volume consistency.

### 5. Wave-domain setup

For another semisubmersible or wave heading, recheck:

- wave direction;
- inlet and outlet distances;
- absorption region behavior;
- free-surface mesh resolution;
- body-near mesh resolution;
- simulation time and write interval;
- decomposition and processor count.

---

## Recommended adaptation path

For a new semisubmersible:

1. Start with `cases/decay/`.
2. Copy it to `constant/triSurface/float.stl`, then run `./mesh.sh`.
3. Fix STL/mesh problems until `checkMesh` is acceptable.
4. Update mass, COM, inertia, restraints, and `CofR`.
5. Run decay and verify stable body motion.
6. Move to `cases/regular/` for deterministic wave response.
7. Move to `cases/irregular/` only after decay and regular cases are reliable.

This sequence separates geometry and hydrostatic problems from wave-forcing problems.

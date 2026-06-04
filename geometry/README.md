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

`mesh.sh` creates that file as a symlink before meshing.

---

## Built-in geometry options

Base geometry:

```bash
cd cases/regular
./mesh.sh
```

Hollow STL geometry:

```bash
cd cases/regular
GEOMETRY_VARIANT=hollow ./mesh.sh
```

Important: `GEOMETRY_VARIANT=hollow` swaps only the STL. It does not automatically update mass, centre of mass, inertia, hydrostatic equilibrium, restraint tuning, or force reference values.

---

## Use your own semisubmersible STL

One-off external STL:

```bash
cd cases/decay
GEOMETRY_FILE=/absolute/path/to/my-semisub.stl ./mesh.sh
```

Permanent repo addition:

```text
geometry/float-my-design.stl
```

Then run:

```bash
cd cases/decay
GEOMETRY_VARIANT=my-design ./mesh.sh
```

The scripts search for:

```text
geometry/float-${GEOMETRY_VARIANT}.stl
```

---

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
2. Run `GEOMETRY_FILE=/path/to/new.stl ./mesh.sh`.
3. Fix STL/mesh problems until `checkMesh` is acceptable.
4. Update mass, COM, inertia, restraints, and `CofR`.
5. Run decay and verify stable body motion.
6. Move to `cases/regular/` for deterministic wave response.
7. Move to `cases/irregular/` only after decay and regular cases are reliable.

This sequence separates geometry and hydrostatic problems from wave-forcing problems.

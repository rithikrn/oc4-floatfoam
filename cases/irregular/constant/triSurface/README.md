# Geometry placeholder

OpenFOAM reads the platform surface from this local file:

```text
constant/triSurface/float.stl
```

This file is **not** tracked in Git and is **not** created automatically. Before
meshing, copy one of the shared STLs from `geometry/` into place (run from this
case directory):

```bash
cp ../../geometry/float-base.stl   constant/triSurface/float.stl   # base (solid)
cp ../../geometry/float-hollow.stl constant/triSurface/float.stl   # 4 m hollow OWC
```

To use an external STL, copy it here under the same name:

```bash
cp /absolute/path/to/my-semisub.stl constant/triSurface/float.stl
```

Do not rename `float.stl` or the `float` patch unless you also update
`system/surfaceFeatureExtractDict`, `system/snappyHexMeshDict`,
`constant/dynamicMeshDict`, `system/controlDict`, and all affected files in `0.orig/`.

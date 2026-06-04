# Geometry placeholder

`mesh.sh` creates this generated file before meshing:

```text
constant/triSurface/float.stl
```

The file is a symlink to either a built-in STL in `geometry/` or an external STL passed with `GEOMETRY_FILE`.

Built-in variants from the case directory:

```bash
GEOMETRY_VARIANT=base ./mesh.sh
GEOMETRY_VARIANT=hollow ./mesh.sh
```

One-off external STL:

```bash
GEOMETRY_FILE=/absolute/path/to/my-semisub.stl ./mesh.sh
```

Do not rename `float.stl` or the `float` patch unless you also update `system/surfaceFeatureExtractDict`, `system/snappyHexMeshDict`, `constant/dynamicMeshDict`, `system/controlDict`, and all affected files in `0.orig/`.

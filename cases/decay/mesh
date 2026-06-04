#!/bin/sh

foamCleanTutorials
blockMesh
surfaceFeatureExtract


decomposePar -force

mpirun -np 96 snappyHexMesh -parallel -overwrite

mpirun -np 96 checkMesh -parallel -constant

reconstructParMesh -constant

rm -rf 0

cp -r 0.orig 0

setFields

decomposePar -force

#------------------------------------------------------------------------------


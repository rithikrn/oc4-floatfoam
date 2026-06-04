#!/bin/bash

#SBATCH --job-name=oc4-decay
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=24
#SBATCH --time=4-00:00:00
#SBATCH --mem=64G
#SBATCH --output=oc4floatfoam-decay.out
#SBATCH --error=oc4floatfoam-decay.err

# Optional email notifications:
# #SBATCH --mail-user=your.email@domain.com
# #SBATCH --mail-type=BEGIN,END,FAIL

module purge
module load openfoam

# Run this job from cases/decay after meshing:
#   ./mesh.sh
#   sbatch submit.slurm

mpirun -n "$SLURM_NTASKS" interFoam -parallel 2>&1 | tee -a log.interFoam

TIMES=$(seq -s, 0 5.0 500.0)
reconstructPar -time "$TIMES"

if [ $? -eq 0 ]; then
    echo "Reconstruction successful. Deleting processor directories..."
    find . -maxdepth 1 -type d -name "processor*" -exec rm -rf {} +
else
    echo "Reconstruction FAILED. Keeping processor directories for debugging."
    exit 1
fi

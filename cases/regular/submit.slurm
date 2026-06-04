#!/bin/bash

#SBATCH --nodes=4   # Number of nodes to use
#SBATCH --ntasks-per-node=24   # Use 8 processor cores per node 
#SBATCH --time=0-0:0:30   # Walltime limit (DD-HH:MM:SS)
#SBATCH --mem=64G   # Maximum memory per node
#SBATCH --job-name="oc4-floatfoam"   # Job name to display in squeue
#SBATCH --mail-user=rithikrn@oc4floatfoam   # Email address
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output="oc4floatfoam.out"   # Job standard output file
#SBATCH --error="oc4floatfoam.err"   # Job standard error file

# LOAD MODULES, INSERT CODE, AND RUN YOUR PROGRAMS HERE

module purge
module load openfoam

#./mesh

mpirun -n $SLURM_NTASKS interFoam -parallel 2>&1 | tee -a log.interFoam

TIMES=$(seq -s, 0 5.0 500.0)

reconstructPar -time "$TIMES"

if [ $? -eq 0 ]; then
    echo "Reconstruction successful. Deleting processor directories..."
    find . -maxdepth 1 -type d -name "processor*" -exec rm -rf {} +
else
    echo "Reconstruction FAILED. Keeping processor directories for debugging."
    exit 1
fi

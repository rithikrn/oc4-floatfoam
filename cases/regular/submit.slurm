#!/usr/bin/env bash
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=24
#SBATCH --time=4-00:00:00
#SBATCH --mem=64G
#SBATCH --job-name=oc4-regular
#SBATCH --output=oc4-regular.out
#SBATCH --error=oc4-regular.err
## Optional email notifications. Uncomment and edit before use.
##SBATCH --mail-user=your.email@example.com
##SBATCH --mail-type=BEGIN,END,FAIL

set -euo pipefail

case_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$case_dir"

module purge
module load openfoam

export NPROCS="${SLURM_NTASKS:-96}"
# Set USE_SRUN=1 if your cluster requires Slurm-native launching instead of mpirun.
export USE_SRUN="${USE_SRUN:-0}"

./mesh.sh
./run.sh
./reconstruct.sh

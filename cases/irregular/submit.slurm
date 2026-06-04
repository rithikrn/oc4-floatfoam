#!/usr/bin/env bash
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=24
#SBATCH --time=6-00:00:00
#SBATCH --mem=64G
#SBATCH --job-name=oc4-irregular
#SBATCH --output=oc4-irregular.out
#SBATCH --error=oc4-irregular.err
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

# Set PREPARE_WAVES=1 to regenerate constant/waveProperties before meshing.
# The shipped file already contains the default PM realization.
if [[ "${PREPARE_WAVES:-0}" == "1" ]]; then
    ./prepare-waves.sh
fi

./mesh.sh
./run.sh
./reconstruct.sh

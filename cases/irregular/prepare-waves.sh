#!/usr/bin/env bash

set -euo pipefail

case_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$case_dir/../.." && pwd)"

Hs="${HS:-2.44}"
Ts="${TS:-8.1}"
N="${NCOMP:-100}"
seed="${SEED:-12345}"
f_lo="${F_LO:-0.5}"
f_hi="${F_HI:-4.0}"
ramp="${RAMP:-4}"

# Plotting is opt-in so normal generation only requires numpy.
plot_args=(--noplot)
if [[ "${PLOT:-0}" == "1" ]]; then
    plot_args=()
fi

python3 "$repo_dir/tools/generate-pm-waveproperties.py" \
    --Hs "$Hs" \
    --Ts "$Ts" \
    --N "$N" \
    --seed "$seed" \
    --f_lo "$f_lo" \
    --f_hi "$f_hi" \
    --ramp "$ramp" \
    --outdir "$case_dir/constant" \
    "${plot_args[@]}"

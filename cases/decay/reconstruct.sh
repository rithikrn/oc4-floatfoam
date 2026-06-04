#!/usr/bin/env bash
set -euo pipefail

case_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$case_dir"

reconstructPar 2>&1 | tee log.reconstructPar

if [[ "${DELETE_PROCESSORS_AFTER_RECONSTRUCT:-0}" == "1" ]]; then
    rm -rf processor*
fi

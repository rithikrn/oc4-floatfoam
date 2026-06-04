#!/usr/bin/env python3
"""
Generate an OpenFOAM v2206 waveProperties dictionary for the irregular
Pierson-Moskowitz wave case.

This script is used only for:

    cases/irregular/constant/waveProperties
"""

from __future__ import annotations

import argparse
import os
from datetime import datetime

import numpy as np


def pm_spectrum(f: np.ndarray, hs: float, tp: float) -> np.ndarray:
    """Modified Pierson-Moskowitz spectrum using Hs and Tp."""
    fp = 1.0 / tp
    return (5.0 / 16.0) * hs**2 * fp**4 * f**(-5.0) * np.exp(-1.25 * (fp / f) ** 4)


def decompose_pm(
    hs: float,
    tp: float,
    n_components: int = 100,
    f_lo: float = 0.5,
    f_hi: float = 4.0,
    seed: int | None = None,
) -> dict:
    """Discretize the PM spectrum into OpenFOAM wave components."""
    fp = 1.0 / tp
    f_min = f_lo * fp
    f_max = f_hi * fp
    df = (f_max - f_min) / n_components

    f = np.linspace(f_min + 0.5 * df, f_max - 0.5 * df, n_components)
    s = pm_spectrum(f, hs, tp)

    heights = 2.0 * np.sqrt(2.0 * s * df)
    periods = 1.0 / f

    rng = np.random.default_rng(seed)
    phases = rng.uniform(0.0, 360.0, n_components)
    directions = np.zeros(n_components)

    m0 = float(np.sum(s * df))
    m1 = float(np.sum(f * s * df))
    m2 = float(np.sum(f**2 * s * df))
    m0_target = hs**2 / 16.0

    return {
        "hs": hs,
        "tp": tp,
        "fp": fp,
        "n": n_components,
        "f": f,
        "s": s,
        "df": df,
        "periods": periods,
        "heights": heights,
        "phases": phases,
        "directions": directions,
        "f_min": f_min,
        "f_max": f_max,
        "hs_reconstructed": 4.0 * np.sqrt(m0),
        "energy_captured": 100.0 * m0 / m0_target,
        "t01": m0 / m1,
        "tz": np.sqrt(m0 / m2),
        "seed": seed,
    }


def foam_list(values: np.ndarray, number_format: str = ".6f") -> str:
    """Format a 1D array as OpenFOAM list syntax used by waveProperties."""
    return "1((" + " ".join(f"{value:{number_format}}" for value in values) + "))"


def write_wave_properties(case: dict, path: str, ramp_multiplier: float = 4.0) -> None:
    """Write the waveProperties dictionary."""
    hs = case["hs"]
    tp = case["tp"]
    ramp_time = ramp_multiplier * tp

    header = f"""/*---------------------------------------------------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2206                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      waveProperties;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
//
// Pierson-Moskowitz irregular wave generated on {datetime.now().strftime("%Y-%m-%d %H:%M")}
// Hs = {hs:.4f} m
// Tp = {tp:.3f} s
// fp = {case["fp"]:.5f} Hz
// N  = {case["n"]} components
// f  = [{case["f_min"]:.5f}, {case["f_max"]:.5f}] Hz
// Hs(reconstructed) = {case["hs_reconstructed"]:.4f} m
// Energy captured   = {case["energy_captured"]:.2f}%
// T01 = {case["t01"]:.3f} s
// Tz  = {case["tz"]:.3f} s
// seed = {case["seed"]}
// rampTime = {ramp_time:.1f} s

inlet
{{
    alpha              alpha.water;
    waveModel          irregularMultiDirectional;
    nPaddle            1;

    rampTime           {ramp_time:.1f};
    activeAbsorption   yes;
    waveAngle          0.0;

    wavePeriods        {foam_list(case["periods"])};
    waveHeights        {foam_list(case["heights"])};
    wavePhases         {foam_list(case["phases"], ".3f")};
    waveDirs           {foam_list(case["directions"], ".1f")};
}}

outlet
{{
    alpha              alpha.water;
    waveModel          shallowWaterAbsorption;
    nPaddle            1;
}}

// ************************************************************************* //
"""

    with open(path, "w", encoding="utf-8") as handle:
        handle.write(header)


def plot_spectrum(case: dict, path: str) -> None:
    """Write an optional PM spectrum verification plot."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    hs = case["hs"]
    tp = case["tp"]

    f_ref = np.linspace(case["f_min"], case["f_max"], 600)
    s_ref = pm_spectrum(f_ref, hs, tp)

    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    ax.plot(f_ref, s_ref, linewidth=1.5, label="continuous PM spectrum")
    ax.bar(
        case["f"],
        case["s"],
        width=0.9 * case["df"],
        alpha=0.5,
        label=f'{case["n"]} discrete components',
    )
    ax.axvline(case["fp"], linestyle="--", linewidth=1.0, label=f'fp = {case["fp"]:.3f} Hz')

    ax.set_xlabel("Frequency, f [Hz]")
    ax.set_ylabel("S(f) [m²/Hz]")
    ax.set_title(f"PM spectrum, Hs={hs:.2f} m, Tp={tp:.2f} s")
    ax.grid(True, alpha=0.3)
    ax.legend()

    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate OpenFOAM waveProperties for the irregular PM-spectrum case."
    )
    parser.add_argument("--Hs", type=float, required=True, help="Significant wave height [m]")
    parser.add_argument("--Ts", type=float, required=True, help="Peak period used as Tp [s]")
    parser.add_argument("--N", type=int, default=100, help="Number of spectral components")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for wave phases")
    parser.add_argument("--f_lo", type=float, default=0.5, help="Lower frequency bound as fp multiple")
    parser.add_argument("--f_hi", type=float, default=4.0, help="Upper frequency bound as fp multiple")
    parser.add_argument("--ramp", type=float, default=4.0, help="Ramp time as multiple of Tp")
    parser.add_argument("--outdir", type=str, default=".", help="Output directory")
    parser.add_argument("--noplot", action="store_true", help="Skip verification plot")

    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    case = decompose_pm(
        hs=args.Hs,
        tp=args.Ts,
        n_components=args.N,
        f_lo=args.f_lo,
        f_hi=args.f_hi,
        seed=args.seed,
    )

    wave_path = os.path.join(args.outdir, "waveProperties")
    write_wave_properties(case, wave_path, ramp_multiplier=args.ramp)

    print(f"Hs target          = {case['hs']:.4f} m")
    print(f"Hs reconstructed   = {case['hs_reconstructed']:.4f} m")
    print(f"Tp                 = {case['tp']:.3f} s")
    print(f"fp                 = {case['fp']:.5f} Hz")
    print(f"N components       = {case['n']}")
    print(f"frequency range    = [{case['f_min']:.5f}, {case['f_max']:.5f}] Hz")
    print(f"energy captured    = {case['energy_captured']:.2f}%")
    print(f"T01                = {case['t01']:.3f} s")
    print(f"Tz                 = {case['tz']:.3f} s")
    print(f"ramp time          = {args.ramp * args.Ts:.1f} s")
    print(f"wrote              = {wave_path}")

    if not args.noplot:
        plot_path = os.path.join(args.outdir, "PM_spectrum_verification.png")
        plot_spectrum(case, plot_path)
        print(f"wrote              = {plot_path}")


if __name__ == "__main__":
    main()

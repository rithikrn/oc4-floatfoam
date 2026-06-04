#!/usr/bin/env python3
"""
Generate OpenFOAM v2206 waveProperties for Pierson-Moskowitz irregular waves.

This tool is ONLY for cases/irregular. The regular-wave case uses OpenFOAM
StokesII directly through cases/regular/constant/waveProperties and does not
call this script.

Uses the `irregularMultiDirectional` wave model. Input: Hs and Ts (=Tp).

PM Spectrum:  S(f) = (5/16) Hs^2 fp^4 f^{-5} exp(-5/4 (fp/f)^4)

Usage:
    python tools/generate-pm-waveproperties.py --Hs 2.44 --Ts 8.1
    python tools/generate-pm-waveproperties.py --Hs 5.49 --Ts 11.3 --N 100 --seed 42 --outdir cases/irregular/constant
"""
import numpy as np, argparse, os
from datetime import datetime


def pm_spectrum(f, Hs, Ts):
    fp = 1.0/Ts
    return (5.0/16.0)*Hs**2*fp**4*f**(-5)*np.exp(-1.25*(fp/f)**4)


def decompose(Hs, Ts, N=100, f_lo=0.5, f_hi=4.0, seed=None):
    fp = 1.0/Ts; fmin = f_lo*fp; fmax = f_hi*fp; df = (fmax-fmin)/N
    f = np.linspace(fmin+df/2, fmax-df/2, N)
    S = pm_spectrum(f, Hs, Ts)
    H = 2.0*np.sqrt(2.0*S*df); T = 1.0/f
    rng = np.random.default_rng(seed)
    phase = rng.uniform(0, 360, N); dirs = np.zeros(N)
    m0 = np.sum(S*df); m1 = np.sum(f*S*df); m2 = np.sum(f**2*S*df)
    return dict(T=T, H=H, phase=phase, direction=dirs, f=f, S=S, df=df,
                Hs=Hs, Hs_r=4*np.sqrt(m0), Ts=Ts, fp=fp, fr=(fmin, fmax), N=N,
                m0a=Hs**2/16, m0d=m0, T01=m0/m1, Tz=np.sqrt(m0/m2),
                ecap=100*m0/(Hs**2/16), seed=seed)


def fmt(v, f='.6f'):
    return '1((' + ' '.join(f'{x:{f}}' for x in v) + '))'


def write_wp(c, path, ramp_n=4):
    Hs = c['Hs']; Ts = c['Ts']; N = c['N']; ramp = ramp_n*Ts
    with open(path, 'w') as f:
        f.write(f"""\
/*---------------------------------------------------------------------------*\\
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
//  Pierson-Moskowitz irregular wave (auto-generated {datetime.now().strftime('%Y-%m-%d %H:%M')})
//  Hs = {Hs:.4f} m,  Ts(=Tp) = {Ts:.3f} s,  fp = {c['fp']:.5f} Hz
//  N = {N} components,  f = [{c['fr'][0]:.5f}, {c['fr'][1]:.5f}] Hz
//  Hs(recon) = {c['Hs_r']:.4f} m,  error = {abs(c['Hs_r']-Hs)/Hs*100:.3f}%
//  Energy captured = {c['ecap']:.2f}%,  T01 = {c['T01']:.3f} s,  Tz = {c['Tz']:.3f} s
//  seed = {c.get('seed','N/A')},  ramp = {ramp:.1f} s
//

inlet
{{
    alpha           alpha.water;
    waveModel       irregularMultiDirectional;
    nPaddle         1;

    // PM irregular sea: Hs = {Hs:.4f} m, Ts = {Ts:.3f} s ({N} components)
    rampTime        {ramp:.1f};
    activeAbsorption yes;
    waveAngle       0.0;

    wavePeriods     {fmt(c['T'])};
    waveHeights     {fmt(c['H'])};
    wavePhases      {fmt(c['phase'],'.3f')};
    waveDirs        {fmt(c['direction'],'.1f')};
}}

outlet
{{
    alpha           alpha.water;
    waveModel       shallowWaterAbsorption;
    nPaddle         1;
}}

// ************************************************************************* //
""")


def plot_spec(c, path):
    """Verification plot: discrete PM components over the continuous spectrum,
    plus a sample of the reconstructed surface elevation."""
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'serif', 'font.size': 11,
                         'figure.dpi': 150, 'axes.grid': True,
                         'grid.alpha': 0.3})
    Hs = c['Hs']; Ts = c['Ts']
    # continuous reference curve
    ff = np.linspace(c['fr'][0], c['fr'][1], 600)
    Sf = pm_spectrum(ff, Hs, Ts)

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))

    # --- left: spectrum ---
    ax[0].plot(ff, Sf, 'b-', lw=1.6, label='PM spectrum S(f)')
    ax[0].bar(c['f'], c['S'], width=c['df']*0.9, color='tab:orange',
              alpha=0.55, label=f"{c['N']} components")
    ax[0].axvline(c['fp'], color='k', ls='--', lw=0.9, label=f"fp = {c['fp']:.3f} Hz")
    ax[0].set_xlabel('Frequency  f  [Hz]')
    ax[0].set_ylabel('S(f)  [m$^2$/Hz]')
    ax[0].set_title(f"PM spectrum  (Hs={Hs:.2f} m, Ts={Ts:.2f} s)")
    ax[0].legend(fontsize=8)

    # --- right: reconstructed surface elevation ---
    t = np.linspace(0, 6*Ts, 3000)
    eta = np.zeros_like(t)
    w = 2*np.pi*c['f']; a = c['H']/2.0; ph = np.deg2rad(c['phase'])
    for ai, wi, pi in zip(a, w, ph):
        eta += ai*np.cos(wi*t + pi)
    ax[1].plot(t, eta, 'b-', lw=0.8)
    ax[1].axhline(Hs/2, color='r', ls='--', lw=0.8, label=f"Hs/2 = {Hs/2:.2f} m")
    ax[1].axhline(-Hs/2, color='r', ls='--', lw=0.8)
    ax[1].set_xlabel('Time  t  [s]')
    ax[1].set_ylabel('Surface elevation  $\\eta$  [m]')
    ax[1].set_title('Reconstructed wave surface (one realisation)')
    ax[1].legend(fontsize=8)

    fig.suptitle(
        f"Hs(recon) = {c['Hs_r']:.3f} m  "
        f"(error {abs(c['Hs_r']-Hs)/Hs*100:.2f}%),  "
        f"energy captured {c['ecap']:.1f}%",
        fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(
        description='Generate OpenFOAM v2206 waveProperties for the irregular PM-spectrum case only.')
    ap.add_argument('--Hs', type=float, required=True,
                    help='Significant wave height [m]')
    ap.add_argument('--Ts', type=float, required=True,
                    help='Peak spectral period Ts (=Tp) [s]')
    ap.add_argument('--N', type=int, default=100,
                    help='Number of spectral components (default 100)')
    ap.add_argument('--seed', type=int, default=None,
                    help='RNG seed for reproducible random phases')
    ap.add_argument('--ramp', type=float, default=4.0,
                    help='Ramp time in multiples of Ts (default 4)')
    ap.add_argument('--f_lo', type=float, default=0.5,
                    help='Lower freq bound as multiple of fp (default 0.5)')
    ap.add_argument('--f_hi', type=float, default=4.0,
                    help='Upper freq bound as multiple of fp (default 4.0)')
    ap.add_argument('--outdir', type=str, default='.',
                    help='Output directory (default current dir)')
    ap.add_argument('--noplot', action='store_true',
                    help='Skip the verification plot')
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    c = decompose(args.Hs, args.Ts, N=args.N,
                  f_lo=args.f_lo, f_hi=args.f_hi, seed=args.seed)

    wp_path = os.path.join(args.outdir, 'waveProperties')
    write_wp(c, wp_path, ramp_n=args.ramp)

    print(f"  Hs (target)        = {c['Hs']:.4f} m")
    print(f"  Hs (reconstructed) = {c['Hs_r']:.4f} m  "
          f"(error {abs(c['Hs_r']-c['Hs'])/c['Hs']*100:.3f}%)")
    print(f"  Ts (=Tp)           = {c['Ts']:.3f} s   fp = {c['fp']:.5f} Hz")
    print(f"  N components       = {c['N']}   "
          f"f = [{c['fr'][0]:.5f}, {c['fr'][1]:.5f}] Hz")
    print(f"  Energy captured    = {c['ecap']:.2f}%")
    print(f"  T01 = {c['T01']:.3f} s   Tz = {c['Tz']:.3f} s")
    print(f"  ramp time          = {args.ramp*args.Ts:.1f} s  ({args.ramp:g} x Ts)")
    print(f"  -> wrote {wp_path}")

    if not args.noplot:
        plot_path = os.path.join(args.outdir, 'PM_spectrum_verification.png')
        plot_spec(c, plot_path)
        print(f"  -> wrote {plot_path}")


if __name__ == '__main__':
    main()
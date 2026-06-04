# PM waveProperties generator

`generate-pm-waveproperties.py` creates the OpenFOAM `waveProperties` file for the irregular-wave case only:

```text
cases/irregular/constant/waveProperties
```

The regular-wave case does not use this script. Regular waves are defined directly in `cases/regular/constant/waveProperties` using OpenFOAM `StokesII`.

---

## Science in one minute

The script discretizes a modified Pierson–Moskowitz spectrum into finite regular-wave components with random phase angles.

```text
S(f) = (5/16) Hs^2 fp^4 f^-5 exp[-1.25(fp/f)^4]
fp   = 1 / Ts
```

In this repo, `Ts` is treated as the peak spectral period `Tp`.

For each frequency bin:

```text
H_i = 2 sqrt(2 S(f_i) df)
```

The output arrays are written in the format expected by OpenFOAM `irregularMultiDirectional`:

```text
wavePeriods
waveHeights
wavePhases
waveDirs
```

The default setup uses one wave direction, `waveAngle = 0.0`, with reproducible random phases controlled by `--seed`.

---

## Install dependencies

Use Conda on clusters to avoid conflicts with system Python modules:

```bash
cd oc4-floatfoam
conda env create -f tools/environment.yml
conda activate oc4-floatfoam-pm
```

The environment pins the generator stack to Python 3.11, NumPy 1.26, and Matplotlib 3.8.

A lightweight pip fallback is also available:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`numpy` is required. `matplotlib` is needed only for the optional verification plot.

---

## Recommended use

Use the wrapper from the irregular case:

```bash
cd cases/irregular
./prepare-waves.sh
```

Change sea-state inputs:

```bash
HS=5.49 TS=11.3 NCOMP=100 SEED=42 F_LO=0.5 F_HI=4.0 RAMP=4 ./prepare-waves.sh
```

Generate the optional plot:

```bash
PLOT=1 ./prepare-waves.sh
```

---

## Direct Python use

From the repository root:

```bash
python3 tools/generate-pm-waveproperties.py \
  --Hs 2.44 \
  --Ts 8.1 \
  --N 100 \
  --seed 12345 \
  --f_lo 0.5 \
  --f_hi 4.0 \
  --ramp 4 \
  --outdir cases/irregular/constant \
  --noplot
```

Options:

```text
--Hs       significant wave height [m]
--Ts       peak period used by the PM spectrum [s]
--N        number of spectral components
--seed     random seed for phases
--f_lo     lower frequency bound as a multiple of fp
--f_hi     upper frequency bound as a multiple of fp
--ramp     ramp time in multiples of Ts
--outdir   output directory
--noplot   skip PM_spectrum_verification.png
```

---

## What to check

The script prints:

- target `Hs`;
- reconstructed `Hs` from discrete components;
- percent error;
- frequency range;
- captured energy;
- `T01` and `Tz` estimates;
- written file path.

For reproducible production runs, record `Hs`, `Ts`, `N`, `F_LO`, `F_HI`, `RAMP`, and `SEED`.

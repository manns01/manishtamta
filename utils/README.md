# Research animations

Python animations that explain the physics behind Manish Tamta's papers. Each
script renders a looping `.mp4` plus a `.jpg` poster frame into
`../assets/animations/`, where `index.html` picks them up. (This folder was
formerly `animation/`.)

| Script | Output | Explains |
| --- | --- | --- |
| `finite_source.py` | — (module) | Finite-source point-lens equations following **Witt & Mao (1994)**: `A_ps` (point source), `A_fs(u, ρ)` (uniform disc, exact singularity-free 1-D integral) and `image_boundary` (the two lensed image contours). Includes a self-test (`python3 finite_source.py`) that cross-checks `A_fs` against the image-area definition and the `√(1+4/ρ²)` central peak. |
| `microlensing_lightcurve.py` | `microlensing.mp4` | Microlensing of a **finite-size star**: the extended source and its two image contours sweep around the Einstein ring, and the light curve shows the point-source spike replaced by a capped, flat-topped finite-source curve — the effect that matters for low-mass lenses. Underlies *"Entering the window of primordial black hole dark matter with x-ray microlensing"* (Phys. Rev. D 111, 043043) and *"Microlensing by fast and slow compact objects"* (arXiv:2604.25434). |
| `wave_optics_lensing.py` | `wave-optics.mp4` | The frequency-domain amplification factor \|F(w)\| for a point mass, sweeping from the wave-optics regime (diffraction suppresses lensing, \|F\| → 1) to the geometric-optics limit (two images interfere). The physics behind the seminar *"Wave-Optics Gravitational Lensing: From X-rays to Gravitational Waves"*. |

## Rendering

```bash
python3 -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt
./render_all.sh                                       # or run either script directly
```

Requirements: Python 3.9+, NumPy, Matplotlib, mpmath, and `ffmpeg` on `PATH`
(`brew install ffmpeg`). `mpmath` is used for the complex confluent
hypergeometric function `1F1` in the wave-optics amplification factor — its
machine-precision `fp` backend overflows for `w` above ~20, so the script runs at
`mp.dps = 25`.

## Shared style

`_style.py` holds the palette (navy `#1a3a52`, teal `#2c7a7b`, burgundy `#8b3a3a`
on warm paper `#fbfaf8`) and render settings (1280×720, 30 fps) so both clips
match the website.

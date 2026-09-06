"""Wave-optics gravitational lensing: the amplification factor from low to high
frequency.

When the wavelength of the signal is not tiny compared with the lens' Einstein
radius, geometric optics breaks down and the lens acts like a diffracting
aperture. For an isolated point mass the frequency-domain amplification factor is

    F(w, y) = exp[ pi w / 4 + i (w/2)(ln(w/2) - 2 phi_m(y)) ]
              * Gamma(1 - i w/2)
              * 1F1( i w/2 ; 1 ; i w y^2 / 2 ),

with dimensionless frequency  w = 8 pi G M_Lz f / c^3  and source position y in
units of the Einstein radius (Nakamura & Deguchi 1999; Takahashi & Nakamura 2003).

  * w << 1 (long wavelength): |F| -> 1, diffraction washes the lensing out.
  * w >> 1 (short wavelength): the two geometric images reappear and interfere,
    so |F| oscillates about sqrt(|mu_+|) + sqrt(|mu_-|).

The animation sweeps the source position y, morphing the curve from a grazing
alignment to a near-perfect one. This is the physics behind the seminar
"Wave-Optics Gravitational Lensing: From X-rays to Gravitational Waves".

Output: ../assets/animations/wave-optics.mp4  (+ .jpg poster)
"""

import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter, FuncAnimation

import mpmath
from mpmath import mp

import _style

_style.apply()
mp.dps = 25  # fp (machine-precision) mpmath overflows Gamma * 1F1 for w >~ 20

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "animations")
os.makedirs(OUT_DIR, exist_ok=True)

# --- grids ---------------------------------------------------------------
W = np.logspace(np.log10(0.1), np.log10(22.0), 300)   # dimensionless frequency
Y = np.linspace(1.5, 0.25, 64)                         # source position sweep


def phi_m(y):
    x_m = 0.5 * (y + math.sqrt(y * y + 4.0))
    return 0.5 * (x_m - y) ** 2 - math.log(x_m)


def amp_factor(w, y):
    """Exact point-mass wave-optics amplification factor F(w, y)."""
    w = float(w)
    y = float(y)
    pm = phi_m(y)
    a = mpmath.mpc(0, w / 2.0)
    phase = mpmath.mpc(0, (w / 2.0) * (math.log(w / 2.0) - 2.0 * pm))
    pref = mpmath.e ** (mpmath.mpf(math.pi) * w / 4.0 + phase)
    val = pref * mpmath.gamma(1 - a) * mpmath.hyp1f1(a, 1, mpmath.mpc(0, w * y * y / 2.0))
    return complex(val)


def geo_band(y):
    """Envelope of |F| in the geometric-optics limit: sqrt(mu+) +/- sqrt(mu-)."""
    root = np.sqrt(y ** 2 + 4.0)
    mu_plus = 0.5 + (y ** 2 + 2.0) / (2.0 * y * root)
    mu_minus = abs(0.5 - (y ** 2 + 2.0) / (2.0 * y * root))
    hi = np.sqrt(mu_plus) + np.sqrt(mu_minus)
    lo = abs(np.sqrt(mu_plus) - np.sqrt(mu_minus))
    return lo, hi


print("evaluating F(w, y) on a %d x %d grid ..." % (len(W), len(Y)))
FGRID = np.empty((len(Y), len(W)))
for j, y in enumerate(Y):
    FGRID[j] = [abs(amp_factor(w, y)) for w in W]
print("done")

# --- figure ------------------------------------------------------------
fig, ax = plt.subplots(figsize=_style.FIGSIZE)
fig.subplots_adjust(left=0.10, right=0.965, top=0.945, bottom=0.155)

ax.set_xscale("log")
ax.set_xlim(W[0], W[-1])
ax.set_ylim(0.0, min(FGRID.max() * 1.12, 3.4))
ax.set_xlabel(r"dimensionless frequency  $w = 8\pi G M_{Lz} f / c^{3}$")
ax.set_ylabel(r"amplification  $|F(w)|$")
ax.grid(True, which="both", alpha=0.5)
ax.axhline(1.0, color=_style.MUTED, lw=0.9, ls=":")
ax.text(0.03, 0.84, r"no lensing,  $|F| \to 1$", transform=ax.transAxes,
        fontsize=8.5, color=_style.MUTED, va="top")
ax.text(0.17, 0.12, "wave optics\n(diffraction)", transform=ax.transAxes,
        fontsize=9, color=_style.NAVY, ha="center")
ax.text(0.83, 0.12, "geometric optics\n(images interfere)", transform=ax.transAxes,
        fontsize=9, color=_style.NAVY, ha="center")

ghost_lines = [ax.plot([], [], color=_style.NAVY, lw=1.0, alpha=0.0)[0] for _ in range(4)]
band = ax.fill_between(W, 0, 0, color=_style.BURGUNDY, alpha=0.10, lw=0)
(curve,) = ax.plot([], [], color=_style.TEAL, lw=2.6)
label = ax.text(0.03, 0.93, "", transform=ax.transAxes, fontsize=10, va="top",
                color=_style.INK)


def frames():
    # sweep in, hold, sweep back out -> clean loop
    idx = list(range(len(Y))) + [len(Y) - 1] * 8 + list(range(len(Y) - 1, -1, -1))
    return idx


def update(j):
    global band
    y = Y[j]
    curve.set_data(W, FGRID[j])

    lo, hi = geo_band(y)
    mask = W > 2.0
    band.remove()
    band = ax.fill_between(
        W[mask], np.full(mask.sum(), lo), np.full(mask.sum(), hi),
        color=_style.BURGUNDY, alpha=0.12, lw=0,
    )

    for k, gl in enumerate(ghost_lines):
        src = j - 6 * (k + 1)
        if src >= 0:
            gl.set_data(W, FGRID[src])
            gl.set_alpha(0.16)
        else:
            gl.set_alpha(0.0)

    label.set_text(rf"source position  $y = {y:.2f}\,\theta_{{\mathrm{{E}}}}$")
    return curve, band, label, *ghost_lines


anim = FuncAnimation(
    fig, update, frames=frames(), blit=False, interval=1000 / _style.FPS
)

mp4_path = os.path.join(OUT_DIR, "wave-optics.mp4")
writer = FFMpegWriter(
    fps=_style.FPS, bitrate=1400,
    extra_args=["-pix_fmt", "yuv420p", "-movflags", "+faststart"],
)
anim.save(mp4_path, writer=writer, dpi=_style.DPI)
update(len(Y) // 2)
fig.savefig(os.path.join(OUT_DIR, "wave-optics.jpg"), dpi=_style.DPI, pil_kwargs={"quality": 85})
print("wrote", mp4_path)

"""Microlensing with an incoherent (finite-size) source -- no wave optics.

A real star is an extended, incoherent source: its light adds in intensity across
the stellar disc.  Writing the source radius in Einstein units as
rho = theta_src / theta_E, the point-source magnification
A_ps(u) = (u^2 + 2) / (u sqrt(u^2 + 4)) is replaced by the uniform-disc average
A_fs(u, rho) (Witt & Mao 1994, ApJ 430, 505).  The divergent point-source peak is
then finite -- A_fs(0, rho) = sqrt(1 + 4/rho^2) -- and, for a near-central passage,
the light curve grows a flat top.  rho is larger for lower-mass lenses (smaller
theta_E), so finite-source effects matter most in exactly that regime -- the one
probed in
  * "Entering the window of primordial black hole dark matter with x-ray
     microlensing" (Phys. Rev. D 111, 043043), and
  * "Microlensing by fast and slow compact objects" (arXiv:2604.25434).

Two sliders are driven in turn, matching
github.com/manns01/projects/blob/main/lensing_finite_source.ipynb:
  * the source position u  -- the star drifts across the line of sight;
  * the dimensionless source size rho.

Left panel: the lens plane.  The extended source and its two image contours come
straight from the point-lens equation
theta_pm = 0.5 s (1 +/- sqrt(1 + 4/|s|^2)) applied to the source boundary.

Output: ../assets/animations/microlensing.mp4  (+ .jpg poster)
"""

import os
import subprocess

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter, FuncAnimation
from matplotlib.patches import Circle, PathPatch
from matplotlib.path import Path
from matplotlib.widgets import Slider

import _style
import finite_source as fs

_style.apply()

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "animations")
os.makedirs(OUT_DIR, exist_ok=True)

# --- geometry -------------------------------------------------------
U0 = 0.08                             # impact parameter (near-central passage)
RHO_A = 0.40                          # source size held fixed while u is swept
RHO_LO, RHO_HI = 0.10, 1.05           # range for the size sweep
TAU = np.linspace(-2.0, 2.0, 160)     # sampling of the light curve in t / t_E
LIM = 1.8

U_OF_T = np.hypot(U0, TAU)
A_POINT = fs.A_ps(U_OF_T)                                    # reference, rho -> 0
RHO_REF = (0.15, RHO_A, 0.90)                                # faint guide curves


# --- storyboard: a list of (tau_head, rho, n_drawn) per frame -------
def _seg_pos(taus, rho):                     # sweep the position slider
    return [(t, rho, i + 1) for i, t in enumerate(taus)]


def _seg_size(rhos, tau):                    # sweep the size slider
    return [(tau, r, len(TAU)) for r in rhos]


def _glide(taus, rho):                       # move the source, curve already full
    return [(t, rho, len(TAU)) for t in taus]


TAU_SWEEP = TAU                         # progressive draw indexes straight into TAU
U_SIZE = 0.75                           # position held here while rho is swept
FRAMES = (
    _seg_pos(TAU_SWEEP, RHO_A)
    + [(TAU[-1], RHO_A, len(TAU))] * 12
    + _glide(np.linspace(TAU[-1], U_SIZE, 14), RHO_A)
    + _seg_size(np.linspace(RHO_A, RHO_HI, 55), U_SIZE)
    + _seg_size(np.linspace(RHO_HI, RHO_LO, 50), U_SIZE)
    + _seg_size(np.linspace(RHO_LO, RHO_A, 28), U_SIZE)
    + [(U_SIZE, RHO_A, len(TAU))] * 12
    + _glide(np.linspace(U_SIZE, TAU[0], 16), RHO_A)
)
N_FRAMES = len(FRAMES)

# cache A_fs(u(TAU); rho) -- reused across frames with the same rho
_A_CACHE = {}


def a_curve(rho):
    key = round(rho, 4)
    if key not in _A_CACHE:
        _A_CACHE[key] = fs.A_fs(U_OF_T, rho)
    return _A_CACHE[key]


def image_path(centre, rho):
    """Compound path of the two image contours; the inner loop is reversed so a
    single non-zero-winding fill gives two blobs when the lens is outside the
    source disc and a clean Einstein-ring annulus when it is inside."""
    outer, inner = fs.image_boundary(centre, rho, n=260)
    inner = inner[::-1]
    verts = np.vstack([outer, outer[:1], inner, inner[:1]])
    codes = (
        [Path.MOVETO] + [Path.LINETO] * (len(outer) - 1) + [Path.CLOSEPOLY]
        + [Path.MOVETO] + [Path.LINETO] * (len(inner) - 1) + [Path.CLOSEPOLY]
    )
    return Path(verts, codes)


# --- figure -------------------------------------------------------
fig, (ax_sky, ax_lc) = plt.subplots(
    1, 2, figsize=_style.FIGSIZE, gridspec_kw=dict(width_ratios=[1.0, 1.25])
)
fig.subplots_adjust(left=0.06, right=0.965, top=0.94, bottom=0.30, wspace=0.30)

# lens plane ------------------------------------------------
ax_sky.set_aspect("equal")
ax_sky.set_xlim(-LIM, LIM)
ax_sky.set_ylim(-LIM, LIM)
ax_sky.set_xticks([])
ax_sky.set_yticks([])
ax_sky.set_title("lens plane", fontsize=11, pad=8)
for spine in ax_sky.spines.values():
    spine.set_visible(False)

ax_sky.plot([-LIM, LIM], [U0, U0], color=_style.MUTED, lw=0.8, ls=":", zorder=1)
image_patch = PathPatch(
    image_path((TAU_SWEEP[0], U0), RHO_A),
    facecolor=_style.BURGUNDY, alpha=0.28, edgecolor=_style.BURGUNDY, lw=1.1,
    zorder=2,
)
ax_sky.add_patch(image_patch)
ax_sky.add_patch(
    Circle((0, 0), 1.0, fill=False, ls=(0, (5, 4)), lw=1.3, ec=_style.NAVY,
           alpha=0.9, zorder=3)
)
source_disc = Circle(
    (TAU_SWEEP[0], U0), RHO_A, facecolor=_style.TEAL, alpha=0.45,
    edgecolor=_style.TEAL, lw=1.3, zorder=4,
)
ax_sky.add_patch(source_disc)
ax_sky.plot(0, 0, marker="x", ms=8, mew=2.0, color=_style.INK, zorder=5)

# light curve ---------------------------------------------
ax_lc.set_xlim(TAU[0], TAU[-1])
ax_lc.set_ylim(1.0, 7.5)                       # small-source & point curves clip
ax_lc.set_xlabel(r"time  $(t-t_0)\,/\,t_{\mathrm{E}}$")
ax_lc.set_ylabel(r"magnification  $A$")
ax_lc.set_title("light curve", fontsize=11, pad=8)
ax_lc.grid(True, alpha=0.6)
ax_lc.axhline(1.0, color=_style.MUTED, lw=0.8, ls=":")

_bbox = dict(boxstyle="round,pad=0.25", fc=_style.PAPER, ec="none", alpha=0.85)
ax_lc.plot(TAU, A_POINT, color=_style.MUTED, lw=1.3, ls=(0, (5, 3)))
ax_lc.text(0.4, 6.9, "point source\n(diverges)", fontsize=8,
           color=_style.MUTED, va="top", ha="left", bbox=_bbox)
for r in RHO_REF:
    ax_lc.plot(TAU, a_curve(r), color=_style.NAVY, lw=1.0, alpha=0.18)

(lc_line,) = ax_lc.plot([], [], color=_style.TEAL, lw=2.4)
(lc_head,) = ax_lc.plot([], [], "o", ms=6, color=_style.TEAL)
read_txt = ax_lc.text(
    0.03, 0.95, "", transform=ax_lc.transAxes, fontsize=9.5, color=_style.INK,
    va="top", bbox=_bbox,
)

# sliders (driven, not interactive) ---------------------
ax_su = fig.add_axes([0.30, 0.135, 0.56, 0.035])
ax_sr = fig.add_axes([0.30, 0.055, 0.56, 0.035])
slider_u = Slider(ax_su, r"source position  $u$", -2.0, 2.0, valinit=-2.0,
                  valfmt="%+.2f", color=_style.NAVY, initcolor="none")
slider_r = Slider(ax_sr, r"source size  $\rho$", 0.0, RHO_HI + 0.05,
                  valinit=RHO_A, valfmt="%.2f", color=_style.TEAL, initcolor="none")
for s in (slider_u, slider_r):
    s.label.set_fontsize(9)
    s.valtext.set_fontsize(9)
    s.poly.set_alpha(0.55)


def init():
    lc_line.set_data([], [])
    lc_head.set_data([], [])
    read_txt.set_text("")
    return image_patch, source_disc, lc_line, lc_head, read_txt


def update(f):
    tau, rho, ndrawn = FRAMES[f]
    curve = a_curve(rho)

    source_disc.set_radius(rho)
    source_disc.center = (tau, U0)
    image_patch.set_path(image_path((tau, U0), rho))

    lc_line.set_data(TAU[:ndrawn], curve[:ndrawn])
    ih = int(np.argmin(np.abs(TAU - tau)))
    lc_head.set_data([tau], [curve[ih]])
    read_txt.set_text(
        rf"$\rho = {rho:.2f}$   $u = {tau:+.2f}$   $A = {curve[ih]:.2f}$"
    )

    slider_u.set_val(tau)
    slider_r.set_val(rho)
    return image_patch, source_disc, lc_line, lc_head, read_txt


anim = FuncAnimation(
    fig, update, frames=N_FRAMES, init_func=init, blit=False,
    interval=1000 / _style.FPS,
)

mp4_path = os.path.join(OUT_DIR, "microlensing.mp4")
writer = FFMpegWriter(
    fps=_style.FPS, bitrate=1200,
    extra_args=["-pix_fmt", "yuv420p", "-movflags", "+faststart"],
)
anim.save(mp4_path, writer=writer, dpi=_style.DPI)

# poster: pull one frame straight from the finished clip (savefig after
# FuncAnimation.save re-fires init_func and would blank the dynamic artists)
_poster_frame = 88                               # flat-topped peak, both knobs shown
subprocess.run(
    ["ffmpeg", "-y", "-loglevel", "error",
     "-i", mp4_path, "-vf", f"select=eq(n\\,{_poster_frame})",
     "-frames:v", "1", "-q:v", "3",
     os.path.join(OUT_DIR, "microlensing.jpg")],
    check=True,
)
print("wrote", mp4_path)

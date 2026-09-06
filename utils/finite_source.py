"""Finite-source point-lens microlensing (no wave optics).

Analytic point-lens equations following Witt & Mao (1994), ApJ 430, 505 — the
same equations used in
github.com/manns01/projects/blob/main/lensing_finite_source.ipynb.

All lengths are in units of the Einstein radius theta_E.  A source of physical
angular radius theta_src has rho = theta_src / theta_E, so rho is *larger* for
lower-mass lenses (smaller theta_E): finite-source effects grow as the lens mass
drops.

Provided here:
  * A_ps(u)                 point-source magnification  (u^2 + 2) / (u sqrt(u^2+4))
  * A_fs(u, rho)            uniform finite-disc magnification
  * image_boundary(c, rho)  the two lensed image contours of the source boundary
"""

import numpy as np


# --- point source --------------------------------------------------------
def A_ps(u):
    """Paczynski point-source magnification."""
    u = np.asarray(u, dtype=float)
    return (u ** 2 + 2.0) / (u * np.sqrt(u ** 2 + 4.0))


# --- image contours (Witt & Mao 1994 lens equation) --------------------
def image_boundary(centre, rho, n=400):
    """Lensed contours of a circular source boundary.

    A source-plane point s maps to two images at

        theta_pm = 0.5 * s * (1 +/- sqrt(1 + 4 / |s|^2))

    i.e. at radii 0.5(|s| +/- sqrt(|s|^2 + 4)) along the s direction.
    `centre` is the (x, y) of the source centre; `rho` its radius.
    Returns (outer_xy, inner_xy), each an (n, 2) array tracing a closed curve.
    """
    phi = np.linspace(0.0, 2.0 * np.pi, n)
    sx = centre[0] + rho * np.cos(phi)
    sy = centre[1] + rho * np.sin(phi)
    s2 = sx ** 2 + sy ** 2
    fac = np.sqrt(1.0 + 4.0 / s2)
    outer = np.column_stack([0.5 * sx * (1.0 + fac), 0.5 * sy * (1.0 + fac)])
    inner = np.column_stack([0.5 * sx * (1.0 - fac), 0.5 * sy * (1.0 - fac)])
    return outer, inner


def _polygon_area(xy):
    """|signed area| of a closed polygon (shoelace)."""
    x, y = xy[:, 0], xy[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def A_fs_from_contours(u, rho, n=2000):
    """Magnification as (image area) / (source area) — the definition Witt & Mao
    integrate.  Used only as an independent cross-check of `A_fs`.

    When the lens sits outside the source disc (u >= rho) the two images are
    separate blobs and their areas add; when it sits inside (u < rho) the images
    merge into one annulus, so the inner contour is a hole and its area subtracts.
    """
    outer, inner = image_boundary((u, 0.0), rho, n=n)
    a_out, a_in = _polygon_area(outer), _polygon_area(inner)
    total = a_out + a_in if u >= rho else a_out - a_in
    return total / (np.pi * rho ** 2)


# --- finite-source magnification --------------------------------------
def A_fs(u, rho, n_theta=400):
    """Magnification of a uniform circular source of radius `rho` whose centre
    is a distance `u` from the lens.

    Singularity-free 1-D form of the Witt & Mao (1994) result
    (Lee, Riffeser, Seitz & Bender 2009, eq. 6):

        A_fs = (1 / (pi rho^2)) * int_0^pi [ F(u2) - F(u1) ] dtheta ,
        F(w) = w sqrt(w^2 + 4)         [ = antiderivative of  w * A_ps(w) ] ,

    with the source-disc chord along azimuth theta

        u1, u2 = u cos(theta) -/+ sqrt(rho^2 - u^2 sin^2(theta)).

    Two regimes -- Witt & Mao give a *separate* closed form exactly at u = rho
    because their elliptic-integral version is singular there; this 1-D version
    is finite at u = rho, but the chord's sqrt goes to zero at the endpoint
    theta = arcsin(rho/u), so for u >= rho we integrate in

        psi   with   u sin(theta) = rho sin(psi),   psi in [0, pi/2],

    which turns  sqrt(rho^2 - u^2 sin^2 theta)  into  rho cos(psi)  -- smooth to
    the endpoint -- and keeps A_fs and its slope well resolved right across
    u = rho.  (The magnification itself is continuous there; d A_fs / d u has a
    genuine logarithmic cusp -- a real feature of a sharp-edged source.)

    Central peak: A_fs(0, rho) = sqrt(1 + 4 / rho^2).
    """
    u = np.atleast_1d(np.asarray(u, dtype=float))
    rho = float(rho)
    out = np.empty_like(u)

    if rho <= 0.0:
        return A_ps(u if u.size > 1 else u[0])

    def F(w):
        return w * np.sqrt(w * w + 4.0)

    inside_th = np.linspace(0.0, np.pi, n_theta)          # for u < rho
    psi = np.linspace(0.0, 0.5 * np.pi, n_theta)          # for u >= rho
    sin_psi, cos_psi = np.sin(psi), np.cos(psi)

    for i, uu in enumerate(u):
        if uu >= rho:                       # lens outside (or on) the source disc
            base = np.sqrt(np.clip(uu ** 2 - (rho * sin_psi) ** 2, 1e-18, None))
            disc = rho * cos_psi
            integ = (F(base + disc) - F(base - disc)) * (rho * cos_psi / base)
            out[i] = np.trapz(integ, psi) / (np.pi * rho ** 2)
        else:                               # lens inside the source disc
            disc = np.sqrt(np.clip(rho ** 2 - (uu * np.sin(inside_th)) ** 2, 0.0, None))
            integ = F(uu * np.cos(inside_th) + disc)       # u1 = 0
            out[i] = np.trapz(integ, inside_th) / (np.pi * rho ** 2)

    return out if out.size > 1 else float(out[0])


# --- self-test --------------------------------------------------------
if __name__ == "__main__":
    # point-source limit
    uu = np.array([0.05, 0.2, 0.5, 1.0, 2.0])
    assert np.allclose(A_fs(uu, 1e-6), A_ps(uu), rtol=2e-3), "rho->0 limit"

    # central peak cap
    for r in (0.1, 0.3, 0.5, 1.0):
        assert abs(A_fs(0.0, r) - np.sqrt(1 + 4 / r ** 2)) < 1e-4, f"peak rho={r}"

    # wings untouched
    assert abs(A_fs(1.5, 0.4) / A_ps(1.5) - 1.0) < 1e-2, "wing"

    # peak decreases with source size
    peaks = [A_fs(0.0, r) for r in (0.1, 0.3, 0.6, 1.0)]
    assert all(a > b for a, b in zip(peaks, peaks[1:])), "monotonic in rho"

    # 1-D integral vs image-area definition (skip the singular u == rho config,
    # where a source-boundary point sits on the lens and the contour blows up)
    for r in (0.15, 0.4, 0.8):
        for uu_ in (0.0, 0.5 * r, 1.4 * r, 1.1):
            a1 = A_fs(uu_, r)
            a2 = A_fs_from_contours(uu_, r)
            assert abs(a1 / a2 - 1.0) < 1e-2, f"area check u={uu_} rho={r}: {a1} {a2}"

    print("finite_source: all checks passed")

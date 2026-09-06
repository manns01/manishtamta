"""Convert world-atlas TopoJSON land into a single SVG path in equirectangular
pixel space, for the collaborators map.

Usage:
    curl -sL https://cdn.jsdelivr.net/npm/world-atlas@2/land-110m.json -o land-110m.json
    python3 build_worldmap.py land-110m.json > land_path.txt

The map uses viewBox "0 0 1000 500":
    x = (lon + 180) / 360 * 1000
    y = (90 - lat) / 180 * 500
so a marker at (lat, lon) uses the same two formulas — see collaborators.html.
"""

import json
import sys

W, H = 1000.0, 500.0


def decode_arcs(topo):
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    arcs = []
    for arc in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx
            y += dy
            lon = x * sx + tx
            lat = y * sy + ty
            px = (lon + 180.0) / 360.0 * W
            py = (90.0 - lat) / 180.0 * H
            pts.append((px, py))
        arcs.append(pts)
    return arcs


def ring_to_path(arc_indices, arcs):
    coords = []
    for idx in arc_indices:
        if idx >= 0:
            seg = arcs[idx]
        else:
            seg = arcs[~idx][::-1]
        if coords:
            seg = seg[1:]
        coords.extend(seg)
    if len(coords) < 4:
        return ""
    xs = [x for x, _ in coords]
    ys = [y for _, y in coords]
    if (max(xs) - min(xs)) < 1.3 and (max(ys) - min(ys)) < 1.3:
        return ""  # drop specks
    # round to integers and drop consecutive duplicates
    out = []
    for x, y in coords:
        p = (round(x), round(y))
        if not out or out[-1] != p:
            out.append(p)
    if len(out) < 4:
        return ""
    return "M" + " ".join(f"{x},{y}" for x, y in out) + "Z"


def main(path):
    topo = json.load(open(path))
    arcs = decode_arcs(topo)
    geom = topo["objects"]["land"]["geometries"]
    parts = []
    for g in geom:
        if g["type"] == "Polygon":
            polys = [g["arcs"]]
        elif g["type"] == "MultiPolygon":
            polys = g["arcs"]
        else:
            continue
        for poly in polys:
            for ring in poly:
                parts.append(ring_to_path(ring, arcs))
    sys.stdout.write("".join(parts))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "land-110m.json")

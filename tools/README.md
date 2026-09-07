# tools/

## build_worldmap.py

Regenerates the land silhouette used by the map on `collaborators.html`.
(`build_worldmap.py` itself is kept locally and not committed.)

```bash
curl -sL https://cdn.jsdelivr.net/npm/world-atlas@2/land-110m.json -o land-110m.json
python3 build_worldmap.py land-110m.json > land_path.txt
```

Then paste the contents of `land_path.txt` into `collaborators.html` as the
`d="…"` of `<path class="land">`. The SVG uses `viewBox="0 40 1000 378"` with an
equirectangular projection:

    x = (lon + 180) / 360 * 1000
    y = (90 - lat) / 180 * 500

so a new pin at `(lat, lon)` uses those same two formulas for its `cx`/`cy`.

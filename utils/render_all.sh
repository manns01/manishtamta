#!/usr/bin/env bash
# Render every research animation into ../assets/animations/ (.mp4 + .jpg poster).
set -euo pipefail
cd "$(dirname "$0")"

python3 microlensing_lightcurve.py
python3 wave_optics_lensing.py

echo
echo "Rendered files:"
ls -lh ../assets/animations/

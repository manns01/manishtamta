# Manish Tamta — academic website

A small, dependency-free static site (plain HTML + CSS + a little vanilla JS).
No build step. The only external requests are Google Fonts (Inter + Source Serif 4).

```
website/
├── index.html                 home: about · research (+ animations) · publications · contact
├── talks.html                  talks, posters & schools
├── cv.html                     full CV (+ PDF download)
├── collaborators.html          co-authors + world map of where they work
├── assets/
│   ├── css/style.css           design system + layout (light/dark)
│   ├── js/main.js              nav, scrollspy, theme toggle, reveal, map ↔ card sync
│   ├── img/                    headshot.jpg, favicon.svg
│   └── animations/             microlensing.mp4 / wave-optics.mp4 (+ .jpg posters)
├── files/CV_Manish_Tamta.pdf   linked from the CV page
├── utils/                      Python sources for the two research animations
└── tools/                      build_worldmap.py — regenerates the map's land path
```

The header/footer markup is duplicated across the four HTML pages (no templating).
If you change a nav link, change it in all four.

## Preview locally

```bash
cd website
python3 -m http.server 8000
# open http://localhost:8000/
```

`?theme=light` / `?theme=dark` on the URL forces a theme (otherwise it follows the
system setting, and the header toggle overrides + remembers your choice).

## Before publishing — things to check

1. **GitHub link.** `index.html` uses `https://github.com/manns01` in the hero and
   Contact profile lists — confirm the handle.
2. **Canonical / Open Graph URLs.** `index.html` `<head>` assumes
   `https://manns01.github.io/manishtamta/`. Update if the site lives elsewhere.
3. **Journal DOI.** The Phys. Rev. D link uses the standard DOI
   `10.1103/PhysRevD.111.043043` — double-check it resolves.

Scholar, arXiv, INSPIRE-HEP, ORCID, X and LinkedIn links are set to real profiles.

## Deploy (GitHub Pages)

This repo is served as a **project site** at
`https://manns01.github.io/manishtamta/` (repo `manns01/manishtamta`, branch
`main`, "Deploy from a branch" → `/root`). `.nojekyll` publishes every file
verbatim (no Jekyll build). All internal links are relative, so moving it to a
different subpath, the account root, or a custom domain needs only the absolute
URLs in the `<head>`s (`canonical`, `og:url`, `og:image`, `twitter:image`,
JSON-LD `url`) updated — search the four HTML files for `manns01.github.io`.

First push:

```bash
# on GitHub, create an empty repo:  manns01/manishtamta
git remote add origin https://github.com/manns01/manishtamta.git
git push -u origin main
# then: repo Settings → Pages → Source: Deploy from a branch → main / (root)
```

## Regenerating the animations

See `utils/README.md`. In short: `pip install -r utils/requirements.txt`
(needs `ffmpeg` on PATH), then `./utils/render_all.sh`. Output MP4s + poster
frames are written straight into `assets/animations/`. The microlensing figure
uses the finite-source point-lens equations (Witt & Mao 1994) in
`utils/finite_source.py`.

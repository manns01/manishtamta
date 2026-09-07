# Manish Tamta — website

Source for **https://manns01.github.io/manishtamta/** — a small, dependency-free
static site (plain HTML + CSS + a little vanilla JS, no build step). The only
external requests are Google Fonts (Inter + Source Serif 4).

```
├── index.html            home: about · research (+ animations) · publications · contact
├── talks.html            talks, posters & schools
├── cv.html               CV (+ PDF download)
├── collaborators.html    co-authors + world map
├── assets/
│   ├── css/style.css     design system + layout (light / dark)
│   ├── js/main.js         nav, scrollspy, theme toggle, reveal, map interactions
│   ├── img/              headshot.jpg, favicon.svg
│   └── animations/       microlensing.mp4 / wave-optics.mp4 (+ .jpg posters)
└── files/                CV PDF
```

The Python that renders the research animations and the world-map land path is
kept locally (`utils/`, `tools/`) and is not part of this repo; only the
rendered `assets/animations/` files ship with the site.

The header and footer markup is copied across the four HTML pages (no templating);
edit a nav link in all four.

## Preview locally

```bash
python3 -m http.server 8000     # then open http://localhost:8000/
```

`?theme=light` / `?theme=dark` forces a theme; otherwise it follows the system
setting and the header toggle remembers your choice.

## Deploy

Served by GitHub Pages from `main` (`.nojekyll`, no build). Push to update:

```bash
git add -A && git commit -m "…" && git push
```

Internal links are relative, so moving the site only needs the absolute URLs in
the four `<head>`s updated (`grep -rl manns01.github.io *.html`).

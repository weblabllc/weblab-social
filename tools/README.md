# Carousel tooling

Slides are HTML rendered to 1080×1350 PNG with Playwright (Chromium).

- `rag.html` — base stylesheet (brand tokens, Google Sans, flask mark symbol) + the first carousel.
- `build_posts.py` — every other carousel as data; renders to `out/<slug>/NN.png`.
  `python3 build_posts.py <slug> [<slug>…]` renders only the named posts.

Setup (once): `npm i @fontsource/google-sans @fontsource/jetbrains-mono` next to these files,
`pip install playwright && playwright install chromium`.

Flask geometry and colors mirror `weblabllc/WebLab` → `src/brand/flask.js`, `src/styles/global.scss`.

## Video covers (Higgsfield)

`overlay.py <slug> <clip.mp4>` puts slide 01 of a post (title, logo, footer) over a clip and writes
`cover-4x5.mp4` (carousel slide 01), `reel-9x16.mp4` and a still `cover-4x5.jpg`. Needs ffmpeg.
Prompts and clip settings: `../higgsfield/PROMPTS.md`.

## Paper theme

`build_paper.py` renders the light editorial variant (paper ground, ink text, amber accent, dark CTA slide) from the same content. Used from 22.10 to break up the dark rows in the grid.

## Reels

`reels.py <slug>` renders a 1080×1920 kinetic-type Reel (`reel_engine.py`: scene zoom/blur transitions, frosted-glass wipes, line-mask text, counters, strikes) to `out-reels/<slug>/reel.mp4` + `cover.jpg`. `reels.py --preview` makes a quick frame sheet without video. Finished reels live in `../reels/`.

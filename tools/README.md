# Carousel tooling

Slides are HTML rendered to 1080×1350 PNG with Playwright (Chromium).

- `rag.html` — base stylesheet (brand tokens, Google Sans, flask mark symbol) + the first carousel.
- `build_posts.py` — every other carousel as data; renders to `out/<slug>/NN.png`.
  `python3 build_posts.py <slug> [<slug>…]` renders only the named posts.

Setup (once): `npm i @fontsource/google-sans @fontsource/jetbrains-mono` next to these files,
`pip install playwright && playwright install chromium`.

Flask geometry and colors mirror `weblabllc/WebLab` → `src/brand/flask.js`, `src/styles/global.scss`.

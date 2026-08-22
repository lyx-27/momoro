# Momoro — meme mascots gallery

A dark-theme static gallery for 124 cute 3D clay-style meme mascots. Fully
self-contained; no build step, no backend.

## Features
- **Dark theme** that makes the colorful mascots pop; accent color per card is
  sampled from each mascot's own background.
- **Gallery lightbox** — clicking a mascot opens a polished preview view (with a
  soft accent glow), keyboard navigable (← → Esc), not a raw single image.
- **Preview vs. original** — the grid and lightbox show fast 512px `.webp`
  thumbnails; the **Download** button always delivers the full-res original PNG.
- **My Collection** — favorite mascots (♥) are saved in `localStorage` and can
  be viewed together; a badge shows the count.
- **Multi-language** — EN / 中文 toggle (persisted); auto-detects on first visit.
- **Search + category filter** — Dogs / Cats / Sea / Birds / Critters / Wild.
- **View on GitHub** link (set the URL in `app.js`).

## Run locally
The page loads `data/mascots.json` via `fetch`, so open it over HTTP (not
`file://`):

```bash
cd site
python3 -m http.server 8123
# open http://127.0.0.1:8123/
```

## Configure
Edit the top of `app.js`:

```js
const CONFIG = {
  projectName: "Momoro",
  githubUrl: "https://github.com/lyx-27/momoro",
};
```

## Deploy
It's a plain static folder — host anywhere:
- **GitHub Pages**: push `site/` (or its contents) and enable Pages.
- **Cloudflare Pages / Netlify / Vercel**: point at this folder, no build command.
- **Cloudflare R2 / any object storage + CDN**: upload the folder as-is.

## New mascots
Generate more mascots with the bundled skill generator in the repo root
(`generate_mascot.py`, see the top-level README), then drop the PNGs into
`images/` and add matching entries to `data/mascots.json`.

## Structure
```
site/
  index.html
  styles.css
  app.js
  logo.png  favicon.png
  data/mascots.json
  images/<slug>.png          # full-res originals (download)
  images/thumbs/<slug>.webp  # 512px display thumbnails (preview)
```

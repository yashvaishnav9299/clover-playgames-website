# Clover Play Games — Coming Soon

A single-page "coming soon" teaser site for Clover Play Games. Plain HTML/CSS, no build step, no dependencies except one Google Font loaded via CDN.

## Project structure

```
clover-play-games/
├── index.html          # All page markup
├── css/
│   └── styles.css      # All styles (layout, type, responsive breakpoints)
├── images/
│   ├── hero-desktop-1672.jpg   # Desktop background, standard screens (≤1700px)
│   ├── hero-desktop-2400.jpg   # Desktop background, large monitors / retina
│   ├── hero-desktop-2560.jpg   # Desktop background, very large monitors (2300px+)
│   ├── hero-mobile-941.jpg     # Mobile background, standard phones
│   └── hero-mobile-1080.jpg    # Mobile background, retina phones
└── README.md
```

Everything the browser needs is in these five items — no build tools, no `node_modules`, no package.json. Open `index.html` in a browser and it works.

## Running it locally

Just open `index.html` directly, or serve it with any static server, e.g.:

```bash
# Python
python3 -m http.server 8000

# Node (if you have it)
npx serve .
```

Then visit `http://localhost:8000`.

## Deploying (GitHub Pages)

1. Push this repo to GitHub.
2. In the repo, go to **Settings → Pages**.
3. Under "Build and deployment", set **Source** to `Deploy from a branch`, branch `main`, folder `/ (root)`.
4. Save. GitHub will publish the site at `https://<your-username>.github.io/<repo-name>/` within a minute or two.

Netlify and Vercel both also support "drag the folder in" deploys if you'd rather skip GitHub Pages — no config needed either way since there's no build step.

## Editing the background art

The right image is picked automatically by screen width and pixel density (see the `.hero-bg` rules in `css/styles.css`). To swap in new artwork, replace the files in `images/` **keeping the same filenames**, or update the filenames referenced in `css/styles.css` if you rename them.

Recommended source sizes if you're re-exporting:
- Desktop: 1672×941 (base), 2400×1350 (large/retina), 2560×1440 (very large screens) — all 16:9
- Mobile: 941×1672 (base), 1080×1920 (retina) — both 9:16

## Editing text/copy

All copy lives directly in `index.html` — headline, subtext, button labels, footer — no CMS or data file involved.

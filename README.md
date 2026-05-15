# WEST Product Catalogue

Interactive product catalogue for WEST IoT sensor product line, featuring bilingual (EN/ZH) support, in-browser gallery/video/document management with localStorage persistence.

## Products

| SKU | Description |
|---|---|
| WE-X280 | Industrial Edge Computing Gateway |
| WE-T214 | 3-in-1 Soil Sensor Transmitter |
| WE-T800 | Multi-Function Field Monitor |
| WE-W200 | Professional Weather Station |

## Features

- **Product pages** — Overview, highlights, gallery, videos, specs, downloads, contact
- **Bilingual** — Full English/Chinese toggle on all pages
- **Gallery Manager** — Upload, categorize (Main/Detail/Other), delete images; hero image auto-syncs with Main category
- **Video Manager** — Upload, categorize, click-to-play video list; multi-video support
- **Document Manager** — Upload, categorize (User Manual/Specification/Instructions/Support/Guide), format badges (PDF/Word/Excel/Markdown/Image), download buttons
- **Catalog page** — Product index with live Download count, per-row delete with localStorage cleanup
- **Persistent** — All user edits (add/delete/categorize) stored in browser localStorage
- **Print-ready** — A4 print styles for catalogue export

## Usage

Open `index.html` in a browser, or visit the [GitHub Pages site](https://myparallel.github.io/west_catalogue/).

### Adding a new product

1. Copy `config.sample.json` → `configs/NEW-SKU.json`
2. Fill in product details, images, documents, videos
3. Place assets in `products/NEW-SKU/images/` and `products/NEW-SKU/docs/`
4. Run `python generate.py configs/NEW-SKU.json`
5. Add entry to the `products` array in `index.html`
6. Open `index.html` to verify

### File structure

```
├── index.html              # Catalogue landing page
├── config.sample.json      # Product config template
├── generate.py             # Static page generator
├── configs/                # Product JSON configs
├── products/               # Generated product pages
│   └── <SKU>/
│       ├── index.html
│       ├── images/
│       └── docs/
└── assets/
    ├── css/main.css
    └── js/main.js
```

## Tech

Pure HTML/CSS/JS — no frameworks, no build tools. Python script (`generate.py`) for static page generation from JSON configs. GitHub Actions for automatic Pages deployment.

# Maestro website

The product page for [Maestro](https://github.com/pughouselabs/omarchy-maestro), the
settings app, bar widget and background service for Logitech MX mice on Omarchy.

Live at https://pughouselabs.github.io/maestro-site/

The page is plain HTML, CSS and a little JavaScript. There is no build step, no
framework, and nothing is loaded from other sites: no fonts, analytics or cookies.
All asset paths are relative, so it works from any folder or subpath.

## Preview locally

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000/ and stop the server with Ctrl+C when you are done.

## Layout

| Path | What it is |
|---|---|
| `index.html` | The page |
| `assets/site.css`, `assets/site.js` | Styles; theme toggle, copy buttons, tabs and gesture presets |
| `assets/img/` | Generated images (WebP in several sizes, PNG fallbacks, favicon, social card) |
| `tools/build_images.py` | Rebuilds every image in `assets/img/` from a plugin checkout |
| `tools/refresh-screenshots` | Rebuilds only the app screenshots from a plugin checkout |
| `.github/workflows/pages.yml` | Deploys the site to GitHub Pages on every push to `main` |

The workflow publishes `index.html`, `assets/` and `LICENSE` only. If you add a
top-level page or file (for example `404.html`), add it to the "Stage site" step.

## Update images

Images come from a checkout of the plugin repository, so this repository never holds
the large source renders. Both tools need Python 3.10+ and Pillow with WebP support.

After a new Maestro release, refresh the app screenshots from its
`docs/screenshots/*.png`:

```bash
git clone https://github.com/pughouselabs/omarchy-maestro ~/src/omarchy-maestro
tools/refresh-screenshots ~/src/omarchy-maestro
```

To rebuild everything, including the device renders, social card and favicon:

```bash
python3 tools/build_images.py --plugin ~/src/omarchy-maestro
```

Both commands check that every source file exists before changing anything. Review the
result with `git status` and a local preview, and undo with `git checkout -- assets/img`.
Lint the tool with `uvx ruff check tools` and `uvx ruff format --check tools`.

## Credits and licenses

- Page code (HTML, CSS, JavaScript, tools) and the Maestro mark: MIT, see [LICENSE](LICENSE).
- MX Master 2S images (`hero-*`, `thumb-*`, `top-down-*`, the device in the app
  screenshots and in `og-card.jpg`) are rendered from
  [Logitech MX master 2S (@danish_blends)](https://sketchfab.com/3d-models/logitech-mx-master-2s-danish-blends-e8f3235951934a01aba4e0ee3de72e71)
  by **danish_blends**, licensed
  [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). Changes: new lighting
  and camera, status light hidden, contact shadow added. These images are **not** covered
  by the MIT license and may not be used commercially.

Maestro is not affiliated with or endorsed by Logitech. Logitech and MX Master are
trademarks of their owners.

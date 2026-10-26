#!/usr/bin/env python3
"""Build the website's optimized images from a Maestro plugin checkout.

    python3 tools/build_images.py --plugin ~/src/omarchy-maestro
    python3 tools/build_images.py --plugin ~/src/omarchy-maestro --only screenshots

Sources come from the plugin repository: device renders (app/assets/devices/mx-master),
app screenshots (docs/screenshots) and the logo (packaging/desktop). Outputs go to
assets/img/ in this site and are committed, so the site itself has no build step.
Needs Pillow with WebP support.
"""

import argparse
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SITE = Path(__file__).resolve().parents[1]
OUT = SITE / "assets/img"
FONT_DIR = Path("/usr/share/fonts/noto")

# Screens the page shows. Each must exist as docs/screenshots/<name>.png in the plugin.
SCREENSHOTS = (
    "device",
    "device-light",
    "gesture-panel",
    "gesture-panel-light",
    "home",
    "home-light",
    "smart-actions",
    "smart-actions-light",
)
# PNG fallbacks: light screens, plus the dark Buttons screen used in the theme pair.
SCREENSHOT_PNGS = {
    "device",
    "device-light",
    "gesture-panel-light",
    "home-light",
    "smart-actions-light",
}


def trimmed(path, pad=0.02):
    im = Image.open(path).convert("RGBA")
    box = im.getchannel("A").getbbox()
    im = im.crop(box)
    p = round(max(im.size) * pad)
    canvas = Image.new("RGBA", (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0))
    canvas.paste(im, (p, p))
    return canvas


def resized(im, width):
    if im.width <= width:
        return im.copy()
    height = round(im.height * width / im.width)
    return im.resize((width, height), Image.LANCZOS)


def save_webp(im, name, quality=80):
    im.save(OUT / f"{name}.webp", "WEBP", quality=quality, method=6)


def save_png(im, name, colors=None):
    if colors:
        im = im.quantize(
            colors=colors, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.FLOYDSTEINBERG
        )
    im.save(OUT / f"{name}.png", "PNG", optimize=True)


def device_images(device):
    # Hero renders: rim-lit version for dark pages, studio version for light pages.
    for src, name in (("hero-rim.png", "hero-dark"), ("hero.png", "hero-light")):
        im = trimmed(device / src)
        for width in (640, 960, 1400):
            save_webp(resized(im, width), f"{name}-{width}", quality=82)
        if name == "hero-light":
            save_png(resized(im, 960), f"{name}-960", colors=256)

    top = trimmed(device / "top-down.png", pad=0.0)
    for width in (360, 560):
        save_webp(resized(top, width), f"top-down-{width}", quality=82)
    save_png(resized(top, 560), "top-down-560", colors=256)

    thumb = Image.open(device / "thumb.png").convert("RGBA")
    for width in (480, 800):
        save_webp(resized(thumb, width), f"thumb-{width}", quality=80)
    save_png(resized(thumb, 800), "thumb-800", colors=256)


def screenshots(shots):
    for name in SCREENSHOTS:
        im = Image.open(shots / f"{name}.png").convert("RGB")
        for width in (800, 1600):
            save_webp(resized(im, width), f"shot-{name}-{width}", quality=84)
        if name in SCREENSHOT_PNGS:
            save_png(resized(im, 1600), f"shot-{name}-1600", colors=256)


def font(name, size):
    try:
        return ImageFont.truetype(str(FONT_DIR / name), size)
    except OSError:
        return ImageFont.load_default(size)


def social_card(device, icons):
    # 1200 x 630 Open Graph / Twitter card.
    w, h = 1200, 630
    card = Image.new("RGB", (w, h), (11, 13, 16))
    glow = Image.new("L", (w, h), 0)
    ImageDraw.Draw(glow).ellipse((560, -40, 1260, 660), fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(140))
    tint = Image.new("RGB", (w, h), (34, 48, 72))
    card = Image.composite(tint, card, glow)

    mouse = resized(trimmed(device / "hero-rim.png", pad=0.0), 600)
    card.paste(mouse, (w - mouse.width + 30, (h - mouse.height) // 2 + 24), mouse)

    draw = ImageDraw.Draw(card)
    icon = Image.open(icons / "maestro-256.png").convert("RGBA").resize((72, 72), Image.LANCZOS)
    card.paste(icon, (72, 76), icon)
    draw.text((164, 92), "Maestro", font=font("NotoSans-Bold.ttf", 40), fill=(236, 239, 243))
    title = font("NotoSans-Bold.ttf", 54)
    draw.text((72, 210), "Your MX mouse,", font=title, fill=(236, 239, 243))
    draw.text((72, 278), "at home on Omarchy.", font=title, fill=(236, 239, 243))
    body = font("NotoSans-Regular.ttf", 27)
    draw.text((72, 392), "Buttons, gestures, per-app profiles and", font=body, fill=(166, 175, 188))
    draw.text((72, 430), "pointer settings for Logitech MX mice.", font=body, fill=(166, 175, 188))
    small = font("NotoSans-Medium.ttf", 22)
    draw.text((72, 528), "Open source  ·  MIT  ·  Pughouse Labs", font=small, fill=(138, 180, 255))
    card.save(OUT / "og-card.jpg", "JPEG", quality=88, optimize=True, progressive=True)


def logo(desktop):
    icons = desktop / "icons"
    for size, name in ((32, "favicon-32"), (180, "apple-touch-icon")):
        src = Image.open(icons / "maestro-512.png").convert("RGBA")
        src.resize((size, size), Image.LANCZOS).save(OUT / f"{name}.png", "PNG", optimize=True)
    # The app icon is named after the plugin id, which can change between releases.
    svg = sorted(desktop.glob("io.github.*.maestro.svg"))
    shutil.copyfile(svg[0], OUT / "favicon.svg")


def check_sources(plugin, only):
    needed = [plugin / "docs/screenshots" / f"{name}.png" for name in SCREENSHOTS]
    if only == "all":
        device = plugin / "app/assets/devices/mx-master"
        desktop = plugin / "packaging/desktop"
        needed += [device / f for f in ("hero.png", "hero-rim.png", "thumb.png", "top-down.png")]
        needed += [desktop / "icons/maestro-256.png", desktop / "icons/maestro-512.png"]
        if not list(desktop.glob("io.github.*.maestro.svg")):
            needed.append(desktop / "io.github.*.maestro.svg")
    return [p for p in needed if not p.is_file()]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--plugin", type=Path, required=True, help="Maestro plugin checkout")
    parser.add_argument("--only", choices=("all", "screenshots"), default="all")
    args = parser.parse_args(argv)
    plugin = args.plugin.expanduser().resolve()

    missing = check_sources(plugin, args.only)
    if missing:
        print("Missing source files; nothing was changed:", file=sys.stderr)
        for path in missing:
            print(f"  {path}", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    pattern = "shot-*" if args.only == "screenshots" else "*"
    for old in OUT.glob(pattern):
        if old.suffix in (".png", ".webp", ".jpg", ".svg"):
            old.unlink()

    screenshots(plugin / "docs/screenshots")
    if args.only == "all":
        device = plugin / "app/assets/devices/mx-master"
        device_images(device)
        social_card(device, plugin / "packaging/desktop/icons")
        logo(plugin / "packaging/desktop")

    files = list(OUT.iterdir())
    total = sum(p.stat().st_size for p in files)
    print(f"wrote {len(files)} files ({total // 1024} KB) in {OUT.relative_to(SITE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

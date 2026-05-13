"""Generate assets/avatar.svg by wrapping IMG_1032.jpg in a circular clip.

Output: assets/avatar.svg

Why this exists:
  GitHub's markdown sanitizer strips `style="..."` from <img> tags, so the
  original `border-radius: 50%` never actually rendered as a circle on the
  profile. Embedding the JPEG inside an SVG that uses a <clipPath> circle
  is the only reliable way to get a true circular avatar on a GitHub README
  without resizing/cropping the source image by hand.

The image is embedded as base64 inside the SVG so the file is fully
self-contained and works regardless of GitHub's cross-origin image loading
rules for nested <image href="..."> tags.
"""

from __future__ import annotations

import base64
import io
import os
import sys
from pathlib import Path

from PIL import Image, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import ASSETS_DIR, PALETTE  # noqa: E402

PROJECT_ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCE_IMAGE = PROJECT_ROOT / "IMG_1032.jpg"
EMBED_PIXELS = 320  # render at 2x of display size for retina screens
JPEG_QUALITY = 82


def compress_source(path: Path, target_px: int, quality: int) -> bytes:
    """Resize source JPEG to a centered square and re-encode, returning raw bytes."""
    with Image.open(path) as im:
        # Respect EXIF orientation so the avatar isn't rotated
        im = ImageOps.exif_transpose(im)
        # Crop to centered square
        im = ImageOps.fit(im, (target_px, target_px), Image.Resampling.LANCZOS)
        if im.mode != "RGB":
            im = im.convert("RGB")
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=quality, optimize=True, progressive=True)
        return buf.getvalue()


def build_avatar_svg(image_bytes: bytes, size: int = 220) -> str:
    """Build a cyberpunk HUD identity badge around the source photo.

    Layout (concentric, from inside out):
      1. Photo clipped to a circle.
      2. Solid neon ring with a Gaussian-blur glow.
      3. Pulsing inner accent ring (opacity loop).
      4. Counter-rotating dashed mid ring (CW).
      5. Slow rotating outer dashed ring with tick marks (CCW).
      6. Four corner HUD brackets that subtly pulse.
      7. Live status dot in the top-right with a pulse.
      8. Scanline that sweeps vertically across the photo on a loop.
    """
    encoded = base64.b64encode(image_bytes).decode("ascii")
    cx = cy = size / 2

    # Concentric radii, from photo outward.
    # Clamp photo_r so the outermost element (backdrop disc at outer_r + 6)
    # stays inside the square viewBox at any size. Without this the HUD
    # crops on default sizes (220) because outer_r + 6 > size / 2.
    photo_r = min(size * 0.36, (size / 2) - 44)
    inner_r = photo_r + 4        # solid neon border
    pulse_r = photo_r + 10       # pulsing accent
    mid_r = photo_r + 22         # counter-rotating dashed ring
    outer_r = photo_r + 36       # slow outer rotating ring with ticks
    tick_inner = outer_r - 5
    tick_outer = outer_r + 5

    # Tick marks around the outer ring (16 ticks = every 22.5°)
    import math
    ticks = []
    for i in range(16):
        angle = math.radians(i * 22.5)
        x1 = cx + tick_inner * math.cos(angle)
        y1 = cy + tick_inner * math.sin(angle)
        x2 = cx + tick_outer * math.cos(angle)
        y2 = cy + tick_outer * math.sin(angle)
        ticks.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{PALETTE["neon"]}" stroke-opacity="0.45" stroke-width="1"/>'
        )

    # Four HUD corner brackets at outer extent of the badge
    bracket_r = size / 2 - 4
    bracket_len = 14

    def corner(cx_off: int, cy_off: int, dx: int, dy: int) -> str:
        # cx_off / cy_off in {-1, +1}, dx / dy gives the L direction
        bx = cx + cx_off * bracket_r
        by = cy + cy_off * bracket_r
        return (
            f'<path d="M {bx - dx * bracket_len} {by} L {bx} {by} L {bx} {by - dy * bracket_len}" '
            f'fill="none" stroke="{PALETTE["neon"]}" stroke-width="2" stroke-linecap="round" '
            f'stroke-opacity="0.7">'
            f'<animate attributeName="stroke-opacity" values="0.7;1;0.7" dur="2.4s" repeatCount="indefinite"/>'
            f'</path>'
        )

    brackets = "".join([
        corner(-0.7, -0.7,  1,  1),  # top-left
        corner( 0.7, -0.7, -1,  1),  # top-right
        corner(-0.7,  0.7,  1, -1),  # bottom-left
        corner( 0.7,  0.7, -1, -1),  # bottom-right
    ])

    # Status dot offset on the top-right edge of the photo
    dot_cx = cx + photo_r * 0.72
    dot_cy = cy - photo_r * 0.72

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  <defs>
    <clipPath id="avatarClip">
      <circle cx="{cx}" cy="{cy}" r="{photo_r:.1f}"/>
    </clipPath>
    <filter id="avatarGlow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <linearGradient id="avatarScan" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%"  stop-color="{PALETTE['neon']}" stop-opacity="0"/>
      <stop offset="50%" stop-color="{PALETTE['neon']}" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="{PALETTE['neon']}" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <!-- Carbon backdrop disc behind everything -->
  <circle cx="{cx}" cy="{cy}" r="{outer_r + 6:.1f}" fill="{PALETTE['carbon_deep']}"/>

  <!-- Photo clipped to inner circle -->
  <image href="data:image/jpeg;base64,{encoded}"
         x="{cx - photo_r:.1f}" y="{cy - photo_r:.1f}"
         width="{photo_r * 2:.1f}" height="{photo_r * 2:.1f}"
         preserveAspectRatio="xMidYMid slice"
         clip-path="url(#avatarClip)"/>

  <!-- Vertical scanline sweep across the photo -->
  <g clip-path="url(#avatarClip)">
    <rect x="{cx - photo_r:.1f}" y="{cy - photo_r - 40:.1f}"
          width="{photo_r * 2:.1f}" height="40" fill="url(#avatarScan)">
      <animateTransform attributeName="transform" type="translate"
                        from="0 0" to="0 {photo_r * 2 + 40:.1f}"
                        dur="3.6s" repeatCount="indefinite"/>
    </rect>
  </g>

  <!-- Solid neon border around the photo -->
  <circle cx="{cx}" cy="{cy}" r="{inner_r:.1f}" fill="none"
          stroke="{PALETTE['neon']}" stroke-width="2" filter="url(#avatarGlow)"/>

  <!-- Pulsing accent ring -->
  <circle cx="{cx}" cy="{cy}" r="{pulse_r:.1f}" fill="none"
          stroke="{PALETTE['neon']}" stroke-width="1" stroke-opacity="0.5">
    <animate attributeName="stroke-opacity" values="0.5;0.95;0.5" dur="2.6s" repeatCount="indefinite"/>
    <animate attributeName="r" values="{pulse_r:.1f};{pulse_r + 2:.1f};{pulse_r:.1f}" dur="2.6s" repeatCount="indefinite"/>
  </circle>

  <!-- Counter-rotating mid dashed ring (CW) -->
  <g transform-origin="{cx} {cy}">
    <circle cx="{cx}" cy="{cy}" r="{mid_r:.1f}" fill="none"
            stroke="{PALETTE['neon']}" stroke-opacity="0.55" stroke-width="1.2"
            stroke-dasharray="4 6"/>
    <animateTransform attributeName="transform" type="rotate"
                      from="0 {cx} {cy}" to="360 {cx} {cy}"
                      dur="16s" repeatCount="indefinite"/>
  </g>

  <!-- Slow outer dashed ring with tick marks (CCW) -->
  <g transform-origin="{cx} {cy}">
    <circle cx="{cx}" cy="{cy}" r="{outer_r:.1f}" fill="none"
            stroke="{PALETTE['neon']}" stroke-opacity="0.35" stroke-width="1"
            stroke-dasharray="2 8"/>
    {''.join(ticks)}
    <animateTransform attributeName="transform" type="rotate"
                      from="360 {cx} {cy}" to="0 {cx} {cy}"
                      dur="24s" repeatCount="indefinite"/>
  </g>

  <!-- HUD corner brackets -->
  {brackets}

  <!-- Live status indicator -->
  <g>
    <circle cx="{dot_cx:.1f}" cy="{dot_cy:.1f}" r="6" fill="{PALETTE['carbon_deep']}"
            stroke="{PALETTE['neon']}" stroke-width="1"/>
    <circle cx="{dot_cx:.1f}" cy="{dot_cy:.1f}" r="3" fill="{PALETTE['neon']}" filter="url(#avatarGlow)">
      <animate attributeName="opacity" values="1;0.3;1" dur="1.6s" repeatCount="indefinite"/>
    </circle>
  </g>
</svg>"""


def main() -> int:
    if not SOURCE_IMAGE.exists():
        print(f"avatar: source image not found at {SOURCE_IMAGE}", file=sys.stderr)
        return 1
    image_bytes = compress_source(SOURCE_IMAGE, EMBED_PIXELS, JPEG_QUALITY)
    svg = build_avatar_svg(image_bytes, size=220)
    os.makedirs(ASSETS_DIR, exist_ok=True)
    out_path = os.path.join(ASSETS_DIR, "avatar.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    size_kb = os.path.getsize(out_path) // 1024
    print(f"Wrote {out_path} ({size_kb} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

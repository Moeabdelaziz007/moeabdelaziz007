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


def build_avatar_svg(image_bytes: bytes, size: int = 180) -> str:
    encoded = base64.b64encode(image_bytes).decode("ascii")
    center = size / 2
    inner_r = center - 6
    ring_r = center - 2
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  <defs>
    <clipPath id="avatarClip">
      <circle cx="{center}" cy="{center}" r="{inner_r}"/>
    </clipPath>
    <filter id="avatarGlow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Outer carbon background ring -->
  <circle cx="{center}" cy="{center}" r="{ring_r}" fill="{PALETTE['carbon_deep']}"/>

  <!-- Image clipped to circle -->
  <image href="data:image/jpeg;base64,{encoded}"
         x="0" y="0" width="{size}" height="{size}"
         preserveAspectRatio="xMidYMid slice"
         clip-path="url(#avatarClip)"/>

  <!-- Neon ring border -->
  <circle cx="{center}" cy="{center}" r="{inner_r}" fill="none"
          stroke="{PALETTE['neon']}" stroke-width="2" filter="url(#avatarGlow)"/>

  <!-- Outer thin accent -->
  <circle cx="{center}" cy="{center}" r="{ring_r}" fill="none"
          stroke="{PALETTE['neon']}" stroke-opacity="0.25" stroke-width="1"
          stroke-dasharray="2 6"/>
</svg>"""


def main() -> int:
    if not SOURCE_IMAGE.exists():
        print(f"avatar: source image not found at {SOURCE_IMAGE}", file=sys.stderr)
        return 1
    image_bytes = compress_source(SOURCE_IMAGE, EMBED_PIXELS, JPEG_QUALITY)
    svg = build_avatar_svg(image_bytes, size=180)
    os.makedirs(ASSETS_DIR, exist_ok=True)
    out_path = os.path.join(ASSETS_DIR, "avatar.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    size_kb = os.path.getsize(out_path) // 1024
    print(f"Wrote {out_path} ({size_kb} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

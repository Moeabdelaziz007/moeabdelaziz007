"""Generate agents_inventory.svg by classifying owned repos into AI categories.

Output: assets/agents_inventory.svg
"""

from __future__ import annotations

import os
import re
import sys
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import ASSETS_DIR, GITHUB_USER, PALETTE  # noqa: E402
from lib.github_client import GitHubClient  # noqa: E402

CATEGORY_RULES = [
    # name, color, keyword patterns (case-insensitive on name+description+topics)
    ("AIX Ecosystem", PALETTE["neon"],
     [r"\baix\b", r"\biqra\b", r"\baxiom\b", r"\baios\b", r"\baura\b"]),
    ("Agents & MCP", "#7FFF50",
     [r"\bagent", r"\bmcp\b", r"\bskill", r"\bclaude", r"\bcodesmith"]),
    ("Voice & Multimodal", "#39FFC4",
     [r"\bvoice\b", r"\bspeech\b", r"\bgemini\b", r"\bmultimodal\b", r"\bimg\b", r"\bvideo\b"]),
    ("OS & Platforms", "#A4F839",
     [r"\bos\b", r"\bplatform\b", r"\bjarhe\b", r"\bphone\b"]),
    ("Trading & Quant", "#39FF8E",
     [r"\bquant\b", r"\btrading\b", r"\bedge\b", r"\balpha\b"]),
]


def classify(repo: Dict) -> str:
    text = " ".join([
        str(repo.get("name") or ""),
        str(repo.get("description") or ""),
        " ".join(repo.get("topics") or []),
    ]).lower()
    for name, _color, patterns in CATEGORY_RULES:
        for pat in patterns:
            if re.search(pat, text):
                return name
    return "Other"


def select_top_repos(repos: List[Dict], limit: int = 12) -> List[Dict]:
    """Pick repos that look meaningful: have description, sorted by stars then update time."""
    ranked = [r for r in repos if not r.get("archived") and not r.get("fork")]
    ranked.sort(
        key=lambda r: (
            int(r.get("stargazers_count") or 0),
            r.get("pushed_at") or "",
        ),
        reverse=True,
    )
    # Prefer repos with descriptions for nicer cards; but keep stars high too
    with_desc = [r for r in ranked if r.get("description")]
    return (with_desc or ranked)[:limit]


def truncate(text: str, n: int) -> str:
    text = (text or "").replace("\n", " ").strip()
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def render_svg(repos: List[Dict], total_repos: int) -> str:
    cols = 3
    card_w = 220
    card_h = 110
    gap_x = 16
    gap_y = 16
    margin_x = 30
    margin_y = 110
    rows = (len(repos) + cols - 1) // cols
    width = margin_x * 2 + cols * card_w + (cols - 1) * gap_x
    height = margin_y + rows * card_h + (rows - 1) * gap_y + 50

    cards = []
    categories_seen = set()
    for idx, repo in enumerate(repos):
        r = idx // cols
        c = idx % cols
        x = margin_x + c * (card_w + gap_x)
        y = margin_y + r * (card_h + gap_y)
        category = classify(repo)
        categories_seen.add(category)
        accent = next(
            (color for name, color, _ in CATEGORY_RULES if name == category),
            PALETTE["gray_mid"],
        )
        name = truncate(repo.get("name") or "unnamed", 22)
        desc = truncate(repo.get("description") or "", 78)
        stars = int(repo.get("stargazers_count") or 0)
        lang = repo.get("language") or "—"
        # Stagger card appearance: each card fades in 0.08s after the previous.
        stagger = round(idx * 0.08, 2)
        cards.append(
            f'<g transform="translate({x}, {y})" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.5s" '
            f'begin="{stagger}s" fill="freeze"/>'
            f'<rect width="{card_w}" height="{card_h}" rx="8" '
            f'fill="{PALETTE["carbon_mid"]}" stroke="{accent}" stroke-opacity="0.5" stroke-width="1"/>'
            f'<rect width="3" height="{card_h}" rx="2" fill="{accent}">'
            f'<animate attributeName="opacity" values="1;0.45;1" dur="3s" '
            f'begin="{stagger}s" repeatCount="indefinite"/>'
            f'</rect>'
            f'<text x="14" y="22" font-family="\'Consolas\',monospace" font-size="13" '
            f'fill="{PALETTE["white"]}" font-weight="600">{escape(name)}</text>'
            f'<text x="14" y="44" font-family="\'Consolas\',monospace" font-size="10" '
            f'fill="{PALETTE["gray_text"]}">{escape(desc)}</text>'
            f'<text x="14" y="{card_h - 14}" font-family="\'Consolas\',monospace" font-size="9" '
            f'fill="{accent}" letter-spacing="1">{escape(category.upper())}</text>'
            f'<text x="{card_w - 14}" y="{card_h - 14}" font-family="\'Consolas\',monospace" '
            f'font-size="9" fill="{PALETTE["gray_mid"]}" text-anchor="end">'
            f'★ {stars} · {escape(lang)}</text>'
            f'</g>'
        )

    # Legend
    legend_items = []
    legend_x = margin_x
    legend_y = height - 30
    for name, color, _ in CATEGORY_RULES:
        if name not in categories_seen:
            continue
        legend_items.append(
            f'<g transform="translate({legend_x}, {legend_y})">'
            f'<circle cx="6" cy="-3" r="4" fill="{color}"/>'
            f'<text x="16" y="0" font-family="\'Consolas\',monospace" font-size="10" '
            f'fill="{PALETTE["gray_text"]}">{escape(name)}</text>'
            f'</g>'
        )
        legend_x += 10 + 8 * len(name) + 24

    return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <pattern id="cfAgents" width="10" height="10" patternUnits="userSpaceOnUse">
      <rect width="10" height="10" fill="{PALETTE['carbon_deep']}"/>
      <path d="M0,0 L5,5 L10,0 L5,-5 Z M5,5 L10,10 L15,5 L10,0 Z M-5,5 L0,10 L5,5 L0,0 Z M0,10 L5,15 L10,10 L5,5 Z" fill="{PALETTE['carbon_mid']}"/>
    </pattern>
    <linearGradient id="topBarAgents" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{PALETTE['neon']}" stop-opacity="0.1"/>
      <stop offset="50%" stop-color="{PALETTE['neon']}" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="{PALETTE['neon']}" stop-opacity="0.1"/>
    </linearGradient>
    <linearGradient id="scanlineAgents" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{PALETTE['neon']}" stop-opacity="0"/>
      <stop offset="50%" stop-color="{PALETTE['neon']}" stop-opacity="0.12"/>
      <stop offset="100%" stop-color="{PALETTE['neon']}" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="agentsClip">
      <rect x="0" y="0" width="{width}" height="{height}" rx="10"/>
    </clipPath>
  </defs>

  <rect width="{width}" height="{height}" fill="url(#cfAgents)" rx="10"
        stroke="{PALETTE['neon']}" stroke-opacity="0.3" stroke-width="1"/>
  <rect width="{width}" height="{height}" fill="#000000" opacity="0.45" rx="10"/>
  <rect width="{width}" height="3" fill="url(#topBarAgents)" rx="2">
    <animate attributeName="opacity" values="0.6;1;0.6" dur="3.4s" repeatCount="indefinite"/>
  </rect>
  <g clip-path="url(#agentsClip)">
    <rect x="-200" y="0" width="200" height="{height}" fill="url(#scanlineAgents)">
      <animateTransform attributeName="transform" type="translate"
                        from="0 0" to="{width + 200} 0" dur="8s" repeatCount="indefinite"/>
    </rect>
  </g>

  <text x="{margin_x}" y="40" font-family="'Consolas','Fira Code',monospace" font-size="11"
        fill="{PALETTE['gray_label']}" letter-spacing="3">// AGENT INVENTORY</text>
  <text x="{margin_x}" y="68" font-family="'Consolas','Fira Code',monospace" font-size="22"
        fill="{PALETTE['white']}" font-weight="600" letter-spacing="2">AI AGENT FLEET</text>
  <text x="{width - margin_x}" y="40" font-family="'Consolas',monospace" font-size="11"
        fill="{PALETTE['gray_mid']}" text-anchor="end" letter-spacing="1">{total_repos} REPOS · {len(repos)} HIGHLIGHTED</text>
  <line x1="{margin_x}" y1="82" x2="{width - margin_x}" y2="82" stroke="{PALETTE['neon']}" stroke-opacity="0.25" stroke-width="1"/>

  {''.join(cards)}
  {''.join(legend_items)}
</svg>"""


def escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_fallback() -> str:
    return f"""<svg width="720" height="180" viewBox="0 0 720 180" xmlns="http://www.w3.org/2000/svg">
  <rect width="720" height="180" fill="{PALETTE['carbon_deep']}" rx="10"
        stroke="{PALETTE['neon']}" stroke-opacity="0.3"/>
  <text x="360" y="95" font-family="'Consolas',monospace" font-size="14"
        fill="{PALETTE['gray_text']}" text-anchor="middle">AGENT INVENTORY · DATA UNAVAILABLE</text>
  <text x="360" y="120" font-family="'Consolas',monospace" font-size="10"
        fill="{PALETTE['gray_mid']}" text-anchor="middle">Awaiting next scheduled telemetry sync...</text>
</svg>"""


def main() -> int:
    os.makedirs(ASSETS_DIR, exist_ok=True)
    out_path = os.path.join(ASSETS_DIR, "agents_inventory.svg")
    try:
        client = GitHubClient()
        repos = client.list_user_repos(GITHUB_USER)
        highlighted = select_top_repos(repos, limit=12)
        svg = render_svg(highlighted, total_repos=len(repos)) if highlighted else render_fallback()
    except Exception as exc:  # noqa: BLE001
        print(f"agents_inventory: falling back due to {exc}")
        svg = render_fallback()

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

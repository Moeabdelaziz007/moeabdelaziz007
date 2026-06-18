"""Generate agents_inventory.svg by classifying owned repos into AI categories.
Focusing on AxiomID Agent Roles.
"""

from __future__ import annotations

import os
import re
import sys
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import ASSETS_DIR, GITHUB_USER, PALETTE  # noqa: E402
from lib.github_client import GitHubClient  # noqa: E402

# New Category Rules for AxiomID Team
CATEGORY_RULES = [
    ("Root Authority", PALETTE["neon"], [r"\baxiomid\b", r"\broot\b"]),
    ("Autonomous Execution", "#7FFF50", [r"\bjules\b", r"\bopencode\b", r"\bruntime\b"]),
    ("Verification & Quality", "#4285F4", [r"\bgemini\b", r"\bcoderabbit\b", r"\baudit\b"]),
    ("Mission Control", "#39FFC4", [r"\bantigravity\b", r"\bide\b", r"\bterminal\b"]),
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

def select_top_repos(repos: List[Dict], limit: int = 6) -> List[Dict]:
    ranked = [r for r in repos if not r.get("archived") and not r.get("fork")]
    # Prioritize AxiomID related repos
    ranked.sort(
        key=lambda r: (
            "axiomid" in (r.get("name") or "").lower(),
            int(r.get("stargazers_count") or 0),
            r.get("pushed_at") or "",
        ),
        reverse=True,
    )
    return ranked[:limit]

def truncate(text: str, n: int) -> str:
    text = (text or "").replace("\n", " ").strip()
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"

def render_svg(repos: List[Dict], total_repos: int) -> str:
    cols = 2
    card_w = 350
    card_h = 100
    gap_x = 20
    gap_y = 20
    margin_x = 40
    margin_y = 100
    rows = (len(repos) + cols - 1) // cols
    width = margin_x * 2 + cols * card_w + (cols - 1) * gap_x
    height = margin_y + rows * card_h + (rows - 1) * gap_y + 40

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
        name = truncate(repo.get("name") or "unnamed", 30)
        desc = truncate(repo.get("description") or "Sovereign identity primitive.", 60)
        stagger = round(idx * 0.1, 2)
        cards.append(
            f'<g transform="translate({x}, {y})" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.5s" '
            f'begin="{stagger}s" fill="freeze"/>'
            f'<rect width="{card_w}" height="{card_h}" rx="8" '
            f'fill="{PALETTE["carbon_mid"]}" stroke="{accent}" stroke-opacity="0.5" stroke-width="1"/>'
            f'<rect width="4" height="{card_h}" rx="2" fill="{accent}">'
            f'<animate attributeName="opacity" values="1;0.4;1" dur="3s" repeatCount="indefinite"/>'
            f'</rect>'
            f'<text x="20" y="30" font-family="\'Consolas\',monospace" font-size="14" '
            f'fill="{PALETTE["white"]}" font-weight="600">{escape(name)}</text>'
            f'<text x="20" y="55" font-family="\'Consolas\',monospace" font-size="11" '
            f'fill="{PALETTE["gray_text"]}">{escape(desc)}</text>'
            f'<text x="20" y="{card_h - 15}" font-family="\'Consolas\',monospace" font-size="10" '
            f'fill="{accent}" letter-spacing="1">{escape(category.upper())}</text>'
            f'</g>'
        )

    return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <pattern id="cfAgents" width="10" height="10" patternUnits="userSpaceOnUse">
      <rect width="10" height="10" fill="{PALETTE['carbon_deep']}"/>
      <path d="M0,0 L5,5 L10,0 L5,-5 Z M5,5 L10,10 L15,5 L10,0 Z M-5,5 L0,10 L5,5 L0,0 Z M0,10 L5,15 L10,10 L5,5 Z" fill="{PALETTE['carbon_mid']}"/>
    </pattern>
  </defs>

  <rect width="{width}" height="{height}" fill="url(#cfAgents)" rx="12" stroke="{PALETTE['neon']}" stroke-opacity="0.3" stroke-width="1"/>
  <text x="{margin_x}" y="50" font-family="'Consolas',monospace" font-size="12" fill="{PALETTE['gray_label']}" letter-spacing="4">// AXIOMID AGENT FLEET</text>
  <text x="{margin_x}" y="80" font-family="'Consolas',monospace" font-size="24" fill="{PALETTE['white']}" font-weight="600">THE CONSORTIUM</text>

  {''.join(cards)}
</svg>"""

def escape(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def main() -> int:
    os.makedirs(ASSETS_DIR, exist_ok=True)
    out_path = os.path.join(ASSETS_DIR, "agents_inventory.svg")
    try:
        client = GitHubClient()
        repos = client.list_user_repos(GITHUB_USER)
        highlighted = select_top_repos(repos, limit=6)
        svg = render_svg(highlighted, total_repos=len(repos))
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

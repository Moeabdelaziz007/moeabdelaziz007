"""Generate ecosystem_graph.svg, the IQRA <-> AIX-Format <-> aix-agent-skills map.

Output: assets/ecosystem_graph.svg

Pulls live stars / language / description from GitHub so the graph stays
fresh, but the topology is intentionally hand-curated rather than inferred.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from typing import Dict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import ASSETS_DIR, GITHUB_USER, PALETTE  # noqa: E402

NODES = [
    {
        "id": "iqra",
        "label": "IQRA",
        "role": "OPERATING SYSTEM",
        "repo": f"{GITHUB_USER}/iqra",
        "x": 425,
        "y": 110,
        "r": 70,
        "accent": PALETTE["neon"],
    },
    {
        "id": "aix-format",
        "label": "AIX-FORMAT",
        "role": "TRUST PROTOCOL",
        "repo": f"{GITHUB_USER}/aix-format",
        "x": 200,
        "y": 290,
        "r": 70,
        "accent": "#7FFF50",
    },
    {
        "id": "aix-agent-skills",
        "label": "AGENT-SKILLS",
        "role": "MARKETPLACE",
        "repo": f"{GITHUB_USER}/aix-agent-skills",
        "x": 650,
        "y": 290,
        "r": 70,
        "accent": "#39FFC4",
    },
]

EDGES = [
    {"from": "iqra", "to": "aix-format", "label": "implements"},
    {"from": "aix-agent-skills", "to": "aix-format", "label": "publishes via"},
    {"from": "iqra", "to": "aix-agent-skills", "label": "consumes"},
]


def fetch_repo_meta(full_name: str, token: str | None) -> Dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "moeabdelaziz007-profile-bot",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        req = urllib.request.Request(f"https://api.github.com/repos/{full_name}", headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError):
        return {}


def node_by_id(nid: str) -> Dict:
    return next(n for n in NODES if n["id"] == nid)


def edge_path(src: Dict, dst: Dict) -> str:
    # Quadratic Bezier with control point pulled toward the canvas center
    mx = (src["x"] + dst["x"]) / 2
    my = (src["y"] + dst["y"]) / 2 - 40
    return f"M {src['x']} {src['y']} Q {mx} {my} {dst['x']} {dst['y']}"


def render_svg(meta_by_id: Dict[str, Dict]) -> str:
    width, height = 850, 440
    edges_svg = []
    edge_labels = []
    for edge in EDGES:
        a = node_by_id(edge["from"])
        b = node_by_id(edge["to"])
        path = edge_path(a, b)
        edges_svg.append(
            f'<path d="{path}" fill="none" stroke="{PALETTE["neon"]}" stroke-opacity="0.55" '
            f'stroke-width="1.5" stroke-dasharray="6 6">'
            f'<animate attributeName="stroke-dashoffset" from="0" to="-24" dur="2.5s" '
            f'repeatCount="indefinite"/></path>'
        )
        mx = (a["x"] + b["x"]) / 2
        my = (a["y"] + b["y"]) / 2 - 22
        edge_labels.append(
            f'<text x="{mx}" y="{my}" font-family="\'Consolas\',monospace" font-size="10" '
            f'fill="{PALETTE["gray_label"]}" text-anchor="middle" letter-spacing="2">'
            f'// {edge["label"].upper()}</text>'
        )

    nodes_svg = []
    for node in NODES:
        meta = meta_by_id.get(node["id"], {})
        stars = int(meta.get("stargazers_count") or 0)
        language = (meta.get("language") or "—").upper()
        description = (meta.get("description") or "").strip()
        if len(description) > 60:
            description = description[:59].rstrip() + "…"
        nodes_svg.append(f"""
  <g transform="translate({node['x']}, {node['y']})">
    <circle r="{node['r'] + 8}" fill="none" stroke="{node['accent']}" stroke-opacity="0.25" stroke-width="1"/>
    <circle r="{node['r']}" fill="{PALETTE['carbon_mid']}" stroke="{node['accent']}" stroke-width="1.5"/>
    <circle r="{node['r'] - 8}" fill="{PALETTE['carbon_deep']}" stroke="{node['accent']}" stroke-opacity="0.3"/>
    <text y="-8" font-family="'Consolas','Fira Code',monospace" font-size="16" fill="{PALETTE['white']}"
          text-anchor="middle" font-weight="600" letter-spacing="2">{node['label']}</text>
    <text y="12" font-family="'Consolas',monospace" font-size="9" fill="{node['accent']}"
          text-anchor="middle" letter-spacing="2">{node['role']}</text>
    <text y="30" font-family="'Consolas',monospace" font-size="9" fill="{PALETTE['gray_mid']}"
          text-anchor="middle">★ {stars} · {language}</text>
  </g>
  <text x="{node['x']}" y="{node['y'] + node['r'] + 24}" font-family="'Consolas',monospace"
        font-size="10" fill="{PALETTE['gray_text']}" text-anchor="middle">{escape(description)}</text>
""")

    return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <pattern id="cfEco" width="10" height="10" patternUnits="userSpaceOnUse">
      <rect width="10" height="10" fill="{PALETTE['carbon_deep']}"/>
      <path d="M0,0 L5,5 L10,0 L5,-5 Z M5,5 L10,10 L15,5 L10,0 Z M-5,5 L0,10 L5,5 L0,0 Z M0,10 L5,15 L10,10 L5,5 Z" fill="{PALETTE['carbon_mid']}"/>
    </pattern>
    <linearGradient id="topBarEco" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{PALETTE['neon']}" stop-opacity="0.1"/>
      <stop offset="50%" stop-color="{PALETTE['neon']}" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="{PALETTE['neon']}" stop-opacity="0.1"/>
    </linearGradient>
    <filter id="ecoGlow">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <rect width="{width}" height="{height}" fill="url(#cfEco)" rx="10"
        stroke="{PALETTE['neon']}" stroke-opacity="0.3" stroke-width="1"/>
  <rect width="{width}" height="{height}" fill="#000000" opacity="0.45" rx="10"/>
  <rect width="{width}" height="3" fill="url(#topBarEco)" rx="2"/>

  <text x="30" y="40" font-family="'Consolas','Fira Code',monospace" font-size="11"
        fill="{PALETTE['gray_label']}" letter-spacing="3">// ECOSYSTEM TOPOLOGY</text>
  <text x="30" y="68" font-family="'Consolas','Fira Code',monospace" font-size="22"
        fill="{PALETTE['white']}" font-weight="600" letter-spacing="2">THE SOVEREIGN AI STACK</text>
  <text x="{width - 30}" y="40" font-family="'Consolas',monospace" font-size="11"
        fill="{PALETTE['gray_mid']}" text-anchor="end" letter-spacing="1">3 NODES · 3 EDGES</text>
  <line x1="30" y1="82" x2="{width - 30}" y2="82" stroke="{PALETTE['neon']}" stroke-opacity="0.25" stroke-width="1"/>

  {''.join(edges_svg)}
  {''.join(edge_labels)}
  <g filter="url(#ecoGlow)">{''.join(nodes_svg)}</g>
</svg>"""


def escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def main() -> int:
    os.makedirs(ASSETS_DIR, exist_ok=True)
    out_path = os.path.join(ASSETS_DIR, "ecosystem_graph.svg")
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    meta_by_id = {n["id"]: fetch_repo_meta(n["repo"], token) for n in NODES}
    svg = render_svg(meta_by_id)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

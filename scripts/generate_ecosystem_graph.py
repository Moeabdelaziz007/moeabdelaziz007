"""Generate ecosystem_graph.svg, the Sovereign AI Stack topology.

Renders a radial graph with IQRA (the operating system) at the center and the
five surrounding projects that compose the rest of the stack: AIX-FORMAT
(trust protocol), AIX-AGENT-SKILLS (marketplace), AxiomID (human-authorization
identity), PiWorker (local-first digital twin), and AlphaAxiom (autonomous
quant engine).

Output: assets/ecosystem_graph.svg

Pulls live stars / language / description from GitHub so the graph stays
fresh, but the topology is intentionally hand-curated rather than inferred.
"""


import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import ASSETS_DIR, GITHUB_USER, PALETTE  # noqa: E402

CANVAS_W = 900
CANVAS_H = 560
CENTER_X = 450
CENTER_Y = 290

# IQRA sits at the center; the other five projects form a pentagon around it.
NODES = [
    {
        "id": "iqra",
        "label": "IQRA",
        "role": "OPERATING SYSTEM",
        "repo": f"{GITHUB_USER}/iqra",
        "x": CENTER_X,
        "y": CENTER_Y,
        "r": 72,
        "accent": PALETTE["neon"],
        "is_core": True,
    },
    {
        "id": "aix-format",
        "label": "AIX-FORMAT",
        "role": "TRUST PROTOCOL",
        "repo": f"{GITHUB_USER}/aix-format",
        "x": 450,
        "y": 90,
        "r": 58,
        "accent": "#7FFF50",
        "is_core": False,
    },
    {
        "id": "aix-agent-skills",
        "label": "AGENT-SKILLS",
        "role": "MARKETPLACE",
        "repo": f"{GITHUB_USER}/aix-agent-skills",
        "x": 760,
        "y": 220,
        "r": 58,
        "accent": "#39FFC4",
        "is_core": False,
    },
    {
        "id": "alpha-axiom",
        "label": "ALPHA-AXIOM",
        "role": "QUANT ENGINE",
        "repo": f"{GITHUB_USER}/AlphaAxiom",
        "x": 660,
        "y": 470,
        "r": 58,
        "accent": "#39C9FF",
        "is_core": False,
    },
    {
        "id": "piworker",
        "label": "PIWORKER",
        "role": "DIGITAL TWIN",
        "repo": f"{GITHUB_USER}/PiWorker",
        "x": 240,
        "y": 470,
        "r": 58,
        "accent": "#C49DFF",
        "is_core": False,
    },
    {
        "id": "axiomid",
        "label": "AXIOMID",
        "role": "HUMAN AUTH",
        "repo": f"{GITHUB_USER}/axiomid-project",
        "x": 140,
        "y": 220,
        "r": 58,
        "accent": "#FFB347",
        "is_core": False,
    },
]

# Directional edges: arrow goes from "from" to "to".
EDGES = [
    {"from": "iqra", "to": "aix-format", "label": "implements"},
    {"from": "iqra", "to": "aix-agent-skills", "label": "consumes"},
    {"from": "iqra", "to": "alpha-axiom", "label": "powers"},
    {"from": "iqra", "to": "piworker", "label": "deploys to"},
    {"from": "axiomid", "to": "iqra", "label": "authorizes"},
    {"from": "aix-agent-skills", "to": "aix-format", "label": "publishes via"},
]


def fetch_repo_meta(full_name: str, token: str | None) -> dict:
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


def node_by_id(nid: str) -> dict:
    return next(n for n in NODES if n["id"] == nid)


def trim_to_circle(src: dict, dst: dict) -> tuple[float, float, float, float]:
    """Return (x1, y1, x2, y2) trimmed to each node's circle boundary."""
    dx = dst["x"] - src["x"]
    dy = dst["y"] - src["y"]
    dist = (dx * dx + dy * dy) ** 0.5
    if dist == 0:
        return src["x"], src["y"], dst["x"], dst["y"]
    ux, uy = dx / dist, dy / dist
    x1 = src["x"] + ux * src["r"]
    y1 = src["y"] + uy * src["r"]
    x2 = dst["x"] - ux * dst["r"]
    y2 = dst["y"] - uy * dst["r"]
    return x1, y1, x2, y2


def render_svg(meta_by_id: dict[str, dict]) -> str:
    edges_svg: list[str] = []
    edge_labels: list[str] = []
    for edge in EDGES:
        a = node_by_id(edge["from"])
        b = node_by_id(edge["to"])
        x1, y1, x2, y2 = trim_to_circle(a, b)
        edges_svg.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{PALETTE["neon"]}" stroke-opacity="0.5" stroke-width="1.4" '
            f'stroke-dasharray="6 6">'
            f'<animate attributeName="stroke-dashoffset" from="0" to="-24" dur="2.5s" '
            f'repeatCount="indefinite"/></line>'
        )
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2 - 6
        edge_labels.append(
            f'<text x="{mx:.1f}" y="{my:.1f}" font-family="\'Consolas\',monospace" font-size="9" '
            f'fill="{PALETTE["gray_label"]}" text-anchor="middle" letter-spacing="2">'
            f'// {edge["label"].upper()}</text>'
        )

    nodes_svg: list[str] = []
    descriptions: list[str] = []
    for node in NODES:
        meta = meta_by_id.get(node["id"], {})
        stars = int(meta.get("stargazers_count") or 0)
        language = (meta.get("language") or "—").upper()
        description = (meta.get("description") or "").strip()
        if len(description) > 56:
            description = description[:55].rstrip() + "…"

        label_font = 16 if node["is_core"] else 13
        role_font = 9
        meta_font = 9
        nodes_svg.append(f"""
  <g transform="translate({node['x']}, {node['y']})">
    <circle r="{node['r'] + 8}" fill="none" stroke="{node['accent']}" stroke-opacity="0.25" stroke-width="1"/>
    <circle r="{node['r']}" fill="{PALETTE['carbon_mid']}" stroke="{node['accent']}" stroke-width="1.5"/>
    <circle r="{node['r'] - 8}" fill="{PALETTE['carbon_deep']}" stroke="{node['accent']}" stroke-opacity="0.3"/>
    <text y="-6" font-family="'Consolas','Fira Code',monospace" font-size="{label_font}" fill="{PALETTE['white']}"
          text-anchor="middle" font-weight="600" letter-spacing="2">{node['label']}</text>
    <text y="12" font-family="'Consolas',monospace" font-size="{role_font}" fill="{node['accent']}"
          text-anchor="middle" letter-spacing="2">{node['role']}</text>
    <text y="28" font-family="'Consolas',monospace" font-size="{meta_font}" fill="{PALETTE['gray_mid']}"
          text-anchor="middle">★ {stars} · {language}</text>
  </g>""")

        if description and not node["is_core"]:
            # Place the description just outside the node, anchored on the side
            # that pushes text toward the canvas edge instead of toward the core.
            offset = node["r"] + 22
            if node["x"] < CENTER_X - 40:
                tx, anchor = node["x"] - offset, "end"
            elif node["x"] > CENTER_X + 40:
                tx, anchor = node["x"] + offset, "start"
            else:
                tx, anchor = node["x"], "middle"
            if node["y"] < CENTER_Y:
                ty = node["y"] - node["r"] - 14
            else:
                ty = node["y"] + node["r"] + 24
            descriptions.append(
                f'<text x="{tx}" y="{ty}" font-family="\'Consolas\',monospace" '
                f'font-size="10" fill="{PALETTE["gray_text"]}" text-anchor="{anchor}">'
                f'{escape(description)}</text>'
            )

    return f"""<svg width="{CANVAS_W}" height="{CANVAS_H}" viewBox="0 0 {CANVAS_W} {CANVAS_H}" xmlns="http://www.w3.org/2000/svg">
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

  <rect width="{CANVAS_W}" height="{CANVAS_H}" fill="url(#cfEco)" rx="10"
        stroke="{PALETTE['neon']}" stroke-opacity="0.3" stroke-width="1"/>
  <rect width="{CANVAS_W}" height="{CANVAS_H}" fill="#000000" opacity="0.45" rx="10"/>
  <rect width="{CANVAS_W}" height="3" fill="url(#topBarEco)" rx="2"/>

  <text x="30" y="40" font-family="'Consolas','Fira Code',monospace" font-size="11"
        fill="{PALETTE['gray_label']}" letter-spacing="3">// ECOSYSTEM TOPOLOGY</text>
  <text x="30" y="68" font-family="'Consolas','Fira Code',monospace" font-size="22"
        fill="{PALETTE['white']}" font-weight="600" letter-spacing="2">THE SOVEREIGN AI STACK</text>
  <text x="{CANVAS_W - 30}" y="40" font-family="'Consolas',monospace" font-size="11"
        fill="{PALETTE['gray_mid']}" text-anchor="end" letter-spacing="1">{len(NODES)} NODES · {len(EDGES)} EDGES</text>
  <line x1="30" y1="82" x2="{CANVAS_W - 30}" y2="82" stroke="{PALETTE['neon']}" stroke-opacity="0.25" stroke-width="1"/>

  {''.join(edges_svg)}
  {''.join(edge_labels)}
  <g filter="url(#ecoGlow)">{''.join(nodes_svg)}</g>
  {''.join(descriptions)}
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

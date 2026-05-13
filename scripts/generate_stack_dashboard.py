"""Generate stack_dashboard.svg by aggregating languages across all owned repos.

Output: assets/stack_dashboard.svg

Reads from GitHub REST API. Requires GITHUB_TOKEN for higher rate limits.
Falls back to a static placeholder render if the API is unavailable.
"""

from __future__ import annotations

import os
import sys
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import ASSETS_DIR, GITHUB_USER, PALETTE  # noqa: E402
from lib.github_client import GitHubClient  # noqa: E402

LANGUAGE_COLORS = {
    "Python":      "#3572A5",
    "TypeScript":  "#3178C6",
    "JavaScript":  "#F1E05A",
    "Go":          "#00ADD8",
    "Rust":        "#DEA584",
    "Solidity":    "#AA6746",
    "C++":         "#F34B7D",
    "C":           "#555555",
    "HTML":        "#E34C26",
    "CSS":         "#563D7C",
    "Shell":       "#89E051",
    "Java":        "#B07219",
    "Ruby":        "#701516",
    "Swift":       "#F05138",
    "Kotlin":      "#A97BFF",
    "PHP":         "#4F5D95",
    "Dart":        "#00B4AB",
    "Jupyter Notebook": "#DA5B0B",
}
DEFAULT_LANG_COLOR = "#888888"


def aggregate_languages(client: GitHubClient, username: str) -> Tuple[Dict[str, int], int]:
    repos = client.list_user_repos(username)
    totals: Dict[str, int] = {}
    for repo in repos:
        if repo.get("archived") or repo.get("private"):
            continue
        owner = repo.get("owner", {}).get("login") or username
        name = repo.get("name")
        if not name:
            continue
        languages = client.get_repo_languages(owner, name)
        for lang, bytes_count in languages.items():
            totals[lang] = totals.get(lang, 0) + int(bytes_count)
    return totals, len(repos)


def top_languages(totals: Dict[str, int], n: int = 10) -> List[Tuple[str, int, float]]:
    grand = sum(totals.values()) or 1
    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:n]
    return [(lang, count, count / grand * 100.0) for lang, count in ranked]


def render_svg(rows: List[Tuple[str, int, float]], repo_count: int) -> str:
    bar_max = 360
    line_h = 32
    height = 100 + line_h * max(len(rows), 1) + 30
    bars = []
    for idx, (lang, _bytes, pct) in enumerate(rows):
        y = 100 + idx * line_h
        color = LANGUAGE_COLORS.get(lang, DEFAULT_LANG_COLOR)
        width = max(4, int(bar_max * (pct / 100.0)))
        bars.append(
            f'<g transform="translate(40, {y})">'
            f'<text x="0" y="14" font-family="\'Consolas\',monospace" font-size="12" '
            f'fill="{PALETTE["gray_text"]}" letter-spacing="1">{lang}</text>'
            f'<rect x="170" y="2" width="{bar_max}" height="16" rx="3" '
            f'fill="{PALETTE["carbon_high"]}"/>'
            f'<rect x="170" y="2" width="{width}" height="16" rx="3" fill="{color}"/>'
            f'<rect x="170" y="2" width="{width}" height="16" rx="3" '
            f'fill="{PALETTE["neon"]}" opacity="0.18"/>'
            f'<text x="{170 + bar_max + 12}" y="14" font-family="\'JetBrains Mono\',monospace" '
            f'font-size="12" fill="{PALETTE["white"]}">{pct:.1f}%</text>'
            f'</g>'
        )

    return f"""<svg width="720" height="{height}" viewBox="0 0 720 {height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <pattern id="cfStack" width="10" height="10" patternUnits="userSpaceOnUse">
      <rect width="10" height="10" fill="{PALETTE['carbon_deep']}"/>
      <path d="M0,0 L5,5 L10,0 L5,-5 Z M5,5 L10,10 L15,5 L10,0 Z M-5,5 L0,10 L5,5 L0,0 Z M0,10 L5,15 L10,10 L5,5 Z" fill="{PALETTE['carbon_mid']}"/>
    </pattern>
    <linearGradient id="topBarStack" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{PALETTE['neon']}" stop-opacity="0.1"/>
      <stop offset="50%" stop-color="{PALETTE['neon']}" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="{PALETTE['neon']}" stop-opacity="0.1"/>
    </linearGradient>
  </defs>

  <rect width="720" height="{height}" fill="url(#cfStack)" rx="10" stroke="{PALETTE['neon']}" stroke-opacity="0.3" stroke-width="1"/>
  <rect width="720" height="{height}" fill="#000000" opacity="0.45" rx="10"/>
  <rect width="720" height="3" fill="url(#topBarStack)" rx="2"/>

  <text x="40" y="40" font-family="'Consolas','Fira Code',monospace" font-size="11"
        fill="{PALETTE['gray_label']}" letter-spacing="3">// STACK ANALYSIS</text>
  <text x="40" y="68" font-family="'Consolas','Fira Code',monospace" font-size="22"
        fill="{PALETTE['white']}" font-weight="600" letter-spacing="2">CORE LANGUAGES</text>
  <text x="680" y="40" font-family="'Consolas',monospace" font-size="11"
        fill="{PALETTE['gray_mid']}" text-anchor="end" letter-spacing="1">{repo_count} REPOSITORIES SCANNED</text>
  <line x1="40" y1="82" x2="680" y2="82" stroke="{PALETTE['neon']}" stroke-opacity="0.25" stroke-width="1"/>

  {''.join(bars)}

  <text x="40" y="{height - 14}" font-family="'Consolas',monospace" font-size="9"
        fill="{PALETTE['gray_low']}" letter-spacing="2">// SOURCE: GITHUB REST API · LANGUAGES ENDPOINT</text>
  <circle cx="680" cy="{height - 18}" r="3" fill="{PALETTE['neon']}">
    <animate attributeName="opacity" values="1;0.2;1" dur="2s" repeatCount="indefinite"/>
  </circle>
</svg>"""


def render_fallback() -> str:
    return f"""<svg width="720" height="180" viewBox="0 0 720 180" xmlns="http://www.w3.org/2000/svg">
  <rect width="720" height="180" fill="{PALETTE['carbon_deep']}" rx="10"
        stroke="{PALETTE['neon']}" stroke-opacity="0.3"/>
  <text x="360" y="95" font-family="'Consolas',monospace" font-size="14"
        fill="{PALETTE['gray_text']}" text-anchor="middle">STACK ANALYSIS · DATA UNAVAILABLE</text>
  <text x="360" y="120" font-family="'Consolas',monospace" font-size="10"
        fill="{PALETTE['gray_mid']}" text-anchor="middle">Awaiting next scheduled telemetry sync...</text>
</svg>"""


def main() -> int:
    os.makedirs(ASSETS_DIR, exist_ok=True)
    out_path = os.path.join(ASSETS_DIR, "stack_dashboard.svg")
    try:
        client = GitHubClient()
        totals, repo_count = aggregate_languages(client, GITHUB_USER)
        rows = top_languages(totals, n=10)
        svg = render_svg(rows, repo_count) if rows else render_fallback()
    except Exception as exc:  # noqa: BLE001
        print(f"stack_dashboard: falling back due to {exc}")
        svg = render_fallback()

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

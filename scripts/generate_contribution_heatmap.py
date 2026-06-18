"""Generate contribution_heatmap.svg from the GitHub GraphQL contribution calendar.

Output: assets/contribution_heatmap.svg
"""

from __future__ import annotations

import os
import sys
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import ASSETS_DIR, GITHUB_USER, PALETTE  # noqa: E402
from lib.github_client import GitHubClient  # noqa: E402


def neon_shade(count: int, max_count: int) -> str:
    """Map a count to one of 5 neon-tinted shades on a carbon background."""
    if count <= 0:
        return "#0a0a0a"
    # Bucketed scale relative to the brightest day in the year
    ratio = min(count / max(max_count, 1), 1.0)
    if ratio < 0.20:
        return "#0d3320"
    if ratio < 0.40:
        return "#155b30"
    if ratio < 0.60:
        return "#218a3f"
    if ratio < 0.80:
        return "#2bbf4d"
    return "#39FF14"


def longest_streak(days: List[Dict]) -> int:
    best = current = 0
    for d in days:
        if int(d.get("contributionCount", 0)) > 0:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def current_streak(days: List[Dict]) -> int:
    import datetime
    today_str = datetime.date.today().isoformat()
    # Filter out future dates
    filtered = [d for d in days if d.get("date", "") <= today_str]
    streak = 0
    for d in reversed(filtered):
        if int(d.get("contributionCount", 0)) > 0:
            streak += 1
        else:
            break
    return streak


def flatten_days(weeks: List[Dict]) -> List[Dict]:
    out: List[Dict] = []
    for w in weeks:
        for d in w.get("contributionDays", []):
            out.append(d)
    return out


def render_svg(contributions: Dict) -> str:
    calendar = contributions.get("contributionCalendar", {})
    weeks = calendar.get("weeks", [])
    total = int(calendar.get("totalContributions", 0))
    total_commits = int(contributions.get("totalCommitContributions", 0))
    total_prs = int(contributions.get("totalPullRequestContributions", 0))
    total_issues = int(contributions.get("totalIssueContributions", 0))

    all_days = flatten_days(weeks)
    if not all_days:
        return render_fallback()

    max_count = max((int(d.get("contributionCount", 0)) for d in all_days), default=0)
    cur_streak = current_streak(all_days)
    best_streak = longest_streak(all_days)

    cell = 11
    gap = 3
    grid_left = 60
    grid_top = 130

    weeks_count = len(weeks)
    width = grid_left + weeks_count * (cell + gap) + 40
    height = grid_top + 7 * (cell + gap) + 60

    cells = []
    for wi, week in enumerate(weeks):
        for d in week.get("contributionDays", []):
            wd = int(d.get("weekday", 0))
            count = int(d.get("contributionCount", 0))
            x = grid_left + wi * (cell + gap)
            y = grid_top + wd * (cell + gap)
            color = neon_shade(count, max_count)
            opacity = "1" if count > 0 else "0.6"
            cells.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" '
                f'fill="{color}" opacity="{opacity}">'
                f'<title>{d.get("date","")}: {count} contributions</title>'
                f'</rect>'
            )

    # Weekday labels (Mon / Wed / Fri)
    weekday_labels = {1: "Mon", 3: "Wed", 5: "Fri"}
    labels = []
    for wd, name in weekday_labels.items():
        y = grid_top + wd * (cell + gap) + cell - 1
        labels.append(
            f'<text x="{grid_left - 8}" y="{y}" font-family="\'Consolas\',monospace" '
            f'font-size="9" fill="{PALETTE["gray_mid"]}" text-anchor="end">{name}</text>'
        )

    return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <pattern id="cfHeat" width="10" height="10" patternUnits="userSpaceOnUse">
      <rect width="10" height="10" fill="{PALETTE['carbon_deep']}"/>
      <path d="M0,0 L5,5 L10,0 L5,-5 Z M5,5 L10,10 L15,5 L10,0 Z M-5,5 L0,10 L5,5 L0,0 Z M0,10 L5,15 L10,10 L5,5 Z" fill="{PALETTE['carbon_mid']}"/>
    </pattern>
    <linearGradient id="topBarHeat" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{PALETTE['neon']}" stop-opacity="0.1"/>
      <stop offset="50%" stop-color="{PALETTE['neon']}" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="{PALETTE['neon']}" stop-opacity="0.1"/>
    </linearGradient>
  </defs>

  <rect width="{width}" height="{height}" fill="url(#cfHeat)" rx="10"
        stroke="{PALETTE['neon']}" stroke-opacity="0.3" stroke-width="1"/>
  <rect width="{width}" height="{height}" fill="#000000" opacity="0.45" rx="10"/>
  <rect width="{width}" height="3" fill="url(#topBarHeat)" rx="2"/>

  <text x="40" y="40" font-family="'Consolas','Fira Code',monospace" font-size="11"
        fill="{PALETTE['gray_label']}" letter-spacing="3">// CONTRIBUTION FLOW</text>
  <text x="40" y="68" font-family="'Consolas','Fira Code',monospace" font-size="22"
        fill="{PALETTE['white']}" font-weight="600" letter-spacing="2">{total:,} CONTRIBUTIONS · LAST YEAR</text>

  <!-- Mini stat cards -->
  <g font-family="'Consolas','Fira Code',monospace">
    <g transform="translate(40, 85)">
      <text font-size="9" fill="{PALETTE['gray_label']}" letter-spacing="2">COMMITS</text>
      <text y="18" font-size="16" fill="{PALETTE['neon']}" font-weight="600">{total_commits:,}</text>
    </g>
    <g transform="translate(180, 85)">
      <text font-size="9" fill="{PALETTE['gray_label']}" letter-spacing="2">PRS OPENED</text>
      <text y="18" font-size="16" fill="{PALETTE['neon']}" font-weight="600">{total_prs:,}</text>
    </g>
    <g transform="translate(320, 85)">
      <text font-size="9" fill="{PALETTE['gray_label']}" letter-spacing="2">ISSUES</text>
      <text y="18" font-size="16" fill="{PALETTE['neon']}" font-weight="600">{total_issues:,}</text>
    </g>
    <g transform="translate(440, 85)">
      <text font-size="9" fill="{PALETTE['gray_label']}" letter-spacing="2">CURRENT STREAK</text>
      <text y="18" font-size="16" fill="{PALETTE['white']}" font-weight="600">{cur_streak}d</text>
    </g>
    <g transform="translate(600, 85)">
      <text font-size="9" fill="{PALETTE['gray_label']}" letter-spacing="2">LONGEST STREAK</text>
      <text y="18" font-size="16" fill="{PALETTE['white']}" font-weight="600">{best_streak}d</text>
    </g>
  </g>

  {''.join(labels)}
  {''.join(cells)}

  <!-- Legend -->
  <g transform="translate({grid_left}, {height - 22})" font-family="'Consolas',monospace" font-size="9" fill="{PALETTE['gray_mid']}">
    <text x="0" y="9">Less</text>
    <rect x="34" y="0" width="10" height="10" rx="2" fill="#0d3320"/>
    <rect x="48" y="0" width="10" height="10" rx="2" fill="#155b30"/>
    <rect x="62" y="0" width="10" height="10" rx="2" fill="#218a3f"/>
    <rect x="76" y="0" width="10" height="10" rx="2" fill="#2bbf4d"/>
    <rect x="90" y="0" width="10" height="10" rx="2" fill="#39FF14"/>
    <text x="108" y="9">More</text>
  </g>
</svg>"""


def render_fallback() -> str:
    return f"""<svg width="720" height="180" viewBox="0 0 720 180" xmlns="http://www.w3.org/2000/svg">
  <rect width="720" height="180" fill="{PALETTE['carbon_deep']}" rx="10"
        stroke="{PALETTE['neon']}" stroke-opacity="0.3"/>
  <text x="360" y="95" font-family="'Consolas',monospace" font-size="14"
        fill="{PALETTE['gray_text']}" text-anchor="middle">CONTRIBUTION HEATMAP · DATA UNAVAILABLE</text>
  <text x="360" y="120" font-family="'Consolas',monospace" font-size="10"
        fill="{PALETTE['gray_mid']}" text-anchor="middle">Requires GITHUB_TOKEN with read:user scope. Awaiting next sync...</text>
</svg>"""


def main() -> int:
    os.makedirs(ASSETS_DIR, exist_ok=True)
    out_path = os.path.join(ASSETS_DIR, "contribution_heatmap.svg")
    try:
        client = GitHubClient()
        contributions = client.contribution_calendar(GITHUB_USER)
        svg = render_svg(contributions) if contributions else render_fallback()
    except Exception as exc:  # noqa: BLE001
        print(f"contribution_heatmap: falling back due to {exc}")
        svg = render_fallback()

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

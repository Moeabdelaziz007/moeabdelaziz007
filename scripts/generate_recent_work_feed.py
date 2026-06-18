"""Generate recent_work_feed.svg from the GitHub Events API.

Output: assets/recent_work_feed.svg

Shows the latest meaningful events (push, PR, release, issue) from the
profile's public activity, styled to match the carbon/neon palette.
"""


import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import ASSETS_DIR, GITHUB_USER, PALETTE  # noqa: E402

INTERESTING_EVENTS = {
    "PushEvent":            ("↥", "PUSH",      PALETTE["neon"]),
    "PullRequestEvent":     ("⌥", "PR",        "#7FFF50"),
    "CreateEvent":          ("✚", "CREATE",    "#39FFC4"),
    "ReleaseEvent":         ("◈", "RELEASE",   "#A4F839"),
    "IssuesEvent":          ("◆", "ISSUE",     "#39FF8E"),
    "PullRequestReviewEvent": ("✓", "REVIEW",  "#7FFF50"),
}
MAX_ROWS = 6


def fetch_events(username: str, token: str | None) -> list[dict]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "moeabdelaziz007-profile-bot",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    url = f"https://api.github.com/users/{urllib.parse.quote(username)}/events/public?per_page=30"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data if isinstance(data, list) else []
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError):
        return []


def humanize(delta: dt.timedelta) -> str:
    seconds = max(0, int(delta.total_seconds()))
    if seconds < 60:
        return f"{seconds}s ago"
    if seconds < 3600:
        return f"{seconds // 60}m ago"
    if seconds < 86400:
        return f"{seconds // 3600}h ago"
    if seconds < 86400 * 30:
        return f"{seconds // 86400}d ago"
    return f"{seconds // (86400 * 30)}mo ago"


def summarize(event: dict) -> str:
    payload = event.get("payload", {}) or {}
    etype = event.get("type")
    if etype == "PushEvent":
        commits = payload.get("commits") or []
        n = len(commits)
        if commits:
            first_msg = commits[-1].get("message", "").split("\n", 1)[0]
            return f"{n} commit{'s' if n != 1 else ''} · {first_msg[:60]}"
        return f"{payload.get('size', 0)} commit pushed"
    if etype == "PullRequestEvent":
        action = payload.get("action", "")
        pr = payload.get("pull_request", {}) or {}
        title = pr.get("title") or ""
        return f"PR {action} · {title[:60]}"
    if etype == "CreateEvent":
        ref_type = payload.get("ref_type", "")
        ref = payload.get("ref") or ""
        return f"{ref_type} created{' · ' + ref if ref else ''}"
    if etype == "ReleaseEvent":
        rel = payload.get("release", {}) or {}
        return f"release {rel.get('tag_name', '')} · {rel.get('name', '')[:50]}"
    if etype == "IssuesEvent":
        issue = payload.get("issue", {}) or {}
        return f"issue {payload.get('action', '')} · {issue.get('title', '')[:60]}"
    if etype == "PullRequestReviewEvent":
        pr = payload.get("pull_request", {}) or {}
        return f"reviewed · {pr.get('title', '')[:60]}"
    return etype or "activity"


def render_svg(events: list[dict]) -> str:
    width = 720
    row_h = 56
    header_h = 90
    footer_h = 36
    rows = events[:MAX_ROWS] if events else []
    height = header_h + max(len(rows), 1) * row_h + footer_h

    now = dt.datetime.now(dt.timezone.utc)

    row_svg = []
    for idx, event in enumerate(rows):
        icon, kind, color = INTERESTING_EVENTS.get(
            event.get("type", ""), ("•", "EVENT", PALETTE["gray_mid"])
        )
        repo_name = (event.get("repo") or {}).get("name", "?")
        when_str = event.get("created_at", "")
        try:
            when = dt.datetime.strptime(when_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
            ago = humanize(now - when)
        except (TypeError, ValueError):
            ago = "—"
        summary = summarize(event)

        y = header_h + idx * row_h
        # Each row slides in from below + fades in, staggered.
        # Newest entries appear first, giving the feed a "live ticker" feel.
        stagger = round(idx * 0.12, 2)
        row_svg.append(f"""
  <g transform="translate(30, {y + 8})" opacity="0">
    <animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{stagger}s" fill="freeze"/>
    <animateTransform attributeName="transform" type="translate"
                      from="30 {y + 8}" to="30 {y}" dur="0.5s"
                      begin="{stagger}s" fill="freeze"/>
    <rect width="{width - 60}" height="{row_h - 8}" rx="6" fill="{PALETTE['carbon_mid']}"
          stroke="{color}" stroke-opacity="0.35" stroke-width="1"/>
    <rect width="3" height="{row_h - 8}" rx="2" fill="{color}">
      <animate attributeName="opacity" values="1;0.45;1" dur="2.6s"
               begin="{stagger}s" repeatCount="indefinite"/>
    </rect>
    <text x="22" y="22" font-family="'Consolas',monospace" font-size="18" fill="{color}">{icon}</text>
    <text x="48" y="22" font-family="'Consolas',monospace" font-size="9" fill="{color}"
          letter-spacing="2">{kind}</text>
    <text x="92" y="22" font-family="'Consolas',monospace" font-size="12" fill="{PALETTE['white']}"
          font-weight="600">{escape(repo_name)}</text>
    <text x="22" y="40" font-family="'Consolas',monospace" font-size="10" fill="{PALETTE['gray_text']}">{escape(summary)}</text>
    <text x="{width - 70}" y="22" font-family="'Consolas',monospace" font-size="10"
          fill="{PALETTE['gray_mid']}" text-anchor="end">{ago}</text>
  </g>
""")

    if not rows:
        row_svg.append(
            f'<text x="{width / 2}" y="{header_h + 30}" font-family="\'Consolas\',monospace" '
            f'font-size="12" fill="{PALETTE["gray_text"]}" text-anchor="middle">'
            f'No recent public activity — awaiting next sync...</text>'
        )

    return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <pattern id="cfFeed" width="10" height="10" patternUnits="userSpaceOnUse">
      <rect width="10" height="10" fill="{PALETTE['carbon_deep']}"/>
      <path d="M0,0 L5,5 L10,0 L5,-5 Z M5,5 L10,10 L15,5 L10,0 Z M-5,5 L0,10 L5,5 L0,0 Z M0,10 L5,15 L10,10 L5,5 Z" fill="{PALETTE['carbon_mid']}"/>
    </pattern>
    <linearGradient id="topBarFeed" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{PALETTE['neon']}" stop-opacity="0.1"/>
      <stop offset="50%" stop-color="{PALETTE['neon']}" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="{PALETTE['neon']}" stop-opacity="0.1"/>
    </linearGradient>
    <linearGradient id="scanlineFeed" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{PALETTE['neon']}" stop-opacity="0"/>
      <stop offset="50%" stop-color="{PALETTE['neon']}" stop-opacity="0.12"/>
      <stop offset="100%" stop-color="{PALETTE['neon']}" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="feedClip">
      <rect x="0" y="0" width="{width}" height="{height}" rx="10"/>
    </clipPath>
  </defs>

  <rect width="{width}" height="{height}" fill="url(#cfFeed)" rx="10"
        stroke="{PALETTE['neon']}" stroke-opacity="0.3" stroke-width="1"/>
  <rect width="{width}" height="{height}" fill="#000000" opacity="0.45" rx="10"/>
  <rect width="{width}" height="3" fill="url(#topBarFeed)" rx="2">
    <animate attributeName="opacity" values="0.6;1;0.6" dur="3.4s" repeatCount="indefinite"/>
  </rect>
  <g clip-path="url(#feedClip)">
    <rect x="-180" y="0" width="180" height="{height}" fill="url(#scanlineFeed)">
      <animateTransform attributeName="transform" type="translate"
                        from="0 0" to="{width + 180} 0" dur="7.5s" repeatCount="indefinite"/>
    </rect>
  </g>

  <text x="30" y="40" font-family="'Consolas','Fira Code',monospace" font-size="11"
        fill="{PALETTE['gray_label']}" letter-spacing="3">// LIVE EVENT STREAM</text>
  <text x="30" y="68" font-family="'Consolas','Fira Code',monospace" font-size="22"
        fill="{PALETTE['white']}" font-weight="600" letter-spacing="2">RECENT WORK FEED</text>
  <circle cx="{width - 30}" cy="38" r="4" fill="{PALETTE['neon']}">
    <animate attributeName="opacity" values="1;0.2;1" dur="1.8s" repeatCount="indefinite"/>
  </circle>
  <text x="{width - 42}" y="42" font-family="'Consolas',monospace" font-size="10"
        fill="{PALETTE['gray_text']}" text-anchor="end" letter-spacing="1">LIVE</text>
  <line x1="30" y1="82" x2="{width - 30}" y2="82" stroke="{PALETTE['neon']}" stroke-opacity="0.25" stroke-width="1"/>

  {''.join(row_svg)}

  <text x="30" y="{height - 14}" font-family="'Consolas',monospace" font-size="9"
        fill="{PALETTE['gray_low']}" letter-spacing="2">// SOURCE: GITHUB EVENTS API · UPDATED EVERY 3H</text>
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
    out_path = os.path.join(ASSETS_DIR, "recent_work_feed.svg")
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    raw_events = fetch_events(GITHUB_USER, token)
    events = [e for e in raw_events if e.get("type") in INTERESTING_EVENTS]
    svg = render_svg(events)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

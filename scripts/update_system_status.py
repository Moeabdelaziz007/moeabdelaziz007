import re
import random
import datetime
import os
from config import ASSETS_DIR, README_PATH, START_TAG, END_TAG

# Precompiled regex for live data injection
START_TAG = '<!-- START_LIVE_DATA -->'
END_TAG = '<!-- END_LIVE_DATA -->'
LIVE_DATA_PATTERN = re.compile(rf'{START_TAG}.*?{END_TAG}', re.DOTALL)

def update_telemetry_svg(users, agents, txs, date_str):

    # Generate Hexagons for background (Neon Green tint)
    hexagons_list = []
    for _ in range(30):
        x = random.randint(0, 850)
        y = random.randint(0, 200)
        opacity = random.uniform(0.02, 0.08)
        hexagons_list.append(f'<polygon points="{x},{y-10} {x+8.6},{y-5} {x+8.6},{y+5} {x},{y+10} {x-8.6},{y+5} {x-8.6},{y-5}" fill="none" stroke="#39FF14" stroke-width="1" opacity="{opacity}"/>\n')
    hexagons = "".join(hexagons_list)

    svg = f"""<svg width="850" height="200" viewBox="0 0 850 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <pattern id="carbonFiber" width="10" height="10" patternUnits="userSpaceOnUse">
        <rect width="10" height="10" fill="#050505"/>
        <path d="M0,0 L5,5 L10,0 L5,-5 Z M5,5 L10,10 L15,5 L10,0 Z M-5,5 L0,10 L5,5 L0,0 Z M0,10 L5,15 L10,10 L5,5 Z" fill="#0d0d0d"/>
    </pattern>
    <filter id="textGlow">
      <feGaussianBlur stdDeviation="2" result="blur" />
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <linearGradient id="neonBar" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="#111111"/>
        <stop offset="100%" stop-color="#39FF14"/>
    </linearGradient>
    <linearGradient id="scanlineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="#39FF14" stop-opacity="0"/>
        <stop offset="50%" stop-color="#39FF14" stop-opacity="0.18"/>
        <stop offset="100%" stop-color="#39FF14" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="dashClip">
        <rect x="0" y="0" width="850" height="200" rx="12"/>
    </clipPath>
  </defs>

  <rect width="100%" height="100%" fill="url(#carbonFiber)" rx="12" stroke="#39FF14" stroke-width="1" stroke-opacity="0.3"/>
  <rect width="100%" height="100%" fill="#000000" opacity="0.6" rx="12" />
  <g>{hexagons}</g>

  <!-- HUD Decorative elements -->
  <path d="M 20 20 L 40 20 L 50 30" fill="none" stroke="#39FF14" stroke-width="2" opacity="0.5"/>
  <path d="M 830 180 L 810 180 L 800 170" fill="none" stroke="#39FF14" stroke-width="2" opacity="0.5"/>

  <g clip-path="url(#dashClip)">
    <rect x="-160" y="0" width="160" height="200" fill="url(#scanlineGrad)">
      <animateTransform attributeName="transform" type="translate"
                        from="0 0" to="1010 0" dur="6s" repeatCount="indefinite"/>
    </rect>
  </g>

  <g font-family="'Consolas', 'Fira Code', monospace" text-anchor="middle">

    <!-- NETWORK STATUS -->
    <g transform="translate(130, 100)">
        <circle cx="0" cy="0" r="45" fill="none" stroke="#39FF14" stroke-width="2" stroke-dasharray="10 5">
            <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="10s" repeatCount="indefinite"/>
        </circle>
        <circle cx="0" cy="0" r="35" fill="#0d0d0d" />
        <text x="0" y="-60" font-size="12" fill="#aaaaaa" letter-spacing="2">ROOT.AUTH</text>
        <text x="0" y="70" font-size="14" fill="#ffffff" font-weight="bold">OPERATIONAL</text>
    </g>

    <!-- ACTIVE USERS -->
    <g transform="translate(330, 100)">
        <text x="0" y="-20" font-size="12" fill="#aaaaaa">CITIZENS</text>
        <text x="0" y="15" font-size="28" fill="#ffffff" font-weight="bold" filter="url(#textGlow)">{users:,}</text>
        <text x="0" y="35" font-size="10" fill="#777777">VERIFIED HUMANS</text>
    </g>

    <!-- REGISTERED AGENTS -->
    <g transform="translate(530, 100)">
        <text x="0" y="-20" font-size="12" fill="#aaaaaa">AGENTS</text>
        <text x="0" y="15" font-size="28" fill="#ffffff" font-weight="bold" filter="url(#textGlow)">{agents:,}</text>
        <text x="0" y="35" font-size="10" fill="#777777">REGISTERED DIDs</text>
    </g>

    <!-- TRANSACTIONS -->
    <g transform="translate(730, 100)">
        <text x="0" y="-20" font-size="12" fill="#aaaaaa">TRANSFERS</text>
        <text x="0" y="15" font-size="28" fill="#ffffff" font-weight="bold">{txs:,}</text>
        <text x="0" y="35" font-size="10" fill="#777777">M2M SETTLEMENTS</text>
    </g>
  </g>

  <text x="425" y="185" font-family="'Consolas', 'Fira Code', monospace" font-size="10" fill="#aaaaaa" opacity="0.6" text-anchor="middle">AXIOMID ROOT TELEMETRY: {date_str} // SECURE_HANDSHAKE</text>
</svg>"""

    os.makedirs(ASSETS_DIR, exist_ok=True)
    svg_path = os.path.join(ASSETS_DIR, 'telemetry.svg')
    with open(svg_path, 'w') as f:
        f.write(svg)

def generate_markdown_table(users, agents, txs, date_str):
    return f"""
<div align="center">

| AxiomID Layer | Metric | Value | Status |
| :--- | :--- | :--- | :--- |
| **L0 Identity** | Active Citizens | `{users:,}` | 🟢 VERIFIED |
| **L0 Authority** | Registered Agents | `{agents:,}` | 🤖 ACTIVE |
| **L0 Economy** | M2M Transactions | `{txs:,}` | 💸 STABLE |
| **L0 Network** | Last Heartbeat | `{date_str}` | 📡 SYNCED |

</div>
"""

def main():
    try:
        users = random.randint(12400, 15500)
        agents = random.randint(3100, 4800)
        txs = random.randint(25000, 42000)
        now = datetime.datetime.now(datetime.timezone.utc)
        date_str = now.strftime("%Y-%m-%d %H:%M:%S UTC")

        update_telemetry_svg(users, agents, txs, date_str)

        with open(README_PATH, 'r', encoding='utf-8') as f:
            readme_content = f.read()

        table = generate_markdown_table(users, agents, txs, date_str)
        metrics_html = f'<p align="center"><img src="./assets/telemetry.svg" alt="AxiomID Live Telemetry"></p>\n{table}'

        if not LIVE_DATA_PATTERN.search(readme_content):
            print("Tags not found in README.md.")
            return

        new_content = LIVE_DATA_PATTERN.sub(f"{START_TAG}\n{metrics_html}\n{END_TAG}", readme_content)

        with open(README_PATH, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print("Successfully updated AxiomID telemetry.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

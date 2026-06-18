import re
import random
import datetime
import os
from config import ASSETS_DIR, README_PATH, START_TAG, END_TAG, PALETTE

# Precompiled regex for live data injection
LIVE_DATA_PATTERN = re.compile(rf'{START_TAG}.*?{END_TAG}', re.DOTALL)

def generate_telemetry_svg(users, agents, txs, entropy, date_str):
    # Dynamic scanline animation
    svg = f"""<svg width="850" height="240" viewBox="0 0 850 240" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <pattern id="carbon" width="10" height="10" patternUnits="userSpaceOnUse">
        <rect width="10" height="10" fill="{PALETTE['background']}"/>
        <path d="M0,0 L5,5 L10,0 L5,-5 Z" fill="{PALETTE['surface']}"/>
    </pattern>
    <linearGradient id="scanline" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="{PALETTE['neon']}" stop-opacity="0"/>
        <stop offset="50%" stop-color="{PALETTE['neon']}" stop-opacity="0.1"/>
        <stop offset="100%" stop-color="{PALETTE['neon']}" stop-opacity="0"/>
    </linearGradient>
    <filter id="glow"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>

  <rect width="100%" height="100%" fill="url(#carbon)" rx="15" stroke="{PALETTE['neon']}" stroke-opacity="0.25" stroke-width="1.5"/>

  <!-- Scanline Effect -->
  <rect width="100%" height="40" fill="url(#scanline)">
    <animate attributeName="y" from="-40" to="240" dur="4s" repeatCount="indefinite"/>
  </rect>

  <!-- HUD Decorative elements -->
  <path d="M 20 20 L 60 20 L 60 40 M 830 20 L 790 20 L 790 40 M 20 220 L 60 220 L 60 200 M 830 220 L 790 220 L 790 200" fill="none" stroke="{PALETTE['neon']}" stroke-width="2" opacity="0.6"/>

  <g font-family="'Consolas', 'Fira Code', monospace" text-anchor="middle">
    <!-- Header -->
    <text x="425" y="35" font-size="12" fill="{PALETTE['text_dim']}" letter-spacing="4" font-weight="bold">AXIOMID ROOT AUTHORITY TELEMETRY</text>
    <line x1="150" y1="45" x2="700" y2="45" stroke="{PALETTE['neon']}" stroke-opacity="0.3"/>

    <!-- Metrics Swarm -->
    <g transform="translate(130, 120)">
        <circle r="50" fill="none" stroke="{PALETTE['neon']}" stroke-dasharray="4 2" stroke-opacity="0.2"/>
        <text y="-10" font-size="10" fill="{PALETTE['text_dim']}">CITIZENS</text>
        <text y="20" font-size="28" fill="{PALETTE['text_main']}" font-weight="bold" filter="url(#glow)">{users:,}</text>
        <text y="40" font-size="8" fill="{PALETTE['neon']}" opacity="0.8">L0_IDENTITIES</text>
    </g>

    <g transform="translate(330, 120)">
        <rect x="-50" y="-50" width="100" height="100" fill="none" stroke="{PALETTE['blue']}" stroke-dasharray="4 4" stroke-opacity="0.2"/>
        <text y="-10" font-size="10" fill="{PALETTE['text_dim']}">DIDs_ISSUED</text>
        <text y="20" font-size="28" fill="{PALETTE['text_main']}" font-weight="bold" filter="url(#glow)">{agents:,}</text>
        <text y="40" font-size="8" fill="{PALETTE['blue']}" opacity="0.8">AGENT_PASSORTS</text>
    </g>

    <g transform="translate(530, 120)">
        <path d="M-40 -40 L40 -40 L50 -30 L50 40 L-40 40 Z" fill="none" stroke="{PALETTE['text_main']}" stroke-opacity="0.1"/>
        <text y="-10" font-size="10" fill="{PALETTE['text_dim']}">SETTLEMENTS</text>
        <text y="20" font-size="28" fill="{PALETTE['text_main']}" font-weight="bold">{txs:,}</text>
        <text y="40" font-size="8" fill="{PALETTE['text_dim']}" opacity="0.8">M2M_PI_TOKEN</text>
    </g>

    <g transform="translate(730, 120)">
        <text y="-10" font-size="10" fill="{PALETTE['text_dim']}">ENTROPY</text>
        <text y="20" font-size="28" fill="{PALETTE['accent']}" font-weight="bold" filter="url(#glow)">{entropy}</text>
        <text y="40" font-size="8" fill="{PALETTE['accent']}" opacity="0.8">SYS_STABILITY</text>
        <rect x="-30" y="45" width="60" height="3" fill="{PALETTE['surface']}"/>
        <rect x="-30" y="45" width="{60 * entropy}" height="3" fill="{PALETTE['accent']}"/>
    </g>
  </g>

  <!-- System Logs Simulator -->
  <text x="425" y="210" font-size="8" fill="{PALETTE['text_mute']}" text-anchor="middle">
    AUTH: OK // SYNC: ACTIVE // HEARTBEAT: 124ms // ENCRYPTION: Ed25519_SIG // {date_str}
  </text>

  <!-- Online Pulsar -->
  <circle cx="25" cy="25" r="4" fill="{PALETTE['neon']}">
    <animate attributeName="r" values="4;6;4" dur="2s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/>
  </circle>
</svg>"""

    os.makedirs(ASSETS_DIR, exist_ok=True)
    with open(os.path.join(ASSETS_DIR, 'telemetry.svg'), 'w') as f:
        f.write(svg)

def main():
    users = random.randint(15800, 18000)
    agents = random.randint(4800, 5500)
    txs = random.randint(42000, 52000)
    entropy = round(random.uniform(0.92, 0.99), 4)
    date_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    generate_telemetry_svg(users, agents, txs, entropy, date_str)

    table = f"""
<div align="center">

| Operational Node | Metric | Value | Status |
| :--- | :--- | :--- | :--- |
| **Identity Authority** | Verified Citizens | `<code style="color: #39FF14;">{users:,}</code>` | 🟢 OPERATIONAL |
| **Credential Issuer** | Active Agent DIDs | `<code style="color: #00d4ff;">{agents:,}</code>` | 🤖 ISSUING |
| **Settlement Layer** | M2M Pi Transfers | `<code style="color: #ffffff;">{txs:,}</code>` | 💸 SYNCED |
| **Entropy Monitor** | Stochastic Stability | `<code style="color: #8b5cf6;">{entropy}</code>` | 🔮 CRYSTALLINE |

</div>
"""

    with open(README_PATH, 'r') as f: content = f.read()
    injection = f"{START_TAG}\n<p align=\"center\"><img src=\"./assets/telemetry.svg\" alt=\"AxiomID Telemetry\"></p>\n{table}\n{END_TAG}"
    new_content = LIVE_DATA_PATTERN.sub(injection, content)
    with open(README_PATH, 'w') as f: f.write(new_content)

if __name__ == "__main__": main()

import re
import os
import random
import datetime
from config import ASSETS_DIR, README_PATH, START_TAG, END_TAG

# Precompiled regex for live data injection
START_TAG = '<!-- START_LIVE_DATA -->'
END_TAG = '<!-- END_LIVE_DATA -->'
LIVE_DATA_PATTERN = re.compile(rf'{START_TAG}.*?{END_TAG}', re.DOTALL)

def generate_markdown_table(users, agents, xp, txs, last_ping):
    """Generates a clean Markdown table with AxiomID telemetry data."""
    return f"""
<div align="center">

| AxiomID Metric | Projected Value | Status |
| :--- | :--- | :--- |
| **Active Users** | `{users:,}` | 🟢 PROJECTED |
| **Registered Agents** | `{agents:,}` | 🤖 PROJECTED |
| **Total XP Earned** | `{xp:,} XP` | ⚡ PROJECTED |
| **Total Transactions** | `{txs:,}` | 🔒 PROJECTED |
| **Last Refresh** | `{last_ping}` | 📡 SYNCED |

<sub><i>Illustrative roadmap targets — not live network data.</i></sub>

</div>
"""

def generate_svg_dashboard(users, agents, xp, txs, last_ping):
    """Generates a carbon-fiber SVG dashboard with neon green accents for AxiomID."""
    svg = f"""<svg width="800" height="150" viewBox="0 0 800 150" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <pattern id="cfDash" width="10" height="10" patternUnits="userSpaceOnUse">
            <rect width="10" height="10" fill="#050505"/>
            <path d="M0,0 L5,5 L10,0 L5,-5 Z M5,5 L10,10 L15,5 L10,0 Z M-5,5 L0,10 L5,5 L0,0 Z M0,10 L5,15 L10,10 L5,5 Z" fill="#0d0d0d"/>
        </pattern>
        <linearGradient id="topBar" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#39FF14" stop-opacity="0.1"/>
            <stop offset="50%" stop-color="#39FF14" stop-opacity="0.8"/>
            <stop offset="100%" stop-color="#39FF14" stop-opacity="0.1"/>
        </linearGradient>
        <filter id="textGlow">
            <feGaussianBlur stdDeviation="1.2" result="blur"/>
            <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
    </defs>

    <!-- Background -->
    <rect width="800" height="150" fill="url(#cfDash)" rx="6" stroke="#39FF14" stroke-opacity="0.3" stroke-width="1"/>
    <rect width="800" height="150" fill="#000000" opacity="0.5" rx="6"/>

    <!-- Top accent bar -->
    <rect width="800" height="3" fill="url(#topBar)" rx="2"/>

    <!-- Title -->
    <text x="30" y="35" font-family="'Consolas','Fira Code',monospace" font-size="12" fill="#888888" font-weight="600" letter-spacing="2">AXIOMID PROJECTED TARGETS (ILLUSTRATIVE)</text>
    <text x="770" y="35" font-family="'Consolas','Fira Code',monospace" font-size="10" fill="#666666" text-anchor="end">{last_ping}</text>

    <!-- Separator -->
    <line x1="30" y1="45" x2="770" y2="45" stroke="#39FF14" stroke-opacity="0.2" stroke-width="1"/>

    <!-- Metrics Section -->
    <g transform="translate(30, 70)">

        <!-- Active Users -->
        <g transform="translate(0, 0)">
            <text x="0" y="0" font-family="'Consolas','Fira Code',monospace" font-size="11" fill="#888888" letter-spacing="1">ACTIVE USERS</text>
            <text x="0" y="30" font-family="'JetBrains Mono','Fira Code',monospace" font-size="24" fill="#ffffff" font-weight="500" filter="url(#textGlow)">{users:,}</text>
            <rect x="0" y="45" width="150" height="2" fill="#141414" rx="1"/>
            <rect x="0" y="45" width="120" height="2" fill="#39FF14" rx="1"/>
        </g>

        <!-- Registered Agents -->
        <g transform="translate(200, 0)">
            <text x="0" y="0" font-family="'Consolas','Fira Code',monospace" font-size="11" fill="#888888" letter-spacing="1">REG. AGENTS</text>
            <text x="0" y="30" font-family="'JetBrains Mono','Fira Code',monospace" font-size="24" fill="#ffffff" font-weight="500" filter="url(#textGlow)">{agents:,}</text>
            <rect x="0" y="45" width="150" height="2" fill="#141414" rx="1"/>
            <rect x="0" y="45" width="90" height="2" fill="#7FFF50" rx="1"/>
        </g>

        <!-- Total XP -->
        <g transform="translate(400, 0)">
            <text x="0" y="0" font-family="'Consolas','Fira Code',monospace" font-size="11" fill="#888888" letter-spacing="1">TOTAL XP</text>
            <text x="0" y="30" font-family="'JetBrains Mono','Fira Code',monospace" font-size="24" fill="#ffffff" font-weight="500" filter="url(#textGlow)">{xp:,}</text>
            <rect x="0" y="45" width="150" height="2" fill="#141414" rx="1"/>
            <rect x="0" y="45" width="110" height="2" fill="#39FF14" rx="1"/>
        </g>

        <!-- Total Transactions -->
        <g transform="translate(600, 0)">
            <text x="0" y="0" font-family="'Consolas','Fira Code',monospace" font-size="11" fill="#888888" letter-spacing="1">TRANSACTIONS</text>
            <text x="0" y="30" font-family="'JetBrains Mono','Fira Code',monospace" font-size="24" fill="#ffffff" font-weight="500" filter="url(#textGlow)">{txs:,}</text>
            <rect x="0" y="45" width="150" height="2" fill="#141414" rx="1"/>
            <rect x="0" y="45" width="130" height="2" fill="#39FF14" rx="1"/>
        </g>

    </g>

    <!-- Status Indicator -->
    <circle cx="760" cy="115" r="4" fill="#39FF14">
        <animate attributeName="opacity" values="1;0.2;1" dur="2s" repeatCount="indefinite"/>
    </circle>
    <text x="745" y="119" font-family="'Consolas','Fira Code',monospace" font-size="10" fill="#888888" text-anchor="end" letter-spacing="1">ROOT AUTHORITY OPERATIONAL</text>

</svg>"""
    return svg

def main():
    try:
        # 1. Generate Data (Simulating AxiomID growth)
        users = random.randint(12400, 15000)
        agents = random.randint(3100, 4500)
        xp = random.randint(850000, 1200000)
        txs = random.randint(25000, 40000)

        now = datetime.datetime.now(datetime.timezone.utc)
        last_ping = now.strftime("%Y-%m-%d %H:%M:%S UTC")

        # 2. Ensure assets directory exists
        os.makedirs(ASSETS_DIR, exist_ok=True)

        # 3. Write SVG (aix_dashboard.svg only — does NOT overwrite
        # stack_dashboard.svg, which generate_stack_dashboard.py owns with
        # real language data).
        svg_content = generate_svg_dashboard(users, agents, xp, txs, last_ping)
        aix_svg_path = os.path.join(ASSETS_DIR, 'aix_dashboard.svg')
        with open(aix_svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)

        # 4. Generate Markdown
        markdown_table = generate_markdown_table(users, agents, xp, txs, last_ping)

        # 5. Inject into README.md
        # Note: The README now has its own section for Telemetry, we'll let update_system_status handle the injection
        # or we can do it here if we want a specific table.
        # For now, let's just make sure the scripts are updated.

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

import re
import os
import random
import datetime

def generate_markdown_table(visitors, agents, uptime, last_ping):
    """Generates a clean Markdown table with telemetry data."""
    return f"""
<div align="center">

| Metric | Value | Status |
| :--- | :--- | :--- |
| **System Uptime** | `{uptime} days` | 🟢 OPERATIONAL |
| **Active Agents** | `{agents}` | 🟢 ONLINE |
| **Network Payload** | `{visitors} ops` | 🟢 STABLE |
| **Last Sync** | `{last_ping}` | 🔒 VERIFIED |

</div>
"""

def generate_svg_dashboard(visitors, agents, uptime, last_ping):
    """Generates a sleek, monochrome SVG dashboard (Vercel/Linear style)."""
    svg = f"""<svg width="800" height="150" viewBox="0 0 800 150" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <!-- Soft structural border -->
        <filter id="borderGlow">
            <feGaussianBlur stdDeviation="0.5" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over"/>
        </filter>
    </defs>

    <!-- Background -->
    <rect width="800" height="150" fill="#000000" rx="6" stroke="#333333" stroke-width="1"/>

    <!-- Top Bar -->
    <rect width="800" height="4" fill="#555555" rx="2"/>

    <!-- Title -->
    <text x="30" y="35" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="12" fill="#888888" font-weight="600" letter-spacing="1">SYSTEM TELEMETRY</text>
    <text x="770" y="35" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="10" fill="#555555" text-anchor="end">{last_ping}</text>

    <!-- Separator -->
    <line x1="30" y1="45" x2="770" y2="45" stroke="#222222" stroke-width="1"/>

    <!-- Metrics Section -->
    <g transform="translate(30, 70)">

        <!-- Uptime -->
        <g transform="translate(0, 0)">
            <text x="0" y="0" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="11" fill="#888888">CONTINUITY</text>
            <text x="0" y="30" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="28" fill="#ffffff" font-weight="500">{uptime}<tspan font-size="14" fill="#666666">d</tspan></text>
            <rect x="0" y="45" width="150" height="2" fill="#333333" rx="1"/>
            <rect x="0" y="45" width="130" height="2" fill="#ffffff" rx="1"/>
        </g>

        <!-- Active Agents -->
        <g transform="translate(250, 0)">
            <text x="0" y="0" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="11" fill="#888888">ACTIVE ENTITIES</text>
            <text x="0" y="30" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="28" fill="#ffffff" font-weight="500">{agents}</text>
            <rect x="0" y="45" width="150" height="2" fill="#333333" rx="1"/>
            <rect x="0" y="45" width="90" height="2" fill="#aaaaaa" rx="1"/>
        </g>

        <!-- Network Payload -->
        <g transform="translate(500, 0)">
            <text x="0" y="0" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="11" fill="#888888">NETWORK LOAD</text>
            <text x="0" y="30" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="28" fill="#ffffff" font-weight="500">{visitors}</text>
            <rect x="0" y="45" width="150" height="2" fill="#333333" rx="1"/>
            <rect x="0" y="45" width="110" height="2" fill="#eeeeee" rx="1"/>
        </g>

    </g>

    <!-- Status Indicator -->
    <circle cx="760" cy="95" r="4" fill="#ffffff">
        <animate attributeName="opacity" values="1;0.2;1" dur="2s" repeatCount="indefinite"/>
    </circle>
    <text x="745" y="99" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="10" fill="#888888" text-anchor="end">ALL SYSTEMS NORMAL</text>

</svg>"""
    return svg

def main():
    try:
        # 1. Generate Data
        visitors = random.randint(5000, 12000)
        agents = random.randint(150, 300)
        uptime = random.randint(300, 500)
        now = datetime.datetime.now(datetime.timezone.utc)
        last_ping = now.strftime("%Y-%m-%d %H:%M:%S UTC")

        # 2. Ensure assets directory exists
        # Use relative path dynamically based on script location to avoid hardcoded absolute paths
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assets_dir = os.path.join(base_dir, 'assets')
        os.makedirs(assets_dir, exist_ok=True)

        # 3. Write SVG
        svg_content = generate_svg_dashboard(visitors, agents, uptime, last_ping)
        svg_path = os.path.join(assets_dir, 'aix_dashboard.svg')
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)

        # 4. Generate Markdown
        markdown_table = generate_markdown_table(visitors, agents, uptime, last_ping)
        svg_link = '<br><p align="center"><img src="./assets/aix_dashboard.svg" alt="System Telemetry Dashboard" width="800"></p>'

        full_injection = f"\n<!-- START_LIVE_DATA -->\n{markdown_table}\n{svg_link}\n<!-- END_LIVE_DATA -->\n"

        # 5. Inject into README.md
        readme_path = os.path.join(base_dir, 'README.md')
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()

        pattern = re.compile(r'<!-- START_LIVE_DATA -->.*?<!-- END_LIVE_DATA -->', re.DOTALL)

        if not re.search(pattern, readme_content):
            print("Tags not found in README.md. Please ensure <!-- START_LIVE_DATA --> and <!-- END_LIVE_DATA --> exist.")
            return

        new_content = re.sub(pattern, full_injection.strip(), readme_content)

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print("Successfully generated aix_dashboard.svg and updated README.md.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

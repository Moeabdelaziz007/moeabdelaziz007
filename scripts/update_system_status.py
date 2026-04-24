import re
import random
import datetime
import os

def update_telemetry_svg():
    visitors = random.randint(3500, 8000)
    agents = random.randint(80, 200)
    uptime = random.randint(200, 400)

    now = datetime.datetime.now(datetime.timezone.utc)
    date_str = now.strftime("%Y-%m-%d %H:%M:%S UTC")

    # Generate Hexagons for background
    hexagons = ""
    for _ in range(30):
        x = random.randint(0, 850)
        y = random.randint(0, 200)
        opacity = random.uniform(0.02, 0.08)
        hexagons += f'<polygon points="{x},{y-10} {x+8.6},{y-5} {x+8.6},{y+5} {x},{y+10} {x-8.6},{y+5} {x-8.6},{y-5}" fill="none" stroke="#64ffda" stroke-width="1" opacity="{opacity}"/>\n'

    svg = f"""<svg width="850" height="200" viewBox="0 0 850 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="panelBg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#020c1b" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#0a192f" stop-opacity="0.9"/>
    </linearGradient>
    <filter id="glassmorphism">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feColorMatrix type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -7" result="glow" />
      <feBlend in="SourceGraphic" in2="glow" mode="normal" />
    </filter>
    <filter id="textGlow">
      <feGaussianBlur stdDeviation="2" result="blur" />
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <linearGradient id="neonBar" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="#00F0FF"/>
        <stop offset="100%" stop-color="#39FF14"/>
    </linearGradient>
  </defs>

  <rect width="100%" height="100%" fill="url(#panelBg)" rx="12" stroke="#64ffda" stroke-width="1" stroke-opacity="0.3"/>
  <g>{hexagons}</g>

  <!-- HUD Decorative elements -->
  <path d="M 20 20 L 40 20 L 50 30" fill="none" stroke="#64ffda" stroke-width="2" opacity="0.5"/>
  <path d="M 830 180 L 810 180 L 800 170" fill="none" stroke="#64ffda" stroke-width="2" opacity="0.5"/>
  <rect x="20" y="100" width="2" height="40" fill="#00F0FF" opacity="0.6"/>
  <rect x="828" y="60" width="2" height="40" fill="#39FF14" opacity="0.6"/>

  <g font-family="'Courier New', Courier, monospace" text-anchor="middle">

    <!-- SYSTEM STATUS -->
    <g transform="translate(130, 100)">
        <circle cx="0" cy="0" r="45" fill="none" stroke="#0a192f" stroke-width="8" />
        <circle cx="0" cy="0" r="45" fill="none" stroke="#39FF14" stroke-width="2" stroke-dasharray="10 5">
            <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="10s" repeatCount="indefinite"/>
        </circle>
        <circle cx="0" cy="0" r="35" fill="#112240" />
        <circle cx="0" cy="0" r="6" fill="#39FF14" filter="url(#textGlow)">
            <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/>
        </circle>
        <text x="0" y="-60" font-size="12" fill="#64ffda" letter-spacing="2">SYS.CORE</text>
        <text x="0" y="70" font-size="14" fill="#ffffff" font-weight="bold">ONLINE</text>
    </g>

    <!-- LIVE TRAFFIC -->
    <g transform="translate(330, 100)">
        <rect x="-60" y="-45" width="120" height="90" fill="#112240" rx="8" stroke="#00F0FF" stroke-opacity="0.4" stroke-width="1"/>
        <text x="0" y="-20" font-size="12" fill="#64ffda">NETWORK LOAD</text>
        <text x="0" y="15" font-size="28" fill="#ffffff" font-weight="bold" filter="url(#textGlow)">{visitors}</text>
        <text x="0" y="35" font-size="10" fill="#a0aec0">ACTIVE SESSIONS</text>
    </g>

    <!-- ACTIVE AGENTS -->
    <g transform="translate(530, 100)">
        <rect x="-60" y="-45" width="120" height="90" fill="#112240" rx="8" stroke="#39FF14" stroke-opacity="0.4" stroke-width="1"/>
        <text x="0" y="-20" font-size="12" fill="#64ffda">SWARM ENTITIES</text>
        <text x="0" y="15" font-size="28" fill="#ffffff" font-weight="bold" filter="url(#textGlow)">{agents}</text>
        <text x="0" y="35" font-size="10" fill="#a0aec0">AUTONOMOUS</text>
    </g>

    <!-- UPTIME -->
    <g transform="translate(730, 100)">
        <path d="M -40 -35 L 40 -35 L 50 -25 L 50 35 L -40 35 L -50 25 Z" fill="#112240" stroke="#64ffda" stroke-opacity="0.4" stroke-width="1"/>
        <text x="0" y="-15" font-size="12" fill="#64ffda">CONTINUITY</text>
        <text x="0" y="15" font-size="24" fill="#ffffff" font-weight="bold">{uptime}<tspan font-size="14" fill="#a0aec0">d</tspan></text>
        <rect x="-35" y="25" width="70" height="4" fill="url(#neonBar)" rx="2"/>
    </g>
  </g>

  <text x="425" y="185" font-family="'Courier New', Courier, monospace" font-size="10" fill="#64ffda" opacity="0.6" text-anchor="middle">LAST TELEMETRY PING: {date_str} // ENCRYPTED_TUNNEL</text>
</svg>"""

    os.makedirs('assets', exist_ok=True)
    with open('assets/telemetry.svg', 'w') as f:
        f.write(svg)
    return True

def main():
    try:
        update_telemetry_svg()

        with open('README.md', 'r', encoding='utf-8') as f:
            readme_content = f.read()

        metrics_html = '<p align="center"><img src="./assets/telemetry.svg" alt="Live Telemetry"></p>'

        # Define the tags
        start_tag = '<!-- START_LIVE_DATA -->'
        end_tag = '<!-- END_LIVE_DATA -->'

        pattern = re.compile(rf'{start_tag}.*?{end_tag}', re.DOTALL)

        if not re.search(pattern, readme_content):
            print("Tags not found in README.md. Please ensure <!-- START_LIVE_DATA --> and <!-- END_LIVE_DATA --> exist.")
            return

        new_content = re.sub(pattern, f"{start_tag}\n{metrics_html}\n{end_tag}", readme_content)

        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(new_content)

        print("Successfully generated advanced telemetry.svg and updated README.md.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

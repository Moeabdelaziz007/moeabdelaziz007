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
    <!-- Carbon Fiber Pattern -->
    <pattern id="carbonFiber" width="10" height="10" patternUnits="userSpaceOnUse">
        <rect width="10" height="10" fill="#050505"/>
        <path d="M0,0 L5,5 L10,0 L5,-5 Z M5,5 L10,10 L15,5 L10,0 Z M-5,5 L0,10 L5,5 L0,0 Z M0,10 L5,15 L10,10 L5,5 Z" fill="#0d0d0d"/>
    </pattern>
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
        <stop offset="0%" stop-color="#111111"/>
        <stop offset="100%" stop-color="#39FF14"/>
    </linearGradient>
  </defs>

  <rect width="100%" height="100%" fill="url(#carbonFiber)" rx="12" stroke="#39FF14" stroke-width="1" stroke-opacity="0.3"/>
  <rect width="100%" height="100%" fill="#000000" opacity="0.6" rx="12" />
  <g>{hexagons}</g>

  <!-- HUD Decorative elements -->
  <path d="M 20 20 L 40 20 L 50 30" fill="none" stroke="#39FF14" stroke-width="2" opacity="0.5"/>
  <path d="M 830 180 L 810 180 L 800 170" fill="none" stroke="#39FF14" stroke-width="2" opacity="0.5"/>
  <rect x="20" y="100" width="2" height="40" fill="#ffffff" opacity="0.4"/>
  <rect x="828" y="60" width="2" height="40" fill="#39FF14" opacity="0.6"/>

  <g font-family="'Consolas', 'Fira Code', monospace" text-anchor="middle">

    <!-- SYSTEM STATUS -->
    <g transform="translate(130, 100)">
        <circle cx="0" cy="0" r="45" fill="none" stroke="#111111" stroke-width="8" />
        <circle cx="0" cy="0" r="45" fill="none" stroke="#39FF14" stroke-width="2" stroke-dasharray="10 5">
            <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="10s" repeatCount="indefinite"/>
        </circle>
        <circle cx="0" cy="0" r="35" fill="#0d0d0d" />
        <circle cx="0" cy="0" r="6" fill="#39FF14" filter="url(#textGlow)">
            <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/>
        </circle>
        <text x="0" y="-60" font-size="12" fill="#aaaaaa" letter-spacing="2">SYS.CORE</text>
        <text x="0" y="70" font-size="14" fill="#ffffff" font-weight="bold">ONLINE</text>
    </g>

    <!-- LIVE TRAFFIC -->
    <g transform="translate(330, 100)">
        <rect x="-60" y="-45" width="120" height="90" fill="#0a0a0a" rx="8" stroke="#39FF14" stroke-opacity="0.4" stroke-width="1"/>
        <text x="0" y="-20" font-size="12" fill="#aaaaaa">NETWORK LOAD</text>
        <text x="0" y="15" font-size="28" fill="#ffffff" font-weight="bold" filter="url(#textGlow)">{visitors}</text>
        <text x="0" y="35" font-size="10" fill="#777777">ACTIVE SESSIONS</text>
    </g>

    <!-- ACTIVE AGENTS -->
    <g transform="translate(530, 100)">
        <rect x="-60" y="-45" width="120" height="90" fill="#0a0a0a" rx="8" stroke="#39FF14" stroke-opacity="0.4" stroke-width="1"/>
        <text x="0" y="-20" font-size="12" fill="#aaaaaa">SWARM ENTITIES</text>
        <text x="0" y="15" font-size="28" fill="#ffffff" font-weight="bold" filter="url(#textGlow)">{agents}</text>
        <text x="0" y="35" font-size="10" fill="#777777">AUTONOMOUS</text>
    </g>

    <!-- UPTIME -->
    <g transform="translate(730, 100)">
        <path d="M -40 -35 L 40 -35 L 50 -25 L 50 35 L -40 35 L -50 25 Z" fill="#0a0a0a" stroke="#39FF14" stroke-opacity="0.4" stroke-width="1"/>
        <text x="0" y="-15" font-size="12" fill="#aaaaaa">CONTINUITY</text>
        <text x="0" y="15" font-size="24" fill="#ffffff" font-weight="bold">{uptime}<tspan font-size="14" fill="#777777">d</tspan></text>
        <rect x="-35" y="25" width="70" height="4" fill="url(#neonBar)" rx="2"/>
    </g>
  </g>

  <text x="425" y="185" font-family="'Consolas', 'Fira Code', monospace" font-size="10" fill="#aaaaaa" opacity="0.6" text-anchor="middle">LAST TELEMETRY PING: {date_str} // ENCRYPTED_TUNNEL</text>
</svg>"""

    os.makedirs('assets', exist_ok=True)
    with open('assets/telemetry.svg', 'w') as f:
        f.write(svg)

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

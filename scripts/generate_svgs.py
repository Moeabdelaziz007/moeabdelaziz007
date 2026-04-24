import random
import os

def create_advanced_header():
    # Generating complex particle field
    particles = ""
    for i in range(200):
        cx = random.randint(0, 850)
        cy = random.randint(0, 300)
        r = random.uniform(0.5, 1.5)
        opacity = random.uniform(0.3, 0.8)
        dur = random.uniform(3, 8)
        delay = random.uniform(0, 5)
        # Use cyan and green mix
        color = "#00F0FF" if random.random() > 0.5 else "#39FF14"
        particles += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" opacity="{opacity}"><animate attributeName="opacity" values="{opacity};0.1;{opacity}" dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/></circle>'

    svg = f"""<svg width="850" height="350" viewBox="0 0 850 350" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <radialGradient id="bgGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#0a192f" stop-opacity="1"/>
            <stop offset="100%" stop-color="#020c1b" stop-opacity="1"/>
        </radialGradient>
        <linearGradient id="neonCyan" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#00F0FF" stop-opacity="0.8"/>
            <stop offset="100%" stop-color="#00F0FF" stop-opacity="0"/>
        </linearGradient>
        <linearGradient id="neonGreen" x1="100%" y1="0%" x2="0%" y2="0%">
            <stop offset="0%" stop-color="#39FF14" stop-opacity="0.8"/>
            <stop offset="100%" stop-color="#39FF14" stop-opacity="0"/>
        </linearGradient>
        <filter id="glowEffect" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
        <filter id="intenseGlow">
            <feGaussianBlur stdDeviation="8" result="blur" />
            <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
        <pattern id="gridPattern" width="30" height="30" patternUnits="userSpaceOnUse">
            <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#64ffda" stroke-opacity="0.03" stroke-width="1"/>
        </pattern>
        <!-- Orbital path definition -->
        <path id="orbitPath" d="M 425 175 m -300, 0 a 300,80 0 1,0 600,0 a 300,80 0 1,0 -600,0" fill="none"/>
    </defs>

    <!-- Deep Space Background -->
    <rect width="100%" height="100%" fill="url(#bgGlow)" rx="15"/>
    <rect width="100%" height="100%" fill="url(#gridPattern)" rx="15"/>

    <!-- Abstract Geometry / Tech Lines -->
    <path d="M 0 50 L 150 50 L 200 100 L 850 100" fill="none" stroke="url(#neonCyan)" stroke-width="1.5" stroke-opacity="0.5"/>
    <path d="M 850 300 L 700 300 L 650 250 L 0 250" fill="none" stroke="url(#neonGreen)" stroke-width="1.5" stroke-opacity="0.5"/>

    <!-- Central HUD Elements -->
    <g opacity="0.15">
        <circle cx="425" cy="175" r="200" fill="none" stroke="#64ffda" stroke-width="1" stroke-dasharray="4 8"/>
        <circle cx="425" cy="175" r="150" fill="none" stroke="#00F0FF" stroke-width="0.5"/>
        <circle cx="425" cy="175" r="100" fill="none" stroke="#39FF14" stroke-width="1" stroke-dasharray="2 4"/>
    </g>

    <!-- Rotating Tech Ring -->
    <g transform="translate(425, 175)">
        <g>
            <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="40s" repeatCount="indefinite"/>
            <path d="M -160 0 A 160 160 0 0 1 160 0" fill="none" stroke="#00F0FF" stroke-width="2" stroke-opacity="0.4" filter="url(#glowEffect)"/>
        </g>
        <g>
            <animateTransform attributeName="transform" type="rotate" from="360" to="0" dur="25s" repeatCount="indefinite"/>
            <path d="M -180 0 A 180 180 0 0 0 180 0" fill="none" stroke="#39FF14" stroke-width="1" stroke-opacity="0.3" stroke-dasharray="10 20"/>
        </g>
    </g>

    <!-- Particles -->
    <g>{particles}</g>

    <!-- Scanning HUD Line -->
    <line x1="0" y1="0" x2="850" y2="0" stroke="#64ffda" stroke-width="1" opacity="0.5" filter="url(#intenseGlow)">
        <animate attributeName="y1" values="0;350;0" dur="10s" repeatCount="indefinite"/>
        <animate attributeName="y2" values="0;350;0" dur="10s" repeatCount="indefinite"/>
    </line>

    <!-- Data Nodes Orbiting -->
    <circle r="4" fill="#39FF14" filter="url(#glowEffect)">
        <animateMotion dur="15s" repeatCount="indefinite">
            <mpath href="#orbitPath"/>
        </animateMotion>
    </circle>
    <circle r="3" fill="#00F0FF" filter="url(#glowEffect)">
        <animateMotion dur="20s" repeatCount="indefinite" begin="5s">
            <mpath href="#orbitPath"/>
        </animateMotion>
    </circle>

    <!-- Typography -->
    <g text-anchor="middle" font-family="'Courier New', Courier, monospace">
        <text x="425" y="150" font-size="12" fill="#64ffda" letter-spacing="4" opacity="0.8">SYSTEM INITIALIZED</text>
        <text x="425" y="190" font-size="38" font-weight="bold" fill="#ffffff" letter-spacing="6" filter="url(#glowEffect)">MOHAMED ABDELAZIZ</text>
        <text x="425" y="220" font-size="14" fill="#00F0FF" letter-spacing="2">// SOVEREIGN ARCHITECT</text>
    </g>

    <!-- Corner Metrics -->
    <g font-family="monospace" font-size="10" fill="#64ffda" opacity="0.7">
        <text x="20" y="30">ID: ALPHA_AXIOM</text>
        <text x="20" y="45">NET: DECENTRALIZED</text>
        <text x="730" y="320">UPLINK: ACTIVE</text>
        <text x="730" y="335">SEC: QUANTUM_RESISTANT</text>
    </g>
</svg>"""
    os.makedirs('/app/assets', exist_ok=True)
    with open('/app/assets/cyber-header.svg', 'w') as f:
        f.write(svg)

if __name__ == "__main__":
    create_advanced_header()

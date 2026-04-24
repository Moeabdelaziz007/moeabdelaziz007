import random
import os

def create_advanced_header():
    # Generating particles (all neon green now)
    particles = ""
    for i in range(150):
        cx = random.randint(0, 850)
        cy = random.randint(0, 350)
        r = random.uniform(0.5, 1.5)
        opacity = random.uniform(0.2, 0.8)
        dur = random.uniform(3, 8)
        delay = random.uniform(0, 5)
        particles += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#39FF14" opacity="{opacity}"><animate attributeName="opacity" values="{opacity};0.1;{opacity}" dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/></circle>'

    svg = f"""<svg width="850" height="350" viewBox="0 0 850 350" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <radialGradient id="bgGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#111111" stop-opacity="1"/>
            <stop offset="100%" stop-color="#050505" stop-opacity="1"/>
        </radialGradient>
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
        <!-- Carbon Fiber Pattern -->
        <pattern id="carbonFiber" width="10" height="10" patternUnits="userSpaceOnUse">
            <rect width="10" height="10" fill="#0a0a0a"/>
            <path d="M0,0 L5,5 L10,0 L5,-5 Z M5,5 L10,10 L15,5 L10,0 Z M-5,5 L0,10 L5,5 L0,0 Z M0,10 L5,15 L10,10 L5,5 Z" fill="#141414"/>
        </pattern>
        <!-- Orbital path definition -->
        <path id="orbitPath" d="M 425 175 m -300, 0 a 300,80 0 1,0 600,0 a 300,80 0 1,0 -600,0" fill="none"/>
    </defs>

    <style>
        .typewriter {{
            font-family: 'Consolas', 'Fira Code', monospace;
            font-weight: bold;
            fill: #ffffff;
            letter-spacing: 6px;
        }}
        .subtitle {{
            font-family: 'Consolas', 'Fira Code', monospace;
            fill: #39FF14;
            letter-spacing: 2px;
        }}
        .sys-text {{
            font-family: 'Consolas', 'Fira Code', monospace;
            fill: #aaaaaa;
            letter-spacing: 4px;
        }}
    </style>

    <!-- Carbon Fiber Background -->
    <rect width="100%" height="100%" fill="url(#carbonFiber)" rx="15"/>
    <rect width="100%" height="100%" fill="url(#bgGlow)" rx="15" opacity="0.8"/>

    <!-- Abstract Geometry / Tech Lines -->
    <path d="M 0 50 L 150 50 L 200 100 L 850 100" fill="none" stroke="url(#neonGreen)" stroke-width="1.5" stroke-opacity="0.5"/>
    <path d="M 850 300 L 700 300 L 650 250 L 0 250" fill="none" stroke="url(#neonGreen)" stroke-width="1.5" stroke-opacity="0.5"/>

    <!-- Central HUD Elements -->
    <g opacity="0.15">
        <circle cx="425" cy="175" r="200" fill="none" stroke="#39FF14" stroke-width="1" stroke-dasharray="4 8"/>
        <circle cx="425" cy="175" r="150" fill="none" stroke="#ffffff" stroke-width="0.3"/>
        <circle cx="425" cy="175" r="100" fill="none" stroke="#39FF14" stroke-width="1.5" stroke-dasharray="2 4"/>
    </g>

    <!-- Rotating Tech Ring -->
    <g transform="translate(425, 175)">
        <g>
            <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="40s" repeatCount="indefinite"/>
            <path d="M -160 0 A 160 160 0 0 1 160 0" fill="none" stroke="#39FF14" stroke-width="2" stroke-opacity="0.4" filter="url(#glowEffect)"/>
        </g>
        <g>
            <animateTransform attributeName="transform" type="rotate" from="360" to="0" dur="25s" repeatCount="indefinite"/>
            <path d="M -180 0 A 180 180 0 0 0 180 0" fill="none" stroke="#39FF14" stroke-width="1" stroke-opacity="0.6" stroke-dasharray="10 20"/>
        </g>
    </g>

    <!-- Particles -->
    <g>{particles}</g>

    <!-- Scanning HUD Line -->
    <line x1="0" y1="0" x2="850" y2="0" stroke="#39FF14" stroke-width="1" opacity="0.5" filter="url(#intenseGlow)">
        <animate attributeName="y1" values="0;350;0" dur="10s" repeatCount="indefinite"/>
        <animate attributeName="y2" values="0;350;0" dur="10s" repeatCount="indefinite"/>
    </line>

    <!-- Data Nodes Orbiting -->
    <circle r="4" fill="#ffffff" filter="url(#glowEffect)">
        <animateMotion dur="15s" repeatCount="indefinite">
            <mpath href="#orbitPath"/>
        </animateMotion>
    </circle>
    <circle r="3" fill="#39FF14" filter="url(#glowEffect)">
        <animateMotion dur="20s" repeatCount="indefinite" begin="5s">
            <mpath href="#orbitPath"/>
        </animateMotion>
    </circle>

    <!-- Typography -->
    <g text-anchor="middle">
        <text class="sys-text" x="425" y="150" font-size="12" opacity="0.8">
            <animate attributeName="opacity" values="0.8;0.3;0.8" dur="3s" repeatCount="indefinite"/>
            SYSTEM INITIALIZED
        </text>

        <text class="typewriter" x="425" y="190" font-size="38" filter="url(#glowEffect)">MOHAMED ABDELAZIZ</text>

        <text class="subtitle" x="425" y="220" font-size="14">
            <animate attributeName="opacity" values="1;0.5;1" dur="2s" repeatCount="indefinite"/>
            // SOVEREIGN ARCHITECT
        </text>
    </g>

    <!-- Corner Metrics -->
    <g font-family="'Consolas', monospace" font-size="10" fill="#aaaaaa" opacity="0.7">
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

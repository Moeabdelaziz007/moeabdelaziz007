import os

# Base directory is the parent of the scripts directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Common directories
ASSETS_DIR = os.path.join(PROJECT_ROOT, 'assets')

# Common files
README_PATH = os.path.join(PROJECT_ROOT, 'README.md')

# Telemetry Tags
START_TAG = '<!-- START_LIVE_DATA -->'
END_TAG = '<!-- END_LIVE_DATA -->'

# ---------------------------------------------------------------------------
# Unified Visual Palette: Carbon Fiber + Medium Gray + Neon Green
# Used by every SVG generator to keep the profile visually consistent.
# ---------------------------------------------------------------------------
PALETTE = {
    # Carbon fiber base shades
    "carbon_deep":  "#050505",
    "carbon_mid":   "#0a0a0a",
    "carbon_high":  "#141414",
    # Medium gray scale (labels, secondary text)
    "gray_low":     "#444444",
    "gray_mid":     "#666666",
    "gray_label":   "#888888",
    "gray_text":    "#aaaaaa",
    # Accent neon green (primary highlight)
    "neon":         "#39FF14",
    "neon_soft":    "#7FFF50",
    "neon_glow":    "#39FF14",
    # White (used sparingly, for emphasized values only)
    "white":        "#ffffff",
}

# GitHub profile owner (used by live data generators)
GITHUB_USER = "Moeabdelaziz007"

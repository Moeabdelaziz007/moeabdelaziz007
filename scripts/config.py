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
# AxiomID Visual Palette: OLED Black + Neon Emerald + Electric Blue
# ---------------------------------------------------------------------------
PALETTE = {
    "carbon_deep":  "#050505",
    "carbon_mid":   "#0a0a0a",
    "carbon_high":  "#141414",
    "gray_low":     "#444444",
    "gray_mid":     "#666666",
    "gray_label":   "#888888",
    "gray_text":    "#aaaaaa",
    "neon":         "#39FF14",  # Neon Emerald
    "blue":         "#00d4ff",  # Electric Blue (AxiomID Data)
    "white":        "#ffffff",
}

# GitHub profile owner
GITHUB_USER = "Moeabdelaziz007"

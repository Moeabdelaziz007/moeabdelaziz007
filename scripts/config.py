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
# AxiomID Unified Visual Palette (Compatible with legacy scripts)
# ---------------------------------------------------------------------------
PALETTE = {
    # Semantic Naming (New)
    "background":   "#050505", # OLED Black
    "surface":      "#0a0a0a", # Carbon Mid
    "border":       "#1a1a1a", # Subtle Border
    "text_main":    "#ffffff", # Pure White
    "text_dim":     "#888888", # Label Gray
    "text_mute":    "#444444", # Muted Gray
    "neon":         "#39FF14", # Neon Emerald (Verified/Authority)
    "blue":         "#00d4ff", # Electric Blue (Data/Intelligence)
    "accent":       "#8b5cf6", # Royal Purple (Sovereign Tier)

    # Legacy Compatibility (Old Scripts)
    "carbon_deep":  "#050505",
    "carbon_mid":   "#0a0a0a",
    "carbon_high":  "#141414",
    "gray_low":     "#444444",
    "gray_mid":     "#666666",
    "gray_label":   "#888888",
    "gray_text":    "#aaaaaa",
    "neon_soft":    "#7FFF50",
    "neon_glow":    "#39FF14",
    "white":        "#ffffff",
}

# GitHub profile owner
GITHUB_USER = "Moeabdelaziz007"

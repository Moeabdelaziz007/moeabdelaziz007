"""Tests for scripts/config.py.

This PR introduced the PALETTE dict and GITHUB_USER constant. These tests
verify that the colour scheme and identifiers are correct so that downstream
SVG generators always receive the expected values.
"""

import os

from scripts import config


# ─── PALETTE tests (new in this PR) ──────────────────────────────────────────

EXPECTED_PALETTE_KEYS = {
    "carbon_deep",
    "carbon_mid",
    "carbon_high",
    "gray_low",
    "gray_mid",
    "gray_label",
    "gray_text",
    "neon",
    "neon_soft",
    "neon_glow",
    "white",
}


class TestPalette:
    def test_palette_exists(self):
        """PALETTE must be defined in config."""
        assert hasattr(config, "PALETTE")

    def test_palette_is_dict(self):
        """PALETTE must be a dictionary."""
        assert isinstance(config.PALETTE, dict)

    def test_palette_has_all_expected_keys(self):
        """PALETTE must contain all expected colour role keys."""
        for key in EXPECTED_PALETTE_KEYS:
            assert key in config.PALETTE, f"Missing key: {key!r}"

    def test_palette_no_extra_keys(self):
        """PALETTE must not contain undocumented keys."""
        assert set(config.PALETTE.keys()) == EXPECTED_PALETTE_KEYS

    def test_palette_values_are_strings(self):
        """Every palette value must be a string."""
        for key, value in config.PALETTE.items():
            assert isinstance(value, str), f"PALETTE[{key!r}] is not a string"

    def test_palette_values_are_valid_hex(self):
        """Every palette value must be a valid 7-character hex colour (#RRGGBB)."""
        import re
        hex_pattern = re.compile(r'^#[0-9a-fA-F]{6}$')
        for key, value in config.PALETTE.items():
            assert hex_pattern.match(value), (
                f"PALETTE[{key!r}] = {value!r} is not a valid hex colour"
            )

    # Carbon shades
    def test_carbon_deep_is_darkest(self):
        """carbon_deep must be the darkest carbon shade (#050505)."""
        assert config.PALETTE["carbon_deep"] == "#050505"

    def test_carbon_mid_value(self):
        """carbon_mid must be #0a0a0a."""
        assert config.PALETTE["carbon_mid"] == "#0a0a0a"

    def test_carbon_high_value(self):
        """carbon_high must be #141414."""
        assert config.PALETTE["carbon_high"] == "#141414"

    # Gray scale
    def test_gray_low_value(self):
        """gray_low must be #444444."""
        assert config.PALETTE["gray_low"] == "#444444"

    def test_gray_mid_value(self):
        """gray_mid must be #666666."""
        assert config.PALETTE["gray_mid"] == "#666666"

    def test_gray_label_value(self):
        """gray_label must be #888888 (used for metric labels)."""
        assert config.PALETTE["gray_label"] == "#888888"

    def test_gray_text_value(self):
        """gray_text must be #aaaaaa (used for secondary body text)."""
        assert config.PALETTE["gray_text"] == "#aaaaaa"

    # Neon accent
    def test_neon_is_bright_green(self):
        """neon must be the signature neon green #39FF14."""
        assert config.PALETTE["neon"] == "#39FF14"

    def test_neon_soft_value(self):
        """neon_soft must be #7FFF50 (softer green for active-entities bar)."""
        assert config.PALETTE["neon_soft"] == "#7FFF50"

    def test_neon_glow_matches_neon(self):
        """neon_glow must equal neon (both #39FF14)."""
        assert config.PALETTE["neon_glow"] == config.PALETTE["neon"]

    # White
    def test_white_value(self):
        """white must be #ffffff."""
        assert config.PALETTE["white"] == "#ffffff"

    def test_neon_is_not_white(self):
        """neon accent must be distinct from white."""
        assert config.PALETTE["neon"] != config.PALETTE["white"]

    def test_carbon_shades_are_darker_than_grays(self):
        """All carbon shades must be darker (lower channel sum) than any gray shade."""
        def channel_sum(hex_color):
            h = hex_color.lstrip("#")
            return int(h[0:2], 16) + int(h[2:4], 16) + int(h[4:6], 16)

        carbon_keys = ["carbon_deep", "carbon_mid", "carbon_high"]
        gray_keys = ["gray_low", "gray_mid", "gray_label", "gray_text"]
        max_carbon = max(channel_sum(config.PALETTE[k]) for k in carbon_keys)
        min_gray = min(channel_sum(config.PALETTE[k]) for k in gray_keys)
        assert max_carbon < min_gray, (
            "Carbon shades should be darker than the gray scale values"
        )


# ─── GITHUB_USER tests (new in this PR) ──────────────────────────────────────

class TestGithubUser:
    def test_github_user_exists(self):
        """GITHUB_USER must be defined in config."""
        assert hasattr(config, "GITHUB_USER")

    def test_github_user_is_string(self):
        """GITHUB_USER must be a string."""
        assert isinstance(config.GITHUB_USER, str)

    def test_github_user_is_non_empty(self):
        """GITHUB_USER must not be empty."""
        assert len(config.GITHUB_USER) > 0

    def test_github_user_value(self):
        """GITHUB_USER must be the correct profile username."""
        assert config.GITHUB_USER == "Moeabdelaziz007"

    def test_github_user_no_whitespace(self):
        """GITHUB_USER must not contain leading or trailing whitespace."""
        assert config.GITHUB_USER == config.GITHUB_USER.strip()

    def test_github_user_no_at_prefix(self):
        """GITHUB_USER must not include an '@' prefix."""
        assert not config.GITHUB_USER.startswith("@")


# ─── Path constant smoke-tests ────────────────────────────────────────────────

class TestPathConstants:
    def test_assets_dir_is_absolute(self):
        """ASSETS_DIR must be an absolute path."""
        assert os.path.isabs(config.ASSETS_DIR)

    def test_assets_dir_ends_with_assets(self):
        """ASSETS_DIR must end with 'assets'."""
        assert os.path.basename(config.ASSETS_DIR) == "assets"

    def test_readme_path_is_absolute(self):
        """README_PATH must be an absolute path."""
        assert os.path.isabs(config.README_PATH)

    def test_readme_path_ends_with_readme_md(self):
        """README_PATH must point to README.md."""
        assert config.README_PATH.endswith("README.md")

    def test_start_tag_value(self):
        """START_TAG must match the marker used in README.md."""
        assert config.START_TAG == "<!-- START_LIVE_DATA -->"

    def test_end_tag_value(self):
        """END_TAG must match the marker used in README.md."""
        assert config.END_TAG == "<!-- END_LIVE_DATA -->"

    def test_start_end_tags_are_distinct(self):
        """START_TAG and END_TAG must differ from each other."""
        assert config.START_TAG != config.END_TAG
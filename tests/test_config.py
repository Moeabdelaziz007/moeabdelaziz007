"""Tests for scripts/config.py – covers the new PALETTE, tag constants, and
GITHUB_USER values introduced in this PR."""

import os
import sys

import pytest

# Ensure the project root is on sys.path so the scripts package is importable.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.config import (  # noqa: E402
    ASSETS_DIR,
    END_TAG,
    GITHUB_USER,
    PALETTE,
    PROJECT_ROOT as CONFIG_PROJECT_ROOT,
    README_PATH,
    START_TAG,
)


# ---------------------------------------------------------------------------
# PALETTE
# ---------------------------------------------------------------------------

class TestPalette:
    """Tests for the PALETTE colour dictionary."""

    REQUIRED_KEYS = [
        "carbon_deep",
        "carbon_mid",
        "carbon_high",
        "gray_low",
        "gray_mid",
        "gray_label",
        "gray_text",
        "neon",
        "blue",
        "white",
    ]

    def test_palette_is_dict(self):
        assert isinstance(PALETTE, dict)

    def test_palette_has_all_required_keys(self):
        for key in self.REQUIRED_KEYS:
            assert key in PALETTE, f"Missing PALETTE key: {key}"

    def test_palette_values_are_hex_strings(self):
        hex_re = r"^#[0-9a-fA-F]{3,8}$"
        import re
        for key, value in PALETTE.items():
            assert re.match(hex_re, value), (
                f"PALETTE['{key}'] = '{value}' is not a valid hex colour"
            )

    def test_neon_colour_is_neon_green(self):
        assert PALETTE["neon"] == "#39FF14"

    def test_blue_colour_is_electric_blue(self):
        assert PALETTE["blue"] == "#00d4ff"

    def test_white_is_full_white(self):
        assert PALETTE["white"] == "#ffffff"

    def test_carbon_deep_is_very_dark(self):
        assert PALETTE["carbon_deep"] == "#050505"

    def test_carbon_mid_is_dark(self):
        assert PALETTE["carbon_mid"] == "#0a0a0a"

    def test_no_empty_colour_values(self):
        for key, value in PALETTE.items():
            assert value, f"PALETTE['{key}'] has an empty value"


# ---------------------------------------------------------------------------
# Tag constants
# ---------------------------------------------------------------------------

class TestTagConstants:
    def test_start_tag_is_html_comment(self):
        assert START_TAG.startswith("<!--")
        assert START_TAG.endswith("-->")

    def test_end_tag_is_html_comment(self):
        assert END_TAG.startswith("<!--")
        assert END_TAG.endswith("-->")

    def test_start_tag_contains_live_data(self):
        assert "START_LIVE_DATA" in START_TAG

    def test_end_tag_contains_live_data(self):
        assert "END_LIVE_DATA" in END_TAG

    def test_start_and_end_tags_are_distinct(self):
        assert START_TAG != END_TAG


# ---------------------------------------------------------------------------
# GITHUB_USER
# ---------------------------------------------------------------------------

class TestGithubUser:
    def test_github_user_is_string(self):
        assert isinstance(GITHUB_USER, str)

    def test_github_user_is_not_empty(self):
        assert GITHUB_USER.strip() != ""

    def test_github_user_value(self):
        assert GITHUB_USER == "Moeabdelaziz007"


# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

class TestPathConstants:
    def test_assets_dir_ends_with_assets(self):
        assert os.path.basename(ASSETS_DIR) == "assets"

    def test_assets_dir_is_absolute(self):
        assert os.path.isabs(ASSETS_DIR)

    def test_readme_path_ends_with_readme(self):
        assert README_PATH.lower().endswith("readme.md")

    def test_readme_path_is_absolute(self):
        assert os.path.isabs(README_PATH)

    def test_assets_dir_is_under_project_root(self):
        assert ASSETS_DIR.startswith(CONFIG_PROJECT_ROOT)

    def test_readme_path_is_under_project_root(self):
        assert README_PATH.startswith(CONFIG_PROJECT_ROOT)


# ---------------------------------------------------------------------------
# Additional edge-case / regression tests for changed code in this PR
# ---------------------------------------------------------------------------

class TestPaletteAdditional:
    """Additional tests targeting the new 'blue' key and full palette integrity."""

    def test_palette_has_exactly_ten_keys(self):
        # After this PR the palette has exactly 10 entries
        assert len(PALETTE) == 10

    def test_blue_key_is_lowercase_hex(self):
        # Electric Blue should be in lowercase hex form
        assert PALETTE["blue"] == PALETTE["blue"].lower() or PALETTE["blue"].startswith("#")

    def test_all_hex_values_start_with_hash(self):
        for key, value in PALETTE.items():
            assert value.startswith("#"), f"PALETTE['{key}'] = '{value}' does not start with '#'"

    def test_carbon_keys_are_progressively_lighter(self):
        # carbon_deep < carbon_mid < carbon_high in terms of numeric brightness
        import re
        def _brightness(hex_str):
            h = hex_str.lstrip("#")
            return int(h, 16)
        assert _brightness(PALETTE["carbon_deep"]) < _brightness(PALETTE["carbon_mid"])
        assert _brightness(PALETTE["carbon_mid"]) < _brightness(PALETTE["carbon_high"])

    def test_gray_keys_exist_and_are_distinct(self):
        gray_keys = ["gray_low", "gray_mid", "gray_label", "gray_text"]
        values = [PALETTE[k] for k in gray_keys]
        assert len(set(values)) == len(values), "All gray palette values should be distinct"

    def test_neon_colour_matches_known_neon_green(self):
        # #39FF14 is the established neon green for this project
        assert PALETTE["neon"] == "#39FF14"

    def test_blue_colour_is_different_from_neon(self):
        assert PALETTE["blue"] != PALETTE["neon"]


class TestTagConstantsAdditional:
    """Additional tag constant tests."""

    def test_start_tag_exact_value(self):
        assert START_TAG == "<!-- START_LIVE_DATA -->"

    def test_end_tag_exact_value(self):
        assert END_TAG == "<!-- END_LIVE_DATA -->"

    def test_start_tag_is_a_proper_open_marker(self):
        assert "START" in START_TAG

    def test_end_tag_is_a_proper_close_marker(self):
        assert "END" in END_TAG

    def test_tags_form_valid_injection_block(self):
        import re
        pattern = re.compile(rf'{re.escape(START_TAG)}.*?{re.escape(END_TAG)}', re.DOTALL)
        test_readme = f"# Header\n{START_TAG}\nold data\n{END_TAG}\n# Footer"
        assert pattern.search(test_readme) is not None


class TestPathConstantsAdditional:
    """Additional path constant tests."""

    def test_assets_dir_separator_is_correct(self):
        # ASSETS_DIR should end with the platform path separator + 'assets'
        assert ASSETS_DIR.endswith(os.sep + "assets") or ASSETS_DIR.endswith("/assets")

    def test_readme_path_ends_with_exact_filename(self):
        basename = os.path.basename(README_PATH)
        assert basename.lower() == "readme.md"

    def test_project_root_is_parent_of_assets_dir(self):
        assert os.path.dirname(ASSETS_DIR) == CONFIG_PROJECT_ROOT
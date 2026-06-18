"""Tests for scripts/update_system_status.py – covers the rewritten
AxiomID-focused telemetry functions introduced in this PR.

Tested: generate_markdown_table(), update_telemetry_svg(),
        LIVE_DATA_PATTERN regex, generate_markdown_table output structure.
"""

import os
import re
import sys
import tempfile
from unittest import mock

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.update_system_status import (  # noqa: E402
    LIVE_DATA_PATTERN,
    START_TAG,
    END_TAG,
    generate_markdown_table,
    update_telemetry_svg,
)


# ---------------------------------------------------------------------------
# generate_markdown_table (4-param version: users, agents, txs, date_str)
# ---------------------------------------------------------------------------

class TestGenerateMarkdownTable:
    def test_returns_string(self):
        assert isinstance(generate_markdown_table(100, 50, 10, "2026-01-01"), str)

    def test_contains_l0_identity_row(self):
        result = generate_markdown_table(100, 50, 10, "2026-01-01")
        assert "L0 Identity" in result

    def test_contains_l0_authority_row(self):
        result = generate_markdown_table(100, 50, 10, "2026-01-01")
        assert "L0 Authority" in result

    def test_contains_l0_economy_row(self):
        result = generate_markdown_table(100, 50, 10, "2026-01-01")
        assert "L0 Economy" in result

    def test_contains_l0_network_row(self):
        result = generate_markdown_table(100, 50, 10, "2026-01-01")
        assert "L0 Network" in result

    def test_users_formatted_with_commas(self):
        result = generate_markdown_table(13000, 50, 10, "2026-01-01")
        assert "13,000" in result

    def test_agents_formatted_with_commas(self):
        result = generate_markdown_table(100, 4200, 10, "2026-01-01")
        assert "4,200" in result

    def test_transactions_formatted_with_commas(self):
        result = generate_markdown_table(100, 50, 39000, "2026-01-01")
        assert "39,000" in result

    def test_date_string_appears_in_output(self):
        date = "2026-06-18 18:13:48 UTC"
        result = generate_markdown_table(100, 50, 10, date)
        assert date in result

    def test_verified_status_present(self):
        result = generate_markdown_table(100, 50, 10, "now")
        assert "VERIFIED" in result

    def test_active_status_present(self):
        result = generate_markdown_table(100, 50, 10, "now")
        assert "ACTIVE" in result

    def test_stable_status_present(self):
        result = generate_markdown_table(100, 50, 10, "now")
        assert "STABLE" in result

    def test_synced_status_present(self):
        result = generate_markdown_table(100, 50, 10, "now")
        assert "SYNCED" in result

    def test_zero_values_do_not_raise(self):
        result = generate_markdown_table(0, 0, 0, "N/A")
        assert isinstance(result, str)

    def test_large_numbers_formatted(self):
        result = generate_markdown_table(1_000_000, 999_999, 5_000_000, "N/A")
        assert "1,000,000" in result
        assert "999,999" in result
        assert "5,000,000" in result

    def test_output_contains_markdown_table_separator(self):
        # Markdown tables contain " :--- " alignment markers
        result = generate_markdown_table(100, 50, 10, "now")
        assert ":---" in result

    def test_output_wrapped_in_div_align_center(self):
        result = generate_markdown_table(100, 50, 10, "now")
        assert 'align="center"' in result


# ---------------------------------------------------------------------------
# TAG constants and LIVE_DATA_PATTERN
# ---------------------------------------------------------------------------

class TestLiveDataPattern:
    def test_start_tag_defined(self):
        assert START_TAG == "<!-- START_LIVE_DATA -->"

    def test_end_tag_defined(self):
        assert END_TAG == "<!-- END_LIVE_DATA -->"

    def test_pattern_matches_simple_block(self):
        text = f"{START_TAG}\nsome content\n{END_TAG}"
        assert LIVE_DATA_PATTERN.search(text) is not None

    def test_pattern_matches_multiline_block(self):
        text = f"{START_TAG}\nline1\nline2\nline3\n{END_TAG}"
        assert LIVE_DATA_PATTERN.search(text) is not None

    def test_pattern_does_not_match_missing_start_tag(self):
        text = f"some content\n{END_TAG}"
        assert LIVE_DATA_PATTERN.search(text) is None

    def test_pattern_does_not_match_missing_end_tag(self):
        text = f"{START_TAG}\nsome content"
        assert LIVE_DATA_PATTERN.search(text) is None

    def test_pattern_replacement_works(self):
        text = f"before\n{START_TAG}\nold content\n{END_TAG}\nafter"
        new_block = f"{START_TAG}\nnew content\n{END_TAG}"
        result = LIVE_DATA_PATTERN.sub(new_block, text)
        assert "old content" not in result
        assert "new content" in result
        assert "before" in result
        assert "after" in result


# ---------------------------------------------------------------------------
# update_telemetry_svg()
# ---------------------------------------------------------------------------

class TestUpdateTelemetrySvg:
    def test_creates_telemetry_svg_file(self, tmp_path):
        """update_telemetry_svg() should write telemetry.svg to ASSETS_DIR."""
        with mock.patch("scripts.update_system_status.ASSETS_DIR", str(tmp_path)):
            update_telemetry_svg()
        svg_file = tmp_path / "telemetry.svg"
        assert svg_file.exists(), "telemetry.svg was not created"

    def test_telemetry_svg_starts_with_svg_tag(self, tmp_path):
        with mock.patch("scripts.update_system_status.ASSETS_DIR", str(tmp_path)):
            update_telemetry_svg()
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert content.strip().startswith("<svg")

    def test_telemetry_svg_ends_with_closing_tag(self, tmp_path):
        with mock.patch("scripts.update_system_status.ASSETS_DIR", str(tmp_path)):
            update_telemetry_svg()
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert content.strip().endswith("</svg>")

    def test_telemetry_svg_contains_citizens_label(self, tmp_path):
        with mock.patch("scripts.update_system_status.ASSETS_DIR", str(tmp_path)):
            update_telemetry_svg()
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert "CITIZENS" in content

    def test_telemetry_svg_contains_agents_label(self, tmp_path):
        with mock.patch("scripts.update_system_status.ASSETS_DIR", str(tmp_path)):
            update_telemetry_svg()
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert "AGENTS" in content

    def test_telemetry_svg_contains_transfers_label(self, tmp_path):
        with mock.patch("scripts.update_system_status.ASSETS_DIR", str(tmp_path)):
            update_telemetry_svg()
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert "TRANSFERS" in content

    def test_telemetry_svg_contains_root_auth_label(self, tmp_path):
        with mock.patch("scripts.update_system_status.ASSETS_DIR", str(tmp_path)):
            update_telemetry_svg()
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert "ROOT.AUTH" in content

    def test_telemetry_svg_contains_neon_colour(self, tmp_path):
        with mock.patch("scripts.update_system_status.ASSETS_DIR", str(tmp_path)):
            update_telemetry_svg()
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert "#39FF14" in content

    def test_telemetry_svg_contains_date_string(self, tmp_path):
        with mock.patch("scripts.update_system_status.ASSETS_DIR", str(tmp_path)):
            update_telemetry_svg()
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        # Should contain a UTC timestamp pattern like "2026-06-18 ..."
        assert re.search(r"\d{4}-\d{2}-\d{2}", content)

    def test_telemetry_svg_contains_axiomid_branding(self, tmp_path):
        with mock.patch("scripts.update_system_status.ASSETS_DIR", str(tmp_path)):
            update_telemetry_svg()
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert "AXIOMID" in content

    def test_telemetry_svg_contains_animate_element(self, tmp_path):
        with mock.patch("scripts.update_system_status.ASSETS_DIR", str(tmp_path)):
            update_telemetry_svg()
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert "<animateTransform" in content or "<animate" in content

    def test_telemetry_svg_contains_hexagon_polygons(self, tmp_path):
        """The function generates ~30 decorative hexagon polygons."""
        with mock.patch("scripts.update_system_status.ASSETS_DIR", str(tmp_path)):
            update_telemetry_svg()
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert "<polygon" in content

    def test_update_telemetry_svg_creates_dir_if_missing(self, tmp_path):
        """ASSETS_DIR should be created with makedirs when it does not exist."""
        assets = tmp_path / "new_assets"
        with mock.patch("scripts.update_system_status.ASSETS_DIR", str(assets)):
            update_telemetry_svg()
        assert (assets / "telemetry.svg").exists()

    def test_update_called_twice_overwrites_file(self, tmp_path):
        """Calling update_telemetry_svg() twice should not raise and should
        overwrite the previous file."""
        with mock.patch("scripts.update_system_status.ASSETS_DIR", str(tmp_path)):
            update_telemetry_svg()
            first_size = (tmp_path / "telemetry.svg").stat().st_size
            update_telemetry_svg()
            second_size = (tmp_path / "telemetry.svg").stat().st_size
        # Both should be valid non-zero SVGs
        assert first_size > 0
        assert second_size > 0

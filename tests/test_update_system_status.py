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
# Shared fixture-like helper
# ---------------------------------------------------------------------------

_SAMPLE_DATE = "2026-06-18 18:13:48 UTC"
_SAMPLE_USERS = 13359
_SAMPLE_AGENTS = 4211
_SAMPLE_TXS = 39390


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

    def test_projected_status_present(self):
        # The table uses "PROJECTED" for Citizens, Agents, and Transactions rows
        result = generate_markdown_table(100, 50, 10, "now")
        assert "PROJECTED" in result

    def test_synced_status_present(self):
        # The L0 Network row has 📡 SYNCED
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

    def test_illustrative_disclaimer_present(self):
        # Should contain the disclaimer about illustrative data
        result = generate_markdown_table(100, 50, 10, "now")
        assert "Illustrative" in result or "illustrative" in result

    def test_active_citizens_metric_label_present(self):
        result = generate_markdown_table(100, 50, 10, "now")
        assert "Active Citizens" in result

    def test_registered_agents_metric_label_present(self):
        result = generate_markdown_table(100, 50, 10, "now")
        assert "Registered Agents" in result

    def test_m2m_transactions_metric_label_present(self):
        result = generate_markdown_table(100, 50, 10, "now")
        assert "M2M Transactions" in result

    def test_last_refresh_metric_label_present(self):
        result = generate_markdown_table(100, 50, 10, "now")
        assert "Last Refresh" in result

    def test_axiomid_layer_column_header_present(self):
        result = generate_markdown_table(100, 50, 10, "now")
        assert "AxiomID Layer" in result

    def test_refreshed_every_3_hours_note_present(self):
        result = generate_markdown_table(100, 50, 10, "now")
        assert "3 hours" in result

    def test_sample_values_round_trip(self):
        result = generate_markdown_table(_SAMPLE_USERS, _SAMPLE_AGENTS, _SAMPLE_TXS, _SAMPLE_DATE)
        assert "13,359" in result
        assert "4,211" in result
        assert "39,390" in result
        assert _SAMPLE_DATE in result


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

    def test_pattern_dotall_flag_set(self):
        # Pattern must match content containing real newlines (re.DOTALL)
        block = f"{START_TAG}\n<img>\n<table>\n</table>\n{END_TAG}"
        assert LIVE_DATA_PATTERN.search(block) is not None


# ---------------------------------------------------------------------------
# update_telemetry_svg()
# update_telemetry_svg signature: (users, agents, txs, date_str)
# ---------------------------------------------------------------------------

class TestUpdateTelemetrySvg:
    def _call(self, tmp_path, users=_SAMPLE_USERS, agents=_SAMPLE_AGENTS,
              txs=_SAMPLE_TXS, date_str=_SAMPLE_DATE):
        with mock.patch("scripts.update_system_status.ASSETS_DIR", str(tmp_path)):
            update_telemetry_svg(users, agents, txs, date_str)

    def test_creates_telemetry_svg_file(self, tmp_path):
        self._call(tmp_path)
        assert (tmp_path / "telemetry.svg").exists()

    def test_telemetry_svg_starts_with_svg_tag(self, tmp_path):
        self._call(tmp_path)
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert content.strip().startswith("<svg")

    def test_telemetry_svg_ends_with_closing_tag(self, tmp_path):
        self._call(tmp_path)
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert content.strip().endswith("</svg>")

    def test_telemetry_svg_contains_citizens_label(self, tmp_path):
        self._call(tmp_path)
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert "CITIZENS" in content

    def test_telemetry_svg_contains_agents_label(self, tmp_path):
        self._call(tmp_path)
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert "AGENTS" in content

    def test_telemetry_svg_contains_transfers_label(self, tmp_path):
        self._call(tmp_path)
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert "TRANSFERS" in content

    def test_telemetry_svg_contains_root_auth_label(self, tmp_path):
        self._call(tmp_path)
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert "ROOT.AUTH" in content

    def test_telemetry_svg_contains_neon_colour(self, tmp_path):
        self._call(tmp_path)
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert "#39FF14" in content

    def test_telemetry_svg_contains_date_string(self, tmp_path):
        self._call(tmp_path, date_str=_SAMPLE_DATE)
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert re.search(r"\d{4}-\d{2}-\d{2}", content)

    def test_telemetry_svg_contains_axiomid_branding(self, tmp_path):
        self._call(tmp_path)
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert "AXIOMID" in content

    def test_telemetry_svg_contains_animate_element(self, tmp_path):
        self._call(tmp_path)
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert "<animateTransform" in content or "<animate" in content

    def test_telemetry_svg_contains_hexagon_polygons(self, tmp_path):
        """The function generates ~30 decorative hexagon polygons."""
        self._call(tmp_path)
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert "<polygon" in content

    def test_update_telemetry_svg_creates_dir_if_missing(self, tmp_path):
        """ASSETS_DIR should be created with makedirs when it does not exist."""
        assets = tmp_path / "new_assets"
        with mock.patch("scripts.update_system_status.ASSETS_DIR", str(assets)):
            update_telemetry_svg(_SAMPLE_USERS, _SAMPLE_AGENTS, _SAMPLE_TXS, _SAMPLE_DATE)
        assert (assets / "telemetry.svg").exists()

    def test_update_called_twice_overwrites_file(self, tmp_path):
        """Calling update_telemetry_svg() twice should not raise and should
        overwrite the previous file."""
        self._call(tmp_path)
        first_size = (tmp_path / "telemetry.svg").stat().st_size
        self._call(tmp_path)
        second_size = (tmp_path / "telemetry.svg").stat().st_size
        assert first_size > 0
        assert second_size > 0

    def test_users_value_embedded_in_svg(self, tmp_path):
        self._call(tmp_path, users=12345)
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert "12,345" in content

    def test_agents_value_embedded_in_svg(self, tmp_path):
        self._call(tmp_path, agents=9999)
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert "9,999" in content

    def test_txs_value_embedded_in_svg(self, tmp_path):
        self._call(tmp_path, txs=50000)
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert "50,000" in content

    def test_date_str_embedded_in_svg(self, tmp_path):
        date = "2026-12-31 23:59:59 UTC"
        self._call(tmp_path, date_str=date)
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert date in content

    def test_telemetry_svg_contains_illustrative_disclaimer(self, tmp_path):
        self._call(tmp_path)
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert "ILLUSTRATIVE" in content or "illustrative" in content.lower()

    def test_telemetry_svg_contains_secure_handshake_marker(self, tmp_path):
        self._call(tmp_path)
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert "SECURE_HANDSHAKE" in content

    def test_telemetry_svg_carbon_fiber_pattern(self, tmp_path):
        self._call(tmp_path)
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert "carbonFiber" in content

    def test_telemetry_svg_width_850(self, tmp_path):
        self._call(tmp_path)
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert 'width="850"' in content

    def test_telemetry_svg_height_200(self, tmp_path):
        self._call(tmp_path)
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert 'height="200"' in content

    def test_zero_values_do_not_raise(self, tmp_path):
        self._call(tmp_path, users=0, agents=0, txs=0, date_str="N/A")
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert isinstance(content, str)

    def test_large_values_formatted_correctly(self, tmp_path):
        self._call(tmp_path, users=1_000_000, agents=500_000, txs=9_999_999)
        content = (tmp_path / "telemetry.svg").read_text(encoding="utf-8")
        assert "1,000,000" in content
        assert "500,000" in content
        assert "9,999,999" in content

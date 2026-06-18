import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.generate_aix_dashboard import (  # noqa: E402
    generate_markdown_table,
    generate_svg_dashboard,
)


def test_generate_markdown_table_basic():
    """Test with normal inputs for AxiomID."""
    users = 13000
    agents = 4000
    xp = 1000000
    txs = 30000
    last_ping = "2026-06-18 12:00:00 UTC"

    result = generate_markdown_table(users, agents, xp, txs, last_ping)
    assert "Active Users" in result
    assert "13,000" in result
    assert "4,000" in result
    assert "1,000,000" in result
    assert "30,000" in result
    assert last_ping in result

def test_generate_markdown_table_formatting():
    """Test number formatting."""
    users = 1000
    agents = 500
    xp = 1000000
    txs = 2000
    last_ping = "N/A"

    result = generate_markdown_table(users, agents, xp, txs, last_ping)
    assert "1,000" in result
    assert "500" in result
    assert "1,000,000" in result
    assert "2,000" in result


# ---------------------------------------------------------------------------
# generate_markdown_table – additional / edge-case coverage
# ---------------------------------------------------------------------------

def test_generate_markdown_table_contains_registered_agents_label():
    result = generate_markdown_table(100, 50, 999, 10, "2026-01-01 00:00:00 UTC")
    assert "Registered Agents" in result

def test_generate_markdown_table_contains_total_xp_label():
    result = generate_markdown_table(100, 50, 999, 10, "2026-01-01 00:00:00 UTC")
    assert "Total XP" in result

def test_generate_markdown_table_contains_total_transactions_label():
    result = generate_markdown_table(100, 50, 999, 10, "2026-01-01 00:00:00 UTC")
    assert "Total Transactions" in result

def test_generate_markdown_table_contains_last_sync_label():
    result = generate_markdown_table(100, 50, 999, 10, "2026-01-01 00:00:00 UTC")
    assert "Last Sync" in result

def test_generate_markdown_table_xp_formatted_with_xp_suffix():
    result = generate_markdown_table(100, 50, 500000, 10, "2026-01-01 00:00:00 UTC")
    assert "500,000 XP" in result

def test_generate_markdown_table_zero_values():
    result = generate_markdown_table(0, 0, 0, 0, "N/A")
    assert "0" in result

def test_generate_markdown_table_large_numbers():
    result = generate_markdown_table(1_000_000, 500_000, 9_999_999, 1_000_000, "N/A")
    assert "1,000,000" in result
    assert "9,999,999" in result

def test_generate_markdown_table_returns_string():
    result = generate_markdown_table(1, 1, 1, 1, "now")
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# generate_svg_dashboard
# ---------------------------------------------------------------------------

class TestGenerateSvgDashboard:
    DEFAULTS = dict(
        users=13000,
        agents=4000,
        xp=1000000,
        txs=30000,
        last_ping="2026-06-18 12:00:00 UTC",
    )

    def _svg(self, **kwargs):
        params = {**self.DEFAULTS, **kwargs}
        return generate_svg_dashboard(**params)

    def test_returns_string(self):
        assert isinstance(self._svg(), str)

    def test_starts_with_svg_tag(self):
        assert self._svg().strip().startswith("<svg")

    def test_ends_with_closing_svg_tag(self):
        assert self._svg().strip().endswith("</svg>")

    def test_contains_width_800(self):
        assert 'width="800"' in self._svg()

    def test_active_users_label_present(self):
        assert "ACTIVE USERS" in self._svg()

    def test_registered_agents_label_present(self):
        assert "REG. AGENTS" in self._svg()

    def test_total_xp_label_present(self):
        assert "TOTAL XP" in self._svg()

    def test_transactions_label_present(self):
        assert "TRANSACTIONS" in self._svg()

    def test_users_value_appears_formatted(self):
        svg = self._svg(users=13000)
        assert "13,000" in svg

    def test_agents_value_appears_formatted(self):
        svg = self._svg(agents=4000)
        assert "4,000" in svg

    def test_xp_value_appears_formatted(self):
        svg = self._svg(xp=1000000)
        assert "1,000,000" in svg

    def test_txs_value_appears_formatted(self):
        svg = self._svg(txs=30000)
        assert "30,000" in svg

    def test_last_ping_appears_in_svg(self):
        svg = self._svg(last_ping="2026-06-18 12:00:00 UTC")
        assert "2026-06-18 12:00:00 UTC" in svg

    def test_root_authority_operational_text_present(self):
        assert "ROOT AUTHORITY OPERATIONAL" in self._svg()

    def test_axiomid_network_telemetry_heading_present(self):
        assert "AXIOMID NETWORK TELEMETRY" in self._svg()

    def test_neon_colour_in_svg(self):
        assert "#39FF14" in self._svg()

    def test_animate_element_present_for_pulse(self):
        assert "<animate" in self._svg()

    def test_zero_values_do_not_raise(self):
        svg = self._svg(users=0, agents=0, xp=0, txs=0)
        assert isinstance(svg, str)

    def test_large_values_formatted_correctly(self):
        svg = self._svg(users=1_000_000, agents=500_000, xp=9_999_999, txs=1_000_000)
        assert "1,000,000" in svg

    def test_svg_contains_defs_section(self):
        assert "<defs>" in self._svg()

    def test_svg_contains_filter_for_text_glow(self):
        svg = self._svg()
        assert "textGlow" in svg

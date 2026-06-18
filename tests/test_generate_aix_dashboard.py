import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# scripts/ must be on sys.path so that `from config import …` inside the module resolves
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

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

def test_generate_markdown_table_contains_last_refresh_label():
    """The table uses 'Last Refresh' (not 'Last Sync') per the current implementation."""
    result = generate_markdown_table(100, 50, 999, 10, "2026-01-01 00:00:00 UTC")
    assert "Last Refresh" in result

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

def test_generate_markdown_table_contains_projected_status():
    """PR changed telemetry from live data to illustrative projections;
    all data-row status cells should say PROJECTED."""
    result = generate_markdown_table(100, 50, 999, 10, "2026-01-01 00:00:00 UTC")
    assert "PROJECTED" in result

def test_generate_markdown_table_contains_synced_status():
    """The Last Refresh row should carry a SYNCED status."""
    result = generate_markdown_table(100, 50, 999, 10, "2026-01-01 00:00:00 UTC")
    assert "SYNCED" in result

def test_generate_markdown_table_contains_illustrative_disclaimer():
    """The table should include a note that values are illustrative targets."""
    result = generate_markdown_table(100, 50, 999, 10, "2026-01-01 00:00:00 UTC")
    assert "llustrative" in result  # catches both 'Illustrative' and 'illustrative'

def test_generate_markdown_table_contains_div_wrapper():
    """Output must be wrapped in a centred <div> for GitHub Markdown rendering."""
    result = generate_markdown_table(100, 50, 999, 10, "2026-01-01 00:00:00 UTC")
    assert "<div" in result and "</div>" in result

def test_generate_markdown_table_ping_value_appears_verbatim():
    """The exact last_ping string (including time and UTC) must appear unchanged."""
    ping = "2026-06-18 18:13:48 UTC"
    result = generate_markdown_table(100, 50, 999, 10, ping)
    assert ping in result


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

    def test_axiomid_projected_targets_heading_present(self):
        """The SVG heading reads 'AXIOMID PROJECTED TARGETS (ILLUSTRATIVE)'."""
        assert "AXIOMID PROJECTED TARGETS (ILLUSTRATIVE)" in self._svg()

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

    def test_svg_contains_separator_line(self):
        """A horizontal separator line between title and metrics is expected."""
        svg = self._svg()
        assert "<line" in svg

    def test_svg_height_is_150(self):
        """The SVG should have a fixed height of 150px."""
        svg = self._svg()
        assert 'height="150"' in svg

    def test_svg_contains_background_rect(self):
        """The SVG must include a background rect element."""
        svg = self._svg()
        assert "<rect" in svg

    def test_svg_has_viewbox_attribute(self):
        """SVG must declare a viewBox for proper scaling."""
        svg = self._svg()
        assert "viewBox" in svg

    def test_svg_xmlns_declared(self):
        """SVG must include xmlns for valid XML."""
        svg = self._svg()
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg

    def test_svg_status_circle_at_correct_position(self):
        """The pulse status circle should be near the bottom-right (cy=115)."""
        svg = self._svg()
        assert 'cy="115"' in svg

    def test_svg_metrics_section_translate_present(self):
        """Metrics section is positioned via translate(30, 70)."""
        svg = self._svg()
        assert "translate(30, 70)" in svg

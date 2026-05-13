import re
import os
import tempfile
import unittest.mock as mock

from scripts.generate_aix_dashboard import generate_markdown_table, generate_svg_dashboard

def test_generate_markdown_table_basic():
    """Test with normal inputs."""
    visitors = 5000
    agents = 150
    uptime = 300
    last_ping = "2023-10-27 12:00:00 UTC"

    result = generate_markdown_table(visitors, agents, uptime, last_ping)

    assert f"`{uptime} days`" in result
    assert f"`{agents}`" in result
    assert f"`{visitors} ops`" in result
    assert f"`{last_ping}`" in result
    assert "| Metric | Value | Status |" in result
    assert "🟢 OPERATIONAL" in result
    assert "🟢 ONLINE" in result
    assert "🟢 STABLE" in result
    assert "🔒 VERIFIED" in result

def test_generate_markdown_table_large_values():
    """Test with large numeric inputs."""
    visitors = 1000000
    agents = 5000
    uptime = 9999
    last_ping = "2023-10-27 12:00:00 UTC"

    result = generate_markdown_table(visitors, agents, uptime, last_ping)

    assert f"`{uptime} days`" in result
    assert f"`{agents}`" in result
    assert f"`{visitors} ops`" in result

def test_generate_markdown_table_empty_ping():
    """Test with empty last_ping string."""
    visitors = 0
    agents = 0
    uptime = 0
    last_ping = ""

    result = generate_markdown_table(visitors, agents, uptime, last_ping)

    assert "| **Last Sync** | `` | 🔒 VERIFIED |" in result

def test_generate_markdown_table_special_chars_ping():
    """Test with special characters in last_ping."""
    visitors = 10
    agents = 5
    uptime = 1
    last_ping = "<b>bold</b> & <script>alert(1)</script>"

    result = generate_markdown_table(visitors, agents, uptime, last_ping)

    assert f"`{last_ping}`" in result


# ─── Tests for generate_svg_dashboard (new in this PR) ────────────────────────

def test_generate_svg_dashboard_returns_string():
    """generate_svg_dashboard should return a non-empty string."""
    result = generate_svg_dashboard(8000, 200, 400, "2026-01-01 00:00:00 UTC")
    assert isinstance(result, str)
    assert len(result) > 0


def test_generate_svg_dashboard_is_valid_svg():
    """Output must begin with an <svg> tag and close it."""
    result = generate_svg_dashboard(8000, 200, 400, "2026-01-01 00:00:00 UTC")
    assert result.strip().startswith("<svg")
    assert "</svg>" in result


def test_generate_svg_dashboard_embeds_visitors():
    """visitors value must appear in the SVG output."""
    visitors = 11247
    result = generate_svg_dashboard(visitors, 182, 493, "2026-05-13 01:20:18 UTC")
    assert str(visitors) in result


def test_generate_svg_dashboard_embeds_agents():
    """agents value must appear in the SVG output."""
    agents = 182
    result = generate_svg_dashboard(11247, agents, 493, "2026-05-13 01:20:18 UTC")
    assert str(agents) in result


def test_generate_svg_dashboard_embeds_uptime():
    """uptime value must appear in the SVG output."""
    uptime = 493
    result = generate_svg_dashboard(11247, 182, uptime, "2026-05-13 01:20:18 UTC")
    assert str(uptime) in result


def test_generate_svg_dashboard_embeds_last_ping():
    """last_ping timestamp must appear in the SVG output."""
    last_ping = "2026-05-13 01:20:18 UTC"
    result = generate_svg_dashboard(11247, 182, 493, last_ping)
    assert last_ping in result


def test_generate_svg_dashboard_neon_green_accent():
    """SVG must use neon green (#39FF14) as the primary accent color."""
    result = generate_svg_dashboard(8000, 200, 400, "2026-01-01 00:00:00 UTC")
    assert "#39FF14" in result


def test_generate_svg_dashboard_neon_soft_accent():
    """SVG must use neon soft green (#7FFF50) for active-entities bar."""
    result = generate_svg_dashboard(8000, 200, 400, "2026-01-01 00:00:00 UTC")
    assert "#7FFF50" in result


def test_generate_svg_dashboard_no_legacy_white_accent():
    """Old design used white (#ffffff) as the metric bar color; new design uses neon green."""
    result = generate_svg_dashboard(8000, 200, 400, "2026-01-01 00:00:00 UTC")
    # The progress bar fills must be neon green, not pure white
    # White may still appear for text, but the bar fills must be neon.
    bar_fill_pattern = re.compile(r'<rect[^>]*height="2"[^>]*fill="([^"]+)"')
    bar_fills = bar_fill_pattern.findall(result)
    # Should only contain neon-green family colors and dark background fills
    assert "#ffffff" not in [f.lower() for f in bar_fills], (
        "Progress bar fills should not use #ffffff in new design"
    )


def test_generate_svg_dashboard_carbon_fiber_pattern():
    """SVG must include the carbon-fiber background pattern definition."""
    result = generate_svg_dashboard(8000, 200, 400, "2026-01-01 00:00:00 UTC")
    assert 'id="cfDash"' in result


def test_generate_svg_dashboard_topbar_gradient():
    """SVG must include the topBar linear gradient definition."""
    result = generate_svg_dashboard(8000, 200, 400, "2026-01-01 00:00:00 UTC")
    assert 'id="topBar"' in result


def test_generate_svg_dashboard_text_glow_filter():
    """SVG must include the textGlow filter for value readability."""
    result = generate_svg_dashboard(8000, 200, 400, "2026-01-01 00:00:00 UTC")
    assert 'id="textGlow"' in result


def test_generate_svg_dashboard_section_labels():
    """SVG must contain all three section labels: CONTINUITY, ACTIVE ENTITIES, NETWORK LOAD."""
    result = generate_svg_dashboard(8000, 200, 400, "2026-01-01 00:00:00 UTC")
    assert "CONTINUITY" in result
    assert "ACTIVE ENTITIES" in result
    assert "NETWORK LOAD" in result


def test_generate_svg_dashboard_status_indicator():
    """SVG must include the pulsing status indicator and ALL SYSTEMS NORMAL text."""
    result = generate_svg_dashboard(8000, 200, 400, "2026-01-01 00:00:00 UTC")
    assert "ALL SYSTEMS NORMAL" in result
    # Animated pulsing circle
    assert 'repeatCount="indefinite"' in result


def test_generate_svg_dashboard_system_telemetry_title():
    """SVG must display SYSTEM TELEMETRY as the header title."""
    result = generate_svg_dashboard(8000, 200, 400, "2026-01-01 00:00:00 UTC")
    assert "SYSTEM TELEMETRY" in result


def test_generate_svg_dashboard_monospace_font():
    """SVG must use monospace fonts (Consolas/Fira Code) as per new design."""
    result = generate_svg_dashboard(8000, 200, 400, "2026-01-01 00:00:00 UTC")
    assert "Consolas" in result or "Fira Code" in result


def test_generate_svg_dashboard_dimensions():
    """SVG must have width=800 and height=150."""
    result = generate_svg_dashboard(8000, 200, 400, "2026-01-01 00:00:00 UTC")
    assert 'width="800"' in result
    assert 'height="150"' in result


def test_generate_svg_dashboard_uptime_unit_label():
    """Uptime value must be followed by a 'd' unit label in neon green."""
    result = generate_svg_dashboard(8000, 200, 400, "2026-01-01 00:00:00 UTC")
    # The tspan for the 'd' unit marker must use neon green
    assert 'fill="#39FF14">d</tspan>' in result


def test_generate_svg_dashboard_zero_values():
    """generate_svg_dashboard must handle zero values without errors."""
    result = generate_svg_dashboard(0, 0, 0, "2026-01-01 00:00:00 UTC")
    assert isinstance(result, str)
    assert "0" in result


def test_generate_svg_dashboard_large_values():
    """generate_svg_dashboard must handle large metric values without truncation."""
    result = generate_svg_dashboard(999999, 9999, 9999, "2026-01-01 00:00:00 UTC")
    assert "999999" in result
    assert "9999" in result

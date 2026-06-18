import re

import scripts.generate_aix_dashboard as aix_mod
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


# --------------------------------------------------------------------------- #
# LIVE_DATA_PATTERN — verifies the PR change (removed local tag overrides)
# --------------------------------------------------------------------------- #

def test_live_data_pattern_uses_config_tags():
    """LIVE_DATA_PATTERN must be compiled from the config-imported tags."""
    from scripts.config import START_TAG, END_TAG
    sample = f"{START_TAG}\nsome content\n{END_TAG}"
    assert aix_mod.LIVE_DATA_PATTERN.search(sample) is not None


def test_live_data_pattern_does_not_match_without_tags():
    content = "no tags here at all"
    assert aix_mod.LIVE_DATA_PATTERN.search(content) is None


def test_live_data_pattern_matches_multiline_content():
    from scripts.config import START_TAG, END_TAG
    sample = f"{START_TAG}\nline1\nline2\nline3\n{END_TAG}"
    assert aix_mod.LIVE_DATA_PATTERN.search(sample) is not None


def test_live_data_pattern_replaces_correctly():
    from scripts.config import START_TAG, END_TAG
    original = f"before\n{START_TAG}\nold content\n{END_TAG}\nafter"
    new_content = aix_mod.LIVE_DATA_PATTERN.sub(f"{START_TAG}\nnew\n{END_TAG}", original)
    assert "old content" not in new_content
    assert "new" in new_content
    assert "before" in new_content
    assert "after" in new_content


# --------------------------------------------------------------------------- #
# generate_svg_dashboard()
# --------------------------------------------------------------------------- #

def test_generate_svg_dashboard_returns_svg():
    result = generate_svg_dashboard(1000, 50, 200, "2024-01-01 00:00:00 UTC")
    assert result.strip().startswith("<svg")
    assert "</svg>" in result


def test_generate_svg_dashboard_embeds_values():
    visitors, agents, uptime, last_ping = 7654, 123, 365, "2024-06-01 12:00:00 UTC"
    result = generate_svg_dashboard(visitors, agents, uptime, last_ping)
    assert str(visitors) in result
    assert str(agents) in result
    assert str(uptime) in result
    assert last_ping in result


def test_generate_svg_dashboard_zero_values():
    result = generate_svg_dashboard(0, 0, 0, "")
    assert "<svg" in result


def test_generate_svg_dashboard_large_values():
    result = generate_svg_dashboard(999999, 9999, 9999, "2099-12-31 23:59:59 UTC")
    assert "999999" in result
    assert "9999" in result


def test_generate_svg_dashboard_valid_xml_structure():
    """SVG output should have exactly one opening and one closing svg tag."""
    result = generate_svg_dashboard(100, 10, 50, "ping")
    assert result.count("<svg") == 1
    assert result.count("</svg>") == 1

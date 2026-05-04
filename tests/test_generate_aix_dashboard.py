import pytest
import sys
import os

# Add the project root to sys.path to allow importing from scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.generate_aix_dashboard import generate_svg_dashboard, generate_markdown_table

def test_generate_svg_dashboard():
    visitors = 1234
    agents = 56
    uptime = 78
    last_ping = "2023-10-27 12:00:00 UTC"

    svg = generate_svg_dashboard(visitors, agents, uptime, last_ping)

    assert str(visitors) in svg
    assert str(agents) in svg
    assert str(uptime) in svg
    assert last_ping in svg
    assert "<svg" in svg
    assert "</svg>" in svg
    assert "SYSTEM TELEMETRY" in svg

def test_generate_markdown_table():
    visitors = 1234
    agents = 56
    uptime = 78
    last_ping = "2023-10-27 12:00:00 UTC"

    table = generate_markdown_table(visitors, agents, uptime, last_ping)

    assert str(visitors) in table
    assert str(agents) in table
    assert str(uptime) in table
    assert last_ping in table
    assert "| Metric | Value | Status |" in table
    assert "🟢 OPERATIONAL" in table

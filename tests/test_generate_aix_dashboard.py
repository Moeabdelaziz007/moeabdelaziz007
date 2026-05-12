from scripts.generate_aix_dashboard import generate_markdown_table

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

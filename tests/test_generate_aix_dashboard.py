from scripts.generate_aix_dashboard import generate_markdown_table

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

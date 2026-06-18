from scripts.generate_agents_inventory import classify, select_top_repos, truncate, escape


# --------------------------------------------------------------------------- #
# classify()
# --------------------------------------------------------------------------- #

class TestClassify:
    def test_aix_ecosystem_by_name(self):
        repo = {"name": "iqra-os", "description": None, "topics": []}
        assert classify(repo) == "AIX Ecosystem"

    def test_aix_ecosystem_by_description(self):
        repo = {"name": "foo", "description": "This is the aix operating system", "topics": []}
        assert classify(repo) == "AIX Ecosystem"

    def test_aix_ecosystem_by_topic(self):
        repo = {"name": "foo", "description": None, "topics": ["aura", "ml"]}
        assert classify(repo) == "AIX Ecosystem"

    def test_agents_mcp_by_name(self):
        repo = {"name": "my-agent-runner", "description": None, "topics": []}
        assert classify(repo) == "Agents & MCP"

    def test_agents_mcp_mcp_keyword(self):
        repo = {"name": "foo", "description": "A model context protocol server", "topics": []}
        assert classify(repo) in ("Agents & MCP",)

    def test_voice_multimodal(self):
        repo = {"name": "speech-to-text", "description": None, "topics": []}
        assert classify(repo) == "Voice & Multimodal"

    def test_os_platforms(self):
        repo = {"name": "jarhe-runtime", "description": None, "topics": []}
        assert classify(repo) == "OS & Platforms"

    def test_trading_quant(self):
        repo = {"name": "quant-strategy", "description": None, "topics": []}
        assert classify(repo) == "Trading & Quant"

    def test_fallback_to_other(self):
        repo = {"name": "random-utils", "description": "Some random utility library", "topics": []}
        assert classify(repo) == "Other"

    def test_none_values_handled(self):
        repo = {"name": None, "description": None, "topics": None}
        # Should not raise; no patterns match None text
        result = classify(repo)
        assert result == "Other"

    def test_empty_repo(self):
        assert classify({}) == "Other"

    def test_case_insensitive_matching(self):
        repo = {"name": "AIX-Format", "description": None, "topics": []}
        assert classify(repo) == "AIX Ecosystem"

    def test_first_matching_category_wins(self):
        # "aix" matches AIX Ecosystem; "agent" matches Agents & MCP
        # AIX Ecosystem is listed first so it should win
        repo = {"name": "aix-agent", "description": None, "topics": []}
        assert classify(repo) == "AIX Ecosystem"


# --------------------------------------------------------------------------- #
# select_top_repos()
# --------------------------------------------------------------------------- #

class TestSelectTopRepos:
    def _make_repo(self, name, stars=0, pushed="2024-01-01", archived=False, fork=False, desc=None):
        return {
            "name": name,
            "stargazers_count": stars,
            "pushed_at": pushed,
            "archived": archived,
            "fork": fork,
            "description": desc,
        }

    def test_returns_at_most_limit(self):
        repos = [self._make_repo(f"repo-{i}", stars=i) for i in range(20)]
        result = select_top_repos(repos, limit=12)
        assert len(result) <= 12

    def test_excludes_archived_repos(self):
        repos = [
            self._make_repo("active", stars=10),
            self._make_repo("archived", stars=100, archived=True),
        ]
        result = select_top_repos(repos)
        names = [r["name"] for r in result]
        assert "archived" not in names
        assert "active" in names

    def test_excludes_forked_repos(self):
        repos = [
            self._make_repo("own", stars=5),
            self._make_repo("forked", stars=50, fork=True),
        ]
        result = select_top_repos(repos)
        names = [r["name"] for r in result]
        assert "forked" not in names

    def test_sorted_by_stars_descending(self):
        repos = [
            self._make_repo("low", stars=1, desc="something"),
            self._make_repo("high", stars=100, desc="something"),
            self._make_repo("mid", stars=50, desc="something"),
        ]
        result = select_top_repos(repos, limit=3)
        assert result[0]["name"] == "high"
        assert result[1]["name"] == "mid"

    def test_prefers_repos_with_description(self):
        repos = [
            self._make_repo("no-desc", stars=100, desc=None),
            self._make_repo("with-desc", stars=10, desc="has description"),
        ]
        result = select_top_repos(repos, limit=2)
        # with_desc should be returned (prefers with-desc when stars allow)
        names = [r["name"] for r in result]
        assert "with-desc" in names

    def test_empty_list(self):
        assert select_top_repos([]) == []

    def test_all_archived_returns_empty(self):
        repos = [self._make_repo(f"r{i}", archived=True) for i in range(5)]
        assert select_top_repos(repos) == []

    def test_limit_zero(self):
        repos = [self._make_repo("repo-1")]
        result = select_top_repos(repos, limit=0)
        assert result == []

    def test_tiebreak_by_pushed_at(self):
        repos = [
            self._make_repo("older", stars=5, pushed="2023-01-01", desc="x"),
            self._make_repo("newer", stars=5, pushed="2024-06-01", desc="x"),
        ]
        result = select_top_repos(repos, limit=2)
        assert result[0]["name"] == "newer"


# --------------------------------------------------------------------------- #
# truncate()
# --------------------------------------------------------------------------- #

class TestTruncate:
    def test_short_text_unchanged(self):
        assert truncate("hello", 10) == "hello"

    def test_exact_length_unchanged(self):
        assert truncate("hello", 5) == "hello"

    def test_truncates_long_text(self):
        result = truncate("hello world", 8)
        assert len(result) <= 8
        assert result.endswith("…")

    def test_truncates_with_newlines_stripped(self):
        result = truncate("foo\nbar baz qux", 8)
        assert "\n" not in result

    def test_none_input_treated_as_empty(self):
        result = truncate(None, 10)
        assert isinstance(result, str)

    def test_empty_string(self):
        assert truncate("", 5) == ""

    def test_ellipsis_at_boundary(self):
        # n=5, text longer → result length should be at most 5
        result = truncate("abcdefgh", 5)
        assert len(result) <= 5
        assert result.endswith("…")


# --------------------------------------------------------------------------- #
# escape()
# --------------------------------------------------------------------------- #

class TestEscape:
    def test_ampersand(self):
        assert "&amp;" in escape("a & b")

    def test_less_than(self):
        assert "&lt;" in escape("a < b")

    def test_greater_than(self):
        assert "&gt;" in escape("a > b")

    def test_double_quote(self):
        assert "&quot;" in escape('say "hi"')

    def test_plain_text_unchanged(self):
        assert escape("hello world") == "hello world"

    def test_all_special_chars(self):
        result = escape('<script>alert("xss")</script> & "safe"')
        assert "&lt;" in result
        assert "&gt;" in result
        assert "&amp;" in result
        assert "&quot;" in result
        assert "<" not in result
        assert ">" not in result

    def test_non_string_input(self):
        assert escape(42) == "42"

    def test_empty_string(self):
        assert escape("") == ""
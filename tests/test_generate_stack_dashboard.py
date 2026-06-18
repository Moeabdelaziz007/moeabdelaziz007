import pytest
from unittest.mock import MagicMock

from scripts.generate_stack_dashboard import (
    top_languages,
    render_svg,
    render_fallback,
    aggregate_languages,
)


# --------------------------------------------------------------------------- #
# top_languages()
# --------------------------------------------------------------------------- #

class TestTopLanguages:
    def test_returns_top_n(self):
        totals = {"Python": 1000, "JS": 500, "Go": 200, "Rust": 100}
        result = top_languages(totals, n=2)
        assert len(result) == 2
        assert result[0][0] == "Python"
        assert result[1][0] == "JS"

    def test_default_n_is_10(self):
        totals = {f"lang{i}": i * 100 for i in range(1, 15)}
        result = top_languages(totals)
        assert len(result) == 10

    def test_percentages_sum_to_100(self):
        totals = {"Python": 300, "JS": 200, "Go": 500}
        result = top_languages(totals, n=3)
        total_pct = sum(pct for _, _, pct in result)
        assert abs(total_pct - 100.0) < 1e-6

    def test_empty_totals_no_error(self):
        result = top_languages({}, n=5)
        assert result == []

    def test_single_language(self):
        result = top_languages({"Python": 500}, n=5)
        assert len(result) == 1
        assert result[0][0] == "Python"
        assert abs(result[0][2] - 100.0) < 1e-6

    def test_percentages_correct(self):
        totals = {"A": 100, "B": 300}
        result = top_languages(totals, n=2)
        by_lang = {lang: pct for lang, _, pct in result}
        assert abs(by_lang["A"] - 25.0) < 1e-6
        assert abs(by_lang["B"] - 75.0) < 1e-6

    def test_result_tuples_have_three_elements(self):
        totals = {"Python": 100}
        for item in top_languages(totals, n=3):
            assert len(item) == 3

    def test_sorted_descending(self):
        totals = {"C": 50, "A": 200, "B": 100}
        result = top_languages(totals, n=3)
        counts = [c for _, c, _ in result]
        assert counts == sorted(counts, reverse=True)

    def test_n_larger_than_totals(self):
        totals = {"X": 10, "Y": 20}
        result = top_languages(totals, n=100)
        assert len(result) == 2


# --------------------------------------------------------------------------- #
# render_svg()
# --------------------------------------------------------------------------- #

class TestRenderSvg:
    def test_returns_svg_string(self):
        rows = [("Python", 1000, 50.0), ("JS", 800, 40.0), ("Go", 200, 10.0)]
        result = render_svg(rows, repo_count=5)
        assert result.strip().startswith("<svg")
        assert "</svg>" in result

    def test_language_names_in_output(self):
        rows = [("Python", 1000, 50.0), ("TypeScript", 500, 25.0)]
        result = render_svg(rows, repo_count=3)
        assert "Python" in result
        assert "TypeScript" in result

    def test_repo_count_in_output(self):
        rows = [("Python", 500, 100.0)]
        result = render_svg(rows, repo_count=42)
        assert "42" in result

    def test_percentages_in_output(self):
        rows = [("Go", 300, 33.3)]
        result = render_svg(rows, repo_count=1)
        assert "33.3%" in result

    def test_empty_rows_still_renders(self):
        result = render_svg([], repo_count=0)
        assert "<svg" in result

    def test_known_language_color_applied(self):
        rows = [("Python", 1000, 100.0)]
        result = render_svg(rows, repo_count=1)
        # Python color from LANGUAGE_COLORS
        assert "#3572A5" in result

    def test_unknown_language_uses_default_color(self):
        rows = [("Brainfuck", 100, 100.0)]
        result = render_svg(rows, repo_count=1)
        # Default language color
        assert "#888888" in result

    def test_single_svg_root(self):
        rows = [("Python", 100, 100.0)]
        result = render_svg(rows, repo_count=1)
        assert result.count("<svg") == 1
        assert result.count("</svg>") == 1


# --------------------------------------------------------------------------- #
# render_fallback()
# --------------------------------------------------------------------------- #

class TestRenderFallback:
    def test_returns_svg(self):
        result = render_fallback()
        assert "<svg" in result
        assert "</svg>" in result

    def test_contains_data_unavailable_message(self):
        result = render_fallback()
        assert "DATA UNAVAILABLE" in result

    def test_fixed_dimensions(self):
        result = render_fallback()
        assert 'width="720"' in result
        assert 'height="180"' in result


# --------------------------------------------------------------------------- #
# aggregate_languages() — uses a mock GitHubClient
# --------------------------------------------------------------------------- #

class TestAggregateLanguages:
    def _make_client(self, repos, languages_map):
        client = MagicMock()
        client.list_user_repos.return_value = repos
        client.get_repo_languages.side_effect = lambda owner, name: languages_map.get(name, {})
        return client

    def test_aggregates_across_repos(self):
        repos = [
            {"name": "repo-a", "owner": {"login": "user"}, "archived": False, "private": False},
            {"name": "repo-b", "owner": {"login": "user"}, "archived": False, "private": False},
        ]
        langs = {"repo-a": {"Python": 500}, "repo-b": {"Python": 300, "Go": 200}}
        client = self._make_client(repos, langs)
        totals, scanned = aggregate_languages(client, "user")
        assert totals["Python"] == 800
        assert totals["Go"] == 200
        assert scanned == 2

    def test_skips_archived_repos(self):
        repos = [
            {"name": "active", "owner": {"login": "user"}, "archived": False, "private": False},
            {"name": "old", "owner": {"login": "user"}, "archived": True, "private": False},
        ]
        client = self._make_client(repos, {"active": {"Rust": 100}})
        totals, scanned = aggregate_languages(client, "user")
        assert scanned == 1
        assert "Rust" in totals

    def test_skips_private_repos(self):
        repos = [
            {"name": "pub", "owner": {"login": "user"}, "archived": False, "private": False},
            {"name": "priv", "owner": {"login": "user"}, "archived": False, "private": True},
        ]
        client = self._make_client(repos, {"pub": {"JS": 400}})
        totals, scanned = aggregate_languages(client, "user")
        assert scanned == 1

    def test_empty_repos_returns_empty(self):
        client = self._make_client([], {})
        totals, scanned = aggregate_languages(client, "user")
        assert totals == {}
        assert scanned == 0

    def test_repo_without_name_skipped(self):
        repos = [
            {"name": None, "owner": {"login": "user"}, "archived": False, "private": False},
        ]
        client = self._make_client(repos, {})
        totals, scanned = aggregate_languages(client, "user")
        assert scanned == 0

    def test_owner_fallback_to_username(self):
        repos = [{"name": "myrepo", "owner": {}, "archived": False, "private": False}]
        langs = {"myrepo": {"Python": 100}}
        client = self._make_client(repos, langs)
        totals, scanned = aggregate_languages(client, "myuser")
        assert "Python" in totals
        # Verify the right owner was passed when owner.login is absent
        client.get_repo_languages.assert_called_with("myuser", "myrepo")
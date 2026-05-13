"""Tests for scripts/generate_stack_dashboard.py."""

from unittest.mock import MagicMock

import pytest

from scripts.generate_stack_dashboard import (
    DEFAULT_LANG_COLOR,
    LANGUAGE_COLORS,
    aggregate_languages,
    render_fallback,
    render_svg,
    top_languages,
)


# ---------------------------------------------------------------------------
# top_languages
# ---------------------------------------------------------------------------

class TestTopLanguages:
    def test_empty_totals(self):
        result = top_languages({})
        assert result == []

    def test_single_language(self):
        result = top_languages({"Python": 1000})
        assert len(result) == 1
        lang, count, pct = result[0]
        assert lang == "Python"
        assert count == 1000
        assert abs(pct - 100.0) < 0.01

    def test_sorts_by_bytes_descending(self):
        totals = {"Python": 500, "Go": 2000, "Rust": 100}
        result = top_languages(totals)
        langs = [r[0] for r in result]
        assert langs[0] == "Go"
        assert langs[1] == "Python"
        assert langs[2] == "Rust"

    def test_percentages_sum_to_100(self):
        totals = {"Python": 60, "Go": 30, "Rust": 10}
        result = top_languages(totals)
        total_pct = sum(pct for _, _, pct in result)
        assert abs(total_pct - 100.0) < 0.01

    def test_n_limits_results(self):
        totals = {f"Lang{i}": i + 1 for i in range(20)}
        result = top_languages(totals, n=5)
        assert len(result) == 5

    def test_n_larger_than_available(self):
        totals = {"Python": 100, "Go": 200}
        result = top_languages(totals, n=10)
        assert len(result) == 2

    def test_default_n_is_10(self):
        totals = {f"Lang{i}": i + 1 for i in range(15)}
        result = top_languages(totals)
        assert len(result) == 10

    def test_returns_tuples_of_three(self):
        result = top_languages({"Python": 100})
        assert len(result[0]) == 3

    def test_percentage_values_are_floats(self):
        result = top_languages({"Python": 70, "Go": 30})
        for _, _, pct in result:
            assert isinstance(pct, float)

    def test_zero_grand_total_does_not_divide_by_zero(self):
        # sum({}) = 0; grand = max(0, 1) = 1 via `or 1`
        result = top_languages({})
        assert result == []

    def test_top_language_has_highest_pct(self):
        totals = {"Python": 800, "Go": 200}
        result = top_languages(totals)
        assert result[0][2] > result[1][2]


# ---------------------------------------------------------------------------
# aggregate_languages
# ---------------------------------------------------------------------------

class TestAggregateLanguages:
    def _mock_client(self, repos, languages_map=None):
        client = MagicMock()
        client.list_user_repos.return_value = repos
        if languages_map is None:
            client.get_repo_languages.return_value = {}
        else:
            client.get_repo_languages.side_effect = lambda owner, name: languages_map.get(name, {})
        return client

    def test_empty_repos(self):
        client = self._mock_client([])
        totals, repo_count = aggregate_languages(client, "user")
        assert totals == {}
        assert repo_count == 0

    def test_skips_archived_repos(self):
        repos = [
            {"name": "archived-repo", "archived": True, "private": False,
             "owner": {"login": "user"}},
        ]
        client = self._mock_client(repos)
        totals, repo_count = aggregate_languages(client, "user")
        assert totals == {}
        client.get_repo_languages.assert_not_called()

    def test_skips_private_repos(self):
        repos = [
            {"name": "private-repo", "archived": False, "private": True,
             "owner": {"login": "user"}},
        ]
        client = self._mock_client(repos)
        totals, repo_count = aggregate_languages(client, "user")
        assert totals == {}
        client.get_repo_languages.assert_not_called()

    def test_aggregates_languages_from_public_repos(self):
        repos = [
            {"name": "repo1", "archived": False, "private": False,
             "owner": {"login": "user"}},
            {"name": "repo2", "archived": False, "private": False,
             "owner": {"login": "user"}},
        ]
        languages_map = {
            "repo1": {"Python": 1000, "Go": 500},
            "repo2": {"Python": 2000, "Rust": 300},
        }
        client = self._mock_client(repos, languages_map)
        totals, repo_count = aggregate_languages(client, "user")
        assert totals["Python"] == 3000
        assert totals["Go"] == 500
        assert totals["Rust"] == 300
        assert repo_count == 2

    def test_repo_count_includes_all_repos(self):
        repos = [
            {"name": "public", "archived": False, "private": False,
             "owner": {"login": "user"}},
            {"name": "archived", "archived": True, "private": False,
             "owner": {"login": "user"}},
        ]
        client = self._mock_client(repos)
        _, repo_count = aggregate_languages(client, "user")
        assert repo_count == 2

    def test_skips_repo_without_name(self):
        repos = [
            {"name": None, "archived": False, "private": False,
             "owner": {"login": "user"}},
        ]
        client = self._mock_client(repos)
        totals, _ = aggregate_languages(client, "user")
        assert totals == {}
        client.get_repo_languages.assert_not_called()

    def test_uses_username_when_owner_missing(self):
        repos = [
            {"name": "my-repo", "archived": False, "private": False},
        ]
        client = self._mock_client(repos, {"my-repo": {"Python": 100}})
        totals, _ = aggregate_languages(client, "fallback-user")
        assert totals == {"Python": 100}
        client.get_repo_languages.assert_called_once_with("fallback-user", "my-repo")


# ---------------------------------------------------------------------------
# render_svg
# ---------------------------------------------------------------------------

class TestRenderSvg:
    def _make_rows(self):
        return [("Python", 1000, 60.0), ("Go", 500, 30.0), ("Rust", 100, 10.0)]

    def test_returns_svg_string(self):
        svg = render_svg(self._make_rows(), 10)
        assert svg.startswith("<svg")
        assert "</svg>" in svg

    def test_contains_language_names(self):
        svg = render_svg(self._make_rows(), 10)
        assert "Python" in svg
        assert "Go" in svg
        assert "Rust" in svg

    def test_contains_repo_count(self):
        svg = render_svg(self._make_rows(), 42)
        assert "42 REPOSITORIES SCANNED" in svg

    def test_contains_percentage_values(self):
        svg = render_svg(self._make_rows(), 10)
        assert "60.0%" in svg
        assert "30.0%" in svg
        assert "10.0%" in svg

    def test_known_language_uses_correct_color(self):
        svg = render_svg([("Python", 1000, 100.0)], 1)
        assert LANGUAGE_COLORS["Python"] in svg

    def test_unknown_language_uses_default_color(self):
        svg = render_svg([("COBOL", 1000, 100.0)], 1)
        assert DEFAULT_LANG_COLOR in svg

    def test_stack_analysis_header(self):
        svg = render_svg(self._make_rows(), 10)
        assert "STACK ANALYSIS" in svg

    def test_core_languages_header(self):
        svg = render_svg(self._make_rows(), 10)
        assert "CORE LANGUAGES" in svg

    def test_source_footer_present(self):
        svg = render_svg(self._make_rows(), 10)
        assert "GITHUB REST API" in svg

    def test_height_scales_with_row_count(self):
        import re

        def get_height(svg_str):
            m = re.search(r'height="(\d+)"', svg_str)
            return int(m.group(1)) if m else 0

        svg_few = render_svg([("Python", 100, 100.0)], 1)
        svg_many = render_svg(self._make_rows(), 5)
        assert get_height(svg_many) > get_height(svg_few)

    def test_zero_repos_display(self):
        svg = render_svg(self._make_rows(), 0)
        assert "0 REPOSITORIES SCANNED" in svg

    def test_bar_min_width_enforced(self):
        # A language with very small pct still renders a rect (min width=4)
        svg = render_svg([("Rust", 1, 0.001)], 1)
        assert "<rect" in svg

    def test_empty_rows_renders_single_language_space(self):
        # render_svg([]) won't crash; bars list is empty but SVG still generated
        svg = render_svg([], 5)
        assert "<svg" in svg
        assert "</svg>" in svg


# ---------------------------------------------------------------------------
# render_fallback
# ---------------------------------------------------------------------------

class TestRenderFallback:
    def test_returns_svg_string(self):
        svg = render_fallback()
        assert svg.startswith("<svg")
        assert "</svg>" in svg

    def test_contains_data_unavailable(self):
        svg = render_fallback()
        assert "DATA UNAVAILABLE" in svg

    def test_contains_awaiting_sync_message(self):
        svg = render_fallback()
        assert "next scheduled telemetry sync" in svg

    def test_fixed_dimensions(self):
        svg = render_fallback()
        assert 'width="720"' in svg
        assert 'height="180"' in svg

    def test_different_from_render_svg(self):
        fallback = render_fallback()
        normal = render_svg([("Python", 100, 100.0)], 1)
        assert fallback != normal


# ---------------------------------------------------------------------------
# LANGUAGE_COLORS constant
# ---------------------------------------------------------------------------

class TestLanguageColors:
    """Regression tests for the LANGUAGE_COLORS dict referenced in the PR."""

    def test_python_color_present(self):
        assert "Python" in LANGUAGE_COLORS

    def test_typescript_color_present(self):
        assert "TypeScript" in LANGUAGE_COLORS

    def test_go_color_present(self):
        assert "Go" in LANGUAGE_COLORS

    def test_rust_color_present(self):
        assert "Rust" in LANGUAGE_COLORS

    def test_all_colors_are_hex(self):
        import re
        hex_re = re.compile(r"^#[0-9A-Fa-f]{3,8}$")
        for lang, color in LANGUAGE_COLORS.items():
            assert hex_re.match(color), f"{lang}: {color!r} is not a valid hex color"

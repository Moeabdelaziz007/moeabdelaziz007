"""Tests for scripts/generate_agents_inventory.py – covers the rewritten
AxiomID-focused logic introduced in this PR.

Tested: classify(), select_top_repos(), truncate(), escape(), render_svg()
"""

import os
import sys

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.generate_agents_inventory import (  # noqa: E402
    CATEGORY_RULES,
    classify,
    escape,
    render_svg,
    select_top_repos,
    truncate,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _repo(name="", description="", topics=None, stars=0, pushed_at="",
          archived=False, fork=False, language=None):
    """Build a minimal repo dict matching the GitHub API shape."""
    return {
        "name": name,
        "description": description,
        "topics": topics or [],
        "stargazers_count": stars,
        "pushed_at": pushed_at,
        "archived": archived,
        "fork": fork,
        "language": language,
    }


# ---------------------------------------------------------------------------
# CATEGORY_RULES sanity checks
# ---------------------------------------------------------------------------

class TestCategoryRules:
    def test_category_rules_is_list(self):
        assert isinstance(CATEGORY_RULES, list)

    def test_each_rule_is_three_tuple(self):
        for rule in CATEGORY_RULES:
            assert len(rule) == 3, f"Expected (name, color, patterns), got {rule!r}"

    def test_root_authority_rule_exists(self):
        names = [r[0] for r in CATEGORY_RULES]
        assert "Root Authority" in names

    def test_all_rules_have_non_empty_patterns(self):
        for name, _color, patterns in CATEGORY_RULES:
            assert patterns, f"Rule '{name}' has no patterns"


# ---------------------------------------------------------------------------
# classify()
# ---------------------------------------------------------------------------

class TestClassify:
    def test_axiomid_in_name_returns_root_authority(self):
        repo = _repo(name="axiomid-project")
        assert classify(repo) == "Root Authority"

    def test_root_in_description_returns_root_authority(self):
        repo = _repo(description="L0 root authority for sovereign identity")
        assert classify(repo) == "Root Authority"

    def test_jules_in_description_returns_autonomous_execution(self):
        repo = _repo(description="async task agent built on jules")
        assert classify(repo) == "Autonomous Execution"

    def test_opencode_in_topics_returns_autonomous_execution(self):
        repo = _repo(topics=["opencode", "agentic"])
        assert classify(repo) == "Autonomous Execution"

    def test_runtime_keyword_returns_autonomous_execution(self):
        repo = _repo(name="my-runtime")
        assert classify(repo) == "Autonomous Execution"

    def test_gemini_in_name_returns_verification_quality(self):
        repo = _repo(name="gemini-audit-tool")
        assert classify(repo) == "Verification & Quality"

    def test_coderabbit_in_description_returns_verification_quality(self):
        repo = _repo(description="Integrates coderabbit for PR reviews")
        assert classify(repo) == "Verification & Quality"

    def test_audit_keyword_returns_verification_quality(self):
        repo = _repo(topics=["audit", "security"])
        assert classify(repo) == "Verification & Quality"

    def test_antigravity_in_name_returns_mission_control(self):
        repo = _repo(name="antigravity-ide")
        assert classify(repo) == "Mission Control"

    def test_terminal_in_topics_returns_mission_control(self):
        repo = _repo(topics=["terminal", "cli"])
        assert classify(repo) == "Mission Control"

    def test_unrecognised_repo_returns_other(self):
        repo = _repo(name="my-blog", description="Personal blog posts")
        assert classify(repo) == "Other"

    def test_empty_repo_returns_other(self):
        assert classify({}) == "Other"

    def test_none_values_do_not_raise(self):
        repo = {"name": None, "description": None, "topics": None}
        result = classify(repo)
        assert isinstance(result, str)

    def test_matching_is_case_insensitive(self):
        repo = _repo(name="AXIOMID")
        assert classify(repo) == "Root Authority"

    def test_first_matching_rule_wins(self):
        # "axiomid" matches Root Authority; if also "jules" is present,
        # Root Authority should still win because it is listed first.
        repo = _repo(name="axiomid-jules")
        assert classify(repo) == "Root Authority"


# ---------------------------------------------------------------------------
# select_top_repos()
# ---------------------------------------------------------------------------

class TestSelectTopRepos:
    def test_returns_up_to_limit(self):
        repos = [_repo(name=f"repo-{i}") for i in range(10)]
        result = select_top_repos(repos, limit=6)
        assert len(result) <= 6

    def test_excludes_archived_repos(self):
        repos = [_repo(name="active"), _repo(name="old", archived=True)]
        result = select_top_repos(repos)
        names = [r["name"] for r in result]
        assert "old" not in names

    def test_excludes_forks(self):
        repos = [_repo(name="original"), _repo(name="forked", fork=True)]
        result = select_top_repos(repos)
        names = [r["name"] for r in result]
        assert "forked" not in names

    def test_axiomid_repo_is_first(self):
        repos = [
            _repo(name="my-lib", stars=100),
            _repo(name="axiomid-project", stars=1),
            _repo(name="another-tool", stars=50),
        ]
        result = select_top_repos(repos, limit=3)
        assert result[0]["name"] == "axiomid-project"

    def test_empty_list_returns_empty(self):
        assert select_top_repos([]) == []

    def test_all_archived_returns_empty(self):
        repos = [_repo(name=f"r{i}", archived=True) for i in range(5)]
        assert select_top_repos(repos) == []

    def test_default_limit_is_6(self):
        repos = [_repo(name=f"repo-{i}") for i in range(20)]
        result = select_top_repos(repos)
        assert len(result) <= 6

    def test_custom_limit_respected(self):
        repos = [_repo(name=f"repo-{i}") for i in range(10)]
        result = select_top_repos(repos, limit=3)
        assert len(result) == 3

    def test_repos_sorted_by_stars_within_same_priority(self):
        repos = [
            _repo(name="low-stars", stars=1),
            _repo(name="high-stars", stars=50),
        ]
        result = select_top_repos(repos, limit=2)
        assert result[0]["name"] == "high-stars"

    def test_pushed_at_used_as_tiebreaker(self):
        repos = [
            _repo(name="older-repo", stars=5, pushed_at="2024-01-01"),
            _repo(name="newer-repo", stars=5, pushed_at="2025-06-01"),
        ]
        result = select_top_repos(repos, limit=2)
        assert result[0]["name"] == "newer-repo"


# ---------------------------------------------------------------------------
# truncate()
# ---------------------------------------------------------------------------

class TestTruncate:
    def test_short_text_unchanged(self):
        assert truncate("hello", 10) == "hello"

    def test_exact_length_unchanged(self):
        assert truncate("hello", 5) == "hello"

    def test_long_text_is_truncated(self):
        result = truncate("hello world", 7)
        assert len(result) <= 7
        assert result.endswith("…")

    def test_truncated_text_ends_with_ellipsis(self):
        result = truncate("a" * 50, 20)
        assert result.endswith("…")

    def test_none_treated_as_empty_string(self):
        result = truncate(None, 10)
        assert isinstance(result, str)
        assert len(result) <= 10

    def test_empty_string_returns_empty(self):
        assert truncate("", 10) == ""

    def test_newlines_replaced_by_spaces(self):
        result = truncate("line1\nline2", 20)
        assert "\n" not in result

    def test_trailing_whitespace_stripped_before_ellipsis(self):
        # Text that would end at a space should not keep trailing space before …
        long = "word " * 5  # "word word word word word "
        result = truncate(long, 12)
        assert not result.endswith(" …"), f"Unexpected trailing space: {result!r}"


# ---------------------------------------------------------------------------
# escape()
# ---------------------------------------------------------------------------

class TestEscape:
    def test_ampersand_escaped(self):
        assert escape("A & B") == "A &amp; B"

    def test_less_than_escaped(self):
        assert escape("a < b") == "a &lt; b"

    def test_greater_than_escaped(self):
        assert escape("a > b") == "a &gt; b"

    def test_combined_escapes(self):
        result = escape("<script>alert('xss')</script>")
        assert "<" not in result
        assert ">" not in result

    def test_plain_text_unchanged(self):
        assert escape("hello world") == "hello world"

    def test_none_converted_to_string(self):
        result = escape(None)
        assert isinstance(result, str)

    def test_integer_converted_to_string(self):
        result = escape(42)
        assert result == "42"

    def test_double_escaping_not_applied(self):
        # Input already contains &amp; – should become &amp;amp;
        result = escape("&amp;")
        assert result == "&amp;amp;"


# ---------------------------------------------------------------------------
# render_svg()
# ---------------------------------------------------------------------------

class TestRenderSvg:
    SAMPLE_REPOS = [
        _repo(name="axiomid-project", description="Root authority", stars=5, language="TypeScript"),
        _repo(name="aix-format", description="AIX protocol spec", stars=1, language="Python"),
    ]

    def test_returns_string(self):
        svg = render_svg(self.SAMPLE_REPOS, total_repos=5)
        assert isinstance(svg, str)

    def test_starts_with_svg_tag(self):
        svg = render_svg(self.SAMPLE_REPOS, total_repos=5)
        assert svg.strip().startswith("<svg")

    def test_ends_with_closing_svg_tag(self):
        svg = render_svg(self.SAMPLE_REPOS, total_repos=5)
        assert svg.strip().endswith("</svg>")

    def test_contains_axiomid_fleet_label(self):
        svg = render_svg(self.SAMPLE_REPOS, total_repos=5)
        assert "AXIOMID AGENT FLEET" in svg

    def test_contains_consortium_heading(self):
        svg = render_svg(self.SAMPLE_REPOS, total_repos=5)
        assert "THE CONSORTIUM" in svg

    def test_repo_names_appear_in_svg(self):
        svg = render_svg(self.SAMPLE_REPOS, total_repos=5)
        for repo in self.SAMPLE_REPOS:
            assert repo["name"] in svg

    def test_empty_repos_still_produces_valid_svg(self):
        svg = render_svg([], total_repos=0)
        assert "<svg" in svg
        assert "</svg>" in svg

    def test_special_chars_in_name_are_escaped(self):
        repos = [_repo(name="a & b")]
        svg = render_svg(repos, total_repos=1)
        assert "&amp;" in svg
        # Raw & should not appear outside of entity references
        # (strip entity references first, then check)
        stripped = svg.replace("&amp;", "").replace("&lt;", "").replace("&gt;", "")
        assert " & " not in stripped

    def test_svg_dimensions_scale_with_row_count(self):
        """More repos => taller SVG."""
        small_svg = render_svg(self.SAMPLE_REPOS[:1], total_repos=1)
        large_repos = [_repo(name=f"r{i}") for i in range(6)]
        large_svg = render_svg(large_repos, total_repos=6)

        # Extract height values from the opening <svg> tag
        import re
        def _height(svg):
            m = re.search(r'height="(\d+)"', svg)
            return int(m.group(1)) if m else 0

        assert _height(large_svg) >= _height(small_svg)

    def test_category_label_in_uppercase_in_svg(self):
        repos = [_repo(name="axiomid-project")]
        svg = render_svg(repos, total_repos=1)
        # classify() returns "Root Authority" → rendered as "ROOT AUTHORITY"
        assert "ROOT AUTHORITY" in svg

    def test_neon_colour_used_for_background(self):
        svg = render_svg(self.SAMPLE_REPOS, total_repos=2)
        # neon color from PALETTE should appear in the SVG stroke
        assert "#39FF14" in svg

    def test_six_repos_produces_three_rows_two_cols(self):
        repos = [_repo(name=f"repo-{i}") for i in range(6)]
        svg = render_svg(repos, total_repos=6)
        # Each card has a translate(x, y) — count them
        import re
        transforms = re.findall(r'<g transform="translate\(', svg)
        assert len(transforms) == 6

    def test_default_description_used_when_none(self):
        repos = [_repo(name="myrepo", description=None)]
        svg = render_svg(repos, total_repos=1)
        assert "Sovereign identity primitive." in svg

    def test_svg_contains_pattern_element(self):
        svg = render_svg(self.SAMPLE_REPOS, total_repos=2)
        assert "<pattern" in svg

    def test_svg_viewbox_matches_width_height(self):
        import re
        svg = render_svg(self.SAMPLE_REPOS, total_repos=2)
        width_m = re.search(r'<svg width="(\d+)"', svg)
        viewbox_m = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
        if width_m and viewbox_m:
            assert width_m.group(1) == viewbox_m.group(1)

    def test_mission_control_category_color_in_svg(self):
        repos = [_repo(name="antigravity-terminal")]
        svg = render_svg(repos, total_repos=1)
        # Mission Control accent = "#39FFC4"
        assert "#39FFC4" in svg

    def test_verification_quality_category_color_in_svg(self):
        repos = [_repo(name="gemini-audit")]
        svg = render_svg(repos, total_repos=1)
        # Verification & Quality accent = "#4285F4"
        assert "#4285F4" in svg

    def test_autonomous_execution_category_color_in_svg(self):
        repos = [_repo(name="jules-runtime")]
        svg = render_svg(repos, total_repos=1)
        # Autonomous Execution accent = "#7FFF50"
        assert "#7FFF50" in svg

    def test_stagger_animation_increments_per_card(self):
        import re
        repos = [_repo(name=f"repo-{i}") for i in range(4)]
        svg = render_svg(repos, total_repos=4)
        stagger_values = re.findall(r'begin="([0-9.]+)s"', svg)
        # Should have 4 stagger values, each 0.1s apart: 0.0, 0.1, 0.2, 0.3
        assert len(stagger_values) == 4
        floats = [float(v) for v in stagger_values]
        for i, v in enumerate(floats):
            assert abs(v - i * 0.1) < 0.001


# ---------------------------------------------------------------------------
# Additional classify() edge cases for new AxiomID category rules
# ---------------------------------------------------------------------------

class TestClassifyAdditional:
    """Additional edge cases for the rewritten category rules."""

    def test_ide_keyword_returns_mission_control(self):
        repo = _repo(description="An IDE plugin for agentic tasks")
        assert classify(repo) == "Mission Control"

    def test_terminal_in_description_returns_mission_control(self):
        repo = _repo(description="A sovereign terminal emulator")
        assert classify(repo) == "Mission Control"

    def test_audit_in_name_returns_verification_quality(self):
        repo = _repo(name="smart-audit-engine")
        assert classify(repo) == "Verification & Quality"

    def test_runtime_in_topic_returns_autonomous_execution(self):
        repo = _repo(topics=["runtime", "agent"])
        assert classify(repo) == "Autonomous Execution"

    def test_root_keyword_word_boundary(self):
        # "root" as a whole word should match
        repo = _repo(description="This is the root authority")
        assert classify(repo) == "Root Authority"

    def test_root_keyword_not_matched_as_substring_in_unrelated_word(self):
        # "carrot" contains "rot" but not "root" as word boundary
        # "uprooted" does NOT contain \broot\b
        repo = _repo(name="uprooted-garden")
        # "uprooted" doesn't match \broot\b so should return "Other"
        assert classify(repo) == "Other"

    def test_all_four_categories_reachable(self):
        """Each of the four new categories can be produced by classify()."""
        repos_and_expected = [
            (_repo(name="axiomid-project"), "Root Authority"),
            (_repo(name="jules-agent"), "Autonomous Execution"),
            (_repo(name="gemini-reviewer"), "Verification & Quality"),
            (_repo(name="antigravity-ide"), "Mission Control"),
        ]
        for repo, expected in repos_and_expected:
            assert classify(repo) == expected, f"Expected '{expected}' for {repo['name']!r}"


# ---------------------------------------------------------------------------
# Additional select_top_repos() edge cases
# ---------------------------------------------------------------------------

class TestSelectTopReposAdditional:
    """Additional edge cases for the AxiomID-prioritising sort."""

    def test_multiple_axiomid_repos_all_promoted(self):
        repos = [
            _repo(name="axiomid-project", stars=1),
            _repo(name="axiomid-core", stars=1),
            _repo(name="unrelated-tool", stars=100),
        ]
        result = select_top_repos(repos, limit=3)
        names = [r["name"] for r in result]
        # Both axiomid repos should appear before unrelated-tool
        assert names.index("axiomid-project") < names.index("unrelated-tool")
        assert names.index("axiomid-core") < names.index("unrelated-tool")

    def test_fork_and_archived_simultaneously_excluded(self):
        repos = [
            _repo(name="good-repo"),
            _repo(name="bad-repo", archived=True, fork=True),
        ]
        result = select_top_repos(repos)
        assert all(r["name"] != "bad-repo" for r in result)

    def test_limit_zero_returns_empty(self):
        repos = [_repo(name="some-repo")]
        result = select_top_repos(repos, limit=0)
        assert result == []

    def test_fewer_repos_than_limit_returns_all(self):
        repos = [_repo(name=f"r{i}") for i in range(3)]
        result = select_top_repos(repos, limit=6)
        assert len(result) == 3
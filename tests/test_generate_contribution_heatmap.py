"""Tests for scripts/generate_contribution_heatmap.py."""

import datetime as dt

import pytest

from scripts.generate_contribution_heatmap import (
    current_streak,
    flatten_days,
    longest_streak,
    neon_shade,
    render_fallback,
    render_svg,
)


# ---------------------------------------------------------------------------
# neon_shade
# ---------------------------------------------------------------------------

class TestNeonShade:
    def test_zero_count_returns_darkest(self):
        assert neon_shade(0, 100) == "#0a0a0a"

    def test_negative_count_returns_darkest(self):
        assert neon_shade(-5, 100) == "#0a0a0a"

    def test_ratio_below_20pct(self):
        # count=10, max=100 → ratio=0.10 < 0.20
        assert neon_shade(10, 100) == "#0d3320"

    def test_ratio_exactly_20pct(self):
        # count=20, max=100 → ratio=0.20 → not < 0.20, not < 0.40 → "#155b30"
        assert neon_shade(20, 100) == "#155b30"

    def test_ratio_below_40pct(self):
        # count=30, max=100 → ratio=0.30
        assert neon_shade(30, 100) == "#155b30"

    def test_ratio_exactly_40pct(self):
        # count=40, max=100 → ratio=0.40 → "#218a3f"
        assert neon_shade(40, 100) == "#218a3f"

    def test_ratio_below_60pct(self):
        # count=50, max=100 → ratio=0.50
        assert neon_shade(50, 100) == "#218a3f"

    def test_ratio_exactly_60pct(self):
        # count=60, max=100 → ratio=0.60 → "#2bbf4d"
        assert neon_shade(60, 100) == "#2bbf4d"

    def test_ratio_below_80pct(self):
        # count=70, max=100 → ratio=0.70
        assert neon_shade(70, 100) == "#2bbf4d"

    def test_ratio_exactly_80pct(self):
        # count=80, max=100 → ratio=0.80 → "#39FF14"
        assert neon_shade(80, 100) == "#39FF14"

    def test_ratio_above_80pct(self):
        # count=90, max=100 → ratio=0.90
        assert neon_shade(90, 100) == "#39FF14"

    def test_count_equals_max_count(self):
        # ratio=1.0 → clamped to 1.0 → "#39FF14"
        assert neon_shade(200, 200) == "#39FF14"

    def test_count_exceeds_max_count(self):
        # min(..., 1.0) clamps → "#39FF14"
        assert neon_shade(300, 200) == "#39FF14"

    def test_max_count_zero_does_not_divide_by_zero(self):
        # max(max_count, 1) prevents ZeroDivisionError; count=1 → ratio=1.0 → "#39FF14"
        assert neon_shade(1, 0) == "#39FF14"

    def test_max_count_one_count_one(self):
        # ratio = 1/1 = 1.0 → "#39FF14"
        assert neon_shade(1, 1) == "#39FF14"


# ---------------------------------------------------------------------------
# longest_streak
# ---------------------------------------------------------------------------

def _make_day(count: int) -> dict:
    return {"contributionCount": count}


class TestLongestStreak:
    def test_empty_list(self):
        assert longest_streak([]) == 0

    def test_all_zeros(self):
        days = [_make_day(0)] * 5
        assert longest_streak(days) == 0

    def test_single_nonzero(self):
        days = [_make_day(0), _make_day(5), _make_day(0)]
        assert longest_streak(days) == 1

    def test_consecutive_days(self):
        days = [_make_day(1), _make_day(2), _make_day(3)]
        assert longest_streak(days) == 3

    def test_multiple_streaks_picks_longest(self):
        # streak of 2, gap, streak of 3
        days = [_make_day(1), _make_day(1), _make_day(0), _make_day(1), _make_day(1), _make_day(1)]
        assert longest_streak(days) == 3

    def test_streak_at_end(self):
        days = [_make_day(0), _make_day(1), _make_day(1)]
        assert longest_streak(days) == 2

    def test_missing_contribution_count_key(self):
        # get() returns 0 by default
        days = [{"date": "2025-01-01"}, _make_day(3)]
        assert longest_streak(days) == 1

    def test_all_nonzero(self):
        days = [_make_day(i + 1) for i in range(10)]
        assert longest_streak(days) == 10


# ---------------------------------------------------------------------------
# current_streak
# ---------------------------------------------------------------------------

class TestCurrentStreak:
    def test_empty_list(self):
        assert current_streak([]) == 0

    def test_last_day_zero(self):
        days = [_make_day(5), _make_day(0)]
        assert current_streak(days) == 0

    def test_single_nonzero_at_end(self):
        days = [_make_day(0), _make_day(3)]
        assert current_streak(days) == 1

    def test_consecutive_from_end(self):
        days = [_make_day(0), _make_day(1), _make_day(2), _make_day(3)]
        assert current_streak(days) == 3

    def test_breaks_at_first_zero(self):
        days = [_make_day(1), _make_day(0), _make_day(2), _make_day(1)]
        assert current_streak(days) == 2

    def test_all_nonzero(self):
        days = [_make_day(i + 1) for i in range(7)]
        assert current_streak(days) == 7

    def test_all_zero(self):
        days = [_make_day(0)] * 5
        assert current_streak(days) == 0


# ---------------------------------------------------------------------------
# flatten_days
# ---------------------------------------------------------------------------

class TestFlattenDays:
    def test_empty_weeks(self):
        assert flatten_days([]) == []

    def test_single_week_single_day(self):
        weeks = [{"contributionDays": [{"date": "2025-01-01", "contributionCount": 3}]}]
        result = flatten_days(weeks)
        assert len(result) == 1
        assert result[0]["date"] == "2025-01-01"

    def test_multiple_weeks(self):
        weeks = [
            {"contributionDays": [{"date": "2025-01-01"}, {"date": "2025-01-02"}]},
            {"contributionDays": [{"date": "2025-01-07"}, {"date": "2025-01-08"}]},
        ]
        result = flatten_days(weeks)
        assert len(result) == 4
        assert result[0]["date"] == "2025-01-01"
        assert result[3]["date"] == "2025-01-08"

    def test_week_missing_contribution_days_key(self):
        weeks = [{"other": "data"}, {"contributionDays": [{"date": "2025-01-01"}]}]
        result = flatten_days(weeks)
        assert len(result) == 1

    def test_week_with_empty_contribution_days(self):
        weeks = [{"contributionDays": []}, {"contributionDays": [{"date": "2025-06-01"}]}]
        result = flatten_days(weeks)
        assert len(result) == 1

    def test_order_preserved(self):
        weeks = [
            {"contributionDays": [{"date": "A"}, {"date": "B"}]},
            {"contributionDays": [{"date": "C"}]},
        ]
        result = flatten_days(weeks)
        assert [d["date"] for d in result] == ["A", "B", "C"]


# ---------------------------------------------------------------------------
# render_svg
# ---------------------------------------------------------------------------

def _make_contributions(total=100, commits=50, prs=10, issues=5, weeks=None):
    if weeks is None:
        weeks = [
            {
                "contributionDays": [
                    {"date": "2025-06-09", "contributionCount": 5, "weekday": 1},
                    {"date": "2025-06-10", "contributionCount": 10, "weekday": 2},
                ]
            }
        ]
    return {
        "contributionCalendar": {
            "totalContributions": total,
            "weeks": weeks,
        },
        "totalCommitContributions": commits,
        "totalPullRequestContributions": prs,
        "totalIssueContributions": issues,
    }


class TestRenderSvg:
    def test_returns_svg_string(self):
        svg = render_svg(_make_contributions())
        assert svg.startswith("<svg")
        assert "</svg>" in svg

    def test_contains_total_contributions(self):
        svg = render_svg(_make_contributions(total=4440))
        assert "4,440 CONTRIBUTIONS" in svg

    def test_contains_commits_count(self):
        svg = render_svg(_make_contributions(commits=3622))
        assert "3,622" in svg

    def test_contains_prs_count(self):
        svg = render_svg(_make_contributions(prs=694))
        assert "694" in svg

    def test_contains_issues_count(self):
        svg = render_svg(_make_contributions(issues=42))
        assert "42" in svg

    def test_contains_rect_elements(self):
        svg = render_svg(_make_contributions())
        assert "<rect" in svg

    def test_contains_contribution_flow_label(self):
        svg = render_svg(_make_contributions())
        assert "CONTRIBUTION FLOW" in svg

    def test_fallback_when_no_days(self):
        contributions = {
            "contributionCalendar": {"totalContributions": 0, "weeks": []},
            "totalCommitContributions": 0,
            "totalPullRequestContributions": 0,
            "totalIssueContributions": 0,
        }
        svg = render_svg(contributions)
        assert "DATA UNAVAILABLE" in svg

    def test_empty_contributions_dict_triggers_fallback(self):
        svg = render_svg({})
        assert "DATA UNAVAILABLE" in svg

    def test_streak_display_present(self):
        svg = render_svg(_make_contributions())
        assert "CURRENT STREAK" in svg
        assert "LONGEST STREAK" in svg

    def test_weekday_labels_present(self):
        svg = render_svg(_make_contributions())
        assert "Mon" in svg
        assert "Wed" in svg
        assert "Fri" in svg

    def test_legend_present(self):
        svg = render_svg(_make_contributions())
        assert "Less" in svg
        assert "More" in svg

    def test_cell_date_in_title(self):
        svg = render_svg(_make_contributions())
        assert "2025-06-09" in svg

    def test_neon_shade_applied_to_cells(self):
        # A zero-count day should use #0a0a0a
        weeks = [{"contributionDays": [{"date": "2025-06-09", "contributionCount": 0, "weekday": 0}]}]
        svg = render_svg(_make_contributions(weeks=weeks))
        assert '#0a0a0a' in svg


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

    def test_contains_github_token_message(self):
        svg = render_fallback()
        assert "GITHUB_TOKEN" in svg

    def test_fixed_dimensions(self):
        svg = render_fallback()
        assert 'width="720"' in svg
        assert 'height="180"' in svg
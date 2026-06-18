import datetime

import pytest

from scripts.generate_contribution_heatmap import (
    neon_shade,
    longest_streak,
    current_streak,
    flatten_days,
)


# --------------------------------------------------------------------------- #
# neon_shade()
# --------------------------------------------------------------------------- #

class TestNeonShade:
    def test_zero_count_returns_darkest(self):
        assert neon_shade(0, 10) == "#0a0a0a"

    def test_negative_count_returns_darkest(self):
        assert neon_shade(-5, 10) == "#0a0a0a"

    def test_max_count_returns_brightest(self):
        assert neon_shade(10, 10) == "#39FF14"

    def test_low_ratio_shade(self):
        # ratio < 0.20 → "#0d3320"
        result = neon_shade(1, 100)
        assert result == "#0d3320"

    def test_mid_low_ratio_shade(self):
        # ratio 0.20–0.40 → "#155b30"
        result = neon_shade(25, 100)
        assert result == "#155b30"

    def test_mid_ratio_shade(self):
        # ratio 0.40–0.60 → "#218a3f"
        result = neon_shade(50, 100)
        assert result == "#218a3f"

    def test_mid_high_ratio_shade(self):
        # ratio 0.60–0.80 → "#2bbf4d"
        result = neon_shade(70, 100)
        assert result == "#2bbf4d"

    def test_high_ratio_shade(self):
        # ratio >= 0.80 → "#39FF14"
        result = neon_shade(85, 100)
        assert result == "#39FF14"

    def test_max_count_zero_no_division_error(self):
        # max_count=0 → max(max_count, 1)=1 avoids ZeroDivisionError
        # count>0 and max=0 → ratio = count/1 ≥ 1.0 → clamped to 1.0 → brightest
        result = neon_shade(1, 0)
        assert result == "#39FF14"

    def test_count_exceeds_max_clamped(self):
        # count > max_count → ratio clamped to 1.0 → brightest shade
        result = neon_shade(200, 100)
        assert result == "#39FF14"


# --------------------------------------------------------------------------- #
# longest_streak()
# --------------------------------------------------------------------------- #

def _day(count, date="2024-01-01"):
    return {"contributionCount": count, "date": date}


class TestLongestStreak:
    def test_empty_list(self):
        assert longest_streak([]) == 0

    def test_all_zeros(self):
        days = [_day(0)] * 5
        assert longest_streak(days) == 0

    def test_all_active(self):
        days = [_day(3)] * 7
        assert longest_streak(days) == 7

    def test_single_active_day(self):
        days = [_day(0), _day(1), _day(0)]
        assert longest_streak(days) == 1

    def test_streak_broken_by_zero(self):
        days = [_day(1), _day(2), _day(0), _day(5), _day(3), _day(4)]
        assert longest_streak(days) == 3

    def test_two_equal_streaks(self):
        days = [_day(1), _day(1), _day(0), _day(1), _day(1)]
        assert longest_streak(days) == 2

    def test_string_count_values(self):
        # contributionCount stored as string in real API responses
        days = [{"contributionCount": "5", "date": "2024-01-01"}] * 4
        assert longest_streak(days) == 4

    def test_missing_contribution_count_key(self):
        days = [{}, {}, {}]
        assert longest_streak(days) == 0


# --------------------------------------------------------------------------- #
# current_streak()
# --------------------------------------------------------------------------- #

class TestCurrentStreak:
    def _make_days(self, counts, base_date=None):
        """Build a list of day dicts ending on today - len(counts) + 1."""
        if base_date is None:
            base_date = datetime.date.today()
        days = []
        for i, c in enumerate(counts):
            d = base_date - datetime.timedelta(days=len(counts) - 1 - i)
            days.append({"contributionCount": c, "date": d.strftime("%Y-%m-%d")})
        return days

    def test_empty_list(self):
        assert current_streak([]) == 0

    def test_no_recent_activity(self):
        days = self._make_days([0, 0, 0])
        assert current_streak(days) == 0

    def test_streak_up_to_today(self):
        days = self._make_days([0, 1, 1, 1])
        assert current_streak(days) == 3

    def test_streak_broken_before_today(self):
        days = self._make_days([1, 1, 0, 1])
        # Last day has 1 contribution, day before has 0 → streak = 1
        assert current_streak(days) == 1

    def test_future_dates_excluded(self):
        today = datetime.date.today()
        future = today + datetime.timedelta(days=1)
        days = [
            {"contributionCount": 5, "date": future.strftime("%Y-%m-%d")},
            {"contributionCount": 3, "date": today.strftime("%Y-%m-%d")},
        ]
        # Future date excluded; today has 3 → streak = 1
        result = current_streak(days)
        assert result == 1

    def test_all_days_active(self):
        days = self._make_days([2, 2, 2, 2, 2])
        assert current_streak(days) == 5


# --------------------------------------------------------------------------- #
# flatten_days()
# --------------------------------------------------------------------------- #

class TestFlattenDays:
    def test_empty_weeks(self):
        assert flatten_days([]) == []

    def test_single_week_single_day(self):
        weeks = [{"contributionDays": [{"date": "2024-01-01", "contributionCount": 1}]}]
        result = flatten_days(weeks)
        assert len(result) == 1
        assert result[0]["date"] == "2024-01-01"

    def test_multiple_weeks(self):
        weeks = [
            {"contributionDays": [{"date": f"2024-01-0{i}"} for i in range(1, 4)]},
            {"contributionDays": [{"date": f"2024-01-0{i}"} for i in range(4, 8)]},
        ]
        result = flatten_days(weeks)
        assert len(result) == 7

    def test_week_with_no_contribution_days_key(self):
        weeks = [{"contributionDays": []}, {}]
        result = flatten_days(weeks)
        assert result == []

    def test_preserves_order(self):
        days1 = [{"date": "2024-01-01"}, {"date": "2024-01-02"}]
        days2 = [{"date": "2024-01-08"}, {"date": "2024-01-09"}]
        weeks = [{"contributionDays": days1}, {"contributionDays": days2}]
        result = flatten_days(weeks)
        assert result[0]["date"] == "2024-01-01"
        assert result[-1]["date"] == "2024-01-09"

    def test_returns_list_type(self):
        assert isinstance(flatten_days([]), list)
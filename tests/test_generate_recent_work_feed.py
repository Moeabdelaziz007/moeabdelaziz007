"""Tests for scripts/generate_recent_work_feed.py."""

import datetime as dt

import pytest

from scripts.generate_recent_work_feed import (
    escape,
    humanize,
    render_svg,
    summarize,
)


# ---------------------------------------------------------------------------
# humanize
# ---------------------------------------------------------------------------

class TestHumanize:
    def test_zero_seconds(self):
        assert humanize(dt.timedelta(seconds=0)) == "0s ago"

    def test_seconds_less_than_60(self):
        assert humanize(dt.timedelta(seconds=45)) == "45s ago"

    def test_exactly_59_seconds(self):
        assert humanize(dt.timedelta(seconds=59)) == "59s ago"

    def test_exactly_60_seconds(self):
        # 60s → 1m ago
        assert humanize(dt.timedelta(seconds=60)) == "1m ago"

    def test_minutes(self):
        assert humanize(dt.timedelta(seconds=90)) == "1m ago"

    def test_exactly_1_hour(self):
        assert humanize(dt.timedelta(seconds=3600)) == "1h ago"

    def test_hours(self):
        assert humanize(dt.timedelta(seconds=7200)) == "2h ago"

    def test_less_than_one_day(self):
        assert humanize(dt.timedelta(seconds=86399)) == "23h ago"

    def test_exactly_one_day(self):
        assert humanize(dt.timedelta(seconds=86400)) == "1d ago"

    def test_days(self):
        assert humanize(dt.timedelta(days=5)) == "5d ago"

    def test_less_than_30_days(self):
        assert humanize(dt.timedelta(days=29)) == "29d ago"

    def test_exactly_30_days(self):
        # 30 * 86400 = 2592000 seconds → >= 86400*30 → months
        assert humanize(dt.timedelta(days=30)) == "1mo ago"

    def test_months(self):
        assert humanize(dt.timedelta(days=60)) == "2mo ago"

    def test_large_value(self):
        assert humanize(dt.timedelta(days=365)) == "12mo ago"


# ---------------------------------------------------------------------------
# escape
# ---------------------------------------------------------------------------

class TestEscape:
    def test_ampersand(self):
        assert escape("a & b") == "a &amp; b"

    def test_less_than(self):
        assert escape("<tag>") == "&lt;tag&gt;"

    def test_greater_than(self):
        assert escape("a > b") == "a &gt; b"

    def test_double_quote(self):
        assert escape('say "hi"') == "say &quot;hi&quot;"

    def test_all_special_chars(self):
        result = escape('<a href="x">foo & bar</a>')
        assert "&lt;" in result
        assert "&gt;" in result
        assert "&amp;" in result
        assert "&quot;" in result

    def test_plain_text_unchanged(self):
        assert escape("hello world") == "hello world"

    def test_empty_string(self):
        assert escape("") == ""

    def test_numeric_input(self):
        # accepts non-str via str() conversion
        assert escape(42) == "42"

    def test_none_input(self):
        assert escape(None) == "None"

    def test_multiple_ampersands(self):
        assert escape("&&") == "&amp;&amp;"


# ---------------------------------------------------------------------------
# summarize
# ---------------------------------------------------------------------------

def _event(etype, payload=None, **kwargs):
    return {"type": etype, "payload": payload or {}, **kwargs}


class TestSummarize:
    def test_push_event_with_commits(self):
        event = _event("PushEvent", {
            "commits": [
                {"message": "first commit"},
                {"message": "second commit"},
            ]
        })
        result = summarize(event)
        assert "2 commits" in result
        assert "second commit" in result

    def test_push_event_single_commit(self):
        event = _event("PushEvent", {"commits": [{"message": "solo commit"}]})
        result = summarize(event)
        assert "1 commit " in result
        assert "solo commit" in result

    def test_push_event_no_commits_uses_size(self):
        event = _event("PushEvent", {"size": 3, "commits": []})
        result = summarize(event)
        assert "3 commit pushed" in result

    def test_push_event_commit_message_truncated_at_60(self):
        long_msg = "x" * 100
        event = _event("PushEvent", {"commits": [{"message": long_msg}]})
        result = summarize(event)
        assert "x" * 60 in result
        assert "x" * 61 not in result

    def test_push_event_multiline_commit_uses_first_line(self):
        event = _event("PushEvent", {"commits": [{"message": "first line\nsecond line"}]})
        result = summarize(event)
        assert "first line" in result
        assert "second line" not in result

    def test_pull_request_event(self):
        event = _event("PullRequestEvent", {
            "action": "opened",
            "pull_request": {"title": "Add new feature"},
        })
        result = summarize(event)
        assert "PR opened" in result
        assert "Add new feature" in result

    def test_pull_request_event_title_truncated(self):
        long_title = "T" * 100
        event = _event("PullRequestEvent", {
            "action": "merged",
            "pull_request": {"title": long_title},
        })
        result = summarize(event)
        assert "T" * 60 in result
        assert "T" * 61 not in result

    def test_create_event_with_ref(self):
        event = _event("CreateEvent", {"ref_type": "branch", "ref": "feature/foo"})
        result = summarize(event)
        assert "branch created" in result
        assert "feature/foo" in result

    def test_create_event_without_ref(self):
        event = _event("CreateEvent", {"ref_type": "repository", "ref": ""})
        result = summarize(event)
        assert "repository created" in result

    def test_release_event(self):
        event = _event("ReleaseEvent", {
            "release": {"tag_name": "v1.0.0", "name": "First Release"}
        })
        result = summarize(event)
        assert "release v1.0.0" in result
        assert "First Release" in result

    def test_issues_event(self):
        event = _event("IssuesEvent", {
            "action": "opened",
            "issue": {"title": "Bug report"},
        })
        result = summarize(event)
        assert "issue opened" in result
        assert "Bug report" in result

    def test_pull_request_review_event(self):
        event = _event("PullRequestReviewEvent", {
            "pull_request": {"title": "My PR"}
        })
        result = summarize(event)
        assert "reviewed" in result
        assert "My PR" in result

    def test_unknown_event_returns_type(self):
        event = _event("WatchEvent")
        result = summarize(event)
        assert result == "WatchEvent"

    def test_none_type_returns_activity(self):
        event = {"type": None, "payload": {}}
        result = summarize(event)
        assert result == "activity"

    def test_push_event_null_payload(self):
        event = {"type": "PushEvent", "payload": None}
        result = summarize(event)
        # payload or {} handles None
        assert "commit pushed" in result

    def test_pull_request_event_null_pr(self):
        event = _event("PullRequestEvent", {"action": "closed", "pull_request": None})
        result = summarize(event)
        assert "PR closed" in result


# ---------------------------------------------------------------------------
# render_svg
# ---------------------------------------------------------------------------

def _make_event(etype="PushEvent", repo_name="user/repo", created_at="2025-06-10T12:00:00Z"):
    return {
        "type": etype,
        "repo": {"name": repo_name},
        "created_at": created_at,
        "payload": {
            "commits": [{"message": "test commit"}],
        },
    }


class TestRenderSvg:
    def test_returns_svg_string(self):
        svg = render_svg([_make_event()])
        assert svg.startswith("<svg")
        assert "</svg>" in svg

    def test_empty_events_shows_no_activity_message(self):
        svg = render_svg([])
        assert "No recent public activity" in svg

    def test_contains_repo_name(self):
        svg = render_svg([_make_event(repo_name="alice/my-project")])
        assert "alice/my-project" in svg

    def test_limits_to_max_rows(self):
        events = [_make_event(repo_name=f"user/repo{i}") for i in range(10)]
        svg = render_svg(events)
        # Only first 6 should appear
        assert "user/repo5" in svg
        assert "user/repo6" not in svg

    def test_contains_live_event_stream_header(self):
        svg = render_svg([])
        assert "LIVE EVENT STREAM" in svg

    def test_contains_recent_work_feed_header(self):
        svg = render_svg([])
        assert "RECENT WORK FEED" in svg

    def test_svg_height_increases_with_events(self):
        svg_empty = render_svg([])
        svg_with = render_svg([_make_event()] * 3)
        # Both are valid SVGs; multi-event version is taller
        import re
        def get_height(svg_str):
            m = re.search(r'<svg width="\d+" height="(\d+)"', svg_str)
            return int(m.group(1)) if m else 0
        assert get_height(svg_with) > get_height(svg_empty)

    def test_html_special_chars_in_repo_escaped(self):
        svg = render_svg([_make_event(repo_name="user/repo&<>\"")])
        assert "&amp;" in svg
        assert "&lt;" in svg
        assert "&gt;" in svg
        assert "&quot;" in svg

    def test_invalid_created_at_shows_dash(self):
        event = _make_event(created_at="not-a-date")
        svg = render_svg([event])
        assert "—" in svg

    def test_push_event_icon_present(self):
        svg = render_svg([_make_event(etype="PushEvent")])
        assert "↥" in svg

    def test_unknown_event_type_uses_bullet(self):
        event = _make_event(etype="StarEvent")
        svg = render_svg([event])
        assert "•" in svg

    def test_source_footer_present(self):
        svg = render_svg([])
        assert "GITHUB EVENTS API" in svg
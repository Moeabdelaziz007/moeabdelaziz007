import datetime as dt

import pytest

from scripts.generate_recent_work_feed import humanize, summarize, escape


# --------------------------------------------------------------------------- #
# humanize()
# --------------------------------------------------------------------------- #

class TestHumanize:
    def test_zero_seconds(self):
        assert humanize(dt.timedelta(seconds=0)) == "0s ago"

    def test_negative_delta_treated_as_zero(self):
        # max(0, ...) clamps negatives to 0
        result = humanize(dt.timedelta(seconds=-100))
        assert result == "0s ago"

    def test_seconds_under_60(self):
        assert humanize(dt.timedelta(seconds=45)) == "45s ago"

    def test_exactly_59_seconds(self):
        assert humanize(dt.timedelta(seconds=59)) == "59s ago"

    def test_exactly_60_seconds_is_minutes(self):
        assert humanize(dt.timedelta(seconds=60)) == "1m ago"

    def test_minutes(self):
        assert humanize(dt.timedelta(minutes=30)) == "30m ago"

    def test_exactly_1_hour(self):
        assert humanize(dt.timedelta(hours=1)) == "1h ago"

    def test_hours(self):
        assert humanize(dt.timedelta(hours=5)) == "5h ago"

    def test_exactly_1_day(self):
        assert humanize(dt.timedelta(days=1)) == "1d ago"

    def test_days(self):
        assert humanize(dt.timedelta(days=10)) == "10d ago"

    def test_exactly_30_days_is_months(self):
        assert humanize(dt.timedelta(days=30)) == "1mo ago"

    def test_months(self):
        assert humanize(dt.timedelta(days=60)) == "2mo ago"

    def test_boundary_59_minutes(self):
        assert humanize(dt.timedelta(minutes=59)) == "59m ago"

    def test_boundary_23_hours(self):
        assert humanize(dt.timedelta(hours=23)) == "23h ago"


# --------------------------------------------------------------------------- #
# summarize()
# --------------------------------------------------------------------------- #

class TestSummarize:
    def test_push_event_with_commits(self):
        event = {
            "type": "PushEvent",
            "payload": {
                "commits": [
                    {"message": "first commit"},
                    {"message": "second commit"},
                ]
            },
        }
        result = summarize(event)
        assert "2 commit" in result
        assert "second commit" in result

    def test_push_event_single_commit(self):
        event = {
            "type": "PushEvent",
            "payload": {"commits": [{"message": "only commit"}]},
        }
        result = summarize(event)
        assert "1 commit" in result
        assert "s" not in result.split("commit")[0].split()[-1] or "commits" not in result

    def test_push_event_no_commits_fallback(self):
        event = {
            "type": "PushEvent",
            "payload": {"size": 3},
        }
        result = summarize(event)
        assert "3 commit pushed" in result

    def test_push_event_long_message_truncated(self):
        long_msg = "a" * 100
        event = {
            "type": "PushEvent",
            "payload": {"commits": [{"message": long_msg}]},
        }
        result = summarize(event)
        # Message after the first commit marker should be ≤ 60 chars
        parts = result.split("·", 1)
        assert len(parts[1].strip()) <= 60

    def test_pull_request_event(self):
        event = {
            "type": "PullRequestEvent",
            "payload": {
                "action": "opened",
                "pull_request": {"title": "Add feature X"},
            },
        }
        result = summarize(event)
        assert "PR opened" in result
        assert "Add feature X" in result

    def test_create_event_with_ref(self):
        event = {
            "type": "CreateEvent",
            "payload": {"ref_type": "branch", "ref": "feature/my-branch"},
        }
        result = summarize(event)
        assert "branch created" in result
        assert "feature/my-branch" in result

    def test_create_event_no_ref(self):
        event = {
            "type": "CreateEvent",
            "payload": {"ref_type": "repository", "ref": ""},
        }
        result = summarize(event)
        assert "repository created" in result

    def test_release_event(self):
        event = {
            "type": "ReleaseEvent",
            "payload": {
                "release": {"tag_name": "v1.2.3", "name": "Version 1.2.3"},
            },
        }
        result = summarize(event)
        assert "v1.2.3" in result
        assert "Version 1.2.3" in result

    def test_issues_event(self):
        event = {
            "type": "IssuesEvent",
            "payload": {
                "action": "opened",
                "issue": {"title": "Bug in login"},
            },
        }
        result = summarize(event)
        assert "issue opened" in result
        assert "Bug in login" in result

    def test_pull_request_review_event(self):
        event = {
            "type": "PullRequestReviewEvent",
            "payload": {
                "pull_request": {"title": "Refactor DB layer"},
            },
        }
        result = summarize(event)
        assert "reviewed" in result
        assert "Refactor DB layer" in result

    def test_unknown_event_type_returns_type(self):
        event = {"type": "WatchEvent", "payload": {}}
        assert summarize(event) == "WatchEvent"

    def test_missing_type_returns_activity(self):
        event = {"payload": {}}
        assert summarize(event) == "activity"

    def test_empty_event(self):
        result = summarize({})
        assert result == "activity"

    def test_none_payload_handled(self):
        event = {"type": "PushEvent", "payload": None}
        # payload = None → {} → no commits → size fallback
        result = summarize(event)
        assert "commit pushed" in result


# --------------------------------------------------------------------------- #
# escape()
# --------------------------------------------------------------------------- #

class TestEscape:
    def test_ampersand(self):
        assert escape("a & b") == "a &amp; b"

    def test_less_than(self):
        assert escape("x < y") == "x &lt; y"

    def test_greater_than(self):
        assert escape("x > y") == "x &gt; y"

    def test_double_quote(self):
        assert escape('"hello"') == "&quot;hello&quot;"

    def test_plain_text(self):
        assert escape("no special chars") == "no special chars"

    def test_non_string_coerced(self):
        assert escape(123) == "123"

    def test_empty_string(self):
        assert escape("") == ""

    def test_xss_payload(self):
        result = escape('<img src=x onerror="alert(1)">')
        assert "<" not in result
        assert ">" not in result
        assert '"' not in result
import pytest
import datetime
from scripts.generate_contribution_heatmap import current_streak

def test_current_streak_basic():
    today = datetime.date.today()
    days = [
        {"date": (today - datetime.timedelta(days=2)).strftime("%Y-%m-%d"), "contributionCount": 5},
        {"date": (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d"), "contributionCount": 3},
        {"date": today.strftime("%Y-%m-%d"), "contributionCount": 1},
    ]
    assert current_streak(days) == 3

def test_current_streak_broken():
    today = datetime.date.today()
    days = [
        {"date": (today - datetime.timedelta(days=2)).strftime("%Y-%m-%d"), "contributionCount": 5},
        {"date": (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d"), "contributionCount": 0},
        {"date": today.strftime("%Y-%m-%d"), "contributionCount": 1},
    ]
    assert current_streak(days) == 1

def test_current_streak_future_dates():
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    days = [
        {"date": (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d"), "contributionCount": 5},
        {"date": today.strftime("%Y-%m-%d"), "contributionCount": 3},
        {"date": tomorrow.strftime("%Y-%m-%d"), "contributionCount": 10},
    ]
    # Future dates should be filtered out
    assert current_streak(days) == 2

def test_current_streak_empty():
    assert current_streak([]) == 0

def test_current_streak_all_zero():
    today = datetime.date.today()
    days = [
        {"date": (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d"), "contributionCount": 0},
        {"date": today.strftime("%Y-%m-%d"), "contributionCount": 0},
    ]
    assert current_streak(days) == 0

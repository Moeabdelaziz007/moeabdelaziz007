"""Tests for scripts/lib/github_client.py.

The PR changed type annotations only (Dict/List/Optional → dict/list/X|None).
Tests verify the cache machinery, header construction, and the guard that
returns {} from graphql() when no token is present — all pure-logic paths that
need no network access.
"""

import json
import os
import time
import tempfile

import pytest

from scripts.lib.github_client import GitHubClient, CACHE_TTL_SECONDS


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def make_client(token=None, cache_path=None):
    if cache_path is None:
        # Use a temp file that won't interfere with other runs
        fd, cache_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.unlink(cache_path)  # start empty (file does not exist yet)
    return GitHubClient(token=token, cache_path=cache_path)


# --------------------------------------------------------------------------- #
# __init__ / _load_cache
# --------------------------------------------------------------------------- #

class TestInit:
    def test_token_set_from_argument(self):
        client = make_client(token="tok123")
        assert client.token == "tok123"

    def test_token_none_when_not_provided_and_env_absent(self, monkeypatch):
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        monkeypatch.delenv("GH_TOKEN", raising=False)
        client = make_client(token=None)
        assert client.token is None

    def test_token_falls_back_to_github_token_env(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "envtok")
        monkeypatch.delenv("GH_TOKEN", raising=False)
        client = make_client(token=None)
        assert client.token == "envtok"

    def test_token_falls_back_to_gh_token_env(self, monkeypatch):
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        monkeypatch.setenv("GH_TOKEN", "gh_envtok")
        client = make_client(token=None)
        assert client.token == "gh_envtok"

    def test_explicit_token_overrides_env(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "envtok")
        client = make_client(token="explicit")
        assert client.token == "explicit"

    def test_empty_cache_on_missing_file(self, tmp_path):
        path = str(tmp_path / "nonexistent.json")
        client = GitHubClient(cache_path=path)
        assert client._cache == {}

    def test_valid_cache_file_loaded(self, tmp_path):
        path = str(tmp_path / "cache.json")
        data = {"repos::user": {"ts": time.time(), "value": [{"name": "x"}]}}
        with open(path, "w") as f:
            json.dump(data, f)
        client = GitHubClient(cache_path=path)
        assert "repos::user" in client._cache

    def test_corrupt_cache_file_ignored(self, tmp_path):
        path = str(tmp_path / "cache.json")
        with open(path, "w") as f:
            f.write("not json {{{}}")
        client = GitHubClient(cache_path=path)
        assert client._cache == {}

    def test_non_dict_cache_file_ignored(self, tmp_path):
        path = str(tmp_path / "cache.json")
        with open(path, "w") as f:
            json.dump([1, 2, 3], f)
        client = GitHubClient(cache_path=path)
        assert client._cache == {}


# --------------------------------------------------------------------------- #
# _cache_get / _cache_set
# --------------------------------------------------------------------------- #

class TestCacheGetSet:
    def test_set_and_get_fresh_value(self, tmp_path):
        client = GitHubClient(cache_path=str(tmp_path / "c.json"))
        client._cache_set("mykey", {"data": 42})
        result = client._cache_get("mykey")
        assert result == {"data": 42}

    def test_get_missing_key_returns_none(self, tmp_path):
        client = GitHubClient(cache_path=str(tmp_path / "c.json"))
        assert client._cache_get("nonexistent") is None

    def test_get_expired_entry_returns_none(self, tmp_path):
        client = GitHubClient(cache_path=str(tmp_path / "c.json"))
        # Write an entry with a timestamp far in the past
        client._cache["oldkey"] = {"ts": time.time() - CACHE_TTL_SECONDS - 1, "value": "stale"}
        assert client._cache_get("oldkey") is None

    def test_get_fresh_entry_returns_value(self, tmp_path):
        client = GitHubClient(cache_path=str(tmp_path / "c.json"))
        client._cache["freshkey"] = {"ts": time.time(), "value": "fresh"}
        assert client._cache_get("freshkey") == "fresh"

    def test_set_persists_to_file(self, tmp_path):
        path = str(tmp_path / "c.json")
        client = GitHubClient(cache_path=path)
        client._cache_set("persist", [1, 2, 3])
        # Read from disk
        with open(path) as f:
            on_disk = json.load(f)
        assert "persist" in on_disk
        assert on_disk["persist"]["value"] == [1, 2, 3]

    def test_set_overwrites_existing(self, tmp_path):
        client = GitHubClient(cache_path=str(tmp_path / "c.json"))
        client._cache_set("k", "first")
        client._cache_set("k", "second")
        assert client._cache_get("k") == "second"

    def test_cache_none_value_handled(self, tmp_path):
        """Storing None should not crash; retrieval returns None like a miss."""
        client = GitHubClient(cache_path=str(tmp_path / "c.json"))
        # _cache_set stores anything; _cache_get checks entry truthiness
        client._cache["nullkey"] = {"ts": time.time(), "value": None}
        # entry is truthy (dict), value is None — _cache_get returns None (from .get("value"))
        result = client._cache_get("nullkey")
        assert result is None


# --------------------------------------------------------------------------- #
# _headers()
# --------------------------------------------------------------------------- #

class TestHeaders:
    def test_headers_without_token(self, monkeypatch):
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        monkeypatch.delenv("GH_TOKEN", raising=False)
        client = make_client(token=None)
        h = client._headers()
        assert "Authorization" not in h
        assert h["Accept"] == "application/vnd.github+json"
        assert "User-Agent" in h

    def test_headers_with_token(self):
        client = make_client(token="mytoken")
        h = client._headers()
        assert h["Authorization"] == "Bearer mytoken"

    def test_custom_accept(self):
        client = make_client(token="tok")
        h = client._headers(accept="application/json")
        assert h["Accept"] == "application/json"

    def test_github_api_version_header_present(self):
        client = make_client(token="tok")
        h = client._headers()
        assert "X-GitHub-Api-Version" in h


# --------------------------------------------------------------------------- #
# graphql() — returns {} when no token
# --------------------------------------------------------------------------- #

class TestGraphqlNoToken:
    def test_returns_empty_dict_without_token(self, monkeypatch):
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        monkeypatch.delenv("GH_TOKEN", raising=False)
        client = make_client(token=None)
        result = client.graphql("{ viewer { login } }")
        assert result == {}

    def test_returns_empty_dict_without_token_with_variables(self, monkeypatch):
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        monkeypatch.delenv("GH_TOKEN", raising=False)
        client = make_client(token=None)
        result = client.graphql("query($login:String!){user(login:$login){id}}", {"login": "x"})
        assert result == {}


# --------------------------------------------------------------------------- #
# get_repo_languages() — cache hit path
# --------------------------------------------------------------------------- #

class TestGetRepoLanguagesCache:
    def test_returns_cached_value_without_network(self, tmp_path):
        client = GitHubClient(cache_path=str(tmp_path / "c.json"))
        key = "lang::owner/myrepo"
        client._cache[key] = {"ts": time.time(), "value": {"Python": 500}}
        result = client.get_repo_languages("owner", "myrepo")
        assert result == {"Python": 500}


# --------------------------------------------------------------------------- #
# list_user_repos() — cache hit path
# --------------------------------------------------------------------------- #

class TestListUserReposCache:
    def test_returns_cached_repos_without_network(self, tmp_path):
        client = GitHubClient(cache_path=str(tmp_path / "c.json"))
        key = "repos::testuser"
        cached_repos = [{"name": "repo1", "fork": False, "archived": False}]
        client._cache[key] = {"ts": time.time(), "value": cached_repos}
        result = client.list_user_repos("testuser")
        assert result == cached_repos


# --------------------------------------------------------------------------- #
# contribution_calendar() — cache hit path
# --------------------------------------------------------------------------- #

class TestContributionCalendarCache:
    def test_returns_cached_calendar_without_network(self, tmp_path):
        client = GitHubClient(cache_path=str(tmp_path / "c.json"))
        key = "contrib::testuser"
        cached = {"totalCommitContributions": 42}
        client._cache[key] = {"ts": time.time(), "value": cached}
        result = client.contribution_calendar("testuser")
        assert result == cached
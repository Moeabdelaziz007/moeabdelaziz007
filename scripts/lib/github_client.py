"""Lightweight GitHub API client used by the dashboard generators.

Designed to run inside a GitHub Actions workflow with the default
``GITHUB_TOKEN`` available in the environment. Falls back to anonymous
requests (with a much lower rate limit) when no token is present.

The client adds a small on-disk cache so repeated runs in the same
workflow share work, and so that local development does not burn through
rate limit quota while iterating.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

GITHUB_API = "https://api.github.com"
GITHUB_GRAPHQL = "https://api.github.com/graphql"
CACHE_PATH = "/tmp/gh_profile_cache.json"
CACHE_TTL_SECONDS = 60 * 30  # 30 minutes


class GitHubClient:
    def __init__(self, token: Optional[str] = None, cache_path: str = CACHE_PATH):
        self.token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        self.cache_path = cache_path
        self._cache = self._load_cache()

    # ---------------------------------------------------------------- cache
    def _load_cache(self) -> Dict[str, Any]:
        try:
            with open(self.cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except (OSError, json.JSONDecodeError):
            pass
        return {}

    def _save_cache(self) -> None:
        try:
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(self._cache, f)
        except OSError:
            pass

    def _cache_get(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if not entry:
            return None
        if time.time() - entry.get("ts", 0) > CACHE_TTL_SECONDS:
            return None
        return entry.get("value")

    def _cache_set(self, key: str, value: Any) -> None:
        self._cache[key] = {"ts": time.time(), "value": value}
        self._save_cache()

    # -------------------------------------------------------- http transport
    def _headers(self, accept: str = "application/vnd.github+json") -> Dict[str, str]:
        headers = {
            "Accept": accept,
            "User-Agent": "moeabdelaziz007-profile-bot",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(self, url: str, *, method: str = "GET", data: Optional[bytes] = None,
                 headers: Optional[Dict[str, str]] = None) -> Any:
        req = urllib.request.Request(url, data=data, method=method,
                                     headers=headers or self._headers())
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                payload = resp.read().decode("utf-8")
                return json.loads(payload) if payload else {}
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub API {method} {url} -> {exc.code}: {body}") from exc

    # ----------------------------------------------------------------- REST
    def list_user_repos(self, username: str) -> List[Dict[str, Any]]:
        cache_key = f"repos::{username}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            return cached

        results: List[Dict[str, Any]] = []
        page = 1
        while True:
            url = (
                f"{GITHUB_API}/users/{urllib.parse.quote(username)}/repos"
                f"?per_page=100&type=owner&sort=updated&page={page}"
            )
            batch = self._request(url)
            if not isinstance(batch, list) or not batch:
                break
            results.extend(batch)
            if len(batch) < 100:
                break
            page += 1
            if page > 10:  # hard cap, prevents runaway pagination
                break

        # Strip forks and archived from default consideration but retain flag
        filtered = [r for r in results if not r.get("fork")]
        self._cache_set(cache_key, filtered)
        return filtered

    def get_repo_languages(self, owner: str, repo: str) -> Dict[str, int]:
        cache_key = f"lang::{owner}/{repo}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            return cached
        url = f"{GITHUB_API}/repos/{owner}/{repo}/languages"
        try:
            data = self._request(url)
        except RuntimeError:
            data = {}
        if not isinstance(data, dict):
            data = {}
        self._cache_set(cache_key, data)
        return data

    # --------------------------------------------------------------- GraphQL
    def graphql(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.token:
            # GraphQL endpoint requires authentication.
            return {}
        body = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
        headers = self._headers(accept="application/json")
        headers["Content-Type"] = "application/json"
        try:
            return self._request(GITHUB_GRAPHQL, method="POST", data=body, headers=headers)
        except RuntimeError:
            return {}

    def contribution_calendar(self, username: str) -> Dict[str, Any]:
        cache_key = f"contrib::{username}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            return cached
        query = """
        query($login: String!) {
          user(login: $login) {
            contributionsCollection {
              totalCommitContributions
              totalPullRequestContributions
              totalIssueContributions
              contributionCalendar {
                totalContributions
                weeks {
                  contributionDays {
                    date
                    contributionCount
                    weekday
                  }
                }
              }
            }
          }
        }
        """
        data = self.graphql(query, {"login": username})
        result = data.get("data", {}).get("user", {}).get("contributionsCollection", {})
        self._cache_set(cache_key, result)
        return result

"""Tests for scripts/update_system_status.py.

The PR change: removed local START_TAG / END_TAG overrides so LIVE_DATA_PATTERN
is now compiled from the config-imported values.  These tests verify that the
module-level pattern still matches the correct tags, and that
update_telemetry_svg() generates a valid SVG string.
"""

# Importing any scripts/ module that runs sys.path.insert ensures that the bare
# `from config import ...` inside update_system_status.py can resolve at import time.
import scripts.generate_aix_dashboard  # noqa: F401 — side-effect: adds scripts/ to sys.path

import scripts.update_system_status as uss_mod


# --------------------------------------------------------------------------- #
# LIVE_DATA_PATTERN — verifies the PR change (removed local tag overrides)
# --------------------------------------------------------------------------- #

def test_live_data_pattern_uses_config_tags():
    """Pattern must match the tags imported from config (not a local override)."""
    from scripts.config import START_TAG, END_TAG
    sample = f"{START_TAG}\nsome content\n{END_TAG}"
    assert uss_mod.LIVE_DATA_PATTERN.search(sample) is not None


def test_live_data_pattern_does_not_match_without_tags():
    content = "just some plain text, no markers"
    assert uss_mod.LIVE_DATA_PATTERN.search(content) is None


def test_live_data_pattern_matches_multiline_content():
    from scripts.config import START_TAG, END_TAG
    sample = f"{START_TAG}\nline1\nline2\nline3\n{END_TAG}"
    assert uss_mod.LIVE_DATA_PATTERN.search(sample) is not None


def test_live_data_pattern_replaces_inner_content():
    from scripts.config import START_TAG, END_TAG
    original = f"header\n{START_TAG}\nOLD\n{END_TAG}\nfooter"
    new_content = uss_mod.LIVE_DATA_PATTERN.sub(f"{START_TAG}\nNEW\n{END_TAG}", original)
    assert "OLD" not in new_content
    assert "NEW" in new_content
    assert "header" in new_content
    assert "footer" in new_content


def test_live_data_pattern_start_tag_value():
    """START_TAG imported from config must be the expected HTML comment."""
    from scripts.config import START_TAG
    assert START_TAG == "<!-- START_LIVE_DATA -->"


def test_live_data_pattern_end_tag_value():
    from scripts.config import END_TAG
    assert END_TAG == "<!-- END_LIVE_DATA -->"


# --------------------------------------------------------------------------- #
# update_telemetry_svg()
# --------------------------------------------------------------------------- #

class TestUpdateTelemetrySvg:
    def test_svg_written_to_path(self, tmp_path, monkeypatch):
        """update_telemetry_svg() should write a file to ASSETS_DIR/telemetry.svg."""
        monkeypatch.setattr(uss_mod, "ASSETS_DIR" if hasattr(uss_mod, "ASSETS_DIR") else "_", None, raising=False)
        # Patch os.makedirs and the open call via the module's reference to ASSETS_DIR
        import scripts.update_system_status as mod
        import os

        assets = str(tmp_path / "assets")
        # Temporarily replace ASSETS_DIR in the module's imported namespace is tricky because
        # the function references os.makedirs(ASSETS_DIR, ...) and os.path.join(ASSETS_DIR, ...).
        # Use monkeypatch on the config module to redirect ASSETS_DIR.
        import scripts.config as cfg
        monkeypatch.setattr(cfg, "ASSETS_DIR", assets)
        # Also patch the local binding used inside update_system_status
        # The function body accesses ASSETS_DIR from its global scope (the module's global).
        # The import `from config import ASSETS_DIR` creates a name in the module's global dict.
        monkeypatch.setattr(mod, "ASSETS_DIR", assets, raising=False)

        mod.update_telemetry_svg()

        svg_path = os.path.join(assets, "telemetry.svg")
        assert os.path.exists(svg_path)
        with open(svg_path) as f:
            content = f.read()
        assert "<svg" in content
        assert "</svg>" in content

    def test_svg_contains_data_values(self, tmp_path, monkeypatch):
        """The generated SVG should contain the randomly-generated metric values."""
        import scripts.update_system_status as mod
        import scripts.config as cfg
        import random

        assets = str(tmp_path / "assets")
        monkeypatch.setattr(cfg, "ASSETS_DIR", assets)
        monkeypatch.setattr(mod, "ASSETS_DIR", assets, raising=False)

        # Fix random values so we know what to assert
        monkeypatch.setattr(random, "randint", lambda a, b: a)
        monkeypatch.setattr(random, "uniform", lambda a, b: a)

        mod.update_telemetry_svg()

        import os
        with open(os.path.join(assets, "telemetry.svg")) as f:
            content = f.read()

        # The SVG must contain the fixed randint values (min of each range)
        assert "3500" in content  # visitors min
        assert "80" in content    # agents min
        assert "200" in content   # uptime min

    def test_svg_valid_structure(self, tmp_path, monkeypatch):
        import scripts.update_system_status as mod
        import scripts.config as cfg
        import os

        assets = str(tmp_path / "assets")
        monkeypatch.setattr(cfg, "ASSETS_DIR", assets)
        monkeypatch.setattr(mod, "ASSETS_DIR", assets, raising=False)

        mod.update_telemetry_svg()

        with open(os.path.join(assets, "telemetry.svg")) as f:
            content = f.read()

        assert content.count("<svg") == 1
        assert content.count("</svg>") == 1

    def test_svg_contains_neon_color(self, tmp_path, monkeypatch):
        """The telemetry SVG must use the neon green theme color."""
        import scripts.update_system_status as mod
        import scripts.config as cfg
        import os

        assets = str(tmp_path / "assets")
        monkeypatch.setattr(cfg, "ASSETS_DIR", assets)
        monkeypatch.setattr(mod, "ASSETS_DIR", assets, raising=False)

        mod.update_telemetry_svg()

        with open(os.path.join(assets, "telemetry.svg")) as f:
            content = f.read()

        assert "#39FF14" in content

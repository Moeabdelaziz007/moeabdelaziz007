import base64

import pytest

# generate_avatar.py requires Pillow; skip the entire module if unavailable
PIL = pytest.importorskip("PIL", reason="Pillow not installed")

from scripts.generate_avatar import build_avatar_svg  # noqa: E402


# --------------------------------------------------------------------------- #
# build_avatar_svg()
# --------------------------------------------------------------------------- #

DUMMY_BYTES = b"\xff\xd8\xff\xe0" + b"\x00" * 20  # minimal fake JPEG header bytes


class TestBuildAvatarSvg:
    def test_returns_svg_element(self):
        result = build_avatar_svg(DUMMY_BYTES, size=180)
        assert result.strip().startswith("<svg")
        assert "</svg>" in result

    def test_default_size_180(self):
        result = build_avatar_svg(DUMMY_BYTES)
        assert 'width="180"' in result
        assert 'height="180"' in result

    def test_custom_size_applied(self):
        result = build_avatar_svg(DUMMY_BYTES, size=100)
        assert 'width="100"' in result
        assert 'height="100"' in result

    def test_base64_image_embedded(self):
        result = build_avatar_svg(DUMMY_BYTES, size=180)
        encoded = base64.b64encode(DUMMY_BYTES).decode("ascii")
        assert encoded in result

    def test_clip_path_present(self):
        result = build_avatar_svg(DUMMY_BYTES, size=180)
        assert "avatarClip" in result
        assert "clipPath" in result

    def test_neon_ring_present(self):
        """The SVG should contain the neon green ring (#39FF14)."""
        result = build_avatar_svg(DUMMY_BYTES, size=180)
        assert "#39FF14" in result

    def test_center_calculation(self):
        """clip circle and rings should use size/2 as their center."""
        size = 200
        result = build_avatar_svg(DUMMY_BYTES, size=size)
        center = size / 2
        assert f'cx="{center}"' in result or f'cx="{int(center)}"' in result

    def test_image_href_data_uri(self):
        result = build_avatar_svg(DUMMY_BYTES, size=180)
        assert "data:image/jpeg;base64," in result

    def test_empty_bytes_still_produces_svg(self):
        result = build_avatar_svg(b"", size=180)
        assert "<svg" in result
        assert "</svg>" in result

    def test_viewbox_matches_size(self):
        size = 160
        result = build_avatar_svg(DUMMY_BYTES, size=size)
        assert f'viewBox="0 0 {size} {size}"' in result

    def test_glow_filter_present(self):
        result = build_avatar_svg(DUMMY_BYTES, size=180)
        assert "avatarGlow" in result
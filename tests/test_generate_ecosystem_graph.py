import math

import pytest

from scripts.generate_ecosystem_graph import node_by_id, trim_to_circle, escape, NODES


# --------------------------------------------------------------------------- #
# node_by_id()
# --------------------------------------------------------------------------- #

class TestNodeById:
    def test_finds_iqra(self):
        node = node_by_id("iqra")
        assert node["id"] == "iqra"
        assert node["label"] == "IQRA"

    def test_finds_peripheral_node(self):
        node = node_by_id("aix-format")
        assert node["id"] == "aix-format"

    def test_raises_for_unknown_id(self):
        with pytest.raises(StopIteration):
            node_by_id("nonexistent-node-xyz")

    def test_returns_dict(self):
        node = node_by_id("iqra")
        assert isinstance(node, dict)

    def test_all_nodes_findable(self):
        for node in NODES:
            found = node_by_id(node["id"])
            assert found["id"] == node["id"]


# --------------------------------------------------------------------------- #
# trim_to_circle()
# --------------------------------------------------------------------------- #

class TestTrimToCircle:
    def _node(self, x, y, r):
        return {"x": x, "y": y, "r": r}

    def test_basic_horizontal_trim(self):
        src = self._node(0, 0, 10)
        dst = self._node(100, 0, 10)
        x1, y1, x2, y2 = trim_to_circle(src, dst)
        # x1 should be src.x + r = 10
        assert abs(x1 - 10) < 1e-9
        assert abs(y1) < 1e-9
        # x2 should be dst.x - r = 90
        assert abs(x2 - 90) < 1e-9
        assert abs(y2) < 1e-9

    def test_basic_vertical_trim(self):
        src = self._node(0, 0, 5)
        dst = self._node(0, 100, 5)
        x1, y1, x2, y2 = trim_to_circle(src, dst)
        assert abs(x1) < 1e-9
        assert abs(y1 - 5) < 1e-9
        assert abs(x2) < 1e-9
        assert abs(y2 - 95) < 1e-9

    def test_same_point_returns_unchanged(self):
        src = self._node(50, 50, 10)
        dst = self._node(50, 50, 10)
        x1, y1, x2, y2 = trim_to_circle(src, dst)
        assert x1 == 50
        assert y1 == 50
        assert x2 == 50
        assert y2 == 50

    def test_diagonal_trim(self):
        src = self._node(0, 0, 0)  # radius=0 → start at origin
        dst = self._node(3, 4, 0)  # radius=0 → end at (3,4)
        x1, y1, x2, y2 = trim_to_circle(src, dst)
        assert abs(x1) < 1e-9
        assert abs(y1) < 1e-9
        assert abs(x2 - 3) < 1e-9
        assert abs(y2 - 4) < 1e-9

    def test_returns_four_floats(self):
        src = self._node(0, 0, 5)
        dst = self._node(100, 0, 5)
        result = trim_to_circle(src, dst)
        assert len(result) == 4
        for v in result:
            assert isinstance(v, float)

    def test_trimmed_start_on_circle_boundary(self):
        """The distance from src center to (x1, y1) must equal src radius."""
        src = self._node(0, 0, 20)
        dst = self._node(80, 60, 15)
        x1, y1, x2, y2 = trim_to_circle(src, dst)
        dist_start = math.sqrt(x1 ** 2 + y1 ** 2)
        assert abs(dist_start - 20) < 1e-6

    def test_trimmed_end_on_circle_boundary(self):
        """The distance from dst center to (x2, y2) must equal dst radius."""
        src = self._node(0, 0, 20)
        dst = self._node(80, 60, 15)
        x1, y1, x2, y2 = trim_to_circle(src, dst)
        dist_end = math.sqrt((x2 - 80) ** 2 + (y2 - 60) ** 2)
        assert abs(dist_end - 15) < 1e-6

    def test_asymmetric_radii(self):
        src = self._node(0, 0, 72)   # iqra-like large radius
        dst = self._node(0, 200, 58)  # peripheral-like radius
        x1, y1, x2, y2 = trim_to_circle(src, dst)
        assert abs(y1 - 72) < 1e-9
        assert abs(y2 - (200 - 58)) < 1e-9


# --------------------------------------------------------------------------- #
# escape()
# --------------------------------------------------------------------------- #

class TestEscape:
    def test_ampersand(self):
        assert escape("a & b") == "a &amp; b"

    def test_less_than(self):
        assert escape("a < b") == "a &lt; b"

    def test_greater_than(self):
        assert escape("a > b") == "a &gt; b"

    def test_double_quote(self):
        assert escape('say "hi"') == "say &quot;hi&quot;"

    def test_plain_text_unchanged(self):
        assert escape("hello") == "hello"

    def test_combined_special_chars(self):
        result = escape('<script>alert("xss") & 1</script>')
        assert "&lt;" in result
        assert "&gt;" in result
        assert "&amp;" in result
        assert "&quot;" in result

    def test_non_string_coerced(self):
        assert escape(None) == "None"

    def test_empty_string(self):
        assert escape("") == ""
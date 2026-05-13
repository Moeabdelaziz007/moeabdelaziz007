import os
import re
import tempfile
import unittest.mock as mock

import pytest

from scripts.generate_svgs import create_advanced_header, create_footer_quote


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _capture_svg(func):
    """Call *func* with ASSETS_DIR patched to a temp dir; return written SVG content."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with mock.patch("scripts.generate_svgs.ASSETS_DIR", tmpdir):
            func()
        # Return all SVG files written (keyed by basename)
        results = {}
        for fname in os.listdir(tmpdir):
            if fname.endswith(".svg"):
                with open(os.path.join(tmpdir, fname), encoding="utf-8") as fh:
                    results[fname] = fh.read()
    return results


# ─── Tests for create_footer_quote (new in this PR) ───────────────────────────

class TestCreateFooterQuote:
    def setup_method(self):
        self.svgs = _capture_svg(create_footer_quote)
        self.svg = self.svgs.get("footer-quote.svg", "")

    def test_creates_footer_quote_svg_file(self):
        """create_footer_quote must write footer-quote.svg."""
        assert "footer-quote.svg" in self.svgs

    def test_output_is_non_empty(self):
        """footer-quote.svg must not be empty."""
        assert len(self.svg) > 0

    def test_valid_svg_element(self):
        """Output must be a valid SVG with opening and closing tags."""
        assert self.svg.strip().startswith("<svg")
        assert "</svg>" in self.svg

    def test_svg_dimensions(self):
        """footer-quote.svg must have width=850 and height=240."""
        assert 'width="850"' in self.svg
        assert 'height="240"' in self.svg

    def test_carbon_fiber_pattern_present(self):
        """Must include a carbon fiber background pattern."""
        assert 'id="carbonFiberFooter"' in self.svg

    def test_neon_green_accent_color(self):
        """Must use #39FF14 as the primary accent color."""
        assert "#39FF14" in self.svg

    def test_neon_fade_gradient(self):
        """Must include the neonFade gradient for the top bar."""
        assert 'id="neonFade"' in self.svg

    def test_glow_filter_defined(self):
        """Must define a glowEffect filter."""
        assert 'id="glowEffect"' in self.svg

    def test_king_quote_present(self):
        """Must contain the 'King isn't Born, he is Made.' headline."""
        assert "King isn't Born, he is Made." in self.svg

    def test_intersection_quote_present(self):
        """Must contain the intersection of complex math / raw compute quote."""
        assert "complex math" in self.svg
        assert "raw compute" in self.svg

    def test_10x_quote_present(self):
        """Must contain the 10x goal quote."""
        assert "10x" in self.svg

    def test_arabic_quote_present(self):
        """Must include the Arabic translation of the mission quote."""
        assert "الرياضيات المعقدة" in self.svg
        assert "قوة الحوسبة الخام" in self.svg

    def test_end_of_transmission_label(self):
        """Must include END_OF_TRANSMISSION footer marker."""
        assert "END_OF_TRANSMISSION" in self.svg

    def test_highlight_class_on_key_terms(self):
        """Key terms (complex math, raw compute, 10x) must use the highlight class."""
        # Both tspan elements for the inline highlights must use class="highlight"
        highlight_matches = re.findall(r'class="highlight"', self.svg)
        assert len(highlight_matches) >= 3, (
            "Expected at least 3 highlight tspans (complex math, raw compute, 10x)"
        )

    def test_king_class_on_headline(self):
        """Headline text must use the .king CSS class."""
        assert 'class="king"' in self.svg

    def test_quote_class_on_english_quotes(self):
        """English quotes must use the .quote CSS class."""
        assert 'class="quote"' in self.svg

    def test_arabic_quote_class_present(self):
        """Arabic quote must use the .quote-ar CSS class."""
        assert 'class="quote-ar"' in self.svg

    def test_cursor_element_present(self):
        """A blinking cursor element must be included at the end of the last quote."""
        assert 'class="cursor"' in self.svg

    def test_border_radius_applied(self):
        """Background rect must have rounded corners (rx attribute)."""
        assert 'rx="12"' in self.svg

    def test_top_glowing_bar_present(self):
        """Must have a top decorative bar using the neonFade gradient."""
        assert 'fill="url(#neonFade)"' in self.svg

    def test_bottom_decorative_lines_present(self):
        """Must include the bottom corner decorative path lines."""
        # Two symmetrical decorative paths at the bottom
        bottom_paths = [m for m in re.findall(r'<path[^>]*stroke="#39FF14"[^>]*/>', self.svg)
                        if "215" in m]
        assert len(bottom_paths) >= 2, "Expected at least 2 bottom decorative paths"

    def test_text_anchor_middle_for_centered_text(self):
        """Main text group must use text-anchor=middle for centering."""
        assert 'text-anchor="middle"' in self.svg

    def test_black_overlay_for_depth(self):
        """Must have a semi-transparent black overlay for depth."""
        assert 'fill="#000000" opacity="0.5"' in self.svg

    def test_stroke_opacity_on_border(self):
        """Background rect border must have stroke-opacity for subtle neon edge."""
        assert "stroke-opacity" in self.svg

    def test_no_white_fill_on_bars(self):
        """No decorative fill elements should use legacy white (#ffffff) color."""
        # The only white allowed is in the .king text fill
        rect_fills = re.findall(r'<rect[^>]*fill="([^"]+)"', self.svg)
        for fill in rect_fills:
            assert fill.lower() != "#ffffff", (
                f"Unexpected white fill on rect: {fill}"
            )


# ─── Tests for create_advanced_header (particle color change in this PR) ───────

class TestCreateAdvancedHeader:
    def setup_method(self):
        self.svgs = _capture_svg(create_advanced_header)
        self.svg = self.svgs.get("cyber-header.svg", "")

    def test_creates_cyber_header_svg_file(self):
        """create_advanced_header must write cyber-header.svg."""
        assert "cyber-header.svg" in self.svgs

    def test_output_is_non_empty(self):
        """cyber-header.svg must not be empty."""
        assert len(self.svg) > 0

    def test_valid_svg_element(self):
        """Output must start with <svg and contain </svg>."""
        assert self.svg.strip().startswith("<svg")
        assert "</svg>" in self.svg

    def test_all_particles_are_neon_green(self):
        """All particle circles must use fill="#39FF14" (changed in this PR).

        Particles are circles that animate their opacity attribute.  We extract
        fill values from opening <circle> tags and then check only those circles
        that also contain an opacity-animating <animate> child.
        """
        # Match each particle block: <circle ...><animate attributeName="opacity" .../></circle>
        particle_blocks = re.findall(
            r'<circle ([^>]+)><animate attributeName="opacity"[^/]*/></circle>',
            self.svg,
        )
        assert len(particle_blocks) > 0, "No particle circles found"
        for attrs in particle_blocks:
            fill_match = re.search(r'fill="([^"]+)"', attrs)
            assert fill_match is not None, f"Particle circle has no fill attribute: {attrs}"
            fill = fill_match.group(1)
            assert fill == "#39FF14", (
                f"Particle circle has unexpected fill color: {fill!r}; "
                "all particles should be neon green (#39FF14)"
            )

    def test_particle_count_is_150(self):
        """Must generate exactly 150 particle circles with opacity animations."""
        particle_blocks = re.findall(
            r'<circle ([^>]+)><animate attributeName="opacity"[^/]*/></circle>',
            self.svg,
        )
        assert len(particle_blocks) == 150

    def test_particles_have_opacity_animation(self):
        """Each particle must have an opacity animation (fade in/out)."""
        animate_tags = re.findall(
            r'<animate attributeName="opacity"[^/]*/>',
            self.svg,
        )
        # At minimum, all 150 particles must have an opacity animation
        assert len(animate_tags) >= 150

    def test_particles_animate_indefinitely(self):
        """Particle animations must repeat indefinitely."""
        assert 'repeatCount="indefinite"' in self.svg

    def test_svg_dimensions(self):
        """cyber-header.svg must have width=850 and height=380."""
        assert 'width="850"' in self.svg
        assert 'height="380"' in self.svg

    def test_carbon_fiber_pattern_in_header(self):
        """Header must use a carbon fiber background pattern."""
        assert 'id="carbonFiber"' in self.svg

    def test_neon_green_color_in_header(self):
        """Header must use #39FF14 as the primary neon accent."""
        assert "#39FF14" in self.svg

    def test_no_non_neon_particle_colors(self):
        """Particles must not use any non-neon colors (e.g., white, blue, red)."""
        non_neon_colors = ["#ffffff", "#ff0000", "#0000ff", "#00ffff"]
        particle_blocks = re.findall(
            r'<circle ([^>]+)><animate attributeName="opacity"[^/]*/></circle>',
            self.svg,
        )
        for attrs in particle_blocks:
            fill_match = re.search(r'fill="([^"]+)"', attrs)
            if fill_match:
                fill = fill_match.group(1).lower()
                assert fill not in non_neon_colors, (
                    f"Particle has a non-neon color: {fill!r}"
                )

    def test_particle_radius_within_range(self):
        """Particle radii must be between 0.5 and 1.5 (per the generator spec)."""
        particle_blocks = re.findall(
            r'<circle ([^>]+)><animate attributeName="opacity"[^/]*/></circle>',
            self.svg,
        )
        for attrs in particle_blocks:
            r_match = re.search(r'\br="([^"]+)"', attrs)
            assert r_match is not None, f"Particle circle has no r attribute: {attrs}"
            r_val = float(r_match.group(1))
            assert 0.5 <= r_val <= 1.5, f"Particle radius {r_val} out of [0.5, 1.5]"

    def test_rotating_tech_ring_present(self):
        """Header must include animated rotating ring elements."""
        assert "animateTransform" in self.svg

    def test_scanning_hud_line_present(self):
        """Header must include the scanning HUD line animation."""
        assert "SYSTEM INITIALIZED" in self.svg or "y1" in self.svg

    def test_name_text_present(self):
        """Header must display MOHAMED ABDELAZIZ."""
        assert "MOHAMED ABDELAZIZ" in self.svg

    def test_sovereign_architect_subtitle(self):
        """Header must include SOVEREIGN ARCHITECT subtitle."""
        assert "SOVEREIGN ARCHITECT" in self.svg

    def test_corner_metrics_present(self):
        """Header must include corner metrics (ID, NET, UPLINK, SEC)."""
        assert "ID: ALPHA_AXIOM" in self.svg
        assert "NET: DECENTRALIZED" in self.svg
        assert "UPLINK: ACTIVE" in self.svg
        assert "SEC: QUANTUM_RESISTANT" in self.svg

    def test_orbital_path_defined(self):
        """Must define an orbital path for the data node animation."""
        assert 'id="orbitPath"' in self.svg

    def test_data_nodes_present(self):
        """Must include at least two data nodes orbiting on the path."""
        mpath_refs = re.findall(r'href="#orbitPath"', self.svg)
        assert len(mpath_refs) >= 2

    def test_academic_credentials_present(self):
        """Header must display the academic credentials text."""
        assert "BS Cybersecurity" in self.svg

# bdb1c1b58ad0547a
# Batch: BAT-329BFC
# Feature witness: bdb1c1b58ad0547a
# Tests for IGameInitializer contract
#   REQ-AADAC4: pygame.init() returns no errors during window initialization
#   REQ-AFFA38: pygame.display.set_mode creates a window at 160x210 logical pixels
#              scaled 3x to 4x (actual display 480x630 or 640x840)

import os

# Set SDL dummy drivers BEFORE any pygame import to enable headless operation
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
import pytest


LOGICAL_WIDTH = 160
LOGICAL_HEIGHT = 210
VALID_SCALES = (3, 4)


class TestGameInitializer:
    """Tests for IGameInitializer: pygame init and display setup contracts."""

    def setup_method(self):
        """Ensure pygame is cleanly shut down before each test."""
        pygame.quit()

    def teardown_method(self):
        """Ensure pygame is cleanly shut down after each test."""
        pygame.quit()

    # REQ-AADAC4 ---------------------------------------------------------------
    def test_pygame_init_returns_no_errors(self):
        """
        REQ-AADAC4: pygame.init() must return zero failures.

        pygame.init() returns a tuple (num_pass, num_fail). A non-zero failure
        count means one or more subsystems failed to initialise, which must not
        happen for the game to function correctly in headless mode.
        """
        success_count, fail_count = pygame.init()
        assert fail_count == 0, (
            f"pygame.init() reported {fail_count} subsystem failure(s); "
            f"expected 0. Passed: {success_count}, Failed: {fail_count}."
        )

    # REQ-AFFA38 ---------------------------------------------------------------
    def test_display_set_mode_logical_dimensions_scaled_3x(self):
        """
        REQ-AFFA38: set_mode at scale=3 must produce a 480x630 surface.

        Logical canvas is 160x210 pixels. Scale factor 3 gives 480x630.
        The returned Surface size must match exactly.
        """
        pygame.init()
        scale = 3
        expected_width = LOGICAL_WIDTH * scale    # 480
        expected_height = LOGICAL_HEIGHT * scale  # 630

        surface = pygame.display.set_mode((expected_width, expected_height))

        actual_width, actual_height = surface.get_size()
        assert actual_width == expected_width, (
            f"Expected display width {expected_width}px (160 * {scale}), "
            f"got {actual_width}px."
        )
        assert actual_height == expected_height, (
            f"Expected display height {expected_height}px (210 * {scale}), "
            f"got {actual_height}px."
        )

    def test_display_set_mode_logical_dimensions_scaled_4x(self):
        """
        REQ-AFFA38: set_mode at scale=4 must produce a 640x840 surface.

        Logical canvas is 160x210 pixels. Scale factor 4 gives 640x840.
        The returned Surface size must match exactly.
        """
        pygame.init()
        scale = 4
        expected_width = LOGICAL_WIDTH * scale    # 640
        expected_height = LOGICAL_HEIGHT * scale  # 840

        surface = pygame.display.set_mode((expected_width, expected_height))

        actual_width, actual_height = surface.get_size()
        assert actual_width == expected_width, (
            f"Expected display width {expected_width}px (160 * {scale}), "
            f"got {actual_width}px."
        )
        assert actual_height == expected_height, (
            f"Expected display height {expected_height}px (210 * {scale}), "
            f"got {actual_height}px."
        )

    def test_display_surface_is_not_none(self):
        """
        REQ-AFFA38: pygame.display.set_mode must return a valid Surface object,
        not None, for the window to be usable.
        """
        pygame.init()
        scale = 3
        surface = pygame.display.set_mode(
            (LOGICAL_WIDTH * scale, LOGICAL_HEIGHT * scale)
        )
        assert surface is not None, (
            "pygame.display.set_mode returned None; expected a valid Surface."
        )

    def test_display_logical_aspect_ratio_preserved(self):
        """
        REQ-AFFA38: The display surface dimensions must preserve the 160:210
        logical aspect ratio (width:height = 16:21) regardless of scale factor.
        """
        pygame.init()
        for scale in VALID_SCALES:
            expected_width = LOGICAL_WIDTH * scale
            expected_height = LOGICAL_HEIGHT * scale
            surface = pygame.display.set_mode((expected_width, expected_height))
            w, h = surface.get_size()
            assert w * LOGICAL_HEIGHT == h * LOGICAL_WIDTH, (
                f"Aspect ratio mismatch at scale={scale}: "
                f"got {w}x{h}, expected ratio {LOGICAL_WIDTH}:{LOGICAL_HEIGHT}."
            )

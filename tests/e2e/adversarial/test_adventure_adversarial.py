"""Adversarial tests for adventure.py game loop + render foundation.

Each test is designed to expose a real defect or verify a critical invariant.
All tests run headless via SDL_VIDEODRIVER=dummy (set in conftest.py).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pygame
import pytest

# Ensure project root importable when pytest runs from a sub-directory.
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import adventure  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fresh_pygame():
    """Re-initialise pygame so each test starts from a clean slate."""
    pygame.quit()
    adventure.initialize_pygame()


def _make_logical_surface() -> pygame.Surface:
    return pygame.Surface((adventure.LOGICAL_WIDTH, adventure.LOGICAL_HEIGHT))


def _make_scaled_surface(scale: int = adventure.WINDOW_SCALE) -> pygame.Surface:
    return pygame.Surface((adventure.LOGICAL_WIDTH * scale, adventure.LOGICAL_HEIGHT * scale))


# ---------------------------------------------------------------------------
# a. Game initialisation
# ---------------------------------------------------------------------------

class TestInitialization:

    def test_initialize_pygame_reports_no_subsystem_failures(self):
        """CATCHES: pygame.init() silently failing subsystems masked by ignoring return value."""
        pygame.quit()
        success, fail = adventure.initialize_pygame()
        try:
            assert fail == 0, (
                f"initialize_pygame() reports {fail} failed subsystem(s); "
                f"only {success} succeeded"
            )
        finally:
            pygame.quit()

    def test_create_window_returns_surface_with_correct_pixel_dimensions(self):
        """CATCHES: create_window() applying scale incorrectly (e.g. adding instead of multiplying)."""
        _fresh_pygame()
        try:
            surface = adventure.create_window(scale=2)
            expected = (adventure.LOGICAL_WIDTH * 2, adventure.LOGICAL_HEIGHT * 2)
            assert surface.get_size() == expected, (
                f"Expected window size {expected}, got {surface.get_size()}"
            )
        finally:
            pygame.quit()

    def test_create_window_scale_one_produces_logical_dimensions(self):
        """CATCHES: scale=1 edge case producing wrong size (off-by-one in multiplication)."""
        _fresh_pygame()
        try:
            surface = adventure.create_window(scale=1)
            expected = (adventure.LOGICAL_WIDTH, adventure.LOGICAL_HEIGHT)
            assert surface.get_size() == expected
        finally:
            pygame.quit()

    def test_constants_are_positive_nonzero(self):
        """CATCHES: zero or negative constants causing divide-by-zero or negative rect sizes."""
        assert adventure.LOGICAL_WIDTH > 0
        assert adventure.LOGICAL_HEIGHT > 0
        assert adventure.WALL_THICKNESS > 0
        assert adventure.PLAYER_SIZE > 0
        assert adventure.TARGET_FPS > 0
        assert adventure.WINDOW_SCALE > 0

    def test_wall_thickness_fits_within_logical_dimensions(self):
        """CATCHES: WALL_THICKNESS >= LOGICAL dimension producing fully-blocked playfield."""
        assert adventure.WALL_THICKNESS < adventure.LOGICAL_WIDTH // 2, (
            "WALL_THICKNESS must leave a gap in the centre horizontally"
        )
        assert adventure.WALL_THICKNESS < adventure.LOGICAL_HEIGHT // 2, (
            "WALL_THICKNESS must leave a gap in the centre vertically"
        )


# ---------------------------------------------------------------------------
# b. Game loop logic
# ---------------------------------------------------------------------------

class TestGameLoopLogic:

    def test_quit_event_exits_loop(self):
        """CATCHES: QUIT event not terminating the loop (running flag not set False)."""
        _fresh_pygame()
        surface = adventure.create_window(scale=1)
        calls = {"n": 0}

        def one_quit_then_nothing():
            calls["n"] += 1
            if calls["n"] == 1:
                return [pygame.event.Event(pygame.QUIT)]
            return []

        try:
            adventure.run_game_loop(surface, event_getter=one_quit_then_nothing)
        finally:
            pygame.quit()

        assert calls["n"] >= 1, "event_getter was never called"
        # The loop must have exited; if it hadn't we'd never reach this line
        # (the test would hang). The assertion above just proves the path was taken.

    def test_escape_keydown_exits_loop(self):
        """CATCHES: K_ESCAPE handler checking wrong key constant or wrong event type."""
        _fresh_pygame()
        surface = adventure.create_window(scale=1)
        calls = {"n": 0}

        def one_escape_then_nothing():
            calls["n"] += 1
            if calls["n"] == 1:
                return [pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})]
            return []

        try:
            adventure.run_game_loop(surface, event_getter=one_escape_then_nothing)
        finally:
            pygame.quit()

        assert calls["n"] >= 1

    def test_non_quit_keydown_does_not_exit_loop(self):
        """CATCHES: any KEYDOWN event (not just K_ESCAPE) terminating the game."""
        _fresh_pygame()
        surface = adventure.create_window(scale=1)
        ticks = {"n": 0}

        def events():
            ticks["n"] += 1
            if ticks["n"] == 1:
                # Fire a non-escape key — should NOT stop the loop
                return [pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_LEFT})]
            if ticks["n"] == 2:
                return [pygame.event.Event(pygame.QUIT)]
            return []

        try:
            adventure.run_game_loop(surface, event_getter=events)
        finally:
            pygame.quit()

        assert ticks["n"] >= 2, (
            "Loop exited after a non-ESC keydown; it should have kept running"
        )

    def test_loop_executes_at_least_one_full_render_cycle_before_quit(self):
        """CATCHES: loop aborting before calling draw_room/draw_player on first tick."""
        _fresh_pygame()
        surface = adventure.create_window(scale=1)
        render_calls = {"n": 0}
        original_draw_room = adventure.draw_room

        def counting_draw_room(s, room=None):
            render_calls["n"] += 1
            original_draw_room(s, room)

        adventure.draw_room = counting_draw_room

        def quit_on_first():
            return [pygame.event.Event(pygame.QUIT)]

        try:
            adventure.run_game_loop(surface, event_getter=quit_on_first)
        finally:
            adventure.draw_room = original_draw_room
            pygame.quit()

        assert render_calls["n"] >= 1, (
            "draw_room was never called — render loop never executed a full cycle"
        )

    def test_fps_zero_does_not_crash(self):
        """CATCHES: clock.tick(0) raising an exception (pygame allows it, means uncapped)."""
        _fresh_pygame()
        surface = adventure.create_window(scale=1)

        def one_quit():
            return [pygame.event.Event(pygame.QUIT)]

        try:
            adventure.run_game_loop(surface, fps=0, event_getter=one_quit)
        finally:
            pygame.quit()
        # Reaching here means no exception was raised


# ---------------------------------------------------------------------------
# c. Render foundation
# ---------------------------------------------------------------------------

class TestRenderFoundation:

    def setup_method(self):
        _fresh_pygame()

    def teardown_method(self):
        pygame.quit()

    def test_draw_room_does_not_raise_on_logical_surface(self):
        """CATCHES: draw_room() crashing when given a surface of logical dimensions."""
        s = _make_logical_surface()
        adventure.draw_room(s)  # must not raise

    def test_draw_room_fills_background_color(self):
        """CATCHES: draw_room() not filling background, leaving previous frame artifacts."""
        s = _make_logical_surface()
        adventure.draw_room(s)
        center_x = adventure.LOGICAL_WIDTH // 2
        center_y = adventure.LOGICAL_HEIGHT // 2
        center_color = s.get_at((center_x, center_y))[:3]
        assert center_color == adventure.ROOM_COLOR, (
            f"Centre pixel is {center_color}, expected ROOM_COLOR {adventure.ROOM_COLOR}"
        )

    def test_draw_room_paints_top_wall_with_wall_color(self):
        """CATCHES: top wall rect having wrong y-offset or height, leaving wall unpainted."""
        s = _make_logical_surface()
        adventure.draw_room(s)
        # Row 0 must be entirely WALL_COLOR
        for x in range(adventure.LOGICAL_WIDTH):
            pixel = s.get_at((x, 0))[:3]
            assert pixel == adventure.WALL_COLOR, (
                f"Top wall pixel at ({x}, 0) is {pixel}, expected WALL_COLOR"
            )

    def test_draw_room_paints_bottom_wall_with_wall_color(self):
        """CATCHES: bottom wall rect y-offset off-by-one, leaving exposed row."""
        s = _make_logical_surface()
        adventure.draw_room(s)
        bottom_y = adventure.LOGICAL_HEIGHT - 1
        for x in range(adventure.LOGICAL_WIDTH):
            pixel = s.get_at((x, bottom_y))[:3]
            assert pixel == adventure.WALL_COLOR, (
                f"Bottom wall pixel at ({x}, {bottom_y}) is {pixel}, expected WALL_COLOR"
            )

    def test_draw_room_paints_left_wall_with_wall_color(self):
        """CATCHES: left wall rect width being zero or misaligned."""
        s = _make_logical_surface()
        adventure.draw_room(s)
        for y in range(adventure.LOGICAL_HEIGHT):
            pixel = s.get_at((0, y))[:3]
            assert pixel == adventure.WALL_COLOR, (
                f"Left wall pixel at (0, {y}) is {pixel}, expected WALL_COLOR"
            )

    def test_draw_room_paints_right_wall_with_wall_color(self):
        """CATCHES: right wall x-offset using wrong constant (e.g. width not minus thickness)."""
        s = _make_logical_surface()
        adventure.draw_room(s)
        right_x = adventure.LOGICAL_WIDTH - 1
        for y in range(adventure.LOGICAL_HEIGHT):
            pixel = s.get_at((right_x, y))[:3]
            assert pixel == adventure.WALL_COLOR, (
                f"Right wall pixel at ({right_x}, {y}) is {pixel}, expected WALL_COLOR"
            )

    def test_draw_room_interior_is_not_wall_color(self):
        """CATCHES: entire surface filled with WALL_COLOR, eliminating the playfield."""
        s = _make_logical_surface()
        adventure.draw_room(s)
        interior_x = adventure.WALL_THICKNESS + 1
        interior_y = adventure.WALL_THICKNESS + 1
        pixel = s.get_at((interior_x, interior_y))[:3]
        assert pixel == adventure.ROOM_COLOR, (
            f"Interior pixel at ({interior_x}, {interior_y}) is {pixel}; "
            f"expected ROOM_COLOR — walls may consume the entire playfield"
        )

    def test_draw_player_does_not_raise_at_default_position(self):
        """CATCHES: draw_player() crashing at the computed default x/y."""
        s = _make_logical_surface()
        adventure.draw_player(s)  # must not raise

    def test_draw_player_paints_player_color_at_default_position(self):
        """CATCHES: draw_player() using wrong color constant or wrong rect coordinates."""
        s = _make_logical_surface()
        adventure.draw_room(s)
        adventure.draw_player(s)
        px = adventure.PLAYER_X
        py = adventure.PLAYER_Y
        pixel = s.get_at((px, py))[:3]
        assert pixel == adventure.PLAYER_COLOR, (
            f"Pixel at player origin ({px}, {py}) is {pixel}, "
            f"expected PLAYER_COLOR {adventure.PLAYER_COLOR}"
        )

    def test_run_game_loop_blits_to_unscaled_surface(self):
        """CATCHES: scale=1 surface going through transform.scale path instead of direct blit,
        which would silently pass but skip the optimised code path."""
        _fresh_pygame()
        # Must use create_window so pygame has a display mode set (needed for display.flip)
        surface = adventure.create_window(scale=1)
        captured_pixel = {}

        original_flip = pygame.display.flip

        def flip_and_capture():
            original_flip()
            cx = adventure.LOGICAL_WIDTH // 2
            cy = adventure.LOGICAL_HEIGHT // 2
            captured_pixel["value"] = surface.get_at((cx, cy))[:3]

        pygame.display.flip = flip_and_capture

        def one_quit():
            return [pygame.event.Event(pygame.QUIT)]

        try:
            adventure.run_game_loop(surface, event_getter=one_quit)
        finally:
            pygame.display.flip = original_flip
            pygame.quit()

        assert "value" in captured_pixel, "display.flip was never called — render loop did not execute"
        pixel = captured_pixel["value"]
        assert pixel in (adventure.ROOM_COLOR, adventure.PLAYER_COLOR), (
            f"Centre pixel {pixel} is neither ROOM_COLOR nor PLAYER_COLOR — "
            "blit to unscaled surface may have failed"
        )

    def test_run_game_loop_renders_to_scaled_surface(self):
        """CATCHES: transform.scale path corrupting the output surface on scale>1."""
        _fresh_pygame()
        scale = 3
        # Must use create_window so pygame has a display mode set (needed for display.flip)
        surface = adventure.create_window(scale=scale)
        captured_pixel = {}
        original_flip = pygame.display.flip

        def flip_and_capture():
            original_flip()
            cx = (adventure.LOGICAL_WIDTH * scale) // 2
            cy = (adventure.LOGICAL_HEIGHT * scale) // 2
            captured_pixel["value"] = surface.get_at((cx, cy))[:3]

        pygame.display.flip = flip_and_capture

        def one_quit():
            return [pygame.event.Event(pygame.QUIT)]

        try:
            adventure.run_game_loop(surface, event_getter=one_quit)
        finally:
            pygame.display.flip = original_flip
            pygame.quit()

        assert "value" in captured_pixel, "display.flip was never called"
        pixel = captured_pixel["value"]
        assert pixel in (adventure.ROOM_COLOR, adventure.PLAYER_COLOR), (
            f"Centre pixel {pixel} after scale=3 render is not a game color — "
            "transform.scale may not be writing to the destination surface"
        )


# ---------------------------------------------------------------------------
# d. Edge cases / boundary conditions
# ---------------------------------------------------------------------------

class TestEdgeCases:

    def setup_method(self):
        _fresh_pygame()

    def teardown_method(self):
        pygame.quit()

    def test_draw_player_at_origin_zero_zero(self):
        """CATCHES: draw_player() crashing or refusing to draw at (0, 0)."""
        s = _make_logical_surface()
        adventure.draw_player(s, x=0, y=0)
        pixel = s.get_at((0, 0))[:3]
        assert pixel == adventure.PLAYER_COLOR, (
            "draw_player at (0, 0) did not paint PLAYER_COLOR"
        )

    def test_draw_player_at_far_corner(self):
        """CATCHES: draw_player() crashing when player rect extends to the edge of the surface."""
        s = _make_logical_surface()
        x = adventure.LOGICAL_WIDTH - adventure.PLAYER_SIZE
        y = adventure.LOGICAL_HEIGHT - adventure.PLAYER_SIZE
        adventure.draw_player(s, x=x, y=y)
        pixel = s.get_at((x, y))[:3]
        assert pixel == adventure.PLAYER_COLOR, (
            f"draw_player at bottom-right corner ({x}, {y}) did not paint PLAYER_COLOR"
        )

    def test_player_default_position_is_within_playfield_bounds(self):
        """CATCHES: PLAYER_X/PLAYER_Y placing player partially or fully outside the playfield."""
        assert adventure.PLAYER_X >= 0, "PLAYER_X is negative"
        assert adventure.PLAYER_Y >= 0, "PLAYER_Y is negative"
        assert adventure.PLAYER_X + adventure.PLAYER_SIZE <= adventure.LOGICAL_WIDTH, (
            "Player rect extends beyond right edge of logical surface"
        )
        assert adventure.PLAYER_Y + adventure.PLAYER_SIZE <= adventure.LOGICAL_HEIGHT, (
            "Player rect extends beyond bottom edge of logical surface"
        )

    def test_player_starts_inside_walls_not_overlapping_them(self):
        """CATCHES: player spawning inside a wall, making them invisible or colliding immediately."""
        assert adventure.PLAYER_X >= adventure.WALL_THICKNESS, (
            "Player X origin is inside or overlapping the left wall"
        )
        assert adventure.PLAYER_Y >= adventure.WALL_THICKNESS, (
            "Player Y origin is inside or overlapping the top wall"
        )
        assert adventure.PLAYER_X + adventure.PLAYER_SIZE <= adventure.LOGICAL_WIDTH - adventure.WALL_THICKNESS, (
            "Player right edge overlaps the right wall"
        )
        assert adventure.PLAYER_Y + adventure.PLAYER_SIZE <= adventure.LOGICAL_HEIGHT - adventure.WALL_THICKNESS, (
            "Player bottom edge overlaps the bottom wall"
        )

    def test_event_getter_returning_empty_list_does_not_crash(self):
        """CATCHES: loop crashing on empty event list (e.g. iterating a None)."""
        _fresh_pygame()
        surface = adventure.create_window(scale=1)
        tick = {"n": 0}

        def empty_then_quit():
            tick["n"] += 1
            if tick["n"] <= 3:
                return []
            return [pygame.event.Event(pygame.QUIT)]

        adventure.run_game_loop(surface, event_getter=empty_then_quit)
        pygame.quit()

    def test_multiple_events_in_one_frame_processed_correctly(self):
        """CATCHES: loop breaking out after first event and not processing the quit in the same batch."""
        _fresh_pygame()
        surface = adventure.create_window(scale=1)
        calls = {"n": 0}

        def batch_quit():
            calls["n"] += 1
            if calls["n"] == 1:
                # Both a benign key and the QUIT in the same batch
                return [
                    pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_UP}),
                    pygame.event.Event(pygame.QUIT),
                ]
            return []

        adventure.run_game_loop(surface, event_getter=batch_quit)
        pygame.quit()

        assert calls["n"] >= 1

    def test_draw_room_called_with_small_surface_does_not_crash(self):
        """CATCHES: draw_room() crashing when surface is smaller than WALL_THICKNESS."""
        tiny = pygame.Surface((2, 2))
        # Should not raise; pygame clips drawing operations to surface bounds
        adventure.draw_room(tiny)

    def test_logical_surface_pixel_content_after_one_quit_frame(self):
        """CATCHES: run_game_loop creating the internal logical_surface with wrong dimensions,
        causing the blit/scale path to render nothing recognisable.

        For a scale=1 window the loop takes the direct blit path. We read the pixel
        during the flip call (before pygame.quit invalidates the surface).
        """
        _fresh_pygame()
        surface = adventure.create_window(scale=1)
        captured_pixel = {}
        original_flip = pygame.display.flip

        def flip_and_capture():
            original_flip()
            cx = adventure.LOGICAL_WIDTH // 2
            cy = adventure.LOGICAL_HEIGHT // 2
            captured_pixel["value"] = surface.get_at((cx, cy))[:3]

        pygame.display.flip = flip_and_capture

        def one_quit():
            return [pygame.event.Event(pygame.QUIT)]

        try:
            adventure.run_game_loop(surface, event_getter=one_quit)
        finally:
            pygame.display.flip = original_flip
            pygame.quit()

        assert "value" in captured_pixel, "display.flip was never called — render loop did not execute"
        pixel = captured_pixel["value"]
        assert pixel in (adventure.ROOM_COLOR, adventure.PLAYER_COLOR), (
            f"Centre pixel {pixel} is not a known game color after one render frame — "
            "the internal logical_surface may have been created with wrong dimensions, "
            "causing draw_room/draw_player to miss the target surface"
        )

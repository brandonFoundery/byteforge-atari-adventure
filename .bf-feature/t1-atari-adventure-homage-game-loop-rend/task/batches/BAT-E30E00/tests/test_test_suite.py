# bdb1c1b58ad0547a
# BAT-E30E00 — Tests for REQ-874B54, REQ-915D4B, REQ-B95A16
# Feature: t1-atari-adventure-homage-game-loop-rend
# These tests MUST fail until the production implementation is complete.

import os

# SDL dummy drivers must be set BEFORE any pygame import.
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
import unittest
from unittest.mock import patch, MagicMock

import pygame

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_esc_event() -> pygame.event.Event:
    """Return a synthetic KEYDOWN+K_ESCAPE pygame Event."""
    return pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE, "mod": 0, "unicode": "\x1b", "scancode": 0})


# ---------------------------------------------------------------------------
# REQ-874B54 — Headless init completes without errors
# ---------------------------------------------------------------------------

class TestHeadlessInitNoErrors:
    """REQ-874B54: Test verifies headless pygame initialization completes without errors."""

    def test_headless_init_no_errors(self):
        """
        adventure.initialize() must return (success, fail) where fail == 0
        when running under SDL dummy drivers (headless mode).
        """
        # Import here so that SDL env vars are already set.
        import importlib
        import adventure  # noqa: PLC0415

        # Ensure a clean pygame state for this test.
        pygame.quit()

        success_count, fail_count = adventure.initialize()

        assert isinstance(success_count, int), (
            f"Expected int for success_count, got {type(success_count)}"
        )
        assert isinstance(fail_count, int), (
            f"Expected int for fail_count, got {type(fail_count)}"
        )
        assert fail_count == 0, (
            f"pygame.init() reported {fail_count} subsystem failure(s) in headless mode. "
            f"Successful subsystems: {success_count}."
        )

        # Tear down after test.
        pygame.quit()


# ---------------------------------------------------------------------------
# REQ-915D4B — ESC event causes game loop to exit
# ---------------------------------------------------------------------------

class TestEscExitsGameLoop:
    """REQ-915D4B: Test verifies ESC event causes the game loop to exit."""

    def test_esc_exits_game_loop(self):
        """
        When run_game_loop() receives a KEYDOWN/K_ESCAPE event it must return
        (i.e. not block forever).  A synthetic event list is injected via
        unittest.mock.patch so no real window or user interaction is needed.
        """
        import adventure  # noqa: PLC0415

        # adventure.run_game_loop must exist; this will raise AttributeError if absent,
        # which counts as a failing test until the function is implemented.
        run_game_loop = adventure.run_game_loop  # type: ignore[attr-defined]

        esc_event = _make_esc_event()

        # Patch pygame.event.get to return [ESC_event] on first call, then []
        # so the loop terminates rather than spinning forever.
        call_count = {"n": 0}

        def fake_event_get():
            call_count["n"] += 1
            if call_count["n"] == 1:
                return [esc_event]
            return []

        pygame.init()
        try:
            with patch("pygame.event.get", side_effect=fake_event_get):
                # run_game_loop should return within a finite number of iterations.
                # If it never returns, the test will time-out in CI.
                run_game_loop()
        finally:
            pygame.quit()

        # If we reach here, the loop exited — that is the success condition.
        assert call_count["n"] >= 1, "pygame.event.get was never called; loop did not run."

    def test_esc_exits_game_loop_does_not_call_sys_exit(self):
        """
        run_game_loop() should return cleanly on ESC rather than calling
        sys.exit(), so the caller controls teardown.
        """
        import adventure  # noqa: PLC0415

        run_game_loop = adventure.run_game_loop  # type: ignore[attr-defined]

        esc_event = _make_esc_event()
        call_count = {"n": 0}

        def fake_event_get():
            call_count["n"] += 1
            if call_count["n"] == 1:
                return [esc_event]
            return []

        pygame.init()
        try:
            with patch("pygame.event.get", side_effect=fake_event_get):
                with patch("sys.exit") as mock_exit:
                    run_game_loop()
                    # sys.exit should NOT have been called for a clean loop exit.
                    mock_exit.assert_not_called()
        finally:
            pygame.quit()


# ---------------------------------------------------------------------------
# REQ-B95A16 — Player starting coordinates match deterministic constants
# ---------------------------------------------------------------------------

class TestPlayerStartCoordsMatchConstants:
    """REQ-B95A16: Test asserts player starting coordinates match deterministic constants."""

    # Expected approximate center values derived from the room dimensions.
    # LOGICAL_W=160, LOGICAL_H=210  →  center ≈ (80, 105)
    # The spec says "near 160/2, 210/2" so we allow a tolerance of ±20 pixels.
    _EXPECTED_X_APPROX = 160 // 2   # 80
    _EXPECTED_Y_APPROX = 210 // 2   # 105
    _TOLERANCE = 20

    def test_player_start_coords_match_constants(self):
        """
        adventure.PLAYER_X and adventure.PLAYER_Y must exist and be near the
        room centre (LOGICAL_W/2, LOGICAL_H/2).
        """
        import adventure  # noqa: PLC0415

        # These attributes will not exist until the implementation is added,
        # causing an AttributeError that correctly fails this test.
        player_x = adventure.PLAYER_X  # type: ignore[attr-defined]
        player_y = adventure.PLAYER_Y  # type: ignore[attr-defined]

        assert isinstance(player_x, (int, float)), (
            f"PLAYER_X must be numeric, got {type(player_x)}"
        )
        assert isinstance(player_y, (int, float)), (
            f"PLAYER_Y must be numeric, got {type(player_y)}"
        )

        assert abs(player_x - self._EXPECTED_X_APPROX) <= self._TOLERANCE, (
            f"PLAYER_X={player_x} is not near expected centre "
            f"{self._EXPECTED_X_APPROX} (±{self._TOLERANCE})."
        )
        assert abs(player_y - self._EXPECTED_Y_APPROX) <= self._TOLERANCE, (
            f"PLAYER_Y={player_y} is not near expected centre "
            f"{self._EXPECTED_Y_APPROX} (±{self._TOLERANCE})."
        )

    def test_player_start_coords_are_deterministic(self):
        """
        Re-importing the adventure module must yield the same PLAYER_X / PLAYER_Y
        values each time (no random initialization).
        """
        import importlib
        import adventure  # noqa: PLC0415

        x1 = adventure.PLAYER_X  # type: ignore[attr-defined]
        y1 = adventure.PLAYER_Y  # type: ignore[attr-defined]

        importlib.reload(adventure)

        x2 = adventure.PLAYER_X  # type: ignore[attr-defined]
        y2 = adventure.PLAYER_Y  # type: ignore[attr-defined]

        assert x1 == x2, f"PLAYER_X changed between imports: {x1} → {x2}"
        assert y1 == y2, f"PLAYER_Y changed between imports: {y1} → {y2}"

    def test_player_start_coords_within_logical_bounds(self):
        """
        PLAYER_X and PLAYER_Y must fall within the logical canvas
        (0 <= x < LOGICAL_W, 0 <= y < LOGICAL_H).
        """
        import adventure  # noqa: PLC0415

        player_x = adventure.PLAYER_X  # type: ignore[attr-defined]
        player_y = adventure.PLAYER_Y  # type: ignore[attr-defined]

        assert 0 <= player_x < adventure.LOGICAL_W, (
            f"PLAYER_X={player_x} is outside logical canvas width {adventure.LOGICAL_W}."
        )
        assert 0 <= player_y < adventure.LOGICAL_H, (
            f"PLAYER_Y={player_y} is outside logical canvas height {adventure.LOGICAL_H}."
        )


# ---------------------------------------------------------------------------
# Allow running directly for quick smoke-checks
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))

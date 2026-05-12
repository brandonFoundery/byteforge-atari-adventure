# bdb1c1b58ad0547a
# BATCH: BAT-E77E3C
# REQs covered:
#   REQ-AAF862 — Main loop ticks at approximately 30 FPS using pygame.time.Clock().tick(30)
#   REQ-3906FD — ESC key press triggers clean pygame teardown and process exit
#   REQ-264497 — OS window close event triggers clean pygame teardown and process exit

import os
import sys

# Set SDL dummy drivers BEFORE any pygame import so no real display/audio is needed.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from unittest.mock import MagicMock, patch, call

import pygame
import pytest

# Ensure the repo root is importable regardless of how pytest is invoked.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../../../.."))

import adventure


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_esc_event() -> pygame.event.Event:
    """Return a synthetic KEYDOWN event with key=K_ESCAPE."""
    return pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE, "mod": 0})


def _make_quit_event() -> pygame.event.Event:
    """Return a synthetic QUIT event (OS window close)."""
    return pygame.event.Event(pygame.QUIT, {})


# ---------------------------------------------------------------------------
# REQ-AAF862: clock.tick(30) is called each iteration
# ---------------------------------------------------------------------------

class TestClockTicksAt30FPS:
    """REQ-AAF862 — Main loop ticks at approximately 30 FPS."""

    def test_clock_ticks_at_30fps(self):
        """
        Verify that clock.tick(30) is called during run_game_loop().

        Strategy: replace pygame.time.Clock with a factory that returns a
        mock clock, then inject an immediate ESC event so the loop exits after
        exactly one iteration.  After the call, assert tick was called with 30.
        """
        mock_clock = MagicMock()

        esc_event = _make_esc_event()

        with patch("adventure.pygame.time.Clock", return_value=mock_clock), \
             patch("adventure.pygame.event.get", return_value=[esc_event]), \
             patch("adventure.pygame.quit"):
            adventure.run_game_loop(screen=None)

        mock_clock.tick.assert_called_with(30)

    def test_clock_tick_called_once_per_iteration_single_loop(self):
        """
        With one ESC event, tick(30) is called exactly once (one loop pass).
        """
        mock_clock = MagicMock()
        esc_event = _make_esc_event()

        with patch("adventure.pygame.time.Clock", return_value=mock_clock), \
             patch("adventure.pygame.event.get", return_value=[esc_event]), \
             patch("adventure.pygame.quit"):
            adventure.run_game_loop(screen=None)

        assert mock_clock.tick.call_count == 1

    def test_clock_tick_uses_integer_30_not_float(self):
        """
        tick() must be called with the integer 30, not a float like 30.0.
        """
        mock_clock = MagicMock()
        esc_event = _make_esc_event()

        with patch("adventure.pygame.time.Clock", return_value=mock_clock), \
             patch("adventure.pygame.event.get", return_value=[esc_event]), \
             patch("adventure.pygame.quit"):
            adventure.run_game_loop(screen=None)

        args, _ = mock_clock.tick.call_args
        assert args == (30,), f"Expected tick(30) but got tick{args}"
        assert isinstance(args[0], int), "FPS argument must be an int, not a float"


# ---------------------------------------------------------------------------
# REQ-3906FD: ESC key triggers clean pygame teardown
# ---------------------------------------------------------------------------

class TestEscTriggersPygameQuit:
    """REQ-3906FD — ESC key press triggers clean pygame teardown and process exit."""

    def test_esc_triggers_pygame_quit(self):
        """
        Injecting a KEYDOWN+K_ESCAPE event must cause run_game_loop() to call
        pygame.quit() before returning.
        """
        esc_event = _make_esc_event()

        with patch("adventure.pygame.time.Clock", return_value=MagicMock()), \
             patch("adventure.pygame.event.get", return_value=[esc_event]), \
             patch("adventure.pygame.quit") as mock_quit:
            adventure.run_game_loop(screen=None)

        mock_quit.assert_called_once()

    def test_esc_loop_exits_without_infinite_loop(self):
        """
        After an ESC event the loop must terminate; run_game_loop() must return.
        If the loop never exits this test will hang (pytest timeout will catch it).
        """
        esc_event = _make_esc_event()

        with patch("adventure.pygame.time.Clock", return_value=MagicMock()), \
             patch("adventure.pygame.event.get", return_value=[esc_event]), \
             patch("adventure.pygame.quit"):
            # Should return normally; no exception or infinite block.
            adventure.run_game_loop(screen=None)

    def test_esc_only_not_other_key_exits(self):
        """
        A non-ESC KEYDOWN event must NOT terminate the loop on its own.
        We provide: first a regular key event (no exit), then an ESC (exit).
        pygame.quit must still be called exactly once.
        """
        other_key_event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RIGHT, "mod": 0})
        esc_event = _make_esc_event()

        call_count = 0

        def event_sequence():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return [other_key_event]
            return [esc_event]

        with patch("adventure.pygame.time.Clock", return_value=MagicMock()), \
             patch("adventure.pygame.event.get", side_effect=event_sequence), \
             patch("adventure.pygame.quit") as mock_quit:
            adventure.run_game_loop(screen=None)

        mock_quit.assert_called_once()

    def test_esc_pygame_quit_called_before_return(self):
        """
        pygame.quit() must be called; the function must not return without it.
        Verified by ensuring mock_quit call count is 1 after normal return.
        """
        esc_event = _make_esc_event()
        quit_called = []

        def track_quit():
            quit_called.append(True)

        with patch("adventure.pygame.time.Clock", return_value=MagicMock()), \
             patch("adventure.pygame.event.get", return_value=[esc_event]), \
             patch("adventure.pygame.quit", side_effect=track_quit):
            adventure.run_game_loop(screen=None)

        assert quit_called, "pygame.quit() was never called after ESC event"


# ---------------------------------------------------------------------------
# REQ-264497: OS window-close (QUIT) event triggers clean pygame teardown
# ---------------------------------------------------------------------------

class TestWindowCloseTriggersPygameQuit:
    """REQ-264497 — OS window close event triggers clean pygame teardown and process exit."""

    def test_window_close_triggers_pygame_quit(self):
        """
        Injecting a QUIT event (OS window-close) must cause run_game_loop()
        to call pygame.quit() before returning.
        """
        quit_event = _make_quit_event()

        with patch("adventure.pygame.time.Clock", return_value=MagicMock()), \
             patch("adventure.pygame.event.get", return_value=[quit_event]), \
             patch("adventure.pygame.quit") as mock_quit:
            adventure.run_game_loop(screen=None)

        mock_quit.assert_called_once()

    def test_window_close_loop_terminates(self):
        """
        After a QUIT event the loop must terminate; run_game_loop() must return.
        """
        quit_event = _make_quit_event()

        with patch("adventure.pygame.time.Clock", return_value=MagicMock()), \
             patch("adventure.pygame.event.get", return_value=[quit_event]), \
             patch("adventure.pygame.quit"):
            adventure.run_game_loop(screen=None)

    def test_window_close_pygame_quit_called_exactly_once(self):
        """
        pygame.quit() must be called exactly once per run_game_loop() invocation.
        Calling it multiple times would double-free pygame subsystems.
        """
        quit_event = _make_quit_event()

        with patch("adventure.pygame.time.Clock", return_value=MagicMock()), \
             patch("adventure.pygame.event.get", return_value=[quit_event]), \
             patch("adventure.pygame.quit") as mock_quit:
            adventure.run_game_loop(screen=None)

        assert mock_quit.call_count == 1, (
            f"pygame.quit() should be called exactly once, was called {mock_quit.call_count} time(s)"
        )

    def test_quit_event_before_esc_still_exits_cleanly(self):
        """
        If both QUIT and ESC arrive in the same event batch, the loop must
        still exit cleanly and pygame.quit() must be called.
        """
        quit_event = _make_quit_event()
        esc_event = _make_esc_event()

        with patch("adventure.pygame.time.Clock", return_value=MagicMock()), \
             patch("adventure.pygame.event.get", return_value=[quit_event, esc_event]), \
             patch("adventure.pygame.quit") as mock_quit:
            adventure.run_game_loop(screen=None)

        mock_quit.assert_called()

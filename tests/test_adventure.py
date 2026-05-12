# bdb1c1b58ad0547a
# BAT-E30E00 — Production test suite for adventure.py
# Feature: t1-atari-adventure-homage-game-loop-rend
# Covers: REQ-874B54 (headless init), REQ-915D4B (ESC exits loop), REQ-B95A16 (player coords)

import os

# SDL dummy drivers must be set BEFORE any pygame import.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
from unittest.mock import patch

import pygame
import pytest

import adventure


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_esc_event() -> pygame.event.Event:
    """Return a synthetic KEYDOWN+K_ESCAPE pygame Event."""
    return pygame.event.Event(
        pygame.KEYDOWN,
        {"key": pygame.K_ESCAPE, "mod": 0, "unicode": "\x1b", "scancode": 0},
    )


# ---------------------------------------------------------------------------
# REQ-874B54 — Headless init completes without errors
# ---------------------------------------------------------------------------

def test_headless_init():
    """
    adventure.initialize() must return (success, fail) where fail == 0 when
    running under SDL dummy drivers (headless mode).
    """
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

    pygame.quit()


# ---------------------------------------------------------------------------
# REQ-915D4B — ESC event causes game loop to exit
# ---------------------------------------------------------------------------

def test_esc_exits_loop():
    """
    run_game_loop() must return when it receives a KEYDOWN/K_ESCAPE event.
    A synthetic event list is injected via unittest.mock.patch so no real
    window or user interaction is needed.
    """
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
            adventure.run_game_loop()
    finally:
        # run_game_loop calls pygame.quit(); re-init is safe
        pygame.init()
        pygame.quit()

    assert call_count["n"] >= 1, "pygame.event.get was never called; loop did not run."


# ---------------------------------------------------------------------------
# REQ-B95A16 — Player starting coordinates match deterministic constants
# ---------------------------------------------------------------------------

def test_player_start_coords():
    """
    adventure.PLAYER_X and adventure.PLAYER_Y must exist and be near the room
    centre (LOGICAL_W/2, LOGICAL_H/2) within ±20 pixels.
    """
    expected_x = adventure.LOGICAL_W // 2  # 80
    expected_y = adventure.LOGICAL_H // 2  # 105
    tolerance = 20

    assert isinstance(adventure.PLAYER_X, (int, float)), (
        f"PLAYER_X must be numeric, got {type(adventure.PLAYER_X)}"
    )
    assert isinstance(adventure.PLAYER_Y, (int, float)), (
        f"PLAYER_Y must be numeric, got {type(adventure.PLAYER_Y)}"
    )
    assert abs(adventure.PLAYER_X - expected_x) <= tolerance, (
        f"PLAYER_X={adventure.PLAYER_X} is not near expected centre "
        f"{expected_x} (±{tolerance})."
    )
    assert abs(adventure.PLAYER_Y - expected_y) <= tolerance, (
        f"PLAYER_Y={adventure.PLAYER_Y} is not near expected centre "
        f"{expected_y} (±{tolerance})."
    )

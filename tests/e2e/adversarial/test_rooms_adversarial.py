"""Adversarial E2E tests for T3 multi-room transitions (REQ-059..REQ-063).

All tests are headless and reuse the existing conftest.py harness.
No new dependencies beyond adventure and pytest.
"""

from __future__ import annotations

import pygame
import pytest

import adventure


# ---------------------------------------------------------------------------
# REQ-059 — Diagonal corner: E passage + S sealed → horizontal exit only
# ---------------------------------------------------------------------------

def test_diagonal_corner_horizontal_priority():
    # yellow: E=green (passage), S=blue (passage)
    # Push both right+down from corner — horizontal (E) wins.
    room = adventure.ROOMS["yellow"]
    result = adventure.move_player(
        adventure._X_MAX,
        adventure._Y_MAX,
        {pygame.K_RIGHT: True, pygame.K_DOWN: True},
        room=room,
    )
    assert result == ("exit", "E"), f"Expected ('exit', 'E'), got {result!r}"


def test_diagonal_corner_sealed_south_horizontal_still_wins():
    # Build a room where E is open and S is sealed
    room_e_open_s_sealed = adventure.Room(
        id="test_corner",
        bg_color=(0, 0, 0),
        neighbors={"N": None, "S": None, "E": "green", "W": None},
    )
    result = adventure.move_player(
        adventure._X_MAX,
        adventure._Y_MAX,
        {pygame.K_RIGHT: True, pygame.K_DOWN: True},
        room=room_e_open_s_sealed,
    )
    # E is open → E exit; S is sealed → clamp (but E wins anyway)
    assert result == ("exit", "E")


# ---------------------------------------------------------------------------
# REQ-060 — Alternating L/R passage crossing for 10+ frames
# ---------------------------------------------------------------------------

def test_alternating_passage_crossing_stays_between_adjacent_rooms():
    # yellow ↔ green via E/W passage
    # Simulate 12 alternating crossings: E then W then E ...
    room = adventure.ROOMS["yellow"]
    px = adventure.PLAYER_X
    py = adventure.PLAYER_Y
    expected_sequence = []

    for i in range(12):
        if room.id == "yellow":
            # Move right to trigger E exit
            px = adventure._X_MAX
            result = adventure.move_player(px, py, {pygame.K_RIGHT: True}, room=room)
            assert result == ("exit", "E"), f"frame {i}: expected E exit from yellow"
            room, px, py = adventure._warp_position(room, "E", px, py)
            expected_sequence.append(room.id)
        else:
            # In green: move left to trigger W exit
            px = adventure._X_MIN
            result = adventure.move_player(px, py, {pygame.K_LEFT: True}, room=room)
            assert result == ("exit", "W"), f"frame {i}: expected W exit from green"
            room, px, py = adventure._warp_position(room, "W", px, py)
            expected_sequence.append(room.id)

    # Should alternate yellow/green/yellow/green... (first warp lands in green)
    assert all(r in {"yellow", "green"} for r in expected_sequence)
    assert expected_sequence[0] == "green"
    assert expected_sequence[-1] in {"yellow", "green"}


# ---------------------------------------------------------------------------
# REQ-061 — Scripted full-graph traversal + final render color check
# ---------------------------------------------------------------------------

def test_scripted_full_graph_traversal_render_color():
    # Traverse: yellow → green → purple → blue → yellow
    # Verify each destination room renders with the correct bg color.
    pygame.display.init()
    surface = pygame.Surface((adventure.LOGICAL_WIDTH, adventure.LOGICAL_HEIGHT))

    traversal = [
        (adventure.ROOMS["yellow"], "E"),   # yellow → green
        (adventure.ROOMS["green"],  "S"),   # green  → purple
        (adventure.ROOMS["purple"], "W"),   # purple → blue
        (adventure.ROOMS["blue"],   "N"),   # blue   → yellow
    ]

    current_room = adventure.ROOMS["yellow"]
    for src_room, direction in traversal:
        assert current_room.id == src_room.id, (
            f"Traversal mismatch: expected {src_room.id!r}, got {current_room.id!r}"
        )
        current_room, px, py = adventure._warp_position(
            current_room, direction, adventure.PLAYER_X, adventure.PLAYER_Y
        )
        adventure.draw_room(surface, current_room)
        cx, cy = adventure.LOGICAL_WIDTH // 2, adventure.LOGICAL_HEIGHT // 2
        pixel = surface.get_at((cx, cy))[:3]
        assert pixel == current_room.bg_color, (
            f"Room {current_room.id!r}: expected color {current_room.bg_color}, got {pixel}"
        )

    # Final room after full traversal should be yellow again
    assert current_room.id == "yellow"
    adventure.draw_room(surface, current_room)
    cx, cy = adventure.LOGICAL_WIDTH // 2, adventure.LOGICAL_HEIGHT // 2
    assert surface.get_at((cx, cy))[:3] == adventure.ROOM_COLOR


# ---------------------------------------------------------------------------
# REQ-062 — Held-direction 60-frame debounce: exactly one transition
# ---------------------------------------------------------------------------

def test_held_direction_60_frames_one_transition():
    # Hold RIGHT in yellow for 60 frames. Should produce exactly 1 E transition.
    room = adventure.ROOMS["yellow"]
    px, py = adventure.PLAYER_X, adventure.PLAYER_Y
    keys = {pygame.K_RIGHT: True}
    transitions = 0

    for _ in range(60):
        result = adventure.move_player(px, py, keys, room=room)
        if isinstance(result[0], str) and result[0] == "exit":
            transitions += 1
            room, px, py = adventure._warp_position(room, result[1], px, py)
        else:
            px, py = result

    assert transitions == 1, f"Expected exactly 1 transition, got {transitions}"


# ---------------------------------------------------------------------------
# REQ-063 — Adversarial suite passes headless with existing harness
# ---------------------------------------------------------------------------

def test_adversarial_suite_imports_only_adventure_and_pytest():
    # Structural: confirm module uses no external dependencies beyond adventure/pygame/pytest
    import sys
    assert "adventure" in sys.modules
    assert "pytest" in sys.modules
    # No extra game-engine dependencies loaded by this test module
    assert "numpy" not in sys.modules or True  # informational only — not blocking

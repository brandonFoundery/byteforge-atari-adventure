"""Adversarial E2E tests for T3 — Multi-room world + screen transitions.

Targets REQ-001..REQ-063 with emphasis on bugs not caught by existing tests:
 - Room registry invariants (REQ-001..REQ-008)
 - Validator mutation safety (REQ-013)
 - Passage/wall render correctness per room (REQ-021..REQ-024)
 - Warp position math for all four directions (REQ-037..REQ-042)
 - Post-warp loop integration render check (REQ-043..REQ-047)
 - Rapid successive transitions (REQ-060, REQ-062)
 - Full-graph warp BFS (REQ-056)
 - Distinct room colors (REQ-003)
 - Adjacency layout (REQ-005)

Run with:
    pytest tests/e2e/adversarial/test_multiroom_adversarial.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pygame
import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import adventure  # noqa: E402


# ---------------------------------------------------------------------------
# REQ-001 — Room class is a proper dataclass with required attributes
# ---------------------------------------------------------------------------

def test_room_has_id_bg_color_neighbors_attributes():
    """CATCHES: Room class missing a required attribute or using wrong names."""
    room = adventure.ROOMS["yellow"]
    assert hasattr(room, "id"), "Room must have 'id' attribute"
    assert hasattr(room, "bg_color"), "Room must have 'bg_color' attribute"
    assert hasattr(room, "neighbors"), "Room must have 'neighbors' attribute"
    assert room.id == "yellow"
    assert isinstance(room.bg_color, tuple)
    assert isinstance(room.neighbors, dict)


# ---------------------------------------------------------------------------
# REQ-002 — ROOMS registry contains exactly 4 entries with correct keys
# ---------------------------------------------------------------------------

def test_rooms_registry_has_exactly_four_entries():
    """CATCHES: registry having 3 or 5 rooms due to copy-paste omission or addition."""
    assert len(adventure.ROOMS) == 4, (
        f"ROOMS must have exactly 4 entries, found {len(adventure.ROOMS)}: "
        f"{list(adventure.ROOMS.keys())}"
    )


def test_rooms_registry_has_exact_expected_keys():
    """CATCHES: room id mismatch (e.g. 'Gold' instead of 'yellow', or 'red' added)."""
    assert set(adventure.ROOMS.keys()) == {"yellow", "blue", "green", "purple"}, (
        f"ROOMS keys must be exactly yellow/blue/green/purple, "
        f"got {set(adventure.ROOMS.keys())}"
    )


# ---------------------------------------------------------------------------
# REQ-003 — All four bg_color values are pairwise distinct
# ---------------------------------------------------------------------------

def test_all_room_bg_colors_are_distinct():
    """CATCHES: two rooms sharing the same bg_color, making them visually indistinguishable."""
    colors = [room.bg_color for room in adventure.ROOMS.values()]
    assert len(set(colors)) == len(colors), (
        f"Each room must have a unique bg_color; found duplicates in: "
        f"{[f'{r.id}={r.bg_color}' for r in adventure.ROOMS.values()]}"
    )


# ---------------------------------------------------------------------------
# REQ-004 — Each Room.neighbors dict has exactly keys N/S/E/W
# ---------------------------------------------------------------------------

def test_every_room_neighbors_has_exactly_four_direction_keys():
    """CATCHES: a room missing a direction key or having extra/typo'd keys."""
    expected = {"N", "S", "E", "W"}
    for room in adventure.ROOMS.values():
        assert set(room.neighbors.keys()) == expected, (
            f"Room {room.id!r} neighbors must have exactly N/S/E/W keys, "
            f"got {set(room.neighbors.keys())}"
        )


def test_every_room_neighbor_value_is_str_or_none():
    """CATCHES: neighbor values being integers or booleans instead of str or None."""
    for room in adventure.ROOMS.values():
        for direction, neighbor_id in room.neighbors.items():
            assert neighbor_id is None or isinstance(neighbor_id, str), (
                f"Room {room.id!r}.{direction} neighbor must be str or None, "
                f"got {type(neighbor_id)!r}: {neighbor_id!r}"
            )


def test_every_room_non_none_neighbor_points_to_existing_room():
    """CATCHES: neighbor id referencing a room that doesn't exist in ROOMS."""
    for room in adventure.ROOMS.values():
        for direction, neighbor_id in room.neighbors.items():
            if neighbor_id is not None:
                assert neighbor_id in adventure.ROOMS, (
                    f"Room {room.id!r}.{direction} points to {neighbor_id!r} "
                    f"which is not in ROOMS"
                )


# ---------------------------------------------------------------------------
# REQ-005 — Adjacency map matches the 2x2 layout
# ---------------------------------------------------------------------------

def test_yellow_east_is_green():
    """CATCHES: yellow's east neighbor being wrong (e.g. blue or purple)."""
    assert adventure.ROOMS["yellow"].neighbors["E"] == "green", (
        f"yellow.E must be 'green', got {adventure.ROOMS['yellow'].neighbors['E']!r}"
    )


def test_yellow_south_is_blue():
    """CATCHES: yellow's south neighbor being wrong."""
    assert adventure.ROOMS["yellow"].neighbors["S"] == "blue", (
        f"yellow.S must be 'blue', got {adventure.ROOMS['yellow'].neighbors['S']!r}"
    )


def test_green_west_is_yellow():
    """CATCHES: green-yellow connection not being bidirectional."""
    assert adventure.ROOMS["green"].neighbors["W"] == "yellow", (
        f"green.W must be 'yellow', got {adventure.ROOMS['green'].neighbors['W']!r}"
    )


def test_blue_north_is_yellow():
    """CATCHES: blue-yellow connection not being bidirectional."""
    assert adventure.ROOMS["blue"].neighbors["N"] == "yellow", (
        f"blue.N must be 'yellow', got {adventure.ROOMS['blue'].neighbors['N']!r}"
    )


def test_green_south_is_purple():
    """CATCHES: green's south neighbor being wrong."""
    assert adventure.ROOMS["green"].neighbors["S"] == "purple", (
        f"green.S must be 'purple', got {adventure.ROOMS['green'].neighbors['S']!r}"
    )


def test_purple_north_is_green():
    """CATCHES: purple-green connection not being bidirectional."""
    assert adventure.ROOMS["purple"].neighbors["N"] == "green", (
        f"purple.N must be 'green', got {adventure.ROOMS['purple'].neighbors['N']!r}"
    )


def test_purple_west_is_blue():
    """CATCHES: purple's west neighbor being wrong."""
    assert adventure.ROOMS["purple"].neighbors["W"] == "blue", (
        f"purple.W must be 'blue', got {adventure.ROOMS['purple'].neighbors['W']!r}"
    )


def test_blue_east_is_purple():
    """CATCHES: blue-purple connection not being bidirectional."""
    assert adventure.ROOMS["blue"].neighbors["E"] == "purple", (
        f"blue.E must be 'purple', got {adventure.ROOMS['blue'].neighbors['E']!r}"
    )


def test_2x2_outer_sealed_edges():
    """CATCHES: a room missing a sealed edge where the 2x2 layout requires one."""
    # Yellow: N and W are outer edges → must be None
    assert adventure.ROOMS["yellow"].neighbors["N"] is None
    assert adventure.ROOMS["yellow"].neighbors["W"] is None
    # Green: N and E are outer edges → must be None
    assert adventure.ROOMS["green"].neighbors["N"] is None
    assert adventure.ROOMS["green"].neighbors["E"] is None
    # Blue: S and W are outer edges → must be None
    assert adventure.ROOMS["blue"].neighbors["S"] is None
    assert adventure.ROOMS["blue"].neighbors["W"] is None
    # Purple: S and E are outer edges → must be None
    assert adventure.ROOMS["purple"].neighbors["S"] is None
    assert adventure.ROOMS["purple"].neighbors["E"] is None


# ---------------------------------------------------------------------------
# REQ-006 — START_ROOM and yellow bg_color
# ---------------------------------------------------------------------------

def test_start_room_is_yellow():
    """CATCHES: START_ROOM pointing to a different room."""
    assert adventure.START_ROOM == "yellow", (
        f"START_ROOM must be 'yellow', got {adventure.START_ROOM!r}"
    )


def test_yellow_bg_color_matches_spec():
    """CATCHES: yellow room's color changed away from (240, 208, 64)."""
    assert adventure.ROOMS["yellow"].bg_color == (240, 208, 64), (
        f"yellow bg_color must be (240, 208, 64), "
        f"got {adventure.ROOMS['yellow'].bg_color}"
    )


# ---------------------------------------------------------------------------
# REQ-007 — Legacy ROOM_COLOR constant preserved
# ---------------------------------------------------------------------------

def test_room_color_constant_equals_240_208_64():
    """CATCHES: ROOM_COLOR being removed or changed, breaking legacy imports."""
    assert adventure.ROOM_COLOR == (240, 208, 64), (
        f"ROOM_COLOR must be (240, 208, 64), got {adventure.ROOM_COLOR!r}"
    )


# ---------------------------------------------------------------------------
# REQ-009 / REQ-010 — assert_symmetric validator behavior
# ---------------------------------------------------------------------------

def test_assert_symmetric_does_not_raise_on_valid_rooms():
    """CATCHES: assert_symmetric raising a false-positive on a valid registry."""
    adventure.assert_symmetric(adventure.ROOMS)  # must not raise


def test_assert_symmetric_raises_on_one_directional_passage():
    """CATCHES: assert_symmetric failing to detect a missing back-edge."""
    broken = {
        "a": adventure.Room("a", (0, 0, 0), {"N": None, "S": None, "E": "b", "W": None}),
        "b": adventure.Room("b", (1, 1, 1), {"N": None, "S": None, "E": None, "W": None}),  # W should be "a"
    }
    with pytest.raises(ValueError):
        adventure.assert_symmetric(broken)


def test_assert_symmetric_error_message_names_offending_room():
    """CATCHES: ValueError raised with no useful message, making debugging impossible."""
    broken = {
        "red": adventure.Room("red", (255, 0, 0), {"N": None, "S": None, "E": "blue", "W": None}),
        "blue": adventure.Room("blue", (0, 0, 255), {"N": None, "S": None, "E": None, "W": None}),
    }
    with pytest.raises(ValueError) as exc_info:
        adventure.assert_symmetric(broken)
    assert "red" in str(exc_info.value) or "blue" in str(exc_info.value), (
        f"ValueError must name the offending room; got: {exc_info.value!r}"
    )


# ---------------------------------------------------------------------------
# REQ-011 / REQ-012 — assert_connected validator behavior
# ---------------------------------------------------------------------------

def test_assert_connected_does_not_raise_on_valid_rooms():
    """CATCHES: assert_connected raising a false-positive on a fully-connected registry."""
    adventure.assert_connected(adventure.ROOMS, adventure.START_ROOM)  # must not raise


def test_assert_connected_raises_on_isolated_room():
    """CATCHES: assert_connected passing when an island room exists."""
    isolated = {
        "start": adventure.Room("start", (0, 255, 0), {"N": None, "S": None, "E": None, "W": None}),
        "island": adventure.Room("island", (255, 0, 0), {"N": None, "S": None, "E": None, "W": None}),
    }
    with pytest.raises(ValueError):
        adventure.assert_connected(isolated, "start")


def test_assert_connected_error_message_names_unreachable_rooms():
    """CATCHES: ValueError raised without identifying which rooms are unreachable."""
    isolated = {
        "start": adventure.Room("start", (0, 255, 0), {"N": None, "S": None, "E": None, "W": None}),
        "island": adventure.Room("island", (255, 0, 0), {"N": None, "S": None, "E": None, "W": None}),
    }
    with pytest.raises(ValueError) as exc_info:
        adventure.assert_connected(isolated, "start")
    assert "island" in str(exc_info.value), (
        f"ValueError must name unreachable room 'island'; got: {exc_info.value!r}"
    )


# ---------------------------------------------------------------------------
# REQ-013 — Validators must not mutate their argument or module-level ROOMS
# ---------------------------------------------------------------------------

def test_assert_symmetric_does_not_mutate_argument():
    """CATCHES: validator rewriting neighbor values in-place during traversal."""
    snapshot = {
        room_id: dict(room.neighbors)
        for room_id, room in adventure.ROOMS.items()
    }
    adventure.assert_symmetric(adventure.ROOMS)
    for room_id, original_neighbors in snapshot.items():
        assert adventure.ROOMS[room_id].neighbors == original_neighbors, (
            f"assert_symmetric mutated ROOMS[{room_id!r}].neighbors"
        )


def test_assert_connected_does_not_mutate_argument():
    """CATCHES: BFS queue accidentally mutating the rooms dict."""
    snapshot = set(adventure.ROOMS.keys())
    adventure.assert_connected(adventure.ROOMS, adventure.START_ROOM)
    assert set(adventure.ROOMS.keys()) == snapshot, (
        "assert_connected mutated the ROOMS dict keys"
    )


# ---------------------------------------------------------------------------
# REQ-021..REQ-024 — draw_room passage/wall edge rendering per room
# ---------------------------------------------------------------------------

def _surface():
    pygame.display.init()
    return pygame.Surface((adventure.LOGICAL_WIDTH, adventure.LOGICAL_HEIGHT))


def test_draw_room_blue_fills_interior_with_blue_bg_color():
    """CATCHES: draw_room using a hard-coded color instead of room.bg_color."""
    s = _surface()
    adventure.draw_room(s, adventure.ROOMS["blue"])
    cx, cy = adventure.LOGICAL_WIDTH // 2, adventure.LOGICAL_HEIGHT // 2
    pixel = s.get_at((cx, cy))[:3]
    assert pixel == adventure.ROOMS["blue"].bg_color, (
        f"Blue room interior pixel must be {adventure.ROOMS['blue'].bg_color}, got {pixel}"
    )


def test_draw_room_purple_fills_interior_with_purple_bg_color():
    """CATCHES: draw_room using a hard-coded color instead of room.bg_color."""
    s = _surface()
    adventure.draw_room(s, adventure.ROOMS["purple"])
    cx, cy = adventure.LOGICAL_WIDTH // 2, adventure.LOGICAL_HEIGHT // 2
    pixel = s.get_at((cx, cy))[:3]
    assert pixel == adventure.ROOMS["purple"].bg_color, (
        f"Purple room interior pixel must be {adventure.ROOMS['purple'].bg_color}, got {pixel}"
    )


def test_draw_room_green_fills_interior_with_green_bg_color():
    """CATCHES: draw_room using a hard-coded color instead of room.bg_color."""
    s = _surface()
    adventure.draw_room(s, adventure.ROOMS["green"])
    cx, cy = adventure.LOGICAL_WIDTH // 2, adventure.LOGICAL_HEIGHT // 2
    pixel = s.get_at((cx, cy))[:3]
    assert pixel == adventure.ROOMS["green"].bg_color, (
        f"Green room interior pixel must be {adventure.ROOMS['green'].bg_color}, got {pixel}"
    )


def test_draw_room_omits_wall_on_south_passage_in_yellow():
    """CATCHES: draw_room painting a wall on yellow's south edge when it's a passage."""
    # yellow.S = "blue" (passage)
    s = _surface()
    adventure.draw_room(s, adventure.ROOMS["yellow"])
    bottom_mid_x = adventure.LOGICAL_WIDTH // 2
    bottom_y = adventure.LOGICAL_HEIGHT - adventure.WALL_THICKNESS // 2
    pixel = s.get_at((bottom_mid_x, bottom_y))[:3]
    assert pixel == adventure.ROOMS["yellow"].bg_color, (
        f"Yellow south edge (passage) must show bg_color, got {pixel} at ({bottom_mid_x}, {bottom_y})"
    )


def test_draw_room_draws_wall_on_north_sealed_in_yellow():
    """CATCHES: draw_room omitting a wall on yellow's north sealed edge."""
    # yellow.N = None (sealed)
    s = _surface()
    adventure.draw_room(s, adventure.ROOMS["yellow"])
    top_y = adventure.WALL_THICKNESS // 2
    mid_x = adventure.LOGICAL_WIDTH // 2
    pixel = s.get_at((mid_x, top_y))[:3]
    assert pixel == adventure.WALL_COLOR, (
        f"Yellow north edge (sealed) must show WALL_COLOR, got {pixel}"
    )


def test_draw_room_draws_wall_on_east_sealed_in_green():
    """CATCHES: draw_room omitting east wall in green where E=None."""
    # green.E = None (sealed)
    s = _surface()
    adventure.draw_room(s, adventure.ROOMS["green"])
    right_x = adventure.LOGICAL_WIDTH - adventure.WALL_THICKNESS // 2
    mid_y = adventure.LOGICAL_HEIGHT // 2
    pixel = s.get_at((right_x, mid_y))[:3]
    assert pixel == adventure.WALL_COLOR, (
        f"Green east edge (sealed) must show WALL_COLOR, got {pixel}"
    )


def test_draw_room_omits_wall_on_west_passage_in_green():
    """CATCHES: draw_room painting a wall on green's west edge when it's a passage to yellow."""
    # green.W = "yellow" (passage)
    s = _surface()
    adventure.draw_room(s, adventure.ROOMS["green"])
    left_x = adventure.WALL_THICKNESS // 2
    mid_y = adventure.LOGICAL_HEIGHT // 2
    pixel = s.get_at((left_x, mid_y))[:3]
    assert pixel == adventure.ROOMS["green"].bg_color, (
        f"Green west edge (passage) must show bg_color, got {pixel}"
    )


def test_draw_room_draws_wall_on_south_sealed_in_blue():
    """CATCHES: draw_room omitting south wall in blue where S=None."""
    # blue.S = None (sealed)
    s = _surface()
    adventure.draw_room(s, adventure.ROOMS["blue"])
    bottom_y = adventure.LOGICAL_HEIGHT - adventure.WALL_THICKNESS // 2
    mid_x = adventure.LOGICAL_WIDTH // 2
    pixel = s.get_at((mid_x, bottom_y))[:3]
    assert pixel == adventure.WALL_COLOR, (
        f"Blue south edge (sealed) must show WALL_COLOR, got {pixel}"
    )


def test_draw_room_omits_wall_on_north_passage_in_blue():
    """CATCHES: draw_room painting a wall on blue's north edge when it's a passage to yellow."""
    # blue.N = "yellow" (passage)
    s = _surface()
    adventure.draw_room(s, adventure.ROOMS["blue"])
    top_y = adventure.WALL_THICKNESS // 2
    mid_x = adventure.LOGICAL_WIDTH // 2
    pixel = s.get_at((mid_x, top_y))[:3]
    assert pixel == adventure.ROOMS["blue"].bg_color, (
        f"Blue north edge (passage) must show bg_color, got {pixel}"
    )


# ---------------------------------------------------------------------------
# REQ-025..REQ-027 — run_game_loop current_room starts at START_ROOM
# ---------------------------------------------------------------------------

def test_run_game_loop_first_frame_renders_start_room_color():
    """CATCHES: run_game_loop starting in a room other than START_ROOM on frame 1."""
    pygame.quit()
    adventure.initialize_pygame()
    surface = adventure.create_window(scale=1)
    captured = {}
    original_draw_room = adventure.draw_room

    def capture_first_draw_room(s, room=None):
        if "first" not in captured:
            captured["first"] = room
        original_draw_room(s, room)

    adventure.draw_room = capture_first_draw_room

    def one_quit():
        return [pygame.event.Event(pygame.QUIT)]

    try:
        adventure.run_game_loop(surface, event_getter=one_quit)
    finally:
        adventure.draw_room = original_draw_room
        pygame.quit()

    assert "first" in captured, "draw_room was never called"
    first_room = captured["first"]
    assert first_room is not None, "draw_room called with room=None on first frame"
    assert first_room.id == adventure.START_ROOM, (
        f"First frame must use START_ROOM ({adventure.START_ROOM!r}), "
        f"got {first_room.id!r}"
    )


# ---------------------------------------------------------------------------
# REQ-026 — current_room must not be a module-level attribute
# ---------------------------------------------------------------------------

def test_current_room_is_not_module_attribute_after_import():
    """CATCHES: current_room leaked to module scope."""
    assert not hasattr(adventure, "current_room"), (
        "adventure.current_room must not exist; it is module-scoped (leaked)"
    )


# ---------------------------------------------------------------------------
# REQ-037..REQ-042 — _warp_position exact coordinate math
# ---------------------------------------------------------------------------

def test_warp_east_x_is_x_min_plus_inward_offset():
    """CATCHES: warp east placing player at wrong x (e.g. _X_MAX or 0 instead of _X_MIN+offset)."""
    _, nx, _ = adventure._warp_position(adventure.ROOMS["yellow"], "E", adventure.PLAYER_X, adventure.PLAYER_Y)
    expected = adventure._X_MIN + adventure.INWARD_OFFSET
    assert nx == expected, (
        f"Warp E: x must be _X_MIN+INWARD_OFFSET={expected}, got {nx}"
    )


def test_warp_west_x_is_x_max_minus_inward_offset():
    """CATCHES: warp west placing player at wrong x."""
    _, nx, _ = adventure._warp_position(adventure.ROOMS["green"], "W", adventure.PLAYER_X, adventure.PLAYER_Y)
    expected = adventure._X_MAX - adventure.INWARD_OFFSET
    assert nx == expected, (
        f"Warp W: x must be _X_MAX-INWARD_OFFSET={expected}, got {nx}"
    )


def test_warp_south_y_is_y_min_plus_inward_offset():
    """CATCHES: warp south placing player at wrong y (e.g. _Y_MAX instead of _Y_MIN+offset)."""
    _, _, ny = adventure._warp_position(adventure.ROOMS["yellow"], "S", adventure.PLAYER_X, adventure.PLAYER_Y)
    expected = adventure._Y_MIN + adventure.INWARD_OFFSET
    assert ny == expected, (
        f"Warp S: y must be _Y_MIN+INWARD_OFFSET={expected}, got {ny}"
    )


def test_warp_north_y_is_y_max_minus_inward_offset():
    """CATCHES: warp north placing player at wrong y."""
    _, _, ny = adventure._warp_position(adventure.ROOMS["blue"], "N", adventure.PLAYER_X, adventure.PLAYER_Y)
    expected = adventure._Y_MAX - adventure.INWARD_OFFSET
    assert ny == expected, (
        f"Warp N: y must be _Y_MAX-INWARD_OFFSET={expected}, got {ny}"
    )


def test_warp_east_returns_correct_destination_room():
    """CATCHES: warp returning a room object pointing to the wrong neighbor."""
    new_room, _, _ = adventure._warp_position(adventure.ROOMS["yellow"], "E", adventure.PLAYER_X, adventure.PLAYER_Y)
    assert new_room.id == "green", (
        f"Warp yellow.E must land in 'green', got {new_room.id!r}"
    )


def test_warp_south_returns_correct_destination_room():
    """CATCHES: warp south from yellow landing in wrong room."""
    new_room, _, _ = adventure._warp_position(adventure.ROOMS["yellow"], "S", adventure.PLAYER_X, adventure.PLAYER_Y)
    assert new_room.id == "blue", (
        f"Warp yellow.S must land in 'blue', got {new_room.id!r}"
    )


def test_warp_east_clamps_y_if_out_of_bounds_low():
    """CATCHES: warp not clamping the perpendicular coordinate (y < _Y_MIN after warp)."""
    _, _, ny = adventure._warp_position(adventure.ROOMS["yellow"], "E", adventure.PLAYER_X, adventure._Y_MIN - 10)
    assert ny == adventure._Y_MIN, (
        f"Warp E with y below min: y must clamp to {adventure._Y_MIN}, got {ny}"
    )


def test_warp_east_clamps_y_if_out_of_bounds_high():
    """CATCHES: warp not clamping y above _Y_MAX."""
    _, _, ny = adventure._warp_position(adventure.ROOMS["yellow"], "E", adventure.PLAYER_X, adventure._Y_MAX + 999)
    assert ny == adventure._Y_MAX, (
        f"Warp E with y above max: y must clamp to {adventure._Y_MAX}, got {ny}"
    )


def test_warp_south_clamps_x_if_out_of_bounds():
    """CATCHES: warp south not clamping x into the new room's interior."""
    _, nx, _ = adventure._warp_position(adventure.ROOMS["yellow"], "S", adventure._X_MIN - 100, adventure.PLAYER_Y)
    assert nx == adventure._X_MIN, (
        f"Warp S with x below min: x must clamp to {adventure._X_MIN}, got {nx}"
    )


def test_warp_sealed_edge_raises_value_error():
    """CATCHES: warp through a sealed edge silently succeeding or returning garbage."""
    with pytest.raises(ValueError):
        adventure._warp_position(adventure.ROOMS["yellow"], "N", adventure.PLAYER_X, adventure.PLAYER_Y)


def test_warp_sealed_west_in_yellow_raises():
    """CATCHES: yellow.W is None — warp must refuse."""
    with pytest.raises(ValueError):
        adventure._warp_position(adventure.ROOMS["yellow"], "W", adventure.PLAYER_X, adventure.PLAYER_Y)


def test_warp_invalid_direction_raises():
    """CATCHES: unknown direction string silently returning wrong data."""
    with pytest.raises(ValueError):
        adventure._warp_position(adventure.ROOMS["yellow"], "X", adventure.PLAYER_X, adventure.PLAYER_Y)


def test_inward_offset_constant_equals_player_speed_plus_one():
    """CATCHES: INWARD_OFFSET being a different value, allowing immediate re-transitions."""
    assert adventure.INWARD_OFFSET == adventure.PLAYER_SPEED + 1, (
        f"INWARD_OFFSET must equal PLAYER_SPEED+1={adventure.PLAYER_SPEED + 1}, "
        f"got {adventure.INWARD_OFFSET}"
    )


def test_warp_position_is_deterministic_across_calls():
    """CATCHES: _warp_position producing different results on repeated identical calls (hidden state)."""
    args = (adventure.ROOMS["yellow"], "E", adventure.PLAYER_X, adventure.PLAYER_Y)
    r1 = adventure._warp_position(*args)
    r2 = adventure._warp_position(*args)
    assert r1 == r2, (
        f"_warp_position must be deterministic; got {r1} then {r2}"
    )


# ---------------------------------------------------------------------------
# REQ-043..REQ-047 — Loop integration: transition updates current_room
# ---------------------------------------------------------------------------

def test_run_game_loop_after_transition_renders_new_room_color():
    """CATCHES: game loop failing to update current_room after _warp_position call,
    so the old room color continues to render post-transition."""
    pygame.quit()
    adventure.initialize_pygame()
    surface = adventure.create_window(scale=1)

    frame_count = {"n": 0}
    last_room_drawn = {}
    original_draw_room = adventure.draw_room

    def tracking_draw_room(s, room=None):
        last_room_drawn["room"] = room
        original_draw_room(s, room)

    adventure.draw_room = tracking_draw_room

    # Frame 1: player at right edge of yellow pressing RIGHT → triggers E transition
    # Frame 2: QUIT
    calls = {"n": 0}

    def scripted_events():
        calls["n"] += 1
        if calls["n"] == 2:
            return [pygame.event.Event(pygame.QUIT)]
        return []

    original_move_player = adventure.move_player
    frame_count_inner = {"n": 0}

    def scripted_move_player(x, y, keys_pressed, room=None):
        frame_count_inner["n"] += 1
        if frame_count_inner["n"] == 1:
            # Force an E exit from yellow by spoofing position + key
            return ("exit", "E")
        return original_move_player(x, y, keys_pressed, room=room)

    adventure.move_player = scripted_move_player

    try:
        adventure.run_game_loop(surface, event_getter=scripted_events)
    finally:
        adventure.draw_room = original_draw_room
        adventure.move_player = original_move_player
        pygame.quit()

    assert "room" in last_room_drawn, "draw_room was never called"
    final_room = last_room_drawn["room"]
    assert final_room is not None
    assert final_room.id == "green", (
        f"After yellow.E transition, loop must draw 'green', "
        f"but drew {final_room.id!r}"
    )


def test_run_game_loop_current_room_not_leaked_as_module_attribute_post_loop():
    """CATCHES: run_game_loop leaking current_room to module scope."""
    pygame.quit()
    adventure.initialize_pygame()
    surface = adventure.create_window(scale=1)

    def one_quit():
        return [pygame.event.Event(pygame.QUIT)]

    try:
        adventure.run_game_loop(surface, event_getter=one_quit)
    finally:
        pygame.quit()

    assert not hasattr(adventure, "current_room"), (
        "adventure.current_room must not exist after run_game_loop completes"
    )


# ---------------------------------------------------------------------------
# REQ-046 — Sealed edge leaves current_room unchanged that frame
# ---------------------------------------------------------------------------

def test_sealed_edge_does_not_change_room():
    """CATCHES: sealed edge accidentally triggering a transition or corrupting current_room."""
    room = adventure.ROOMS["yellow"]  # yellow.N = None, yellow.W = None
    # Push against sealed north wall
    result = adventure.move_player(adventure.PLAYER_X, adventure._Y_MIN, {pygame.K_UP: True}, room=room)
    assert not (isinstance(result[0], str) and result[0] == "exit"), (
        f"Sealed north edge must clamp, not emit exit; got {result!r}"
    )
    # Verify position — should be clamped to _Y_MIN
    if isinstance(result[0], int):
        _, ny = result
        assert ny == adventure._Y_MIN, f"y must clamp to _Y_MIN, got {ny}"


# ---------------------------------------------------------------------------
# REQ-055 — No immediate re-transition after warp
# ---------------------------------------------------------------------------

def test_no_immediate_re_transition_east_to_green():
    """CATCHES: INWARD_OFFSET too small so the player immediately re-exits on the very next frame."""
    new_room, nx, ny = adventure._warp_position(adventure.ROOMS["yellow"], "E", adventure._X_MAX, adventure.PLAYER_Y)
    assert new_room.id == "green"
    # Player is now at _X_MIN + INWARD_OFFSET in green. Pressing RIGHT for one frame must NOT exit.
    result = adventure.move_player(nx, ny, {pygame.K_RIGHT: True}, room=new_room)
    is_exit = isinstance(result[0], str) and result[0] == "exit"
    assert not is_exit, (
        f"Immediately after warp into green, one RIGHT press must not re-exit; "
        f"got {result!r} (nx={nx}, INWARD_OFFSET={adventure.INWARD_OFFSET})"
    )


def test_no_immediate_re_transition_west_to_yellow():
    """CATCHES: re-transition after warp W."""
    new_room, nx, ny = adventure._warp_position(adventure.ROOMS["green"], "W", adventure._X_MIN, adventure.PLAYER_Y)
    assert new_room.id == "yellow"
    result = adventure.move_player(nx, ny, {pygame.K_LEFT: True}, room=new_room)
    assert not (isinstance(result[0], str) and result[0] == "exit"), (
        f"Immediately after warp into yellow, one LEFT press must not re-exit; got {result!r}"
    )


def test_no_immediate_re_transition_south_to_blue():
    """CATCHES: re-transition after warp S."""
    new_room, nx, ny = adventure._warp_position(adventure.ROOMS["yellow"], "S", adventure.PLAYER_X, adventure._Y_MAX)
    assert new_room.id == "blue"
    result = adventure.move_player(nx, ny, {pygame.K_DOWN: True}, room=new_room)
    assert not (isinstance(result[0], str) and result[0] == "exit"), (
        f"Immediately after warp into blue, one DOWN press must not re-exit; got {result!r}"
    )


def test_no_immediate_re_transition_north_to_yellow():
    """CATCHES: re-transition after warp N."""
    new_room, nx, ny = adventure._warp_position(adventure.ROOMS["blue"], "N", adventure.PLAYER_X, adventure._Y_MIN)
    assert new_room.id == "yellow"
    result = adventure.move_player(nx, ny, {pygame.K_UP: True}, room=new_room)
    assert not (isinstance(result[0], str) and result[0] == "exit"), (
        f"Immediately after warp into yellow, one UP press must not re-exit; got {result!r}"
    )


# ---------------------------------------------------------------------------
# REQ-056 — Full graph walkable via _warp_position BFS
# ---------------------------------------------------------------------------

def test_full_graph_reachable_from_start_via_warp():
    """CATCHES: a room being unreachable via _warp_position (dead-end neighbor not wired correctly)."""
    visited: set[str] = set()
    queue = [adventure.ROOMS[adventure.START_ROOM]]
    while queue:
        room = queue.pop()
        if room.id in visited:
            continue
        visited.add(room.id)
        for direction, neighbor_id in room.neighbors.items():
            if neighbor_id is not None:
                new_room, _, _ = adventure._warp_position(room, direction, adventure.PLAYER_X, adventure.PLAYER_Y)
                if new_room.id not in visited:
                    queue.append(new_room)
    assert visited == set(adventure.ROOMS.keys()), (
        f"All rooms must be reachable via _warp_position BFS from START_ROOM; "
        f"unreachable: {set(adventure.ROOMS.keys()) - visited}"
    )


# ---------------------------------------------------------------------------
# REQ-058 — Sealed edge does not transition; current_room unchanged
# ---------------------------------------------------------------------------

def test_sealed_edge_move_returns_clamped_position_not_exit():
    """CATCHES: sealed edge emitting exit signal instead of clamping coordinates."""
    sealed_room = adventure.Room(
        "sealed_test", (128, 128, 128),
        {"N": None, "S": None, "E": None, "W": None}
    )
    result = adventure.move_player(
        adventure._X_MAX, adventure._Y_MAX,
        {pygame.K_RIGHT: True, pygame.K_DOWN: True},
        room=sealed_room
    )
    assert isinstance(result[0], int), (
        f"Sealed-room move must return (x, y) int tuple, not exit signal; got {result!r}"
    )
    x, y = result
    assert x == adventure._X_MAX
    assert y == adventure._Y_MAX


# ---------------------------------------------------------------------------
# REQ-059 — Diagonal corner: horizontal wins even when both passages open
# ---------------------------------------------------------------------------

def test_diagonal_at_corner_with_both_passages_open_horizontal_wins():
    """CATCHES: vertical axis winning tie-break instead of horizontal (REQ-035 invariant)."""
    # yellow: E=green (open), S=blue (open)
    room = adventure.ROOMS["yellow"]
    result = adventure.move_player(
        adventure._X_MAX, adventure._Y_MAX,
        {pygame.K_RIGHT: True, pygame.K_DOWN: True},
        room=room,
    )
    assert result == ("exit", "E"), (
        f"Diagonal with both E+S open: horizontal (E) must win, got {result!r}"
    )


def test_diagonal_at_corner_with_only_south_open_exits_south():
    """CATCHES: horizontal bias preventing south exit when east is sealed and south is open."""
    room_e_sealed_s_open = adventure.Room(
        "e_sealed_s_open", (0, 0, 0),
        {"N": None, "S": "blue", "E": None, "W": None}
    )
    result = adventure.move_player(
        adventure._X_MAX, adventure._Y_MAX,
        {pygame.K_RIGHT: True, pygame.K_DOWN: True},
        room=room_e_sealed_s_open,
    )
    assert result == ("exit", "S"), (
        f"When E is sealed and S is open, diagonal must exit S; got {result!r}"
    )


# ---------------------------------------------------------------------------
# REQ-062 — Held direction 60+ frames triggers exactly one transition
# ---------------------------------------------------------------------------

def test_holding_right_60_frames_in_yellow_triggers_exactly_one_transition():
    """CATCHES: transition count != 1 over 60 frames (0 = never exits, >1 = thrash)."""
    room = adventure.ROOMS["yellow"]
    px, py = adventure.PLAYER_X, adventure.PLAYER_Y
    keys = {pygame.K_RIGHT: True}
    transition_count = 0

    for _ in range(60):
        result = adventure.move_player(px, py, keys, room=room)
        if isinstance(result[0], str) and result[0] == "exit":
            transition_count += 1
            room, px, py = adventure._warp_position(room, result[1], px, py)
        else:
            px, py = result

    assert transition_count == 1, (
        f"Holding RIGHT for 60 frames from yellow must trigger exactly 1 transition, "
        f"got {transition_count}"
    )


def test_holding_down_60_frames_in_yellow_triggers_exactly_one_transition():
    """CATCHES: south passage transition count != 1 over 60 frames."""
    room = adventure.ROOMS["yellow"]
    px, py = adventure.PLAYER_X, adventure.PLAYER_Y
    keys = {pygame.K_DOWN: True}
    transition_count = 0

    for _ in range(60):
        result = adventure.move_player(px, py, keys, room=room)
        if isinstance(result[0], str) and result[0] == "exit":
            transition_count += 1
            room, px, py = adventure._warp_position(room, result[1], px, py)
        else:
            px, py = result

    assert transition_count == 1, (
        f"Holding DOWN for 60 frames from yellow must trigger exactly 1 transition, "
        f"got {transition_count}"
    )

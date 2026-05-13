import dataclasses

import pygame
import pytest

import adventure


def test_room_dataclass_exists():
    assert hasattr(adventure, "Room")
    assert dataclasses.is_dataclass(adventure.Room)


def test_rooms_registry_has_four_rooms():
    assert hasattr(adventure, "ROOMS")
    assert len(adventure.ROOMS) == 4
    assert set(adventure.ROOMS.keys()) == {"yellow", "blue", "green", "purple"}


def test_start_room_constant():
    assert adventure.START_ROOM == "yellow"


def test_room_color_alias_preserved():
    assert adventure.ROOM_COLOR == (240, 208, 64)


def test_start_room_bg_color_matches_room_color():
    assert adventure.ROOMS[adventure.START_ROOM].bg_color == adventure.ROOM_COLOR


def test_room_is_frozen():
    room = adventure.ROOMS["yellow"]
    with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
        room.id = "changed"


def test_room_neighbors_structure():
    for room in adventure.ROOMS.values():
        assert set(room.neighbors.keys()) == {"N", "S", "E", "W"}


def test_sealed_edge_is_none():
    assert adventure.ROOMS["yellow"].neighbors["N"] is None


def test_passage_edge_is_string():
    assert adventure.ROOMS["yellow"].neighbors["E"] == "green"


def test_assert_symmetric_passes_on_valid_registry():
    adventure.assert_symmetric(adventure.ROOMS)


def test_assert_connected_passes_on_valid_registry():
    adventure.assert_connected(adventure.ROOMS, adventure.START_ROOM)


def test_assert_symmetric_raises_on_asymmetric_registry():
    bad_yellow = adventure.Room(
        id="yellow",
        bg_color=(240, 208, 64),
        neighbors={"N": None, "S": "blue", "E": "green", "W": None},
    )
    bad_blue = adventure.Room(
        id="blue",
        bg_color=(64, 96, 200),
        neighbors={"N": None, "S": None, "E": "purple", "W": None},  # N should be "yellow"
    )
    bad_green = adventure.Room(
        id="green",
        bg_color=(48, 160, 64),
        neighbors={"N": None, "S": "purple", "E": None, "W": "yellow"},
    )
    bad_purple = adventure.Room(
        id="purple",
        bg_color=(144, 64, 176),
        neighbors={"N": "green", "S": None, "E": None, "W": "blue"},
    )
    bad_rooms = {
        "yellow": bad_yellow,
        "blue": bad_blue,
        "green": bad_green,
        "purple": bad_purple,
    }
    with pytest.raises(ValueError):
        adventure.assert_symmetric(bad_rooms)


def test_assert_connected_raises_on_disconnected_registry():
    island = adventure.Room(
        id="island",
        bg_color=(255, 0, 0),
        neighbors={"N": None, "S": None, "E": None, "W": None},
    )
    start = adventure.Room(
        id="start",
        bg_color=(0, 255, 0),
        neighbors={"N": None, "S": None, "E": None, "W": None},
    )
    disconnected_rooms = {"start": start, "island": island}
    with pytest.raises(ValueError):
        adventure.assert_connected(disconnected_rooms, "start")


# ---------------------------------------------------------------------------
# C03 — RoomAwareRendering (REQ-021..030)
# ---------------------------------------------------------------------------

def _headless_surface():
    pygame.display.init()
    return pygame.Surface((adventure.LOGICAL_WIDTH, adventure.LOGICAL_HEIGHT))


def test_draw_room_uses_active_room_color():
    s = _headless_surface()
    adventure.draw_room(s, adventure.ROOMS["blue"])
    cx, cy = adventure.LOGICAL_WIDTH // 2, adventure.LOGICAL_HEIGHT // 2
    assert s.get_at((cx, cy))[:3] == (64, 96, 200)


def test_draw_room_omits_wall_on_passage_edge():
    # yellow.E = "green" (passage) — right edge should show room bg, not wall
    s = _headless_surface()
    adventure.draw_room(s, adventure.ROOMS["yellow"])
    right_x = adventure.LOGICAL_WIDTH - adventure.WALL_THICKNESS // 2
    cy = adventure.LOGICAL_HEIGHT // 2
    assert s.get_at((right_x, cy))[:3] == adventure.ROOMS["yellow"].bg_color


def test_draw_room_draws_wall_on_sealed_edge():
    # yellow.W = None (sealed) — left edge should show wall color
    s = _headless_surface()
    adventure.draw_room(s, adventure.ROOMS["yellow"])
    assert s.get_at((adventure.WALL_THICKNESS // 2, adventure.LOGICAL_HEIGHT // 2))[:3] == adventure.WALL_COLOR


def test_rendered_frame_matches_start_room_bg_color():
    s = _headless_surface()
    adventure.draw_room(s, adventure.ROOMS[adventure.START_ROOM])
    cx, cy = adventure.LOGICAL_WIDTH // 2, adventure.LOGICAL_HEIGHT // 2
    assert s.get_at((cx, cy))[:3] == adventure.ROOM_COLOR


def test_rendered_frame_shows_walls_only_on_sealed_edges_of_start_room():
    # yellow: N=None(wall), W=None(wall), S=blue(open), E=green(open)
    s = _headless_surface()
    adventure.draw_room(s, adventure.ROOMS["yellow"])
    bg = adventure.ROOMS["yellow"].bg_color
    # N sealed → top wall present
    assert s.get_at((adventure.LOGICAL_WIDTH // 2, adventure.WALL_THICKNESS // 2))[:3] == adventure.WALL_COLOR
    # W sealed → left wall present
    assert s.get_at((adventure.WALL_THICKNESS // 2, adventure.LOGICAL_HEIGHT // 2))[:3] == adventure.WALL_COLOR
    # S open → bottom shows bg color
    assert s.get_at((adventure.LOGICAL_WIDTH // 2, adventure.LOGICAL_HEIGHT - adventure.WALL_THICKNESS // 2))[:3] == bg
    # E open → right shows bg color
    assert s.get_at((adventure.LOGICAL_WIDTH - adventure.WALL_THICKNESS // 2, adventure.LOGICAL_HEIGHT // 2))[:3] == bg


def test_no_module_global_current_room():
    assert not hasattr(adventure, "current_room")


# ---------------------------------------------------------------------------
# C04 — RoomAwareMovement (REQ-031..036)
# ---------------------------------------------------------------------------

def _sealed_room():
    return adventure.Room(
        id="sealed",
        bg_color=(0, 0, 0),
        neighbors={"N": None, "S": None, "E": None, "W": None},
    )


def test_move_player_passage_east_emits_exit():
    room = adventure.ROOMS["yellow"]  # yellow.E = "green"
    # Position player at right edge
    result = adventure.move_player(adventure._X_MAX, adventure.PLAYER_Y, {pygame.K_RIGHT: True}, room=room)
    assert result == ("exit", "E")


def test_move_player_passage_west_emits_exit():
    room = adventure.ROOMS["green"]  # green.W = "yellow"
    result = adventure.move_player(adventure._X_MIN, adventure.PLAYER_Y, {pygame.K_LEFT: True}, room=room)
    assert result == ("exit", "W")


def test_move_player_passage_south_emits_exit():
    room = adventure.ROOMS["yellow"]  # yellow.S = "blue"
    result = adventure.move_player(adventure.PLAYER_X, adventure._Y_MAX, {pygame.K_DOWN: True}, room=room)
    assert result == ("exit", "S")


def test_move_player_passage_north_emits_exit():
    room = adventure.ROOMS["blue"]  # blue.N = "yellow"
    result = adventure.move_player(adventure.PLAYER_X, adventure._Y_MIN, {pygame.K_UP: True}, room=room)
    assert result == ("exit", "N")


def test_move_player_sealed_east_clamps():
    room = _sealed_room()
    x, y = adventure.move_player(adventure._X_MAX, adventure.PLAYER_Y, {pygame.K_RIGHT: True}, room=room)
    assert x == adventure._X_MAX


def test_move_player_sealed_west_clamps():
    room = _sealed_room()
    x, y = adventure.move_player(adventure._X_MIN, adventure.PLAYER_Y, {pygame.K_LEFT: True}, room=room)
    assert x == adventure._X_MIN


def test_move_player_diagonal_horizontal_wins():
    # yellow has E=green (passage), S=blue (passage). At corner (E+S), should return E exit.
    room = adventure.ROOMS["yellow"]
    result = adventure.move_player(
        adventure._X_MAX, adventure._Y_MAX,
        {pygame.K_RIGHT: True, pygame.K_DOWN: True},
        room=room,
    )
    assert result == ("exit", "E")


def test_move_player_legacy_mode_still_clamps():
    x, y = adventure.move_player(adventure._X_MAX, adventure.PLAYER_Y, {pygame.K_RIGHT: True})
    assert x == adventure._X_MAX


# ---------------------------------------------------------------------------
# C04 movement reconciliation — sealed-room clamp assertions (REQ-048..052)
# ---------------------------------------------------------------------------

def test_sealed_room_clamp_left():
    room = _sealed_room()
    x, y = adventure.move_player(adventure._X_MIN, adventure.PLAYER_Y, {pygame.K_LEFT: True}, room=room)
    assert x == adventure._X_MIN


def test_sealed_room_clamp_right():
    room = _sealed_room()
    x, y = adventure.move_player(adventure._X_MAX, adventure.PLAYER_Y, {pygame.K_RIGHT: True}, room=room)
    assert x == adventure._X_MAX


def test_sealed_room_clamp_top():
    room = _sealed_room()
    x, y = adventure.move_player(adventure.PLAYER_X, adventure._Y_MIN, {pygame.K_UP: True}, room=room)
    assert y == adventure._Y_MIN


def test_sealed_room_clamp_bottom():
    room = _sealed_room()
    x, y = adventure.move_player(adventure.PLAYER_X, adventure._Y_MAX, {pygame.K_DOWN: True}, room=room)
    assert y == adventure._Y_MAX


def test_no_transition_assertions_in_sealed_room():
    room = _sealed_room()
    result = adventure.move_player(adventure._X_MAX, adventure._Y_MAX, {pygame.K_RIGHT: True, pygame.K_DOWN: True}, room=room)
    # Both axes clamp — no exit signal
    assert isinstance(result[0], int)


# ---------------------------------------------------------------------------
# C05 — TransitionWarpHelper (REQ-037..042, REQ-053..058)
# ---------------------------------------------------------------------------

def test_transition_east_warp_position():
    new_room, nx, ny = adventure._warp_position(adventure.ROOMS["yellow"], "E", adventure.PLAYER_X, adventure.PLAYER_Y)
    assert new_room == adventure.ROOMS["green"]
    assert nx == adventure._X_MIN + adventure.INWARD_OFFSET
    assert adventure._Y_MIN <= ny <= adventure._Y_MAX


def test_transition_west_warp_position():
    new_room, nx, ny = adventure._warp_position(adventure.ROOMS["green"], "W", adventure.PLAYER_X, adventure.PLAYER_Y)
    assert new_room == adventure.ROOMS["yellow"]
    assert nx == adventure._X_MAX - adventure.INWARD_OFFSET
    assert adventure._Y_MIN <= ny <= adventure._Y_MAX


def test_transition_north_warp_position():
    new_room, nx, ny = adventure._warp_position(adventure.ROOMS["blue"], "N", adventure.PLAYER_X, adventure.PLAYER_Y)
    assert new_room == adventure.ROOMS["yellow"]
    assert ny == adventure._Y_MAX - adventure.INWARD_OFFSET
    assert adventure._X_MIN <= nx <= adventure._X_MAX


def test_transition_south_warp_position():
    new_room, nx, ny = adventure._warp_position(adventure.ROOMS["yellow"], "S", adventure.PLAYER_X, adventure.PLAYER_Y)
    assert new_room == adventure.ROOMS["blue"]
    assert ny == adventure._Y_MIN + adventure.INWARD_OFFSET
    assert adventure._X_MIN <= nx <= adventure._X_MAX


def test_sealed_edge_does_not_transition():
    with pytest.raises(ValueError):
        adventure._warp_position(adventure.ROOMS["yellow"], "W", adventure.PLAYER_X, adventure.PLAYER_Y)


def test_no_immediate_re_transition():
    # After warping E (yellow→green), player is at _X_MIN + INWARD_OFFSET
    # One frame of held-right should NOT retrigger exit (INWARD_OFFSET = PLAYER_SPEED + 1)
    _, nx, ny = adventure._warp_position(adventure.ROOMS["yellow"], "E", adventure._X_MAX, adventure.PLAYER_Y)
    result = adventure.move_player(nx, ny, {pygame.K_RIGHT: True}, room=adventure.ROOMS["green"])
    assert not (isinstance(result[0], str) and result[0] == "exit")


def test_full_graph_walkable_from_start():
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
    assert visited == set(adventure.ROOMS.keys())


def test_re_entry_is_deterministic():
    r1 = adventure._warp_position(adventure.ROOMS["yellow"], "E", adventure.PLAYER_X, adventure.PLAYER_Y)
    r2 = adventure._warp_position(adventure.ROOMS["yellow"], "E", adventure.PLAYER_X, adventure.PLAYER_Y)
    assert r1 == r2


def test_warp_perpendicular_clamped():
    # Warp E with y out-of-bounds — should be clamped
    new_room, nx, ny = adventure._warp_position(adventure.ROOMS["yellow"], "E", adventure.PLAYER_X, -999)
    assert ny == adventure._Y_MIN
    new_room, nx, ny = adventure._warp_position(adventure.ROOMS["yellow"], "E", adventure.PLAYER_X, 9999)
    assert ny == adventure._Y_MAX


def test_inward_offset_prevents_immediate_retrigger():
    assert adventure.INWARD_OFFSET == adventure.PLAYER_SPEED + 1


# ---------------------------------------------------------------------------
# C06 — GameLoopIntegration (REQ-015..020, REQ-043..047)
# ---------------------------------------------------------------------------

def test_current_room_is_not_module_attribute():
    assert not hasattr(adventure, "current_room")


def test_run_game_loop_exits_with_validators_passing():
    # Validates that run_game_loop completes without raising (ROOMS is valid)
    pygame.quit()
    adventure.initialize_pygame()
    surface = adventure.create_window(scale=1)
    esc_event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
    calls = {"n": 0}
    def events():
        calls["n"] += 1
        return [esc_event] if calls["n"] == 1 else []
    try:
        adventure.run_game_loop(surface, event_getter=events)
    finally:
        pygame.quit()
    assert calls["n"] >= 1


def test_run_game_loop_renders_start_room_color():
    # scale=1 surface gets blit from logical_surface; sample a pixel away from player
    # (player default position is ~(76,101); sample upper-left interior at (20,20))
    pygame.quit()
    adventure.initialize_pygame()
    surface = adventure.create_window(scale=1)
    esc_event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
    calls = {"n": 0}
    def events():
        calls["n"] += 1
        return [esc_event] if calls["n"] == 1 else []
    try:
        adventure.run_game_loop(surface, event_getter=events)
    finally:
        # Sample inside the room but well away from the player spawn position
        sample_x = adventure.WALL_THICKNESS + 5
        sample_y = adventure.WALL_THICKNESS + 5
        pixel = surface.get_at((sample_x, sample_y))[:3]
        pygame.quit()
    assert pixel == adventure.ROOM_COLOR


def test_module_has_no_current_room_after_loop():
    # current_room must remain function-local even after run_game_loop completes
    pygame.quit()
    adventure.initialize_pygame()
    surface = adventure.create_window(scale=1)
    esc_event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
    calls = {"n": 0}
    def events():
        calls["n"] += 1
        return [esc_event] if calls["n"] == 1 else []
    try:
        adventure.run_game_loop(surface, event_getter=events)
    finally:
        pygame.quit()
    assert not hasattr(adventure, "current_room")

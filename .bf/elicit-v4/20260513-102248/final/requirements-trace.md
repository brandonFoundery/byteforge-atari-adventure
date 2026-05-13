# Requirements Trace Registry

**Run ID:** 20260513-102248
**Total requirements:** 63
**Epics:** 3 | **Stories:** 12

| REQ-ID  | Epic     | Story         | Description                                                                                                          | Status |
|---------|----------|---------------|----------------------------------------------------------------------------------------------------------------------|--------|
| REQ-001 | EPIC-001 | STORY-001-1   | `adventure.py` exposes public `Room` class with `id`, `bg_color`, `neighbors` attributes, importable                  | open   |
| REQ-002 | EPIC-001 | STORY-001-1   | Module-level `ROOMS` mapping contains exactly 4 entries: `yellow`, `blue`, `green`, `purple`                          | open   |
| REQ-003 | EPIC-001 | STORY-001-1   | Each room's `bg_color` matches authored palette; all four `bg_color` values are pairwise distinct                     | open   |
| REQ-004 | EPIC-001 | STORY-001-1   | Each `Room.neighbors` dict has exactly keys N/S/E/W; values are existing room id or `None`                            | open   |
| REQ-005 | EPIC-001 | STORY-001-1   | Adjacency map matches the 2×2 layout (yellow–blue–green–purple grid)                                                  | open   |
| REQ-006 | EPIC-001 | STORY-001-1   | `START_ROOM = "yellow"` and `ROOMS[START_ROOM].bg_color == (240, 208, 64)`                                            | open   |
| REQ-007 | EPIC-001 | STORY-001-1   | Module-level constant `ROOM_COLOR` still exists with value `(240, 208, 64)` for legacy imports                        | open   |
| REQ-008 | EPIC-001 | STORY-001-1   | `tests/test_adventure.py` and `tests/test_movement.py` pass unmodified after this story                               | open   |
| REQ-009 | EPIC-001 | STORY-001-2   | `assert_symmetric(rooms)` returns `None` for registries with symmetric adjacency                                      | open   |
| REQ-010 | EPIC-001 | STORY-001-2   | `assert_symmetric` raises `ValueError` (naming offending room/direction) on asymmetric registries                     | open   |
| REQ-011 | EPIC-001 | STORY-001-2   | `assert_connected(rooms, start)` returns `None` when BFS from `start` reaches every key                               | open   |
| REQ-012 | EPIC-001 | STORY-001-2   | `assert_connected` raises `ValueError` (listing unreachable rooms) when registry is not connected                     | open   |
| REQ-013 | EPIC-001 | STORY-001-2   | Neither validator mutates `rooms` argument; neither reads/mutates module-level `ROOMS`                                | open   |
| REQ-014 | EPIC-001 | STORY-001-2   | `tests/test_adventure.py` and `tests/test_movement.py` pass unmodified after this story                               | open   |
| REQ-015 | EPIC-001 | STORY-001-3   | New file `tests/test_rooms.py` exists and is collected by `pytest`                                                    | open   |
| REQ-016 | EPIC-001 | STORY-001-3   | All 11 named test cases are implemented as separate `test_*` functions                                                | open   |
| REQ-017 | EPIC-001 | STORY-001-3   | All tests in `tests/test_rooms.py` pass under existing `tests/conftest.py` (headless SDL)                             | open   |
| REQ-018 | EPIC-001 | STORY-001-3   | `tests/test_adventure.py` and `tests/test_movement.py` pass unmodified after this story                               | open   |
| REQ-019 | EPIC-001 | STORY-001-3   | `tests/test_rooms.py` imports only from `adventure` and `pytest` (no new dependencies)                                | open   |
| REQ-020 | EPIC-001 | STORY-001-3   | Validator-failure tests construct synthetic registries inline; do NOT mutate `adventure.ROOMS`                        | open   |
| REQ-021 | EPIC-002 | STORY-002-1   | `draw_room` accepts a `room` argument and fills background with `room.bg_color`; `ROOM_COLOR` preserved as alias       | open   |
| REQ-022 | EPIC-002 | STORY-002-1   | `draw_room` draws walls only on sealed edges (`neighbors[dir] is None`); passage edges show no wall                   | open   |
| REQ-023 | EPIC-002 | STORY-002-1   | `test_draw_room_uses_active_room_color` samples interior pixel and asserts it equals `room.bg_color`                  | open   |
| REQ-024 | EPIC-002 | STORY-002-1   | `test_draw_room_omits_wall_on_passage_edge` verifies passage edges show `bg_color`, sealed edges show `WALL_COLOR`     | open   |
| REQ-025 | EPIC-002 | STORY-002-2   | `run_game_loop` declares function-local `current_room` from `START_ROOM`; passes it to `draw_room` each frame          | open   |
| REQ-026 | EPIC-002 | STORY-002-2   | `current_room` is function-local only; `hasattr(adventure, "current_room")` returns False; no cross-invocation leak    | open   |
| REQ-027 | EPIC-002 | STORY-002-2   | `test_run_game_loop_uses_start_room_for_initial_frame` asserts rendered color equals `START_ROOM.bg_color`            | open   |
| REQ-028 | EPIC-002 | STORY-002-3   | `test_rendered_frame_matches_start_room_bg_color` samples center pixel after one frame; documented fallback if needed | open   |
| REQ-029 | EPIC-002 | STORY-002-3   | `test_rendered_frame_shows_walls_only_on_sealed_edges_of_start_room` verifies wall vs. bg per direction                | open   |
| REQ-030 | EPIC-002 | STORY-002-3   | `test_no_module_global_current_room` asserts `not hasattr(adventure, "current_room")`; full pytest run stays green     | open   |
| REQ-031 | EPIC-003 | STORY-003-1   | `move_player` accepts `room` parameter and uses `room.neighbors` to decide clamp vs. exit per edge                    | open   |
| REQ-032 | EPIC-003 | STORY-003-1   | East passage exit: `x > _X_MAX` + passage neighbor → returns `exit_dir="E"` without clamping `x`                       | open   |
| REQ-033 | EPIC-003 | STORY-003-1   | East sealed clamp: `x > _X_MAX` + `neighbors["E"] is None` → clamps to `_X_MAX`, returns `exit_dir=None`               | open   |
| REQ-034 | EPIC-003 | STORY-003-1   | Symmetric clamp/exit behavior implemented for west, north, south edges                                                | open   |
| REQ-035 | EPIC-003 | STORY-003-1   | Diagonal cross resolves at most one transition per frame; horizontal axis wins ties (documented in docstring)         | open   |
| REQ-036 | EPIC-003 | STORY-003-1   | Existing `tests/test_movement.py` calls pass via `room=None` legacy mode or same-commit fixture update                 | open   |
| REQ-037 | EPIC-003 | STORY-003-2   | `_warp_position(room, "E", x, y)` returns east neighbor with `x = _X_MIN + INWARD_OFFSET`, clamped `y`                 | open   |
| REQ-038 | EPIC-003 | STORY-003-2   | Mirror behavior implemented and tested for `"W"`, `"N"`, `"S"` exit directions                                        | open   |
| REQ-039 | EPIC-003 | STORY-003-2   | Module constant `INWARD_OFFSET = PLAYER_SPEED + 1` used by `_warp_position` for the parallel axis                     | open   |
| REQ-040 | EPIC-003 | STORY-003-2   | `_warp_position` is deterministic: identical args → identical return tuple; no hidden state                            | open   |
| REQ-041 | EPIC-003 | STORY-003-2   | Perpendicular coordinate after warp is clamped into new room's interior (e.g. `y = _Y_MIN - 1` → `y = _Y_MIN`)         | open   |
| REQ-042 | EPIC-003 | STORY-003-2   | `_warp_position` has no `import pygame` and no module-global writes; callable without `SDL_VIDEODRIVER=dummy`          | open   |
| REQ-043 | EPIC-003 | STORY-003-3   | `run_game_loop` initializes `current_room` from registry's start room; uses it on first frame's `draw_room`/`move_player` | open |
| REQ-044 | EPIC-003 | STORY-003-3   | On `exit_dir` from `move_player`, loop calls `_warp_position` and reassigns `current_room`/`px`/`py` before `draw_room`| open   |
| REQ-045 | EPIC-003 | STORY-003-3   | Headless test verifies post-transition frame shows new room's `bg_color` and warped player position                    | open   |
| REQ-046 | EPIC-003 | STORY-003-3   | When `move_player` returns no `exit_dir`, `current_room` is unchanged that frame (verified holding sealed edge)        | open   |
| REQ-047 | EPIC-003 | STORY-003-3   | `current_room` is function-local; test asserts `not hasattr(adventure, "current_room")` after loop run                 | open   |
| REQ-048 | EPIC-003 | STORY-003-4   | Module-level fixture room with all four edges sealed exists in `tests/test_movement.py`; used by every clamp test     | open   |
| REQ-049 | EPIC-003 | STORY-003-4   | `test_wall_clamp_left` asserts pressing left at `x = _X_MIN` keeps `x == _X_MIN` (T2 invariant preserved)              | open   |
| REQ-050 | EPIC-003 | STORY-003-4   | `_right`, `_top`, `_bottom` clamp tests updated analogously; original T2 boundary values preserved                     | open   |
| REQ-051 | EPIC-003 | STORY-003-4   | No new test in `tests/test_movement.py` asserts a transition; transition tests live in `tests/test_rooms.py`           | open   |
| REQ-052 | EPIC-003 | STORY-003-4   | `pytest tests/test_movement.py` exits 0 with all four clamp tests passing under new `move_player` signature           | open   |
| REQ-053 | EPIC-003 | STORY-003-5   | East exit test: new `x == _X_MIN + INWARD_OFFSET`; `current_room` equals eastern neighbor                              | open   |
| REQ-054 | EPIC-003 | STORY-003-5   | Analogous transition tests for west, north, south: mirror math, inward offset, correct neighbor selection             | open   |
| REQ-055 | EPIC-003 | STORY-003-5   | `test_no_immediate_re_transition`: one additional `move_player` after warp east does NOT return `exit_dir`            | open   |
| REQ-056 | EPIC-003 | STORY-003-5   | `test_full_graph_walkable_from_start`: BFS via `_warp_position` reaches every room in registry                         | open   |
| REQ-057 | EPIC-003 | STORY-003-5   | `test_re_entry_is_deterministic`: `_warp_position` twice with same args returns equal tuples                           | open   |
| REQ-058 | EPIC-003 | STORY-003-5   | `test_sealed_edge_does_not_transition`: sealed edge → `exit_dir=None`, `current_room` unchanged                       | open   |
| REQ-059 | EPIC-003 | STORY-003-6   | Corner diagonal test: passage east + sealed south → transitions east, south clamps (per REQ-035)                     | open   |
| REQ-060 | EPIC-003 | STORY-003-6   | Alternating left/right across passage for 10+ frames toggles `current_room` between exactly two rooms, no thrash       | open   |
| REQ-061 | EPIC-003 | STORY-003-6   | Full-graph scripted traversal: final `current_room` matches expected; surface bg pixel equals that room's `bg_color`   | open   |
| REQ-062 | EPIC-003 | STORY-003-6   | Holding one direction toward passage edge for 60 frames triggers exactly one transition in window                     | open   |
| REQ-063 | EPIC-003 | STORY-003-6   | New adversarial file passes under `pytest` headlessly using existing `conftest.py`; no new dependencies                | open   |

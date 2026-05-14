# C06 — GameLoopIntegration

**Type:** integration
**Epic:** EPIC-003 (plus EPIC-001 STORY-001-3 test landing)
**Stories:** STORY-003-3, STORY-003-4, STORY-003-5, STORY-003-6 (also STORY-001-3)
**Dependencies:** C02, C03, C04, C05 (transitively C01)

## Traced requirements

STORY-001-3 (test landing): REQ-015, REQ-016, REQ-017, REQ-018, REQ-019, REQ-020
STORY-003-3: REQ-043, REQ-044, REQ-045, REQ-046, REQ-047
STORY-003-4: REQ-048, REQ-049, REQ-050, REQ-051, REQ-052
STORY-003-5: REQ-053, REQ-054, REQ-055, REQ-056, REQ-057, REQ-058
STORY-003-6: REQ-059, REQ-060, REQ-061, REQ-062, REQ-063

## Goal

Wire C03 rendering + C04 movement + C05 warp into `run_game_loop`. Land all new tests; reconcile existing `tests/test_movement.py` clamp tests; add adversarial e2e tests.

## Constraints

### Loop wiring (STORY-003-3)
- `run_game_loop` initializes `current_room` from `ROOMS[START_ROOM]`; uses on first frame's `draw_room`/`move_player` (REQ-043).
- On exit signal from `move_player`, loop calls `_warp_position`, reassigns `current_room/px/py` BEFORE `draw_room` (REQ-044).
- Headless test asserts post-transition frame shows new room's `bg_color` and warped player position (REQ-045).
- When `move_player` returns no exit, `current_room` unchanged that frame (REQ-046).
- `current_room` remains function-local: `not hasattr(adventure, "current_room")` after loop run (REQ-047).

### Movement test reconciliation (STORY-003-4)
- Module-level fixture room with all four edges sealed in `tests/test_movement.py`; used by every clamp test (REQ-048).
- `test_wall_clamp_left`, `_right`, `_top`, `_bottom` updated to use that fixture (REQ-049, REQ-050).
- Original T2 boundary values preserved (REQ-049, REQ-050).
- No transition assertions in `tests/test_movement.py` — those live in `tests/test_rooms.py` (REQ-051).
- `pytest tests/test_movement.py` exits 0 (REQ-052).

### Transition tests (STORY-003-5)
- East exit test: new `x == _X_MIN + INWARD_OFFSET`; `current_room` equals eastern neighbor (REQ-053).
- Analogous W/N/S transition tests (REQ-054).
- `test_no_immediate_re_transition`: one more `move_player` after warp east does NOT return an exit (REQ-055).
- `test_full_graph_walkable_from_start`: BFS via `_warp_position` reaches every room (REQ-056).
- `test_re_entry_is_deterministic` (REQ-057).
- `test_sealed_edge_does_not_transition` (REQ-058).

### Adversarial e2e (STORY-003-6)
- New `tests/e2e/adversarial/test_rooms_adversarial.py`.
- Corner diagonal: passage E + sealed S -> transitions east, south clamps (REQ-059).
- Alternating left/right across passage for 10+ frames toggles `current_room` between exactly two rooms (REQ-060).
- Full-graph scripted traversal: final `current_room` matches expected; surface bg pixel equals that room's `bg_color` (REQ-061).
- Holding one direction toward passage edge for 60 frames triggers exactly one transition in window (REQ-062).
- Adversarial file passes headlessly using existing `conftest.py`; no new dependencies (REQ-063).

### Test file (STORY-001-3 lands here)
- `tests/test_rooms.py` is created and collected by pytest (REQ-015).
- All 11 named test cases implemented as separate `test_*` functions (REQ-016).
- All tests pass under existing `tests/conftest.py` (REQ-017).
- `tests/test_adventure.py` and `tests/test_movement.py` pass unmodified (REQ-018, modulo the reconcile in STORY-003-4 which is itself the intended change).
- `tests/test_rooms.py` imports only `adventure` and `pytest` (REQ-019).
- Validator-failure tests construct synthetic registries inline (do NOT mutate `adventure.ROOMS`) (REQ-020).

## Out of scope

Anything not in the wired loop or its tests. Per-room interior wall layouts.

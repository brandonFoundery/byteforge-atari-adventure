# T3 — Multi-Room World + Screen Transitions — Assembled Specification

**Run ID:** 20260513-102248
**Mode:** understand-driven
**Source:** `.bf/understand-v4/20260513-102248/diamond`
**Epics:** 3 | **Stories:** 12 | **Requirements:** 63

## Source Summary

T3 expands the Atari Adventure homage from a single screen into a connected
world of 4–6 distinct rooms. Each room fills the entire screen with its own
distinct color/theme. Walking past a screen-edge that connects to a neighbor
instantly swaps the active room and warps the player to the opposite edge.
Sealed edges (no neighbor) continue to behave as walls. T1/T2 behavior must
not regress.

All production work is scoped to `adventure.py`; tests live under `tests/`.

## Resolved Cross-Cutting Decisions

- **Room count / topology:** 4 rooms in a 2×2 grid (`yellow`, `blue`, `green`, `purple`).
- **Starting room:** `"yellow"` (top-left); `bg_color = (240, 208, 64)` matches legacy `ROOM_COLOR`.
- **Color palette:**
  - `yellow` → `(240, 208, 64)`
  - `blue` → `(64, 96, 200)`
  - `green` → `(48, 160, 64)`
  - `purple` → `(144, 64, 176)`
- **Sealed-edge representation:** `neighbors[dir] is None` (not a separate `walls` set).
- **Adjacency:** symmetric, bidirectional; validated by `assert_symmetric`.
- **Connectivity:** BFS from `START_ROOM` reaches every room; validated by `assert_connected`.
- **Post-transition position:** mirror perpendicular coordinate + inward offset `PLAYER_SPEED + 1`.
- **`current_room` location:** function-local in `run_game_loop` (never module-global).
- **Diagonal exit priority:** horizontal axis wins ties (documented in `move_player` docstring).
- **Transition visuals:** silent / instantaneous (no flash, fade, or label).

## Boundaries (from `location.md`)

- **In scope:** `adventure.py`, `tests/test_rooms.py` (NEW),
  `tests/test_movement.py` (reconcile), `tests/e2e/adversarial/test_rooms_adversarial.py` (NEW).
- **Out of scope:** inventory, enemies, items, scrolling, audio, new
  dependencies, per-room interior wall layouts.

## Rollout Order

EPIC-001 → EPIC-002 → EPIC-003 — each epic lands on green tests.

---

# EPIC-001 — Room model + registry (foundation, no behavior change)

## Goal

Introduce the core data foundation for the multi-room world: a `Room` data
structure carrying a per-room background color and a 4-direction adjacency
map, plus a hand-authored registry of 4 rooms wired into a connected graph.
This epic is pure data + validation — no rendering, no movement change, no
transitions. T1/T2 behavior must remain bit-for-bit identical at the end of
this epic.

## Success Criterion

Game contains 4 distinct rooms with per-room `bg_color` and a connected
adjacency graph; registry validates symmetry and connectivity; T1/T2 tests
still pass.

## Scope

**In scope** (`location.md`):
- `adventure.py` — add `Room` data class (`id`, `bg_color`, `neighbors`).
- `adventure.py` — add module-level `ROOMS` registry (4 rooms).
- `adventure.py` — add `START_ROOM = "yellow"` constant.
- `adventure.py` — preserve `ROOM_COLOR = (240, 208, 64)` as back-compat alias.
- `tests/test_rooms.py` (NEW) — registry shape, count, symmetry, connectivity, distinct colors.

**Out of scope:** rendering changes (EPIC-002), transitions / movement
signature changes (EPIC-003), interior wall layouts, enemies, items, audio.

## Authored 2×2 Map

```
+--------+--------+
| yellow | blue   |
+--------+--------+
| green  | purple |
+--------+--------+
```

Adjacency (all symmetric):
- `yellow.E = "blue"`, `yellow.S = "green"`, `yellow.N = None`, `yellow.W = None`
- `blue.W = "yellow"`, `blue.S = "purple"`, `blue.N = None`, `blue.E = None`
- `green.E = "purple"`, `green.N = "yellow"`, `green.S = None`, `green.W = None`
- `purple.W = "green"`, `purple.N = "blue"`, `purple.S = None`, `purple.E = None`

## Epic-Level Acceptance Criteria

- Importing `adventure` exposes a `ROOMS` mapping with ≥4 and ≤6 entries.
- Every room exposes `bg_color: tuple[int, int, int]` and a `neighbors` dict
  with all four cardinal keys present.
- The graph is connected (BFS from `START_ROOM` reaches every room id).
- Adjacency is symmetric for every authored edge.
- All `bg_color` values are pairwise distinct.
- `tests/test_adventure.py` and `tests/test_movement.py` continue to pass
  unmodified (regression gate for "no behavior change").

## Stories

### STORY-001-1 — Add `Room` data structure, `ROOMS` registry, and `START_ROOM`

**Touch:** `adventure.py` (additive — NEW symbols only).

**Design:**
- `dataclass(frozen=True)` named `Room` with fields `id: str`,
  `bg_color: tuple[int, int, int]`, `neighbors: dict[str, str | None]`.
- `ROOMS: dict[str, Room]` — module-level registry.
- `START_ROOM: str = "yellow"`.
- Retain `ROOM_COLOR = (240, 208, 64)` as alias.

**Requirements:**
- **REQ-001**: `adventure.py` exposes a public `Room` class (or dataclass)
  with attributes `id`, `bg_color`, and `neighbors`, importable as
  `from adventure import Room`.
- **REQ-002**: `adventure.py` exposes a module-level `ROOMS` mapping of
  `room_id -> Room` containing exactly 4 entries with ids `"yellow"`,
  `"blue"`, `"green"`, `"purple"`.
- **REQ-003**: Each entry in `ROOMS` has `bg_color` equal to the palette
  specified above, and all four `bg_color` values are pairwise distinct.
- **REQ-004**: Each `Room.neighbors` dict has exactly the four keys
  `"N"`, `"S"`, `"E"`, `"W"` present; values are either another existing
  room id (string) or `None`.
- **REQ-005**: The adjacency map matches the 2×2 layout documented above.
- **REQ-006**: `adventure.py` exposes `START_ROOM = "yellow"` and
  `ROOMS[START_ROOM].bg_color == (240, 208, 64)`.
- **REQ-007**: The module-level constant `ROOM_COLOR` still exists with
  value `(240, 208, 64)` so legacy imports continue to resolve.
- **REQ-008**: `tests/test_adventure.py` and `tests/test_movement.py` pass
  unmodified after this story's changes.

### STORY-001-2 — Registry validation helpers (symmetry & connectivity)

**Touch:** `adventure.py` (additive — two new functions).

**Design:**
```python
_OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}

def assert_symmetric(rooms: dict[str, Room]) -> None: ...
def assert_connected(rooms: dict[str, Room], start: str) -> None: ...
```

Both functions are pure (no module-global reads), take explicit `rooms`
argument, raise `ValueError` with descriptive message on failure, return
`None` on success. NOT invoked at module import time.

**Requirements:**
- **REQ-009**: `adventure.py` exports a callable `assert_symmetric(rooms)`
  that returns `None` for any registry where every authored edge
  `A.neighbors[d] == B_id` has the matching reverse edge
  `rooms[B_id].neighbors[opposite(d)] == A.id`.
- **REQ-010**: `assert_symmetric` raises `ValueError` (with a message
  naming the offending room id and direction) when given a registry whose
  adjacency is asymmetric.
- **REQ-011**: `adventure.py` exports a callable `assert_connected(rooms, start)`
  that returns `None` when a breadth-first search starting at `start`
  reaches every key in `rooms`.
- **REQ-012**: `assert_connected` raises `ValueError` (with a message
  listing the unreachable room ids) when given a registry that is not
  fully connected from `start`.
- **REQ-013**: Neither validator mutates its `rooms` argument and neither
  reads or mutates the module-level `ROOMS`.
- **REQ-014**: `tests/test_adventure.py` and `tests/test_movement.py` pass
  unmodified after this story.

### STORY-001-3 — `tests/test_rooms.py` — registry coverage

**Create:** `tests/test_rooms.py` (NEW). Pytest style, plain functions.

**Test cases:**
1. `test_room_registry_has_4_to_6_rooms`
2. `test_room_ids_are_unique`
3. `test_room_has_bg_color_and_neighbors`
4. `test_all_bg_colors_pairwise_distinct`
5. `test_neighbor_values_reference_existing_rooms_or_none`
6. `test_adjacency_is_symmetric`
7. `test_adjacency_graph_is_connected`
8. `test_start_room_constant_is_valid`
9. `test_room_color_legacy_constant_preserved`
10. `test_assert_symmetric_rejects_asymmetric_registry`
11. `test_assert_connected_rejects_orphan_room`

**Requirements:**
- **REQ-015**: New file `tests/test_rooms.py` exists and is collected by `pytest`.
- **REQ-016**: All 11 test cases listed above are implemented as separate
  `test_*` functions with descriptive names matching the list.
- **REQ-017**: All tests in `tests/test_rooms.py` pass under the existing
  `tests/conftest.py` fixture (headless SDL).
- **REQ-018**: `tests/test_adventure.py` and `tests/test_movement.py` pass
  unmodified after this story (no edits to either file).
- **REQ-019**: `tests/test_rooms.py` imports only from `adventure` and
  `pytest` (no new dependencies introduced).
- **REQ-020**: Validator-failure tests construct synthetic registries
  inline and DO NOT mutate `adventure.ROOMS`.

---

# EPIC-002 — Room-aware rendering + active room state

## Summary

Generalize the render and frame-loop layer so the game draws a specific Room
(the active room) each frame instead of the hard-coded single screen. After
this epic, `draw_room` accepts a Room and renders that room's `bg_color`,
drawing wall rectangles only on the room's sealed edges; `run_game_loop`
carries `current_room` as a function-local (no module global); the rendered
frame always reflects whichever Room is active.

This epic *consumes* EPIC-001's registry — no edge-crossing or transition
logic is introduced yet. The output is a game that visibly renders the
registry's starting room (its color, its sealed walls) but still clamps at
every edge exactly like T2 did.

## Success Criterion

`draw_room` renders the active room's `bg_color` and renders walls only on
sealed edges; `run_game_loop` threads `current_room` as a local (no module
global); rendered frame reflects the active room.

## Scope

**In scope:**
- `adventure.py::draw_room` (lines 77–92) — generalize signature, render `room.bg_color`, render walls only on sealed edges.
- `adventure.py::run_game_loop` (lines 100–129) — function-local `current_room` initialized from `START_ROOM`.
- `adventure.py` module constants — `ROOM_COLOR` preserved as back-compat alias.
- `tests/test_rooms.py` — extend with rendering tests using `pygame.Surface.get_at()`.

**Out of scope (EPIC-003):** edge-crossing in `move_player`, room mutation in loop, warp logic, `tests/test_movement.py` reconciliation.

## Epic-Level Acceptance Criteria

1. `python adventure.py` launches and renders the starting room's `bg_color` as the background.
2. Walls are drawn only on edges where the starting room has no neighbor.
3. The game continues to run at 60 FPS with no console errors.
4. All existing T1 / T2 tests pass without modification.
5. `grep` for `current_room` in `adventure.py` shows zero occurrences at module scope.

## Stories

### STORY-002-1 — Generalize `draw_room` to render active room's color and sealed-edge walls

**Touch:** `adventure.py::draw_room` (lines 77–92).

**Requirements:**
- **REQ-021**: `draw_room` accepts a `room` argument (a Room object from
  EPIC-001's registry) in addition to its existing `surface` argument, and
  fills the play area background with the color exposed by `room.bg_color`
  (replacing the hard-coded `ROOM_COLOR` fill). The module-level `ROOM_COLOR`
  constant is preserved as a back-compat alias so external imports do not
  break.
- **REQ-022**: For each cardinal direction in {N, S, E, W}, `draw_room`
  renders a wall rectangle using the existing `WALL_COLOR` and
  `WALL_THICKNESS` constants if and only if `room.neighbors[direction] is None`
  (sealed edge). When the neighbor is a Room reference (passage edge),
  no wall is drawn on that edge and the `bg_color` fill reaches the screen
  border. N/S walls span the full `LOGICAL_WIDTH`; E/W walls span the full
  `LOGICAL_HEIGHT`. This story does NOT introduce per-room wall colors.
- **REQ-023**: A new unit test in `tests/test_rooms.py`
  (`test_draw_room_uses_active_room_color`) constructs a Room with a known
  `bg_color`, calls `draw_room(surface, room)`, and asserts via
  `surface.get_at((x, y))` at an interior pixel that the rendered color
  matches `room.bg_color` exactly (RGB).
- **REQ-024**: A new unit test
  (`test_draw_room_omits_wall_on_passage_edge`) constructs a Room whose
  `neighbors["E"]` points to another Room (passage) and whose other three
  edges are sealed; calls `draw_room`; asserts via `surface.get_at()` that a
  pixel one pixel inside the right edge has the room's `bg_color` (NOT
  `WALL_COLOR`), while a pixel one pixel inside the top edge has
  `WALL_COLOR`.

### STORY-002-2 — Thread `current_room` as a function-local through `run_game_loop`

**Touch:** `adventure.py::run_game_loop` (lines 100–129).

**Requirements:**
- **REQ-025**: `run_game_loop` declares a function-local `current_room`
  initialized from the registry's designated starting room exposed by EPIC-001
  before the `while running:` loop body, and passes it to `draw_room` each
  frame (updating the existing call site at adventure.py line 121).
  `run_game_loop`'s public signature is unchanged.
- **REQ-026**: `current_room` exists only as a function-local inside
  `run_game_loop` — there is no module-scope `current_room` binding, no
  `global current_room` statement anywhere in `adventure.py`, and
  `hasattr(adventure, "current_room")` returns False after import. Running
  the loop twice in the same Python process re-initializes `current_room` to
  `START_ROOM` on each invocation.
- **REQ-027**: A new unit test
  (`test_run_game_loop_uses_start_room_for_initial_frame`) drives one frame
  of `run_game_loop` (via the existing `max_frames=1` style fixture from
  `tests/test_adventure.py`) and asserts via `surface.get_at()` at an
  interior pixel that the rendered color equals `START_ROOM.bg_color`.
  Existing `tests/test_adventure.py` tests continue to pass without
  modification.

### STORY-002-3 — Verify rendered frame reflects the active room (pixel-level integration test)

**Touch:** `tests/test_rooms.py` (verification-only).

**Requirements:**
- **REQ-028**: A new integration test in `tests/test_rooms.py`
  (`test_rendered_frame_matches_start_room_bg_color`) initializes pygame
  headlessly, runs `run_game_loop` for exactly one frame, then asserts that
  `surface.get_at((LOGICAL_WIDTH // 2, LOGICAL_HEIGHT // 2))` returns an RGB
  triple equal to `START_ROOM.bg_color` (alpha channel ignored). Must pass
  under the existing `SDL_VIDEODRIVER=dummy` fixture; if `surface.get_at()`
  proves unreliable under the dummy driver, the test uses a documented
  `screen.blit`-target-surface workaround (NOT removed).
- **REQ-029**: A new integration test
  (`test_rendered_frame_shows_walls_only_on_sealed_edges_of_start_room`)
  runs one frame of `run_game_loop` and, for each of the four cardinal
  edges, samples a pixel one pixel inside `WALL_THICKNESS` from the
  edge. The pixel must equal `WALL_COLOR` when `START_ROOM.neighbors[dir]`
  is `None`, and must equal `START_ROOM.bg_color` when
  `START_ROOM.neighbors[dir]` is a Room reference.
- **REQ-030**: A regression check (`test_no_module_global_current_room`)
  asserts `not hasattr(adventure, "current_room")` to enforce REQ-026
  from STORY-002-2 over time. The full `pytest` run remains green after
  this story.

---

# EPIC-003 — Edge transitions + room-aware movement

## Summary

Convert the room-edge clamping behavior into edge-aware transitions. When the
player crosses a passage edge, the active room swaps to that neighbor and
the player is warped to the mirrored coordinate on the opposite edge of the
new room, with an inward offset that prevents an immediate re-trigger.
Sealed edges continue to clamp the player exactly as in T2. The full graph
must be walkable in both directions, re-entry must be deterministic, and the
existing `tests/test_movement.py` wall-clamp tests must be reconciled.

## Success Criterion

Crossing a passage edge swaps `current_room` and warps the player to the
opposite edge (mirrored coordinate, inward offset to prevent re-trigger);
sealed edges still clamp; full graph is walkable; re-entry is deterministic;
`tests/test_movement.py` wall-clamp tests reconciled.

## Scope

**In scope:**
- `adventure.py::move_player` — room-aware clamp/exit signaling.
- `adventure.py::run_game_loop` — invoke `_warp_position`, swap `current_room`, rebind `(px, py)`.
- `adventure.py::_warp_position` (NEW pure helper) — mirror perpendicular axis, apply inward offset.
- `tests/test_rooms.py` — extend with transition warp tests.
- `tests/test_movement.py` — reconcile wall-clamp tests with a sealed fixture room.
- `tests/e2e/adversarial/test_rooms_adversarial.py` (NEW) — adversarial scenarios.

**Out of scope:** visual transition effects, persistence of visited rooms, new gameplay objects, changes to `PLAYER_SPEED` / `TARGET_FPS` / window dimensions.

## Epic-Level Acceptance Criteria

- AC-E3-1: Walking past a passage edge replaces the active room on the same frame, no scroll/pan.
- AC-E3-2: After a transition, perpendicular coordinate preserved (clamped to interior).
- AC-E3-3: After a transition, parallel coordinate set inward by `PLAYER_SPEED + 1`.
- AC-E3-4: Pressing into a sealed edge produces T2 clamp behavior; `current_room` unchanged.
- AC-E3-5: Every room reachable from `START_ROOM` via legal arrow-key transitions.
- AC-E3-6: Re-entering a room via the same edge places player at the same warp position.
- AC-E3-7: All pre-existing T1 tests and the reconciled T2 tests pass.
- AC-E3-8: `python adventure.py` launches a playable game traversing the full graph.

## Stories

### STORY-003-1 — Detect edge exit in `move_player` and return a crossing signal

**Touch:** `adventure.py::move_player` (lines 54–64).

**Requirements:**
- **REQ-031**: `move_player` accepts a `room` parameter referencing the
  active `Room` and uses `room.neighbors` to decide clamp vs. exit per edge.
- **REQ-032**: When the player's post-speed `x` exceeds `_X_MAX` and
  `room.neighbors["E"]` is a `Room`, `move_player` returns `exit_dir="E"`
  and does NOT clamp `x`.
- **REQ-033**: When the player's post-speed `x` exceeds `_X_MAX` and
  `room.neighbors["E"] is None`, `move_player` clamps `x` to `_X_MAX` and
  returns `exit_dir=None` (T2 behavior).
- **REQ-034**: Symmetric clamp/exit behavior is implemented for the three
  remaining edges: west (`x < _X_MIN`), north (`y < _Y_MIN`), south
  (`y > _Y_MAX`).
- **REQ-035**: When the player moves diagonally and crosses two edges in
  the same frame, `move_player` resolves at most one transition per frame
  using a deterministic priority order documented in the docstring
  (horizontal axis wins ties; flag the other axis as clamped in that frame).
- **REQ-036**: Existing `tests/test_movement.py` calls pass either via a
  default `room=None` legacy mode that preserves T2 clamp behavior, or via
  a same-commit test update that threads a fixture room with all four edges
  sealed — the choice is recorded in the docstring and reflected in the
  test fixture.

### STORY-003-2 — Pure transition helper `_warp_position`

**Touch:** `adventure.py` (NEW pure function).

**Mirror rules:**
- exit `"E"` → new `x = _X_MIN + INWARD_OFFSET`, new `y = clamp(y)`.
- exit `"W"` → new `x = _X_MAX - INWARD_OFFSET`, new `y = clamp(y)`.
- exit `"N"` → new `y = _Y_MAX - INWARD_OFFSET`, new `x = clamp(x)`.
- exit `"S"` → new `y = _Y_MIN + INWARD_OFFSET`, new `x = clamp(x)`.

`INWARD_OFFSET = PLAYER_SPEED + 1`.

**Requirements:**
- **REQ-037**: `_warp_position(room, "E", x, y)` returns the room stored at
  `room.neighbors["E"]`, with new-`x = _X_MIN + INWARD_OFFSET` and
  new-`y = clamp(y, _Y_MIN, _Y_MAX)`.
- **REQ-038**: Mirror behavior is implemented and tested for all four exit
  directions (`"W"`, `"N"`, `"S"` analogous to REQ-037).
- **REQ-039**: A new module constant `INWARD_OFFSET` exists, equals
  `PLAYER_SPEED + 1`, and is used by `_warp_position` for the parallel axis
  on every transition.
- **REQ-040**: Calling `_warp_position` twice with identical arguments
  returns identical `(room, x, y)` tuples — the helper is deterministic
  and has no hidden state.
- **REQ-041**: The perpendicular coordinate after a warp is clamped into
  the new room's interior; the unit test asserts that warping at
  `y = _Y_MIN - 1` returns `y = _Y_MIN` in the new room.
- **REQ-042**: The helper has no `import pygame` and no module-global
  writes; it is callable from a unit test without `SDL_VIDEODRIVER=dummy`.

### STORY-003-3 — Wire transitions into the game loop

**Touch:** `adventure.py::run_game_loop`.

**Order of operations per frame:**
1. Drain events.
2. `result = move_player(px, py, keys, current_room)`.
3. If `result.exit_dir is None`: `px, py = result.x, result.y`.
4. Else: `current_room, px, py = _warp_position(current_room, result.exit_dir, result.x, result.y)`.
5. `draw_room(logical_surface, current_room)`.
6. `draw_player(logical_surface, px, py)`.
7. Blit / flip / tick.

**Requirements:**
- **REQ-043**: `run_game_loop` initializes `current_room` to the registry's
  designated start room and uses that room on the first frame's `draw_room`
  and `move_player` calls.
- **REQ-044**: When `move_player` returns an `exit_dir`, the loop calls
  `_warp_position` and reassigns `current_room`, `px`, `py` before
  `draw_room` is invoked on that frame.
- **REQ-045**: The rendered frame after a transition shows the new room's
  `bg_color` and the player at the warped position — verified by a headless
  test that drives `run_game_loop` for a fixed frame count with a stub
  `event_getter` and a key-state stub holding "right", then samples the
  framebuffer via `pygame.Surface.get_at()`.
- **REQ-046**: When `move_player` returns no `exit_dir`, `current_room` is
  unchanged for that frame — verified by a headless test holding a direction
  toward a sealed edge.
- **REQ-047**: `current_room` is a function-local variable inside
  `run_game_loop`, not a module attribute — verified by a test that imports
  `adventure` and asserts `not hasattr(adventure, "current_room")` after a
  loop run.

### STORY-003-4 — Reconcile `tests/test_movement.py` wall-clamp tests

**Touch:** `tests/test_movement.py` (lines 63–80).

**Approach:** Introduce a module-level `_SEALED_ROOM` fixture with all four
neighbors set to `None`; all four clamp tests pass this fixture into the new
`move_player`.

**Requirements:**
- **REQ-048**: A module-level fixture room with all four edges sealed
  exists in `tests/test_movement.py` and is used by every wall-clamp test.
- **REQ-049**: `test_wall_clamp_left` asserts that pressing left at
  `x = _X_MIN` results in `x == _X_MIN` after `move_player` (T2 invariant
  preserved).
- **REQ-050**: The remaining three wall-clamp tests (`_right`, `_top`,
  `_bottom`) are updated analogously and continue to assert the original
  T2 boundary values.
- **REQ-051**: No new test in `tests/test_movement.py` asserts a
  transition — transition behavior lives in `tests/test_rooms.py`
  (STORY-003-5).
- **REQ-052**: Running `pytest tests/test_movement.py` exits 0 with all
  four clamp tests passing under the new `move_player` signature.

### STORY-003-5 — Add `tests/test_rooms.py` transition coverage

**Touch:** `tests/test_rooms.py` (extend).

**Requirements:**
- **REQ-053**: A test verifies that exiting east from a sample passage
  edge results in the player's new `x == _X_MIN + INWARD_OFFSET` and
  `current_room` equals the eastern neighbor.
- **REQ-054**: Analogous tests exist for the three remaining directions
  (west, north, south) — each asserts mirror math, inward offset, and
  correct neighbor selection.
- **REQ-055**: A `test_no_immediate_re_transition` confirms that after a
  warp east, one additional `move_player` call with the east key held does
  NOT return an `exit_dir`, because `INWARD_OFFSET` placed the player
  inside the new room beyond the speed reach of the entry edge.
- **REQ-056**: A `test_full_graph_walkable_from_start` performs a BFS
  starting at the start room and confirms every room in the registry is
  reachable via `_warp_position` traversal alone.
- **REQ-057**: A `test_re_entry_is_deterministic` calls `_warp_position`
  twice with identical inputs (exit room, direction, x, y) and asserts
  the returned tuple is equal on both calls.
- **REQ-058**: A `test_sealed_edge_does_not_transition` confirms that on
  a sealed edge, `move_player` returns `exit_dir=None` and `current_room`
  is unchanged for any input held against that edge.

### STORY-003-6 — Add `tests/e2e/adversarial/test_rooms_adversarial.py`

**Touch:** `tests/e2e/adversarial/test_rooms_adversarial.py` (NEW).

**Requirements:**
- **REQ-059**: A test holds both right and down arrows for one frame at a
  corner where the east edge is a passage and the south edge is sealed,
  and asserts the player transitions east (per REQ-035) while the south
  coordinate clamps.
- **REQ-060**: A test scripts alternating left/right inputs across an
  east-passage edge for at least 10 frames and asserts that `current_room`
  toggles between exactly two rooms without skipping a third room or freezing.
- **REQ-061**: A test traverses every room in the registry via scripted
  input, asserting that after the scripted route `current_room` equals
  the expected terminal room and that the logical surface's background
  pixel equals that room's `bg_color`.
- **REQ-062**: A test asserts that holding a single direction toward a
  passage edge for 60 frames results in exactly one transition during
  that window (the inward offset prevents accidental multi-room skipping
  on a single hold).
- **REQ-063**: The new adversarial file passes under `pytest` headlessly
  using the existing `conftest.py` fixtures, with no new dependencies.

---

## Risk Register (consolidated)

| Risk | Mitigation | Owner |
|---|---|---|
| Disconnected / asymmetric room graph | `assert_symmetric` + `assert_connected` + tests | EPIC-001 |
| `ROOM_COLOR` constant removed/renamed breaks imports | Preserved as alias to yellow's `bg_color` | EPIC-001/002 |
| `draw_room` signature change cascades | Only one caller (`run_game_loop`); update atomically | EPIC-002 |
| Module-global `current_room` causes test flake | Function-local + `test_no_module_global_current_room` | EPIC-002 |
| Headless `get_at()` can't read pixel color | Verified under dummy driver; documented blit fallback | EPIC-002 |
| `move_player` signature change breaks T2 tests | Default `room=None` legacy + `_SEALED_ROOM` fixture | EPIC-003 |
| Off-by-one jitter causes immediate re-transition | `INWARD_OFFSET = PLAYER_SPEED + 1` | EPIC-003 |
| Diagonal exit at corner with mixed edge types | Documented priority (horizontal wins ties), REQ-059 | EPIC-003 |
| Adversarial suite silently green on bad transitions | `tests/e2e/adversarial/test_rooms_adversarial.py` | EPIC-003 |

# Elicit-v4 Plan — T3 Multi-Room World + Screen Transitions

**Run ID:** 20260513-102248
**Mode:** understand-driven
**Source:** `.bf/understand-v4/20260513-102248/diamond`

## Source Summary

T3 expands the Atari Adventure homage from a single screen into a connected
world of 4-6 distinct rooms. Each room fills the entire screen with its own
distinct color/theme. Walking past a screen-edge that connects to a neighbor
instantly swaps the active room and warps the player to the opposite edge.
Sealed edges (no neighbor) continue to behave as walls. T1/T2 behavior must
not regress.

All production work is scoped to `adventure.py`; tests live under `tests/`.

## Epic Breakdown

The work decomposes into three epics. Order matches the rollout sequence in
`impact.md` so each epic lands on green tests.

### EPIC-001 — Room model + registry (foundation, no behavior change)

**Success criteria covered:**
- Game contains between 4 and 6 distinct rooms (count assertion).
- Each room is visually distinguishable (per-room `bg_color`).
- Room graph is connected (BFS validator).

**Scope (in `adventure.py`):**
- Add a `Room` data structure (`bg_color`, `neighbors: {N,S,E,W -> Room|None}`).
- Build a static registry of 4-6 hand-authored rooms with a designated
  `START_ROOM`.
- Validate adjacency symmetry and graph connectivity at registry construction.
- Keep `ROOM_COLOR` constant as a back-compat alias (default = start room's
  color) so existing imports continue to resolve.

**Stories:**
- STORY-001-1: Define `Room` data class and module-level registry of 4-6
  rooms with per-room `bg_color` and N/S/E/W neighbors.
- STORY-001-2: Designate `START_ROOM`; preserve `ROOM_COLOR` as a back-compat
  alias.
- STORY-001-3: Add `tests/test_rooms.py` with: count (4 ≤ N ≤ 6), schema
  (each room exposes `bg_color` + `neighbors` dict), adjacency symmetry, and
  graph-connectivity (BFS reaches every room from `START_ROOM`).

**Acceptance criteria (risks → ACs):**
- Asymmetric adjacency (`A.east = B` but `B.west != A`) fails a test.
- Orphan room (unreachable from start) fails a test.
- `import adventure; adventure.ROOM_COLOR` still resolves (back-compat).
- `tests/test_adventure.py` and `tests/test_movement.py` continue to pass
  unchanged (no behavior wired into the loop yet).

---

### EPIC-002 — Room-aware rendering + active room state

**Success criteria covered:**
- Each room is visually distinguishable in a rendered frame.
- Game tracks a current/active room and renders it each frame.
- All existing T1/T2 behavior continues (no regression).

**Scope (in `adventure.py`):**
- Generalize `draw_room` to accept the active `Room` and render its
  `bg_color`; render walls only on sealed edges (`neighbors[dir] is None`),
  not on passage edges.
- Thread `current_room` state through `run_game_loop` (parameter / local
  variable, NOT module global — avoids cross-test state leak per risk
  register).
- Initialize `current_room = START_ROOM`; pass it to `draw_room` each frame.
- No transition logic yet — passage edges still clamp via existing
  `move_player` (effectively still single-room behavior visually, but
  rendering pipeline is now room-aware).

**Stories:**
- STORY-002-1: Change `draw_room(surface)` to `draw_room(surface, room)`;
  render `room.bg_color` background and render walls only on sealed edges.
  Update the single call site in `run_game_loop`.
- STORY-002-2: Introduce `current_room` as a local variable in
  `run_game_loop` (default `START_ROOM`); pass to `draw_room`.
- STORY-002-3: Add `tests/test_rooms.py::test_draw_room_uses_active_room_color`
  — render one frame under `SDL_VIDEODRIVER=dummy`, sample a center pixel
  via `pygame.Surface.get_at()`, assert it equals the active room's
  `bg_color`. If `get_at` is unusable headless, fall back to asserting the
  color is read from `room.bg_color` (mock-based).

**Acceptance criteria (risks → ACs):**
- No new module-level state introduced for `current_room` (verified by
  inspection / test that running the loop twice in one interpreter does not
  leak state).
- `tests/test_adventure.py` still passes (`run_game_loop` public surface
  unchanged from caller perspective).
- Headless pixel sampling works under `SDL_VIDEODRIVER=dummy` (risk
  mitigation). If it does not, the color assertion uses `room.bg_color`
  directly and the rendered-pixel check is documented as a manual step.

---

### EPIC-003 — Edge transitions + room-aware movement

**Success criteria covered:**
- Crossing a passage edge swaps the display to the adjacent room as a whole-
  screen replacement (no scroll/pan).
- After a transition, the player appears on the opposite edge of the new
  room.
- Player remains controllable in the new room (T2 controls).
- Wall collision continues inside every room.
- Edges with no adjacent room behave as solid walls.
- Re-entering a previously-visited room via the same edge returns the player
  to a deterministic position.

**Scope (in `adventure.py`):**
- Convert `move_player` to room-aware: accept an optional `room` parameter
  (`room=None` keeps legacy clamp behavior for back-compat); when a `room`
  is supplied, clamp on sealed edges and return an "exited via <direction>"
  signal on passage edges.
- Add a transition handler invoked in `run_game_loop` after `move_player`:
  swaps `current_room` to the neighbor and warps the player to the opposite
  edge at the mirrored perpendicular coordinate, offset inward by
  `PLAYER_SIZE` to prevent immediate re-transition.
- Update `tests/test_movement.py` wall-clamp tests so they target a sealed
  edge of the starting room (or pass a fully-sealed room fixture) so the
  clamp assertions remain meaningful.

**Stories:**
- STORY-003-1: Add `room` parameter to `move_player` (default `None` =
  legacy clamp). When `room` is given, return either the new `(x, y)` or a
  `("exit", direction)` signal on a passage edge. Document the contract.
- STORY-003-2: Add `transition(room, direction, x, y) -> (new_room, new_x,
  new_y)` helper that warps the player to the opposite edge with inward
  offset (`PLAYER_SIZE`) and mirrors the perpendicular coordinate.
- STORY-003-3: Wire transition + room-aware `move_player` into
  `run_game_loop`, updating `current_room` and `(px, py)` each frame.
- STORY-003-4: Reconcile `tests/test_movement.py::test_wall_clamp_*` — point
  them at an edge of the starting room that is sealed in the authored
  registry, OR pass a sealed-on-all-sides fixture room into `move_player`.
- STORY-003-5: Extend `tests/test_rooms.py` with:
  - `test_transition_east_warps_player_to_west_edge_of_neighbor` (and
    N/S/W variants).
  - `test_no_immediate_re_transition` — one more `move_player` step after a
    warp does not re-transition.
  - `test_sealed_edge_still_clamps` — pressing into a `neighbors[dir] is
    None` edge keeps the player at the boundary.
  - `test_re_entry_is_deterministic` — exit → re-enter via the same edge
    returns to a deterministic position.
- STORY-003-6: Add `tests/e2e/adversarial/test_rooms_adversarial.py`:
  diagonal exit at corner where one edge is sealed and the other is a
  passage; rapid alternating direction at an edge (no thrash); full graph
  traversal visits every room.

**Acceptance criteria (risks → ACs):**
- `move_player` signature change does not break existing `tests/test_movement.py`
  callers (default `room=None` preserves legacy clamping).
- Holding a direction across a transition does not chain multiple
  transitions in one frame (debounce via inward `PLAYER_SIZE` offset).
- Pressing into a sealed edge still clamps (T2 behavior preserved).
- Full BFS traversal from `START_ROOM` reaches every room via walking only.
- `python adventure.py` launches without console errors and supports manual
  traversal of all rooms; closing the window shuts down cleanly.

---

## Cross-Cutting Notes

**Decisions deferred to spec stage** (from `teachback.md` Requirement
Decisions and `impact.md` Unknowns):
- Exact room count (4 / 5 / 6) and topology (e.g., 2x2, 2x3, linear, ring).
- Per-room color palette (arbitrary vs. Atari Adventure kingdom colors).
- Sealed-edge representation: `neighbors[dir] = None` (planner's preferred
  default) vs. explicit `walls` set.
- Post-transition position rule: mirror perpendicular coordinate (planner's
  preferred default) vs. snap-to-center vs. per-edge spawn points.
- Visual theming scope: background color only (T3 minimum) vs. wall color /
  interior layout (deferred).
- Whether each room has its own interior wall layout (planner default: empty
  interior in T3; varied interior is T4+).
- Transition indicator (flash, room name): default OFF (silent swap) in T3.
- `current_room` state location: planner's preferred default is a local in
  `run_game_loop` (avoids module-global flakiness risk).

**Boundaries (from `location.md`):**
- In scope: `adventure.py`, `tests/test_rooms.py` (new),
  `tests/test_movement.py` (reconcile), `tests/e2e/adversarial/test_rooms_adversarial.py` (new).
- Out of scope: inventory, enemies, items, scrolling, audio, new
  dependencies.

**Order of execution:** EPIC-001 → EPIC-002 → EPIC-003 (each epic lands on
green tests; matches `impact.md` rollout order).

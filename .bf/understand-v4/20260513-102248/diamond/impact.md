# Impact Assessment

## Blast Radius Summary

- **Direct changes (production code, one file):**
  - `adventure.py` — add a Room data model and registry (4-6 rooms) with per-room `bg_color` and a 4-direction adjacency map (N/S/E/W neighbors, or `None` for sealed wall).
  - `adventure.py::run_game_loop` (lines 100-129) — introduce `current_room` state, invoke transition handler after `move_player`, pass active room to `draw_room`.
  - `adventure.py::move_player` (lines 54-64) — change from unconditional clamping to room-aware behavior: clamp on sealed edges, return an "exited via <direction>" signal on passage edges so the loop can swap rooms.
  - `adventure.py::draw_room` (lines 77-92) — generalize to accept the active room (color + which edges are walls vs. passages); currently hardcodes `ROOM_COLOR` and draws all four walls.
  - `adventure.py` module constants (lines 7-26) — `ROOM_COLOR` may be retained as a default/alias to preserve import compatibility; new per-room colors live on Room objects. `_X_MIN/_X_MAX/_Y_MIN/_Y_MAX` semantics shift from "world boundary" to "current-room boundary" — names should stay so test imports do not break.

- **Direct changes (test code):**
  - `tests/test_rooms.py` (NEW) — unit coverage for room registry, adjacency, transition warp-to-opposite-edge math, and per-room color rendering.
  - `tests/test_movement.py` (lines 63-80) — `test_wall_clamp_left/right/top/bottom` must be reconciled: either retargeted at an edge that is still a sealed wall in the starting room, or `move_player` test calls must thread a room context.
  - `tests/e2e/adversarial/test_rooms_adversarial.py` (NEW, or extend existing adversarial suite) — adversarial transition scenarios (rapid edge crossing, diagonal exit, re-entry).

- **Downstream consumers (everything that imports `adventure`):**
  - `tests/test_adventure.py` (lines 1-47) — consumes `LOGICAL_WIDTH`, `LOGICAL_HEIGHT`, `PLAYER_SIZE`, `PLAYER_X`, `PLAYER_Y`, `initialize_pygame`, `create_window`, `run_game_loop`. None of these symbols are slated for renaming, but `run_game_loop`'s internal state model changes. If any test drives the loop for N frames and then asserts pixel/position state, room state will now be part of that surface.
  - `tests/test_movement.py` (lines 1-86) — consumes `WALL_THICKNESS`, `LOGICAL_WIDTH`, `LOGICAL_HEIGHT`, `PLAYER_SIZE`, `PLAYER_X`, `PLAYER_Y`, `PLAYER_SPEED`, `move_player`. The `move_player` signature is the high-risk surface — adding a `room` parameter is a breaking change to every caller.
  - `tests/conftest.py` — no behavioral change, but headless SDL fixture continues to be the only way the new room tests can run in CI.
  - `tests/e2e/adversarial/test_adventure_adversarial.py`, `tests/e2e/adversarial/test_movement_adversarial.py` — pre-existing adversarial suites; if they assert clamp-at-edge behavior they will fail under the new transition semantics.
  - `README.md` — no new user-facing controls (still arrow keys), so docs are unaffected unless rooms get named or numbered visibly.

## Risks

| Risk | Likelihood | Severity | Notes |
|------|:----------:|:--------:|-------|
| `move_player` signature change breaks `tests/test_movement.py` | H | M | Tests call `move_player(...)` with current 4-arg signature; adding a required `room` argument breaks every call site. Mitigation: default the parameter (e.g., `room=None` → legacy clamp behavior) OR update the test in the same commit. |
| `test_wall_clamp_*` semantically wrong after change | H | M | Once an edge becomes a passage, clamp tests targeting that edge will fail or assert the wrong thing. Tests must be retargeted to a sealed edge of the starting room. |
| Adversarial suites silently fail on transition behavior | M | M | `tests/e2e/adversarial/test_movement_adversarial.py` likely encodes clamp-at-edge assumptions. Not yet read in scope; needs inspection. |
| Off-by-one / jitter on transition warp causes immediate re-transition | M | H | If player exits east at `x = _X_MAX + 1` and is warped to `x = _X_MIN` of the new room while still holding the east key, naive logic re-triggers the same exit next frame. Need a one-frame debounce or warp to `_X_MIN + PLAYER_SIZE` so player is inside the next room. |
| Disconnected room graph (orphan room, asymmetric adjacency) | M | M | Hand-authored adjacency map can have `A.east = B` but `B.west = None`, stranding the player. Need a validator (test) that adjacency is symmetric and the graph is connected. |
| `ROOM_COLOR` constant removed/renamed | L | L | Tests don't import it today (only `WALL_THICKNESS` etc. are imported per location.md), but removing it would break any out-of-tree consumer. Keep as default/back-compat alias. |
| `draw_room` signature change forces every render call site to update | L | L | Only one caller (`run_game_loop` line 121) — small surface. Easy to update atomically. |
| Performance regression at 60 FPS | L | L | 4-6 rooms with dict lookup per frame is trivial; pygame draw cost unchanged. |
| Headless tests can't observe color difference per room | M | M | `conftest.py` uses `SDL_VIDEODRIVER=dummy`. Color assertions need to read pixels via `pygame.Surface.get_at()` (works in dummy driver) — verify before relying on it. |
| New module-level state (current_room) becomes a global → flaky tests | M | M | If `current_room` is stored as a module global instead of being passed through `run_game_loop`, tests run in the same interpreter will leak state. Prefer parameterized state or explicit reset. |
| Missing T3 acceptance criteria (which 4 vs 6 rooms? layout?) | H | M | The location boundary says "≥4, ≤6 rooms" — the exact count, colors, and layout are not pinned. Needs decision before design. |

## Mitigations / Verification

- **Required automated tests:**
  - `tests/test_rooms.py` (NEW):
    - `test_room_registry_has_4_to_6_rooms` — count assertion.
    - `test_room_has_bg_color_and_neighbors` — schema assertion (each room exposes `bg_color`, `neighbors` dict with N/S/E/W keys).
    - `test_adjacency_is_symmetric` — for every `A.neighbors[dir] == B`, `B.neighbors[opposite(dir)] == A`.
    - `test_adjacency_graph_is_connected` — BFS from start room reaches all rooms.
    - `test_transition_east_warps_player_to_west_edge_of_neighbor` (and N/S/W variants) — call the transition function with an exiting player position and assert active-room swap + position warp.
    - `test_no_immediate_re_transition` — after a warp, one more `move_player` step in the same direction must NOT trigger another transition immediately.
    - `test_sealed_edge_still_clamps` — pressing into a `neighbors[dir] is None` edge keeps the player at the boundary.
    - `test_draw_room_uses_active_room_color` — render one frame, sample pixel via `pygame.Surface.get_at()` against the room's `bg_color`.
  - `tests/test_movement.py` reconciliation:
    - Either update wall-clamp tests to target a sealed edge of the starting room, or thread a "sealed-on-all-sides" room fixture into the existing `move_player` calls.
  - `tests/e2e/adversarial/test_rooms_adversarial.py` (NEW or extension):
    - Diagonal exit (player holds two arrow keys at a corner where one edge is sealed and the other is a passage).
    - Rapid alternating direction at an edge (verify no transition thrash).
    - Full graph traversal — visit every room in the registry, asserting `current_room` changes match expected adjacency.

- **Manual verification:**
  1. `python adventure.py` — game launches at 60 FPS, no console errors.
  2. Walk player to each of the 4 edges of the starting room. For passage edges, confirm the background color changes and player appears at the opposite edge. For sealed edges, confirm clamp (no transition).
  3. Traverse the full graph (visit every room at least once) and return to start — colors match registry, no rooms are unreachable.
  4. Hold a single direction across a transition — confirm player does not "teleport" through multiple rooms in one frame (debounce works).
  5. Close window — clean shutdown (T1/T2 behavior preserved).

- **Rollout:**
  - Single branch / single PR. No feature flag — this is a local Python pygame game with no production deployment surface. Either it ships in `adventure.py` HEAD or it doesn't.
  - Order of commits inside the PR:
    1. Add Room model + registry + tests (no behavior change yet, room not consumed).
    2. Wire `current_room` into `run_game_loop`, generalize `draw_room`, default to the starting room.
    3. Convert `move_player` to room-aware clamping (default `room=None` preserves old behavior for back-compat).
    4. Add transition handler, hook into the loop, update `tests/test_movement.py`.
    5. Add adversarial e2e suite.

- **Rollback:**
  - `git revert <merge-sha>` — single-commit revert restores T2 behavior (single room, all edges clamp). No DB, no migration, no deployed artifact to roll back.
  - If a partial revert is needed (e.g., transition broken but room registry fine), revert commits 3-5 only, leaving 1-2 as dormant infrastructure.

## Unknowns / Missing Info

- Exact room count and layout — question: Is the room graph a 2×2 (4 rooms), 2×3 (6 rooms), or hand-authored chain? The location boundary says "≥4, ≤6" but doesn't pin layout.
- Per-room colors — question: Are these arbitrary (designer picks 4-6 distinct hex values) or must they mirror Atari Adventure's original kingdom colors? README and historical `.bf-feature/` artifacts should be checked.
- Sealed-edge marker — question: Is a sealed edge represented as `neighbors[dir] = None`, a separate `walls = {"N","E"}` set, or implicit (any direction not in `neighbors` is sealed)? Affects `draw_room`'s wall-rendering logic.
- `move_player` signature compatibility — question: Should the new `room` parameter be optional (`room=None` → clamp legacy behavior) to preserve `tests/test_movement.py` call sites, or is a hard signature change acceptable with test updates in the same commit?
- Adversarial suite contents — question: Does `tests/e2e/adversarial/test_movement_adversarial.py` encode clamp-at-edge invariants that will break under transitions? Need to read the file before estimating its blast.
- `pygame.Surface.get_at()` under `SDL_VIDEODRIVER=dummy` — question: Confirmed-working in headless CI for color assertions? If not, color verification must move to RGB-equality on the room object instead of rendered output.
- Module-level state vs. function-local — question: Should `current_room` be a module global, an attribute of a Game object, or a local variable threaded through `run_game_loop`? Codebase convention to date (T1/T2) is functional / module-level; a Game class would be a departure.
- Initial / spawn room — question: Which room is the start? Pinning a stable `START_ROOM` constant helps tests and matches Atari Adventure's "yellow castle" convention.

## Evidence (Triptych)

- `adventure.py::move_player` (lines 54-64): clamps to `_X_MIN/_X_MAX/_Y_MIN/_Y_MAX` — via filesystem `Read(adventure.py 1-146)` per location.md. Triptych MCP not productive on a 1-module Python repo (locator confirmed: `get_architecture_map` produces no nodes beyond the module itself; `semantic_search` filters expect Controller/Service patterns that don't exist).
- `adventure.py::draw_room` (lines 77-92): hardcoded `ROOM_COLOR` + four wall rects — via filesystem `Read(adventure.py 1-146)`.
- `adventure.py::run_game_loop` (lines 100-129): calls `move_player`, `draw_room`, `draw_player` each frame — via filesystem `Read(adventure.py 1-146)`; confirmed by location.md edge list lines 119/121/122.
- `tests/test_movement.py` -> imports `adventure` (line 6); calls `move_player`; clamp tests at lines 63-80 — via location.md edges; Read confirmed in locator artifact lines 18-19.
- `tests/test_adventure.py` -> imports public symbols `LOGICAL_WIDTH`, `LOGICAL_HEIGHT`, `PLAYER_SIZE`, `PLAYER_X`, `PLAYER_Y`, `initialize_pygame`, `create_window`, `run_game_loop` (line 3) — via location.md edges.
- `tests/conftest.py` sets `SDL_VIDEODRIVER=dummy` / `SDL_AUDIODRIVER=dummy` — via location.md Read 1-11; required for headless test verification of rendered color.
- `tests/e2e/adversarial/test_adventure_adversarial.py`, `tests/e2e/adversarial/test_movement_adversarial.py` exist — via location.md Glob `tests/e2e/**/*.py`; contents not yet read (recorded as Unknown above).
- No external production consumers of `adventure` module — via location.md Glob `**/*.py` (1 production module, 4 active test files, 9 archived `.bf-feature/**` batch test files only).

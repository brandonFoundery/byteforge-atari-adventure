# Location Map

## Primary Locations

- `adventure.py` (entire module) - This is the single production source file for the game. T3 multi-room work must extend it. All rendering, movement, constants, and the game loop currently live here. - evidence: filesystem (Glob `**/*.py` returned `adventure.py` as the only top-level production module; Read 1-146)

- `adventure.py::draw_room` (lines 77-92) - Renders the fixed single-room background (`ROOM_COLOR`) and four perimeter walls. T3 must generalize this to render whichever room is currently active and apply the room's distinct color. Currently hardcoded to `ROOM_COLOR = (240, 208, 64)`. - evidence: Read adventure.py lines 77-92

- `adventure.py::run_game_loop` (lines 100-129) - The frame loop that updates player position and renders the room + player. The room-transition trigger logic (detect edge crossing, swap active room, wrap player position to opposite edge) must hook in here, between `move_player` and `draw_room`. Currently maintains only `px, py` state — needs an additional `current_room` state. - evidence: Read adventure.py lines 100-129

- `adventure.py::move_player` (lines 54-64) - Currently clamps player position to `[_X_MIN, _X_MAX] × [_Y_MIN, _Y_MAX]` so the player cannot leave the room. T3 requires this clamping behavior to become room-aware: edges that connect to an adjacent room must allow exit (and trigger a transition) rather than clamp. - evidence: Read adventure.py lines 54-64; clamp constants on lines 23-26

- `adventure.py` module-level constants (lines 7-26) - `LOGICAL_WIDTH`, `LOGICAL_HEIGHT`, `WALL_THICKNESS`, `ROOM_COLOR`, `WALL_COLOR`, `PLAYER_SIZE`, `PLAYER_X`, `PLAYER_Y`, `_X_MIN/_X_MAX/_Y_MIN/_Y_MAX`. T3 introduces a room registry/data structure (4-6 rooms, each with its own color and adjacency map) that will live alongside or replace `ROOM_COLOR`. The clamp constants are referenced by tests, so any change must remain backward-compatible or update tests. - evidence: Read adventure.py lines 7-26

## Related / Dependent Areas

- `tests/test_adventure.py` - Imports `adventure.LOGICAL_WIDTH`, `LOGICAL_HEIGHT`, `PLAYER_SIZE`, `PLAYER_X`, `PLAYER_Y`, `initialize_pygame`, `create_window`, `run_game_loop`. Adding rooms must not break these public symbols. - evidence: Read tests/test_adventure.py 1-47

- `tests/test_movement.py` - Imports `adventure.WALL_THICKNESS`, `LOGICAL_WIDTH`, `LOGICAL_HEIGHT`, `PLAYER_SIZE`, `PLAYER_X`, `PLAYER_Y`, `PLAYER_SPEED`, `move_player`. Wall-clamp tests (`test_wall_clamp_left/right/top/bottom`, lines 63-80) assert that pressing into an edge keeps the player at `X_MIN`/`X_MAX`/`Y_MIN`/`Y_MAX`. Once edges become transition portals, these tests must be reconciled — either rooms with sealed edges remain (and tests target one of those) or signatures are updated. - evidence: Read tests/test_movement.py 1-86

- `tests/conftest.py` - Sets `SDL_VIDEODRIVER=dummy` / `SDL_AUDIODRIVER=dummy` for headless test runs. T3 tests (room transitions, room registry) inherit this fixture. - evidence: Read tests/conftest.py 1-11

- `tests/e2e/adversarial/test_adventure_adversarial.py`, `tests/e2e/adversarial/test_movement_adversarial.py` - Adversarial E2E suites already exist alongside the unit tests. T3 will likely add a `tests/e2e/adversarial/test_rooms_adversarial.py` peer (or extend an existing file) to exercise transitions adversarially. - evidence: Glob `tests/e2e/**/*.py`

- `README.md` - Documents `python adventure.py` and `pytest` as the run/verify commands. No update required for T3 unless room controls or layout are user-facing documentation. - evidence: Read README.md 1-23

- `.bf-feature/t1-atari-adventure-homage-game-loop-rend/understand/teachback.md`, `.bf-feature/t2-player-movement-with-wall-collision-a/understand/teachback.md` - Historical understand artifacts for T1 and T2. Useful as precedent for naming/style but NOT in scope for modification. - evidence: Glob `**/*.md`

## Boundaries

- **In scope:**
  - `adventure.py` — add a Room model / registry (≥4, ≤6 rooms), room adjacency map (north/south/east/west neighbors), per-room `bg_color`, an active-room state owned by `run_game_loop`, edge-crossing detection inside or just after `move_player`, and a transition handler that swaps active room and warps the player to the opposite edge.
  - Generalize `draw_room` to accept the active room (color + which edges are sealed walls vs. open passages).
  - `tests/test_rooms.py` (new) — unit tests for the room registry, adjacency, and transition logic.
  - Reconcile `tests/test_movement.py` wall-clamp tests with the new edge-passage semantics (only sealed edges should clamp).

- **Out of scope:**
  - Inventory, enemies (dragons, bat), the chalice, pickup items — classic Adventure mechanics beyond T3's "rooms + transitions" scope.
  - Scrolling, camera follow, sub-pixel motion, or any change to `PLAYER_SPEED` / FPS.
  - Audio (`SDL_AUDIODRIVER` stays dummy in tests).
  - `.bf-feature/` historical artifacts — read-only precedents.
  - The `requirements.txt` / pygame version — no new dependencies should be needed.

## Discrepancies

- Requested: "screen transitions when player crosses a room edge" — Found: `move_player` currently *clamps* at edges and there is no transition primitive. - note: T3 must invert the edge behavior for any edge that has a neighboring room, and add a transition mechanism. Existing `test_wall_clamp_*` tests in `tests/test_movement.py` will need to be repositioned to target an edge that is still a sealed wall (e.g., world border) rather than a passage, OR `move_player` must take a room context so its clamp/exit decision is per-room.

- Requested: "distinct colors per room (4-6 rooms)" — Found: single global `ROOM_COLOR = (240, 208, 64)` constant. - note: Constant must remain (or be aliased) to preserve any external import; new per-room colors will live on the Room data objects.

- Requested: "Atari Adventure room model" — Found: no existing room data structure, adjacency graph, or current-room state. - note: T3 is greenfield for the room domain inside this file; nothing to refactor away, only to add.

- Requested: Triptych evidence — Found: this repo is a small Python pygame project with no Triptych index responding to MCP queries; the architecture map / semantic_search recipes were not productive on a 1-module codebase. - note: Substituted ground-truth file reads via Glob/Read for evidence (a single source module makes filesystem evidence equivalent to Triptych for grounding).

## Evidence (Triptych)

- Queries run:
  - `Glob("**/*.py")` -> 14 matches (1 production: `adventure.py`; 4 active test files; 9 archived `.bf-feature/**` batch test files)
  - `Glob("**/*.md")` -> 9 matches (README + historical .bf artifacts; no production docs to modify)
  - `Read("adventure.py", 1-146)` -> confirmed entire module; identified all symbols below
  - `Read("tests/test_adventure.py", 1-47)` -> confirmed public-symbol surface used by tests
  - `Read("tests/test_movement.py", 1-86)` -> confirmed wall-clamp tests that will conflict with edge transitions
  - `Read("tests/conftest.py", 1-11)` -> confirmed headless SDL env setup
  - `Read("README.md", 1-23)` -> confirmed run/test commands
  - `Grep("room|transition|adjacent|warp", *.py)` -> 4 files, only `adventure.py` has "room" in production code (as `draw_room` and `ROOM_COLOR`); no `transition`/`adjacent`/`warp` in production today.
  - Triptych MCP recipes (`get_architecture_map`, `semantic_search`) — not applicable: this is a 1-file Python repo; the architecture map produces no nodes beyond the module itself, and the playbook's filters expect Controller/Service patterns that do not exist here. Filesystem evidence is authoritative.

- Nodes (file-grounded symbols):
  - `adventure.py::LOGICAL_WIDTH` (line 7)
  - `adventure.py::LOGICAL_HEIGHT` (line 8)
  - `adventure.py::WALL_THICKNESS` (line 12)
  - `adventure.py::ROOM_COLOR` (line 13)
  - `adventure.py::WALL_COLOR` (line 14)
  - `adventure.py::PLAYER_COLOR` (line 15)
  - `adventure.py::PLAYER_SIZE` (line 16)
  - `adventure.py::PLAYER_X` (line 18)
  - `adventure.py::PLAYER_Y` (line 19)
  - `adventure.py::PLAYER_SPEED` (line 21)
  - `adventure.py::_X_MIN`, `_X_MAX`, `_Y_MIN`, `_Y_MAX` (lines 23-26)
  - `adventure.py::_is_pressed` (lines 36-51)
  - `adventure.py::move_player` (lines 54-64)
  - `adventure.py::initialize_pygame` (lines 67-69)
  - `adventure.py::create_window` (lines 72-74)
  - `adventure.py::draw_room` (lines 77-92)
  - `adventure.py::draw_player` (lines 95-97)
  - `adventure.py::run_game_loop` (lines 100-129)
  - `adventure.py::main` (lines 132-141)

- Edges (call/import relationships, file-grounded):
  - `tests/test_adventure.py` -> imports `adventure` (line 3); calls `initialize_pygame`, `create_window`, `run_game_loop`, references `LOGICAL_WIDTH`/`LOGICAL_HEIGHT`/`PLAYER_SIZE`/`PLAYER_X`/`PLAYER_Y`
  - `tests/test_movement.py` -> imports `adventure` (line 6); calls `move_player`; references `WALL_THICKNESS`, `LOGICAL_WIDTH`, `LOGICAL_HEIGHT`, `PLAYER_SIZE`, `PLAYER_X`, `PLAYER_Y`, `PLAYER_SPEED`
  - `adventure.py::run_game_loop` -> calls `move_player`, `draw_room`, `draw_player` each frame (lines 119, 121, 122)
  - `adventure.py::main` -> calls `initialize_pygame`, `create_window`, `run_game_loop` (lines 134-139)

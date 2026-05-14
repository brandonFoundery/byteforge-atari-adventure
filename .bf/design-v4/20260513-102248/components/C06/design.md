# C06 — GameLoopIntegration — Design

**Type:** integration | **Epic:** EPIC-003 (+ STORY-001-3 landing)
**Stories:** STORY-003-3, STORY-003-4, STORY-003-5, STORY-003-6 (+ STORY-001-3)
**Dependencies:** C02, C03, C04, C05
**Requirements covered:** REQ-015..REQ-020, REQ-043..REQ-063

## 1. Purpose

Integrate all prior component contracts into a coherent runtime flow and test
suite:

- validate room graph once at loop start (C02)
- render active room each frame (C03)
- detect passage exits vs sealed clamps (C04)
- warp player/room deterministically on transitions (C05)
- land the full `tests/test_rooms.py` and adversarial test coverage

## 2. `run_game_loop` integration design

### 2.1 Initialization

At function entry (not module import):

```python
assert_symmetric(ROOMS)
assert_connected(ROOMS, START_ROOM)

logical_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
current_room = ROOMS[START_ROOM]   # function-local only
px, py = PLAYER_X, PLAYER_Y
```

Validator call order matters: symmetry first, connectivity second. If a bad
neighbor id exists, the error is surfaced by `assert_symmetric`.

### 2.2 Per-frame flow

```python
keys = pygame.key.get_pressed()
move_result = move_player(px, py, keys, room=current_room)

if isinstance(move_result[0], str):
    # ("exit", direction)
    direction = move_result[1]
    current_room, px, py = _warp_position(current_room, direction, px, py)
else:
    px, py = move_result

draw_room(logical_surface, current_room)
draw_player(logical_surface, px, py)
```

Key guarantees:
- Transition reassignment occurs before `draw_room` for the same frame
  (REQ-044).
- No-exit frames leave `current_room` unchanged (REQ-046).
- `current_room` is local, never module-scoped (REQ-047).

## 3. Movement-test reconciliation (`tests/test_movement.py`)

### 3.1 Fixture strategy

Add module-level fixture room with all edges sealed:

```python
SEALED_ROOM = adventure.Room(
    id="sealed",
    bg_color=(0, 0, 0),
    neighbors={"N": None, "S": None, "E": None, "W": None},
)
```

All clamp tests call:

```python
adventure.move_player(..., room=SEALED_ROOM)
```

This preserves T2 boundary assertions while documenting explicit room-aware
semantics (REQ-048..REQ-052).

### 3.2 Invariants preserved

- Boundary constants unchanged (`X_MIN/X_MAX/Y_MIN/Y_MAX` derivation remains).
- Assertions still verify exact clamp coordinates, not fuzzy bounds.
- Transition assertions stay out of `tests/test_movement.py`.

## 4. `tests/test_rooms.py` structure

`tests/test_rooms.py` is the central T3 specification file and includes three
blocks.

### 4.1 Registry/foundation tests (11 required names)

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

These satisfy STORY-001-3 requirements (REQ-015..REQ-020).

### 4.2 Rendering/current-room tests (from C03)

- `test_draw_room_uses_active_room_color`
- `test_draw_room_omits_wall_on_passage_edge`
- `test_run_game_loop_uses_start_room_for_initial_frame`
- `test_rendered_frame_matches_start_room_bg_color`
- `test_rendered_frame_shows_walls_only_on_sealed_edges_of_start_room`
- `test_no_module_global_current_room`

### 4.3 Transition math/flow tests (from C04/C05)

- `test_transition_east_warp_position`
- `test_transition_west_warp_position`
- `test_transition_north_warp_position`
- `test_transition_south_warp_position`
- `test_no_immediate_re_transition`
- `test_full_graph_walkable_from_start`
- `test_re_entry_is_deterministic`
- `test_sealed_edge_does_not_transition`

These cover REQ-053..REQ-058 plus integration properties REQ-043..REQ-047.

## 5. Adversarial E2E file

Create `tests/e2e/adversarial/test_rooms_adversarial.py` with scripted frame
inputs and headless loop runs.

Required scenarios:
- diagonal corner (E passage + S sealed, horizontal priority) (REQ-059)
- alternating L/R passage crossing for 10+ frames (REQ-060)
- scripted full-graph traversal + final render color check (REQ-061)
- held-direction 60-frame debounce (exactly one transition) (REQ-062)

No new dependencies; reuse existing conftest/headless setup (REQ-063).

## 6. Traceability gate and coverage accounting

C06 closes remaining requirements and verifies full trace coverage:

- STORY-001-3: REQ-015..020
- STORY-003-3: REQ-043..047
- STORY-003-4: REQ-048..052
- STORY-003-5: REQ-053..058
- STORY-003-6: REQ-059..063

Combined with C01..C05, all REQ-001..REQ-063 are covered exactly once in
component ownership.

## 7. Failure handling

Loop-level defensive expectations:

- If validators raise, loop exits with explicit failure rather than rendering
  inconsistent rooms.
- `_warp_position` errors surface immediately (invalid exit/registry) and are
  not swallowed.
- No silent fallback to module-global state.

Test-level expectations:

- Synthetic bad registries live inside tests and never mutate `adventure.ROOMS`.
- Render assertions sample RGB `[:3]` to avoid alpha noise.

## 8. REQ coverage matrix

| REQ | How satisfied |
|-----|---------------|
| REQ-015 | `tests/test_rooms.py` created and collected by pytest. |
| REQ-016 | All 11 named registry tests implemented as separate `test_*` functions. |
| REQ-017 | `tests/test_rooms.py` passes under headless `tests/conftest.py`. |
| REQ-018 | Legacy suites remain green; `tests/test_movement.py` reconciled intentionally. |
| REQ-019 | `tests/test_rooms.py` imports only `adventure` and `pytest`. |
| REQ-020 | Validator-failure cases use synthetic inline registries only. |
| REQ-043 | `run_game_loop` seeds `current_room` from `ROOMS[START_ROOM]`. |
| REQ-044 | Exit result triggers `_warp_position` and room/player reassignment before drawing. |
| REQ-045 | Headless integration test verifies post-transition room color and player placement. |
| REQ-046 | No-exit frames preserve `current_room`. |
| REQ-047 | `current_room` remains function-local (`not hasattr(adventure, "current_room")`). |
| REQ-048 | Sealed fixture room used by all movement clamp tests. |
| REQ-049 | Left clamp invariant preserved at `_X_MIN`. |
| REQ-050 | Right/top/bottom clamp invariants preserved at original T2 bounds. |
| REQ-051 | No transition assertions in `tests/test_movement.py`. |
| REQ-052 | `pytest tests/test_movement.py` passes with new signature. |
| REQ-053 | East transition test asserts destination room + inward x offset. |
| REQ-054 | W/N/S transition tests assert mirror behavior. |
| REQ-055 | One-frame post-warp hold does not immediately retrigger transition. |
| REQ-056 | BFS via `_warp_position` reaches every room from start. |
| REQ-057 | `_warp_position` deterministic for identical inputs. |
| REQ-058 | Sealed edge returns no transition and no room change. |
| REQ-059 | Corner diagonal adversarial case transitions horizontally and clamps vertical. |
| REQ-060 | Alternating left/right adversarial sequence toggles only between expected adjacent rooms. |
| REQ-061 | Full-graph scripted traversal ends in expected room and matching rendered color. |
| REQ-062 | 60-frame held-direction run produces exactly one transition. |
| REQ-063 | Adversarial suite passes headless with existing harness/deps. |

## 9. Decisions

- **D6.1 — Validators run inside `run_game_loop` startup, not at import.**
  Keeps import side effects minimal and test setup explicit.
- **D6.2 — Loop consumes C04 discriminated exit tuple directly.**
  Clear branch semantics with no hidden sentinel constants.
- **D6.3 — Movement clamp tests explicitly pass sealed fixture room.**
  Documents intent under new semantics and prevents accidental passage drift.
- **D6.4 — Transition correctness split between unit and adversarial E2E tests.**
  Faster math verification plus realistic frame-sequence stress.

## 10. Risks

- **R2 — module-global room leak.** Mitigated by dedicated test and local-only
  assignment discipline.
- **R7 — regressions in legacy suites from signature/wiring changes.** Mitigated
  by explicit T1/T2 regression checks and fixture reconciliation.

## 11. Out of scope

- Transition FX (fade/flash/labels/audio).
- Expanding room count beyond authored 4-room topology.
- Inventory/enemy/gameplay features unrelated to room transitions.

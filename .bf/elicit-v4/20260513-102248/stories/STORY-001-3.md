# STORY-001-3: `tests/test_rooms.py` — registry coverage

## Parent Epic
EPIC-001 — Room model + registry (foundation, no behavior change)

## User Value
As the CI gate, I need automated tests that pin every invariant of the room
registry (count, schema, distinct colors, symmetric adjacency, connected
graph, validator behavior on broken fixtures), so that any future edit to
the authored map fails fast instead of producing a stranded player at
runtime.

## Scope
**Create:** `tests/test_rooms.py` (NEW).

**Do NOT touch:** any production source. Do NOT modify
`tests/test_adventure.py` or `tests/test_movement.py` in this story —
those passing unmodified is the regression gate.

## Design Notes
- Use the same `conftest.py`-provided headless SDL fixture (no display
  required for these tests; the registry is pure data).
- Use `pytest` style consistent with existing `tests/test_adventure.py`
  and `tests/test_movement.py` (plain functions, simple assertions).
- For validator-failure tests, build small synthetic registries inline
  (do NOT mutate `adventure.ROOMS`).

### Test cases
1. `test_room_registry_has_4_to_6_rooms` — `4 <= len(ROOMS) <= 6`.
2. `test_room_ids_are_unique` — `len(set(ROOMS.keys())) == len(ROOMS)`.
3. `test_room_has_bg_color_and_neighbors` — for every room, `bg_color` is
   a 3-tuple of ints in `0..255`, and `neighbors` has exactly the keys
   `{"N","S","E","W"}`.
4. `test_all_bg_colors_pairwise_distinct` — set of `bg_color` tuples has
   length equal to `len(ROOMS)`.
5. `test_neighbor_values_reference_existing_rooms_or_none` — every
   neighbor value is either `None` or a key in `ROOMS`.
6. `test_adjacency_is_symmetric` — calls `assert_symmetric(ROOMS)` and
   asserts no exception.
7. `test_adjacency_graph_is_connected` — calls
   `assert_connected(ROOMS, START_ROOM)` and asserts no exception.
8. `test_start_room_constant_is_valid` — `START_ROOM in ROOMS` and
   `ROOMS[START_ROOM].bg_color == (240, 208, 64)`.
9. `test_room_color_legacy_constant_preserved` —
   `adventure.ROOM_COLOR == (240, 208, 64)`.
10. `test_assert_symmetric_rejects_asymmetric_registry` — build a 2-room
    fixture where A.E = B but B.W = None; expect `ValueError`.
11. `test_assert_connected_rejects_orphan_room` — build a 3-room fixture
    where room C has all-None neighbors; expect `ValueError` mentioning C.

## Acceptance Criteria
- **REQ-015**: New file `tests/test_rooms.py` exists and is collected by
  `pytest` (i.e., contains at least one `test_*` function discovered from
  the project root).
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

## Out of Scope
- Tests for rendering, movement, or transitions (later epics).
- Adversarial e2e tests (EPIC-003 / its successors).

## Dependencies
- STORY-001-1 (needs `ROOMS`, `START_ROOM`, `Room`).
- STORY-001-2 (needs `assert_symmetric`, `assert_connected`).

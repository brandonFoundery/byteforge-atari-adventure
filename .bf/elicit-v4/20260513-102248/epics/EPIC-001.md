# EPIC-001: Room model + registry (foundation, no behavior change)

## Goal
Introduce the core data foundation for the multi-room world: a `Room` data
structure carrying a per-room background color and a 4-direction adjacency
map, plus a hand-authored registry of 4–6 rooms wired into a connected graph.
This epic is pure data + validation — no rendering, no movement change, no
transitions. T1/T2 behavior must remain bit-for-bit identical at the end of
this epic.

## Success Criterion (from teachback)
Game contains 4–6 distinct rooms with per-room `bg_color` and a connected
adjacency graph; registry validates symmetry and connectivity; T1/T2 tests
still pass.

## Scope
**In scope** (per `location.md`):
- `adventure.py` — add a `Room` data class (or equivalent dict/namedtuple)
  exposing `id`, `bg_color`, and `neighbors` (dict keyed by `"N"/"S"/"E"/"W"`
  with values that are either another room id or `None` for a sealed edge).
- `adventure.py` — add a `ROOMS` registry (module-level) containing 4–6 rooms
  with hand-authored distinct background colors and a connected adjacency
  graph.
- `adventure.py` — add a `START_ROOM` constant naming the spawn room.
- `adventure.py` — preserve `ROOM_COLOR = (240, 208, 64)` as the starting
  room's `bg_color` (or alias) so legacy imports keep working.
- `tests/test_rooms.py` (NEW) — registry shape, count bound, symmetry,
  connectivity, distinct-color assertions.

**Out of scope** (deferred to EPIC-002 / EPIC-003):
- Changing `draw_room` to consume the registry (EPIC-002).
- Threading `current_room` through `run_game_loop` (EPIC-002).
- Edge-crossing detection / transitions / room-aware movement (EPIC-003).
- Any change to `move_player`'s signature or clamping behavior (EPIC-003).
- Interior wall layouts, enemies, items, audio, save/load — out of T3 entirely.

## Boundaries / Touched Files
- `adventure.py` (add new symbols only; do NOT modify existing function
  bodies in this epic).
- `tests/test_rooms.py` (NEW).
- `tests/test_adventure.py`, `tests/test_movement.py` — MUST NOT change in
  this epic (proves "no behavior change").

## Resolved Decisions (carried from teachback / impact)
- **Room count**: 4 rooms (smallest count that satisfies "4–6", keeps the
  authored map simple and 100% testable). Topology is a 2×2 grid.
- **Starting room**: top-left of the 2×2 grid, named `"yellow"`, carries
  the legacy `ROOM_COLOR = (240, 208, 64)` so existing tests/screenshots
  remain stable.
- **Adjacency representation**: `neighbors` dict keyed by `"N"/"S"/"E"/"W"`;
  value is a room id (string) for a passage or `None` for a sealed wall.
  This satisfies the `impact.md` question on sealed-edge representation.
- **Bidirectionality**: all edges are bidirectional; the registry validator
  enforces symmetry (`A.neighbors["E"] == B  ⇒  B.neighbors["W"] == A`).
- **Distinct colors**: each room has a unique RGB triple, hand-authored.
  Concrete palette is fixed in STORY-001-1.

## Acceptance Criteria (epic-level rollup)
- Importing `adventure` exposes a `ROOMS` mapping with ≥4 and ≤6 entries.
- Every room exposes `bg_color: tuple[int, int, int]` and a `neighbors`
  dict with all four cardinal keys present.
- The graph is connected (BFS from `START_ROOM` reaches every room id).
- Adjacency is symmetric for every authored edge.
- All `bg_color` values are pairwise distinct.
- `tests/test_adventure.py` and `tests/test_movement.py` continue to pass
  unmodified (regression gate for "no behavior change").

## Stories
- STORY-001-1 — Add `Room` data structure + `ROOMS` registry + `START_ROOM`.
- STORY-001-2 — Add registry validation helpers (`assert_symmetric`,
  `assert_connected`) used by tests and importable for future runtime use.
- STORY-001-3 — Create `tests/test_rooms.py` covering count, schema,
  symmetry, connectivity, and distinct colors.

## Risks Addressed (from impact.md)
- "Disconnected room graph (orphan room, asymmetric adjacency)" — mitigated
  by validator + tests in STORY-001-2 / STORY-001-3.
- "`ROOM_COLOR` constant removed/renamed" — mitigated: kept as alias to the
  starting room's `bg_color`.
- "Missing T3 acceptance criteria (which 4 vs 6 rooms? layout?)" — mitigated
  by pinning 4 rooms / 2×2 grid in this epic.

## Open Questions
- None blocking. All decisions are resolved above.

## Non-Goals (re-emphasised)
- No frame/render change. `draw_room` is NOT modified here.
- No `move_player` signature change. EPIC-003 owns that.
- No `current_room` state in the game loop yet. EPIC-002 owns that.

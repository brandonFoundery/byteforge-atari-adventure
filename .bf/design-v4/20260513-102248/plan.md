# Design-v4 Plan — T3 Multi-Room World + Screen Transitions

**Run ID:** 20260513-102248
**Mode:** spec-driven
**Source:** `.bf/elicit-v4/20260513-102248/final/assembled.md`
**Ticket:** c847ce28-daf2-4b0e-6c13-08deb0efcb30

## Source Inputs

- Understand diamond: `.bf/understand-v4/20260513-102248/diamond`
- Elicit assembled spec: `.bf/elicit-v4/20260513-102248/final/assembled.md`
- Requirements trace (63 reqs / 3 epics / 12 stories): `.bf/elicit-v4/20260513-102248/final/requirements-trace.md`

## Design Strategy

The elicit phase resolved all cross-cutting decisions:
- 4-room 2x2 grid (yellow / blue / green / purple)
- Start room: yellow (back-compat with existing `ROOM_COLOR = (240, 208, 64)`)
- Sealed edges: `neighbors[dir] is None`
- `current_room` is function-local inside `run_game_loop` (never module-global)
- Diagonal exits: horizontal axis wins ties
- Post-transition warp: mirror perpendicular coord + inward offset `PLAYER_SPEED + 1`

The implementation surface is a single production file (`adventure.py`) plus
test files. The design decomposes work along the natural seams in `adventure.py`
so each component can be implemented + tested in isolation, then composed in
`run_game_loop`.

## Component Decomposition

Six components were chosen instead of three epic-sized blocks because the
movement + rendering + transition logic each has independently testable
contracts that benefit from clean per-component design docs. The DAG is:

```
C01 (Room model + registry)
 |
 +-- C02 (Validators)
 +-- C03 (Room-aware rendering)        \
 +-- C04 (Room-aware move_player)       +--> C06 (Game loop integration + tests)
 +-- C05 (Transition warp helper)      /
```

### Components

| ID  | Name                       | Epic     | Type              | Depends on    |
|-----|----------------------------|----------|-------------------|---------------|
| C01 | RoomDataModelAndRegistry   | EPIC-001 | data-model        | -             |
| C02 | RegistryValidators         | EPIC-001 | backend-service   | C01           |
| C03 | RoomAwareRendering         | EPIC-002 | frontend-component| C01           |
| C04 | RoomAwareMovement          | EPIC-003 | backend-service   | C01           |
| C05 | TransitionWarpHelper       | EPIC-003 | backend-service   | C01           |
| C06 | GameLoopIntegration        | EPIC-003 | integration       | C02,C03,C04,C5|

### Rationale

- **C01 first.** Everything depends on the `Room` shape and the `ROOMS` registry.
  Pure data + module-level constants. No I/O, no pygame import for the model.
- **C02 validators.** Pure functions (`assert_symmetric`, `assert_connected`).
  Independently testable, no rendering, no side effects.
- **C03 rendering.** Generalizes `draw_room(surface)` -> `draw_room(surface, room)`.
  Walls only on sealed edges. Threads `current_room` as a function-local in
  `run_game_loop` (no module global). Does not yet wire transitions.
- **C04 movement.** Changes `move_player` to accept a `room` argument. Returns
  either clamped `(x, y)` or an exit signal on a passage edge. Legacy
  `room=None` mode keeps the T2 clamp behavior so existing
  `tests/test_movement.py` passes.
- **C05 warp helper.** Pure `_warp_position(room, exit_dir, x, y) -> (new_room, nx, ny)`.
  No pygame import. Mirror perpendicular coord, inward offset `PLAYER_SPEED + 1`.
- **C06 integration.** Wires C02 + C03 + C04 + C05 into `run_game_loop`. Adds
  `tests/test_rooms.py` (count, symmetry, connectivity, rendering, transitions)
  and `tests/e2e/adversarial/test_rooms_adversarial.py` (diagonal corner,
  alternating direction, full-graph traversal). Reconciles
  `tests/test_movement.py` clamp tests to target a sealed edge of the fixture
  room.

## Requirement Coverage

All 63 REQs in `requirements-trace.md` map to exactly one component (see
`progress.json::components[].traced_requirements`). Every component traces to
at least one REQ; no REQ is orphaned.

## Shared-Context Files

- `shared-context/PATTERN_REGISTRY.md` — code patterns (data class layout,
  registry, validator signatures, headless-pygame conventions).
- `shared-context/DECISION_LOG.md` — already-resolved decisions inherited
  from elicit, plus any design-stage refinements.
- `shared-context/API_CONTRACT.md` — public functions / signatures /
  module-level names that must remain importable.
- `shared-context/COMPONENT_MAP.md` — quick lookup: component -> files /
  functions touched.
- `shared-context/RISK_REGISTER.md` — risks carried from elicit + design-stage
  additions (e.g. pygame headless pixel sampling).
- `shared-context/feature-overview.md` — short narrative of T3.
- `shared-context/conventions.md` — coding conventions for `adventure.py`.
- `shared-context/integration-points.md` — call sites and integration
  contracts between components.

## Execution Order

C01 -> (C02, C03, C04, C05 in parallel) -> C06.

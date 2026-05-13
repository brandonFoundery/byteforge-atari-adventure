# EPIC-003: Edge transitions + room-aware movement

## Summary

Convert the room-edge clamping behavior into edge-aware transitions. When the
player crosses a passage edge (an edge whose adjacent neighbor exists in the
room registry from EPIC-001), the active room swaps to that neighbor and the
player is warped to the mirrored coordinate on the opposite edge of the new
room, with an inward offset that prevents an immediate re-trigger. Sealed
edges (neighbor is `None`) continue to clamp the player exactly as in T2. The
full graph must be walkable in both directions, re-entry must be
deterministic, and the existing `tests/test_movement.py` wall-clamp tests must
be reconciled against the new semantics.

## Source Success Criterion

> Crossing a passage edge swaps `current_room` and warps the player to the
> opposite edge (mirrored coordinate, inward offset to prevent re-trigger);
> sealed edges still clamp; full graph is walkable; re-entry is
> deterministic; `tests/test_movement.py` wall-clamp tests reconciled.

## Scope

### In scope
- `adventure.py::move_player` — make clamp behavior room-aware. On a sealed
  edge, clamp at `_X_MIN/_X_MAX/_Y_MIN/_Y_MAX` (T2 behavior). On a passage
  edge, signal exit via the crossing direction so the caller can swap rooms.
- `adventure.py::run_game_loop` — after each `move_player` call, if an exit
  signal is returned, look up the neighbor in the registry, swap
  `current_room`, and compute the warp position (mirror perpendicular axis,
  apply inward offset of `PLAYER_SPEED + 1` pixels minimum).
- A pure transition helper (e.g. `_warp_position(room, exit_dir, x, y)`)
  that is unit-testable without pygame, returning the new `(room, x, y)`.
- `tests/test_rooms.py` — extend with transition warp tests (mirror math,
  no-immediate-retrigger, full-graph walkability, deterministic re-entry).
- `tests/test_movement.py` — reconcile wall-clamp tests to target a sealed
  edge of a fixture room (or the world border on a room with all-sealed
  edges) so the T2 invariant is preserved without conflicting with new
  passage semantics.
- New `tests/e2e/adversarial/test_rooms_adversarial.py` — adversarial
  scenarios: rapid edge oscillation, diagonal exit at corners with one
  sealed and one passage edge, full traversal of the registry graph.

### Out of scope
- Visual transition effects (flash, fade, room-name overlay) — the swap is
  silent and instantaneous, matching the Atari Adventure model and the
  resolved decisions in `teachback.md`.
- Persistence of visited-rooms state.
- Any new gameplay objects (items, enemies, doors).
- Changes to `PLAYER_SPEED`, `TARGET_FPS`, or window dimensions.

## Dependencies

- **Depends on EPIC-001** (Room model + registry) — supplies the `Room`
  objects, `neighbors` adjacency, and the validated symmetric/connected
  graph that this epic walks across.
- **Depends on EPIC-002** (Room-aware rendering + active room state) —
  supplies the `current_room` local threaded through `run_game_loop` and
  the `draw_room(active_room)` signature that this epic mutates each
  transition.

## Acceptance Criteria (Epic-level)

- AC-E3-1: Walking past a passage edge replaces the active room with the
  registered neighbor on the same frame as the exit, with no scrolling /
  panning animation.
- AC-E3-2: After a transition, the player's perpendicular coordinate is
  preserved (exit-right at `y=100` → enter-left at `y=100`), clamped to the
  new room's interior bounds.
- AC-E3-3: After a transition, the player's parallel coordinate is set
  inward from the entry edge by at least `PLAYER_SPEED + 1` pixels so that
  one further move in the same direction does NOT re-trigger another
  transition.
- AC-E3-4: Pressing into a sealed edge (where `neighbors[dir] is None`)
  produces the same clamp behavior as T2 — the player stops at
  `_X_MIN / _X_MAX / _Y_MIN / _Y_MAX` and `current_room` does not change.
- AC-E3-5: Every room in the registry is reachable from the starting room
  using only legal arrow-key transitions (validated by a graph-walk test).
- AC-E3-6: Re-entering a previously visited room via the same edge places
  the player at the same warp position as the first entry, given the same
  exit coordinate (deterministic).
- AC-E3-7: All pre-existing T1 tests (`tests/test_adventure.py`) and the
  reconciled T2 tests (`tests/test_movement.py`) pass.
- AC-E3-8: `python adventure.py` launches a playable game where the player
  can traverse the full room graph using arrow keys.

## Open Questions

- None blocking. The understand-v4 diamond resolved:
  - Player warp rule: mirror the perpendicular coordinate + inward offset
    (one-frame debounce via position, not via a state flag).
  - Sealed edges: `neighbors[dir] is None` (no separate `walls` set).
  - `current_room` is a local variable threaded through `run_game_loop`,
    not a module global.

## Traceability

- Risks addressed: "Off-by-one / jitter on transition warp causes immediate
  re-transition" (H severity), "test_wall_clamp_* semantically wrong after
  change" (H likelihood), "Adversarial suites silently fail on transition
  behavior" (M/M), "New module-level state becomes a global → flaky tests"
  (M/M) — all from `impact.md`.
- Location: `adventure.py::move_player` (lines 54-64),
  `adventure.py::run_game_loop` (lines 100-129),
  `tests/test_movement.py` (lines 63-80).

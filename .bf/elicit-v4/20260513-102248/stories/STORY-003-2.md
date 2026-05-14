# STORY-003-2: Pure transition helper — warp player to opposite edge

## Parent

EPIC-003 — Edge transitions + room-aware movement

## User Story

As the game loop, I need a pure helper that, given the current room, an exit
direction, and the player's exit coordinate, returns the new active room and
the warp position on the opposite edge — without touching pygame state — so
I can unit-test the warp math headlessly and keep `run_game_loop` thin.

## Scope

- File: `adventure.py` — add a new pure function, suggested name
  `_warp_position(current_room, exit_dir, x, y) -> tuple[Room, int, int]`.
- No pygame imports inside this helper. No reads from module globals other
  than the boundary constants `_X_MIN / _X_MAX / _Y_MIN / _Y_MAX` and
  `PLAYER_SPEED`.
- The helper trusts that `current_room.neighbors[exit_dir]` is not `None`
  (the caller in STORY-003-3 guarantees this).

## Technical Notes

- Mirror rule (per resolved decision in `teachback.md`):
  - exit `"E"` → new room, new `x = _X_MIN + INWARD_OFFSET`, new `y = y`.
  - exit `"W"` → new room, new `x = _X_MAX - INWARD_OFFSET`, new `y = y`.
  - exit `"N"` → new room, new `y = _Y_MAX - INWARD_OFFSET`, new `x = x`.
  - exit `"S"` → new room, new `y = _Y_MIN + INWARD_OFFSET`, new `x = x`.
- `INWARD_OFFSET` is a new module-level constant set to `PLAYER_SPEED + 1`
  (minimum) so that one further frame of held-direction input does not
  push the player back across the edge it just entered.
- The perpendicular coordinate must additionally be clamped to the new
  room's `[_X_MIN, _X_MAX]` (or `[_Y_MIN, _Y_MAX]`) so a transition near a
  corner cannot drop the player into a wall.

## Acceptance Criteria

- **REQ-037**: `_warp_position(room, "E", x, y)` returns the room stored at
  `room.neighbors["E"]`, with new-`x = _X_MIN + INWARD_OFFSET` and
  new-`y = clamp(y, _Y_MIN, _Y_MAX)`.
- **REQ-038**: Mirror behavior is implemented and tested for all four exit
  directions (`"W"`, `"N"`, `"S"` analogous to REQ-037).
- **REQ-039**: A new module constant `INWARD_OFFSET` exists, equals
  `PLAYER_SPEED + 1`, and is used by `_warp_position` for the parallel
  axis on every transition.
- **REQ-040**: Calling `_warp_position` twice with identical arguments
  returns identical `(room, x, y)` tuples — the helper is deterministic
  and has no hidden state.
- **REQ-041**: The perpendicular coordinate after a warp is clamped into
  the new room's interior; the unit test asserts that warping at
  `y = _Y_MIN - 1` returns `y = _Y_MIN` in the new room.
- **REQ-042**: The helper has no `import pygame` and no module-global
  writes; it is callable from a unit test without `SDL_VIDEODRIVER=dummy`.

## Out of Scope

- Wiring the helper into `run_game_loop` (STORY-003-3).
- Detecting the exit in the first place (STORY-003-1).

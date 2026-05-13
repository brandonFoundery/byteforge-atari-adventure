# C05 — TransitionWarpHelper

**Type:** backend-service
**Epic:** EPIC-003
**Stories:** STORY-003-2
**Dependencies:** C01

## Traced requirements

REQ-037, REQ-038, REQ-039, REQ-040, REQ-041, REQ-042

## Goal

Pure helper `_warp_position(room, exit_dir, x, y) -> (new_room, new_x, new_y)` that computes the player's position in the neighboring room after a passage-edge crossing.

## Constraints

- `_warp_position(room, "E", x, y)` returns east neighbor with `x = _X_MIN + INWARD_OFFSET`, clamped `y` (REQ-037).
- Mirror behavior implemented and tested for `"W"`, `"N"`, `"S"` (REQ-038).
- Module constant `INWARD_OFFSET = PLAYER_SPEED + 1` exists and is used by `_warp_position` (REQ-039).
- Deterministic: identical args -> identical return tuple; no hidden state (REQ-040).
- Perpendicular coordinate after warp is clamped into the new room's interior (e.g. `y = _Y_MIN - 1` -> `y = _Y_MIN`) (REQ-041).
- No `import pygame`; no module-global writes; callable without `SDL_VIDEODRIVER=dummy` (REQ-042).

## Public contract

- Input: `room: Room`, `exit_dir: str ("N"|"S"|"E"|"W")`, `x: int`, `y: int`.
- Output: `(new_room: Room, new_x: int, new_y: int)`.
- Side effects: none.

## Out of scope

Loop wiring (C06); tests verifying full transition flow (C06).

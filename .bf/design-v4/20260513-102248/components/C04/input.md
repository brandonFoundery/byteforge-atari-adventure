# C04 — RoomAwareMovement

**Type:** backend-service
**Epic:** EPIC-003
**Stories:** STORY-003-1
**Dependencies:** C01

## Traced requirements

REQ-031, REQ-032, REQ-033, REQ-034, REQ-035, REQ-036

## Goal

Convert `move_player` to room-aware. Accept an optional `room` parameter (default `None` keeps legacy T2 clamp behavior). With a `room`, clamp on sealed edges and return an exit signal on passage edges.

## Constraints

- New signature: `move_player(x, y, keys_pressed, room=None)`.
- With `room` provided, uses `room.neighbors` to decide clamp vs. exit per edge (REQ-031).
- East passage: `x > _X_MAX` AND `neighbors["E"]` is not None -> returns `("exit", "E")` without clamping x (REQ-032).
- East sealed: `x > _X_MAX` AND `neighbors["E"] is None` -> clamps to `_X_MAX`, no exit (REQ-033).
- Symmetric behavior implemented for W / N / S (REQ-034).
- Diagonal cross resolves at most one transition per frame; horizontal axis wins ties (REQ-035) — documented in docstring.
- Existing `tests/test_movement.py` calls (room=None mode) continue to pass (REQ-036).

## Public contract

- Return shape: `tuple[int, int]` (clamped position) OR `tuple[str, str]` where the first element is the literal `"exit"` and the second is the cardinal direction `"N"|"S"|"E"|"W"`.

## Out of scope

The warp helper (C05) and the loop's transition handler (C06). Wall-clamp test reconciliation lives in C06.

# STORY-003-1: Detect edge exit in `move_player` and return a crossing signal

## Parent

EPIC-003 — Edge transitions + room-aware movement

## User Story

As the game loop, I need `move_player` to tell me when the player has crossed
a room edge (and in which direction), so I can decide whether to clamp
(sealed edge) or hand off to the transition handler (passage edge).

## Scope

- File: `adventure.py::move_player` (lines 54-64 today).
- Change the signature to accept the active `Room` (from EPIC-001) so the
  function can read `room.neighbors` and distinguish sealed from passage
  edges per call.
- Return either the new clamped `(x, y)` (no crossing) or `(x, y, exit_dir)`
  where `exit_dir` is one of `"N" | "S" | "E" | "W"`.

## Technical Notes

- A sealed edge is `room.neighbors[dir] is None`; a passage edge is any
  other value (a `Room` reference).
- On a sealed edge, clamp at `_X_MIN / _X_MAX / _Y_MIN / _Y_MAX` exactly as
  T2 did — do not change the boundary constants.
- On a passage edge, do NOT clamp; let the post-clamp coordinate fall
  outside the bounds so the loop can compute the warp.
- Pure function — no pygame side effects, no global mutation. Takes the
  candidate `(x, y)` after speed applied and returns the resolved tuple.
- Recommended return shape: a small dataclass or `(x, y, exit_dir | None)`
  to keep the call site simple. Pick whichever matches the codebase style
  established in EPIC-001/002 and document the choice in a docstring.

## Acceptance Criteria

- **REQ-031**: `move_player` accepts a `room` parameter referencing the
  active `Room` and uses `room.neighbors` to decide clamp vs. exit per
  edge.
- **REQ-032**: When the player's post-speed `x` exceeds `_X_MAX` and
  `room.neighbors["E"]` is a `Room`, `move_player` returns `exit_dir="E"`
  and does NOT clamp `x`.
- **REQ-033**: When the player's post-speed `x` exceeds `_X_MAX` and
  `room.neighbors["E"] is None`, `move_player` clamps `x` to `_X_MAX` and
  returns `exit_dir=None` (T2 behavior).
- **REQ-034**: Symmetric clamp/exit behavior is implemented for the three
  remaining edges: west (`x < _X_MIN`), north (`y < _Y_MIN`), south
  (`y > _Y_MAX`).
- **REQ-035**: When the player moves diagonally and crosses two edges in
  the same frame, `move_player` resolves at most one transition per frame
  using a deterministic priority order documented in the docstring
  (recommended: horizontal axis wins ties; flag the other axis as clamped
  in that frame).
- **REQ-036**: Existing `tests/test_movement.py` calls pass either via a
  default `room=None` legacy mode that preserves T2 clamp behavior, or via
  a same-commit test update that threads a fixture room with all four
  edges sealed — the choice is recorded in the docstring and reflected in
  the test fixture.

## Out of Scope

- The actual room swap and warp computation (STORY-003-2).
- Modifying `run_game_loop` to consume the new return shape (STORY-003-3).

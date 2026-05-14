# STORY-003-4: Reconcile `tests/test_movement.py` wall-clamp tests

## Parent

EPIC-003 — Edge transitions + room-aware movement

## User Story

As the maintainer of the T2 test suite, I need the existing wall-clamp tests
to continue protecting the clamp invariant under the new room-aware
`move_player` signature, so EPIC-003 cannot silently regress T2 by turning a
clamped edge into a passage edge.

## Scope

- File: `tests/test_movement.py` (lines 63-80 today contain
  `test_wall_clamp_left`, `_right`, `_top`, `_bottom`).
- Each clamp test must call the new `move_player` with a fixture room
  whose corresponding edge is sealed (`neighbors[dir] is None`). The
  recommended approach is a module-level fixture room (e.g.
  `_SEALED_ROOM`) with all four neighbors set to `None`, used by all
  four clamp tests.
- Tests that asserted clamping must continue to assert clamping; they must
  not be deleted or weakened.

## Technical Notes

- Do not introduce a real entry in the production room registry just for
  testing — construct the fixture inside the test module so it is
  isolated from the live world.
- If STORY-003-1 chose the `room=None → legacy clamp` back-compat path,
  the tests may pass without modification — but they should still be
  updated to pass an explicit `_SEALED_ROOM` so the test documents the
  invariant under the new semantics.

## Acceptance Criteria

- **REQ-048**: A module-level fixture room with all four edges sealed
  exists in `tests/test_movement.py` and is used by every wall-clamp test.
- **REQ-049**: `test_wall_clamp_left` asserts that pressing left at
  `x = _X_MIN` results in `x == _X_MIN` after `move_player` (T2 invariant
  preserved).
- **REQ-050**: The remaining three wall-clamp tests (`_right`, `_top`,
  `_bottom`) are updated analogously and continue to assert the original
  T2 boundary values.
- **REQ-051**: No new test in `tests/test_movement.py` asserts a
  transition — transition behavior lives in `tests/test_rooms.py`
  (STORY-003-5).
- **REQ-052**: Running `pytest tests/test_movement.py` exits 0 with all
  four clamp tests passing under the new `move_player` signature.

## Out of Scope

- New transition-focused tests (STORY-003-5).
- Adversarial scenarios (STORY-003-6).

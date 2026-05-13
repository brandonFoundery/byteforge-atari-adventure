# STORY-003-5: Add `tests/test_rooms.py` transition coverage

## Parent

EPIC-003 — Edge transitions + room-aware movement

## User Story

As the maintainer, I need unit-level coverage of the transition mechanics —
mirror math, inward offset, no-immediate-retrigger, full-graph walkability,
and deterministic re-entry — so the epic's success criteria are protected
by automated tests that run headlessly.

## Scope

- File: `tests/test_rooms.py` (created in EPIC-001; this story extends it
  with transition tests). If EPIC-001 has not landed the file yet, this
  story creates it.
- Tests rely only on `move_player`, `_warp_position`, and the production
  room registry from EPIC-001. No new pygame initialization required for
  `_warp_position` tests; `move_player` tests use `SDL_VIDEODRIVER=dummy`
  via the existing `conftest.py`.

## Technical Notes

- Use the production registry where possible (validates the real world
  graph). Use small ad-hoc fixture rooms only when targeting a specific
  edge configuration that the production registry happens not to expose.
- The "full graph walkability" test should perform a BFS over the
  registry by simulating: for each room, for each direction with a
  non-`None` neighbor, call `_warp_position` and confirm we land in the
  expected neighbor.

## Acceptance Criteria

- **REQ-053**: A test verifies that exiting east from a sample passage
  edge results in the player's new `x == _X_MIN + INWARD_OFFSET` and
  `current_room` equals the eastern neighbor.
- **REQ-054**: Analogous tests exist for the three remaining directions
  (west, north, south) — each asserts mirror math, inward offset, and
  correct neighbor selection.
- **REQ-055**: A `test_no_immediate_re_transition` confirms that after a
  warp east, one additional `move_player` call with the east key held does
  NOT return an `exit_dir`, because `INWARD_OFFSET` placed the player
  inside the new room beyond the speed reach of the entry edge.
- **REQ-056**: A `test_full_graph_walkable_from_start` performs a BFS
  starting at the start room and confirms every room in the registry is
  reachable via `_warp_position` traversal alone.
- **REQ-057**: A `test_re_entry_is_deterministic` calls `_warp_position`
  twice with identical inputs (exit room, direction, x, y) and asserts
  the returned tuple is equal on both calls.
- **REQ-058**: A `test_sealed_edge_does_not_transition` confirms that on
  a sealed edge, `move_player` returns `exit_dir=None` and `current_room`
  is unchanged for any input held against that edge.

## Out of Scope

- Adversarial / E2E scenarios (STORY-003-6).
- Color rendering verification per room (EPIC-002).

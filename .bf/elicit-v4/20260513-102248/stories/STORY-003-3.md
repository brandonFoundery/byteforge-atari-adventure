# STORY-003-3: Wire transitions into the game loop

## Parent

EPIC-003 — Edge transitions + room-aware movement

## User Story

As a player, when I walk off a passage edge of the current room I want the
screen to instantly become the adjacent room with my character on the
opposite edge, so the world feels connected without scrolling.

## Scope

- File: `adventure.py::run_game_loop` (lines 100-129 today, post EPIC-002
  changes).
- Consume the new `move_player` return shape from STORY-003-1: when
  `exit_dir is None`, behave as today. When `exit_dir` is a direction
  string, call `_warp_position` from STORY-003-2 and rebind `current_room`,
  `px`, `py` in-place for the same frame.
- Pass the (possibly new) `current_room` to `draw_room` later in the same
  frame so the player never sees a frame of "wrong room with new
  coordinates".

## Technical Notes

- `current_room` remains a local variable inside `run_game_loop` (per the
  resolved decision recorded in `teachback.md`). No module-level global.
- Order of operations per frame:
  1. Drain events.
  2. `result = move_player(px, py, keys, current_room)`.
  3. If `result.exit_dir is None`: `px, py = result.x, result.y`.
  4. Else: `current_room, px, py = _warp_position(current_room,
     result.exit_dir, result.x, result.y)`.
  5. `draw_room(logical_surface, current_room)`.
  6. `draw_player(logical_surface, px, py)`.
  7. Blit / flip / tick.

## Acceptance Criteria

- **REQ-043**: `run_game_loop` initializes `current_room` to the
  registry's designated start room and uses that room on the first frame's
  `draw_room` and `move_player` calls.
- **REQ-044**: When `move_player` returns an `exit_dir`, the loop calls
  `_warp_position` and reassigns `current_room`, `px`, `py` before
  `draw_room` is invoked on that frame.
- **REQ-045**: The rendered frame after a transition shows the new room's
  `bg_color` and the player at the warped position — verified by a
  headless test that drives `run_game_loop` for a fixed frame count with
  a stub `event_getter` and a key-state stub holding "right", then samples
  the framebuffer via `pygame.Surface.get_at()`.
- **REQ-046**: When `move_player` returns no `exit_dir`, `current_room` is
  unchanged for that frame — verified by a headless test holding a
  direction toward a sealed edge.
- **REQ-047**: `current_room` is a function-local variable inside
  `run_game_loop`, not a module attribute — verified by a test that
  imports `adventure` and asserts `not hasattr(adventure, "current_room")`
  after a loop run.

## Out of Scope

- Modifying `draw_room` itself (EPIC-002).
- Adding a transition flash, sound, or label (out of scope per intent.md).

# STORY-002-1: Generalize `draw_room` to render active room's color and sealed-edge walls

## Parent Epic
EPIC-002 — Room-aware rendering + active room state

## User Story
As the game's render layer, I need `draw_room` to render whichever Room is
currently active — using that Room's `bg_color` for the background and drawing
wall rectangles only on the Room's sealed edges — so that the screen can
visually reflect the multi-room world introduced in EPIC-001.

## Context
Today `adventure.py::draw_room` (lines 77-92) fills the entire screen with the
module constant `ROOM_COLOR = (240, 208, 64)` and unconditionally draws four
wall rectangles (top, bottom, left, right) using `WALL_COLOR` and
`WALL_THICKNESS`. After this story, the function accepts a Room object and:
- fills the background with `room.bg_color`;
- for each direction in {N, S, E, W}, draws a wall rectangle only when
  `room.neighbors[direction]` is `None` (sealed edge).

The Room schema (attribute names, neighbors map shape, sealed-edge sentinel)
comes from EPIC-001's registry. This story consumes that schema verbatim.

## Touch Surface (from location.md)
- `adventure.py::draw_room` (lines 77-92) — generalize.
- `adventure.py::WALL_THICKNESS`, `adventure.py::WALL_COLOR` — still used; no
  rename.
- `adventure.py::ROOM_COLOR` — preserved as module-level back-compat alias
  (do NOT delete; out-of-tree consumers may import it).

## Acceptance Criteria

- **REQ-021**: `draw_room` accepts a `room` argument (a Room object from
  EPIC-001's registry) in addition to its existing `surface` argument, and
  fills the play area background with the color exposed by `room.bg_color`
  (replacing the hard-coded `ROOM_COLOR` fill). The module-level `ROOM_COLOR`
  constant is preserved as a back-compat alias so external imports do not
  break.
- **REQ-022**: For each cardinal direction in {N, S, E, W}, `draw_room`
  renders a wall rectangle using the existing `WALL_COLOR` and
  `WALL_THICKNESS` constants if and only if `room.neighbors[direction] is
  None` (sealed edge). When the neighbor is a Room reference (passage edge),
  no wall is drawn on that edge and the `bg_color` fill reaches the screen
  border. N/S walls span the full `LOGICAL_WIDTH`; E/W walls span the full
  `LOGICAL_HEIGHT`. This story does NOT introduce per-room wall colors.
- **REQ-023**: A new unit test in `tests/test_rooms.py`
  (`test_draw_room_uses_active_room_color`) constructs a Room with a known
  `bg_color`, calls `draw_room(surface, room)`, and asserts via
  `surface.get_at((x, y))` at an interior pixel that the rendered color
  matches `room.bg_color` exactly (RGB).
- **REQ-024**: A new unit test
  (`test_draw_room_omits_wall_on_passage_edge`) constructs a Room whose
  `neighbors["E"]` points to another Room (passage) and whose other three
  edges are sealed; calls `draw_room`; asserts via `surface.get_at()` that a
  pixel one pixel inside the right edge has the room's `bg_color` (NOT
  `WALL_COLOR`), while a pixel one pixel inside the top edge has
  `WALL_COLOR`.

## Non-Goals
- Do not modify `move_player`. Edges still clamp because of T2 logic; this
  story only changes what is *drawn*, not how movement responds to edges.
- Do not introduce a transition or a "current room" parameter to other
  functions yet (STORY-002-2 owns the `run_game_loop` integration).
- No animation or fade between rooms.

## Verification
- `pytest tests/test_rooms.py -k draw_room` passes.
- `pytest tests/test_adventure.py tests/test_movement.py` continues to pass
  (no regression).
- Manual: `python adventure.py` shows the starting room's `bg_color` as the
  background; sealed edges show walls, passage edges show no wall.

## Open Questions
- None. (Schema deferred to whatever EPIC-001 produced.)

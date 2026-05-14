# C03 — RoomAwareRendering

**Type:** frontend-component
**Epic:** EPIC-002
**Stories:** STORY-002-1, STORY-002-2, STORY-002-3
**Dependencies:** C01

## Traced requirements

REQ-021, REQ-022, REQ-023, REQ-024, REQ-025, REQ-026, REQ-027, REQ-028, REQ-029, REQ-030

## Goal

Generalize `draw_room(surface)` to `draw_room(surface, room)`. Render `room.bg_color` background and walls only on sealed edges. Thread `current_room` as a function-local in `run_game_loop` (never module-global).

## Constraints

- `draw_room(surface, room)`: fills with `room.bg_color`; preserves `ROOM_COLOR` alias (REQ-021).
- Draws walls only on edges where `neighbors[dir] is None`; passage edges show no wall (REQ-022).
- `run_game_loop` declares function-local `current_room = ROOMS[START_ROOM]` and passes it to `draw_room` each frame (REQ-025).
- `current_room` is local only; `hasattr(adventure, "current_room")` is False; no cross-invocation leak (REQ-026, REQ-030).
- Tests in `tests/test_rooms.py`:
  - `test_draw_room_uses_active_room_color` (REQ-023) — center-pixel sample equals `room.bg_color`.
  - `test_draw_room_omits_wall_on_passage_edge` (REQ-024) — passage edge shows bg, sealed shows wall.
  - `test_run_game_loop_uses_start_room_for_initial_frame` (REQ-027).
  - `test_rendered_frame_matches_start_room_bg_color` (REQ-028) — documented fallback if `get_at` headless fails.
  - `test_rendered_frame_shows_walls_only_on_sealed_edges_of_start_room` (REQ-029).
  - `test_no_module_global_current_room` (REQ-030).

## Out of scope

Transition logic (C04, C05), full integration test wiring (C06). Passage edges still clamp via the existing `move_player` until C04+C06 land — visually still single-room at the loop level for this component's intermediate state.

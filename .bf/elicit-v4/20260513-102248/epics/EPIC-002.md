# EPIC-002: Room-aware rendering + active room state

## Summary
Generalize the render and frame-loop layer so that the game draws a specific Room
(the active room) each frame instead of the hard-coded single screen. After this
epic, `draw_room` accepts a Room and renders that room's `bg_color`, drawing wall
rectangles only on the room's sealed edges; `run_game_loop` carries
`current_room` as a function-local (no module global); and the rendered frame
always reflects whichever Room is active.

This is the second of three epics in T3 (multi-room world + screen transitions).
It builds on EPIC-001 (Room model + registry) by *consuming* the registry — no
edge-crossing or transition logic is introduced yet (that lives in EPIC-003).
The output of EPIC-002 is a game that visibly renders the registry's starting
room (its color, its sealed walls) but still clamps at every edge exactly like
T2 did.

## Success Criterion (from understand-v4)
`draw_room` renders the active room's `bg_color` and renders walls only on
sealed edges; `run_game_loop` threads `current_room` as a local (no module
global); rendered frame reflects the active room.

## Scope (from location.md)

### In scope
- `adventure.py::draw_room` (lines 77-92) — generalize signature to accept an
  active room; replace hard-coded `ROOM_COLOR` fill with `room.bg_color`;
  replace unconditional four-wall draw with per-edge logic that renders a wall
  rectangle only when `room.neighbors[dir] is None`.
- `adventure.py::run_game_loop` (lines 100-129) — introduce a function-local
  `current_room` initialized from the registry's designated `START_ROOM`; pass
  it to `draw_room`. No module global, no class attribute.
- `adventure.py` module constants (lines 7-26) — `ROOM_COLOR` remains as a
  back-compat alias (set to the starting room's color, or left as the existing
  yellow) so out-of-tree imports do not break.
- `tests/test_rooms.py` — extend with rendering tests that drive one frame of
  the loop and sample pixels via `pygame.Surface.get_at()` to verify the active
  room's color and its sealed-wall layout.

### Out of scope (deferred to EPIC-003)
- Edge-crossing detection in `move_player`.
- Active-room mutation / room swapping during the loop.
- Player warp-to-opposite-edge logic.
- `tests/test_movement.py` wall-clamp reconciliation (still clamps everywhere
  in EPIC-002 because `move_player` is unchanged).

### Out of scope (deferred to later tickets entirely)
- Audio, animation, in-room objects, HUD, mini-map.
- Scrolling / camera follow.
- New pygame dependencies.

## Acceptance Criteria
This epic is complete when all of its child stories' REQ items pass and the
following epic-level invariants hold:

1. Running `python adventure.py` launches and renders the *starting room's*
   `bg_color` as the screen background (no longer the hard-coded yellow unless
   the starting room is yellow by design).
2. Walls are drawn only on edges where the starting room has no neighbor;
   edges that point to a neighboring room have NO wall pixels drawn (the play
   area visibly extends to the screen border on those edges).
3. The game continues to run at 60 FPS with no console errors.
4. All existing T1 / T2 tests (`tests/test_adventure.py`,
   `tests/test_movement.py`) continue to pass without modification. (Movement
   still clamps everywhere because `move_player` is unchanged in this epic.)
5. `grep` for `current_room` in `adventure.py` shows zero occurrences at module
   scope (no module global); occurrences exist only inside `run_game_loop` and
   any helper it explicitly passes the room to.

## Dependencies
- **Depends on:** EPIC-001 (Room model + registry must exist and expose a
  `START_ROOM` and per-room `bg_color` + `neighbors` map).
- **Blocks:** EPIC-003 (transitions need a room-aware render and a threaded
  `current_room` state to mutate).

## Risks (carried from impact.md)

| Risk | Mitigation |
|------|------------|
| `ROOM_COLOR` constant removed/renamed | Keep as back-compat alias on module scope. |
| `draw_room` signature change cascades | Only one caller (`run_game_loop` line 121); update atomically in same commit. |
| Module-global `current_room` causes test flake | Story STORY-002-2 explicitly requires function-local state. Reviewer must verify no module-level binding. |
| Headless `get_at()` can't read pixel color | Story STORY-002-3 verifies `get_at()` works under `SDL_VIDEODRIVER=dummy` before relying on it; falls back to asserting the Room object's `bg_color` if pixel sampling is unreliable. |
| Sealed-edge representation differs from EPIC-001's choice | This epic must consume *whatever* representation EPIC-001 chose (`neighbors[dir] is None` per impact.md). Story STORY-002-1 reads the representation from the Room object — does not invent a new one. |

## Open Questions
- None blocking. EPIC-001 will pin the exact `Room` schema; this epic adapts to
  whatever EPIC-001 produces (color attribute, neighbors map, sealed-edge
  convention).

## Stories
- STORY-002-1 — Generalize `draw_room` to render active room's color and sealed-edge walls
- STORY-002-2 — Thread `current_room` as a function-local through `run_game_loop`
- STORY-002-3 — Verify rendered frame reflects the active room (pixel-level test)

# MOCK-003-transition: Edge crossing — instant whole-screen swap

## Purpose

Document the visible behavior of a passage-edge crossing so a screenshot
reviewer can verify EPIC-003 by eye. There is no new UI chrome — the
"mock" is a description of three sequential frames.

## Frame sequence

### Frame N-1 — about to exit
- Player (red 8x8 square) is one `PLAYER_SPEED` step away from the east
  wall of the current room.
- Background = current room's `bg_color` (e.g., yellow for the start
  "Yellow Castle" room, per EPIC-001 palette).
- Perimeter wall on the east side is visible if and only if the east
  edge is sealed. On a passage edge, the wall band is absent (the
  background color extends fully to the edge) — this matches the
  resolved decision that sealed-edge rendering comes from
  `room.neighbors[dir] is None`.

### Frame N — crossing (single frame, no animation)
- Player input pushed the player past `_X_MAX`.
- `move_player` returns `exit_dir="E"`; the loop calls
  `_warp_position`, which returns `(neighbor_room, _X_MIN +
  INWARD_OFFSET, y)`.
- `draw_room` is invoked with the new `neighbor_room` BEFORE
  `pygame.display.flip()` — the player never sees a half-rendered
  frame.

### Frame N+1 — landed
- Background = neighbor room's `bg_color` (e.g., blue).
- Player (red 8x8) is positioned `INWARD_OFFSET = PLAYER_SPEED + 1`
  pixels east of `_X_MIN` and at the same `y` as Frame N-1 (clamped
  to the new room's interior if near a corner).
- East-wall band visible / absent in the new room according to
  `neighbor_room.neighbors["W"]` — by symmetry this neighbor exists
  (we just came from it), so the WEST band of the new room is
  passage-open and the background extends to `x = 0`.

## Negative case — sealed edge

If the player presses east at a sealed edge, frames N-1, N, N+1 all
show the same background color. The player's `x` stays clamped at
`_X_MAX` and the east-wall band remains drawn — visually identical to
T2 behavior.

## Verification by screenshot

1. `python adventure.py`, walk east until transition.
2. Capture screenshot before and after transition.
3. Confirm:
   - Background color differs between the two screenshots.
   - Player y-coordinate is unchanged.
   - Player x-coordinate is small (near `_X_MIN`) in the post-transition
     screenshot, not large (near `_X_MAX`).
   - No "in-between" frame containing both rooms.

## Non-goals (explicitly NOT drawn)

- No fade or pan animation.
- No transition flash / strobe.
- No room-name label or HUD overlay.
- No mini-map.

Per `intent.md` non-goals and `teachback.md` constraints, the swap is
silent and instantaneous.

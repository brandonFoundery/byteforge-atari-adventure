# MOCK-EPIC-002: Room render — sealed walls vs. passage edges

## Purpose
Visual description of what `draw_room` produces *after* EPIC-002, for the
starting room. Illustrates two key visible differences from T2:
1. Background color is the *starting room's* `bg_color` (from EPIC-001),
   not the hard-coded `ROOM_COLOR = (240, 208, 64)`.
2. Wall rectangles are drawn only on sealed edges. Passage edges (where
   the room has a neighbor) have NO wall — the background extends to
   the screen edge.

There is still NO transition behavior in EPIC-002. The player still
clamps at every edge (passage or sealed) because `move_player` is
unchanged in this epic. EPIC-003 will make passage edges trigger
transitions.

## Reference Pattern
- Existing T1/T2 single-room render in `adventure.py::draw_room`
  (lines 77-92) — uniform yellow `ROOM_COLOR` with four black walls,
  player rendered as a colored square.
- Atari Adventure (1980) screen-warp model — single-screen rooms,
  whole-screen swap on edge cross.

## ASCII Mockup — Starting Room (assume neighbors: N=None, E=Room2, S=None, W=None)

```
+========================================+    <- top edge, SEALED -> wall drawn
||                                      ||
||                                      ||
||                                      ||
||                                      ||
||                                      ||
||                                      ||
||              [P]                      <- right edge, PASSAGE -> NO wall
||                                      ||
||                                      ||      background reaches the
||                                      ||      right screen border
||                                      ||
||                                      ||
||                                      ||
+========================================+    <- bottom edge, SEALED -> wall drawn
 ^                                              ^
 left edge SEALED -> wall drawn                 right edge has NO wall
```

Legend:
- `=` and `||` = `WALL_COLOR` rectangle of thickness `WALL_THICKNESS`.
- empty interior = `room.bg_color` (from EPIC-001's `START_ROOM`).
- `[P]` = the player square (rendered by the unchanged `draw_player`).
- The right edge in this example has NO `||` characters; the background
  fill extends fully to `LOGICAL_WIDTH - 1`.

## ASCII Mockup — Hypothetical "all sealed" room (e.g., a dead-end room)

```
+========================================+
||                                      ||
||                                      ||
||                                      ||
||                 [P]                  ||
||                                      ||
||                                      ||
||                                      ||
+========================================+
```

This matches the T2 visual exactly except for the background color,
which would now be that room's `bg_color`.

## ASCII Mockup — Hypothetical "all open" room (4 passages)

```
+                                        +
                                          
                                          
                                          
                                          
                                          
                       [P]                
                                          
                                          
                                          
                                          
                                          
+                                        +
```

No wall rectangles are drawn on any edge. Only the corner-marker `+`
glyphs are shown here to bound the diagram; in the actual render there
are NO pixels at the corners either (since both adjacent edges are
passages). Player still clamps at every edge in EPIC-002 because
`move_player` is unchanged.

## Pixel-Sampling Targets (for tests)

The integration tests in STORY-002-3 sample these coordinates:

| Test pixel | Coordinate | Expected color (start room) |
|------------|------------|------------------------------|
| Interior center | `(LOGICAL_WIDTH // 2, LOGICAL_HEIGHT // 2)` | `START_ROOM.bg_color` |
| Just inside top edge | `(LOGICAL_WIDTH // 2, WALL_THICKNESS - 1)` | `WALL_COLOR` if N sealed else `START_ROOM.bg_color` |
| Just inside bottom edge | `(LOGICAL_WIDTH // 2, LOGICAL_HEIGHT - WALL_THICKNESS)` | `WALL_COLOR` if S sealed else `START_ROOM.bg_color` |
| Just inside left edge | `(WALL_THICKNESS - 1, LOGICAL_HEIGHT // 2)` | `WALL_COLOR` if W sealed else `START_ROOM.bg_color` |
| Just inside right edge | `(LOGICAL_WIDTH - WALL_THICKNESS, LOGICAL_HEIGHT // 2)` | `WALL_COLOR` if E sealed else `START_ROOM.bg_color` |

## Not Shown / Out of Scope
- Transition flash, fade, or animation between rooms (no transition in
  EPIC-002).
- Mini-map, HUD, or room name overlay (out of T3 entirely).
- Per-room wall color, interior obstacles, decorative motifs (T3
  uses a uniform `WALL_COLOR` and empty interiors).

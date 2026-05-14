# STORY-001-1: Add `Room` data structure, `ROOMS` registry, and `START_ROOM`

## Parent Epic
EPIC-001 — Room model + registry (foundation, no behavior change)

## User Value
As the game runtime, I need a typed, in-memory description of every room in
the world (id, background color, four cardinal neighbors) and a designated
spawn room, so that later epics can render the active room and transition
between rooms without re-deriving the world layout each frame.

## Scope
**Touch:** `adventure.py` (additive — NEW symbols only; existing functions
unchanged in this story).

**Do NOT touch:** `draw_room`, `move_player`, `run_game_loop`, any existing
constant in lines 7–26 except aliasing.

## Design Notes
- Use a `dataclass(frozen=True)` named `Room` with fields:
  - `id: str`
  - `bg_color: tuple[int, int, int]`
  - `neighbors: dict[str, str | None]` — keys are exactly `"N"`, `"S"`,
    `"E"`, `"W"`. A value of `None` denotes a sealed wall.
- `ROOMS: dict[str, Room]` — module-level registry mapping room id → Room.
- `START_ROOM: str = "yellow"` — module-level constant.
- Retain `ROOM_COLOR = (240, 208, 64)` and use that exact tuple as the
  `bg_color` of the `"yellow"` room. Keep the constant declaration so
  legacy imports still resolve.

### Authored 2×2 map (4 rooms)
```
+--------+--------+
| yellow | blue   |   (top row)
+--------+--------+
| green  | purple |   (bottom row)
+--------+--------+
```

Concrete colors (pairwise distinct, visually identifiable in a screenshot):
- `yellow`  → `(240, 208, 64)`   — legacy `ROOM_COLOR`
- `blue`    → `(64, 96, 200)`
- `green`   → `(48, 160, 64)`
- `purple`  → `(144, 64, 176)`

Adjacency:
- `yellow.E = "blue"`,    `yellow.S = "green"`,  `yellow.N = None`, `yellow.W = None`
- `blue.W   = "yellow"`,  `blue.S   = "purple"`, `blue.N   = None`, `blue.E   = None`
- `green.E  = "purple"`,  `green.N  = "yellow"`, `green.S  = None`, `green.W  = None`
- `purple.W = "green"`,   `purple.N = "blue"`,   `purple.S = None`, `purple.E = None`

This graph is connected (all four rooms reachable from `yellow`) and every
edge is symmetric.

## Acceptance Criteria
- **REQ-001**: `adventure.py` exposes a public `Room` class (or dataclass)
  with attributes `id`, `bg_color`, and `neighbors`, importable as
  `from adventure import Room`.
- **REQ-002**: `adventure.py` exposes a module-level `ROOMS` mapping of
  `room_id -> Room` containing exactly 4 entries with ids `"yellow"`,
  `"blue"`, `"green"`, `"purple"`.
- **REQ-003**: Each entry in `ROOMS` has `bg_color` equal to the palette
  specified above, and all four `bg_color` values are pairwise distinct.
- **REQ-004**: Each `Room.neighbors` dict has exactly the four keys
  `"N"`, `"S"`, `"E"`, `"W"` present; values are either another existing
  room id (string) or `None`.
- **REQ-005**: The adjacency map matches the 2×2 layout documented above
  (yellow–blue–green–purple cycle of the grid).
- **REQ-006**: `adventure.py` exposes `START_ROOM = "yellow"` and
  `ROOMS[START_ROOM].bg_color == (240, 208, 64)`.
- **REQ-007**: The module-level constant `ROOM_COLOR` still exists with
  value `(240, 208, 64)` so legacy imports continue to resolve.
- **REQ-008**: `tests/test_adventure.py` and `tests/test_movement.py` pass
  unmodified after this story's changes.

## Out of Scope
- Validators (STORY-001-2).
- Tests (STORY-001-3).
- Any consumer of `ROOMS` (EPIC-002+).

## Dependencies
- None. First story in the epic.

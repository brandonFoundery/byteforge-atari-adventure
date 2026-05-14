# API Contract — `adventure.py` public surface (post-T3)

## Must remain importable (back-compat)

- `ROOM_COLOR: tuple[int, int, int] = (240, 208, 64)`
- `WALL_COLOR`, `PLAYER_COLOR`, `PLAYER_SIZE`, `PLAYER_SPEED`
- `LOGICAL_WIDTH`, `LOGICAL_HEIGHT`, `WINDOW_SCALE`, `TARGET_FPS`, `WALL_THICKNESS`
- `PLAYER_X`, `PLAYER_Y`
- `initialize_pygame`, `create_window`, `draw_player`, `run_game_loop`, `main`

## New public surface

| Name | Kind | Signature | Notes |
|------|------|-----------|-------|
| `Room` | class | `Room(id: str, bg_color: tuple[int,int,int], neighbors: dict[str, str|None])` | dataclass |
| `ROOMS` | mapping | `dict[str, Room]` | 4 entries: yellow/blue/green/purple |
| `START_ROOM` | str | `"yellow"` | |
| `INWARD_OFFSET` | int | `PLAYER_SPEED + 1` | used by `_warp_position` |
| `assert_symmetric` | fn | `(rooms: dict[str, Room]) -> None` | raises `ValueError` on asymmetric edge |
| `assert_connected` | fn | `(rooms: dict[str, Room], start: str) -> None` | raises `ValueError` listing unreachable rooms |
| `_warp_position` | fn (private) | `(room: Room, exit_dir: str, x: int, y: int) -> tuple[Room, int, int]` | no pygame import |

## Changed signatures

| Name | Before | After | Compat |
|------|--------|-------|--------|
| `draw_room` | `(surface) -> None` | `(surface, room) -> None` | Hard change; only call site is `run_game_loop` |
| `move_player` | `(x, y, keys_pressed) -> (x, y)` | `(x, y, keys_pressed, room=None) -> (x, y) \| ("exit", dir)` | `room=None` keeps T2 clamp behavior |

## Module-level invariants

- `not hasattr(adventure, "current_room")` — verified by test.
- `ROOMS[START_ROOM].bg_color == ROOM_COLOR == (240, 208, 64)`.
- `len(ROOMS) == 4` (in scope: 4-6 allowed by spec; authored layout is 4).
- All four `bg_color` values pairwise distinct.

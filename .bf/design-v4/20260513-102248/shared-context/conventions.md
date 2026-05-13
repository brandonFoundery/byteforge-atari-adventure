# Conventions

## Module layout (`adventure.py`)

- Keep `from __future__ import annotations` at the top.
- Module-level constants are SCREAMING_SNAKE_CASE.
- Public data class: `Room` (dataclass; `id: str`, `bg_color: tuple[int,int,int]`, `neighbors: dict[str, str | None]`).
- Module registry: `ROOMS: dict[str, Room]`.
- Start room id: `START_ROOM = "yellow"`.
- Legacy alias preserved: `ROOM_COLOR = (240, 208, 64)`.

## Function signatures

- `draw_room(surface, room) -> None` (additive arg; old `(surface)` callers must be updated).
- `move_player(x, y, keys_pressed, room=None) -> tuple[int, int] | tuple[str, str]` — legacy mode `room=None` returns just `(x, y)`; with `room` returns either `(x, y)` or `("exit", direction)`.
- `_warp_position(room, exit_dir, x, y) -> (new_room, new_x, new_y)` — pure, no pygame import.
- `assert_symmetric(rooms) -> None` — raises `ValueError` naming offender.
- `assert_connected(rooms, start) -> None` — raises `ValueError` listing unreachable rooms.

## State rules

- `current_room` is **always** function-local in `run_game_loop`. Never assigned to the module.
- Validators never mutate their `rooms` argument and never read module-level `ROOMS`.
- `_warp_position` is deterministic with no hidden state.

## Tests

- Headless pygame is set up by `tests/conftest.py` via `SDL_VIDEODRIVER=dummy`.
- New tests in `tests/test_rooms.py` import only from `adventure` and `pytest`.
- Adversarial tests in `tests/e2e/adversarial/test_rooms_adversarial.py`.
- Existing `tests/test_movement.py` clamp tests target a sealed edge of the fixture room (NOT the live registry's start room).

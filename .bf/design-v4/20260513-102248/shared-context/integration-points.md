# Integration Points

## Call graph (post-T3)

```
main()
  -> initialize_pygame()
  -> create_window()
  -> run_game_loop(surface)
       |-- (locals: current_room = ROOMS[START_ROOM]; px, py)
       |-- event_getter()
       |-- pygame.key.get_pressed()
       |-- move_player(px, py, keys_pressed, room=current_room)
       |     -> returns (x, y)  OR  ("exit", direction)
       |-- if exit:
       |     _warp_position(current_room, direction, px, py)
       |       -> (new_room, new_x, new_y)
       |     current_room, px, py = ...
       |-- draw_room(logical_surface, current_room)
       |-- draw_player(logical_surface, px, py)
       |-- blit / scale / flip / tick
```

## Component boundaries

| Component | Owns                                   | Consumers                |
|-----------|----------------------------------------|--------------------------|
| C01       | `Room`, `ROOMS`, `START_ROOM`, `ROOM_COLOR` | C02, C03, C04, C05, C06 |
| C02       | `assert_symmetric`, `assert_connected` | C06 (registry construction) |
| C03       | `draw_room(surface, room)`             | C06                      |
| C04       | `move_player(..., room=None)`          | C06                      |
| C05       | `_warp_position`, `INWARD_OFFSET`      | C06                      |
| C06       | `run_game_loop` body + all new tests   | (entry point)            |

## Test integration

- `tests/test_adventure.py` — must remain green (T1 behavior).
- `tests/test_movement.py` — clamp tests retargeted to sealed-edge fixture room (C06).
- `tests/test_rooms.py` — new (C06 owns the file; individual reqs filled across C01-C05).
- `tests/e2e/adversarial/test_rooms_adversarial.py` — new (C06).

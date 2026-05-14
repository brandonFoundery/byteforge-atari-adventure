# Component Map

| Component | Files touched | Symbols owned |
|-----------|---------------|---------------|
| C01 RoomDataModelAndRegistry | `adventure.py` | `Room`, `ROOMS`, `START_ROOM`, `ROOM_COLOR` |
| C02 RegistryValidators | `adventure.py` | `assert_symmetric`, `assert_connected` |
| C03 RoomAwareRendering | `adventure.py` | `draw_room(surface, room)`, threading `current_room` local |
| C04 RoomAwareMovement | `adventure.py` | `move_player(x, y, keys_pressed, room=None)` |
| C05 TransitionWarpHelper | `adventure.py` | `_warp_position`, `INWARD_OFFSET` |
| C06 GameLoopIntegration | `adventure.py` (loop wiring), `tests/test_rooms.py` (new), `tests/test_movement.py` (reconcile), `tests/e2e/adversarial/test_rooms_adversarial.py` (new) | `run_game_loop` body update + test suite |

## DAG

```
        C01
       / | \ \
     C02 C3 C4 C5
       \ | /  /
        C06
```

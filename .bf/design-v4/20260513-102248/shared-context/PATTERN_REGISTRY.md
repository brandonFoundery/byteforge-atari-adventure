# Pattern Registry

| Pattern | Where | Notes |
|---------|-------|-------|
| Dataclass for plain records | `adventure.Room` | `@dataclass(frozen=True)` is acceptable; equality by id ok |
| Module-level registry dict | `adventure.ROOMS` | keyed by string id |
| Module-level constant exports | `adventure.START_ROOM`, `ROOM_COLOR` | uppercase, immutable |
| Pure validators raising `ValueError` | `assert_symmetric`, `assert_connected` | no mutation, message names offender |
| Function-local state in game loop | `run_game_loop` locals (`current_room`, `px`, `py`) | never assign to module |
| Headless pygame in tests | `tests/conftest.py` sets `SDL_VIDEODRIVER=dummy` | inherited from T1 |
| SDL1+SDL2 dual key support | `_is_pressed` | preserved; no change |
| Back-compat optional arg | `move_player(..., room=None)` | legacy callers untouched |

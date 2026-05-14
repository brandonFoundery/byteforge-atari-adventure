# Feature Overview — T3 Multi-Room World + Screen Transitions

Expands the single-screen Atari Adventure homage into a connected world of 4
distinct rooms in a 2x2 grid (yellow / blue / green / purple). Each room
fills the screen with its own bg color. Walking past a passage-edge
instantly swaps the active room and warps the player to the opposite edge
with an inward offset. Sealed edges keep T2 clamp behavior. T1/T2 tests
must continue to pass.

All production work is in `adventure.py`. New tests live under `tests/`.

## Cross-cutting decisions (locked by elicit)

- 4 rooms in a 2x2: yellow (start), blue, green, purple
- bg_colors: yellow (240,208,64), blue (64,96,200), green (48,160,64), purple (144,64,176)
- Sealed edge: `neighbors[dir] is None`
- `current_room` is function-local in `run_game_loop`
- Diagonal ties: horizontal axis wins
- Warp: mirror perpendicular coord, inward offset `PLAYER_SPEED + 1`
- No flash / fade / label on transition (silent swap)

## Source

- Assembled spec: `.bf/elicit-v4/20260513-102248/final/assembled.md`
- Requirements trace: `.bf/elicit-v4/20260513-102248/final/requirements-trace.md`

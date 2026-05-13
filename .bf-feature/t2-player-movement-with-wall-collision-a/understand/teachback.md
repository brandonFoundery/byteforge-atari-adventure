# Teach-back (Proof of Understanding)

feature_witness: b6731a13a9b00140

## Summary
T2 adds player movement to the Atari Adventure homage built in T1. The player
entity responds to the keyboard arrow keys and travels in four cardinal
directions (up, down, left, right). When the player reaches a wall, movement
into that wall is denied so the player cannot pass through or overlap it. The
work is grounded in the single-module pygame game in `adventure.py` and is
verified by a dedicated test module at `tests/test_movement.py`. The T1
regression surface in `tests/test_adventure.py` continues to pass, and
`tests/conftest.py` keeps the headless pygame environment compatible.

## What Changes / What Doesn't
- Changes:
  - `adventure.py` gains the `PLAYER_SPEED` constant, the wall-clamp boundary
    constants `_X_MIN`, `_X_MAX`, `_Y_MIN`, `_Y_MAX`, the
    `move_player(x, y, keys_pressed)` function, and `run_game_loop` integration
    that calls `pygame.key.get_pressed()` each frame and applies the result
    through `move_player` before rendering.
  - `tests/test_movement.py` is added to cover the speed constant, each of the
    four directional axes, the four wall-clamp boundaries, and the
    no-keys-no-motion invariant.
- Does not change:
  - Diagonal movement or eight-direction input.
  - WASD, gamepad, mouse, or touch input bindings.
  - Variable movement speed, acceleration, or inertia tuning beyond a single
    constant speed.
  - Combat, item pickup, doors, or interactions with non-wall objects.
  - Multi-player or AI-controlled entity movement.
  - Level design, new maps, or new wall layouts beyond what T1 provides.
  - Animation frames, sprite swapping, or facing-direction art changes.
  - Sound effects for movement or collision.
  - Visual identity constants (`ROOM_COLOR`, `WALL_COLOR`, `PLAYER_COLOR`),
    `draw_room` room geometry, and `create_window` display surface management —
    all owned by T1.
  - `tests/test_adventure.py` and `tests/conftest.py` are untouched and remain
    in the regression scope.

## Example
- Current (pre-T2): The player sprite renders at its initial position and stays
  there regardless of keyboard input; arrow-key presses have no effect on
  `PLAYER_X` / `PLAYER_Y`.
- Desired (T2): Pressing and holding the right arrow advances the player
  rightward each frame by `PLAYER_SPEED` until the player's right edge meets
  `_X_MAX` (the inner wall boundary derived from `WALL_THICKNESS`,
  `LOGICAL_WIDTH`, and `PLAYER_SIZE`). Further right-arrow input does not change
  the player's position; the player does not overlap the wall.

## Success Criteria
- [ ] Pressing the up, down, left, or right arrow key changes the player position in that direction on screen on the next rendered frame.
- [ ] When the player is adjacent to a wall and an arrow key is pressed toward that wall, the player position does not change and the player does not overlap the wall.
- [ ] Releasing all arrow keys leaves the player stationary for at least one full second with no position change.
- [ ] Pressing two opposing arrow keys (e.g., left and right) does not move the player past a wall in either direction.
- [ ] An automated or scripted test verifies that attempting to move into a wall tile leaves the player coordinates unchanged.

## Constraints / Invariants
- Movement is restricted to four cardinal directions; diagonal motion is not produced.
- Input source is the keyboard arrow keys, read via `pygame.key.get_pressed()` each frame.
- Wall collision is implemented as boundary clamping against `_X_MIN`, `_X_MAX`,
  `_Y_MIN`, `_Y_MAX` — the player position is denied entry into the perimeter
  wall rectangles drawn by `draw_room`, rather than swept-collision against
  arbitrary tiles.
- The work stays inside the `adventure` single-file game module and
  `tests/test_movement.py`; `tests/test_adventure.py` and `tests/conftest.py`
  remain unmodified and must continue to pass under the T2 changes.
- Risk recorded in `impact.yaml` (high severity, behavior): `move_player`
  applies each axis independently and clamps after summing, so pressing
  `K_LEFT` and `K_RIGHT` in the same frame nets zero motion (likewise
  `K_UP`+`K_DOWN`). The behavior is undocumented at the request level; the
  fourth success criterion above pins it down, and the mitigation is to cover
  the simultaneous-opposite-keys case explicitly in `tests/test_movement.py`.

## Blocking Ambiguity Questions (must be empty to proceed)
- What constitutes a "wall" — any non-floor tile, an explicit wall layer, or a collision-flagged object?
- Should diagonal input (two arrow keys pressed simultaneously) be ignored, resolved to one axis, or move on both axes independently?
- Is movement tile-stepped (one tile per key press / per tick) or continuous (pixels per frame while held)?

## Requirement Decisions (resolve before epics/stories/mocks)
- Define the canonical player movement speed (tiles/sec or pixels/frame).
- Decide simultaneous-key resolution policy (last-pressed wins, axis priority, or independent axes).
- Decide whether the player can be spawned inside a wall and, if so, how that is handled.

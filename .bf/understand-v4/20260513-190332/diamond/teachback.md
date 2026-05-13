# Teach-back (Proof of Understanding)

## Summary
We are adding three pickable world items — a chalice, a key, and a sword — to the existing pygame Atari Adventure homage. The player will be able to pick up an item by simply walking into it (touch collision), can carry only one item at a time, and can release the currently carried item by pressing a dedicated drop key. The change lives in the single `adventure.py` module on top of the T1 game-loop/render foundation and T2 movement/wall-collision work, and adds new tests for the item behavior without altering any existing T1/T2 contracts.

## What Changes / What Doesn’t
- Changes:
  - Three new world items (chalice, key, sword) are spawned at distinct positions inside the playfield and visibly rendered every frame, each visually distinguishable from one another and from the player.
  - A new "carry" state tracks at most one item in the player's possession.
  - A new touch-based pickup rule: when the player's sprite overlaps a world item and they are not already carrying, the item leaves the world and becomes the carried item.
  - A new drop action triggered by a dedicated keypress: while carrying, pressing the drop key returns the item to the world at the player's current position and clears the carry slot.
  - A visible indication of which item (if any) is currently being carried.
  - New tests covering pickup, carry-one, drop, and item-position bounds (unit and adversarial).
- Does not change:
  - The existing game loop, frame pacing, window setup, or render foundation from T1.
  - Arrow-key movement or wall-collision clamp behavior from T2 (no change to `move_player`'s signature or return shape).
  - The runtime/engine (still pygame).
  - The existing constants `PLAYER_X/Y`, `PLAYER_SIZE`, `WALL_THICKNESS`, `LOGICAL_WIDTH/HEIGHT`, `_X_MIN/_X_MAX/_Y_MIN/_Y_MAX` (only new constants are added; none are redefined).
  - The ESC-to-quit behavior or the event-loop signature.
  - There is no item use/consume behavior (key does not unlock, sword does not attack, chalice does not score/win), no enemies, no scoring, no multi-room navigation, no audio, and no persistence across restarts.

## Example
- Current: The player moves around a single room with arrow keys and is stopped by the walls. The room contains only the player; there are no items, no inventory, and no drop action.
- Desired: The same room now also contains a chalice, a key, and a sword at fixed starting positions. The player walks into the key and the key disappears from the room while the player is now shown to be carrying the key. The player walks onto the sword while still holding the key — nothing happens, the sword remains visible. The player walks to an open spot, presses the drop key, and the key reappears in the world at the player's position; the carry indicator clears. The player can then walk away and back onto the key to pick it up again.

## Success Criteria
- [ ] Three items — chalice, key, sword — are visible on screen at game start at distinct, non-overlapping positions inside the playfield, each visually distinguishable from one another and from the player.
- [ ] Walking the player into a world item while not carrying anything removes that item from the world and marks the player as carrying it.
- [ ] While carrying an item, walking into another world item does not pick up the second item (the second item remains visible in the world).
- [ ] Pressing the drop key while carrying an item causes that item to reappear in the world at a position associated with the player, and the player is no longer carrying anything.
- [ ] Pressing the drop key while not carrying anything has no effect (no crash, no phantom item spawned).
- [ ] After dropping an item, the player can move off it and back onto it to pick it up again.
- [ ] The currently carried item (if any) is communicated to the player either as a sprite attached to the player or via a HUD indicator.
- [ ] Player movement and wall collision from T1/T2 continue to work unchanged.
- [ ] The game loop continues to run at a stable frame rate with items present (no render or input regressions).
- [ ] All pre-existing tests in `tests/test_adventure.py`, `tests/test_movement.py`, and the two adversarial suites pass unmodified; new item tests under `tests/test_items.py` and `tests/e2e/adversarial/test_items_adversarial.py` are green.

## Constraints / Invariants
- The game loop and render foundation from T1 must not be altered or broken.
- Arrow-key movement and wall-collision clamp from T2 must not be altered or broken; `move_player` keeps its signature and `(x, y)` return shape.
- Implementation remains in pygame, in the single `adventure.py` module.
- Carry capacity is strictly one item at any moment.
- Pickup must be triggered by collision/touch only (never by a keypress).
- Drop must be triggered by a keypress only (never automatically, never by collision).
- Only new constants are added; existing constants (`PLAYER_X/Y`, `PLAYER_SIZE`, `WALL_THICKNESS`, `LOGICAL_WIDTH/HEIGHT`, `_X_MIN/_X_MAX/_Y_MIN/_Y_MAX`) are not redefined or shadowed.
- Item spawn positions must keep the existing adversarial pixel assertions valid (notably the center pixel `(80, 105)` and the corner interior pixel `(9, 9)` sampled by `test_adventure_adversarial.py` must continue to read the expected `ROOM_COLOR` / `PLAYER_COLOR`).
- Render order must remain `draw_room` → items → `draw_player` so the player visually stays on top of world items at its own position.

## Blocking Ambiguity Questions (must be empty to proceed)
- None. Remaining open choices are treated as non-blocking requirement decisions.

## Requirement Decisions (resolve before epics/stories/mocks)
1. Which keyboard key is the drop key (e.g., Space, D, Enter)? Affects acceptance criteria and any on-screen hint text.
2. How is the currently carried item shown to the player — attached to the player sprite, or displayed in a HUD area (and if HUD, where on screen)?
3. Item starting positions in the play area (specific coordinates or general regions) — needed for mocks and acceptance tests, and must avoid the existing adversarial sample pixels `(80, 105)` and `(9, 9)`.
4. Visual representation of each item — color and shape/glyph for the chalice, key, and sword — and item-size assumptions for collision tuning (recommended `ITEM_SIZE >= PLAYER_SIZE` to avoid `PLAYER_SPEED` jump-over).
5. Should dropped items be re-pickup-able immediately once the player is no longer overlapping them, or only after some cooldown? (Default assumption: re-pickup-able as soon as not overlapping.)
6. Is the developer responsible for hand-placing items at valid non-overlapping coordinates, or must initial placement programmatically avoid walls, the player spawn, and other items?
7. Carry-one collision policy while already carrying: ignore second-item contact (recommended), swap, or block overlap.
8. Drop placement and anti-loop policy: drop at player position with one-frame pickup suppression (recommended), fixed offset, or direction-based offset.

# Intent

## Request (verbatim)
> T4 — Items: pickup, carry-one, drop (chalice + key + sword, touch-to-pickup, drop on keypress). Add three world items (chalice, key, sword) to the pygame Atari Adventure homage. Player picks up by touch (collision), can carry only one item at a time, and drops the carried item via a keypress. Builds on T1 (game loop/render) and T2 (movement + wall collision).

## Understanding (rephrase)
The game currently has a player that moves around with arrow keys and collides with walls. After this change, three distinct items — a chalice, a key, and a sword — will exist in the world at defined starting positions and be visibly rendered each frame. When the player's sprite touches an item, the player will automatically pick it up, the item will disappear from the world, and the player will be considered "carrying" that item. The player can only hold one item at a time, so touching another item while already carrying one will have no pickup effect. Pressing a dedicated drop key will release the currently carried item back into the world at (or near) the player's current position, making it visible again and available to be picked up by re-touching it.

## Success Criteria (observable)
- [ ] Three items — chalice, key, and sword — are visible on screen at game start, each at a distinct location and visually distinguishable from one another and from the player.
- [ ] When the player moves into contact with a world item and is not already carrying anything, that item disappears from the world and the player is marked as carrying it.
- [ ] While carrying an item, the player walking into another world item does not pick up the second item (the second item remains visible in the world).
- [ ] Pressing the designated drop key while carrying an item causes that item to reappear in the world at a position associated with the player, and the player is no longer carrying anything.
- [ ] Pressing the drop key while not carrying anything has no effect (no crash, no phantom item spawned).
- [ ] After dropping an item, the player can move away and then re-enter contact with that same item to pick it up again.
- [ ] The carried item is indicated to the player somehow (either visually attached to the player or shown in a HUD) so the player can tell which item, if any, they are holding.
- [ ] Player movement and wall collision behavior from T1/T2 continue to work unchanged.
- [ ] The game loop continues to run at a stable frame rate with the items present (no regressions in render or input handling).

## Constraints / Non-Goals
- Constraints:
  - Must not break or alter the existing game loop and render foundation from T1.
  - Must not break or alter arrow-key movement or wall collision from T2.
  - Must remain implemented with pygame (no new runtime or engine).
  - Carry capacity is strictly one item at any moment.
  - Pickup must be triggered by collision/touch only (not a keypress).
  - Drop must be triggered by a keypress (not automatic, not collision-based).
- Non-goals:
  - No item use/consume/effect behavior (e.g., the key does not unlock anything, the sword does not attack, the chalice does not score/win).
  - No inventory beyond the single carry slot (no backpack, no swapping in one action).
  - No enemies, dragons, scoring, or game-over conditions.
  - No multiple rooms or map transitions (single screen / current play area only).
  - No animation of pickup/drop beyond the item appearing or disappearing.
  - No sound effects required.
  - No persistence of item state across game restarts.

## Assumptions Ledger
- A1: The "world" is the existing single play area established by T1/T2; items live in the same coordinate space as the player and walls. (safe) — evidence: request says "Add three world items ... to the pygame Atari Adventure homage" and "Builds on T1 ... and T2".
- A2: Items are static (do not move on their own) until picked up or dropped. (safe) — evidence: phrasing "world items" with no motion behavior described.
- A3: Items can be placed on any walkable tile and do not need to respect wall collision themselves (they're authored by the developer, not spawned dynamically). (safe) — evidence: not specified; standard for Adventure homage.
- A4: A single dedicated keyboard key will be used to drop, distinct from movement keys. (safe) — evidence: "drop on keypress".
- A5: Dropping places the item at or immediately adjacent to the player's current position such that the player is not instantly re-overlapping and re-picking it up on the next frame. (risky) — evidence: not specified; behavior must be defined to avoid an infinite pickup/drop loop.
- A6: "Carry-one" means the player cannot swap items by walking onto a second item; the second item is simply ignored while carrying. (risky) — evidence: request says "can carry only one item at a time" but does not specify swap semantics.
- A7: The carried item is communicated to the player either by drawing it attached to the player sprite or via a simple HUD indicator; either is acceptable for this ticket. (risky) — evidence: not specified.
- A8: Item starting positions are chosen by the implementer (any sensible non-overlapping placement inside the play area) and do not need to match historical Atari Adventure coordinates. (safe) — evidence: "homage", not "replica".
- A9: There is exactly one chalice, one key, and one sword (three items total, not three of each). (safe) — evidence: "three world items (chalice, key, sword)".
- A10: Visual distinction between items can be by color and/or shape; pixel-accurate Atari sprites are not required for T4. (safe) — evidence: "homage" framing and scope of prior tickets.

## Blocking Ambiguity Questions (must be answered to proceed)
- None. Remaining implementation choices are converted into non-blocking requirement decisions below.

## Requirement Decisions (needed before epics/stories/mocks)
1. Which keyboard key is the drop key? (e.g., Space, D, or Enter — affects story acceptance criteria and any on-screen hint text.)
2. How is the currently carried item shown to the player — attached to the player sprite, or displayed in a HUD area (and if HUD, where on screen)?
3. Item starting positions in the play area (specific coordinates or general regions) — needed for mocks and acceptance tests.
4. Visual representation of each item — color and shape/glyph for the chalice, key, and sword — and player-sprite size assumptions for collision tuning.
5. Should dropped items be re-pickup-able immediately (after the player steps away once), or only after some cooldown? (Default assumption: re-pickup-able as soon as the player is no longer overlapping them.)
6. Should the initial placement of items avoid overlapping walls and each other automatically, or is the developer responsible for hand-placing them at valid coordinates?
7. Carry-one collision policy while already carrying: ignore second-item contact (recommended), swap, or block overlap.
8. Drop placement and anti-loop policy: drop at player position with one-frame pickup suppression (recommended), fixed offset, or direction-based offset.

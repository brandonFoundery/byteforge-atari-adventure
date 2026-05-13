# Intent

## Request (verbatim)
> T3 — Multi-room world + screen transitions (4-6 rooms, edge transitions, distinct colors). Build a multi-room world (4–6 rooms) with screen-transition mechanics: when the player crosses a room edge, the display swaps to the adjacent room. Each room has its own distinct color/theme, mimicking the Atari Adventure room model (single-screen rooms connected by edge-warp transitions, not scrolling). Builds on T1 (game loop + render foundation, Python pygame) and T2 (player movement with wall collision).

## Understanding (rephrase)
The game world will be expanded from a single screen into a small connected map of between 4 and 6 distinct rooms. Each room occupies the full game screen (no camera scrolling) and is visually distinguishable from every other room by color or theme. When the player character walks past a room boundary (the edge of the screen, in one of the four cardinal directions), the game instantly replaces the current room with the adjacent room, and the player reappears on the opposite edge of the new room — matching the classic Atari Adventure "screen warp" model. Player movement and wall-collision behavior from prior work continues to function inside each room without regression.

## Success Criteria (observable)
- [ ] The game contains between 4 and 6 distinct rooms, inclusive.
- [ ] Each room is visually distinguishable from every other room by a unique color or theme that can be identified by eye in a screenshot.
- [ ] At least one valid edge connection exists between rooms such that the player can reach every room from the starting room by walking through edges (the room graph is connected).
- [ ] When the player crosses a room edge, the display swaps to the adjacent room as a whole-screen replacement (no scrolling/panning animation).
- [ ] After a transition, the player character appears on the opposite edge of the new room (e.g., exiting via the right edge causes entry on the left edge of the next room).
- [ ] The player remains controllable in the new room using the same movement controls established in T2.
- [ ] Wall collision continues to work inside every room (player cannot pass through interior walls).
- [ ] Room boundaries that are NOT connected to an adjacent room behave as walls (player cannot exit into nothing).
- [ ] Re-entering a previously-visited room via the same edge returns the player to a deterministic position.
- [ ] The existing T1 game loop and T2 movement features continue to function (no regression).

## Constraints / Non-Goals
- Constraints:
  - Must build on T1 (pygame game loop + render foundation) and T2 (player movement with wall collision) — must not regress those features.
  - Must use the Atari Adventure room model: single-screen rooms connected by edge warps, NOT scrolling/camera-following.
  - Implementation must remain Python + pygame, consistent with prior tickets.
- Non-goals:
  - Scrolling cameras or smooth pan transitions between rooms.
  - In-room objects, items, enemies, NPCs, doors, keys, or pickups.
  - Procedural room generation.
  - Save/load of room state.
  - Sound effects for transitions.
  - Mini-map or HUD showing room layout.
  - More than 6 rooms.

## Assumptions Ledger
- A1: "Room edge" means the four screen-boundary edges (top, bottom, left, right) of the play area, not interior thresholds. (safe) — evidence: request explicitly references "crosses a room edge" in the Atari Adventure model.
- A2: A transition is instantaneous (frame-swap), not animated. (safe) — evidence: request says "the display swaps to the adjacent room" and references Atari Adventure.
- A3: The room graph is authored (hand-defined), not procedurally generated. (safe) — evidence: small fixed count (4–6) and Adventure homage implies a designed map.
- A4: Player entry position after a transition mirrors exit position on the opposite edge (e.g., exit right at y=100 → enter left at y=100). (risky) — evidence: standard Atari Adventure convention; not explicitly stated.
- A5: Each room shares the same screen dimensions and play-area bounds as T1. (safe) — evidence: "single-screen rooms" and continuation of T1 foundation.
- A6: "Distinct color/theme" can be satisfied by a unique background color per room (theming beyond background is not required). (risky) — evidence: request lists "distinct colors" as the headline differentiator.
- A7: Edges that do not lead to another room behave as solid walls. (risky) — evidence: needed to prevent the player from walking off-screen into undefined state; not explicitly specified.
- A8: There is exactly one designated starting room when the game launches. (safe) — evidence: implied by the game-loop foundation in T1.
- A9: Room connections are bidirectional (if room A's east edge leads to B, then B's west edge leads back to A). (risky) — evidence: Adventure convention; not explicitly stated, and one-way connections are plausible.

## Blocking Ambiguity Questions (must be answered to proceed)
1. None — the request is sufficiently specified at the intent level. Open product/UX choices are captured below as Requirement Decisions and can be resolved during specification rather than blocking intent approval.

## Requirement Decisions (needed before epics/stories/mocks)
1. Exact room count: 4, 5, or 6 rooms?
2. Map topology: what is the adjacency layout (e.g., 2x2 grid, 2x3 grid, linear chain, branching, ring)? Which room is the starting room?
3. Are room connections always bidirectional, or are one-way edges allowed?
4. How are edges that do not lead anywhere treated — invisible walls, visible walls, or some other indicator?
5. Post-transition player position rule — preserve the perpendicular coordinate (mirror across the edge), snap to edge center, or a per-edge authored spawn point?
6. Distinct visual theme per room — background color only, or also distinctive wall color / interior wall layout / decorative motif?
7. Should each room have its own interior wall layout (carrying T2 collision into varied geometry), or do all rooms share an empty interior in T3?
8. Is there any visible indicator (e.g., a labeled room name, a transition flash) when a transition occurs, or is the swap completely silent?
9. Should the player be able to immediately re-cross the edge they just entered from to return, or is there a debounce/cooldown to prevent rapid oscillation?
10. Is there any persistence requirement (e.g., remembering which rooms have been visited) for T3, or is this purely stateless room rendering?

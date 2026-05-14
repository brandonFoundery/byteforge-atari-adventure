# Teach-back (Proof of Understanding)

## Summary
T3 expands the game from a single screen into a small connected world of 4–6 distinct rooms, in the style of Atari Adventure. Each room fills the entire screen (no scrolling) and has its own distinct color/theme. When the player walks past a screen-edge that connects to another room, the display is instantly replaced with that adjacent room and the player reappears on the opposite edge of the new room. Player movement and wall collision from T1/T2 must continue to work inside every room without regression.

## What Changes / What Doesn’t
- Changes:
  - The world is now multi-room (between 4 and 6 rooms) instead of a single screen.
  - Each room has its own distinct background color/theme.
  - Edges of the screen become room-aware: an edge that points to a neighbor is a passage that triggers a transition; an edge that points to nothing remains a solid wall.
  - The game tracks a current/active room and renders that room each frame.
  - Crossing a passage edge instantly swaps the active room and warps the player to the opposite edge of the new room (Atari Adventure–style screen warp).
- Does not change:
  - The Python + pygame technology stack (no new dependencies).
  - The arrow-key, 4-direction movement controls from T2.
  - The T1 game-loop / render foundation.
  - The single-screen, no-scrolling presentation (each room fills the screen; transitions are whole-screen swaps, never animated pans).
  - No inventory, enemies, items, doors, NPCs, audio, save/load, mini-map, or procedural generation are introduced.

## Example
- Current (T2): The player can move in a single room. Pressing into any edge clamps the player at that edge. The screen color never changes.
- Desired (T3): The player is in a room with (for example) a yellow background. Walking off the right edge instantly replaces the screen with a different-colored room (e.g., blue), and the player now stands at the left edge of that room at roughly the same vertical position. Walking back off the left edge returns to the yellow room at the right edge. If an edge has no neighbor, pressing into it still clamps like a wall.

## Success Criteria
- [ ] The game contains between 4 and 6 distinct rooms, inclusive.
- [ ] Each room is visually distinguishable from every other room by a unique color or theme that can be identified by eye in a screenshot.
- [ ] The room graph is connected: every room is reachable from the starting room by walking through edges.
- [ ] Crossing a passage edge swaps the display to the adjacent room as a whole-screen replacement (no scrolling/panning animation).
- [ ] After a transition, the player appears on the opposite edge of the new room (e.g., exit right → enter left).
- [ ] The player remains controllable in the new room using the T2 arrow-key controls.
- [ ] Wall collision continues to work inside every room.
- [ ] Edges with no adjacent room behave as solid walls (player cannot exit into nothing).
- [ ] Re-entering a previously-visited room via the same edge returns the player to a deterministic position.
- [ ] All existing T1 / T2 behavior continues to work (no regression).

## Constraints / Invariants
- Builds on T1 (pygame game loop + render foundation) and T2 (movement + wall collision); must not regress either.
- Implementation stays in Python + pygame, consistent with prior tickets.
- Atari Adventure room model: single-screen rooms connected by edge warps; never scrolling or camera-following.
- All rooms share the same screen dimensions and play-area bounds as T1.
- A transition is instantaneous (frame-swap), not animated.
- Exactly one designated starting room when the game launches.

## Blocking Ambiguity Questions (must be empty to proceed)
- None

## Requirement Decisions (resolve before epics/stories/mocks)
- Exact room count (4, 5, or 6), adjacency/topology (e.g., 2×2, 2×3, linear, ring), and designated starting room.
- Whether room connections must be bidirectional or one-way edges are allowed.
- Post-transition player position rule: mirror the perpendicular coordinate, snap to edge center, or use per-edge authored spawn points.
- Visual theming scope: background color only vs. also wall color / interior layout / decorative motif.
- Whether each room has its own interior wall layout or all rooms share an empty interior in T3.
- Treatment of edges that lead nowhere: invisible wall, visible wall, or other indicator.
- Whether a transition indicator (flash, room name) is required or the swap is silent.
- Whether a re-cross debounce/cooldown is required to prevent rapid oscillation at an edge.
- Persistence requirement for visited rooms (stateful) vs. stateless room rendering only for T3.
- Per-room color palette: arbitrary designer pick vs. mirror Atari Adventure’s original kingdom colors.
- Sealed-edge representation: `neighbors[dir] = None` vs. an explicit `walls` set vs. implicit absence.
- `move_player` signature evolution: optional `room=None` for back-compat vs. hard signature change with same-commit test updates.
- `current_room` state location: module global vs. Game object attribute vs. threaded through `run_game_loop`.

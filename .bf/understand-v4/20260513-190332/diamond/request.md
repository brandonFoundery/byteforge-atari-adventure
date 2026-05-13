# Request Seed — T4: Items (pickup, carry-one, drop)

**Ticket:** 901b7299-81f1-4995-6c14-08deb0efcb30

## Raw Request

T4 — Items: pickup, carry-one, drop (chalice + key + sword, touch-to-pickup, drop on keypress)

## Inferred Scope

Building on the existing Atari Adventure homage (T1: game loop + render foundation; T2: player movement with wall collision), introduce an item system with three items — chalice, key, and sword — that the player can:

- **Touch-to-pickup**: Walking onto an item picks it up (no button required).
- **Carry-one**: The player can only hold a single item at a time. Picking up another item is either disallowed while carrying, or swaps with the carried item (to be decided in comprehender).
- **Drop on keypress**: Pressing a designated key drops the currently carried item at (or near) the player's current position.

Items live in the world (with positions), are rendered when not carried, are rendered attached to the player when carried, and become world entities again when dropped.

## Anchor Context

- Repo: pygame-based Python Atari Adventure homage
- Prior tickets: T1 (game loop/render), T2 (movement + wall collision)
- Next downstream concerns likely: room transitions, dragons, item-gated interactions (key opens gate, sword fights dragon, chalice = win condition) — but T4 only covers the pickup/carry/drop mechanic itself

# Adversary Brief — test-v4

## Your Role
You are the RED TEAM adversary for the test-v4 pipeline. Your job is to write adversarial Python pytest tests for a pygame-based game that probe edge cases and failure modes.

## Team Context
- Team: test-v4-20260513-222227
- Your name: adversary
- Report results to: team-lead

## Feature Under Test
**T4 — Items: pickup, carry-one, drop (chalice + key + sword, touch-to-pickup, drop on keypress)**

### Implementation Details (known from adventure.py)
- Drop key: `pygame.K_SPACE` (NOT K_F — it's spacebar)
- Functions: `_try_pickup(px, py, player_size, floor_items, carried)`, `_on_drop_key(px, py, floor_items, carried)`
- Items init: `_init_items()` returns list of 3 dicts
- Carried item drawn at offset: `(px + PLAYER_SIZE, py)`
- AABB collision detection for pickup
- Carry-one enforced: `if carried: return floor_items, carried` at top of `_try_pickup`
- Drop places item at player position (px, py)

### Constants
- PLAYER_SIZE = 8, ITEM_SIZE = 6
- CHALICE at (40, 50), KEY at (100, 80), SWORD at (70, 140)
- PLAYER starts at center of screen

## Technology Stack
- Python/pygame game (NOT browser-based)
- Tests are Python pytest files
- Game module: `adventure` (importable as `import adventure`)
- Working directory: `/Users/brandonshuey/data/ByteForge/Repositories/e0710c02-7a18-467f-8a6e-519bafe16e3e/.bf-worktrees/901b7299`

## Output File
`/Users/brandonshuey/data/ByteForge/Repositories/e0710c02-7a18-467f-8a6e-519bafe16e3e/.bf-worktrees/901b7299/tests/e2e/adversarial/test_items_adversarial.py`

## Existing Coverage to AVOID Duplicating
From `tests/test_items.py`:
- draw call order (room/items/player)
- pixel at floor item matches color before pickup
- pixel near player matches carried color after pickup
- pixel at old position empty after pickup

## Tests to Write (8-10 adversarial tests targeting these failure modes)

Focus on LOGIC bugs in `_try_pickup` and `_on_drop_key`:

1. **carry-one invariant**: With item already carried, touching a second item should NOT replace the carried item
2. **all 3 kinds pickupable**: each of chalice, key, sword can be independently picked up via `_try_pickup`
3. **drop clears carried**: after `_on_drop_key`, carried must be None
4. **drop adds to floor**: after drop, the item appears in floor_items with correct position
5. **drop-then-pickup same item**: drop item, then move player onto it — should re-pickup
6. **AABB boundary precision**: player just outside range should NOT pick up item; player just inside range SHOULD
7. **rapid pickup-drop cycle**: 10 cycles of pickup+drop, state remains consistent
8. **drop preserves item kind**: dropped item retains original kind/color/size
9. **no items empty floor**: `_try_pickup` with empty floor returns ([], None) gracefully
10. **drop with no carried item is no-op**: `_on_drop_key` when carried=None returns unchanged floor_items

## Test File Template
```python
"""Adversarial tests for T4 — Items: pickup, carry-one, drop.

Each test targets a specific potential defect in item pickup/carry/drop logic.
All tests run headless via SDL_VIDEODRIVER=dummy.

Run with:
    pytest tests/e2e/adversarial/test_items_adversarial.py -v
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pygame
import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import adventure  # noqa: E402

# ... tests here
```

## Instructions
1. Read `adventure.py` to verify any details (you have full read access)
2. Read existing `tests/test_items.py` to avoid duplication
3. Write the test file at the output path above
4. After writing, send a message to **team-lead** with:
   - list of test names you wrote
   - brief rationale for each
   - path to the test file

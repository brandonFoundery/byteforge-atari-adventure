# C01 — RoomDataModelAndRegistry

**Type:** data-model
**Epic:** EPIC-001
**Stories:** STORY-001-1
**Dependencies:** (none)

## Traced requirements

REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006, REQ-007, REQ-008

## Goal

Introduce the `Room` data structure and the module-level 2x2 `ROOMS` registry in `adventure.py`. Pure data; no behavior change to game loop. T1/T2 tests must remain green.

## Constraints

- `Room` is importable from `adventure` and exposes `id`, `bg_color`, `neighbors`.
- `ROOMS` has exactly 4 entries: `yellow`, `blue`, `green`, `purple` (REQ-002).
- All four `bg_color` values pairwise distinct (REQ-003); use the palette in `shared-context/feature-overview.md`.
- `Room.neighbors` keys are exactly `{N, S, E, W}`; values are either an existing room id (string) or `None` (REQ-004).
- Adjacency matches 2x2 yellow-blue / green-purple layout (REQ-005).
- `START_ROOM = "yellow"` and `ROOMS["yellow"].bg_color == (240, 208, 64)` (REQ-006).
- Preserve `ROOM_COLOR = (240, 208, 64)` as a legacy alias (REQ-007).
- `tests/test_adventure.py` and `tests/test_movement.py` unchanged; pass without modification (REQ-008).

## Out of scope

Validators (C02), rendering (C03), movement (C04), warp (C05), loop wiring (C06).

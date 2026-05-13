# C02 — RegistryValidators

**Type:** backend-service
**Epic:** EPIC-001
**Stories:** STORY-001-2
**Dependencies:** C01

## Traced requirements

REQ-009, REQ-010, REQ-011, REQ-012, REQ-013, REQ-014

## Goal

Add two pure validator functions to `adventure.py`:
- `assert_symmetric(rooms)` — verifies bidirectional adjacency.
- `assert_connected(rooms, start)` — BFS from `start` reaches every room id.

## Constraints

- `assert_symmetric(rooms)` returns `None` on symmetric registries (REQ-009).
- Raises `ValueError` naming the offending room and direction on asymmetric registries (REQ-010).
- `assert_connected(rooms, start)` returns `None` when BFS from `start` reaches every key (REQ-011).
- Raises `ValueError` listing unreachable rooms otherwise (REQ-012).
- Neither validator mutates `rooms`; neither reads/mutates module-level `ROOMS` (REQ-013).
- `tests/test_adventure.py` and `tests/test_movement.py` continue to pass (REQ-014).

## Out of scope

Rendering, movement, transitions, and the `tests/test_rooms.py` file (C06).

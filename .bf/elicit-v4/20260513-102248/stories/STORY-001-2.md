# STORY-001-2: Registry validation helpers — symmetry & connectivity

## Parent Epic
EPIC-001 — Room model + registry (foundation, no behavior change)

## User Value
As a developer (and as the test suite), I need importable pure-Python helpers
that validate the room registry's structural invariants, so that hand-
authored maps cannot silently ship with broken/asymmetric/disconnected
adjacency.

## Scope
**Touch:** `adventure.py` (additive — two new functions; no other change).

**Do NOT touch:** `move_player`, `draw_room`, `run_game_loop`, the existing
constants block, the `Room`/`ROOMS`/`START_ROOM` symbols introduced in
STORY-001-1.

## Design Notes
Add two pure functions, both side-effect-free, taking the registry as input:

```python
_OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}

def assert_symmetric(rooms: dict[str, Room]) -> None:
    """Raise ValueError if any A.neighbors[d] == B but B.neighbors[opp(d)] != A."""

def assert_connected(rooms: dict[str, Room], start: str) -> None:
    """Raise ValueError if BFS from start does not reach every room id."""
```

Both functions:
- Take an explicit `rooms` argument (do NOT read the module-level `ROOMS`
  inside the function body). This keeps them unit-testable with arbitrary
  fixtures, including intentionally-broken fixtures.
- Raise `ValueError` with a clear message identifying the offending room/edge.
- Return `None` on success.

Do NOT invoke these validators at module import time in this story —
keep them callable from tests. (Calling them at import time may be added in
a later epic; this story stays minimal-surface.)

## Acceptance Criteria
- **REQ-009**: `adventure.py` exports a callable `assert_symmetric(rooms)`
  that returns `None` for any registry where every authored edge
  `A.neighbors[d] == B_id` has the matching reverse edge
  `rooms[B_id].neighbors[opposite(d)] == A.id`.
- **REQ-010**: `assert_symmetric` raises `ValueError` (with a message
  naming the offending room id and direction) when given a registry whose
  adjacency is asymmetric.
- **REQ-011**: `adventure.py` exports a callable `assert_connected(rooms,
  start)` that returns `None` when a breadth-first search starting at
  `start` reaches every key in `rooms`.
- **REQ-012**: `assert_connected` raises `ValueError` (with a message
  listing the unreachable room ids) when given a registry that is not
  fully connected from `start`.
- **REQ-013**: Neither validator mutates its `rooms` argument and neither
  reads or mutates the module-level `ROOMS`.
- **REQ-014**: `tests/test_adventure.py` and `tests/test_movement.py` pass
  unmodified after this story.

## Out of Scope
- Calling the validators at import time (deferred; would change failure
  semantics of `import adventure`).
- Tests for the validators themselves (STORY-001-3 covers that).

## Dependencies
- STORY-001-1 (needs `Room` / `ROOMS` to exist for type hints, though the
  functions accept any dict-shaped argument).

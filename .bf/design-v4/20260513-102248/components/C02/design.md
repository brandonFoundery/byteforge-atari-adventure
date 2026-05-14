# C02 — RegistryValidators — Design

**Type:** backend-service | **Epic:** EPIC-001 | **Story:** STORY-001-2
**Dependencies:** C01
**Requirements covered:** REQ-009..REQ-014

## 1. Purpose

Provide two **pure** validator functions on `adventure.py` that an
author / runtime can invoke against any room registry (not just the live
`ROOMS`) to detect authoring mistakes:

- `assert_symmetric(rooms)` — every adjacency is bidirectional.
- `assert_connected(rooms, start)` — BFS from `start` reaches every key.

These are the runtime guard that makes C01's "don't validate at import"
decision safe. C06 will call both once during `run_game_loop`
initialization.

## 2. Public symbols (added to `adventure.py`)

| Symbol | Signature | Raises |
|--------|-----------|--------|
| `assert_symmetric` | `(rooms: dict[str, Room]) -> None` | `ValueError` |
| `assert_connected` | `(rooms: dict[str, Room], start: str) -> None` | `ValueError` |

Both return `None` on success.

## 3. `assert_symmetric` — design

### 3.1 Contract

For every `room_id` in `rooms` and every direction `dir`, if
`rooms[room_id].neighbors[dir] == other_id`, then `other_id` must exist
in `rooms` AND `rooms[other_id].neighbors[OPPOSITE[dir]] == room_id`.

### 3.2 Algorithm

```python
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}

def assert_symmetric(rooms: dict[str, Room]) -> None:
    """Verify every passage edge is bidirectional.

    Raises ValueError naming the offending room and direction.
    """
    for room_id, room in rooms.items():
        for direction, neighbor_id in room.neighbors.items():
            if neighbor_id is None:
                continue  # sealed edges have no symmetry requirement
            if neighbor_id not in rooms:
                raise ValueError(
                    f"Room {room_id!r} edge {direction!r} points to "
                    f"unknown room {neighbor_id!r}"
                )
            back = rooms[neighbor_id].neighbors.get(OPPOSITE[direction])
            if back != room_id:
                raise ValueError(
                    f"Asymmetric edge: {room_id!r}.{direction} -> "
                    f"{neighbor_id!r}, but {neighbor_id!r}."
                    f"{OPPOSITE[direction]} -> {back!r}"
                )
```

### 3.3 Edge cases (covered)

| Case | Behavior |
|------|----------|
| Sealed edge (`neighbor_id is None`) | Skipped — sealing is unilateral by spec. |
| Edge points to unknown room id | Raises with offending room + direction + bad id. |
| Edge points to existing room but the reciprocal direction is sealed | Raises (asymmetric). |
| Edge points to existing room and reciprocal direction targets a third room | Raises (asymmetric — `back != room_id`). |
| Reciprocal direction key absent from neighbor's `neighbors` dict | `.get(OPPOSITE[direction])` returns `None`; comparison fails; raises (treats missing key as sealed for purpose of the error message). |
| Self-loop (`neighbor_id == room_id`) | `back = rooms[room_id].neighbors.get(OPPOSITE[direction])` — if not the same room id, raises. Self-loops are nonsensical for this game but are not specially banned here; if authored both ways (`yellow.E="yellow"` and `yellow.W="yellow"`) it would pass — acceptable for a pure symmetry check. |

### 3.4 No mutation

The function only **reads** `rooms` and the `neighbors` dicts. No
assignment. No call to module-level `ROOMS`. The function never imports
anything new (uses only builtins). (REQ-013)

## 4. `assert_connected` — design

### 4.1 Contract

BFS from `start` (visiting only passage neighbors — `neighbor_id is not
None`) must reach every key in `rooms`. If any key is unreachable, raise
`ValueError` listing those unreachable ids.

### 4.2 Algorithm

```python
from collections import deque

def assert_connected(rooms: dict[str, Room], start: str) -> None:
    """Verify BFS from start reaches every room id.

    Raises ValueError listing unreachable rooms (sorted).
    """
    if start not in rooms:
        raise ValueError(f"Start room {start!r} not in registry")

    visited: set[str] = {start}
    queue: deque[str] = deque([start])
    while queue:
        current = queue.popleft()
        for neighbor_id in rooms[current].neighbors.values():
            if neighbor_id is None:
                continue
            if neighbor_id not in rooms:
                # don't crash here — let assert_symmetric report it
                continue
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                queue.append(neighbor_id)

    missing = set(rooms.keys()) - visited
    if missing:
        raise ValueError(
            f"Rooms unreachable from {start!r}: {sorted(missing)}"
        )
```

### 4.3 Edge cases

| Case | Behavior |
|------|----------|
| `start` not in `rooms` | Raises immediately with explicit message. |
| Single-room registry with `start == only_id` | Passes (visited == {start} == set(rooms)). |
| Two disconnected components | Raises listing component not containing `start`. |
| Edge to unknown id encountered mid-BFS | Skipped — `assert_symmetric` is the authority on unknown ids. (Author should call both validators; C06 does.) |
| Repeated visits | Guarded by `visited` set. |

### 4.4 No mutation

Same as `assert_symmetric` — only reads (REQ-013). `deque` and `set` are
local. The `rooms` argument is not mutated.

## 5. Integration

### 5.1 Call site (C06)

Inside `run_game_loop` (function-local, **once** at top of loop, before
the event loop):

```python
def run_game_loop(surface, *, fps=TARGET_FPS, event_getter=pygame.event.get):
    assert_symmetric(ROOMS)
    assert_connected(ROOMS, START_ROOM)
    current_room = ROOMS[START_ROOM]
    ...
```

Calling them inside `run_game_loop` (not at module import) keeps the
import path quick and lets tests construct synthetic registries and call
the validators directly without first triggering pygame init. This
matches DECISION D1.4.

### 5.2 Test usage

`tests/test_rooms.py` (lands in C06) tests both validators with
**synthetic** registries built inline — never mutating `adventure.ROOMS`
(REQ-020). Example shapes covered:

- Pass: symmetric 2-node and 4-node registries.
- Fail symmetric: `{"a": Room("a", c, {"E": "b", ...}), "b": Room("b", c, {"W": None, ...})}` — must raise.
- Fail connected: `{"a": ..., "b": ..., "c": all-sealed}` — must raise
  with `"c"` in the listed missing rooms.
- No mutation: caller passes a registry and asserts identity / equality
  after the call.

## 6. Determinism

- `assert_symmetric` iterates `rooms.items()` in insertion order; first
  asymmetric edge wins for the error message — deterministic given
  Python 3.7+ dict ordering.
- `assert_connected` uses BFS with insertion-order traversal of
  `neighbors.values()`; `missing` is reported sorted alphabetically so
  the message text is stable across runs (helps test stability).

## 7. Performance

Registry size is bounded (4 rooms in scope; spec allows 4-6). Both
validators are O(V + E) where V is rooms and E is the total declared
edges (≤ 4·V). With V=4 this is ≤ 20 operations per validator. Negligible
even on every `run_game_loop` call.

## 8. REQ coverage matrix

| REQ | How satisfied |
|-----|---------------|
| REQ-009 | Symmetric registries: function returns `None` (no raise). |
| REQ-010 | Asymmetric: raises `ValueError` whose message names offending room id + direction (and back-pointer where applicable). |
| REQ-011 | Connected registries: function returns `None`. |
| REQ-012 | Disconnected: raises `ValueError` listing unreachable rooms (sorted). |
| REQ-013 | Neither function mutates the input; neither references module-level `ROOMS`. (`assert_connected` accepts `start` as a parameter; nothing looks at `adventure.START_ROOM` from inside the function.) |
| REQ-014 | Pure additions; no signature changes elsewhere. `tests/test_adventure.py` and `tests/test_movement.py` pass unmodified. |

## 9. Decisions (added to DECISION_LOG)

- **D2.1 — Validators are pure module-level functions, not methods on
  `Room`.** Keeps `Room` a dumb dataclass; lets tests pass synthetic
  registries without instantiating live `ROOMS`.
- **D2.2 — Skip unknown-id during connectivity scan.** Symmetry is the
  authority on unknown ids; reporting both would produce noisy double
  errors when only `assert_symmetric` is needed. C06 calls
  `assert_symmetric` **first** so the unknown-id case surfaces there.
- **D2.3 — Missing reciprocal key treated as sealed (`.get` returns
  `None`).** Message still surfaces the asymmetric mismatch cleanly.
- **D2.4 — `missing` reported sorted in `assert_connected` error.**
  Stable test assertions.

## 10. Risks

- **R6 (asymmetric authoring).** Addressed.
- **No new risks introduced.** Validators are pure, side-effect-free,
  no I/O.

## 11. Out of scope

Rendering, movement, transitions, `tests/test_rooms.py` file creation
(C06 owns the file). Reporting style of error messages beyond the rules
above is left to implementation; tests assert structural content
(`"yellow"`, `"E"`, etc.) not exact strings.

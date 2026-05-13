# C05 — TransitionWarpHelper — Design

**Type:** backend-service | **Epic:** EPIC-003 | **Story:** STORY-003-2
**Dependencies:** C01
**Requirements covered:** REQ-037..REQ-042

## 1. Purpose

Add a pure helper that computes destination-room player placement after an
edge exit, with no pygame dependency and no hidden state.

`_warp_position` transforms an `(exit_dir, x, y)` event into:
- destination room (`Room`)
- new in-room x/y coordinates

This isolates transition math so C06 can keep loop logic simple.

## 2. Public symbols (added)

| Symbol | Signature | Notes |
|--------|-----------|-------|
| `INWARD_OFFSET` | `int` | `PLAYER_SPEED + 1` |
| `_warp_position` | `(room: Room, exit_dir: str, x: int, y: int) -> tuple[Room, int, int]` | pure helper |

`_warp_position` is private-by-convention (`_` prefix) but intentionally
importable for tests.

## 3. Constant contract

```python
INWARD_OFFSET = PLAYER_SPEED + 1
```

Why `+1`:
- One held-direction frame immediately after warp should not re-trigger the
  edge crossing (debounce by geometry, no extra state flags).

## 4. Warp algorithm

Helper utilities:

```python
def _clamp_x(v: int) -> int:
    return max(_X_MIN, min(_X_MAX, v))

def _clamp_y(v: int) -> int:
    return max(_Y_MIN, min(_Y_MAX, v))
```

Core logic:

```python
def _warp_position(room: Room, exit_dir: str, x: int, y: int) -> tuple[Room, int, int]:
    neighbor_id = room.neighbors.get(exit_dir)
    if neighbor_id is None:
        raise ValueError(f"Cannot warp through sealed edge {room.id}.{exit_dir}")
    if neighbor_id not in ROOMS:
        raise ValueError(f"Unknown room id {neighbor_id!r} from {room.id}.{exit_dir}")

    new_room = ROOMS[neighbor_id]

    if exit_dir == "E":
        return new_room, _X_MIN + INWARD_OFFSET, _clamp_y(y)
    if exit_dir == "W":
        return new_room, _X_MAX - INWARD_OFFSET, _clamp_y(y)
    if exit_dir == "N":
        return new_room, _clamp_x(x), _Y_MAX - INWARD_OFFSET
    if exit_dir == "S":
        return new_room, _clamp_x(x), _Y_MIN + INWARD_OFFSET

    raise ValueError(f"Unknown exit direction: {exit_dir!r}")
```

## 5. Direction mapping table

| Exit dir | New room edge entered | Parallel axis placement | Perpendicular axis placement |
|----------|-----------------------|--------------------------|-------------------------------|
| `E` | west edge of east neighbor | `x = _X_MIN + INWARD_OFFSET` | `y = clamp(y)` |
| `W` | east edge of west neighbor | `x = _X_MAX - INWARD_OFFSET` | `y = clamp(y)` |
| `N` | south edge of north neighbor | `y = _Y_MAX - INWARD_OFFSET` | `x = clamp(x)` |
| `S` | north edge of south neighbor | `y = _Y_MIN + INWARD_OFFSET` | `x = clamp(x)` |

This is the mirror rule resolved in elicit and carried into design.

## 6. Purity and determinism guarantees

- No `import pygame` required.
- Reads only explicit arguments plus constant tables (`ROOMS`, bounds,
  `INWARD_OFFSET`).
- No writes to module globals.
- Same input tuple yields same output tuple (deterministic).

## 7. Validation and failure policy

Although C06 should call `_warp_position` only after C04 emits a valid exit,
C05 still performs defensive checks and raises `ValueError` for:

- sealed edge warp request
- unknown neighbor id
- unsupported exit direction

This keeps failure modes explicit in tests and avoids silent corruption.

## 8. Test plan impact

C06-owned tests should cover:

- E/W/N/S warp placement math
- perpendicular clamping bounds
- deterministic repeated calls
- no immediate re-transition behavior when paired with C04/C06 loop flow

## 9. REQ coverage matrix

| REQ | How satisfied |
|-----|---------------|
| REQ-037 | East warp returns east neighbor with `x = _X_MIN + INWARD_OFFSET` and clamped `y`. |
| REQ-038 | Mirror handling implemented for W/N/S. |
| REQ-039 | `INWARD_OFFSET = PLAYER_SPEED + 1` introduced and used for all transition entries. |
| REQ-040 | Pure function with deterministic mapping from args to return tuple. |
| REQ-041 | Perpendicular axis clamped to room-interior bounds. |
| REQ-042 | No pygame import, no module-global writes, callable headlessly. |

## 10. Decisions

- **D5.1 — Geometry-based debounce via `INWARD_OFFSET`.**
  Avoids extra transition state machine complexity.
- **D5.2 — Defensive `ValueError` on invalid warp requests.**
  Aids debugging and protects against silent graph corruption.
- **D5.3 — Keep helper private-by-convention but directly testable.**
  Transition math stays isolated and unit-test-friendly.

## 11. Risks

- **R4 — repeated transitions on held input.** Mitigated by inward offset.
- **R6 — malformed registry neighbor ids.** Mitigated by validation checks and
  C02 validators.

## 12. Out of scope

- Detecting exits from raw input (C04).
- Mutating `current_room` inside loop (C06).

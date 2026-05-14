# C04 — RoomAwareMovement — Design

**Type:** backend-service | **Epic:** EPIC-003 | **Story:** STORY-003-1
**Dependencies:** C01
**Requirements covered:** REQ-031..REQ-036

## 1. Purpose

Extend `move_player` so it can operate in two modes:

- **Legacy mode** (`room=None`): preserve exact T2 clamp behavior and return
  `(x, y)`.
- **Room-aware mode** (`room=Room`): detect passage-edge exits and return an
  exit signal instead of clamping through a doorway.

This component owns only edge-crossing detection and deterministic tie
resolution. It does not perform room swaps or warp math (C05/C06).

## 2. Public surface change

| Symbol | Before | After |
|--------|--------|-------|
| `move_player` | `move_player(x, y, keys_pressed) -> tuple[int, int]` | `move_player(x, y, keys_pressed, room=None) -> tuple[int, int] \| tuple[str, str]` |

Exit signal form (room-aware mode only):
- `("exit", "E")`
- `("exit", "W")`
- `("exit", "N")`
- `("exit", "S")`

The first tuple item is a literal discriminator (`"exit"`) to keep loop wiring
in C06 explicit and branch-safe.

## 3. Algorithm

### 3.1 Shared input processing (both modes)

Movement deltas are applied exactly once using existing `_is_pressed` and
`PLAYER_SPEED`:

```python
nx, ny = x, y
if _is_pressed(keys_pressed, _K_RIGHT, pygame.K_RIGHT):
    nx += PLAYER_SPEED
if _is_pressed(keys_pressed, _K_LEFT, pygame.K_LEFT):
    nx -= PLAYER_SPEED
if _is_pressed(keys_pressed, _K_DOWN, pygame.K_DOWN):
    ny += PLAYER_SPEED
if _is_pressed(keys_pressed, _K_UP, pygame.K_UP):
    ny -= PLAYER_SPEED
```

### 3.2 Legacy path (`room is None`)

Return exact T2 clamp behavior:

```python
return max(_X_MIN, min(_X_MAX, nx)), max(_Y_MIN, min(_Y_MAX, ny))
```

This preserves all existing callers that do not pass a room (REQ-036).

### 3.3 Room-aware path (`room is not None`)

Evaluation order is deterministic and enforces the diagonal rule:

1. Resolve horizontal overflow/underflow first (`E`, then `W`).
2. Only if no horizontal exit is produced, resolve vertical overflow/underflow
   (`S`, then `N`).
3. If all crossing checks are non-exit, return clamped `(x, y)`.

Pseudo-code:

```python
# Horizontal priority (REQ-035)
if nx > _X_MAX:
    if room.neighbors["E"] is not None:
        return ("exit", "E")
    nx = _X_MAX
elif nx < _X_MIN:
    if room.neighbors["W"] is not None:
        return ("exit", "W")
    nx = _X_MIN

# Vertical only when no horizontal exit was emitted
if ny > _Y_MAX:
    if room.neighbors["S"] is not None:
        return ("exit", "S")
    ny = _Y_MAX
elif ny < _Y_MIN:
    if room.neighbors["N"] is not None:
        return ("exit", "N")
    ny = _Y_MIN

return nx, ny
```

## 4. Edge behavior matrix

| Edge condition | Neighbor exists | Result |
|----------------|-----------------|--------|
| `nx > _X_MAX` | `neighbors["E"] is not None` | `("exit", "E")` |
| `nx > _X_MAX` | `neighbors["E"] is None` | clamp `nx = _X_MAX` |
| `nx < _X_MIN` | `neighbors["W"] is not None` | `("exit", "W")` |
| `nx < _X_MIN` | `neighbors["W"] is None` | clamp `nx = _X_MIN` |
| `ny > _Y_MAX` | `neighbors["S"] is not None` | `("exit", "S")` (unless horizontal exit already emitted) |
| `ny > _Y_MAX` | `neighbors["S"] is None` | clamp `ny = _Y_MAX` |
| `ny < _Y_MIN` | `neighbors["N"] is not None` | `("exit", "N")` (unless horizontal exit already emitted) |
| `ny < _Y_MIN` | `neighbors["N"] is None` | clamp `ny = _Y_MIN` |

## 5. Deterministic diagonal policy (REQ-035)

When the player crosses two edges in one frame (e.g. right+down at a corner):

- At most one exit signal is emitted.
- Horizontal axis wins ties.
- The non-winning axis is resolved by clamp behavior in that frame.

This keeps transition count bounded (`<= 1` per frame) and prevents ambiguous
`("E" and "S")` dual-exit states.

## 6. Integration contract with C05/C06

- C04 reports **whether** an edge transition should occur and which edge.
- C05 computes **where** the player lands in the destination room.
- C06 performs the actual room reassignment and rendering order.

`move_player` never mutates room state, player globals, or module attributes.

## 7. Test implications

Primary tests are implemented in C06-owned files (`tests/test_rooms.py` and
`tests/test_movement.py`). C04-defined coverage:

- Passage-edge emits exit for E/W/N/S.
- Sealed-edge clamps for E/W/N/S.
- Diagonal priority emits one horizontal exit.
- Legacy mode (`room=None`) remains stable for existing tests.

## 8. REQ coverage matrix

| REQ | How satisfied |
|-----|---------------|
| REQ-031 | New optional `room` parameter; room-aware path reads `room.neighbors` to choose clamp vs exit. |
| REQ-032 | East passage crossing returns `("exit", "E")` and does not clamp through `_X_MAX`. |
| REQ-033 | East sealed crossing clamps `x` to `_X_MAX` and emits no exit. |
| REQ-034 | Same clamp/exit behavior implemented for W/N/S. |
| REQ-035 | Horizontal-first branch order guarantees one deterministic transition per frame. |
| REQ-036 | `room=None` branch preserves T2 `(x, y)` return and clamp behavior for legacy callers/tests. |

## 9. Decisions

- **D4.1 — Preserve legacy mode instead of forcing all callers to pass a room.**
  Keeps T2 tests and helper usage stable while C06 performs integration.
- **D4.2 — Discriminated exit tuple `("exit", dir)` in room-aware mode.**
  Minimal payload; C06 remains the single owner of room swap/warp logic.
- **D4.3 — Horizontal-first edge evaluation.**
  Implements REQ-035 deterministically and simplifies adversarial tests.

## 10. Risks

- **R3 — Signature drift breaking legacy tests.** Mitigated by explicit
  `room=None` branch.
- **R5 — Dual-edge ambiguity in diagonals.** Mitigated by fixed axis priority.

## 11. Out of scope

- Warp math (`INWARD_OFFSET`, perpendicular clamping) — C05.
- Loop-level room mutation and render sequencing — C06.

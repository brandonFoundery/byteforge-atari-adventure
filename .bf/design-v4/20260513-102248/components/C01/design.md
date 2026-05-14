# C01 — RoomDataModelAndRegistry — Design

**Type:** data-model | **Epic:** EPIC-001 | **Story:** STORY-001-1
**Dependencies:** (none)
**Requirements covered:** REQ-001..REQ-008

## 1. Purpose

Introduce the `Room` data class and the module-level `ROOMS` registry to
`adventure.py`. This component is pure data — no behavior changes to the
game loop, rendering, or movement. After this lands, the module-level
public surface is extended but every existing T1/T2 test path still works.

## 2. Public symbols (added)

All declared at module top in `adventure.py`, **above** existing
`PLAYER_SPEED` so other functions/modules can import them without
re-ordering.

| Symbol | Kind | Type / Value |
|--------|------|--------------|
| `Room` | dataclass (frozen=True) | see § 3 |
| `ROOMS` | module constant | `dict[str, Room]` (4 entries) |
| `START_ROOM` | module constant | `str` = `"yellow"` |
| `ROOM_COLOR` | module constant | `tuple[int, int, int]` = `(240, 208, 64)` (preserved alias) |

## 3. Data structure

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Room:
    id: str
    bg_color: tuple[int, int, int]
    neighbors: dict[str, str | None]
```

Rationale for `frozen=True`:
- Rooms are authored constants; immutability prevents accidental mutation.
- Hashable by default (helps `BFS` sets in C02 if needed).
- Equality is structural (all fields) — sufficient for tests that compare
  `room == ROOMS["yellow"]`.

`neighbors` is a `dict[str, str | None]` keyed by the four cardinal
strings `"N" | "S" | "E" | "W"`. A value of `None` means **sealed**
(REQ-004); a value of a string means the id of the room reached by
crossing that edge (REQ-005).

NOTE: `frozen=True` does **not** make the inner `dict` immutable. Authors
must not mutate `room.neighbors` at runtime. Convention enforced by
inspection / validators in C02; no runtime guard added (out of scope per
input stub: rendering, validators are separate components).

## 4. Layout (authored adjacency)

A 2x2 grid:

```
     N
     |
W -- yellow -- E -- blue
     |               |
     S               S
     |               |
     green -- E -- purple
     |               |
     S               S
```

The 2x2 grid arrangement (REQ-005):

| Room   | N      | S      | E      | W      |
|--------|--------|--------|--------|--------|
| yellow | None   | green  | blue   | None   |
| blue   | None   | purple | None   | yellow |
| green  | yellow | None   | purple | None   |
| purple | blue   | None   | None   | green  |

This produces:
- 4 passage edges (yellow↔blue E/W; yellow↔green N/S; blue↔purple N/S;
  green↔purple E/W).
- 8 sealed edges (the outer perimeter of the 2x2).
- Bidirectional adjacency (symmetric — verifiable by C02
  `assert_symmetric`).
- BFS from `"yellow"` reaches all four ids (verifiable by C02
  `assert_connected`).

Palette (REQ-003):

| Room id | `bg_color`     |
|---------|----------------|
| yellow  | `(240, 208, 64)` |
| blue    | `(64, 96, 200)`  |
| green   | `(48, 160, 64)`  |
| purple  | `(144, 64, 176)` |

All four values are pairwise distinct (verifiable by static inspection /
tests in C06).

## 5. Module-level wiring

In `adventure.py`, the constant block immediately following the existing
window/color constants is extended:

```python
ROOM_COLOR = (240, 208, 64)   # gold-like castle room  (PRESERVED alias)
...

# --- T3 room registry --------------------------------------------------

START_ROOM = "yellow"

ROOMS: dict[str, Room] = {
    "yellow": Room(
        id="yellow",
        bg_color=(240, 208, 64),
        neighbors={"N": None, "S": "green", "E": "blue", "W": None},
    ),
    "blue": Room(
        id="blue",
        bg_color=(64, 96, 200),
        neighbors={"N": None, "S": "purple", "E": None, "W": "yellow"},
    ),
    "green": Room(
        id="green",
        bg_color=(48, 160, 64),
        neighbors={"N": "yellow", "S": None, "E": "purple", "W": None},
    ),
    "purple": Room(
        id="purple",
        bg_color=(144, 64, 176),
        neighbors={"N": "blue", "S": None, "E": None, "W": "green"},
    ),
}
```

The `Room` class definition lives in the same file (no new module). Per
shared-context `conventions.md`: keep `from __future__ import annotations`
and screaming-snake-case for module constants.

## 6. Back-compat invariants

- `ROOM_COLOR = (240, 208, 64)` stays at module top (REQ-007).
- `ROOMS["yellow"].bg_color == ROOM_COLOR` (REQ-006).
- No existing import paths change (`from adventure import ROOM_COLOR` still
  works; `adventure.ROOM_COLOR` still works).
- The existing single-arg `draw_room(surface)` is **not** touched in C01
  — C03 owns the signature change. After C01 lands but before C03 lands,
  the loop still calls `draw_room(logical_surface)` and tests pass.
- `move_player` is unchanged in C01 (C04 owns the change). C01 lands
  cleanly without touching `tests/test_movement.py`.

## 7. Integration with other components

| Consumer | What it reads from C01 |
|----------|------------------------|
| C02 (Validators) | Iterates `rooms` argument (will be passed `ROOMS` from `run_game_loop`); uses `room.neighbors` keys/values. |
| C03 (Rendering) | `room.bg_color` for `surface.fill`; `room.neighbors[dir]` to decide wall vs passage. |
| C04 (Movement) | `room.neighbors[dir]` to decide clamp vs exit. |
| C05 (Warp) | `room.neighbors[exit_dir]` to look up new room id; `ROOMS[new_id]` to dereference. |
| C06 (Loop) | `ROOMS[START_ROOM]` to seed function-local `current_room`. |

C01 itself imports nothing from later components.

## 8. Edge cases / constraints

- **No pygame import in C01.** The dataclass and the registry literal
  have no pygame dependency. `Room` is importable in a non-pygame test
  environment.
- **`neighbors` keys.** Authored as exactly `{N, S, E, W}` per entry.
  Validation is C02's job; C01 is responsible only for authoring the
  literal correctly.
- **No module-level mutation after import.** `ROOMS` is built once at
  import time. `frozen=True` blocks reassignment of `Room` fields.
- **`current_room` MUST NOT appear at module level.** C01 deliberately
  does not introduce a `current_room` module attribute (REQ-026). The
  loop seed is done in C06.
- **Determinism.** `dict` iteration order in Python 3.7+ is insertion
  order; tests that depend on iteration order (e.g. C02 BFS unreachable
  list) can rely on it. The authored insertion order is
  `yellow, blue, green, purple`.

## 9. REQ coverage matrix

| REQ | How satisfied |
|-----|---------------|
| REQ-001 | `Room` dataclass with `id`, `bg_color`, `neighbors`; importable from `adventure`. |
| REQ-002 | `ROOMS` has exactly 4 keys: `yellow`, `blue`, `green`, `purple`. |
| REQ-003 | Palette listed in § 4 with four distinct RGB tuples. |
| REQ-004 | Each `neighbors` dict has exactly `{N, S, E, W}` keys; values are existing room ids or `None`. |
| REQ-005 | Authored adjacency forms the 2x2 layout in § 4 (yellow–blue / green–purple). |
| REQ-006 | `START_ROOM = "yellow"`; `ROOMS[START_ROOM].bg_color == (240, 208, 64)`. |
| REQ-007 | `ROOM_COLOR = (240, 208, 64)` preserved at module top. |
| REQ-008 | Only additions; no signature changes; `tests/test_adventure.py` and `tests/test_movement.py` pass without modification. |

## 10. Key decisions (added to DECISION_LOG)

- **D1.1 — `@dataclass(frozen=True)`.** Prevents accidental mutation;
  preserves equality semantics; no runtime cost for static data. (See
  PATTERN_REGISTRY row 1.)
- **D1.2 — `neighbors` as plain `dict[str, str | None]`, not nested
  dataclasses.** Authored literally; flat tuple keys would lose clarity;
  named typed mapping would over-engineer four cardinal strings.
- **D1.3 — Insertion order `yellow, blue, green, purple` is canonical.**
  Future BFS / iteration tests may rely on it.
- **D1.4 — Do NOT validate at import time in C01.** Validators
  (`assert_symmetric`, `assert_connected`) exist as separate functions
  in C02 and are invoked by C06 once at registry-construction time. C01
  leaves the registry literal and trusts authors to write it correctly;
  C02 + C06 are the runtime guard.

## 11. Risks

- **R6 (asymmetric authoring).** Mitigated by C02 (validators) called in
  C06. C01 must not silently mask this — authors should run pytest after
  edits.
- **Hashing of `Room`.** `frozen=True` makes `Room` hashable, but
  `neighbors: dict` is not hashable — `hash(Room(...))` will raise. This
  is **fine** because C02 uses BFS keyed by `room.id` (string), not by
  `Room` object. Documented here to head off future code that tries
  `set[Room]`.

## 12. Out of scope

Validators (C02), rendering generalization (C03), movement (C04), warp
(C05), loop wiring (C06), `tests/test_rooms.py` (C06 owns the file).

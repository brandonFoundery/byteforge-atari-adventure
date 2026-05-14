# Decision Log

Inherited from elicit (`.bf/elicit-v4/20260513-102248/final/assembled.md`):

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | 4 rooms in 2x2 grid | Smallest set that exercises all four cardinal directions; matches assembled spec |
| 2 | Start room = `yellow` with `bg_color = (240,208,64)` | Matches legacy `ROOM_COLOR` so T1/T2 visuals are unchanged at boot |
| 3 | Sealed edge = `neighbors[dir] is None` | Single representation, less state than a separate `walls` set |
| 4 | `current_room` function-local | Eliminates cross-test module-global flakiness |
| 5 | Warp = mirror perpendicular coord + inward `PLAYER_SPEED + 1` | Prevents single-frame re-transition |
| 6 | Diagonal ties: horizontal axis wins | Deterministic, documented in `move_player` docstring |
| 7 | Silent transition (no flash/label) | Out of scope for T3 |
| 8 | Tests use `SDL_VIDEODRIVER=dummy` from `conftest.py` | Already wired by T1; no new deps |

Design-stage additions (this run):

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | Split EPIC-003 into C04 + C05 + C06 | Move/warp/loop have independently testable contracts |
| D2 | Validators (C02) separate from registry (C01) | Pure functions; testable without registry data |
| D3 | `tests/test_rooms.py` created in C06 (integration) | Earlier components contribute requirement coverage but file lands once with the wired loop |
| D1.1 | `Room` is `@dataclass(frozen=True)` | Immutability for static authored data; hashable; clean equality. |
| D1.2 | `neighbors` is `dict[str, str \| None]` (no nested dataclass) | Authored literally; over-engineering avoided for 4 cardinal strings. |
| D1.3 | Canonical room iteration order = insertion order: yellow, blue, green, purple | Determinism for BFS/test order; relied on by tests. |
| D1.4 | Validators NOT called at import in C01 | C01 stays pure data; C06 invokes validators once at registry construction. |
| D2.1 | Validators are module functions, not `Room` methods | Lets tests pass synthetic registries; `Room` stays a dumb dataclass. |
| D2.2 | `assert_connected` skips unknown ids silently | `assert_symmetric` is the authority on unknown ids; avoids double-reporting. C06 calls symmetric first. |
| D2.3 | Missing reciprocal key → treated as sealed (`.get` returns `None`) | Stable error message for asymmetric edges with absent keys. |
| D2.4 | `missing` rooms reported sorted in `assert_connected` error | Stable, asserttable test output. |
| D3.1 | Walls drawn per-edge after a single `surface.fill` | Mirrors T1 code style; simplest impl. |
| D3.2 | `room.neighbors.get(dir)` instead of `[dir]` in renderer | Defensive — malformed Room draws a wall (conservative) instead of crashing. |
| D3.3 | Pixel-sample rendering tests (recorder fallback documented) | Faithful real-rendering coverage; fallback only if headless `get_at` proves broken on a platform. |
| D3.4 | C03 does not yet wire transitions | T2 clamp still active in intermediate state until C06 lands; player can't cross passage edge yet, but passage walls visually absent. |
| D4.1 | `move_player` keeps `room=None` legacy branch | Preserves T2 call sites/tests while transition integration lands in C06. |
| D4.2 | Room-aware exits encoded as discriminated tuples `("exit", dir)` | Keeps room mutation centralized in C06 and simplifies transition branching. |
| D4.3 | Diagonal ties resolve horizontal-first | Deterministic single-transition behavior per frame (REQ-035). |
| D5.1 | `INWARD_OFFSET = PLAYER_SPEED + 1` | Geometry-based debounce prevents immediate re-transition without extra flags. |
| D5.2 | `_warp_position` raises `ValueError` on invalid exits | Explicit failure mode for malformed graph states; avoids silent corruption. |
| D6.1 | C06 runs validators at loop startup, not module import | Keeps import side-effects minimal and test harness predictable. |
| D6.2 | Movement clamp tests pass explicit sealed-room fixture | Preserves T2 invariants under room-aware semantics (REQ-048..052). |
| D6.3 | Transition tests split into unit + adversarial e2e suites | Faster deterministic math checks plus frame-sequence stress coverage. |

# C03 — RoomAwareRendering — Design

**Type:** frontend-component | **Epic:** EPIC-002
**Stories:** STORY-002-1, STORY-002-2, STORY-002-3
**Dependencies:** C01
**Requirements covered:** REQ-021..REQ-030

## 1. Purpose

Generalize the existing single-room renderer so a `Room` argument
controls background color and wall placement. Also seed
`current_room` as a function-local in `run_game_loop` (never as a
module global) and pass it to `draw_room` each frame.

## 2. Public surface change

| Symbol | Before | After |
|--------|--------|-------|
| `draw_room` | `draw_room(surface) -> None` | `draw_room(surface, room: Room) -> None` |

Hard signature change. The **only** caller in the production code is
`run_game_loop`, which is updated in the same change (see § 4). Tests
have never called `draw_room` directly (verified: not referenced by any
existing `tests/test_*.py`); the renderer is implicitly tested through
`run_game_loop`.

## 3. `draw_room(surface, room)` — design

### 3.1 Algorithm

```python
def draw_room(surface: pygame.Surface, room: Room) -> None:
    """Render the active room's background and walls.

    Walls are drawn ONLY on edges where room.neighbors[dir] is None
    (sealed). Passage edges show the bg color through.
    """
    surface.fill(room.bg_color)

    # Top (N)
    if room.neighbors.get("N") is None:
        pygame.draw.rect(
            surface, WALL_COLOR,
            pygame.Rect(0, 0, LOGICAL_WIDTH, WALL_THICKNESS),
        )
    # Bottom (S)
    if room.neighbors.get("S") is None:
        pygame.draw.rect(
            surface, WALL_COLOR,
            pygame.Rect(
                0, LOGICAL_HEIGHT - WALL_THICKNESS,
                LOGICAL_WIDTH, WALL_THICKNESS,
            ),
        )
    # Left (W)
    if room.neighbors.get("W") is None:
        pygame.draw.rect(
            surface, WALL_COLOR,
            pygame.Rect(0, 0, WALL_THICKNESS, LOGICAL_HEIGHT),
        )
    # Right (E)
    if room.neighbors.get("E") is None:
        pygame.draw.rect(
            surface, WALL_COLOR,
            pygame.Rect(
                LOGICAL_WIDTH - WALL_THICKNESS, 0,
                WALL_THICKNESS, LOGICAL_HEIGHT,
            ),
        )
```

### 3.2 Behavior notes

- `surface.fill(room.bg_color)` is called **unconditionally** first, so
  passage edges visibly show the bg-color "open gap" exactly the width
  of `WALL_THICKNESS` (REQ-022, REQ-024).
- Wall rectangles use the existing `WALL_COLOR` and `WALL_THICKNESS`
  constants. No new geometry constants introduced.
- Corner overlap behavior matches T1: when two adjacent edges are
  sealed, their wall rectangles overlap at the corner. Color is
  unchanged (both `WALL_COLOR`); no visual artifact.

### 3.3 Edge cases

| Case | Behavior |
|------|----------|
| Room with **all four** edges sealed | Identical to T1 rendering (4 walls drawn). |
| Room with **all four** edges open | No walls drawn; full surface is `room.bg_color`. (Allowed for tests; never produced by authored ROOMS.) |
| `room.bg_color` equals `WALL_COLOR` | Wall would be invisible. Acceptable; not a defect. Authored palette avoids this. |
| Missing key in `room.neighbors` | `.get(dir)` returns `None` → treated as sealed; conservative (wall drawn). This should never occur in practice; C02 catches authoring errors elsewhere. |

## 4. `run_game_loop` change (C03's portion)

This is **partial** wiring — full transition handling lands in C06. C03
introduces only the `current_room` function-local + the new
`draw_room(surface, room)` call.

### 4.1 Loop body diff (C03-only scope)

```python
def run_game_loop(surface, *, fps=TARGET_FPS, event_getter=pygame.event.get):
    clock = pygame.time.Clock()
    running = True
    logical_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
    current_room = ROOMS[START_ROOM]       # <-- NEW (function-local)
    px, py = PLAYER_X, PLAYER_Y

    while running:
        for event in event_getter():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        px, py = move_player(px, py, pygame.key.get_pressed())  # unchanged here

        draw_room(logical_surface, current_room)                # <-- CHANGED
        draw_player(logical_surface, px, py)

        if surface.get_size() == (LOGICAL_WIDTH, LOGICAL_HEIGHT):
            surface.blit(logical_surface, (0, 0))
        else:
            pygame.transform.scale(logical_surface, surface.get_size(), surface)
        pygame.display.flip()
        clock.tick(fps)
```

### 4.2 Why C03 doesn't yet wire transitions

C03's scope per the input stub is rendering + `current_room`
function-local. Movement-aware exits and warp wiring are owned by C04 +
C05 + C06. After C03 lands, `current_room` is read-only inside the loop
(no reassignment) — the player still clamps via the existing
`move_player` (T2 behavior). This is an acceptable intermediate state
because:

- The start room (`yellow`) has only **two** passage edges (E to blue,
  S to green). With T2 clamp behavior still active, the player simply
  clamps at the passage edge — visually identical to a wall. Tests that
  assert no transition happen in C03 are NOT added; transition tests
  land in C06 once the loop wires the warp.
- Wall rendering visibly removes the wall on passage edges. The player
  cannot cross because T2 clamps. Acceptable per input stub.

## 5. `current_room` discipline (function-local invariant)

The most important contract this component owns (REQ-026, REQ-030,
REQ-047):

- **MUST** be assigned only inside `run_game_loop` as a local variable.
- **MUST NOT** appear at module level. After any number of
  `run_game_loop` invocations, `hasattr(adventure, "current_room")` is
  `False`.
- **MUST NOT** be assigned via `globals()["current_room"] = ...` or
  attribute set on `adventure`.

Enforcement mechanisms:

1. Code review during implementation.
2. `test_no_module_global_current_room` in `tests/test_rooms.py` (lands
   in C06): `import adventure; assert not hasattr(adventure, "current_room")`.
3. Optional grep guard documented in conventions: a CI grep for
   `^current_room\s*=` in `adventure.py` outside of `def
   run_game_loop` body would catch regressions; not required for T3.

C06's reassignment of `current_room` on transition (REQ-044) also stays
function-local; C05's `_warp_position` returns a new room rather than
mutating module state.

## 6. Test coverage owned by C03 (lands in C06's `tests/test_rooms.py`)

C03 contributes 6 tests by **specification**; the file is created in
C06 (per DECISION D3), but these tests are owned conceptually by C03
and described here so the implementor knows the expected shapes.

### 6.1 `test_draw_room_uses_active_room_color` (REQ-023)

```python
def test_draw_room_uses_active_room_color():
    pygame.init()
    surface = pygame.Surface((adventure.LOGICAL_WIDTH, adventure.LOGICAL_HEIGHT))
    blue = adventure.ROOMS["blue"]
    adventure.draw_room(surface, blue)
    # Sample an interior pixel (away from walls). Center is safe.
    cx, cy = adventure.LOGICAL_WIDTH // 2, adventure.LOGICAL_HEIGHT // 2
    sampled = tuple(surface.get_at((cx, cy)))[:3]
    assert sampled == blue.bg_color
```

### 6.2 `test_draw_room_omits_wall_on_passage_edge` (REQ-024)

Pick a room where exactly one edge is passage and one is sealed. With
the authored registry, `yellow` (N sealed, S passage to green, E passage
to blue, W sealed) is ideal. Sample a pixel **inside** the wall band
near each edge:

```python
def test_draw_room_omits_wall_on_passage_edge():
    surface = pygame.Surface((adventure.LOGICAL_WIDTH, adventure.LOGICAL_HEIGHT))
    yellow = adventure.ROOMS["yellow"]
    adventure.draw_room(surface, yellow)
    half_w = adventure.LOGICAL_WIDTH // 2
    half_h = adventure.LOGICAL_HEIGHT // 2
    t = adventure.WALL_THICKNESS // 2

    # N sealed -> WALL_COLOR; S passage -> bg_color
    assert tuple(surface.get_at((half_w, t)))[:3] == adventure.WALL_COLOR
    assert tuple(surface.get_at((half_w, adventure.LOGICAL_HEIGHT - t - 1)))[:3] == yellow.bg_color
    # W sealed -> WALL_COLOR; E passage -> bg_color
    assert tuple(surface.get_at((t, half_h)))[:3] == adventure.WALL_COLOR
    assert tuple(surface.get_at((adventure.LOGICAL_WIDTH - t - 1, half_h)))[:3] == yellow.bg_color
```

### 6.3 `test_run_game_loop_uses_start_room_for_initial_frame` (REQ-027)

Run the loop with an event_getter that immediately fires ESC. Assert
the rendered `logical_surface`-equivalent center pixel matches
`ROOMS[START_ROOM].bg_color`. Implementation pattern reuses
`test_main_loop_exits_on_escape_event` from T1 and reads `surface` after
the loop exits.

### 6.4 `test_rendered_frame_matches_start_room_bg_color` (REQ-028)

Same as 6.3 but explicit assertion against tuple `(240, 208, 64)`. If
`pygame.Surface.get_at` returns surprising bytes on a headless platform
(documented risk R1), the test falls back to checking
`adventure.draw_room` was called with `ROOMS[START_ROOM]` by patching
`adventure.draw_room` with a recorder.

### 6.5 `test_rendered_frame_shows_walls_only_on_sealed_edges_of_start_room` (REQ-029)

Combines 6.2 and 6.4 against the live `run_game_loop` (not just direct
`draw_room` call). Sample the four wall-band pixels of the
post-loop-exit `logical_surface` and assert per-direction wall presence
matches the start room's authored `neighbors`.

### 6.6 `test_no_module_global_current_room` (REQ-030)

```python
def test_no_module_global_current_room():
    # Run the loop to completion at least once.
    adventure.run_game_loop(surface, event_getter=fake_esc_event_getter)
    assert not hasattr(adventure, "current_room")
```

The pre-run condition is also implicitly verified by `tests/test_adventure.py`
not seeing the attribute on import.

### 6.7 Headless fallback (R1)

If `pygame.Surface.get_at` returns alpha-incorrect or platform-specific
bytes on a CI headless run:

1. The slice `[:3]` (in §6.1 example) drops the alpha byte — first
   defence.
2. The pixel value tuple equality is the canonical assertion.
3. If equality still fails on a known-broken platform, the test
   downgrades to **recorder-based**: monkeypatch
   `adventure.surface.fill` and assert the call's first argument equals
   `room.bg_color`. The recorder-based variant is documented in the
   test docstring (REQ-028 mentions "documented fallback if needed").
   Decision: ship the pixel-sample version first; only fall back if a
   platform forces it.

## 7. Integration boundaries

| Boundary | Contract |
|----------|----------|
| `draw_room` ← `run_game_loop` | Caller passes a `Room`; receives `None`; surface has been mutated. |
| `draw_room` ← test | Same. Tests must pre-init pygame headless (handled by `conftest.py`). |
| `draw_room` → `WALL_COLOR`, `WALL_THICKNESS`, `LOGICAL_WIDTH`, `LOGICAL_HEIGHT` | Read-only references to existing module constants. |
| `draw_room` → `room.bg_color`, `room.neighbors` | Read-only access to dataclass fields. |

No new module constants. No new imports.

## 8. REQ coverage matrix

| REQ | How satisfied |
|-----|---------------|
| REQ-021 | `draw_room(surface, room)` fills with `room.bg_color`; `ROOM_COLOR` preserved as legacy alias (untouched by C03). |
| REQ-022 | Walls drawn per-edge only when `room.neighbors[dir] is None`. |
| REQ-023 | `test_draw_room_uses_active_room_color` samples center pixel of arbitrary room. |
| REQ-024 | `test_draw_room_omits_wall_on_passage_edge` samples wall-band of yellow's N/S/E/W. |
| REQ-025 | Function-local `current_room = ROOMS[START_ROOM]` in `run_game_loop`; passed to every `draw_room` call. |
| REQ-026 | `current_room` is never assigned to module; verified by REQ-030 test. |
| REQ-027 | `test_run_game_loop_uses_start_room_for_initial_frame` — single-frame ESC loop, center pixel assertion. |
| REQ-028 | `test_rendered_frame_matches_start_room_bg_color` — explicit RGB tuple match; documented recorder-based fallback. |
| REQ-029 | `test_rendered_frame_shows_walls_only_on_sealed_edges_of_start_room` — four wall-band samples. |
| REQ-030 | `test_no_module_global_current_room`. |

## 9. Decisions

- **D3.1 — Wall rectangles are drawn per-edge after a single
  `surface.fill`.** Simpler than computing a wall mask; matches existing
  T1 code style.
- **D3.2 — `.get(dir)` instead of `[dir]` indexing.** Defensive: a
  malformed `Room` (missing key) draws a wall (conservative) instead of
  crashing the renderer. C02 catches the actual authoring bug at loop
  start.
- **D3.3 — Pixel-sample tests over mock-based tests.** Faithful to
  real rendering; R1 fallback documented but not pre-emptively used.
- **D3.4 — C03 does not call `_warp_position`.** Even though
  `current_room` becomes a local, transition handling is C06's job.
  C03 leaves the existing `move_player` call unchanged and the loop
  still uses T2 clamp behavior.

## 10. Risks

- **R1 — `Surface.get_at` headless.** Mitigated by `[:3]` slicing and
  documented recorder-based fallback.
- **R2 — `current_room` module-global leak.** Mitigated by REQ-030 test
  + code review.
- **R7 — T1/T2 regression.** `draw_room` signature change is the only
  cross-cutting change; the sole caller is updated in the same change.
  `tests/test_adventure.py` and `tests/test_movement.py` don't call
  `draw_room` directly — they stay green.

## 11. Out of scope

- Transition logic (C04 owns `move_player(room=...)`; C05 owns
  `_warp_position`; C06 wires both into the loop).
- `tests/test_rooms.py` file creation (lands in C06).
- Per-room interior wall patterns (future ticket).

# STORY-002-3: Verify rendered frame reflects the active room (pixel-level integration test)

## Parent Epic
EPIC-002 — Room-aware rendering + active room state

## User Story
As a QA owner verifying that EPIC-002 actually closes its success criterion,
I need a headless integration test that drives `run_game_loop` for one frame
and confirms — via pixel sampling on the rendered surface — that the frame
buffer contains the active room's `bg_color` and its sealed-wall layout, so
that we have an automated, regression-proof guarantee that "rendered frame
reflects the active room" beyond unit-level coverage of `draw_room`.

## Context
STORY-002-1 verifies `draw_room` in isolation. STORY-002-2 verifies
`current_room` is wired as a local. This story verifies the *integration* —
that the live frame buffer produced by `run_game_loop` for one tick, under
the headless `SDL_VIDEODRIVER=dummy` test fixture, contains the expected
pixels for the starting room.

This addresses two risks from impact.md:
1. "Headless tests can't observe color difference per room" — proves
   `pygame.Surface.get_at()` works under the dummy driver, OR forces a
   fallback strategy if it doesn't.
2. "Missing T3 acceptance criteria — which 4 vs 6 rooms?" — by sampling the
   *actual* starting room from the registry (not a fixed expected color),
   the test stays valid regardless of which color EPIC-001 picks.

## Touch Surface
- `tests/test_rooms.py` — add an integration test that boots the loop for
  one frame.
- `tests/conftest.py` — no change; existing headless SDL fixture is
  inherited.
- No production-code changes; this story is verification-only on top of
  STORY-002-1 and STORY-002-2.

## Acceptance Criteria

- **REQ-028**: A new integration test in `tests/test_rooms.py`
  (`test_rendered_frame_matches_start_room_bg_color`) initializes pygame
  headlessly, runs `run_game_loop` for exactly one frame (via the existing
  `max_frames` test hook used in `tests/test_adventure.py`), then asserts
  that `surface.get_at((LOGICAL_WIDTH // 2, LOGICAL_HEIGHT // 2))` returns
  an RGB triple equal to `START_ROOM.bg_color` (alpha channel ignored).
  Must pass under the existing `SDL_VIDEODRIVER=dummy` fixture; if
  `surface.get_at()` proves unreliable under the dummy driver, the test
  uses a documented `screen.blit`-target-surface workaround (NOT removed).
- **REQ-029**: A new integration test
  (`test_rendered_frame_shows_walls_only_on_sealed_edges_of_start_room`)
  runs one frame of `run_game_loop` and, for each of the four cardinal
  edges, samples a pixel one pixel *inside* `WALL_THICKNESS` from the
  edge. The pixel must equal `WALL_COLOR` when `START_ROOM.neighbors[dir]`
  is `None`, and must equal `START_ROOM.bg_color` when
  `START_ROOM.neighbors[dir]` is a Room reference.
- **REQ-030**: A regression check (`test_no_module_global_current_room`)
  asserts `not hasattr(adventure, "current_room")` to enforce REQ-026
  from STORY-002-2 over time and prevent a future refactor from silently
  re-introducing a module global. The full `pytest` run remains green
  after this story (pre-existing `tests/test_adventure.py`,
  `tests/test_movement.py`, and the adversarial suites under
  `tests/e2e/adversarial/` all continue to pass).

## Non-Goals
- Do not test edge-crossing (EPIC-003) or transitions.
- Do not test color uniqueness across rooms — that is EPIC-001's
  acceptance (room registry invariants).
- Do not add screenshots / image-snapshot infrastructure. Pixel sampling
  via `Surface.get_at()` is sufficient.

## Verification
- `pytest tests/test_rooms.py -k rendered_frame` passes.
- `pytest` full run is green.
- Manual: `python adventure.py` continues to launch and play identically
  to STORY-002-2's manual check (this story adds NO runtime behavior).

## Open Questions
- Whether `pygame.Surface.get_at()` returns deterministic RGB under
  `SDL_VIDEODRIVER=dummy` on the CI runner. TBD until first run; fallback
  strategy is documented in REQ-028.

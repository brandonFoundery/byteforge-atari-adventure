# STORY-003-6: Add `tests/e2e/adversarial/test_rooms_adversarial.py`

## Parent

EPIC-003 — Edge transitions + room-aware movement

## User Story

As the maintainer, I need adversarial E2E coverage of transition behavior
under stress — diagonal exits at corners, rapid alternating key presses at
an edge, and full-graph traversal driven through `run_game_loop` — so that
edge-case interactions between input, movement, and transitions cannot
silently break.

## Scope

- File: `tests/e2e/adversarial/test_rooms_adversarial.py` (NEW).
- Drives `run_game_loop` with stubbed `event_getter` and stubbed key-state
  providers (matching the SDL1/SDL2 dual support in `_is_pressed`) so the
  loop runs headlessly under `SDL_VIDEODRIVER=dummy`.
- Verifies behavior end-to-end (loop → move → transition → render),
  complementing the pure unit tests in STORY-003-5.

## Technical Notes

- Reuse the patterns already established in
  `tests/e2e/adversarial/test_movement_adversarial.py` and
  `tests/e2e/adversarial/test_adventure_adversarial.py`.
- For rapid alternating-direction scenarios, drive the loop with a
  scripted key-state sequence (frame 1: right, frame 2: left, frame 3:
  right, …) and verify `current_room` changes match the expected pattern
  (i.e., no thrash from a stuck transition).
- Use `pygame.Surface.get_at()` on the logical surface to verify the
  rendered background color matches the expected room after traversal —
  this validates the integration of EPIC-002 rendering with EPIC-003
  transitions.

## Acceptance Criteria

- **REQ-059**: A test holds both right and down arrows for one frame at a
  corner where the east edge is a passage and the south edge is sealed,
  and asserts the player transitions east (per the documented diagonal
  priority from REQ-035) while the south coordinate clamps.
- **REQ-060**: A test scripts alternating left/right inputs across an
  east-passage edge for at least 10 frames and asserts that
  `current_room` toggles between exactly two rooms without skipping a
  third room or freezing.
- **REQ-061**: A test traverses every room in the registry via scripted
  input, asserting that after the scripted route `current_room` equals
  the expected terminal room and that the logical surface's background
  pixel equals that room's `bg_color`.
- **REQ-062**: A test asserts that holding a single direction toward a
  passage edge for 60 frames results in exactly one transition during
  that window (the inward offset prevents accidental multi-room skipping
  on a single hold).
- **REQ-063**: The new adversarial file passes under `pytest` headlessly
  using the existing `conftest.py` fixtures, with no new dependencies.

## Out of Scope

- Unit-level mirror-math tests (STORY-003-5).
- Reconciling pre-existing `test_movement_adversarial.py` clamp
  assertions — that work belongs in STORY-003-4's umbrella (movement
  reconciliation) and should be flagged there if any pre-existing
  adversarial clamp assertion conflicts with the new semantics.

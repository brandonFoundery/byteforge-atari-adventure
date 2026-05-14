# STORY-002-2: Thread `current_room` as a function-local through `run_game_loop`

## Parent Epic
EPIC-002 — Room-aware rendering + active room state

## User Story
As the game's frame loop, I need to own a `current_room` variable as a
function-local inside `run_game_loop` — initialized from the registry's
designated `START_ROOM` and passed explicitly to `draw_room` each frame — so
that active-room state is parameterized (not a module global), preventing
cross-test state leakage and matching the existing functional style of T1/T2.

## Context
`adventure.py::run_game_loop` (lines 100-129) today maintains only `px, py` as
loop-local state. EPIC-002 adds a third piece of state, `current_room`, that
selects which Room is rendered each frame. The location.md and impact.md
explicitly call out that this state must NOT be a module-level global (risk:
flaky tests via cross-interpreter state leak; convention: T1/T2 use
function-local state).

EPIC-003 will later mutate `current_room` inside the loop to swap rooms after
edge crossings. EPIC-002 leaves it constant for the lifetime of the loop —
it's `START_ROOM` from the first frame to the last.

## Touch Surface
- `adventure.py::run_game_loop` (lines 100-129) — add `current_room` local;
  pass to `draw_room`.
- `adventure.py` — import / reference `START_ROOM` and the registry produced
  by EPIC-001 (likely a `ROOMS` dict + a `START_ROOM` constant or a
  `get_start_room()` accessor; exact symbol comes from EPIC-001).
- No new module-level state.

## Acceptance Criteria

- **REQ-025**: `run_game_loop` declares a function-local `current_room`
  initialized from the registry's designated starting room exposed by EPIC-001
  (e.g., `START_ROOM` or `get_start_room()`) before the `while running:` loop
  body, and passes it to `draw_room` each frame (updating the existing call
  site at adventure.py line 121). `run_game_loop`'s public signature is
  unchanged (callable from `tests/test_adventure.py` and `main()` with the
  same arguments).
- **REQ-026**: `current_room` exists only as a function-local inside
  `run_game_loop` — there is no module-scope `current_room` binding, no
  `global current_room` statement anywhere in `adventure.py`, and
  `hasattr(adventure, "current_room")` returns False after import. Running
  the loop twice in the same Python process re-initializes `current_room` to
  `START_ROOM` on each invocation (no cross-invocation state leak).
- **REQ-027**: A new unit test
  (`test_run_game_loop_uses_start_room_for_initial_frame`) drives one frame
  of `run_game_loop` (via the existing `max_frames=1` style fixture from
  `tests/test_adventure.py`) and asserts via `surface.get_at()` at an
  interior pixel that the rendered color equals `START_ROOM.bg_color`.
  Existing `tests/test_adventure.py` tests continue to pass without
  modification.

## Non-Goals
- Do not mutate `current_room` inside the loop. It stays equal to
  `START_ROOM` for the entire loop lifetime in EPIC-002. (EPIC-003 will add
  mutation.)
- Do not change `move_player`. Movement clamping is identical to T2.
- Do not introduce a Game class. Convention is functional / module-level
  per location.md "codebase convention to date (T1/T2) is functional".

## Verification
- `pytest tests/test_rooms.py -k current_room` passes.
- `pytest tests/test_adventure.py tests/test_movement.py` continues to pass.
- Manual: `python adventure.py` runs and renders the starting room
  indefinitely until the window closes.

## Open Questions
- The exact name of EPIC-001's starting-room accessor (`START_ROOM` constant
  vs. `get_start_room()` function vs. `ROOMS["start"]`) is TBD — defer to
  EPIC-001's chosen API.

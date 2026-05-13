# Impact Assessment

## Blast Radius Summary

- **Direct changes (this PR will modify):**
  - `adventure.py` — single application module. Surface to be touched:
    - **Constants block (lines 7-33):** add `ITEM_SIZE`, `CHALICE_COLOR`, `KEY_COLOR`, `SWORD_COLOR`, three world spawn positions, drop key code (likely `pygame.K_SPACE`), and possibly an SDL1 alias if drop is a held key.
    - **New top-level state / data structures:** world-item list (3 entries with position + color + id), carried-item slot (None or item id).
    - **New helpers:** `draw_items(surface, world_items, carried_item, player_x, player_y)` (or per-item draws), `check_pickup(player_rect, world_items, carried_item) -> updated state`, `drop_item(carried_item, player_x, player_y, world_items) -> updated state`.
    - **`run_game_loop` (lines 100-129):** insert four touch points — (a) state init alongside `px, py = PLAYER_X, PLAYER_Y` (line 110), (b) KEYDOWN drop-key branch in event loop (lines 113-117), (c) pickup collision check after `move_player` (line 119), (d) item draws between `draw_room` (121) and `draw_player` (122) so player renders on top of items.
  - `tests/test_items.py` (new) — unit tests for pickup, carry-one, drop semantics, spawn-position bounds.
  - `tests/e2e/adversarial/test_items_adversarial.py` (new) — adversarial coverage following the `TestInitialization` / `TestGameLoopLogic` / `TestRenderFoundation` / `TestEdgeCases` class structure used in `test_adventure_adversarial.py`.
  - `.bf-feature/t4-items-*/` (new) — diamond/elicit/design/task artifact tree (workflow scaffolding, not application code).

- **Downstream consumers (could break if invariants change):**
  - `tests/test_adventure.py` — `test_player_position_is_expected` (asserts `PLAYER_X/Y` are room center) and `test_main_loop_exits_on_escape_event` (drives `run_game_loop` via fake event getter). Both will continue to pass **only if** T4 (a) does not change `PLAYER_X/Y`, and (b) does not change the ESC-quit path or the event-loop signature. evidence: `Read(tests/test_adventure.py)` lines 19-23, 26-46.
  - `tests/test_movement.py` — derives `X_MIN/X_MAX/Y_MIN/Y_MAX` from production constants and asserts `move_player` return-value contract. Pickup/drop must **not** alter `move_player`'s signature or return shape (still `(x, y)`); pickup must be performed by a **separate** call after `move_player`. evidence: `Read(tests/test_movement.py)` lines 8-12, 39-86.
  - `tests/e2e/adversarial/test_adventure_adversarial.py` — three tests (`test_run_game_loop_blits_to_unscaled_surface` ~ line 313, `test_run_game_loop_renders_to_scaled_surface` ~ line 347, `test_logical_surface_pixel_content_after_one_quit_frame` ~ line 481) sample the **center pixel** of the rendered surface and assert it is either `ROOM_COLOR` or `PLAYER_COLOR`. **If any T4 item spawns at or near room center, these tests will fail.** Additionally `test_draw_room_interior_is_not_wall_color` (line 283) samples `(WALL_THICKNESS+1, WALL_THICKNESS+1)` = `(9, 9)` and asserts ROOM_COLOR — items placed at that pixel would also fail it. evidence: `Grep(get_at, test_adventure_adversarial.py)` lines 235, 246, 257, 267, 278, 289, 307, 327, 360, 397, 408, 497.
  - `tests/e2e/adversarial/test_movement_adversarial.py` — sibling adversarial movement suite; only at risk if `move_player` signature or `_is_pressed` semantics change. evidence: `Grep(move_player|_is_pressed)` returned this file as a consumer.
  - `tests/conftest.py` — provides headless SDL fixture; no change required, but new tests must inherit it (place under `tests/` so `pytest` autodiscovers it). evidence: `Read(tests/conftest.py)` confirmed in locator.

- **Not consumers (verified, not at risk):**
  - No other application source modules exist. `Glob(**/*.py)` returned exactly one application file (`adventure.py`) plus tests and `.bf-feature/**` archived workflow scripts. evidence: locator §Evidence.
  - `.bf-feature/t1-*/task/batches/*/tests/*.py` and `.bf-feature/t2-*/task/batches/*/tests/*.py` are **archived** historical artifacts under workflow scaffolding directories, not part of the live test run (`pytest` is invoked from `tests/`, per `tests/conftest.py` adding project root to `sys.path`). evidence: `Grep(move_player)` matches in `.bf-feature/` are inside batch artifact trees, not the live test path.

## Risks

| Risk | Likelihood | Severity | Notes |
|------|:----------:|:--------:|-------|
| Item spawn at room center collides with adversarial center-pixel assertions (`test_run_game_loop_blits_to_unscaled_surface`, `test_run_game_loop_renders_to_scaled_surface`, `test_logical_surface_pixel_content_after_one_quit_frame`) | H | M | Tests sample `(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2)` = `(80, 105)` and accept only `ROOM_COLOR` or `PLAYER_COLOR`. Player default spawn `(76, 101)` covers `(76..83, 101..108)` which **does** include `(80, 105)` — so the player already covers center and item placements there would be hidden by the player anyway. Mitigation: place items away from center AND away from `(9, 9)` corner; or expand the adversarial assertion's accepted colors set. evidence: `Grep(get_at, test_adventure_adversarial.py)`. |
| Item draw ordering reversed (player rendered under item) causes adversarial player-pixel assertion to fail | M | M | `test_draw_player_paints_player_color_at_default_position` (~line 300) and `test_run_game_loop_blits_to_unscaled_surface` accept `PLAYER_COLOR` at player default origin. If items are drawn **after** player, an item overlapping the default spawn would paint over player. Mitigation: enforce `draw_room` → `draw_items(world)` → `draw_player` → `draw_carried_item(at player pos)` order, and assert this order in a new test. evidence: locator §Primary Locations bullet 4. |
| Carried-item rendering at player position obscures `PLAYER_COLOR` at `(PLAYER_X, PLAYER_Y)` and breaks `test_draw_player_paints_player_color_at_default_position` | M | M | If carried item is drawn on top of the player at the same pixel, the player-color assertion fails. Mitigation: render carried item with a 1-pixel offset (above or beside player) OR draw carried item **before** player so player overpaints it OR document that carried item appears at adjacent pixel. The classic Atari Adventure carries items in front of the player — offset is the canonical choice. evidence: `Grep(get_at, test_adventure_adversarial.py)` line 307. |
| Drop-key choice collides with existing input — ESC quits, arrows move | L | M | `pygame.K_SPACE` is unbound today and is the natural choice. `pygame.K_RETURN` also free. Must not pick a key the OS / pygame consumes (e.g., F11 fullscreen, Alt+F4). evidence: `Grep(K_)` against `adventure.py` shows only `K_ESCAPE`, `K_LEFT/RIGHT/UP/DOWN` used. |
| Pickup AABB collision logic miscounts overlap (off-by-one) → item picked up before visual touch, or item never picked up | M | M | Player rect is `PLAYER_SIZE × PLAYER_SIZE` from `(px, py)`. Item rect is `ITEM_SIZE × ITEM_SIZE`. AABB: `px < ix + ITEM_SIZE and px + PLAYER_SIZE > ix and py < iy + ITEM_SIZE and py + PLAYER_SIZE > iy`. Edge condition: when `PLAYER_SPEED=2`, the player can jump over a 1-pixel gap; if `ITEM_SIZE < PLAYER_SPEED`, item may be straddled without touching. Mitigation: choose `ITEM_SIZE >= PLAYER_SIZE` (e.g., 8) and add adversarial tests for tangent contact and one-pixel separation. evidence: `Read(adventure.py)` lines 16, 21 — `PLAYER_SIZE=8`, `PLAYER_SPEED=2`. |
| Carry-one rule undefined for second-touch (swap / block / ignore) leads to inconsistent behavior across review iterations | H | L | Request does not specify; locator's Discrepancy §3 flags this. Pick at design time; default recommendation: ignore second touch (classic Adventure). Adversarial test must encode the chosen rule explicitly. evidence: location.md §Discrepancies bullet 3. |
| Drop position lands inside a wall or off-screen (e.g., player against right wall, drop spawns item right of player → clamped outside `_X_MAX + ITEM_SIZE`) | M | M | `_X_MAX = LOGICAL_WIDTH - WALL_THICKNESS - PLAYER_SIZE = 144`. Dropping at `(px, py)` keeps the item inside playfield only if `ITEM_SIZE <= PLAYER_SIZE`. Mitigation: drop at exactly the player's current `(px, py)` and clamp item position via the same `_X_MIN.._X_MAX`/`_Y_MIN.._Y_MAX` math as `move_player`. Adversarial test: drop while clamped against each wall, assert item fully inside playfield. evidence: `Read(adventure.py)` lines 23-26. |
| Drop on a frame when player is standing on top of another world item → instant re-pickup loop | M | M | Drop sets carried = None; same-frame pickup check would re-pick the dropped item. Mitigation: skip pickup check on the frame a drop occurred, OR drop with 1px offset behind movement direction, OR require the player to move off the dropped item before re-pickup is enabled. Adversarial test: drop while standing on a different world item; assert carried is now that other item OR carried is None depending on chosen rule. evidence: locator §Boundaries. |
| Held-drop-key vs KEYDOWN-edge decision changes test fixture shape — held-key tests need `_is_pressed` dict idiom, edge tests need `pygame.event.Event` injection | M | L | Locator flags this (Primary Location bullet 6). `move_player` already uses `_is_pressed` polling. ESC uses event-loop edge detection. Either is feasible; design must pin one. If held, an SDL1 numeric alias for the drop key must be added. evidence: location.md §Primary Locations bullet 6. |
| pygame.K_SPACE numeric value differs between SDL1 and SDL2 → `_is_pressed` SDL1 fixture path silently fails on held-drop tests | L | L | SDL1 `SDLK_SPACE = 32`; SDL2 `K_SPACE = 32` (same in pygame builds). Lower risk than arrow keys, but must verify with `pygame.K_SPACE` constant value before adding numeric SDL1 alias. evidence: `Read(adventure.py)` lines 28-33 establish the alias pattern. |
| State leakage between tests because module-level world-item list is mutated by `run_game_loop` | M | M | If items are stored in a module-level list, repeated `run_game_loop` invocations in tests would see drained state. Mitigation: instantiate item state **inside** `run_game_loop` (mirroring `px, py = PLAYER_X, PLAYER_Y` at line 110), exposing a `reset_world_items()` or factory function for tests. evidence: `Read(adventure.py)` lines 100-111. |
| Pixel-color tests for new items would fail under pygame's antialiased rect rendering (none expected, but possible if helper is mis-used) | L | L | `pygame.draw.rect` is non-antialiased; existing wall/player tests rely on this. New `draw_items` must use `pygame.draw.rect` (same primitive). evidence: `Read(adventure.py)` lines 81-91, 97. |
| Performance: per-frame iteration over a 3-item list inside `run_game_loop` at 30 FPS is trivial; no impact | L | L | 3 AABB checks per frame is negligible. evidence: `Read(adventure.py)` line 103 (`TARGET_FPS=30`). |
| Backward compatibility: existing T1 / T2 tests already encode `PLAYER_X/Y`, `PLAYER_SIZE`, `WALL_THICKNESS`, `LOGICAL_WIDTH/HEIGHT` from production constants; T4 must not redefine or shadow any of these | L | H | Renaming or rebinding any of these constants would silently break ~15 existing tests. Mitigation: only **add** new constants; never modify existing ones. evidence: `Grep(_X_MIN\|PLAYER_SIZE\|WALL_THICKNESS)` returned `tests/test_movement.py`, `tests/test_adventure.py`, both adversarial files. |

## Mitigations / Verification

- **Required automated tests:**
  - `tests/test_items.py` (new) — pure-Python unit tests:
    - `test_world_items_initially_three_items` (count and ids)
    - `test_world_item_positions_in_bounds` (each item's rect ⊆ `[_X_MIN.._X_MAX] × [_Y_MIN.._Y_MAX]`)
    - `test_no_world_item_at_player_default_position` (no overlap with `PLAYER_X..PLAYER_X+PLAYER_SIZE` × `PLAYER_Y..PLAYER_Y+PLAYER_SIZE`)
    - `test_pickup_on_overlap_removes_item_from_world_and_sets_carried`
    - `test_pickup_when_already_carrying_does_nothing` (or swap, per design)
    - `test_drop_when_carrying_places_item_at_player_position_and_clears_carried`
    - `test_drop_when_not_carrying_is_noop`
    - `test_drop_clamps_inside_playfield_against_each_wall` (4 cases)
    - `test_pickup_aabb_tangent_does_not_pick_up` (edge separating by 0 pixels)
    - `test_drop_then_immediate_pickup_does_not_loop` (per chosen anti-loop rule)
  - `tests/e2e/adversarial/test_items_adversarial.py` (new) — mirroring `test_adventure_adversarial.py` class layout:
    - `TestItemInitialization`: counts, distinct positions, no overlap with walls or player spawn
    - `TestItemGameLoopLogic`: pickup on touch during a single `run_game_loop` frame; drop key triggers state change; ESC still quits after pickup
    - `TestItemRenderFoundation`: each item's color appears at its spawn pixel after one render frame; carried item appears at/near player position after pickup; world item disappears from its prior location after pickup
    - `TestItemEdgeCases`: drop against each wall stays in-bounds; pickup of item adjacent to a wall; pickup with `PLAYER_SPEED` jump over a 1-pixel gap (chosen sizes prevent this)
  - **Regression: re-run existing suites** — `tests/test_adventure.py`, `tests/test_movement.py`, `tests/e2e/adversarial/test_adventure_adversarial.py`, `tests/e2e/adversarial/test_movement_adversarial.py` must all pass unmodified. **Special attention to `test_draw_room_interior_is_not_wall_color` and the three `(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2)` center-pixel assertions** — item positions must be chosen so neither pixel `(9, 9)` nor pixel `(80, 105)` is overpainted by a world item.

- **Manual verification:**
  1. `SDL_VIDEODRIVER=dummy pytest tests/ -v` — all pre-existing tests green.
  2. `SDL_VIDEODRIVER=dummy pytest tests/test_items.py tests/e2e/adversarial/test_items_adversarial.py -v` — all new tests green.
  3. `python adventure.py` (with display) — walk to each item, observe pickup; press drop key, observe item appears at player position; walk over second item while carrying first, observe configured behavior (ignore / swap); ESC still exits.
  4. Visual: confirm each item is its own color, items render below player, dropped item stays where placed, no item visually overlaps walls.

- **Rollout:**
  - Single PR. No feature flag (the project has no flag system; this is a from-scratch single-file game). Merge to `main` after green CI and manual playthrough.
  - Sequenced after T3 if T3 is in flight (none indicated by repo state); otherwise immediate.

- **Rollback:**
  - `git revert <T4 merge commit>` restores the pre-T4 `adventure.py` and removes `tests/test_items.py` + `tests/e2e/adversarial/test_items_adversarial.py`. T1 + T2 functionality is untouched by any T4 code paths (T4 only adds; the only edits are insertion points inside `run_game_loop`).
  - No data, no persistence, no migrations — revert is fully sufficient.
  - If a partial regression sneaks past CI (e.g., a center-pixel test starts failing intermittently), the smallest fix is to relocate the offending item spawn position constant in `adventure.py` and re-run.

## Unknowns / Missing Info

- Drop key code — question: is `pygame.K_SPACE` acceptable, or does the user want `K_RETURN`, `K_LCTRL`, or another?
- Held-key vs KEYDOWN-edge for drop — question: does the user want the drop to fire once per press (KEYDOWN, classic) or fire continuously while held (which would spam-drop and immediately re-pick)? Recommend KEYDOWN edge; needs confirmation.
- Carry-one second-touch rule — question: ignore second touch, swap with carried, or block movement on contact? Locator's Discrepancy §3 already flags this; design must pin it.
- Drop-then-immediate-pickup rule — question: should the player have to step off the dropped item before re-pickup is allowed, or is same-frame re-pickup acceptable (effectively a no-op)? Affects test `test_drop_then_immediate_pickup_does_not_loop`.
- Item spawn positions — question: where should the chalice, key, and sword spawn? Must avoid `(80, 105)` and `(9, 9)` to keep existing adversarial pixel tests green. Recommend three positions like `(24, 32)` (key), `(120, 32)` (sword), `(72, 168)` (chalice) — each fully inside the playfield and far from sampled test pixels.
- Item sizes and colors — question: confirm `ITEM_SIZE = 8` (matches PLAYER_SIZE) and specific RGB triples for chalice/key/sword (recommend chalice=purple `(160, 32, 200)`, key=yellow `(240, 224, 32)`, sword=cyan `(96, 224, 240)` — all distinct from `PLAYER_COLOR`, `WALL_COLOR`, `ROOM_COLOR`).
- Carried-item render style — question: render the carried item as an overlay sprite offset 1px above the player, replace the player sprite while carrying, or render below the player? Affects test `test_draw_player_paints_player_color_at_default_position` if the carried item overpaints player pixels.
- Triptych architecture map — question: was skipping correct? location.md §Discrepancies §5 documents the explicit decision: tiny single-file Python repo, no controllers/services/components, Triptych's map is calibrated for C#/TS multi-tier projects. This impact assessment inherits that decision and uses filesystem + Grep for consumer expansion. If the scorer wants Triptych evidence, the answer is "n/a — out-of-fit for this repo."

## Evidence (Triptych)

Triptych queries are **out-of-fit** for this repo (one Python file, ~146 LOC, no multi-tier architecture). Per location.md §Discrepancies §5, the locator deliberately did not invoke `mcp__triptych__get_architecture_map`. Impact analysis uses filesystem-grounded consumer discovery via `Grep` over the live test directory, which is the correct tool for this project shape.

Filesystem-grounded evidence (same conventions as locator):

- `adventure.run_game_loop` → calls `move_player` (line 119), `draw_room` (121), `draw_player` (122) via `Read(adventure.py, lines 100-129)`. T4 insertion points are bounded by these three call sites.
- `adventure.move_player` consumers: `run_game_loop` line 119 (production), `tests/test_movement.py` lines 39-86 (10 tests), `tests/e2e/adversarial/test_movement_adversarial.py` via `Grep(move_player) -> files_with_matches` returning these two files (live) plus archived `.bf-feature/**/batches/**` (not live).
- `adventure.draw_player` consumers: `run_game_loop` line 122 (production), `tests/e2e/adversarial/test_adventure_adversarial.py` lines 295, 300, 393, 402 via `Grep(draw_player)`. **No T4 changes to `draw_player` signature** ⇒ these consumers are safe.
- `adventure.draw_room` consumers: `run_game_loop` line 121 (production), `tests/e2e/adversarial/test_adventure_adversarial.py` lines 224, 229, 240, 251, 262, 272, 283 via `Grep(draw_room)`. **No T4 changes to `draw_room`** ⇒ these consumers are safe.
- `adventure.PLAYER_X / PLAYER_Y / PLAYER_SIZE / WALL_THICKNESS / LOGICAL_WIDTH / LOGICAL_HEIGHT / _X_MIN / _X_MAX / _Y_MIN / _Y_MAX` consumers: 4 live test files via `Grep(_X_MIN|...) -> files_with_matches`. **No T4 redefinition of any of these** ⇒ regression-safe by construction.
- Center-pixel and corner-pixel adversarial assertions via `Grep(get_at, test_adventure_adversarial.py)`: lines 235 (center), 246 (top wall), 257 (bottom wall), 267 (left wall), 278 (right wall), 289 (corner interior `(9, 9)`), 307 (player default origin), 327 (center after one quit frame), 360 (center scaled), 397 (origin draw_player), 408 (far-corner draw_player), 497 (center one-frame). **Sampled fixed pixels: `(80, 105)` center and `(9, 9)` corner.** Item spawn constants must avoid both.
- Archived `.bf-feature/t1-*/` and `.bf-feature/t2-*/` directories returned by `Grep(move_player)` are workflow artifact trees, not live tests — confirmed by inspecting `tests/conftest.py` which only adds the project root to `sys.path` for live tests under `tests/`.
- No application-side consumers of T4 internals exist: `Glob("**/*.py")` returned exactly one application module (`adventure.py`). T4 is additive and self-contained at the module level.

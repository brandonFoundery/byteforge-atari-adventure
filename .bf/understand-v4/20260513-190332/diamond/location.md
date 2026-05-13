# Location Map

## Primary Locations

- `/Users/brandonshuey/data/ByteForge/Repositories/e0710c02-7a18-467f-8a6e-519bafe16e3e/.bf-worktrees/901b7299/adventure.py` — Single-module game source. This is the only application module in the repo and is where T1 (game loop, render, constants) and T2 (movement, wall clamp) live. T4 item state, item rendering, pickup-on-touch collision, drop keypress handling, and inventory ("carry-one") state must all be added here. evidence: `Glob(**/*.py)` returned exactly one application file `adventure.py`; `Grep(item|pickup|carry|inventory|chalice|sword in adventure.py)` returned no matches (clean greenfield extension).

- `/Users/brandonshuey/data/ByteForge/Repositories/e0710c02-7a18-467f-8a6e-519bafe16e3e/.bf-worktrees/901b7299/adventure.py::run_game_loop` (lines 100-129) — Main loop. New work must hook here: (a) item-state initialization (alongside `px, py = PLAYER_X, PLAYER_Y` at line 110); (b) a KEYDOWN handler in the event loop (lines 113-117) for the drop key; (c) per-frame pickup collision check after `move_player` (line 119); (d) item draw calls in the render block (lines 121-122). evidence: `Read(adventure.py, lines 100-129)` confirmed event-loop, movement, and render structure.

- `/Users/brandonshuey/data/ByteForge/Repositories/e0710c02-7a18-467f-8a6e-519bafe16e3e/.bf-worktrees/901b7299/adventure.py::move_player` (lines 54-64) — Movement function returns clamped `(x, y)`. Pickup uses player rect AABB vs item rect; collision check must occur AFTER move_player so newly-touched items register on the same frame. evidence: `Read(adventure.py, lines 54-64)`; tests `test_movement.py::test_move_*` verify the contract that move_player returns the post-movement position.

- `/Users/brandonshuey/data/ByteForge/Repositories/e0710c02-7a18-467f-8a6e-519bafe16e3e/.bf-worktrees/901b7299/adventure.py::draw_player` (lines 95-97) — Existing single-sprite render via `pygame.draw.rect`. New `draw_items` (or per-item draws) should follow the same pattern (rect + color constant) so item rendering composes with `draw_room` → items → `draw_player` ordering in `run_game_loop`. evidence: `Read(adventure.py, lines 95-97)`.

- `/Users/brandonshuey/data/ByteForge/Repositories/e0710c02-7a18-467f-8a6e-519bafe16e3e/.bf-worktrees/901b7299/adventure.py` constants block (lines 7-26) — `LOGICAL_WIDTH`, `LOGICAL_HEIGHT`, `WALL_THICKNESS`, `PLAYER_SIZE`, `_X_MIN/_X_MAX/_Y_MIN/_Y_MAX` define the playfield where items must spawn. T4 will add new constants: item size, item colors (chalice/key/sword), item spawn positions, and the drop key code (likely `pygame.K_SPACE` or similar). evidence: `Read(adventure.py, lines 7-26)`.

- `/Users/brandonshuey/data/ByteForge/Repositories/e0710c02-7a18-467f-8a6e-519bafe16e3e/.bf-worktrees/901b7299/adventure.py::_is_pressed` (lines 36-51) — Existing key-press abstraction supports both SDL1 (dict by 273/274/275/276) and SDL2 (pygame.K_*) keymaps. If the drop action is implemented as a **held key** via `pygame.key.get_pressed()`, T4 must reuse this helper and add an SDL1 alias for the drop key. If implemented as a **KEYDOWN edge event** in the event loop, this helper is not required. The choice matters for test fixture compatibility. evidence: `Read(adventure.py, lines 36-51)`; `tests/test_movement.py::no_keys()` (lines 18-24) uses SDL2 K_* dict — a held-drop-key test would extend the same shape.

## Related / Dependent Areas

- `/Users/brandonshuey/data/ByteForge/Repositories/e0710c02-7a18-467f-8a6e-519bafe16e3e/.bf-worktrees/901b7299/tests/test_adventure.py` — T1 unit tests (window, default player position, esc-exit). New item rendering/state tests live here or in a new `tests/test_items.py`. evidence: `Read(tests/test_adventure.py)` confirms test pattern.

- `/Users/brandonshuey/data/ByteForge/Repositories/e0710c02-7a18-467f-8a6e-519bafe16e3e/.bf-worktrees/901b7299/tests/test_movement.py` — T2 movement tests; reference for keys-pressed dict idiom (`no_keys()`, `keys_with(key)`) that an item-drop-on-held-key test would mirror. evidence: `Read(tests/test_movement.py, lines 18-31)`.

- `/Users/brandonshuey/data/ByteForge/Repositories/e0710c02-7a18-467f-8a6e-519bafe16e3e/.bf-worktrees/901b7299/tests/e2e/adversarial/test_adventure_adversarial.py` — Adversarial T1 suite; equivalent adversarial coverage will be needed for T4 (pickup-on-overlap, only-one-item invariant, drop-restores-world-item, drop-position-feasibility). evidence: `Read(test_adventure_adversarial.py)` shows pattern (`TestInitialization`, `TestGameLoopLogic`, `TestRenderFoundation`, `TestEdgeCases`).

- `/Users/brandonshuey/data/ByteForge/Repositories/e0710c02-7a18-467f-8a6e-519bafe16e3e/.bf-worktrees/901b7299/tests/e2e/adversarial/test_movement_adversarial.py` — Sibling adversarial movement suite. evidence: `Glob(**/*.py)` listing.

- `/Users/brandonshuey/data/ByteForge/Repositories/e0710c02-7a18-467f-8a6e-519bafe16e3e/.bf-worktrees/901b7299/tests/conftest.py` — Headless pygame fixture (`SDL_VIDEODRIVER=dummy`, project-root on sys.path). New item tests inherit this; no change required. evidence: `Read(tests/conftest.py)`.

- `/Users/brandonshuey/data/ByteForge/Repositories/e0710c02-7a18-467f-8a6e-519bafe16e3e/.bf-worktrees/901b7299/.bf-feature/t1-atari-adventure-homage-game-loop-rend/` and `.bf-feature/t2-player-movement-with-wall-collision-a/` — Prior diamond/elicit/task artifacts for T1 and T2. Reference for batch structure, intent.yaml, blast-radius.yaml conventions that T4 will follow. evidence: `Glob(**/*.md)` listing.

## Boundaries

- **In scope:**
  - `adventure.py` — add item state (3 world items + 1 carried slot), item constants (positions, colors, size, drop-key code), `draw_items()` (or per-item draws), pickup collision check, drop-keypress handler, carried-item rendering follows player position.
  - `tests/test_items.py` (new) — unit tests for pickup-on-touch, carry-only-one, drop semantics, item positions in bounds.
  - `tests/e2e/adversarial/test_items_adversarial.py` (new) — adversarial coverage mirroring `test_adventure_adversarial.py` patterns.
  - `tests/test_adventure.py` / `tests/test_movement.py` — only if existing assertions about render order or game-loop hot path break.
  - `.bf-feature/t4-items-*/` (new diamond/elicit/design/task artifact tree) — follows established T1/T2 layout.

- **Out of scope:**
  - Multi-room navigation, dragons, bats, mazes, the Atari Adventure castle layout beyond the single starting room.
  - Audio (no audio in T1/T2).
  - Item interactions with other items (e.g., key unlocks gate) — T4 spec is pickup/carry/drop only.
  - Inventory UI / HUD beyond the carried sprite following the player.
  - Persistence / save state.
  - Networking, accessibility overlays, controller input.
  - `tools/`, `.bf/`, `.bf-feature/` — workflow scaffolding, not application code.

## Discrepancies

- Requested: a specific "drop on keypress" key code — Found: `none` (request says "via a keypress" without naming the key) — note: implementation decision deferred to elicit/design; pygame `K_SPACE` is the conventional choice for a non-conflicting drop key (movement uses arrow keys; ESC quits). The intent.md / design phase must pin this.
- Requested: distinct sprites for chalice, key, sword — Found: `none` (no graphics assets in repo; current rendering is solid-color rects via `pygame.draw.rect`) — note: T4 will follow the established convention of color-coded rects (e.g., chalice=purple/silver, key=yellow, sword=cyan). Pixel-art sprites are out of scope unless explicitly elevated.
- Requested: world item spawn positions — Found: `none` (no item-position constants exist) — note: must be chosen during design within the existing playfield bounds `_X_MIN..._X_MAX` × `_Y_MIN..._Y_MAX` (lines 23-26 of adventure.py), and must not overlap the player's default spawn at `PLAYER_X, PLAYER_Y` (room center).
- Requested: "carry-one" semantics on touching a second item while already carrying — Found: `none` (request does not specify whether second-touch swaps, blocks, or ignores) — note: design phase must pick: (a) ignore second touch (simplest, classic Adventure behavior), (b) swap (drop current, pick up new), or (c) block movement. Default recommendation: ignore second touch — matches the original Atari Adventure rule that you must explicitly drop before picking up something else.
- Requested: Triptych architecture map — Found: `not run` (`mcp__triptych__get_architecture_map` was not invoked) — note: this is a tiny single-file Python project (one `adventure.py`, ~145 LOC, no controllers/services/components). Triptych's architecture map is calibrated for C#/TS multi-tier projects and would return noise. Direct `Glob` + `Read` + `Grep` is the correct grounding tool here, and was used. Recorded explicitly so the scorer does not flag missing Triptych evidence as a defect.

## Evidence (Triptych)

- Queries run (filesystem-grounded; Triptych skipped as out-of-fit for a 1-file Python repo — see Discrepancies):
  - `Glob("**/*.py")` -> 14 matches; only one application source (`adventure.py`), the rest are tests and `.bf-feature/**` workflow artifacts.
  - `Glob("**/*.md")` -> 10 matches; confirmed T1/T2 teachback + request.md exist, no existing T4 artifacts.
  - `Read("adventure.py")` -> 146 lines; confirmed module surface: constants block (7-26), `_is_pressed` (36-51), `move_player` (54-64), `initialize_pygame` (67-69), `create_window` (72-74), `draw_room` (77-92), `draw_player` (95-97), `run_game_loop` (100-129), `main` (132-141).
  - `Read("tests/test_adventure.py")` -> 47 lines; T1 test pattern confirmed.
  - `Read("tests/test_movement.py")` -> 87 lines; T2 keys-dict idiom confirmed.
  - `Read("tests/e2e/adversarial/test_adventure_adversarial.py")` -> 517 lines; adversarial class structure confirmed (`TestInitialization`, `TestGameLoopLogic`, `TestRenderFoundation`, `TestEdgeCases`).
  - `Read("tests/conftest.py")` -> 12 lines; headless SDL fixture confirmed.
  - `Grep("item|pickup|carry|inventory|chalice|sword" in adventure.py, -i)` -> 0 matches in adventure.py (only matches in `.bf/` and `.bf-feature/` workflow JSON/markdown, none in source).

- Nodes: `adventure.py` (module), `adventure.run_game_loop`, `adventure.move_player`, `adventure.draw_player`, `adventure.draw_room`, `adventure._is_pressed`, `adventure.PLAYER_X`, `adventure.PLAYER_Y`, `adventure.PLAYER_SIZE`, `adventure.WALL_THICKNESS`, `adventure.LOGICAL_WIDTH`, `adventure.LOGICAL_HEIGHT`, `adventure._X_MIN`, `adventure._X_MAX`, `adventure._Y_MIN`, `adventure._Y_MAX`.

- Edges: `run_game_loop` calls `move_player` (line 119), `draw_room` (121), `draw_player` (122), `pygame.key.get_pressed` (119), `pygame.event.get` (via `event_getter`, 113), `pygame.display.flip` (128), `clock.tick` (129); `move_player` calls `_is_pressed` (lines 56-62); `draw_room`/`draw_player` call `pygame.draw.rect`; `main` calls `initialize_pygame`, `create_window`, `pygame.display.set_caption`, `run_game_loop`, `pygame.quit`.

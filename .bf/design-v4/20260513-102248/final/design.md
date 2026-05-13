# T3 Multi-Room World + Screen Transitions — Final Design

**Run ID:** 20260513-102248  
**Ticket:** c847ce28-daf2-4b0e-6c13-08deb0efcb30  
**Mode:** spec-driven  
**Status:** complete

## 1. Executive Summary

This design expands the T1/T2 single-room adventure loop into a 4-room,
2x2 connected world while preserving legacy behavior and test stability.
The design adds:

- immutable room registry and start-room constants
- pure graph validators (symmetry/connectivity)
- room-aware rendering (sealed-edge walls only)
- room-aware movement with deterministic exit signaling
- pure warp helper with inward-offset debounce
- integrated loop transition flow and full test strategy (unit + adversarial)

The architecture preserves T1/T2 compatibility by keeping `ROOM_COLOR` and a
legacy `move_player(..., room=None)` path while introducing new room-aware
contracts for T3 integration.

## 2. Component Decomposition

| ID | Component | Type | Depends On | Status |
|----|-----------|------|------------|--------|
| C01 | RoomDataModelAndRegistry | data-model | - | designed + audited |
| C02 | RegistryValidators | backend-service | C01 | designed + audited |
| C03 | RoomAwareRendering | frontend-component | C01 | designed + audited |
| C04 | RoomAwareMovement | backend-service | C01 | designed + audited |
| C05 | TransitionWarpHelper | backend-service | C01 | designed + audited |
| C06 | GameLoopIntegration | integration | C02,C03,C04,C05 | designed + audited |

DAG: `C01 -> {C02,C03,C04,C05} -> C06`

## 3. Room Model and Topology

Authored world layout (4 rooms):

- `yellow` (start), `blue`, `green`, `purple`
- 2x2 grid with symmetric adjacency
- sealed edges represented by `neighbors[dir] is None`

Palette:

- yellow: `(240, 208, 64)`
- blue: `(64, 96, 200)`
- green: `(48, 160, 64)`
- purple: `(144, 64, 176)`

Compatibility guarantees:

- `ROOM_COLOR = (240, 208, 64)` preserved
- `START_ROOM = "yellow"`
- `ROOMS[START_ROOM].bg_color == ROOM_COLOR`

## 4. Runtime Contract (Post-T3)

### 4.1 Validation

`run_game_loop` performs startup registry checks:

- `assert_symmetric(ROOMS)`
- `assert_connected(ROOMS, START_ROOM)`

### 4.2 Movement and Transition

- `move_player(..., room=current_room)` returns either:
  - `(x, y)` for no transition
  - `("exit", dir)` for passage-edge crossing
- On exit, loop calls `_warp_position(current_room, dir, px, py)` and rebinds
  `current_room`, `px`, `py` before rendering.

Diagonal crossings resolve with deterministic policy:

- horizontal axis wins ties
- at most one transition per frame

### 4.3 Warp Semantics

`_warp_position(room, dir, x, y)`:

- selects neighbor by `room.neighbors[dir]`
- mirrors perpendicular coordinate
- clamps perpendicular coordinate to interior bounds
- places player inward by `INWARD_OFFSET = PLAYER_SPEED + 1`

## 5. Rendering Contract

`draw_room(surface, room)`:

- fills with `room.bg_color`
- draws edge walls only where `neighbors[dir] is None`
- leaves passage edges open (room color visible)

`current_room` is function-local only in `run_game_loop`; it is never a module
attribute.

## 6. Test Design

### 6.1 `tests/test_rooms.py`

- 11 registry/foundation tests (REQ-015..REQ-020)
- rendering/current-room tests (REQ-023..REQ-030)
- transition unit tests (REQ-053..REQ-058)

### 6.2 `tests/test_movement.py` reconciliation

- sealed fixture room used by all clamp tests
- original T2 boundary assertions preserved (REQ-048..REQ-052)
- no transition assertions added in this file

### 6.3 Adversarial E2E

`tests/e2e/adversarial/test_rooms_adversarial.py` covers:

- diagonal corner priority behavior
- alternating passage-edge toggling
- scripted full-graph traversal render confirmation
- held-direction debounce over 60 frames

## 7. Requirement Trace Coverage

Trace ownership by component:

- C01: REQ-001..REQ-008
- C02: REQ-009..REQ-014
- C03: REQ-021..REQ-030
- C04: REQ-031..REQ-036
- C05: REQ-037..REQ-042
- C06: REQ-015..REQ-020, REQ-043..REQ-063

Coverage result:

- Total requirements: 63
- Covered requirements: 63
- Missing requirements: 0

## 8. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Headless render sampling variability | RGB `[:3]` sampling + documented fallback strategy |
| `current_room` leakage across tests | function-local state + explicit `hasattr` assertions |
| Movement signature regressions | legacy `room=None` path + clamp reconciliation tests |
| Hold-to-retrigger transitions | `INWARD_OFFSET = PLAYER_SPEED + 1` |
| Asymmetric/disconnected graph drift | startup validators + synthetic negative tests |

## 9. Implementation Order

1. C01 foundation (`Room`, `ROOMS`, `START_ROOM`)
2. C02 validators
3. C03 rendering + local `current_room`
4. C04 movement exit signaling
5. C05 warp helper
6. C06 loop wiring + full test landing

This order is mandatory for stable incremental verification.

## 10. Artifacts

- Component designs: `components/C01..C06/design.md`
- Component summaries: `components/C01..C06/summary.json`
- Audit reports: `qa/C01..C06.json`, `qa/verify.json`
- Shared context: `shared-context/*.md`

# Risk Register

| ID | Risk | Mitigation | Owner |
|----|------|------------|-------|
| R1 | `pygame.Surface.get_at()` may not work headless on all platforms | Fall back to mock-based assertion that color is read from `room.bg_color` (REQ-028) | C03 |
| R2 | Module-level `current_room` would leak between tests in one interpreter | Function-local only; assert `not hasattr(adventure, "current_room")` (REQ-026, REQ-030, REQ-047) | C03, C06 |
| R3 | `move_player` signature break crashes legacy callers in `tests/test_movement.py` | `room=None` keeps legacy clamp behavior (REQ-036); reconcile clamp tests to use sealed fixture | C04, C06 |
| R4 | Holding direction across passage edge could chain transitions every frame | Inward offset `PLAYER_SPEED + 1` debounce (REQ-039, REQ-055, REQ-062) | C05 |
| R5 | Diagonal exit (passage + sealed at corner) could double-transition | Horizontal axis wins ties; at most one transition per frame (REQ-035, REQ-059) | C04 |
| R6 | Asymmetric author error in `ROOMS` would silently break BFS | `assert_symmetric` + `assert_connected` invoked at registry construction (REQ-009..REQ-012) | C02 |
| R7 | `tests/test_adventure.py` (T1) and `tests/test_movement.py` (T2) regressing under signature changes | Every story explicitly re-asserts these stay green (REQ-008, REQ-014, REQ-018, REQ-030) | C06 |

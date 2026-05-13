# Audit Request

**Run ID**: 20260513-093234
**Target**: T2 — Player movement with wall collision (arrow-key input, 4-direction)
**Tests file**: tests/e2e/adversarial/test_movement_adversarial.py
**Test count**: 49

## Tests Written by Orchestrator (Acting as Adversary)

### TestFourDirectionMovement (9 tests)
- test_right_increases_x_only — verifies RIGHT key increases x, not y
- test_left_decreases_x_only — verifies LEFT key decreases x, not y
- test_up_decreases_y_only — verifies UP decreases y (screen coords)
- test_down_increases_y_only — verifies DOWN increases y
- test_right_step_equals_player_speed — step magnitude = PLAYER_SPEED
- test_left_step_equals_player_speed — step magnitude = PLAYER_SPEED
- test_up_step_equals_player_speed — step magnitude = PLAYER_SPEED
- test_down_step_equals_player_speed — step magnitude = PLAYER_SPEED
- test_no_keys_returns_same_position — no movement when no keys

### TestWallCollisionClamping (15 tests)
- test_left_wall_clamp_exact_boundary — x stays at X_MIN when LEFT pressed at wall
- test_right_wall_clamp_exact_boundary — x stays at X_MAX when RIGHT pressed at wall
- test_top_wall_clamp_exact_boundary — y stays at Y_MIN when UP pressed at wall
- test_bottom_wall_clamp_exact_boundary — y stays at Y_MAX when DOWN pressed at wall
- test_player_cannot_go_left_of_left_wall — cannot pass through left wall
- test_player_cannot_go_right_of_right_wall — cannot pass through right wall
- test_player_cannot_go_above_top_wall — cannot pass through top wall
- test_player_cannot_go_below_bottom_wall — cannot pass through bottom wall
- test_left_wall_boundary_constants_are_consistent — X_MIN == WALL_THICKNESS
- test_right_wall_boundary_accounts_for_player_size — X_MAX formula correct
- test_bottom_wall_boundary_accounts_for_player_size — Y_MAX formula correct
- test_player_can_reach_left_wall — not stopped early
- test_player_can_reach_right_wall — not stopped early
- test_player_can_reach_top_wall — not stopped early
- test_player_can_reach_bottom_wall — not stopped early

### TestOppositeKeyHandling (4 tests)
- test_left_and_right_simultaneously_result_is_deterministic
- test_up_and_down_simultaneously_result_is_deterministic
- test_left_and_right_simultaneously_position_within_bounds
- test_up_and_down_simultaneously_position_within_bounds

### TestDiagonalMovement (6 tests)
- test_right_and_down_moves_both_axes
- test_right_and_up_moves_both_axes
- test_left_and_down_moves_both_axes
- test_left_and_up_moves_both_axes
- test_diagonal_magnitude_is_independent_per_axis
- test_diagonal_from_corner_clamps_both_axes

### TestSdl1LegacyKeys (5 tests)
- test_sdl1_right_moves_player_right
- test_sdl1_left_moves_player_left
- test_sdl1_up_moves_player_up
- test_sdl1_down_moves_player_down
- test_sdl1_right_wall_clamp_applies

### TestRepeatedMovement (6 tests)
- test_hold_right_reaches_and_stays_at_right_wall
- test_hold_left_reaches_and_stays_at_left_wall
- test_hold_up_reaches_and_stays_at_top_wall
- test_hold_down_reaches_and_stays_at_bottom_wall
- test_rapid_direction_reversal_does_not_escape_bounds
- test_all_four_walls_reachable_from_center_in_steps

### TestReturnValueContract (4 tests)
- test_return_type_is_tuple_of_two
- test_return_values_are_integers
- test_return_values_are_integers_at_boundary
- test_position_always_within_valid_range

## Run Results
All 49 tests PASSED.

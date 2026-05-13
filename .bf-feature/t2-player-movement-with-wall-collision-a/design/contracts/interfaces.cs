// T2 — Player movement with wall collision (arrow-key input, 4-direction)
// Behavioral contracts derived from adventure.py (Python/pygame single-module game).
// These C# interfaces model the logical contracts enforced by the Python implementation.

using System.Collections.Generic;

namespace T2.PlayerMovement;

/// <summary>
/// Behavioral contract for 4-direction arrow-key movement.
/// Maps to adventure.move_player(x, y, keys_pressed) and PLAYER_SPEED constant.
/// </summary>
/// <req>REQ-077E89</req>
/// <req>REQ-61A105</req>
/// <req>REQ-9463A3</req>
/// <req>REQ-7B8D30</req>
/// <req>REQ-77D5D3</req>
/// <req>REQ-D70100</req>
/// <req>REQ-68475D</req>
/// <req>REQ-995830</req>
/// <req>REQ-A617E0</req>
/// <req>REQ-DEEA15</req>
public interface IPlayerMovement
{
    /// <summary>
    /// Applies directional key input to position and returns clamped result.
    /// pygame key constants (K_RIGHT=275, K_LEFT=276, K_UP=273, K_DOWN=274) are
    /// used as dictionary keys; true means the key is currently held.
    /// </summary>
    (int X, int Y) MovePlayer(int x, int y, IReadOnlyDictionary<int, bool> keysPressed);

    /// <summary>Pixels-per-frame movement magnitude (positive integer).</summary>
    int PlayerSpeed { get; }
}

/// <summary>
/// Contract for wall-boundary constants and axis clamping.
/// Maps to adventure._X_MIN/_X_MAX/_Y_MIN/_Y_MAX derived from WALL_THICKNESS,
/// LOGICAL_WIDTH/HEIGHT, and PLAYER_SIZE.
/// </summary>
/// <req>REQ-12A97B</req>
/// <req>REQ-14DD79</req>
/// <req>REQ-E75BF0</req>
/// <req>REQ-F869F1</req>
/// <req>REQ-AB8DAB</req>
/// <req>REQ-D6D25F</req>
/// <req>REQ-6C4582</req>
/// <req>REQ-EFF78E</req>
/// <req>REQ-201AD6</req>
/// <req>REQ-398CFE</req>
public interface IWallBoundary
{
    /// <summary>Left wall inner edge (== WALL_THICKNESS).</summary>
    int XMin { get; }

    /// <summary>Right wall inner edge (== LOGICAL_WIDTH - WALL_THICKNESS - PLAYER_SIZE).</summary>
    int XMax { get; }

    /// <summary>Top wall inner edge (== WALL_THICKNESS).</summary>
    int YMin { get; }

    /// <summary>Bottom wall inner edge (== LOGICAL_HEIGHT - WALL_THICKNESS - PLAYER_SIZE).</summary>
    int YMax { get; }

    /// <summary>Clamps (x, y) to the room interior [XMin..XMax] x [YMin..YMax].</summary>
    (int X, int Y) Clamp(int x, int y);
}

/// <summary>
/// Contract for the T2 movement test suite acceptance obligations.
/// Maps to tests/test_movement.py (10 unit tests), tests/test_adventure.py (regression),
/// and tests/conftest.py (headless SDL fixture).
/// </summary>
/// <req>REQ-14E1B4</req>
/// <req>REQ-900635</req>
/// <req>REQ-4D064A</req>
/// <req>REQ-BE9F8B</req>
/// <req>REQ-7CE888</req>
/// <req>REQ-E37D72</req>
/// <req>REQ-146585</req>
/// <req>REQ-ADA63A</req>
public interface IMovementTestSuite
{
    /// <summary>pytest collects and passes all 10 tests in tests/test_movement.py.</summary>
    void VerifyAllTenMovementTestsPass();

    /// <summary>Exactly 10 tests collected from tests/test_movement.py.</summary>
    void VerifyExactlyTenTestsCollected();

    /// <summary>Each of the 4 wall-clamp boundaries has a dedicated test.</summary>
    void VerifyFourWallClampBoundaries();

    /// <summary>Each of the 4 directional axes has a dedicated test.</summary>
    void VerifyFourDirectionalAxes();

    /// <summary>tests/test_adventure.py regression suite passes after T2 changes.</summary>
    void VerifyAdventureRegressionSuitePasses();

    /// <summary>conftest.py sets SDL_VIDEODRIVER=dummy for headless test runs.</summary>
    void VerifyHeadlessSdlFixture();

    /// <summary>test_main_loop_exits_on_escape_event passes after T2 integration.</summary>
    void VerifyEscapeEventTest();

    /// <summary>pygame.key.get_pressed is callable inside run_game_loop with dummy SDL.</summary>
    void VerifyKeyGetPressedCallable();
}

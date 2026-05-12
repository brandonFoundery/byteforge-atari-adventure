// feature_witness: bdb1c1b58ad0547a
// Design contracts for: t1-atari-adventure-homage-game-loop-rend
// These C# interface stubs document the logical design of the Python pygame implementation.
using System.Collections.Generic;

namespace AdventureContracts;

/// <summary>
/// Manages pygame initialization and display window setup.
/// </summary>
/// <req>REQ-AADAC4</req>
/// <req>REQ-AFFA38</req>
public interface IGameInitializer
{
    /// <summary>Calls pygame.init() and returns true when failure count is zero.</summary>
    bool Initialize();

    /// <summary>
    /// Creates the display surface at logicalWidth x logicalHeight scaled by scale factor (3–4x).
    /// </summary>
    void SetDisplayMode(int logicalWidth, int logicalHeight, int scale);

    /// <summary>Calls pygame.quit() and releases all resources.</summary>
    void Shutdown();
}

/// <summary>
/// Renders the room background, perimeter walls, and player square each frame.
/// </summary>
/// <req>REQ-07C0B4</req>
/// <req>REQ-82B4D1</req>
/// <req>REQ-16D6CB</req>
/// <req>REQ-05A20B</req>
public interface IGameRenderer
{
    /// <summary>
    /// Fills the inner room area with a single solid background color.
    /// </summary>
    void DrawBackground();

    /// <summary>
    /// Draws four wall rectangles (top, bottom, left, right) with no passage gaps.
    /// </summary>
    void DrawWalls();

    /// <summary>
    /// Draws the player square at deterministic coordinates using the configured size constant.
    /// </summary>
    void DrawPlayer();

    /// <summary>Calls pygame.display.flip() to present the composed frame.</summary>
    void Present();
}

/// <summary>
/// Drives the main game loop: polls events, delegates rendering, enforces FPS cap, handles exit signals.
/// </summary>
/// <req>REQ-AAF862</req>
/// <req>REQ-3906FD</req>
/// <req>REQ-264497</req>
public interface IGameLoop
{
    /// <summary>
    /// Runs the game loop. Returns only when an exit signal (ESC key or OS close) is received.
    /// Ticks at approximately 30 FPS using pygame.time.Clock().tick(30).
    /// </summary>
    void Run();

    /// <summary>
    /// Returns true when an ESC key event or OS window-close event has been detected,
    /// signalling that Run() should exit and pygame.quit() should be called.
    /// </summary>
    bool ShouldExit { get; }
}

/// <summary>
/// Contracts for headless test environment setup: SDL dummy drivers and pinned dependencies.
/// </summary>
/// <req>REQ-33C367</req>
/// <req>REQ-3857A0</req>
public interface ITestEnvironment
{
    /// <summary>
    /// Sets SDL_VIDEODRIVER=dummy and SDL_AUDIODRIVER=dummy before any pygame import.
    /// </summary>
    void ConfigureDummyDrivers();

    /// <summary>
    /// Returns the list of pinned package version strings declared in requirements.txt.
    /// </summary>
    IReadOnlyList<string> GetPinnedDependencies();
}

/// <summary>
/// Contracts that the pytest test suite must satisfy for the game core.
/// </summary>
/// <req>REQ-874B54</req>
/// <req>REQ-915D4B</req>
/// <req>REQ-B95A16</req>
public interface ITestSuite
{
    /// <summary>Verifies headless pygame initialization completes without errors.</summary>
    bool TestHeadlessInit();

    /// <summary>Verifies that a synthetic ESC event causes the game loop to exit.</summary>
    bool TestEscExit();

    /// <summary>Asserts the player starting coordinates match the deterministic constants.</summary>
    bool TestPlayerStartCoordinates();
}

/// <summary>
/// Contracts for the project README documentation.
/// </summary>
/// <req>REQ-95C535</req>
public interface IDocumentation
{
    /// <summary>
    /// Returns verbatim install, run, and test commands as documented in README.md.
    /// </summary>
    IReadOnlyList<string> GetVerbatimCommands();
}

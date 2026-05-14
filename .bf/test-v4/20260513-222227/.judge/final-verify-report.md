# Final Verify Report

- Run: `20260513-222227`
- Target: `T4 — Items: pickup, carry-one, drop (chalice + key + sword, touch-to-pickup, drop on keypress)`
- Verifier: `tester (direct CLI failover execution)`

## Adversarial Suite Verify
Command:
`SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy pytest tests/e2e/adversarial/test_items_adversarial.py -v`

Result:
- Total: `20`
- Passing: `20`
- Failing: `0`
- Pass rate: `100%`

## Regression Sanity Verify
Command:
`SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy pytest -q`

Result:
- Total: `122`
- Passing: `122`
- Failing: `0`
- Pass rate: `100%`

## Notes
Warnings observed were third-party `pkg_resources` deprecation warnings from installed dependencies; no test failures occurred.

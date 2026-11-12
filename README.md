# Dataset Factory prospective study

Paper-ready target: **18 November 2026, 18:00 Europe/Paris**.
Protocol: [PROTOCOL.md](PROTOCOL.md). Machine dates/settings: [protocol.json](protocol.json).

A local LaunchAgent polls the public factory dashboard, records all candidates,
and dispatches the first 12 new releases to three 85-minute Fable 5.2 consumer
attempts each. Each dataset gets a separate local Git study and private evidence
branch. No more than three consumer attempts run concurrently. Existing seven
releases are excluded pilot material. The cohort closes 17 November at 18:00 Paris.

`python3 controller.py status` reads state. `collect` only collects; `tick` runs the
scheduled orchestration. `run_study.py self-test` tests the inherited runner.
The LaunchAgent requires this Mac to stay awake, signed in, connected and able to
use authenticated Claude Code and GitHub. Missed polls resume at login; they are
not retroactive observations. Local logs and workspaces live in `.local/`.

The controller schedules a bounded analysis/writing run on November 18 and retains
its output for author review. Scheduling is not proof of a finished or correct
paper. `STATUS.md`, evidence and paper/SIGNOFF.md distinguish actual outcomes.
Nothing is automatically submitted or made public.

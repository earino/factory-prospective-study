# Dataset Factory prospective study

Paper-ready target: **16 November 2026, afternoon Europe/Paris**.
Protocol: [PROTOCOL.md](PROTOCOL.md). Machine dates/settings: [protocol.json](protocol.json).

**Current paper direction (agreed 15 November):**
[From Public Data to Prediction Benchmarks](paper/PAPER-DIRECTION.md).
Center the complete factory, production cost and reliability, and independent
usefulness of its outputs. This supersedes earlier editorial outlines; the study
protocol and experiments remain unchanged. The scheduled writer reads this direction.

A local LaunchAgent polls the public factory dashboard, records all candidates,
and dispatches the first 12 new releases to three 85-minute Fable 5.2 consumer
attempts each. Each dataset gets a separate local Git study and private evidence
branch. No more than three consumer attempts run concurrently. Existing seven
releases are excluded pilot material. The cohort closes 16 November at 08:00 Paris.

`python3 controller.py status` reads state. `collect` only collects; `tick` runs the
scheduled orchestration. `run_study.py self-test` tests the inherited runner.
The LaunchAgent requires this Mac to stay awake, signed in, connected and able to
use authenticated Claude Code and GitHub. Missed polls resume at login; they are
not retroactive observations. Local logs and workspaces live in `.local/`.

The controller schedules a bounded analysis/writing run on November 16 and retains
its output for author review. Scheduling is not proof of a finished or correct
paper. `STATUS.md`, evidence and paper/SIGNOFF.md distinguish actual outcomes.
Nothing is automatically submitted or made public.

Install once with `python3 install_monitor.py`. The monitor checks every five
minutes and captures a dashboard observation every thirty minutes. A separate
`caffeinate -i` assertion prevents idle sleep through November 16 at 16:00 Paris;
it does not prevent manual sleep, shutdown or logout. Both jobs are scoped to
this study. To stop future scheduling, use `launchctl bootout gui/$(id -u)/org.earino.factory-prospective-study`
and the same command with `.awake` appended. At November 16 16:00 Paris, the next five-minute tick archives both owned
LaunchAgent plists and unloads them. If the Mac is asleep or logged out, cleanup
runs on the first tick after it returns. Evidence and study files remain intact.
Stopping scheduling manually does not interrupt an experiment already running;
those processes have their own registered deadlines.

The November 15 deadline amendment preserves the original protocol and the
then-observed cohort in `evidence/protocol-amendments/2026-11-15-deadline.json`.

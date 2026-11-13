# Prospective study status

{
  "consumer": {
    "dataset": "phmsa-pipeline-penalty-reduction",
    "started": "2026-11-13T18:32:30.303797+00:00",
    "status": "running"
  },
  "factory_counts": {
    "build": 1,
    "deferred": 43,
    "discover": 1,
    "published": 10,
    "rejected": 5
  },
  "observed_at": "2026-11-13T20:03:15.859786+00:00",
  "paper": {},
  "queue": [
    {
      "dataset": "fjc-civil-trial-36m",
      "verified_at": "2026-11-13T02:30:19.452430+00:00",
      "status": "complete",
      "selected": true,
      "branch": "consumer/fjc-civil-trial-36m",
      "error": null
    },
    {
      "dataset": "eia861-reliability-deterioration",
      "verified_at": "2026-11-13T05:28:19.001460+00:00",
      "status": "complete",
      "selected": true,
      "branch": "consumer/eia861-reliability-deterioration",
      "error": null
    },
    {
      "dataset": "phmsa-pipeline-penalty-reduction",
      "verified_at": "2026-11-13T07:53:15.783341+00:00",
      "status": "queued",
      "selected": true,
      "branch": null,
      "error": null
    }
  ],
  "snapshot_generated_at": "2026-11-13T19:51:25+00:00",
  "window": {
    "analysis_start": "2026-11-18T04:00:00Z",
    "attempt_minutes": 85,
    "cohort_close": "2026-11-17T17:00:00Z",
    "cohort_start": "2026-11-12T21:27:59.319944+00:00",
    "dashboard": "https://earino.github.io/dataset-factory-dashboard/dashboard.json",
    "factory_commit": "6238b7dca455b2ec4ac87b1602dd7fa1caad8201",
    "jobs": 3,
    "max_datasets": 12,
    "model": "claude-fable-5-2",
    "paper_draft_due": "2026-11-18T11:00:00Z",
    "paper_ready_due": "2026-11-18T17:00:00Z",
    "per_dataset_wall_hours": 6,
    "pilot_commit": "2e7dd9b117cf76f78eb6a77218a83778fbdaa5df",
    "poll_seconds": 1800,
    "registered_at": "2026-11-12T21:27:59.319944+00:00",
    "remote": "https://github.com/earino/factory-prospective-study.git",
    "research_stop": "2026-11-18T03:00:00Z",
    "threads": 5
  }
}

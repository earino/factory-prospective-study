# Prospective study status

{
  "consumer": {
    "branch": "consumer/seattle-building-permit-completion-retry-2",
    "dataset": "seattle-building-permit-completion",
    "execution_id": "seattle-building-permit-completion-retry-2",
    "started": "2026-11-15T21:52:53.525159+00:00",
    "status": "running"
  },
  "factory_counts": {
    "build": 2,
    "deferred": 92,
    "published": 19,
    "rejected": 7
  },
  "observed_at": "2026-11-15T22:28:53.810459+00:00",
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
      "status": "complete",
      "selected": true,
      "branch": "consumer/phmsa-pipeline-penalty-reduction",
      "error": null
    },
    {
      "dataset": "fda-510k-five-year-recall",
      "verified_at": "2026-11-13T23:42:15.349488+00:00",
      "status": "complete",
      "selected": true,
      "branch": "consumer/fda-510k-five-year-recall",
      "error": null
    },
    {
      "dataset": "t100-new-route-survival",
      "verified_at": "2026-11-14T02:04:19.792527+00:00",
      "status": "complete",
      "selected": true,
      "branch": "consumer/t100-new-route-survival",
      "error": null
    },
    {
      "dataset": "sbir-phase1-to-phase2-conversion",
      "verified_at": "2026-11-14T04:36:15.599185+00:00",
      "status": "complete",
      "selected": true,
      "branch": "consumer/sbir-phase1-to-phase2-conversion",
      "error": null
    },
    {
      "dataset": "caa-fce-hpv-escalation",
      "verified_at": "2026-11-14T22:55:16.477819+00:00",
      "status": "complete",
      "selected": true,
      "branch": "consumer/caa-fce-hpv-escalation",
      "error": null
    },
    {
      "dataset": "wser-effluent-exceedance",
      "verified_at": "2026-11-15T01:17:16.726399+00:00",
      "status": "complete",
      "selected": true,
      "branch": "consumer/wser-effluent-exceedance",
      "error": null
    },
    {
      "dataset": "faa-wildlife-strike-substantial-damage",
      "verified_at": "2026-11-15T09:22:16.250788+00:00",
      "status": "complete",
      "selected": true,
      "branch": "consumer/faa-wildlife-strike-substantial-damage",
      "error": null
    },
    {
      "dataset": "seattle-building-permit-completion",
      "verified_at": "2026-11-15T11:13:20.100537+00:00",
      "status": "complete",
      "selected": true,
      "branch": "consumer/seattle-building-permit-completion",
      "error": null
    },
    {
      "dataset": "fra-form54-hazmat-release",
      "verified_at": "2026-11-15T11:22:19.117088+00:00",
      "status": "complete",
      "selected": true,
      "branch": "consumer/fra-form54-hazmat-release",
      "error": null
    },
    {
      "dataset": "sdwis-lcr-lead-action-level-next-period",
      "verified_at": "2026-11-15T14:56:16.234161+00:00",
      "status": "complete",
      "selected": true,
      "branch": "consumer/sdwis-lcr-lead-action-level-next-period",
      "error": null
    }
  ],
  "retries": [
    {
      "dataset": "faa-wildlife-strike-substantial-damage",
      "execution_id": "faa-wildlife-strike-substantial-damage-retry-1",
      "outcome": {
        "branch": "consumer/faa-wildlife-strike-substantial-damage-retry-1",
        "commit": "ba071829395194aed1eeb6567534ccda25cc3976",
        "dataset": "faa-wildlife-strike-substantial-damage",
        "execution_id": "faa-wildlife-strike-substantial-damage-retry-1",
        "finished": "2026-11-15T16:44:24.717076+00:00",
        "started": "2026-11-15T14:41:22.642538+00:00",
        "status": "complete"
      }
    },
    {
      "dataset": "seattle-building-permit-completion",
      "execution_id": "seattle-building-permit-completion-retry-1",
      "outcome": {
        "branch": "consumer/seattle-building-permit-completion-retry-1",
        "commit": "b6e207596570efb9bb80d3aca208fa54b09021ed",
        "dataset": "seattle-building-permit-completion",
        "execution_id": "seattle-building-permit-completion-retry-1",
        "finished": "2026-11-15T18:29:30.983627+00:00",
        "started": "2026-11-15T16:44:24.718217+00:00",
        "status": "complete"
      }
    },
    {
      "dataset": "fra-form54-hazmat-release",
      "execution_id": "fra-form54-hazmat-release-retry-1",
      "outcome": {
        "branch": "consumer/fra-form54-hazmat-release-retry-1",
        "commit": "16e5ba920f95ccda9516f5b3e5d30d1810e7baf4",
        "dataset": "fra-form54-hazmat-release",
        "execution_id": "fra-form54-hazmat-release-retry-1",
        "finished": "2026-11-15T20:08:03.670058+00:00",
        "started": "2026-11-15T18:29:30.985035+00:00",
        "status": "complete"
      }
    },
    {
      "dataset": "eia861-reliability-deterioration",
      "execution_id": "eia861-reliability-deterioration-retry-1",
      "outcome": {}
    }
  ],
  "snapshot_generated_at": "2026-11-15T21:51:52+00:00",
  "window": {
    "analysis_start": "2026-11-16T10:00:00Z",
    "attempt_minutes": 85,
    "cohort_close": "2026-11-16T07:00:00Z",
    "cohort_start": "2026-11-12T21:27:59.319944+00:00",
    "dashboard": "https://earino.github.io/dataset-factory-dashboard/dashboard.json",
    "factory_commit": "6238b7dca455b2ec4ac87b1602dd7fa1caad8201",
    "jobs": 3,
    "max_datasets": 12,
    "model": "claude-fable-5-2",
    "paper_draft_due": "2026-11-16T12:00:00Z",
    "paper_ready_due": "2026-11-16T14:00:00Z",
    "per_dataset_wall_hours": 6,
    "pilot_commit": "2e7dd9b117cf76f78eb6a77218a83778fbdaa5df",
    "poll_seconds": 1800,
    "registered_at": "2026-11-12T21:27:59.319944+00:00",
    "remote": "https://github.com/earino/factory-prospective-study.git",
    "research_stop": "2026-11-16T10:00:00Z",
    "threads": 5
  }
}

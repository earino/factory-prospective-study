"""Verify the retained original review packet against the public release; no LLM call."""
from pathlib import Path
import hashlib
import json

P = Path(__file__).resolve().parent / "sbir-acceptance"
read = lambda name: json.loads((P / name).read_text())
sha = lambda data: hashlib.sha256(data).hexdigest()
retrieval = read("retrieval.json")
for name, digest in retrieval["sha256"].items():
    assert sha((P / name).read_bytes()) == digest, name

manifest = read("published-manifest.json")
descriptor_bytes = (P / "published-construction.json").read_bytes()
assert sha(descriptor_bytes) == manifest["assets"]["reproduction/construction.json"]["sha256"]
builder = read("build-3/response.json")["build_py"]
assert sha(builder.encode()) == manifest["assets"]["reproduction/build.py"]["sha256"]
prompt = (P / "evaluate-1/prompt.txt").read_text()
packet = json.loads(prompt[prompt.index('{"construction_code":'):])
assert packet["construction_code"] == builder
selection = json.loads(descriptor_bytes)["quality"]["timing"]["row_selection"]["rule"]
assert "no outcome field is used to select rows" in selection
assert "no outcome field is used to select rows" not in prompt
assert "Check population/selection" in prompt
assert "Compare the actual code to the stated rules" in prompt
assert packet["measurement"]["qualification"]["ok"] is True
checks = packet["measurement"]["source-checks.json"]["checks"]
assert len(checks) == 17 and all(c["passed"] for c in checks)
exclusion = next(c for c in checks if c["check"] == "unknown phase never becomes a negative label")
assert exclusion["observed"]["excluded_unknown_phase_in_window"] == 98
assert "unknown_phase.get((key, agency), set())" in builder
assert "excluded['unknown_phase_in_window'] += 1\n            continue" in builder
response = read("evaluate-1/response.json")
assert response["verdict"] == "accept" and response["findings"] == []
assert "Population matches the rule" in response["reason"]
assert "unknown/missing phases in a window are excluded" in response["reason"]
messages = read("evaluate-1/transcript.json")["messages"]
calls = [c for m in messages for c in (m.get("tool_calls") or [])]
assert len(messages) == 4 and len(calls) == 1
assert calls[0]["function"]["name"] == "web_extract"
urls = json.loads(calls[0]["function"]["arguments"])["urls"]
assert urls == ["https://www.sbir.gov/data-resources/data-dictionary/award", "https://www.sbir.gov/data-resources"]
report = {
    "source_repository": retrieval["repository"],
    "source_commit": retrieval["commit"],
    "source_hashes_verified": len(retrieval["sha256"]),
    "release_version": manifest["version"],
    "manifest_sha256": sha((P / "published-manifest.json").read_bytes()),
    "builder_sha256": sha(builder.encode()),
    "descriptor_sha256": sha(descriptor_bytes),
    "builder_in_original_prompt_matches_published_bytes": True,
    "explicit_population_and_code_check_instructions": True,
    "published_selection_rule": selection,
    "selection_rule_absent_from_original_prompt": True,
    "measurement_fields": sorted(packet["measurement"]),
    "source_check_passes": len(checks),
    "later_unknown_phase_exclusions_reported_to_reviewer": 98,
    "original_verdict": response["verdict"],
    "reviewer_explicitly_noticed_exclusions": True,
    "reviewer_claimed_population_match": True,
    "review_tool_calls": [{"name": "web_extract", "urls": urls}],
    "limits": [
        "No new judgment, source reconstruction, or model fit was performed.",
        "This verifies input and output records, not the model's hidden reasoning.",
        "The effect of exclusions on predictive scores is not measured.",
        "No counterfactual review tests whether supplying the omitted declaration would change acceptance.",
    ],
}
(P / "checks.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))

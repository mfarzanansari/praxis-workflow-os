# Profile schema guide

The canonical file is `praxis/profile.json`.

Required top-level fields:

- `schema_version`
- `profile_id`
- `status`
- `interview`
- `person`
- `consent`
- `outcomes`
- `work_streams`
- `tools_and_sources`
- `human_constraints`
- `knowledge_policy`
- `automation_boundaries`
- `governance`
- `evidence`
- `open_questions`

Each work stream should eventually contain:

```json
{
  "id": "content-campaign",
  "name": "Content campaign",
  "priority": 1,
  "frequency": "weekly",
  "trigger": "approved campaign objective",
  "inputs": [],
  "decisions": [],
  "actions": [],
  "deliverables": [],
  "quality_gates": [],
  "approvals": [],
  "handoff": {},
  "durable_residue": []
}
```

A field may be incomplete during interviewing. The evidence log records how facts were obtained.

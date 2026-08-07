# Open Draft PR — INIT-GATEFLOW-011 (spec-draft)

| Field | Value |
|-------|-------|
| Pin node | `spec-pr-action` (`authorization: automated`; human skill path via `/open-draft-pr`) |
| Forge action | `open_draft_pr` (`draft: true`, `apply_labels: [spec-pending]`) |
| Title | `[INIT-GATEFLOW-011] Spec — Day-1 visibility and GitHub reconcile (gateflow)` |
| Body path | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` (summary body from handoff Proposed Draft PR body) |
| Head | `chore/INIT-GATEFLOW-011-spec-gateflow` |
| Base | `develop` |
| PR | https://github.com/drivestream-lab/gateflow/pull/159 |
| Draft | **true** |
| Labels applied | `spec-pending` (no `*-lgtm`) |
| Outcome | **pass** |
| Date | 2026-08-06 |

## Notes

- Did **not** merge. Spec merge remains human-only after Gate 2 `spec-lgtm`.
- Content handoff resume: `next_candidates: [spec-pr-action]` satisfied; next content stage is `/initiative-feasibility` on this Draft PR head.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: open-draft-pr
  outcome: pass
  artifact:
    path: docs/specification/reports/Open-Draft-PR-INIT-GATEFLOW-011-spec-draft.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    pr_number: 159
    pr_url: "https://github.com/drivestream-lab/gateflow/pull/159"
    head_ref: chore/INIT-GATEFLOW-011-spec-gateflow
    base_ref: develop
    draft: true
    labels_applied:
      - spec-pending
  human_checkpoint: false
  external_action: false
```

Resume programme from content handoff: after Draft PR, run `/initiative-feasibility` on published spec head.

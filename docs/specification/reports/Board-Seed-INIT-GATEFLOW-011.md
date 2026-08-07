# Board seed report — INIT-GATEFLOW-011

## Board binding (governance SSOT)

| Field | Value |
|-------|-------|
| Org | drivestream-lab |
| Board name | drivestream-lab Board |
| Board number | 3 |
| Board URL | https://github.com/orgs/drivestream-lab/projects/3 |
| Governance path | prayog-meta/config/governance-drivestream-lab.yaml |
| Plan §9 target.project | drivestream-lab Board |
| Binding match | MATCH |

## Spec merge evidence

| Field | Value |
|-------|-------|
| Integration branch | `develop` @ `234f66a1b4d5e9d34522cb6bceb016c5672626a4` |
| Plan path | docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-011.md |
| Spec PR | https://github.com/drivestream-lab/gateflow/pull/159 (MERGED) |
| spec-lgtm on merge head | verified (label present on merged PR) |
| WorkManifest contract | `workmanifest-contract-pass` |
| apiVersion / kind | `prayog/v1` / `WorkManifest` |

## Result tree

| Role | Issue | URL | On board | Sub-issue of EPIC | TASK ids in body | REQ / deps / exit / proof preserved |
|------|-------|-----|----------|-------------------|------------------|-------------------------------------|
| EPIC | #160 | https://github.com/drivestream-lab/gateflow/issues/160 | yes | — | — | — |
| W0 | #161 | https://github.com/drivestream-lab/gateflow/issues/161 | yes | yes | TASK-W0-01…05 | yes |
| W1 | #162 | https://github.com/drivestream-lab/gateflow/issues/162 | yes | yes | TASK-W1-01…05 | yes |
| W2 | #163 | https://github.com/drivestream-lab/gateflow/issues/163 | yes | yes | TASK-W2-01…03 | yes |
| W3 | #164 | https://github.com/drivestream-lab/gateflow/issues/164 | yes | yes | TASK-W3-01…03 | yes |
| W4 | #165 | https://github.com/drivestream-lab/gateflow/issues/165 | yes | yes | TASK-W4-01…03 | yes |
| W5 | #166 | https://github.com/drivestream-lab/gateflow/issues/166 | yes | yes | TASK-W5-01…03 | yes |
| W6 | #167 | https://github.com/drivestream-lab/gateflow/issues/167 | yes | yes | TASK-W6-01…03 | yes |
| W7 | #168 | https://github.com/drivestream-lab/gateflow/issues/168 | yes | yes | TASK-W7-01…03 | yes |
| W8 | #169 | https://github.com/drivestream-lab/gateflow/issues/169 | yes | yes | TASK-W8-01…04 | yes |
| W9 | #170 | https://github.com/drivestream-lab/gateflow/issues/170 | yes | yes | TASK-W9-01…03 | yes |

## Project fields (manual if API cannot set)

Set on programme Project for each item if blank:

- **Initiative:** `INIT-GATEFLOW-011`
- **Codebase:** `drivestream-lab/gateflow`
- **Spec path:** `docs/specification/product/INIT-GATEFLOW-011-gateflow.md`
- **Status:** Backlog

Checks: **B1–B8** PASS (seeded).

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: create-board-tickets
  outcome: pass
  artifact:
    path: docs/specification/reports/Board-Seed-INIT-GATEFLOW-011.md
    digest: null
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    board_name: drivestream-lab Board
    board_url: https://github.com/orgs/drivestream-lab/projects/3
    epic_issue: https://github.com/drivestream-lab/gateflow/issues/160
    waves_seeded: [W0, W1, W2, W3, W4, W5, W6, W7, W8, W9]
    workmanifest_contract: pass
    tasks_preserved: true
    seeded: true
    repo: drivestream-lab/gateflow
    stack_profile: python-backend
  next_candidates:
    - wave-in-progress-action
  human_checkpoint: false
  external_action: false
```

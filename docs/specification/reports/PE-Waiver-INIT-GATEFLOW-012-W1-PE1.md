# PE waiver — INIT-GATEFLOW-012 W1 / PE-1 sequencing

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-012 |
| Wave | W1 |
| Board issue | [#186](https://github.com/drivestream-lab/gateflow/issues/186) |
| Date | 2026-08-08 |
| Authority | PE waiver aligning plan TASK-W1-01 with TDD PE-1 (REQ-16…19 → W2) |
| Status | **Active** — unblocks W1 `/pre-implement` / `/loop-spec` |

## Decision

Proceed with **W1** (REQ-10–15 clone/refresh) without waiting for a remounted `prayog-skills` tip that introduces Tenant workspace-prep / branch lifecycle **pin node shapes** (CTR-01 / REQ-28–31).

That remount remains a **hard gate for W2** (REQ-16…19), not W1.

## TASK-W1-01 exit (W1 only)

| Item | Value |
|------|--------|
| Criteria | Current pin tip reports **0 BROKEN** for **existing** workflow nodes |
| Pin | `.harness-pin.yaml` `agent_skills.ref: v0.5.0-rc.2` |
| Submodule | `git -C prayog-skills rev-parse HEAD` → `75b207ce0885ddaa28056cd624b4588efa3d960d` (at waiver time) |
| Proof command | `pytest tests/unit/test_forge_policy.py::test_all_remounted_pin_nodes_parse` and/or full `make test` pin-parse coverage |
| Explicitly **not** required for W1 | Net-new node ids for workspace-prep / branch create-or-reuse / branch-delete forge shapes |

## Still binding later

- Plan §9 **DEP-02** / PE-1 remount with 0 BROKEN for **new** shapes → **W2 exit** (and any wave that consumes those shapes).
- Do not claim CTR-01 fully satisfied for REQ-28–31 until remount lands.

## Rationale

1. TDD PE-1 product constraints are REQ-16…19 (**W2**), not REQ-10–15.
2. W1 implements gateflow-local git clone/fetch + orchestrator path resolution; it does not require the new pin dispatch shapes.
3. Prior `/loop-spec` stop (RISK-05) treated plan wording as blocking absent shapes; this waiver resolves the plan↔TDD sequencing mismatch for W1 only.

## Board record

Same text posted on [#186](https://github.com/drivestream-lab/gateflow/issues/186) (issue comment).

## Next hops

1. `/pre-implement` W1 — cite this waiver under TASK-W1-01 / PE-1 gate note; expect PASS.
2. `/loop-spec` W1 — clear TASK-W1-01 with current-pin evidence; implement TASK-W1-02…06.

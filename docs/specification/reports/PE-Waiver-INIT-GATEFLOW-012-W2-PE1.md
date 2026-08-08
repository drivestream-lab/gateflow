# PE waiver — INIT-GATEFLOW-012 W2 / PE-1 sequencing

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-012 |
| Wave | W2 |
| Board issue | [#187](https://github.com/drivestream-lab/gateflow/issues/187) |
| Date | 2026-08-08 |
| Authority | PE waiver aligning W2 coding start with TDD §3.5 (compose existing branch primitives) vs plan DEP-02 / W1 waiver “hard gate for W2” wording |
| Status | **Active** — unblocks W2 `/pre-implement` / `/loop-spec` |
| Supersedes (in part) | [`PE-Waiver-INIT-GATEFLOW-012-W1-PE1.md`](PE-Waiver-INIT-GATEFLOW-012-W1-PE1.md) “hard gate for W2” start-block — remount remains binding for **pin-shape consume**, not gateflow branch-resolve coding |

## Decision

Proceed with **W2** (REQ-16–19 branch create-or-reuse) **without** waiting for a remounted `prayog-skills` tip that introduces Tenant workspace-prep / branch lifecycle **pin node shapes** (CTR-01 / REQ-28–31).

W2 implements gateflow composition of **existing** `ForgeClient.ensure_branch_from_base` + `pr_branch_naming` (TDD §3.5 — no third primitive). It does **not** dispatch on net-new pin node ids.

## W2 coding-start exit (amended)

| Item | Value |
|------|--------|
| Criteria | Current pin tip reports **0 BROKEN** for **existing** workflow nodes (same bar as W1 TASK-W1-01 waiver proof) |
| Pin | `.harness-pin.yaml` `agent_skills.ref: v0.5.0-rc.2` |
| Submodule | `git -C prayog-skills rev-parse HEAD` → `75b207ce0885ddaa28056cd624b4588efa3d960d` (at waiver time) |
| Proof command | `pytest tests/unit/test_forge_policy.py::test_all_remounted_pin_nodes_parse` and/or full `make test` pin-parse coverage |
| Explicitly **not** required for W2 coding start | Net-new node ids for workspace-prep / branch create-or-reuse / branch-delete forge shapes |

## Still binding later

- Plan §9 **DEP-02** / PE-1 remount with 0 BROKEN for **new** shapes remains required before any wave that **consumes** those pin dispatch shapes (or claims CTR-01 / REQ-28–31 satisfied).
- Do **not** invent “0 BROKEN” for absent CTR-01 node shapes.
- W2 WorkManifest TASK-W2-01…04 stay gateflow-local (orchestrator / naming / verify / as-built).

## Rationale

1. TDD §3.5 binds W2 to composing existing branch primitives — not to new pin graph nodes.
2. Product scope: REQ-28–31 / CTR-01 live in `prayog-skills` (impact-map H2); gateflow W2 ships REQ-16–19 only.
3. W1 waiver deferred remount to “W2” as a sequencing placeholder; this waiver clarifies **coding start** for W2 is unblocked when existing-node parse is green, while remount stays a hard gate for **pin-shape consumption**.
4. Avoids inventing absent pin shapes and unblocks `/pre-implement` → `/loop-spec` W2.

## Board record

Same text posted on [#187](https://github.com/drivestream-lab/gateflow/issues/187) (issue comment).

## Next hops

1. `/pre-implement` W2 — cite this waiver under PE-1 / DEP-02 gate note; expect PASS (after wave head bound).
2. Cut `feature/INIT-GATEFLOW-012-w2-branch-resolve` from `develop` @ merge tip (human/Forge — not this skill).
3. `/loop-spec` W2 — TASK-W2-01…04 per WorkManifest.

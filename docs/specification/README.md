# Specification (gateflow)

| Layer | Path | Purpose |
|-------|------|---------|
| Product specs | [`product/`](product/) | Initiative FR slices for this repo |
| ADRs | [`adr/`](adr/) | Architecture decisions (when accepted) |
| As-built | [`as-built/implementation-status.md`](as-built/implementation-status.md) | Live vs deferred; verification matrix |
| Reports | [`reports/`](reports/) | Wave evidence (feasibility, TDD, plan, ground). Living SSOT is as-built + ADRs — see [`reports/README.md`](reports/README.md) |

## Lane naming

| Name | Meaning | Legacy PRD label |
|------|---------|------------------|
| **spec lane** | PRD → repo spec / feasibility / TDD / plan | Scenario A |
| **implement lane** | pre-implement → loop → verify → ground | Scenario B |

Verify: `verify_spec_lane` / `verify_implement_lane`. Product smoke: `verify_all`
(does not include deep lane prove-its).

Active initiative draft: [`product/INIT-GATEFLOW-006-gateflow.md`](product/INIT-GATEFLOW-006-gateflow.md)
(forge publish/mutate + lane start APIs + dual-workspace spec intake). Implementation plan (PE review):
[`reports/Implementation-Plan-INIT-GATEFLOW-006.md`](reports/Implementation-Plan-INIT-GATEFLOW-006.md).
Interactive execution (file-level + dead-code first):
[`reports/Execution-Plan-INIT-GATEFLOW-006.md`](reports/Execution-Plan-INIT-GATEFLOW-006.md).
Architecture:
[`adr/adr-009-pin-forge-publish-mutate-authority.md`](adr/adr-009-pin-forge-publish-mutate-authority.md)
(**Accepted**);
[`adr/adr-010-lane-intake-and-dual-workspace-authority.md`](adr/adr-010-lane-intake-and-dual-workspace-authority.md)
(**Accepted**).
Gate 1 / retrospective meta PRD still open (see INIT Spec questions).

Verification matrices: [`as-built/implementation-status.md`](as-built/implementation-status.md).

**Deferred / out of this track:** INIT-GATEFLOW-005 **W2** multi-skill dogfood
([#57](https://github.com/drivestream-lab/gateflow/issues/57)).

Predecessors: [`product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md`](product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md)
(W0/W1 delivered; W2 deferred),
[`product/INIT-GATEFLOW-003-gateflow.md`](product/INIT-GATEFLOW-003-gateflow.md) (delivered),
[`product/INIT-GATEFLOW-002-gateflow.md`](product/INIT-GATEFLOW-002-gateflow.md) (delivered),
[`product/INIT-GATEFLOW-001-gateflow.md`](product/INIT-GATEFLOW-001-gateflow.md) (delivered).

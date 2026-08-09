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
| **implement lane** | Pass-1: pre-implement → loop-spec → live-verify; Pass-2 closeout: learning-extract → ground-spec → wave-signoff | Scenario B |

Verify: `verify_spec_lane` / `verify_implement_lane` (Pass-1). Product smoke: `verify_all`
(does not include deep lane prove-its). Pass-2 closeout verify is INIT-007.

**Active initiative (013 spec draft):** [`product/INIT-GATEFLOW-013-gateflow.md`](product/INIT-GATEFLOW-013-gateflow.md)
(Programme-first onboarding — connect to programme meta, catalogue-driven
select/deselect, repo setup, real Launchpad readiness replacing file-presence
for newly selected repos, catalogue refresh; retires hand-typed `repos[]` at
tenant registration; CAP-01…07 / REQ-01…28; Gate 1 approved on
[prayog-meta#33](https://github.com/drivestream-lab/prayog-meta/pull/33)).

**Prior (012):** [`product/INIT-GATEFLOW-012-gateflow.md`](product/INIT-GATEFLOW-012-gateflow.md)
(Tenant registry + workspace/branch lifecycle — repo clone/refresh replacing
`Path.cwd()` fallback, branch create-or-reuse, harness-readiness gate,
repo-scoped `NO_CONCURRENT_RUN`, dormant `ForgeClient.delete_branch`; REQ-01…27,
REQ-32; Gate 1 approved on [prayog-meta#32](https://github.com/drivestream-lab/prayog-meta/pull/32)).

**Prior (011 W0–W9 human_approved; merges pending wave-signoff):** [`product/INIT-GATEFLOW-011-gateflow.md`](product/INIT-GATEFLOW-011-gateflow.md)
(Day-1 visibility + GitHub reconcile — checkpoint status-check CAP-01/02 +
visibility CAP-03…10; REQ-01…28; all GET-only; Gate 1 approved on
[prayog-meta#30](https://github.com/drivestream-lab/prayog-meta/pull/30)).

**Prior (010 W0–W3 human_approved; W4 tip pending merge):** [`product/INIT-GATEFLOW-010-gateflow.md`](product/INIT-GATEFLOW-010-gateflow.md)
(eng-lane pin tip executor parity — Gate 1 on
[prayog-meta#28](https://github.com/drivestream-lab/prayog-meta/pull/28)).

**Prior (009 freeze):** [`product/INIT-GATEFLOW-009-gateflow.md`](product/INIT-GATEFLOW-009-gateflow.md)
(both-lane factory prove-out — spec Draft PR tip + wrap-up + authorize API live;
Gate 1 approved on [prayog-meta#23](https://github.com/drivestream-lab/prayog-meta/pull/23)).

**Prior (008 W2 closed):** [`product/INIT-GATEFLOW-008-gateflow.md`](product/INIT-GATEFLOW-008-gateflow.md)
(**006A** — pin `authorization` explicit\|automated; Pass-1:
`pre-implement` → `loop-spec` → automated `wave-pr-action` → `live-verify`;
retire PR-at-start; WorkManifest `prayog/v1` before board create). Wire id
`INIT-GATEFLOW-008`. After **008 on `develop`**, **prove INIT-007 first** (REQ-17).

**Next dogfood:** [`product/INIT-GATEFLOW-007-gateflow.md`](product/INIT-GATEFLOW-007-gateflow.md)
(wave closeout start + learning DB ingest). Prior track:
[`product/INIT-GATEFLOW-006-gateflow.md`](product/INIT-GATEFLOW-006-gateflow.md)
(forge publish/mutate + lane start APIs + dual-workspace; REQ-7 superseded for
`automated` nodes by 008). Implementation plan (006):
[`reports/Implementation-Plan-INIT-GATEFLOW-006.md`](reports/Implementation-Plan-INIT-GATEFLOW-006.md).
Interactive execution (006):
[`reports/Execution-Plan-INIT-GATEFLOW-006.md`](reports/Execution-Plan-INIT-GATEFLOW-006.md).
Architecture:
[`adr/adr-009-pin-forge-publish-mutate-authority.md`](adr/adr-009-pin-forge-publish-mutate-authority.md)
(**Accepted** — dual authorization; hygiene strip under 010);
[`adr/adr-010-lane-intake-and-dual-workspace-authority.md`](adr/adr-010-lane-intake-and-dual-workspace-authority.md)
(**Accepted** — closeout §6; initiative closure §7; no ADR-011).
Gate 1 / retrospective meta PRD still open for 006/007/008 (see INIT Spec questions).

Verification matrices: [`as-built/implementation-status.md`](as-built/implementation-status.md).

**Deferred / out of this track:** INIT-GATEFLOW-005 **W2** multi-skill dogfood
([#57](https://github.com/drivestream-lab/gateflow/issues/57)); authorize→resume
(Pass-2 is new closeout Enter-at — INIT-007).

Predecessors: [`product/INIT-GATEFLOW-007-gateflow.md`](product/INIT-GATEFLOW-007-gateflow.md)
(parked),
[`product/INIT-GATEFLOW-006-gateflow.md`](product/INIT-GATEFLOW-006-gateflow.md),
[`product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md`](product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md)
(W0/W1 delivered; W2 deferred),
[`product/INIT-GATEFLOW-003-gateflow.md`](product/INIT-GATEFLOW-003-gateflow.md) (delivered),
[`product/INIT-GATEFLOW-002-gateflow.md`](product/INIT-GATEFLOW-002-gateflow.md) (delivered),
[`product/INIT-GATEFLOW-001-gateflow.md`](product/INIT-GATEFLOW-001-gateflow.md) (delivered).

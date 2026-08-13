# INIT-GATEFLOW-016 — spec slice for gateflow

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-016 |
| PRD | `prayog-meta/prd/INIT-GATEFLOW-016.md` |
| PRD digest (H1) | `sha256:2ee19c297b4f948c9f3fbb29d5b45e1e5db9e32fce4a21780915872b3640947a` |
| Meta PR | https://github.com/drivestream-lab/prayog-meta/pull/41 |
| Meta PR approved head (G1) | `5422e0f28ce8cb6b0b9f936b5df87afe280d4957` |
| Impact map | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-016.md` |
| Impact-map revision (H3) | `1` |
| Repo scope digest (H2) | **none** — this repo is **not** in map §2 Affected repositories. Map §4 disposition is **monitor** (transitive consumer risk only). `Spec to create` is `INIT-GATEFLOW-016-gateflow-ops.md`, not this file. |
| Tech-lead approval | [@0xbeefdead APPROVED](https://github.com/drivestream-lab/prayog-meta/pull/41#pullrequestreview-4915708147) 2026-08-12T10:57:35Z; GitHub `commit_id` = G1 head `5422e0f28ce8cb6b0b9f936b5df87afe280d4957`; attestation `map_revision: 1`, `prd_digest` match, `artifact: prd/reports/Impact-Map-INIT-GATEFLOW-016.md`; label `impact-map-lgtm`. Review **body** still prints `meta_pr_head_sha: 003e4228d2a66ccb5305305c7103bef95824bc70` (first PR commit; second commit is harness pin). Mechanical G1 uses review `commit_id` = current head. |
| Architecture constraints (existing) | [`adr-014`](../adr/adr-014-jwt-only-product-edge-trust-zone.md) (**Accepted** — JWT-only product edge). [`adr-016`](../adr/adr-016-tenant-scoped-run-board-checkpoint-authorization.md) (**Accepted** — tenant-scoped product reads). This INIT requests **no** successor ADR in gateflow. |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-13 |
| Status | Draft — **out of scope for this repo**; not a delivery spec. Dev review: confirm hold vs a new initiative for unrelated chat work. |

> **H4 citations:** H1 and H3 match the approved map. **H2 is absent by design** — Gate 1 did not assign a scope digest to gateflow. That fails D1 (repo must be `affected`). This file exists to **withdraw** the pre-Gate-1 person-directory outline that incorrectly used this initiative id.

> **Withdrawn content:** the 2026-08-13 pre-Gate-1 outline (person directory, N:N programme membership, login snapshot / select-programme, breaking replace of INIT-014 attach) is **not** INIT-GATEFLOW-016. If that product is still wanted, PM files a **new** initiative. Do not implement it under this id.

## Overview

INIT-GATEFLOW-016 is **Gateflow Mission Control** for **`gateflow-ops`**: a UI/BFF over gateflow's **existing** live API (PRD CAP-A–G / REQ-01–REQ-31). Gateflow is the upstream provider. The approved impact map (revision 1) lists this repo as **transitively affected, monitor only**, with **zero** route, schema, or contract change requested (PRD success criterion “Zero gateflow diff”; map D2 / §4 / §7).

**Scope boundary (this repo):** no new or changed observable behaviour. No person-directory APIs. No N:N membership. No session select-programme. No deletion of `POST /api/v1/programmes/{id}/tenant-admins`. Those were a local outline written before Gate 1; they collide with this initiative id and are withdrawn.

**Ownership:** this file records the map disposition and the freeze of existing as-built APIs as a **non-delivery** fact. It does not choose architecture. Delivery spec for Mission Control belongs in `gateflow-ops`.

**As-built baseline (2026-08-13, verified against this checkout):** the routes Mission Control will consume already exist (tenant, catalogue-connection, waves, runs, forge, checkpoints, board, initiatives, metrics). Attach remains 1:1 create+JWT (`ProgrammeService.attach_tenant_admin`, `POST .../tenant-admins`). Login remains `{access_token, token_type}` (`LoginResponse`). That is **existing** INIT-014 behaviour, not work in this INIT.

## Functional requirements

| ID | Requirement | PRD source | Condition / event | Observable result | Evidence layer |
|----|-------------|-----------|-------------------|-------------------|----------------|
| — | **None.** This repo has no in-scope PRD CAP. Map §2 `Spec to create` is `INIT-GATEFLOW-016-gateflow-ops.md`. | PRD document control “Primary repo: drivestream-lab/gateflow-ops”; “Explicitly **not** touched: Any gateflow backend change”; map §2–§4 | n/a | No new or changed gateflow product behaviour ships as INIT-GATEFLOW-016 | inspection (diff / this spec) |

> **Id convention:** `REQ-*` is canonical. No `REQ-*` rows are assigned here because assigning them would invent gateflow delivery scope the map did not grant.

### PRD capability disposition (this repo)

| PRD CAP | PRD REQ | Lands in | This repo |
|---------|---------|----------|-----------|
| CAP-A Identity & access | REQ-01–REQ-02 | gateflow-ops | Out of scope — consume existing tenant routes; no change |
| CAP-B Fleet onboarding | REQ-03–REQ-08 | gateflow-ops | Out of scope — consume existing catalogue/connect/select |
| CAP-C Wave operations | REQ-09–REQ-12 | gateflow-ops | Out of scope — consume existing waves/runs/forge |
| CAP-F Initiative tracking | REQ-13–REQ-21 | gateflow-ops | Out of scope — consume existing initiatives readouts |
| CAP-G Metrics & efficacy | REQ-22–REQ-25 | gateflow-ops | Out of scope — consume existing metrics APIs |
| CAP-D Checkpoint evidence | REQ-26–REQ-27 | gateflow-ops | Out of scope — consume existing checkpoints |
| CAP-E Board & tickets | REQ-28–REQ-31 | gateflow-ops | Out of scope — consume existing board routes |

## Negative and failure paths

| REQ | Condition | Required behavior | Why it matters | Evidence |
|-----|-----------|-------------------|-----------------|----------|
| — | n/a | N/A — no new gateflow behaviour, so no new failure paths in this repo | Prevents specifying ops-console errors as gateflow REQs | inspection |

Existing INIT-014 refuse paths (cross-programme isolation, role gates, PAT-never-in-body) stay as already specified and as-built. This INIT does not amend them.

## Out of scope for this repo

- Entire Mission Control UI/BFF (CAP-A–G) — **`gateflow-ops`**
- Person directory, N:N programme membership, login snapshot, select-programme, breaking removal of combined attach+JWT — **not this initiative** (withdrawn local outline; needs a new INIT if still wanted)
- Fleet-summary endpoint, workflow-pin readiness probe, process-map endpoint, log-pane richness, platform-admin console, Launchpad scaffolding, `prayog-skills` pin edits, server-side onboarding-scorecard composite — PRD explicit non-goals
- Any gateflow route, schema, or contract change (PRD KPI “Zero gateflow diff”)

## Cross-service contracts

These are **pre-existing** map CTR-01–07. This INIT does not change them. Concrete paths are already live (as-built); this table is semantic ownership only.

| Contract ID | Provider / owner | Consumer / owner | Entry point | Input shape | Output shape | Invariants | Errors | Compatibility / versioning | Contract-test location |
|-------------|------------------|------------------|-------------|-------------|--------------|------------|--------|----------------------------|------------------------|
| CTR-01 | gateflow / prayog-pe-team | gateflow-ops / prayog-pe-team | Identity & access (tenant detail / invite) | Tenant-scoped JWT | Tenant and tenant-user fields already published | Unchanged this INIT | Existing 401/403 | **Unchanged** — map CTR-01 | existing tenant verify |
| CTR-02 | gateflow / prayog-pe-team | gateflow-ops / prayog-pe-team | Fleet onboarding (connect, catalogue, select/deselect, readiness) | Programme-scoped JWT | Catalogue / membership / readiness already published | Unchanged this INIT | Existing named select outcomes | **Unchanged** — map CTR-02 | `verify_programme_connect`, `verify_repo_selection`, `verify_catalogue_refresh` |
| CTR-03 | gateflow / prayog-pe-team | gateflow-ops / prayog-pe-team | Wave operations (start, runs, forge authorize) | Programme-scoped JWT | Run/timeline/forge already published | Unchanged this INIT | Existing stop/fail semantics | **Unchanged** — map CTR-03 | `verify_wave_start`, `verify_implement_lane` |
| CTR-04 | gateflow / prayog-pe-team | gateflow-ops / prayog-pe-team | Checkpoint evidence | Programme-scoped JWT | Checkpoint payloads already published | Unchanged this INIT | Existing | **Unchanged** — map CTR-04 | `verify_checkpoint_status`, `verify_checkpoint_history` |
| CTR-05 | gateflow / prayog-pe-team | gateflow-ops / prayog-pe-team | Board & tickets | Programme-scoped JWT | Board payloads already published | Unchanged this INIT | Existing | **Unchanged** — map CTR-05 | `verify_board`, `verify_create_tickets` |
| CTR-06 | gateflow / prayog-pe-team | gateflow-ops / prayog-pe-team | Initiative & delivery tracking | Programme-scoped JWT | Initiative readouts already published | Unchanged this INIT | Existing honest gaps | **Unchanged** — map CTR-06 | `verify_initiatives_readout` and related |
| CTR-07 | gateflow / prayog-pe-team | gateflow-ops / prayog-pe-team | Metrics & efficacy panel | Programme-scoped JWT | Skill/factory/scorecard already published | Unchanged this INIT | Existing empty/named-clean | **Unchanged** — map CTR-07 | `verify_skill_efficacy`, `verify_factory_effectiveness`, `verify_delivery_scorecard` |

## Non-functional requirements

| Area | Requirement or N/A rationale | Acceptance / evidence |
|------|------------------------------|-----------------------|
| Security | N/A — no new gateflow surface; existing JWT/role gates unchanged | inspection |
| Reliability | N/A — no new writes or workflows in this repo | inspection |
| Performance / capacity | N/A — no new gateflow SLO; ops console load is a `gateflow-ops` concern | inspection |
| Observability | N/A — no new gateflow log/metric contract | inspection |
| Privacy / data handling | N/A — no new PII fields in this repo | inspection |
| Migration / compatibility | **No breaking gateflow change this INIT.** Withdrawn outline must not ship under this id. | inspection / this spec |
| Rollback / recovery | N/A — no delivery change to roll back in this repo | inspection |
| Operations / support | Map IM-01: treat consumed APIs as frozen for the duration of `gateflow-ops` delivery (monitoring commitment, not a gateflow TASK) | map §10 IM-01 |

## Assumptions

| ID | Assumption | Evidence | Owner | Status | Invalidated when |
|----|------------|----------|-------|--------|------------------|
| A-1 | Gate 1 assignment of INIT-GATEFLOW-016 to `gateflow-ops` (zero gateflow backend) stands | Meta PR #41 `impact-map-lgtm`; map §2–§4 | PM | confirmed | A new approved map revision lists gateflow as affected with an H2 digest |
| A-2 | Person-directory / N:N membership / session-select is a **different** product and must not reuse this initiative id | Feasibility FF-02; withdrawn outline vs PRD CAP-A–G | PM | confirmed for this INIT | A new INIT is filed and Gate-1-approved for that product |
| A-3 | Review-body SHA `003e4228…` vs G1 head `5422e0f…` does not reopen Gate 1 while GitHub `commit_id` matches the head and `impact-map-lgtm` is on | `gh` review JSON 2026-08-13 | PE | open (hygiene) | Label dropped or a new commit lands without matching APPROVED `commit_id` |

## Spec questions (ambiguities)

| ID | Lane | Question | Owner | Blocking | Required by | Default if deferred | Status | Resolution link |
|----|------|----------|-------|----------|-------------|---------------------|--------|-----------------|
| Q-1 | PM | If person-directory + N:N membership is still wanted, file a **new** prayog-meta initiative (do not amend 016's map to add gateflow backend scope without a material map revision). | PM | no | future PRD | Do not implement that product under INIT-GATEFLOW-016 | open | pending |
| Q-2 | PE | Map IM-01 freeze of consumed APIs during ops delivery — monitoring only, or a written compatibility promise? | PE | no | `gateflow-ops` W0 | Proceed — no gateflow change planned (map default) | open | map IM-01 |

No material question blocks the **hold** disposition for this repo.

## Draft check summary (D1–D12)

| Check | Status | Evidence / findings |
|-------|--------|---------------------|
| D1 Approved handoff current | FAIL | H1 digest and H3 revision 1 match. G1 review `commit_id` = current meta head. **H2 missing:** gateflow is not `affected`. D1 requires affected + `scope_digest`. |
| D2 Complete PRD traceability | PASS | Every PRD CAP is mapped; all land in `gateflow-ops`. Empty REQ table is the repo-bounded result, not a missing trace. |
| D3 Repo-bounded scope | PASS | Agrees with map §2–§4: no delivery in this repo; ops UI and withdrawn directory work listed out of scope. |
| D4 Observable acceptance | PASS | Not applicable — no in-scope REQ. Freeze is inspection of “no INIT-016 diff”, not a new behaviour statement. |
| D5 Negative/failure paths | PASS | N/A with reason; existing 014 paths not amended. |
| D6 Assumptions/questions | PASS | A-1…A-3; Q-1/Q-2 non-blocking with defaults. |
| D7 Cross-repository contracts | PASS | CTR-01–07 listed as unchanged provider contracts; no new CTR. |
| D8 NFR applicability | PASS | All rows present; most N/A with reason; compatibility row states no breaking change. |
| D9 As-built alignment | PASS | Distinguishes existing 014 attach/login vs withdrawn outline vs ops-only 016. |
| D10 Dependency order | PASS | Map §7: gateflow already live → gateflow-ops. No sequencing TASK in this repo. |
| D11 Zero unresolved blockers | FAIL | D1 is an explicit gate closure (repo not affected). Q-1/Q-2 are not material for hold. |
| D12 Output completeness | PASS | Header (H2 recorded as none), tables, checks, outcome, PR readiness. |

**Draft verdict:** FAIL (D1/D11 — this repo is not an affected build target)

**Selected workflow outcome:** `blocked`
**Outcome reason:** Explicit gate: approved map does not list `drivestream-lab/gateflow` as affected and assigns no H2 `scope_digest`; Mission Control delivery is `gateflow-ops`. Not `stale` (H1/H3/G1 identities match). Not `needs-input` (no missing PRD; hold is already decided by Gate 1).

Do not advance to `/initiative-feasibility` for a gateflow **delivery** slice. Re-run feasibility only if a **new** map revision adds this repo as affected. Person-directory work waits on a new initiative.

## PR readiness handoff

| Item | Value |
|------|-------|
| Workflow outcome | `blocked` — D1 repo not affected / no H2 |
| Verdict | **PR BLOCKED** for Gate 2 delivery-spec merge; local file is a hold/withdraw record |
| Existing spec PR | [#242](https://github.com/drivestream-lab/gateflow/pull/242) **merged** (pre-Gate-1 outline + catalogue). Branch `chore/INIT-GATEFLOW-016-spec-gateflow` has the STALE feasibility report @ `a0ded06` |
| Proposed branch | `chore/INIT-GATEFLOW-016-spec-gateflow` |
| Proposed base | `develop` |
| Proposed title | `[INIT-GATEFLOW-016] Spec — gateflow (out of scope / monitor)` |
| PR type | **Draft** (entire spec lifecycle) — only if PE still wants the hold record on a spec PR |
| Local artifacts to publish | `docs/specification/product/INIT-GATEFLOW-016-gateflow.md` (this withdraw); `docs/specification/README.md` pointer |
| Forge readiness | **`open_draft_pr` not filled** (outcome is not `pass`). Pin `commit_workspace: required` — recommend `/commit-workspace` to persist the withdraw. Next node `spec-human-decision`. |
| Reviewer | @drivestream-lab/prayog-pe-team |
| Initial Gate 2 label | do not apply — not opening a delivery spec PR from this hop |
| Additional invalidation label | none from this skill |
| Blocking items | D1 (repo not affected) |

**No GitHub side effects have occurred.**

### Proposed Draft PR body

```markdown
## Initiative

INIT-GATEFLOW-016 — gateflow is **not** a build target (Mission Control is gateflow-ops)

## Meta handoff

- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/41
- Approved meta head: `5422e0f28ce8cb6b0b9f936b5df87afe280d4957`
- Impact-map revision: 1
- PRD digest: `sha256:2ee19c297b4f948c9f3fbb29d5b45e1e5db9e32fce4a21780915872b3640947a`
- Repo scope digest: none (not affected)

## Spec path

`docs/specification/product/INIT-GATEFLOW-016-gateflow.md`

## Summary

- Withdraws the pre-Gate-1 person-directory outline
- Zero REQ rows — map assigns delivery to gateflow-ops
- Open: Q-1 (new INIT for directory work if wanted), Q-2 (IM-01 freeze monitoring)

## Gate 2 — spec package readiness

Not applicable as a delivery slice. Outcome `blocked` → `spec-human-decision`.

Requested reviewer: @drivestream-lab/prayog-pe-team
```

## Developer review

- [x] Scope matches the approved impact-map (this repo **not** in §2; monitor only)
- [x] REQs: none in-scope — empty table is intentional
- [x] Contracts are semantic; unchanged CTR-01–07; no architecture decisions
- [x] No blocking question remains **for the hold** (D1 is a gate, not a PM ambiguity)
- [ ] Developer confirmed draft is ready for feasibility — **N/A** (do not run delivery feasibility)

## After Draft PR creation

Not opened by this skill. PE may still publish the hold record via `/commit-workspace`.

## References

- PRD: `prayog-meta/prd/INIT-GATEFLOW-016.md`
- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/41
- Impact map: `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-016.md` revision 1
- Feasibility: `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-016.md` (`stale` / FF-01, FF-02)
- Prior attach (unchanged): [`INIT-GATEFLOW-014-gateflow.md`](INIT-GATEFLOW-014-gateflow.md)
- ADR-014: [`adr-014-jwt-only-product-edge-trust-zone.md`](../adr/adr-014-jwt-only-product-edge-trust-zone.md)

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-draft
  outcome: blocked
  artifact:
    path: docs/specification/product/INIT-GATEFLOW-016-gateflow.md
  blockers:
    - D1
  signals:
    gate1_h1: sha256:2ee19c297b4f948c9f3fbb29d5b45e1e5db9e32fce4a21780915872b3640947a
    gate1_h2: none
    gate1_h3: 1
    gate1_g1: 5422e0f28ce8cb6b0b9f936b5df87afe280d4957
    ripple_action: hold
    this_repo_disposition: monitor
    approved_primary_repo: drivestream-lab/gateflow-ops
    withdrawn_outline: person-directory-nn-membership
    d1: repo_not_affected
    d11: gate_closed
    codegraph_provider: mcp-user-prayog-fleet-cbm
    grounding_depth: light
  next_candidates:
    - spec-human-decision
  human_checkpoint: true
  external_action: false
  forge:
    action: commit_workspace
    title: "[INIT-GATEFLOW-016] Spec — gateflow out of scope (Mission Control is gateflow-ops)"
    body_path: docs/specification/product/INIT-GATEFLOW-016-gateflow.md
```

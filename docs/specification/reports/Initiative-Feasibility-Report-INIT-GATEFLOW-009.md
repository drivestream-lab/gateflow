# Feasibility report — INIT-GATEFLOW-009

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-009 |
| Spec | `docs/specification/product/INIT-GATEFLOW-009-gateflow.md` |
| Spec digest | `sha256:69f68f455b19334f0f9a2f6ad9753927daa3d4f9fdc2e7a7fd4ea794d56c2f65` |
| PRD digest | `sha256:76ab22b3c197b9d0cb6b08e6cea379c4e07b3a471b8a88203fddca6014c1c012` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-009.md` / `1` |
| Repo scope digest | `sha256:d0a2b62632113db0fa64cb7d7e63dc393fa5a8217092dda242a99b3392978e9b` |
| Approved meta PR head | `6660aa4fefbcd80324cb970aa5bab642d3e5e0a1` |
| Impact-map approval | Meta PR [#23](https://github.com/drivestream-lab/prayog-meta/pull/23) APPROVED @ head; label `impact-map-lgtm`; tech-lead `0xbeefdead` (2026-08-03) |
| Source freshness | **CURRENT** — PRD digest, map revision 1, scope digest, and approved meta head match spec header and prior `spec-draft` handoff signals; ripple action `continue` |
| Prior stage | `/spec-draft` outcome `pass` → `spec-pr-action` (automated Draft PR) |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-03 |
| Branch | `chore/INIT-GATEFLOW-009-spec-gateflow` — Draft spec PR (single review surface) |
| Initiative segment | `INIT-GATEFLOW-009` |
| Status | Draft |
| Review deadline | 2026-08-06 |
| Deciders | PM: programme PM · Domain SME: N/A (gateflow-only prove-out) |

## Summary

INIT-GATEFLOW-009 is **buildable in this repo** as a **prove-out** initiative: the spec
lane, forge publish, automated `spec-pr-action`, authorize API, closeout chain, and
`verify_spec_lane` harness already exist from INIT-006–008 and INIT-007. Delivery is
primarily **live verification**, a **feature-readiness freeze** artifact, and **replacing
placeholder CI** — not a rebuild. Gate 1 handoff is current; spec REQs align with
**Accepted ADR-009** and **ADR-010** with no NEW-ADR. Open non-blocking questions
(Q-1…Q-4) have documented defaults. Informational gaps (live dogfood deferred, as-built
rows lagging pin/migration state) are expected prove-out targets and do not block
`/spec-implementation-plan`.

**Findings:** 5 total (0 Critical, 0 Should fix, 2 Verify, 3 Gap)

### Derived counts (lane × severity)

| Lane | Blocking open | Non-blocking open | Resolved |
|------|---------------|-------------------|----------|
| PM | 0 | 1 (Q-4) | 0 |
| PE / ADR | 0 | 3 (Q-1…Q-3) | 0 |
| Domain | 0 | 0 | 0 |
| Auto-fix | 0 | 1 (AF-1) | 0 |

| Severity | Unresolved count |
|----------|------------------|
| Critical | 0 |
| Should fix | 0 |
| Verify / Gap (informational) | 5 |

### Selected workflow outcome

| Field | Value |
|-------|-------|
| Outcome | `pass` |
| Rationale | Source freshness CURRENT; zero unresolved blocking PE/ADR findings; Q-1…Q-4 non-blocking with defaults |
| Next (from workflow) | `spec-implementation-plan` |

---

## Baseline snapshot (F1)

| Area | Current state | Evidence |
|------|---------------|----------|
| Unit tests | `tests/unit/` — 30 modules; forge, wave-start, meta intake, orchestrator, closeout, handoff | `make test`; `tests/unit/test_forge_policy.py`, `test_wave_start.py`, `test_meta_pr_intake.py`, `test_forge_action_service.py` |
| Live verify | `verify_spec_lane` (opt-in Pass-1); `verify_wave_closeout` (closeout/W2); `verify_board` (authorize path); `verify_all` smoke | `tests/verify/verify_spec_lane.py`; `tests/README.md` |
| Toolchain | `make check` (black, ruff, pyright, import-linter) wired | `implementation-status.md` §Testing harness |
| As-built | Implement lane live-proven; spec lane code + unit exist; forge publish + automated spec-pr wired (INIT-008); live forge/authorize/spec wrap-up **deferred**; CI **placeholder** | `docs/specification/as-built/implementation-status.md` |
| Pin | `v0.5.0-rc.2` family; spec lane orchestrated (`spec-draft` → `spec-pr-action` → `initiative-feasibility` → STOP @ `spec-implementation-plan`) | `.harness-pin.yaml`; `prayog-skills/workflow.yaml` |

## Traceability matrix

| Spec REQ / wave | Spec claim | Code evidence | Unit | Verify | Status |
|-----------------|------------|---------------|------|--------|--------|
| REQ-1 / W0 | Meta accept-gate + dual workspace bind | `wave_start_service.py`, `meta_pr_intake.py`, `waves_routes` | `test_wave_start`, `test_meta_pr_intake` | `verify_spec_lane` (start) | **exists** |
| REQ-2 / W1 | Draft Spec PR tip deliverable via forge publish hops | `run_orchestrator._publish_stage_workspace_if_needed`, `ForgeActionService`, pin `spec-pr-action` automated | `test_forge_client`, `test_forge_action_service`, `test_publish_stage_workspace_*` | `verify_spec_lane` | **partial** — unit complete; live dogfood deferred |
| REQ-3 / W1 | Honest stop at first manual gate | pin `spec-implementation-plan` `dispatch: manual`; walker STOP policy | `test_run_orchestrator`, `test_handoff_workflow` | `verify_spec_lane` stop asserts | **exists** |
| REQ-4 / W2 | Spec wrap-up live on Draft Spec PR | `POST /waves/closeout/start`, Pass-2 pin chain | `test_wave_closeout` | `verify_wave_closeout` dogfood | **partial** — implement-lane dogfood approved; spec-lane closeout live deferred (superseded for this INIT) |
| REQ-5 / W3 | Authorize API stop→approve→side-effect | `ForgeActionService`, `POST …/forge/authorize` | `test_forge_action_service` | `verify_board` (partial) | **partial** — unit complete; live authorize deferred |
| REQ-6 / W3 | Feature-readiness freeze + as-built update | no dedicated freeze artifact yet | — | inspection | **gap** — new doc work (W3) |
| REQ-7 / W3 | Replace placeholder CI | `.github/workflows/ci.yml` echo-only placeholder | — | CI run | **gap** — expected W3 deliverable |

## ADR pass (pre-T2)

| ADR | Domain matched | Status |
|-----|----------------|--------|
| ADR-009 | pin forge publish/mutate, spec-pr automated, authorize | **Accepted** — aligned (amended INIT-008) |
| ADR-010 | spec lane intake, dual workspace, closeout | **Accepted** — aligned |
| ADR-003 | ForgeClient infra boundary | **Accepted** — aligned (CTR-02) |
| ADR-005 | programme token on starts/authorize | **Accepted** — aligned |
| ADR-008 | handoff baton ingest | **Accepted** — aligned |

## MDC pass (pre-T2)

| MDC | Domain | Read / skipped |
|-----|--------|----------------|
| `spec-driven-development.mdc` | truth hierarchy, same-PR discipline | read |
| `testing-verify-flows.mdc` | unit vs live verify boundary | read |
| `fail-fast.mdc` | fail-closed preconditions | read |
| `architecture.mdc` | layering | skipped (no new modules) |
| `database-migrations.mdc` | Alembic | skipped (no new DDL in prove-out) |

## ADR traceability (F13)

| Spec REQ / wave | Relevant ADR(s) | Status | Finding |
|-----------------|-----------------|--------|---------|
| REQ-1, REQ-2 | ADR-010, ADR-009 | aligned | — |
| REQ-3 | pin + ADR-009 | aligned | — |
| REQ-4 | ADR-010 (closeout) | aligned | — |
| REQ-5 | ADR-009 (explicit authorize) | aligned | — |
| REQ-7 | N/A (CI hygiene) | N/A | — |

No **NEW-ADR** required — initiative reuses Accepted decisions.

## Governance findings (F13–F14)

| ID | Check | Spec quote | Governing doc | Finding |
|----|-------|------------|---------------|---------|
| — | F13 | (none) | ADR-009, ADR-010 | No conflicts |
| — | F14 | REQ evidence layers cite unit + live verify | `testing-verify-flows.mdc` | Aligned — no MDC conflict |

## Findings by severity

### Critical

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| — | — | None | — |

### Should fix

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| — | — | None | — |

### Verify

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-01 | F5 | As-built §006 open gap lists human Alembic for `runs.meta_pr_url` / `meta_head_sha`, but first migration already declares columns | `implementation-status.md` L184; `postgres_migrations/versions/1cd9a83a94a2_first_version.py` L36–37; spec A-6 |
| FF-02 | F5 | As-built says spec-lane skills `dispatch: manual`; pinned workflow has `spec-draft` and `initiative-feasibility` as `dispatch: orchestrated` | `implementation-status.md` L185; `prayog-skills/workflow.yaml` L106–143 |

### Gap (informational)

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-03 | F1/F8 | CI job is placeholder echo — REQ-7 deliverable for W3 | `.github/workflows/ci.yml` L18–21; spec REQ-7 |
| FF-04 | F3 | Live forge dogfood, live authorize, and spec-lane Pass-1 prove-out deferred — expected prove-out work, not missing code | `implementation-status.md`; spec Overview as-built baseline |
| FF-05 | F11 | Feature-readiness freeze artifact not yet present — W3 doc deliverable | spec REQ-6; no freeze file in repo |

## Impact surface

| Wave / area | Likely files/modules | Test touch |
|-------------|----------------------|------------|
| W0 | `.harness-pin.yaml`, prove-out fixtures/checklist, `tests/config.yaml.example` | inspection + W0 checklist |
| W1 | `run_orchestrator.py`, forge publish path, `verify_spec_lane.py` | live `verify_spec_lane`; unit forge/orchestrator |
| W2 | closeout start, Pass-2 walker, learning ingest | `verify_wave_closeout` on spec PR tip |
| W3 | `.github/workflows/ci.yml`, freeze doc under `docs/specification/reports/`, as-built rows | CI run; `make check` + `make test`; inspection |

## Risks & assumptions

| ID | Risk / assumption | Mitigation |
|----|-------------------|------------|
| R-1 | Live prove-out env missing applied Postgres migration (Q-1 / A-6) | Fail closed on spec start; apply `1cd9a83a94a2` before W1 |
| R-2 | Forge creds / worker unavailable during W1 live walk | Document preflight in `verify_spec_lane` header; PE manual record fallback for authorize (Q-2 default) |
| R-3 | CI replacement blocks emergency merges | Spec rollback note (NFR migration row); keep job name `ci` |

## Recommended spec edits

- Update A-6 status when live env migration confirmed (or cite `1cd9a83a94a2` if applied).
- After W3, add freeze artifact path to REQ-6 evidence row when file is chosen.
- No blocking spec rewrites required before plan.

---

## Open items by lane

| ID | Lane | Question / item | Blocking | Owner | Status | Required by | Default if deferred | Evidence | Resolution reference |
|----|------|-----------------|----------|-------|--------|-------------|---------------------|----------|----------------------|
| Q-1 | PE | Alembic for `meta_pr_url` / `meta_head_sha` applied in live prove-out env? | no | PE | open | W1 live | Fail closed if columns missing | spec L146; migration file exists | as-built §006 |
| Q-2 | PE | Dedicated authorize verify script vs manual live record? | no | PE | open | W3 | Manual record with run id + URLs | spec L147 | PRD REQ-03 |
| Q-3 | PE | Exact CI check set beyond non-placeholder? | no | PE | open | W3 / plan | `make check` + `make test` | spec L148; Q-3 default | `.github/workflows/ci.yml` |
| Q-4 | PM | Vision note: meta link only vs duplicate in gateflow freeze? | no | PM | open | W3 freeze | Gateflow lists features; meta note in programme package | spec L149 | PRD REQ-04 AC-4 |
| AF-1 | auto-fix | Align as-built §006 meta-column gap + spec-lane dispatch row with migration + pin | no | PE | open | plan / W0 | Update as-built during plan publish | FF-01, FF-02 | `implementation-status.md` |

### PM questions (product scope, UX, priority)

#### Blocking — must resolve before spec merge

None.

#### Defer — can proceed with documented assumption

1. **Q-4** — Gateflow freeze lists feature names; meta vision note stays in programme package (lean default).

### PE questions (engineering decisions — resolved by `/spec-technical-review`)

#### Blocking for implementation plan

None — no NEW-ADR or ADR conflict.

#### Defer with default

1. **Q-1** — Confirm migration applied in live env before W1; migration file already in repo.
2. **Q-2** — Manual live authorize record acceptable per PRD.
3. **Q-3** — Default CI: `make check` + `make test`.

### Domain clarifications (business source-of-truth)

| # | Question | Suggested SME | Blocks |
|---|----------|---------------|--------|
| — | None | — | — |

### Auto-fixable (agent resolves later — not inside this skill)

| # | Item | Fix |
|---|------|-----|
| AF-1 | As-built drift on meta columns + spec-lane dispatch | Update `implementation-status.md` rows to match migration + pin |

---

## Check summary

| Check | Status | Findings |
|-------|--------|----------|
| F1 Baseline snapshot | PASS | FF-03, FF-04 (informational) |
| F2 Spec → code map | PASS | prove-out reuse mapped |
| F3 Spec → verify map | PASS | `verify_spec_lane`, `verify_wave_closeout`, `verify_board` |
| F4 Spec → unit map | PASS | cited unit modules exist |
| F5 As-built drift | PASS | FF-01, FF-02 Verify only |
| F6 Docs drift | PASS | tests README / AGENTS / ADR index aligned |
| F7 Overlap risk | PASS | live verify opt-in; unit uses mocks — no duplicate full journey |
| F8 CI vs live boundary | PASS | placeholder CI noted (FF-03) |
| F9 Cross-service touch | PASS | CTR-01…03 files/tests exist |
| F10 Assumptions | PASS | A-1…A-7 evidenced or flagged non-blocking |
| F11 Effort drivers | PASS | W0 fixtures → W1 live spec → W2 wrap-up → W3 authorize/CI/freeze |
| F12 PM questions | PASS | Q-4 non-blocking |
| F13 ADR conformance | PASS | ADR-009/010 aligned; no NEW-ADR |
| F14 MDC conformance | PASS | no rule conflicts |

**Check PASS** = zero unresolved blocking findings (informational OK).

---

## Next steps

> Persist this report locally alongside the spec draft. Fill `handoff.forge` for
> `/commit-workspace` (or Gateflow ForgeClient) onto the Draft spec PR —
> **do not** commit, push, open PRs, or apply labels inside this skill.
> Gate 2 label stays **`spec-pending`**.

1. **`/commit-workspace`** — publish spec + this report onto `chore/INIT-GATEFLOW-009-spec-gateflow`.
2. **`/spec-implementation-plan`** — wave plan for W0–W3 prove-outs (no PE blockers).
3. PE sets **`spec-lgtm`** only after spec + feasibility + plan on branch head — not during feasibility.

### Forge readiness

| Item | Value |
|------|-------|
| Local report path | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-009.md` |
| Target branch | `chore/INIT-GATEFLOW-009-spec-gateflow` |
| Recommended forge | `/commit-workspace` (Gate 2 stays `spec-pending`) |
| Mutations performed by this skill | **none** |

```
Draft spec PR: chore/INIT-GATEFLOW-009-spec-gateflow  (spec-pending)
When ready:
  [x] Source freshness is CURRENT
  [x] All blocking PM questions answered (none)
  [x] Zero blocking PE/ADR findings
  [ ] Spec + feasibility published on branch tip (Forge `/commit-workspace`)
  [ ] Proceed: /spec-implementation-plan
  [ ] After spec + feasibility + plan on branch: PE sets spec-lgtm + Approve → merge
  [ ] After merge: live prove-outs W0–W3 per plan
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: initiative-feasibility
  outcome: pass
  artifact:
    path: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-009.md
    digest: sha256:e9f9ea05901b710bc385cd1751e7f4f65ae818e8c671551f4e1c2b2964297397
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-009
    freshness: CURRENT
    ripple_action: continue
    map_revision: 1
    meta_pr_head: "6660aa4fefbcd80324cb970aa5bab642d3e5e0a1"
    prd_digest: sha256:76ab22b3c197b9d0cb6b08e6cea379c4e07b3a471b8a88203fddca6014c1c012
    scope_digest: sha256:d0a2b62632113db0fa64cb7d7e63dc393fa5a8217092dda242a99b3392978e9b
    spec_digest: sha256:69f68f455b19334f0f9a2f6ad9753927daa3d4f9fdc2e7a7fd4ea794d56c2f65
    new_adr: false
    findings_critical: 0
    findings_should_fix: 0
    findings_verify: 2
    findings_gap: 3
    nonblocking_questions: "Q-1,Q-2,Q-3,Q-4"
    outcome_rationale: "Gate 1 current; zero blocking PE/ADR; prove-out reuse buildable"
  next_candidates:
    - spec-implementation-plan
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    # Pin: initiative-feasibility forge.commit_workspace = required.
    # Publish spec + this report onto Draft spec PR branch — invoke /commit-workspace
    # (or Gateflow ForgeClient). Gate 2 stays spec-pending. This skill does not mutate.
```

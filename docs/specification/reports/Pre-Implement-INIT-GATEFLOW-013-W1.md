## Pre-implement — gateflow / W1 — Select/deselect repos; retire repos[]

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-013-W1.md` |
| Initiative | INIT-GATEFLOW-013 |
| Wave | W1 |
| Date | 2026-08-09 |
| Outcome | `pass` |
| Outcome reason | W0 Ground Report + human_approved; board #201 seeded; WorkManifest pass; P15 live verify contracted; H1–H3 CURRENT |
| Wave head context | Bound by Forge/human context: `develop` @ `d8e124342bc7c64cfe17abba74c8cfd12a92b42c` — recommended coding branch `feature/INIT-GATEFLOW-013-w1-repo-selection` (not opened by this skill) |

---

### Gate check (prior wave)

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | `develop` or `feature/INIT-*-w{N}-*` — not `chore/*-spec-*` | [x] ok — on `develop` |
| Spec PR merged | Implementation plan on integration | [x] yes — #198 merged |
| Coding-readiness at merge | `spec-lgtm` on merged spec PR | [x] verified |
| Board seed (read-only) | Wave issue + TASK ids | [x] seeded — W1 [#201](https://github.com/drivestream-lab/gateflow/issues/201) parent EPIC [#199](https://github.com/drivestream-lab/gateflow/issues/199) |
| WorkManifest contract | `prayog/v1` §9 pass | [x] pass |
| TASK exit proof | Every W1 TASK has exit + proof | [x] complete |
| Live-verification contract | P15 live script under `tests/verify/` | [x] `verify_repo_selection.py` |
| Plan / H1–H3 freshness | CURRENT | [x] current |
| Impact-map repo scope | match | [x] match — rev 1; scope `sha256:17921af2…` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live when P15 | [x] `.venv/bin/python -m tests.verify.verify_repo_selection` |
| `ground_command` | N/A reason | [x] N/A — Pass-2 `/ground-spec` |
| Co-shipped live verify (P15) | FILE path | [x] `tests/verify/verify_repo_selection.py` (TASK-W1-04) |
| Prior wave as-built row | `human_approved` | [x] INIT-013 W0 = human_approved |
| Prior Ground Report exists | W0 report | [x] `Ground-Report-INIT-GATEFLOW-013-W0.md` |
| Plan PE sign-off (W0 only) | N/A for W1 | [x] N/A |

**Gate verdict:** PASS

**Forge readiness:** `handoff.forge` → `/commit-workspace` to publish this checklist (recommend cut/bind `feature/INIT-GATEFLOW-013-w1-repo-selection` before `/loop-spec` coding).

---

### Contracts consumed (from prior Ground Report)

> Source: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-013-W0.md` §Contracts produced — confirmed against `src/` on `develop` @ `d8e1243`.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Programme connection | upsert/get by tenant_id | tenant_id, org, repo, optional ref | connection DTO (no PAT) | Ground-Report W0 | [x] yes — required before select |
| Catalogue API / parse | GET `…/programme/catalogue` / `parse_candidates` | connected tenant | candidates or named parse error | Ground-Report W0 | [x] yes — select validates against current candidates |
| Connect API | PUT `…/programme/connect` | org/repo/ref | connection | Ground-Report W0 | [x] yes — verify flow prerequisite |
| Tenant bearer zone | `verify_tenant_bearer_token` | bearer + path tenant_id | resolved context | ADR-011 / W0 | [x] yes |
| GithubPatProbe | `verify_read_access` | PAT, org, repo | ok / named reason | INIT-012 live | [x] yes — call at new select only (REQ-11) |
| Active run lookup | `find_active_run` (or equivalent) | org/repo | active run or none | INIT-012 W4 as-built | [x] yes — deselect guard (REQ-27); confirm call site in `/loop-spec` |

**Unconfirmed contracts:**
- Exact select/deselect OpenAPI paths — deferred to OpenAPI in `/loop-spec` (tenant-scoped; body models in `src/models/`).
- Setup + status in same request (TDD) — **not W1 scope**; W1 admits + probe + pending_setup shape; W2/W3 wire setup/status (plan TASK notes).
- PM-1 inventory of hand-typed `repos[]` dependents — non-blocking process gate before W1 merge (as-built/README/verify updates in TASK-W1-01).

---

### Must read

- [x] `AGENTS.md`
- [x] MDC (domain-filtered):
  - [x] `http-api-conventions.mdc` — body models for select/deselect; registration body break
  - [x] `pydantic-schemas.mdc` — models in `src/models/` only
  - [x] `repository-pattern.mdc` / `architecture.mdc` — business → repo; no ORM in service
  - [x] `fail-fast.mdc` / `logging-loguru.mdc` — named 422 reasons; structured kwargs
  - [x] `testing-verify-flows.mdc` / `python-tooling.mdc` — co-ship live verify
  - skipped: launchpad status / dual-evaluator MDCs (W3)
- [x] ADRs:
  - [x] ADR-012 — catalogue remains discovery authority for select validation
  - [x] ADR-011 — tenant bearer on select/deselect routes
  - skipped: ADR-013 (W3 readiness)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` (REQ-08–13, REQ-26–27)
- [x] Plan / §9 W1: `Implementation-Plan-INIT-GATEFLOW-013.md`
- [x] Board wave: https://github.com/drivestream-lab/gateflow/issues/201 — TASK list:
  - [x] TASK-W1-01 — REQ-12, REQ-13 — retire `repos[]` at registration; close alternate admit paths — proof: `make test`
  - [x] TASK-W1-02 — REQ-08–11, REQ-26–27 — select/deselect + PAT probe + ACTIVE-run guard — proof: `make check`
  - [x] TASK-W1-03 — REQ-08–13, REQ-26–27 — unit selection suite — proof: `make test`
  - [x] TASK-W1-04 — REQ-08,09,11,12,26,27 — live `verify_repo_selection` + README/as-built — proof: live FILE

---

### Governance alignment

- [x] Slice does not contradict ADR-012 / ADR-011
- [x] Plan TASK MDC/ADR notes for W1 reviewed
- [x] Selection must use **current** catalogue (REQ-10), not a snapshot frozen at connect
- [x] Deselect: membership only — do not delete clone or touch harness_verified (REQ-26)

---

### Must update (via `/loop-spec`)

- [ ] `TenantRegisterRequest` / register path — reject non-empty `repos` (or remove field); empty/absent only
- [ ] `verify_tenant_registry` + unit registration tests (AF-1)
- [ ] Select/deselect routes + `programme_selection_models.py` + repo active-list writers
- [ ] `tests/unit/test_programme_selection.py`
- [ ] `tests/verify/verify_repo_selection.py` + `tests/README.md` feature map
- [ ] `as-built/implementation-status.md` — INIT-013 W1 row

---

### Must not

- [ ] Wire Launchpad status or dual evaluators (W3)
- [ ] Require full setup batch success for admit (W2 owns setup wiring)
- [ ] Delete local clone or clear readiness on deselect
- [ ] Accept out-of-catalogue org/repo
- [ ] Add repos via any path other than selection after this wave
- [ ] Open branch / commit / PR / labels from this skill
- [ ] Ship select/deselect HTTP without co-shipped live verify (P15)

---

### Engineering contracts to produce (W1)

| Contract | Entry point | Input | Output / invariants |
|----------|-------------|-------|---------------------|
| Registration without repos | tenant register API | body without `repos` (or empty only) | tenant created with zero `tenant_repos`; non-empty `repos` → reject |
| Select active list | programme select API | list of {org,repo} ⊂ current catalogue | persist active membership; new admits run PAT probe; fail → 0 change |
| Deselect | programme deselect API | {org,repo} | membership removed; clone + harness_verified untouched; ACTIVE run → 422 |
| Per-repo admit result | select response | batch | per-repo admitted / probe_failed / pending_setup (setup later W2) |

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format, lint, types, layers | `make check` |
| Unit | select/deselect/probe/active-run/registration reject | `make test` |
| Live verify | human @ wave-acceptance | `.venv/bin/python -m tests.verify.verify_repo_selection` |
| Ground check | Pass-2 | N/A — `/ground-spec` |

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] Run `.venv/bin/python -m tests.verify.verify_repo_selection`
- [ ] Confirm registration rejects `repos[]`; select/deselect behaviour
- [ ] Label tip `wave-accepted` (human only)

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-013
- Issue: [#201](https://github.com/drivestream-lab/gateflow/issues/201) (EPIC [#199](https://github.com/drivestream-lab/gateflow/issues/199))
- Spec path: `docs/specification/product/INIT-GATEFLOW-013-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_repo_selection`
- ADRs in scope: ADR-012, ADR-011
- Wave head: `develop` @ `d8e1243…` (cut `feature/INIT-GATEFLOW-013-w1-repo-selection` before coding)
- Process note: PM-1 `repos[]` inventory before W1 merge (non-blocking)

---

### Checklist publish readiness (on `pass`)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — gates satisfied |
| Next | `loop-spec` |
| Forge (this hop) | `commit_workspace` **required** — publish this Pre-Implement file |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR |

Recommend `/commit-workspace` after authorization. Do not open the PR here.

---

### Merge order

N/A — single-repo W1. Depends on W0 catalogue + connection contracts (grounded).

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-013-W1.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-013
    wave: W1
    board_issue: https://github.com/drivestream-lab/gateflow/issues/201
    epic_issue: https://github.com/drivestream-lab/gateflow/issues/199
    tasks:
      - TASK-W1-01
      - TASK-W1-02
      - TASK-W1-03
      - TASK-W1-04
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_repo_selection
    ground_command: null
    workmanifest_contract: pass
    prior_wave_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-013-W0.md
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    head_ref: develop
    include_paths:
      - docs/specification/reports/Pre-Implement-INIT-GATEFLOW-013-W1.md
```

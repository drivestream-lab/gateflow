# Implementation plan — INIT-GATEFLOW-019 (gateflow)

| Field | Value |
|-------|-------|
| Status | **Review draft** — Gate 1 skipped; no board seed; not `/pre-implement` ready |
| Spec | `docs/specification/product/INIT-GATEFLOW-019-gateflow.md` |
| Date | 2026-08-15 |
| `check_command` | `make check` |
| `test_command` | `make test` |
| `verify_command` | per-wave FILE below |
| `ground_command` | N/A — no Makefile ground target |

Do not cut a feature branch from this file until PE accepts the local spec. CAP-D code already exists on `fix/session-grant-tenant-binding` @ `c575356` — W0 **grounds** it.

## Why this plan exists

Ops cannot offer the agreed walk until gateflow (1) lists attested meta PRs with a join, and (2) spec start resolves `{workspace_root}/{org}/{repo}` like implement. 016-ops D2 forbade that change; this INIT is that change.

## 1. Requirements

| ID | Summary | Wave |
|----|---------|------|
| REQ-12…16 | Grant tenant bind; auto-connect; connect=meta; list without board; Forge 404 empty | W0 |
| REQ-01…03, REQ-18…20 | Meta PR list + CAP-01 + spec-run join + onboard / admitted set | W1 |
| REQ-04…11, REQ-21 | Spec start resolve/omit; CAP-01 fail-closed; onboard required; implement slug default; closeout unchanged | W2 |

## 2. Waves

### W0 — Ground CAP-D (already coded)

**GOAL-W0:** As-built and tests own the `c575356` behaviours. No new product surface.

| Task | Implements | Files | Exit |
|------|------------|-------|------|
| TASK-W0-01 | REQ-12 | `auth_identity_service.py`, `programme_membership_repository.py`, `programme_membership_models.py`, `test_auth_identity_service.py` — already on branch | Login/me grants have `tenant_id` + `programme_name`; `make test` |
| TASK-W0-02 | REQ-13, REQ-14 | `programme_service.py`, `catalogue_connection_service.py`, `test_programme_service.py`, `test_programme_onboarding.py` — already on branch | Create auto-connects; connect defaults/rejects meta; `make test` |
| TASK-W0-03 | REQ-15, REQ-16 | `initiative_readout_service.py`, `forge_client.py`, matching units — already on branch | Board miss → runs still list; label 404 → `[]`; `make test` |
| TASK-W0-04 | REQ-12…16 | `Implementation-Status-INIT-GATEFLOW-019.md`; 017 as-built note stays “extended by 019”; `tests/README.md` feature map | As-built W0 = implemented (unit). Live: existing `verify_jwt_login` / onboarding / isolation — no new FILE required (P15 N/A: no new route) |

**verify_command (W0):** `.venv/bin/python -m tests.verify.verify_jwt_login` (human; grants shape). Not claimed by this plan.

### W1 — Meta PR picker (CAP-A)

**GOAL-W1:** Tenant-scoped list of INIT-* meta PRs with CAP-01 + join.

| Task | Implements | Files | Exit |
|------|------------|-------|------|
| TASK-W1-01 | REQ-01 | `forge_client.py` add list-PRs; programme meta org/repo from entered tenant | Lists open+merged; omit non-INIT; unit with mocked GitHub |
| TASK-W1-02 | REQ-02 | Reuse `CheckpointEvidenceService` `prd-impact-acceptance` per PR | Stale / missing label / blocked named; unit |
| TASK-W1-03 | REQ-03 | Join `RunRepository` spec runs (`meta_pr_url` / `initiative_id`) | `spec_run_id` or none; never invent; unit |
| TASK-W1-04 | REQ-01…03 | New route under `src/api/v1/` (name in TDD — e.g. `GET /tenants/{id}/meta/pulls`); models in `src/models/`; `tests/verify/verify_meta_pr_picker.py` | Live FILE: entered tenant, ≥1 INIT PR, CAP-01 fields present |

**verify_command (W1):** `.venv/bin/python -m tests.verify.verify_meta_pr_picker`

### W2 — Operator-shaped starts (CAP-B / CAP-C)

**GOAL-W2:** Spec start matches implement resolve; PE fields hidden; CAP-01 on the API.

| Task | Implements | Files | Exit |
|------|------------|-------|------|
| TASK-W2-01 | REQ-04, REQ-07 | `wave_start_service.start_spec_wave` resolve app+meta via `TenantGitWorkspaceClient`; paths optional | Omit paths → clone `{root}/{org}/{repo}`; unit + 422 on unregistered app repo |
| TASK-W2-02 | REQ-05, REQ-06, REQ-08 | `SpecWaveStartRequest` — optional `start_node` / `branch_slug` / `initiative_id` / runner+model; defaults from pin + `lane_defaults[spec]` | Head still `feature/{INIT}-spec`; empty defaults → named refuse; unit |
| TASK-W2-03 | REQ-09 | Spec start calls CAP-01; not satisfied → 422, 0 enqueue | Unit: missing label / stale |
| TASK-W2-04 | REQ-10, REQ-11 | Implement omitted slug → `implement`; closeout body unchanged | Unit; closeout tests still pass |
| TASK-W2-05 | REQ-04…11 | `tests/verify/verify_spec_start_binds.py`; `tests/README.md` | Live: attested meta PR, omit paths, run enqueues; unattested → 422 |

**verify_command (W2):** `.venv/bin/python -m tests.verify.verify_spec_start_binds`

## 3. Verification coverage

| Wave | Unit | Live |
|------|------|------|
| W0 | existing tests on branch | existing jwt/onboarding (human) |
| W1 | new picker units | `verify_meta_pr_picker` (P15 — new route) |
| W2 | wave_start units | `verify_spec_start_binds` (P15 — start contract change) |

## 4. Risks

| Risk | Mitigation |
|------|------------|
| List-PRs is a GitHub read from **gateflow** (allowed) vs ops scrape (forbidden) | Only ForgeClient in this repo |
| Spec start without CAP-01 today — curl bypass | REQ-09 on API in W2 |
| Dual workspace missing until connect | REQ-13 W0; resolve in W2 still 422 if PAT/root broken |
| Gate 1 skipped | No `spec-lgtm` / board tickets from this plan |

## 5. Coding-readiness (local only)

- [ ] PE accepts local 019 spec (no meta PRD)
- [ ] W0 commit is this INIT, not an unspec’d chore
- [ ] Ops W0 does not start until W1+W2 are consumable

```yaml
# Informal seed — not prayog/v1 board-ready (Gate 1 skipped)
workmanifest_draft:
  initiative: INIT-GATEFLOW-019
  repo: gateflow
  waves:
    - id: W0
      tasks: [TASK-W0-01, TASK-W0-02, TASK-W0-03, TASK-W0-04]
    - id: W1
      tasks: [TASK-W1-01, TASK-W1-02, TASK-W1-03, TASK-W1-04]
    - id: W2
      tasks: [TASK-W2-01, TASK-W2-02, TASK-W2-03, TASK-W2-04, TASK-W2-05]
```

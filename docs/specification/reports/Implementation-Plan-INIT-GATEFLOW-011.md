---
goal: INIT-GATEFLOW-011 — Day-1 visibility and GitHub reconcile
initiative: INIT-GATEFLOW-011
status: Planned
date_created: 2026-08-06
source_spec: docs/specification/product/INIT-GATEFLOW-011-gateflow.md
source_spec_digest: sha256:0edf9b72b5e66e9edb9686faddbe24ced7bfe5ca30aed4462dead234d7376ac4
feasibility_report: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-011.md
feasibility_digest: sha256:61cd10b2f402d517bd45e62cac3d165cdf39ff923293ea99f812729f32a8ace8
technical_review: docs/specification/reports/Technical-Review-INIT-GATEFLOW-011.md
technical_review_digest: sha256:aa68a3c65b213865884f7f2e7eaafd81123b7955a9ad58667092a51f5e8a5e30
prd_digest: sha256:eca06cbe986d619db58ae3ca84f4ec0987c19aa19b8f1485693280c6a655e4dd
impact_map: prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-011.md
impact_map_revision: 1
repo_scope_digest: sha256:afdc7bd51bcd0c12f614feebf338bdc78766396bb84777121a2565c0ecc7966d
approved_meta_pr_head: f3da8148f3e861fad4720a3491f11f1fdc0145aa
branch: chore/INIT-GATEFLOW-011-spec-gateflow
review_deadline: 2026-08-11
deciders: PE @drivestream-lab/prayog-pe-team — spec-lgtm + Approve on exact head after full package
---

# Implementation plan — INIT-GATEFLOW-011

## Source freshness and command contract

| Item | Value | Status |
|------|-------|--------|
| Spec / digest | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` / `sha256:0edf9b72b5e66e9edb9686faddbe24ced7bfe5ca30aed4462dead234d7376ac4` | CURRENT |
| Feasibility / digest | `…/Initiative-Feasibility-Report-INIT-GATEFLOW-011.md` / `sha256:61cd10b2f402d517bd45e62cac3d165cdf39ff923293ea99f812729f32a8ace8` | CURRENT |
| Technical review / digest | `…/Technical-Review-INIT-GATEFLOW-011.md` / `sha256:aa68a3c65b213865884f7f2e7eaafd81123b7955a9ad58667092a51f5e8a5e30` | CURRENT — **Accepted** |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-011.md` / `1` | CURRENT |
| Repo scope digest | `sha256:afdc7bd51bcd0c12f614feebf338bdc78766396bb84777121a2565c0ecc7966d` | CURRENT |
| Approved meta PR head | `f3da8148f3e861fad4720a3491f11f1fdc0145aa` | CURRENT (G1) |
| `check_command` | `make check` | RESOLVED |
| `test_command` | `make test` | RESOLVED |
| `verify_command` | Per-wave under `tests/verify/` (see phases) | RESOLVED |
| `ground_command` | N/A — `/ground-spec` is Pass-2 pin skill, not a Makefile target | N/A |

## 0. Technical design reference

| Item | Value |
|------|-------|
| Technical review | [`Technical-Review-INIT-GATEFLOW-011.md`](Technical-Review-INIT-GATEFLOW-011.md) |
| Technical review status | **Accepted** |
| PE sign-off | [x] complete — 2026-08-06 (Cursor chat: TDD accepted; proceed to plan) |
| Resolved ADRs | none required — light confirmation, zero NEW-ADR; cite Accepted ADR-001/003/004/005/009/010 as constraints |
| ADR product-boundary re-check | N/A — no ADR_REQUIRED Draft/Accepted files from this INIT |
| Outstanding PM questions | PM-1 / Q-1 OpenAPI field names (non-blocking) |
| Outstanding domain questions | none |

> Do not start W0 coding until this plan is on tip with coding-readiness unlock
> (`spec-lgtm` + Approve on exact head), then merge + `/create-board-tickets`.
> Note: PR #159 may already show `spec-lgtm` early — attestation must still
> match the head that contains **this plan**.

## 1. Requirements (REQ) — product ids

| ID | Summary | Spec path | Waves |
|----|---------|-----------|-------|
| REQ-01 | Checkpoint status-check accepts pin checkpoint id + PR refs; read-only | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W0 |
| REQ-02 | Evidence from pinned delivery-contract labels+review_roles+checks live at head | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W0 |
| REQ-03 | checked_sha/checked_at; stale evidence → not_satisfied | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W1 |
| REQ-04 | Non-pass lists missing items by name | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W0 |
| REQ-05 | Status-check never mutates GitHub/board | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W0 |
| REQ-06 | Persist check record on every CAP-01 call | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W1 |
| REQ-07 | History labeled historical; never substitutes live | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W1 |
| REQ-08 | Composed checkpoint readout via initiative+wave | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W1 |
| REQ-09 | Initiative list/detail fields incl PRD approval | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W2, W3 |
| REQ-10 | Composition from Gateflow-owned data (+ one meta read) | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W2 |
| REQ-11 | Meta unreachable → partial 200 unavailable | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W3 |
| REQ-12 | Spec-lane readout fields from pin+run | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W5 |
| REQ-13 | Plain not-ready before spec-pr-action | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W5 |
| REQ-14 | Wave map statuses + block reason | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W4 |
| REQ-15 | Wave status from board/run only | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W4 |
| REQ-16 | Implementation task progress + Draft PR link | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W6 |
| REQ-17 | Named task+reason on failure/stop | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W6 |
| REQ-18 | Closeout lists learning/ground additions | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W7 |
| REQ-19 | Drift safeguard vs acceptance baseline | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W7 |
| REQ-20 | Drift advisory only | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W7 |
| REQ-21 | Merge confirm via CAP-01 wave-signoff | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W8 |
| REQ-22 | Next-wave unblocked nudge | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W8 |
| REQ-23 | Completion eligibility Done rollup | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W8 |
| REQ-24 | Completion reuses CAP-05 logic only | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W8 |
| REQ-25 | Closure preview pre-purge from purge manifest | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W9 |
| REQ-26 | Closure preview post-purge actuals | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W9 |
| REQ-27 | Closure signoff reuses CAP-01 | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W9 |
| REQ-28 | GET-only; no mutate from CAP paths | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | W0, W1, W2, W3, W4, W5, W6, W7, W8, W9 |

---

## 2. Implementation phases

### Phase W0 — Checkpoint status-check foundation

**GOAL-W0:** Ship live read-only CAP-01: ForgeClient read extension, pin contract vocabulary, CheckpointEvidenceService, GET /api/v1/checkpoints/status (no persistence).

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W0-01 | list_reviews, list_check_runs, and merge fields available on read path | REQ-02 | — | `src/infra_services/forge_client.py` modify; `src/models/meta_pr_models.py` modify; `tests/unit/test_forge_client.py` modify | list_reviews, list_check_runs, and merge fields available on read path; unit green | command / `make check && make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W0.md § TASK-W0-01 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_checkpoint_status` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w0-checkpoint-status` |
| TASK-W0-02 | All six checkpoint ids resolve labels+review_roles from pinned deliver | REQ-02 | TASK-W0-01 | `src/business_services/workflow_engine.py` modify; `src/models/checkpoint_models.py` create; `tests/unit/test_checkpoint_vocab.py` create | All six checkpoint ids resolve labels+review_roles from pinned delivery-contract.yaml | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W0.md § TASK-W0-02 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_checkpoint_status` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w0-checkpoint-status` |
| TASK-W0-03 | evaluate() returns itemized misses; GitHub down → could_not_verify; ze | REQ-01, REQ-04, REQ-05 | TASK-W0-01, TASK-W0-02 | `src/business_services/checkpoint_evidence_service.py` create; `tests/unit/test_checkpoint_evidence.py` create; `src/di/modules/business_services_module.py` modify; `src/di/dependency_container.py` modify | evaluate() returns itemized misses; GitHub down → could_not_verify; zero mutate ForgeClient calls | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W0.md § TASK-W0-03 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_checkpoint_status` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w0-checkpoint-status` |
| TASK-W0-04 | GET /api/v1/checkpoints/status programme-token; non-GET rejected; publ | REQ-01, REQ-05, REQ-28 | TASK-W0-03 | `src/api/v1/checkpoints_routes.py` create; `src/api/v1/__init__.py` modify; `src/app.py` modify; `tests/unit/test_checkpoints_api.py` create | GET /api/v1/checkpoints/status programme-token; non-GET rejected; public_paths includes /api/v1/checkpoints | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W0.md § TASK-W0-04 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_checkpoint_status` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w0-checkpoint-status` |
| TASK-W0-05 | Live verify exit 0; feature-map + as-built W0 row present | REQ-01, REQ-05, REQ-28 | TASK-W0-04 | `tests/verify/verify_checkpoint_status.py` create; `tests/README.md` modify; `docs/specification/as-built/implementation-status.md` modify | Live verify exit 0; feature-map + as-built W0 row present | command / `make check && make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W0.md § TASK-W0-05 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_checkpoint_status` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w0-checkpoint-status` |

#### Files (W0)

| ID | Path | Action |
|----|------|--------|
| FILE-W0-01 | `src/infra_services/forge_client.py` | modify |
| FILE-W0-02 | `src/models/meta_pr_models.py` | modify |
| FILE-W0-03 | `tests/unit/test_forge_client.py` | modify |
| FILE-W0-04 | `src/business_services/workflow_engine.py` | modify |
| FILE-W0-05 | `src/models/checkpoint_models.py` | create |
| FILE-W0-06 | `tests/unit/test_checkpoint_vocab.py` | create |
| FILE-W0-07 | `src/business_services/checkpoint_evidence_service.py` | create |
| FILE-W0-08 | `tests/unit/test_checkpoint_evidence.py` | create |
| FILE-W0-09 | `src/di/modules/business_services_module.py` | modify |
| FILE-W0-10 | `src/di/dependency_container.py` | modify |
| FILE-W0-11 | `src/api/v1/checkpoints_routes.py` | create |
| FILE-W0-12 | `src/api/v1/__init__.py` | modify |
| FILE-W0-13 | `src/app.py` | modify |
| FILE-W0-14 | `tests/unit/test_checkpoints_api.py` | create |
| FILE-W0-15 | `tests/verify/verify_checkpoint_status.py` | create |
| FILE-W0-16 | `tests/README.md` | modify |
| FILE-W0-17 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W0)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W0-U | unit | `make test` | REQ-01, REQ-02, REQ-04, REQ-05, REQ-28 |
| TEST-W0-I | integration/contract | N/A — ForgeClient/httpx doubled in unit | — |
| TEST-W0-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_checkpoint_status` | P15 surface |

#### Verification Coverage (W0)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-01 | TEST-W0-U | N/A | TEST-W0-L | N/A | |
| REQ-02 | TEST-W0-U | N/A | TEST-W0-L | N/A | |
| REQ-04 | TEST-W0-U | N/A | TEST-W0-L | N/A | |
| REQ-05 | TEST-W0-U | N/A | TEST-W0-L | N/A | |
| REQ-28 | TEST-W0-U | N/A | TEST-W0-L | N/A | |

#### Live-verification intent (W0)

| Field | Value |
|-------|-------|
| Applicable | **yes** — new/changed GET product surface (P15) |
| Environment class | local-compose (`make run`) |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` against wave PR tip |
| Prerequisites | Programme token; `tests/config.yaml`; fixture PR where GitHub evidence required |
| Safe test data | Non-prod fixture org/repo/PR; no label/merge mutations |
| Steps / command | `.venv/bin/python -m tests.verify.verify_checkpoint_status` |
| Expected observations | exit 0; assertions for wave REQs |
| Expected evidence | `wave-accepted` on tip |
| Cleanup | none (read-only) |
| Stop conditions | non-zero exit; unexpected write call |

### Phase W1 — Check persistence + composed readout

**GOAL-W1:** Persist every CAP-01 attempt; expose history (historical) and composed initiative/wave checkpoint readout with checked_sha/checked_at/stale.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W1-01 | Every evaluate attempt appends checkpoint_check run_event with require | REQ-06 | — | `src/models/policy_types.py` modify; `src/models/run_store_models.py` modify; `src/database/postgres/repository/run_store_repository.py` modify; `src/business_services/checkpoint_evidence_service.py` modify; `tests/unit/test_checkpoint_persistence.py` create | Every evaluate attempt appends checkpoint_check run_event with required payload fields | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W1.md § TASK-W1-01 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_checkpoint_history` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w1-checkpoint-persistence` |
| TASK-W1-02 | Stale evidence → not_satisfied with stale reason; checked_sha and chec | REQ-03 | TASK-W1-01 | `src/business_services/checkpoint_evidence_service.py` modify; `tests/unit/test_checkpoint_evidence.py` modify | Stale evidence → not_satisfied with stale reason; checked_sha and checked_at always present | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W1.md § TASK-W1-02 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_checkpoint_history` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w1-checkpoint-persistence` |
| TASK-W1-03 | GET /checkpoints/history marks records historical; never claims live v | REQ-07, REQ-28 | TASK-W1-01 | `src/api/v1/checkpoints_routes.py` modify; `tests/unit/test_checkpoints_api.py` modify | GET /checkpoints/history marks records historical; never claims live verdict | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W1.md § TASK-W1-03 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_checkpoint_history` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w1-checkpoint-persistence` |
| TASK-W1-04 | Composed readout via initiative+wave; 404 no run found for this wave w | REQ-08, REQ-28 | TASK-W1-02, TASK-W1-03 | `src/business_services/checkpoint_evidence_service.py` modify; `src/api/v1/checkpoints_routes.py` modify; `tests/unit/test_checkpoints_api.py` modify | Composed readout via initiative+wave; 404 no run found for this wave when unresolved | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W1.md § TASK-W1-04 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_checkpoint_history` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w1-checkpoint-persistence` |
| TASK-W1-05 | Live verify exit 0 covering persist/stale/404; as-built W1 row | REQ-03, REQ-06, REQ-07, REQ-08, REQ-28 | TASK-W1-04 | `tests/verify/verify_checkpoint_history.py` create; `tests/README.md` modify; `docs/specification/as-built/implementation-status.md` modify | Live verify exit 0 covering persist/stale/404; as-built W1 row | command / `make check && make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W1.md § TASK-W1-05 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_checkpoint_history` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w1-checkpoint-persistence` |

#### Files (W1)

| ID | Path | Action |
|----|------|--------|
| FILE-W1-01 | `src/models/policy_types.py` | modify |
| FILE-W1-02 | `src/models/run_store_models.py` | modify |
| FILE-W1-03 | `src/database/postgres/repository/run_store_repository.py` | modify |
| FILE-W1-04 | `src/business_services/checkpoint_evidence_service.py` | modify |
| FILE-W1-05 | `tests/unit/test_checkpoint_persistence.py` | create |
| FILE-W1-06 | `tests/unit/test_checkpoint_evidence.py` | modify |
| FILE-W1-07 | `src/api/v1/checkpoints_routes.py` | modify |
| FILE-W1-08 | `tests/unit/test_checkpoints_api.py` | modify |
| FILE-W1-09 | `tests/verify/verify_checkpoint_history.py` | create |
| FILE-W1-10 | `tests/README.md` | modify |
| FILE-W1-11 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W1)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W1-U | unit | `make test` | REQ-03, REQ-06, REQ-07, REQ-08, REQ-28 |
| TEST-W1-I | integration/contract | N/A — ForgeClient/httpx doubled in unit | — |
| TEST-W1-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_checkpoint_history` | P15 surface |

#### Verification Coverage (W1)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-03 | TEST-W1-U | N/A | TEST-W1-L | N/A | |
| REQ-06 | TEST-W1-U | N/A | TEST-W1-L | N/A | |
| REQ-07 | TEST-W1-U | N/A | TEST-W1-L | N/A | |
| REQ-08 | TEST-W1-U | N/A | TEST-W1-L | N/A | |
| REQ-28 | TEST-W1-U | N/A | TEST-W1-L | N/A | |

#### Live-verification intent (W1)

| Field | Value |
|-------|-------|
| Applicable | **yes** — new/changed GET product surface (P15) |
| Environment class | local-compose (`make run`) |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` against wave PR tip |
| Prerequisites | Programme token; `tests/config.yaml`; fixture PR where GitHub evidence required |
| Safe test data | Non-prod fixture org/repo/PR; no label/merge mutations |
| Steps / command | `.venv/bin/python -m tests.verify.verify_checkpoint_history` |
| Expected observations | exit 0; assertions for wave REQs |
| Expected evidence | `wave-accepted` on tip |
| Cleanup | none (read-only) |
| Stop conditions | non-zero exit; unexpected write call |

### Phase W2 — Initiative list/detail (Gateflow-owned)

**GOAL-W2:** GET /initiatives and /initiatives/{id} from runs+board; PRD approval field unavailable until W3.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W2-01 | List/detail returns Gateflow-owned fields; prd_approval=unavailable | REQ-09, REQ-10 | — | `src/business_services/initiative_readout_service.py` create; `src/models/initiative_readout_models.py` create; `tests/unit/test_initiative_readout.py` create; `src/di/modules/business_services_module.py` modify | List/detail returns Gateflow-owned fields; prd_approval=unavailable | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W2.md § TASK-W2-01 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_initiatives_readout` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w2-initiatives-owned` |
| TASK-W2-02 | GET list/detail routes programme-token; GET-only guard | REQ-09, REQ-10, REQ-28 | TASK-W2-01 | `src/api/v1/initiatives_routes.py` modify; `tests/unit/test_initiatives_read_api.py` create | GET list/detail routes programme-token; GET-only guard | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W2.md § TASK-W2-02 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_initiatives_readout` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w2-initiatives-owned` |
| TASK-W2-03 | Live smoke exit 0; as-built W2 row | REQ-09, REQ-10, REQ-28 | TASK-W2-02 | `tests/verify/verify_initiatives_readout.py` create; `tests/README.md` modify; `docs/specification/as-built/implementation-status.md` modify | Live smoke exit 0; as-built W2 row | command / `make check && make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W2.md § TASK-W2-03 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_initiatives_readout` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w2-initiatives-owned` |

#### Files (W2)

| ID | Path | Action |
|----|------|--------|
| FILE-W2-01 | `src/business_services/initiative_readout_service.py` | create |
| FILE-W2-02 | `src/models/initiative_readout_models.py` | create |
| FILE-W2-03 | `tests/unit/test_initiative_readout.py` | create |
| FILE-W2-04 | `src/di/modules/business_services_module.py` | modify |
| FILE-W2-05 | `src/api/v1/initiatives_routes.py` | modify |
| FILE-W2-06 | `tests/unit/test_initiatives_read_api.py` | create |
| FILE-W2-07 | `tests/verify/verify_initiatives_readout.py` | create |
| FILE-W2-08 | `tests/README.md` | modify |
| FILE-W2-09 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W2)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W2-U | unit | `make test` | REQ-09, REQ-10, REQ-28 |
| TEST-W2-I | integration/contract | N/A — ForgeClient/httpx doubled in unit | — |
| TEST-W2-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_initiatives_readout` | P15 surface |

#### Verification Coverage (W2)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-09 | TEST-W2-U | N/A | TEST-W2-L | N/A | |
| REQ-10 | TEST-W2-U | N/A | TEST-W2-L | N/A | |
| REQ-28 | TEST-W2-U | N/A | TEST-W2-L | N/A | |

#### Live-verification intent (W2)

| Field | Value |
|-------|-------|
| Applicable | **yes** — new/changed GET product surface (P15) |
| Environment class | local-compose (`make run`) |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` against wave PR tip |
| Prerequisites | Programme token; `tests/config.yaml`; fixture PR where GitHub evidence required |
| Safe test data | Non-prod fixture org/repo/PR; no label/merge mutations |
| Steps / command | `.venv/bin/python -m tests.verify.verify_initiatives_readout` |
| Expected observations | exit 0; assertions for wave REQs |
| Expected evidence | `wave-accepted` on tip |
| Cleanup | none (read-only) |
| Stop conditions | non-zero exit; unexpected write call |

### Phase W3 — Meta bridge + partial success

**GOAL-W3:** Complete initiative PRD-approval via read-only meta CAP-01; meta-down → 200 with unavailable.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W3-01 | PRD approval populated via CAP-01 against prd-impact-acceptance on met | REQ-09 | — | `src/business_services/initiative_readout_service.py` modify; `tests/unit/test_initiative_readout.py` modify | PRD approval populated via CAP-01 against prd-impact-acceptance on meta PR | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W3.md § TASK-W3-01 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_initiative_meta_bridge` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w3-meta-bridge` |
| TASK-W3-02 | Meta unreachable → HTTP 200; meta fields unavailable; owned fields pre | REQ-11 | TASK-W3-01 | `src/business_services/initiative_readout_service.py` modify; `tests/unit/test_initiative_readout.py` modify | Meta unreachable → HTTP 200; meta fields unavailable; owned fields present | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W3.md § TASK-W3-02 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_initiative_meta_bridge` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w3-meta-bridge` |
| TASK-W3-03 | Live meta-up + meta-down paths; as-built W3 row | REQ-09, REQ-11, REQ-28 | TASK-W3-02 | `tests/verify/verify_initiative_meta_bridge.py` create; `tests/README.md` modify; `docs/specification/as-built/implementation-status.md` modify | Live meta-up + meta-down paths; as-built W3 row | command / `make check && make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W3.md § TASK-W3-03 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_initiative_meta_bridge` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w3-meta-bridge` |

#### Files (W3)

| ID | Path | Action |
|----|------|--------|
| FILE-W3-01 | `src/business_services/initiative_readout_service.py` | modify |
| FILE-W3-02 | `tests/unit/test_initiative_readout.py` | modify |
| FILE-W3-03 | `tests/verify/verify_initiative_meta_bridge.py` | create |
| FILE-W3-04 | `tests/README.md` | modify |
| FILE-W3-05 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W3)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W3-U | unit | `make test` | REQ-09, REQ-11, REQ-28 |
| TEST-W3-I | integration/contract | N/A — ForgeClient/httpx doubled in unit | — |
| TEST-W3-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_initiative_meta_bridge` | P15 surface |

#### Verification Coverage (W3)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-09 | TEST-W3-U | N/A | TEST-W3-L | N/A | |
| REQ-11 | TEST-W3-U | N/A | TEST-W3-L | N/A | |
| REQ-28 | TEST-W3-U | N/A | TEST-W3-L | N/A | |

#### Live-verification intent (W3)

| Field | Value |
|-------|-------|
| Applicable | **yes** — new/changed GET product surface (P15) |
| Environment class | local-compose (`make run`) |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` against wave PR tip |
| Prerequisites | Programme token; `tests/config.yaml`; fixture PR where GitHub evidence required |
| Safe test data | Non-prod fixture org/repo/PR; no label/merge mutations |
| Steps / command | `.venv/bin/python -m tests.verify.verify_initiative_meta_bridge` |
| Expected observations | exit 0; assertions for wave REQs |
| Expected evidence | `wave-accepted` on tip |
| Cleanup | none (read-only) |
| Stop conditions | non-zero exit; unexpected write call |

### Phase W4 — Wave map readout

**GOAL-W4:** GET /initiatives/{id}/waves returns done/ready-to-start/blocked/active from board+run data only.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W4-01 | Per-wave status + block reason; no new wave-state store | REQ-14, REQ-15 | — | `src/business_services/wave_map_service.py` create; `src/models/wave_map_models.py` create; `tests/unit/test_wave_map_service.py` create | Per-wave status + block reason; no new wave-state store | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W4.md § TASK-W4-01 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_wave_map` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w4-wave-map` |
| TASK-W4-02 | GET .../waves route wired GET-only | REQ-14, REQ-15, REQ-28 | TASK-W4-01 | `src/api/v1/initiatives_routes.py` modify; `tests/unit/test_initiatives_read_api.py` modify | GET .../waves route wired GET-only | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W4.md § TASK-W4-02 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_wave_map` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w4-wave-map` |
| TASK-W4-03 | Live wave-map smoke; as-built W4 row | REQ-14, REQ-28 | TASK-W4-02 | `tests/verify/verify_wave_map.py` create; `tests/README.md` modify; `docs/specification/as-built/implementation-status.md` modify | Live wave-map smoke; as-built W4 row | command / `make check && make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W4.md § TASK-W4-03 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_wave_map` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w4-wave-map` |

#### Files (W4)

| ID | Path | Action |
|----|------|--------|
| FILE-W4-01 | `src/business_services/wave_map_service.py` | create |
| FILE-W4-02 | `src/models/wave_map_models.py` | create |
| FILE-W4-03 | `tests/unit/test_wave_map_service.py` | create |
| FILE-W4-04 | `src/api/v1/initiatives_routes.py` | modify |
| FILE-W4-05 | `tests/unit/test_initiatives_read_api.py` | modify |
| FILE-W4-06 | `tests/verify/verify_wave_map.py` | create |
| FILE-W4-07 | `tests/README.md` | modify |
| FILE-W4-08 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W4)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W4-U | unit | `make test` | REQ-14, REQ-15, REQ-28 |
| TEST-W4-I | integration/contract | N/A — ForgeClient/httpx doubled in unit | — |
| TEST-W4-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_wave_map` | P15 surface |

#### Verification Coverage (W4)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-14 | TEST-W4-U | N/A | TEST-W4-L | N/A | |
| REQ-15 | TEST-W4-U | N/A | TEST-W4-L | N/A | |
| REQ-28 | TEST-W4-U | N/A | TEST-W4-L | N/A | |

#### Live-verification intent (W4)

| Field | Value |
|-------|-------|
| Applicable | **yes** — new/changed GET product surface (P15) |
| Environment class | local-compose (`make run`) |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` against wave PR tip |
| Prerequisites | Programme token; `tests/config.yaml`; fixture PR where GitHub evidence required |
| Safe test data | Non-prod fixture org/repo/PR; no label/merge mutations |
| Steps / command | `.venv/bin/python -m tests.verify.verify_wave_map` |
| Expected observations | exit 0; assertions for wave REQs |
| Expected evidence | `wave-accepted` on tip |
| Cleanup | none (read-only) |
| Stop conditions | non-zero exit; unexpected write call |

### Phase W5 — Spec lane readout

**GOAL-W5:** GET /initiatives/{id}/spec returns pin+run fields; plain not-ready before spec-pr-action.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W5-01 | Fields from pin+run; not-ready message when no Draft Spec PR | REQ-12, REQ-13 | — | `src/business_services/spec_readout_service.py` create; `src/models/spec_readout_models.py` create; `tests/unit/test_spec_readout_service.py` create | Fields from pin+run; not-ready message when no Draft Spec PR | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W5.md § TASK-W5-01 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_spec_readout` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w5-spec-readout` |
| TASK-W5-02 | GET .../spec GET-only route | REQ-12, REQ-13, REQ-28 | TASK-W5-01 | `src/api/v1/initiatives_routes.py` modify; `tests/unit/test_initiatives_read_api.py` modify | GET .../spec GET-only route | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W5.md § TASK-W5-02 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_spec_readout` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w5-spec-readout` |
| TASK-W5-03 | Live spec readout smoke; as-built W5 row | REQ-12, REQ-28 | TASK-W5-02 | `tests/verify/verify_spec_readout.py` create; `tests/README.md` modify; `docs/specification/as-built/implementation-status.md` modify | Live spec readout smoke; as-built W5 row | command / `make check && make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W5.md § TASK-W5-03 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_spec_readout` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w5-spec-readout` |

#### Files (W5)

| ID | Path | Action |
|----|------|--------|
| FILE-W5-01 | `src/business_services/spec_readout_service.py` | create |
| FILE-W5-02 | `src/models/spec_readout_models.py` | create |
| FILE-W5-03 | `tests/unit/test_spec_readout_service.py` | create |
| FILE-W5-04 | `src/api/v1/initiatives_routes.py` | modify |
| FILE-W5-05 | `tests/unit/test_initiatives_read_api.py` | modify |
| FILE-W5-06 | `tests/verify/verify_spec_readout.py` | create |
| FILE-W5-07 | `tests/README.md` | modify |
| FILE-W5-08 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W5)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W5-U | unit | `make test` | REQ-12, REQ-13, REQ-28 |
| TEST-W5-I | integration/contract | N/A — ForgeClient/httpx doubled in unit | — |
| TEST-W5-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_spec_readout` | P15 surface |

#### Verification Coverage (W5)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-12 | TEST-W5-U | N/A | TEST-W5-L | N/A | |
| REQ-13 | TEST-W5-U | N/A | TEST-W5-L | N/A | |
| REQ-28 | TEST-W5-U | N/A | TEST-W5-L | N/A | |

#### Live-verification intent (W5)

| Field | Value |
|-------|-------|
| Applicable | **yes** — new/changed GET product surface (P15) |
| Environment class | local-compose (`make run`) |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` against wave PR tip |
| Prerequisites | Programme token; `tests/config.yaml`; fixture PR where GitHub evidence required |
| Safe test data | Non-prod fixture org/repo/PR; no label/merge mutations |
| Steps / command | `.venv/bin/python -m tests.verify.verify_spec_readout` |
| Expected observations | exit 0; assertions for wave REQs |
| Expected evidence | `wave-accepted` on tip |
| Cleanup | none (read-only) |
| Stop conditions | non-zero exit; unexpected write call |

### Phase W6 — Wave implementation progress

**GOAL-W6:** GET .../waves/{wave_id}/implementation returns task timeline, Draft PR link, and named failure on stop.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W6-01 | Per-task progress + Draft PR when present; named task+reason on failur | REQ-16, REQ-17 | — | `src/business_services/implementation_readout_service.py` create; `src/models/implementation_readout_models.py` create; `tests/unit/test_implementation_readout_service.py` create | Per-task progress + Draft PR when present; named task+reason on failure | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W6.md § TASK-W6-01 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_wave_implementation` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w6-implementation-readout` |
| TASK-W6-02 | GET .../implementation GET-only route | REQ-16, REQ-17, REQ-28 | TASK-W6-01 | `src/api/v1/initiatives_routes.py` modify; `tests/unit/test_initiatives_read_api.py` modify | GET .../implementation GET-only route | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W6.md § TASK-W6-02 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_wave_implementation` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w6-implementation-readout` |
| TASK-W6-03 | Live implementation smoke; as-built W6 row | REQ-16, REQ-28 | TASK-W6-02 | `tests/verify/verify_wave_implementation.py` create; `tests/README.md` modify; `docs/specification/as-built/implementation-status.md` modify | Live implementation smoke; as-built W6 row | command / `make check && make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W6.md § TASK-W6-03 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_wave_implementation` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w6-implementation-readout` |

#### Files (W6)

| ID | Path | Action |
|----|------|--------|
| FILE-W6-01 | `src/business_services/implementation_readout_service.py` | create |
| FILE-W6-02 | `src/models/implementation_readout_models.py` | create |
| FILE-W6-03 | `tests/unit/test_implementation_readout_service.py` | create |
| FILE-W6-04 | `src/api/v1/initiatives_routes.py` | modify |
| FILE-W6-05 | `tests/unit/test_initiatives_read_api.py` | modify |
| FILE-W6-06 | `tests/verify/verify_wave_implementation.py` | create |
| FILE-W6-07 | `tests/README.md` | modify |
| FILE-W6-08 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W6)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W6-U | unit | `make test` | REQ-16, REQ-17, REQ-28 |
| TEST-W6-I | integration/contract | N/A — ForgeClient/httpx doubled in unit | — |
| TEST-W6-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_wave_implementation` | P15 surface |

#### Verification Coverage (W6)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-16 | TEST-W6-U | N/A | TEST-W6-L | N/A | |
| REQ-17 | TEST-W6-U | N/A | TEST-W6-L | N/A | |
| REQ-28 | TEST-W6-U | N/A | TEST-W6-L | N/A | |

#### Live-verification intent (W6)

| Field | Value |
|-------|-------|
| Applicable | **yes** — new/changed GET product surface (P15) |
| Environment class | local-compose (`make run`) |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` against wave PR tip |
| Prerequisites | Programme token; `tests/config.yaml`; fixture PR where GitHub evidence required |
| Safe test data | Non-prod fixture org/repo/PR; no label/merge mutations |
| Steps / command | `.venv/bin/python -m tests.verify.verify_wave_implementation` |
| Expected observations | exit 0; assertions for wave REQs |
| Expected evidence | `wave-accepted` on tip |
| Cleanup | none (read-only) |
| Stop conditions | non-zero exit; unexpected write call |

### Phase W7 — Closeout readout + drift safeguard

**GOAL-W7:** Closeout GET lists learning/ground additions; advisory drift vs wave-acceptance baseline from W1 records.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W7-01 | Itemized closeout additions; drift or unknown baseline; advisory only | REQ-18, REQ-19, REQ-20 | — | `src/business_services/closeout_readout_service.py` create; `src/models/closeout_readout_models.py` create; `tests/unit/test_closeout_readout_service.py` create | Itemized closeout additions; drift or unknown baseline; advisory only | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W7.md § TASK-W7-01 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_wave_closeout_readout` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w7-closeout-drift` |
| TASK-W7-02 | GET .../closeout GET-only route | REQ-18, REQ-19, REQ-20, REQ-28 | TASK-W7-01 | `src/api/v1/initiatives_routes.py` modify; `tests/unit/test_initiatives_read_api.py` modify | GET .../closeout GET-only route | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W7.md § TASK-W7-02 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_wave_closeout_readout` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w7-closeout-drift` |
| TASK-W7-03 | Live closeout+drift smoke; as-built W7 row | REQ-18, REQ-19, REQ-28 | TASK-W7-02 | `tests/verify/verify_wave_closeout_readout.py` create; `tests/README.md` modify; `docs/specification/as-built/implementation-status.md` modify | Live closeout+drift smoke; as-built W7 row | command / `make check && make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W7.md § TASK-W7-03 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_wave_closeout_readout` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w7-closeout-drift` |

#### Files (W7)

| ID | Path | Action |
|----|------|--------|
| FILE-W7-01 | `src/business_services/closeout_readout_service.py` | create |
| FILE-W7-02 | `src/models/closeout_readout_models.py` | create |
| FILE-W7-03 | `tests/unit/test_closeout_readout_service.py` | create |
| FILE-W7-04 | `src/api/v1/initiatives_routes.py` | modify |
| FILE-W7-05 | `tests/unit/test_initiatives_read_api.py` | modify |
| FILE-W7-06 | `tests/verify/verify_wave_closeout_readout.py` | create |
| FILE-W7-07 | `tests/README.md` | modify |
| FILE-W7-08 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W7)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W7-U | unit | `make test` | REQ-18, REQ-19, REQ-20, REQ-28 |
| TEST-W7-I | integration/contract | N/A — ForgeClient/httpx doubled in unit | — |
| TEST-W7-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_wave_closeout_readout` | P15 surface |

#### Verification Coverage (W7)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-18 | TEST-W7-U | N/A | TEST-W7-L | N/A | |
| REQ-19 | TEST-W7-U | N/A | TEST-W7-L | N/A | |
| REQ-20 | TEST-W7-U | N/A | TEST-W7-L | N/A | |
| REQ-28 | TEST-W7-U | N/A | TEST-W7-L | N/A | |

#### Live-verification intent (W7)

| Field | Value |
|-------|-------|
| Applicable | **yes** — new/changed GET product surface (P15) |
| Environment class | local-compose (`make run`) |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` against wave PR tip |
| Prerequisites | Programme token; `tests/config.yaml`; fixture PR where GitHub evidence required |
| Safe test data | Non-prod fixture org/repo/PR; no label/merge mutations |
| Steps / command | `.venv/bin/python -m tests.verify.verify_wave_closeout_readout` |
| Expected observations | exit 0; assertions for wave REQs |
| Expected evidence | `wave-accepted` on tip |
| Cleanup | none (read-only) |
| Stop conditions | non-zero exit; unexpected write call |

### Phase W8 — Merge confirm + completion eligibility

**GOAL-W8:** Merge confirm reuses CAP-01 wave-signoff; next-wave nudge; completion is pure CAP-05 rollup.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W8-01 | Merged/not-merged + misses; nudge when next wave unblocked | REQ-21, REQ-22 | — | `src/business_services/merge_readout_service.py` create; `src/models/merge_readout_models.py` create; `tests/unit/test_merge_readout_service.py` create | Merged/not-merged + misses; nudge when next wave unblocked | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W8.md § TASK-W8-01 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_merge_and_completion` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w8-merge-completion` |
| TASK-W8-02 | Ready-to-close iff all wave tickets Done; empty → no waves found; reus | REQ-23, REQ-24 | — | `src/business_services/completion_readout_service.py` create; `src/models/completion_readout_models.py` create; `tests/unit/test_completion_readout_service.py` create | Ready-to-close iff all wave tickets Done; empty → no waves found; reuses wave-map logic | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W8.md § TASK-W8-02 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_merge_and_completion` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w8-merge-completion` |
| TASK-W8-03 | GET .../merge and GET .../completion GET-only | REQ-21, REQ-22, REQ-23, REQ-24, REQ-28 | TASK-W8-01, TASK-W8-02 | `src/api/v1/initiatives_routes.py` modify; `tests/unit/test_initiatives_read_api.py` modify | GET .../merge and GET .../completion GET-only | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W8.md § TASK-W8-03 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_merge_and_completion` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w8-merge-completion` |
| TASK-W8-04 | Live merge+completion smoke; as-built W8 row | REQ-21, REQ-22, REQ-23, REQ-28 | TASK-W8-03 | `tests/verify/verify_merge_and_completion.py` create; `tests/README.md` modify; `docs/specification/as-built/implementation-status.md` modify | Live merge+completion smoke; as-built W8 row | command / `make check && make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W8.md § TASK-W8-04 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_merge_and_completion` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w8-merge-completion` |

#### Files (W8)

| ID | Path | Action |
|----|------|--------|
| FILE-W8-01 | `src/business_services/merge_readout_service.py` | create |
| FILE-W8-02 | `src/models/merge_readout_models.py` | create |
| FILE-W8-03 | `tests/unit/test_merge_readout_service.py` | create |
| FILE-W8-04 | `src/business_services/completion_readout_service.py` | create |
| FILE-W8-05 | `src/models/completion_readout_models.py` | create |
| FILE-W8-06 | `tests/unit/test_completion_readout_service.py` | create |
| FILE-W8-07 | `src/api/v1/initiatives_routes.py` | modify |
| FILE-W8-08 | `tests/unit/test_initiatives_read_api.py` | modify |
| FILE-W8-09 | `tests/verify/verify_merge_and_completion.py` | create |
| FILE-W8-10 | `tests/README.md` | modify |
| FILE-W8-11 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W8)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W8-U | unit | `make test` | REQ-21, REQ-22, REQ-23, REQ-24, REQ-28 |
| TEST-W8-I | integration/contract | N/A — ForgeClient/httpx doubled in unit | — |
| TEST-W8-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_merge_and_completion` | P15 surface |

#### Verification Coverage (W8)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-21 | TEST-W8-U | N/A | TEST-W8-L | N/A | |
| REQ-22 | TEST-W8-U | N/A | TEST-W8-L | N/A | |
| REQ-23 | TEST-W8-U | N/A | TEST-W8-L | N/A | |
| REQ-24 | TEST-W8-U | N/A | TEST-W8-L | N/A | |
| REQ-28 | TEST-W8-U | N/A | TEST-W8-L | N/A | |

#### Live-verification intent (W8)

| Field | Value |
|-------|-------|
| Applicable | **yes** — new/changed GET product surface (P15) |
| Environment class | local-compose (`make run`) |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` against wave PR tip |
| Prerequisites | Programme token; `tests/config.yaml`; fixture PR where GitHub evidence required |
| Safe test data | Non-prod fixture org/repo/PR; no label/merge mutations |
| Steps / command | `.venv/bin/python -m tests.verify.verify_merge_and_completion` |
| Expected observations | exit 0; assertions for wave REQs |
| Expected evidence | `wave-accepted` on tip |
| Cleanup | none (read-only) |
| Stop conditions | non-zero exit; unexpected write call |

### Phase W9 — Closure preview + CAP-01 reuse

**GOAL-W9:** Closure preview from purge skill manifest (pre/post); signoff confirmation reuses CheckpointEvidenceService only.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W9-01 | Pre/post lists from purge manifest; CAP-01 for closure signoff checkpo | REQ-25, REQ-26, REQ-27 | — | `src/business_services/closure_preview_service.py` create; `src/models/closure_preview_models.py` create; `tests/unit/test_closure_preview_service.py` create | Pre/post lists from purge manifest; CAP-01 for closure signoff checkpoints | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W9.md § TASK-W9-01 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_closure_preview` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w9-closure-preview` |
| TASK-W9-02 | GET .../closure GET-only; zero write calls | REQ-25, REQ-26, REQ-27, REQ-28 | TASK-W9-01 | `src/api/v1/initiatives_routes.py` modify; `tests/unit/test_initiatives_read_api.py` modify | GET .../closure GET-only; zero write calls | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W9.md § TASK-W9-02 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_closure_preview` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w9-closure-preview` |
| TASK-W9-03 | Live closure preview smoke; as-built W9 complete | REQ-25, REQ-26, REQ-27, REQ-28 | TASK-W9-02 | `tests/verify/verify_closure_preview.py` create; `tests/README.md` modify; `docs/specification/as-built/implementation-status.md` modify | Live closure preview smoke; as-built W9 complete | command / `make check && make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-011-W9.md § TASK-W9-03 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` | `.venv/bin/python -m tests.verify.verify_closure_preview` | architecture.mdc, http-api-conventions.mdc, pydantic-schemas.mdc, fail-fast.mdc | ADR-001; ADR-003; ADR-005; ADR-009 | `feature/INIT-GATEFLOW-011-w9-closure-preview` |

#### Files (W9)

| ID | Path | Action |
|----|------|--------|
| FILE-W9-01 | `src/business_services/closure_preview_service.py` | create |
| FILE-W9-02 | `src/models/closure_preview_models.py` | create |
| FILE-W9-03 | `tests/unit/test_closure_preview_service.py` | create |
| FILE-W9-04 | `src/api/v1/initiatives_routes.py` | modify |
| FILE-W9-05 | `tests/unit/test_initiatives_read_api.py` | modify |
| FILE-W9-06 | `tests/verify/verify_closure_preview.py` | create |
| FILE-W9-07 | `tests/README.md` | modify |
| FILE-W9-08 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W9)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W9-U | unit | `make test` | REQ-25, REQ-26, REQ-27, REQ-28 |
| TEST-W9-I | integration/contract | N/A — ForgeClient/httpx doubled in unit | — |
| TEST-W9-L | live (smoke) | `.venv/bin/python -m tests.verify.verify_closure_preview` | P15 surface |

#### Verification Coverage (W9)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-25 | TEST-W9-U | N/A | TEST-W9-L | N/A | |
| REQ-26 | TEST-W9-U | N/A | TEST-W9-L | N/A | |
| REQ-27 | TEST-W9-U | N/A | TEST-W9-L | N/A | |
| REQ-28 | TEST-W9-U | N/A | TEST-W9-L | N/A | |

#### Live-verification intent (W9)

| Field | Value |
|-------|-------|
| Applicable | **yes** — new/changed GET product surface (P15) |
| Environment class | local-compose (`make run`) |
| Mode | smoke |
| Runtime head binding | Bound at `wave-acceptance` against wave PR tip |
| Prerequisites | Programme token; `tests/config.yaml`; fixture PR where GitHub evidence required |
| Safe test data | Non-prod fixture org/repo/PR; no label/merge mutations |
| Steps / command | `.venv/bin/python -m tests.verify.verify_closure_preview` |
| Expected observations | exit 0; assertions for wave REQs |
| Expected evidence | `wave-accepted` on tip |
| Cleanup | none (read-only) |
| Stop conditions | non-zero exit; unexpected write call |

## 3. Dependencies (DEP)

| ID | Dependency | Blocks |
|----|------------|--------|
| DEP-01 | W0 before W1 (persistence needs CAP-01) | W1 |
| DEP-02 | W0 before W2 (readouts may call CAP-01 later) | W2+ |
| DEP-03 | W2 before W3–W5 | W3,W4,W5 |
| DEP-04 | W4 before W6 | W6 |
| DEP-05 | W1+W2 before W7 (drift baseline) | W7 |
| DEP-06 | W1+W4 before W8 | W8 |
| DEP-07 | W1+W8 before W9 | W9 |
| DEP-08 | Pin tip `v0.5.0-rc.2` remounted | all waves |
| DEP-09 | Human Alembic if CAP-02 sibling table chosen (default run_events — no DDL) | W1 |

## 4. Risks (RISK)

| ID | Risk | Mitigation |
|----|------|------------|
| RISK-01 | ForgeClient extension underestimated | Explicit W0 tasks; unit fixtures for reviews/check-runs |
| RISK-02 | Silent GitHub cache as current | Fail-closed could_not_verify; no cache path (TDD PE-7) |
| RISK-03 | Meta App missing prayog-meta | Same credentials default; W3 live meta-down path |
| RISK-04 | OpenAPI field-name churn (Q-1) | Paths+HTTP normative; fields deferred |
| RISK-05 | run_events query insufficient later | Revisit sibling table with human Alembic (PE-5) |

## 5. Out of scope

- gateflow-ops screens
- prayog-skills pin redesign
- prayog-meta process changes
- Any POST/PUT/PATCH/DELETE product routes from this INIT
- Automatic label/approve/merge
- Webhook-driven auto-progression
- Phase 3/4/8/14 product work

## 6. As-built and docs tasks

| Task | File | Action |
|------|------|--------|
| Per-wave as-built matrix rows | `docs/specification/as-built/implementation-status.md` | modify each wave |
| Feature-map live commands | `tests/README.md` | add verify_* rows per wave |
| Optional OpenAPI field pass | deferred Q-1 | later |

## 7. Plan check summary

| Check | Status |
|-------|--------|
| P1 REQ inventory | PASS — REQ-01…28 in §1 |
| P2 TASK Implements | PASS |
| P3 FILE paths | PASS |
| P4 Exit evidence | PASS |
| P5 Verification layers | PASS — unit + live each wave |
| P6 Scope | PASS |
| P7 Risks | PASS |
| P8 Wave order | PASS |
| P9 Docs in same PR | PASS |
| P10 Self-contained + commands | PASS |
| P11 MDC notes | PASS |
| P12 ADR | PASS — ADR_REQUIRED=0; constraints cited |
| P13 TDD Accepted | PASS — Accepted 2026-08-06 |
| P14 WorkManifest seed | PASS |
| P15 Co-ship live verify | PASS — each W0–W9 |
| P16 WorkManifest contract | PASS — see validation below |

**Selected workflow outcome:** `pass` → `coding-readiness`

## 8. Forge / PR instructions

> Persist locally; publish via `/commit-workspace` to Draft spec PR #159.
> Do **not** commit inside this skill.

```
Branch: chore/INIT-GATEFLOW-011-spec-gateflow
PR: https://github.com/drivestream-lab/gateflow/pull/159
Reviewer: @drivestream-lab/prayog-pe-team
```


## 9. WorkManifest seed

> Validate with `python prayog-skills/scripts/workmanifest_contract.py`.

```yaml
# Generated by /spec-implementation-plan — 2026-08-06
apiVersion: prayog/v1
kind: WorkManifest

initiative: INIT-GATEFLOW-011
metadata:
  title: INIT-GATEFLOW-011 — Day-1 visibility and GitHub reconcile
  summary: |
    Read-only checkpoint status-check (CAP-01/02) and initiative/wave
    visibility GETs (CAP-03–10) against pinned delivery-contract vocabulary.
  playbook:
    - docs/specification/product/INIT-GATEFLOW-011-gateflow.md
    - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-011.md
target:
  org: drivestream-lab
  project: "drivestream-lab Board"
defaults:
  initiative: INIT-GATEFLOW-011
  parent: EPIC
  labels:
    - INIT-GATEFLOW-011
epic:
  id: EPIC
  repo: drivestream-lab/gateflow
  title: "[feature] INIT-GATEFLOW-011 — Day-1 visibility and GitHub reconcile"
  codebase: drivestream-lab/gateflow
  spec_path: docs/specification/product/INIT-GATEFLOW-011-gateflow.md
  verify_command: .venv/bin/python -m tests.verify.verify_checkpoint_status
  body: |
    ## Objective
    Build GET-only visibility + GitHub reconcile for Day-1 delivery phases.
    ## Waves
    | Wave | Goal |
    |------|------|
    | W0 | Ship live read-only CAP-01: ForgeClient read extension, pin contract vocabulary, |
    | W1 | Persist every CAP-01 attempt; expose history (historical) and composed initiativ |
    | W2 | GET /initiatives and /initiatives/{id} from runs+board; PRD approval field unava |
    | W3 | Complete initiative PRD-approval via read-only meta CAP-01; meta-down → 200 with |
    | W4 | GET /initiatives/{id}/waves returns done/ready-to-start/blocked/active from boar |
    | W5 | GET /initiatives/{id}/spec returns pin+run fields; plain not-ready before spec-p |
    | W6 | GET .../waves/{wave_id}/implementation returns task timeline, Draft PR link, and |
    | W7 | Closeout GET lists learning/ground additions; advisory drift vs wave-acceptance  |
    | W8 | Merge confirm reuses CAP-01 wave-signoff; next-wave nudge; completion is pure CA |
    | W9 | Closure preview from purge skill manifest (pre/post); signoff confirmation reuse |
    ## References
    - Spec: docs/specification/product/INIT-GATEFLOW-011-gateflow.md
    - Plan: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-011.md
    - TDD: docs/specification/reports/Technical-Review-INIT-GATEFLOW-011.md
work:
  - id: W0
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-011 W0] Checkpoint status-check foundation"
    depends_on: []
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-011-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_checkpoint_status
    tasks:
      - id: TASK-W0-01
        implements: [REQ-02]
        depends_on: []
        files:
          - path: src/infra_services/forge_client.py
            action: modify
          - path: src/models/meta_pr_models.py
            action: modify
          - path: tests/unit/test_forge_client.py
            action: modify
        exit:
          criteria:
            - "list_reviews, list_check_runs, and merge fields available on read path; unit green"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0; list_reviews, list_check_runs, and merge fields available on read path; unit gre"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W0.md § TASK-W0-01"
      - id: TASK-W0-02
        implements: [REQ-02]
        depends_on: [TASK-W0-01]
        files:
          - path: src/business_services/workflow_engine.py
            action: modify
          - path: src/models/checkpoint_models.py
            action: create
          - path: tests/unit/test_checkpoint_vocab.py
            action: create
        exit:
          criteria:
            - "All six checkpoint ids resolve labels+review_roles from pinned delivery-contract.yaml"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; All six checkpoint ids resolve labels+review_roles from pinned delivery-contract"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W0.md § TASK-W0-02"
      - id: TASK-W0-03
        implements: [REQ-01, REQ-04, REQ-05]
        depends_on: [TASK-W0-01, TASK-W0-02]
        files:
          - path: src/business_services/checkpoint_evidence_service.py
            action: create
          - path: tests/unit/test_checkpoint_evidence.py
            action: create
          - path: src/di/modules/business_services_module.py
            action: modify
          - path: src/di/dependency_container.py
            action: modify
        exit:
          criteria:
            - "evaluate() returns itemized misses; GitHub down → could_not_verify; zero mutate ForgeClient calls"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; evaluate() returns itemized misses; GitHub down → could_not_verify; zero mutate "
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W0.md § TASK-W0-03"
      - id: TASK-W0-04
        implements: [REQ-01, REQ-05, REQ-28]
        depends_on: [TASK-W0-03]
        files:
          - path: src/api/v1/checkpoints_routes.py
            action: create
          - path: src/api/v1/__init__.py
            action: modify
          - path: src/app.py
            action: modify
          - path: tests/unit/test_checkpoints_api.py
            action: create
        exit:
          criteria:
            - "GET /api/v1/checkpoints/status programme-token; non-GET rejected; public_paths includes /api/v1/checkpoints"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; GET /api/v1/checkpoints/status programme-token; non-GET rejected; public_paths i"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W0.md § TASK-W0-04"
      - id: TASK-W0-05
        implements: [REQ-01, REQ-05, REQ-28]
        depends_on: [TASK-W0-04]
        files:
          - path: tests/verify/verify_checkpoint_status.py
            action: create
          - path: tests/README.md
            action: modify
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "Live verify exit 0; feature-map + as-built W0 row present"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0; Live verify exit 0; feature-map + as-built W0 row present"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W0.md § TASK-W0-05"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_checkpoint_status
        covers: [REQ-01, REQ-02, REQ-04, REQ-05, REQ-28]
        prerequisites:
          - "API+worker up via make run; PROGRAMME_SERVICE_TOKEN set; tests/config.yaml"
        safe_test_data:
          - "fixture org/repo/PR or programme knobs — no prod mutate"
        steps:
          - "Run .venv/bin/python -m tests.verify.verify_checkpoint_status"
        expected_observations:
          - "script exit 0; asserted GET responses match REQ exit criteria"
        expected_evidence: wave-accepted on tip
        cleanup:
          - "no board/GitHub writes from verify scripts"
        stop_conditions:
          - "non-zero exit or unexpected mutate call"
    body: |
      ## Goal
      Ship live read-only CAP-01: ForgeClient read extension, pin contract vocabulary, CheckpointEvidenceService, GET /api/v1/checkpoints/status (no persistence).
      ## Tasks
      | TASK | Implements | Depends on | Exit | Proof |
      |------|------------|------------|------|-------|
      | TASK-W0-01 | REQ-02 | — | list_reviews, list_check_runs, and merge fields available on | make check && make test |
      | TASK-W0-02 | REQ-02 | TASK-W0-01 | All six checkpoint ids resolve labels+review_roles from pinn | make test |
      | TASK-W0-03 | REQ-01, REQ-04, REQ-05 | TASK-W0-01,TASK-W0-02 | evaluate() returns itemized misses; GitHub down → could_not_ | make test |
      | TASK-W0-04 | REQ-01, REQ-05, REQ-28 | TASK-W0-03 | GET /api/v1/checkpoints/status programme-token; non-GET reje | make test |
      | TASK-W0-05 | REQ-01, REQ-05, REQ-28 | TASK-W0-04 | Live verify exit 0; feature-map + as-built W0 row present | make check && make test |
      ## Verify
      `.venv/bin/python -m tests.verify.verify_checkpoint_status`
  - id: W1
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-011 W1] Check persistence + composed readout"
    depends_on: [W0]
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-011-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_checkpoint_history
    tasks:
      - id: TASK-W1-01
        implements: [REQ-06]
        depends_on: []
        files:
          - path: src/models/policy_types.py
            action: modify
          - path: src/models/run_store_models.py
            action: modify
          - path: src/database/postgres/repository/run_store_repository.py
            action: modify
          - path: src/business_services/checkpoint_evidence_service.py
            action: modify
          - path: tests/unit/test_checkpoint_persistence.py
            action: create
        exit:
          criteria:
            - "Every evaluate attempt appends checkpoint_check run_event with required payload fields"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; Every evaluate attempt appends checkpoint_check run_event with required payload "
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W1.md § TASK-W1-01"
      - id: TASK-W1-02
        implements: [REQ-03]
        depends_on: [TASK-W1-01]
        files:
          - path: src/business_services/checkpoint_evidence_service.py
            action: modify
          - path: tests/unit/test_checkpoint_evidence.py
            action: modify
        exit:
          criteria:
            - "Stale evidence → not_satisfied with stale reason; checked_sha and checked_at always present"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; Stale evidence → not_satisfied with stale reason; checked_sha and checked_at alw"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W1.md § TASK-W1-02"
      - id: TASK-W1-03
        implements: [REQ-07, REQ-28]
        depends_on: [TASK-W1-01]
        files:
          - path: src/api/v1/checkpoints_routes.py
            action: modify
          - path: tests/unit/test_checkpoints_api.py
            action: modify
        exit:
          criteria:
            - "GET /checkpoints/history marks records historical; never claims live verdict"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; GET /checkpoints/history marks records historical; never claims live verdict"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W1.md § TASK-W1-03"
      - id: TASK-W1-04
        implements: [REQ-08, REQ-28]
        depends_on: [TASK-W1-02, TASK-W1-03]
        files:
          - path: src/business_services/checkpoint_evidence_service.py
            action: modify
          - path: src/api/v1/checkpoints_routes.py
            action: modify
          - path: tests/unit/test_checkpoints_api.py
            action: modify
        exit:
          criteria:
            - "Composed readout via initiative+wave; 404 no run found for this wave when unresolved"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; Composed readout via initiative+wave; 404 no run found for this wave when unreso"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W1.md § TASK-W1-04"
      - id: TASK-W1-05
        implements: [REQ-03, REQ-06, REQ-07, REQ-08, REQ-28]
        depends_on: [TASK-W1-04]
        files:
          - path: tests/verify/verify_checkpoint_history.py
            action: create
          - path: tests/README.md
            action: modify
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "Live verify exit 0 covering persist/stale/404; as-built W1 row"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0; Live verify exit 0 covering persist/stale/404; as-built W1 row"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W1.md § TASK-W1-05"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_checkpoint_history
        covers: [REQ-03, REQ-06, REQ-07, REQ-08, REQ-28]
        prerequisites:
          - "API+worker up via make run; PROGRAMME_SERVICE_TOKEN set; tests/config.yaml"
        safe_test_data:
          - "fixture org/repo/PR or programme knobs — no prod mutate"
        steps:
          - "Run .venv/bin/python -m tests.verify.verify_checkpoint_history"
        expected_observations:
          - "script exit 0; asserted GET responses match REQ exit criteria"
        expected_evidence: wave-accepted on tip
        cleanup:
          - "no board/GitHub writes from verify scripts"
        stop_conditions:
          - "non-zero exit or unexpected mutate call"
    body: |
      ## Goal
      Persist every CAP-01 attempt; expose history (historical) and composed initiative/wave checkpoint readout with checked_sha/checked_at/stale.
      ## Tasks
      | TASK | Implements | Depends on | Exit | Proof |
      |------|------------|------------|------|-------|
      | TASK-W1-01 | REQ-06 | — | Every evaluate attempt appends checkpoint_check run_event wi | make test |
      | TASK-W1-02 | REQ-03 | TASK-W1-01 | Stale evidence → not_satisfied with stale reason; checked_sh | make test |
      | TASK-W1-03 | REQ-07, REQ-28 | TASK-W1-01 | GET /checkpoints/history marks records historical; never cla | make test |
      | TASK-W1-04 | REQ-08, REQ-28 | TASK-W1-02,TASK-W1-03 | Composed readout via initiative+wave; 404 no run found for t | make test |
      | TASK-W1-05 | REQ-03, REQ-06, REQ-07, REQ-08, REQ-28 | TASK-W1-04 | Live verify exit 0 covering persist/stale/404; as-built W1 r | make check && make test |
      ## Verify
      `.venv/bin/python -m tests.verify.verify_checkpoint_history`
  - id: W2
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-011 W2] Initiative list/detail (Gateflow-owned)"
    depends_on: [W0]
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-011-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_initiatives_readout
    tasks:
      - id: TASK-W2-01
        implements: [REQ-09, REQ-10]
        depends_on: []
        files:
          - path: src/business_services/initiative_readout_service.py
            action: create
          - path: src/models/initiative_readout_models.py
            action: create
          - path: tests/unit/test_initiative_readout.py
            action: create
          - path: src/di/modules/business_services_module.py
            action: modify
        exit:
          criteria:
            - "List/detail returns Gateflow-owned fields; prd_approval=unavailable"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; List/detail returns Gateflow-owned fields; prd_approval=unavailable"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W2.md § TASK-W2-01"
      - id: TASK-W2-02
        implements: [REQ-09, REQ-10, REQ-28]
        depends_on: [TASK-W2-01]
        files:
          - path: src/api/v1/initiatives_routes.py
            action: modify
          - path: tests/unit/test_initiatives_read_api.py
            action: create
        exit:
          criteria:
            - "GET list/detail routes programme-token; GET-only guard"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; GET list/detail routes programme-token; GET-only guard"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W2.md § TASK-W2-02"
      - id: TASK-W2-03
        implements: [REQ-09, REQ-10, REQ-28]
        depends_on: [TASK-W2-02]
        files:
          - path: tests/verify/verify_initiatives_readout.py
            action: create
          - path: tests/README.md
            action: modify
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "Live smoke exit 0; as-built W2 row"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0; Live smoke exit 0; as-built W2 row"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W2.md § TASK-W2-03"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_initiatives_readout
        covers: [REQ-09, REQ-10, REQ-28]
        prerequisites:
          - "API+worker up via make run; PROGRAMME_SERVICE_TOKEN set; tests/config.yaml"
        safe_test_data:
          - "fixture org/repo/PR or programme knobs — no prod mutate"
        steps:
          - "Run .venv/bin/python -m tests.verify.verify_initiatives_readout"
        expected_observations:
          - "script exit 0; asserted GET responses match REQ exit criteria"
        expected_evidence: wave-accepted on tip
        cleanup:
          - "no board/GitHub writes from verify scripts"
        stop_conditions:
          - "non-zero exit or unexpected mutate call"
    body: |
      ## Goal
      GET /initiatives and /initiatives/{id} from runs+board; PRD approval field unavailable until W3.
      ## Tasks
      | TASK | Implements | Depends on | Exit | Proof |
      |------|------------|------------|------|-------|
      | TASK-W2-01 | REQ-09, REQ-10 | — | List/detail returns Gateflow-owned fields; prd_approval=unav | make test |
      | TASK-W2-02 | REQ-09, REQ-10, REQ-28 | TASK-W2-01 | GET list/detail routes programme-token; GET-only guard | make test |
      | TASK-W2-03 | REQ-09, REQ-10, REQ-28 | TASK-W2-02 | Live smoke exit 0; as-built W2 row | make check && make test |
      ## Verify
      `.venv/bin/python -m tests.verify.verify_initiatives_readout`
  - id: W3
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-011 W3] Meta bridge + partial success"
    depends_on: [W2]
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-011-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_initiative_meta_bridge
    tasks:
      - id: TASK-W3-01
        implements: [REQ-09]
        depends_on: []
        files:
          - path: src/business_services/initiative_readout_service.py
            action: modify
          - path: tests/unit/test_initiative_readout.py
            action: modify
        exit:
          criteria:
            - "PRD approval populated via CAP-01 against prd-impact-acceptance on meta PR"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; PRD approval populated via CAP-01 against prd-impact-acceptance on meta PR"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W3.md § TASK-W3-01"
      - id: TASK-W3-02
        implements: [REQ-11]
        depends_on: [TASK-W3-01]
        files:
          - path: src/business_services/initiative_readout_service.py
            action: modify
          - path: tests/unit/test_initiative_readout.py
            action: modify
        exit:
          criteria:
            - "Meta unreachable → HTTP 200; meta fields unavailable; owned fields present"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; Meta unreachable → HTTP 200; meta fields unavailable; owned fields present"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W3.md § TASK-W3-02"
      - id: TASK-W3-03
        implements: [REQ-09, REQ-11, REQ-28]
        depends_on: [TASK-W3-02]
        files:
          - path: tests/verify/verify_initiative_meta_bridge.py
            action: create
          - path: tests/README.md
            action: modify
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "Live meta-up + meta-down paths; as-built W3 row"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0; Live meta-up + meta-down paths; as-built W3 row"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W3.md § TASK-W3-03"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_initiative_meta_bridge
        covers: [REQ-09, REQ-11, REQ-28]
        prerequisites:
          - "API+worker up via make run; PROGRAMME_SERVICE_TOKEN set; tests/config.yaml"
        safe_test_data:
          - "fixture org/repo/PR or programme knobs — no prod mutate"
        steps:
          - "Run .venv/bin/python -m tests.verify.verify_initiative_meta_bridge"
        expected_observations:
          - "script exit 0; asserted GET responses match REQ exit criteria"
        expected_evidence: wave-accepted on tip
        cleanup:
          - "no board/GitHub writes from verify scripts"
        stop_conditions:
          - "non-zero exit or unexpected mutate call"
    body: |
      ## Goal
      Complete initiative PRD-approval via read-only meta CAP-01; meta-down → 200 with unavailable.
      ## Tasks
      | TASK | Implements | Depends on | Exit | Proof |
      |------|------------|------------|------|-------|
      | TASK-W3-01 | REQ-09 | — | PRD approval populated via CAP-01 against prd-impact-accepta | make test |
      | TASK-W3-02 | REQ-11 | TASK-W3-01 | Meta unreachable → HTTP 200; meta fields unavailable; owned  | make test |
      | TASK-W3-03 | REQ-09, REQ-11, REQ-28 | TASK-W3-02 | Live meta-up + meta-down paths; as-built W3 row | make check && make test |
      ## Verify
      `.venv/bin/python -m tests.verify.verify_initiative_meta_bridge`
  - id: W4
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-011 W4] Wave map readout"
    depends_on: [W2]
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-011-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_wave_map
    tasks:
      - id: TASK-W4-01
        implements: [REQ-14, REQ-15]
        depends_on: []
        files:
          - path: src/business_services/wave_map_service.py
            action: create
          - path: src/models/wave_map_models.py
            action: create
          - path: tests/unit/test_wave_map_service.py
            action: create
        exit:
          criteria:
            - "Per-wave status + block reason; no new wave-state store"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; Per-wave status + block reason; no new wave-state store"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W4.md § TASK-W4-01"
      - id: TASK-W4-02
        implements: [REQ-14, REQ-15, REQ-28]
        depends_on: [TASK-W4-01]
        files:
          - path: src/api/v1/initiatives_routes.py
            action: modify
          - path: tests/unit/test_initiatives_read_api.py
            action: modify
        exit:
          criteria:
            - "GET .../waves route wired GET-only"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; GET .../waves route wired GET-only"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W4.md § TASK-W4-02"
      - id: TASK-W4-03
        implements: [REQ-14, REQ-28]
        depends_on: [TASK-W4-02]
        files:
          - path: tests/verify/verify_wave_map.py
            action: create
          - path: tests/README.md
            action: modify
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "Live wave-map smoke; as-built W4 row"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0; Live wave-map smoke; as-built W4 row"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W4.md § TASK-W4-03"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_wave_map
        covers: [REQ-14, REQ-15, REQ-28]
        prerequisites:
          - "API+worker up via make run; PROGRAMME_SERVICE_TOKEN set; tests/config.yaml"
        safe_test_data:
          - "fixture org/repo/PR or programme knobs — no prod mutate"
        steps:
          - "Run .venv/bin/python -m tests.verify.verify_wave_map"
        expected_observations:
          - "script exit 0; asserted GET responses match REQ exit criteria"
        expected_evidence: wave-accepted on tip
        cleanup:
          - "no board/GitHub writes from verify scripts"
        stop_conditions:
          - "non-zero exit or unexpected mutate call"
    body: |
      ## Goal
      GET /initiatives/{id}/waves returns done/ready-to-start/blocked/active from board+run data only.
      ## Tasks
      | TASK | Implements | Depends on | Exit | Proof |
      |------|------------|------------|------|-------|
      | TASK-W4-01 | REQ-14, REQ-15 | — | Per-wave status + block reason; no new wave-state store | make test |
      | TASK-W4-02 | REQ-14, REQ-15, REQ-28 | TASK-W4-01 | GET .../waves route wired GET-only | make test |
      | TASK-W4-03 | REQ-14, REQ-28 | TASK-W4-02 | Live wave-map smoke; as-built W4 row | make check && make test |
      ## Verify
      `.venv/bin/python -m tests.verify.verify_wave_map`
  - id: W5
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-011 W5] Spec lane readout"
    depends_on: [W2]
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-011-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_spec_readout
    tasks:
      - id: TASK-W5-01
        implements: [REQ-12, REQ-13]
        depends_on: []
        files:
          - path: src/business_services/spec_readout_service.py
            action: create
          - path: src/models/spec_readout_models.py
            action: create
          - path: tests/unit/test_spec_readout_service.py
            action: create
        exit:
          criteria:
            - "Fields from pin+run; not-ready message when no Draft Spec PR"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; Fields from pin+run; not-ready message when no Draft Spec PR"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W5.md § TASK-W5-01"
      - id: TASK-W5-02
        implements: [REQ-12, REQ-13, REQ-28]
        depends_on: [TASK-W5-01]
        files:
          - path: src/api/v1/initiatives_routes.py
            action: modify
          - path: tests/unit/test_initiatives_read_api.py
            action: modify
        exit:
          criteria:
            - "GET .../spec GET-only route"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; GET .../spec GET-only route"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W5.md § TASK-W5-02"
      - id: TASK-W5-03
        implements: [REQ-12, REQ-28]
        depends_on: [TASK-W5-02]
        files:
          - path: tests/verify/verify_spec_readout.py
            action: create
          - path: tests/README.md
            action: modify
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "Live spec readout smoke; as-built W5 row"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0; Live spec readout smoke; as-built W5 row"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W5.md § TASK-W5-03"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_spec_readout
        covers: [REQ-12, REQ-13, REQ-28]
        prerequisites:
          - "API+worker up via make run; PROGRAMME_SERVICE_TOKEN set; tests/config.yaml"
        safe_test_data:
          - "fixture org/repo/PR or programme knobs — no prod mutate"
        steps:
          - "Run .venv/bin/python -m tests.verify.verify_spec_readout"
        expected_observations:
          - "script exit 0; asserted GET responses match REQ exit criteria"
        expected_evidence: wave-accepted on tip
        cleanup:
          - "no board/GitHub writes from verify scripts"
        stop_conditions:
          - "non-zero exit or unexpected mutate call"
    body: |
      ## Goal
      GET /initiatives/{id}/spec returns pin+run fields; plain not-ready before spec-pr-action.
      ## Tasks
      | TASK | Implements | Depends on | Exit | Proof |
      |------|------------|------------|------|-------|
      | TASK-W5-01 | REQ-12, REQ-13 | — | Fields from pin+run; not-ready message when no Draft Spec PR | make test |
      | TASK-W5-02 | REQ-12, REQ-13, REQ-28 | TASK-W5-01 | GET .../spec GET-only route | make test |
      | TASK-W5-03 | REQ-12, REQ-28 | TASK-W5-02 | Live spec readout smoke; as-built W5 row | make check && make test |
      ## Verify
      `.venv/bin/python -m tests.verify.verify_spec_readout`
  - id: W6
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-011 W6] Wave implementation progress"
    depends_on: [W4]
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-011-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_wave_implementation
    tasks:
      - id: TASK-W6-01
        implements: [REQ-16, REQ-17]
        depends_on: []
        files:
          - path: src/business_services/implementation_readout_service.py
            action: create
          - path: src/models/implementation_readout_models.py
            action: create
          - path: tests/unit/test_implementation_readout_service.py
            action: create
        exit:
          criteria:
            - "Per-task progress + Draft PR when present; named task+reason on failure"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; Per-task progress + Draft PR when present; named task+reason on failure"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W6.md § TASK-W6-01"
      - id: TASK-W6-02
        implements: [REQ-16, REQ-17, REQ-28]
        depends_on: [TASK-W6-01]
        files:
          - path: src/api/v1/initiatives_routes.py
            action: modify
          - path: tests/unit/test_initiatives_read_api.py
            action: modify
        exit:
          criteria:
            - "GET .../implementation GET-only route"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; GET .../implementation GET-only route"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W6.md § TASK-W6-02"
      - id: TASK-W6-03
        implements: [REQ-16, REQ-28]
        depends_on: [TASK-W6-02]
        files:
          - path: tests/verify/verify_wave_implementation.py
            action: create
          - path: tests/README.md
            action: modify
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "Live implementation smoke; as-built W6 row"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0; Live implementation smoke; as-built W6 row"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W6.md § TASK-W6-03"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_wave_implementation
        covers: [REQ-16, REQ-17, REQ-28]
        prerequisites:
          - "API+worker up via make run; PROGRAMME_SERVICE_TOKEN set; tests/config.yaml"
        safe_test_data:
          - "fixture org/repo/PR or programme knobs — no prod mutate"
        steps:
          - "Run .venv/bin/python -m tests.verify.verify_wave_implementation"
        expected_observations:
          - "script exit 0; asserted GET responses match REQ exit criteria"
        expected_evidence: wave-accepted on tip
        cleanup:
          - "no board/GitHub writes from verify scripts"
        stop_conditions:
          - "non-zero exit or unexpected mutate call"
    body: |
      ## Goal
      GET .../waves/{wave_id}/implementation returns task timeline, Draft PR link, and named failure on stop.
      ## Tasks
      | TASK | Implements | Depends on | Exit | Proof |
      |------|------------|------------|------|-------|
      | TASK-W6-01 | REQ-16, REQ-17 | — | Per-task progress + Draft PR when present; named task+reason | make test |
      | TASK-W6-02 | REQ-16, REQ-17, REQ-28 | TASK-W6-01 | GET .../implementation GET-only route | make test |
      | TASK-W6-03 | REQ-16, REQ-28 | TASK-W6-02 | Live implementation smoke; as-built W6 row | make check && make test |
      ## Verify
      `.venv/bin/python -m tests.verify.verify_wave_implementation`
  - id: W7
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-011 W7] Closeout readout + drift safeguard"
    depends_on: [W1, W2]
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-011-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_wave_closeout_readout
    tasks:
      - id: TASK-W7-01
        implements: [REQ-18, REQ-19, REQ-20]
        depends_on: []
        files:
          - path: src/business_services/closeout_readout_service.py
            action: create
          - path: src/models/closeout_readout_models.py
            action: create
          - path: tests/unit/test_closeout_readout_service.py
            action: create
        exit:
          criteria:
            - "Itemized closeout additions; drift or unknown baseline; advisory only"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; Itemized closeout additions; drift or unknown baseline; advisory only"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W7.md § TASK-W7-01"
      - id: TASK-W7-02
        implements: [REQ-18, REQ-19, REQ-20, REQ-28]
        depends_on: [TASK-W7-01]
        files:
          - path: src/api/v1/initiatives_routes.py
            action: modify
          - path: tests/unit/test_initiatives_read_api.py
            action: modify
        exit:
          criteria:
            - "GET .../closeout GET-only route"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; GET .../closeout GET-only route"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W7.md § TASK-W7-02"
      - id: TASK-W7-03
        implements: [REQ-18, REQ-19, REQ-28]
        depends_on: [TASK-W7-02]
        files:
          - path: tests/verify/verify_wave_closeout_readout.py
            action: create
          - path: tests/README.md
            action: modify
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "Live closeout+drift smoke; as-built W7 row"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0; Live closeout+drift smoke; as-built W7 row"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W7.md § TASK-W7-03"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_wave_closeout_readout
        covers: [REQ-18, REQ-19, REQ-20, REQ-28]
        prerequisites:
          - "API+worker up via make run; PROGRAMME_SERVICE_TOKEN set; tests/config.yaml"
        safe_test_data:
          - "fixture org/repo/PR or programme knobs — no prod mutate"
        steps:
          - "Run .venv/bin/python -m tests.verify.verify_wave_closeout_readout"
        expected_observations:
          - "script exit 0; asserted GET responses match REQ exit criteria"
        expected_evidence: wave-accepted on tip
        cleanup:
          - "no board/GitHub writes from verify scripts"
        stop_conditions:
          - "non-zero exit or unexpected mutate call"
    body: |
      ## Goal
      Closeout GET lists learning/ground additions; advisory drift vs wave-acceptance baseline from W1 records.
      ## Tasks
      | TASK | Implements | Depends on | Exit | Proof |
      |------|------------|------------|------|-------|
      | TASK-W7-01 | REQ-18, REQ-19, REQ-20 | — | Itemized closeout additions; drift or unknown baseline; advi | make test |
      | TASK-W7-02 | REQ-18, REQ-19, REQ-20, REQ-28 | TASK-W7-01 | GET .../closeout GET-only route | make test |
      | TASK-W7-03 | REQ-18, REQ-19, REQ-28 | TASK-W7-02 | Live closeout+drift smoke; as-built W7 row | make check && make test |
      ## Verify
      `.venv/bin/python -m tests.verify.verify_wave_closeout_readout`
  - id: W8
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-011 W8] Merge confirm + completion eligibility"
    depends_on: [W1, W4]
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-011-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_merge_and_completion
    tasks:
      - id: TASK-W8-01
        implements: [REQ-21, REQ-22]
        depends_on: []
        files:
          - path: src/business_services/merge_readout_service.py
            action: create
          - path: src/models/merge_readout_models.py
            action: create
          - path: tests/unit/test_merge_readout_service.py
            action: create
        exit:
          criteria:
            - "Merged/not-merged + misses; nudge when next wave unblocked"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; Merged/not-merged + misses; nudge when next wave unblocked"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W8.md § TASK-W8-01"
      - id: TASK-W8-02
        implements: [REQ-23, REQ-24]
        depends_on: []
        files:
          - path: src/business_services/completion_readout_service.py
            action: create
          - path: src/models/completion_readout_models.py
            action: create
          - path: tests/unit/test_completion_readout_service.py
            action: create
        exit:
          criteria:
            - "Ready-to-close iff all wave tickets Done; empty → no waves found; reuses wave-map logic"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; Ready-to-close iff all wave tickets Done; empty → no waves found; reuses wave-ma"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W8.md § TASK-W8-02"
      - id: TASK-W8-03
        implements: [REQ-21, REQ-22, REQ-23, REQ-24, REQ-28]
        depends_on: [TASK-W8-01, TASK-W8-02]
        files:
          - path: src/api/v1/initiatives_routes.py
            action: modify
          - path: tests/unit/test_initiatives_read_api.py
            action: modify
        exit:
          criteria:
            - "GET .../merge and GET .../completion GET-only"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; GET .../merge and GET .../completion GET-only"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W8.md § TASK-W8-03"
      - id: TASK-W8-04
        implements: [REQ-21, REQ-22, REQ-23, REQ-28]
        depends_on: [TASK-W8-03]
        files:
          - path: tests/verify/verify_merge_and_completion.py
            action: create
          - path: tests/README.md
            action: modify
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "Live merge+completion smoke; as-built W8 row"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0; Live merge+completion smoke; as-built W8 row"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W8.md § TASK-W8-04"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_merge_and_completion
        covers: [REQ-21, REQ-22, REQ-23, REQ-24, REQ-28]
        prerequisites:
          - "API+worker up via make run; PROGRAMME_SERVICE_TOKEN set; tests/config.yaml"
        safe_test_data:
          - "fixture org/repo/PR or programme knobs — no prod mutate"
        steps:
          - "Run .venv/bin/python -m tests.verify.verify_merge_and_completion"
        expected_observations:
          - "script exit 0; asserted GET responses match REQ exit criteria"
        expected_evidence: wave-accepted on tip
        cleanup:
          - "no board/GitHub writes from verify scripts"
        stop_conditions:
          - "non-zero exit or unexpected mutate call"
    body: |
      ## Goal
      Merge confirm reuses CAP-01 wave-signoff; next-wave nudge; completion is pure CAP-05 rollup.
      ## Tasks
      | TASK | Implements | Depends on | Exit | Proof |
      |------|------------|------------|------|-------|
      | TASK-W8-01 | REQ-21, REQ-22 | — | Merged/not-merged + misses; nudge when next wave unblocked | make test |
      | TASK-W8-02 | REQ-23, REQ-24 | — | Ready-to-close iff all wave tickets Done; empty → no waves f | make test |
      | TASK-W8-03 | REQ-21, REQ-22, REQ-23, REQ-24, REQ-28 | TASK-W8-01,TASK-W8-02 | GET .../merge and GET .../completion GET-only | make test |
      | TASK-W8-04 | REQ-21, REQ-22, REQ-23, REQ-28 | TASK-W8-03 | Live merge+completion smoke; as-built W8 row | make check && make test |
      ## Verify
      `.venv/bin/python -m tests.verify.verify_merge_and_completion`
  - id: W9
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-011 W9] Closure preview + CAP-01 reuse"
    depends_on: [W1, W8]
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-011-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_closure_preview
    tasks:
      - id: TASK-W9-01
        implements: [REQ-25, REQ-26, REQ-27]
        depends_on: []
        files:
          - path: src/business_services/closure_preview_service.py
            action: create
          - path: src/models/closure_preview_models.py
            action: create
          - path: tests/unit/test_closure_preview_service.py
            action: create
        exit:
          criteria:
            - "Pre/post lists from purge manifest; CAP-01 for closure signoff checkpoints"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; Pre/post lists from purge manifest; CAP-01 for closure signoff checkpoints"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W9.md § TASK-W9-01"
      - id: TASK-W9-02
        implements: [REQ-25, REQ-26, REQ-27, REQ-28]
        depends_on: [TASK-W9-01]
        files:
          - path: src/api/v1/initiatives_routes.py
            action: modify
          - path: tests/unit/test_initiatives_read_api.py
            action: modify
        exit:
          criteria:
            - "GET .../closure GET-only; zero write calls"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; GET .../closure GET-only; zero write calls"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W9.md § TASK-W9-02"
      - id: TASK-W9-03
        implements: [REQ-25, REQ-26, REQ-27, REQ-28]
        depends_on: [TASK-W9-02]
        files:
          - path: tests/verify/verify_closure_preview.py
            action: create
          - path: tests/README.md
            action: modify
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "Live closure preview smoke; as-built W9 complete"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0; Live closure preview smoke; as-built W9 complete"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-011-W9.md § TASK-W9-03"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_closure_preview
        covers: [REQ-25, REQ-26, REQ-27, REQ-28]
        prerequisites:
          - "API+worker up via make run; PROGRAMME_SERVICE_TOKEN set; tests/config.yaml"
        safe_test_data:
          - "fixture org/repo/PR or programme knobs — no prod mutate"
        steps:
          - "Run .venv/bin/python -m tests.verify.verify_closure_preview"
        expected_observations:
          - "script exit 0; asserted GET responses match REQ exit criteria"
        expected_evidence: wave-accepted on tip
        cleanup:
          - "no board/GitHub writes from verify scripts"
        stop_conditions:
          - "non-zero exit or unexpected mutate call"
    body: |
      ## Goal
      Closure preview from purge skill manifest (pre/post); signoff confirmation reuses CheckpointEvidenceService only.
      ## Tasks
      | TASK | Implements | Depends on | Exit | Proof |
      |------|------------|------------|------|-------|
      | TASK-W9-01 | REQ-25, REQ-26, REQ-27 | — | Pre/post lists from purge manifest; CAP-01 for closure signo | make test |
      | TASK-W9-02 | REQ-25, REQ-26, REQ-27, REQ-28 | TASK-W9-01 | GET .../closure GET-only; zero write calls | make test |
      | TASK-W9-03 | REQ-25, REQ-26, REQ-27, REQ-28 | TASK-W9-02 | Live closure preview smoke; as-built W9 complete | make check && make test |
      ## Verify
      `.venv/bin/python -m tests.verify.verify_closure_preview`
```

## 10. Coding-readiness unlock (PE — after plan on head)

| Item | Value |
|------|-------|
| Workflow outcome | `pass` — P1–P16 PASS; TDD Accepted; sources CURRENT |
| Verdict | GATE OPEN REQUEST |
| Spec PR | https://github.com/drivestream-lab/gateflow/pull/159 |
| Spec PR head SHA | `db1ace451b2fd4ae96ff807337bfffe176abd123` (update after Forge publish of this plan) |
| Gate label (current) | may already be `spec-lgtm` — re-attest on plan tip |
| Gate label (target) | `spec-lgtm` |
| Local plan path | `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-011.md` |
| Forge readiness | `/commit-workspace` — do not commit inside this skill |
| Blocking items | none |

### Approve attestation body

```text
Spec package approved
initiative: INIT-GATEFLOW-011
spec_pr_head_sha: {{SHA after plan commit}}
meta_pr_head_sha: f3da8148f3e861fad4720a3491f11f1fdc0145aa
impact_map_revision: 1
prd_digest: sha256:eca06cbe986d619db58ae3ca84f4ec0987c19aa19b8f1485693280c6a655e4dd
scope_digest: sha256:afdc7bd51bcd0c12f614feebf338bdc78766396bb84777121a2565c0ecc7966d
plan_digest: see handoff.artifact.digest (body sha256 excluding this handoff fence)
artifacts:
  - docs/specification/product/INIT-GATEFLOW-011-gateflow.md
  - docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-011.md
  - docs/specification/reports/Technical-Review-INIT-GATEFLOW-011.md
  - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-011.md
```

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-implementation-plan
  outcome: pass
  artifact:
    path: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-011.md
    digest: sha256:ec85d78871b4a754413582ba7da41784bc18a1760ada4dfa6f762471a49c16f2
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    spec_pr: "https://github.com/drivestream-lab/gateflow/pull/159"
    source_freshness: CURRENT
    workmanifest_contract: pass
    p15_waves: "W0,W1,W2,W3,W4,W5,W6,W7,W8,W9"
    ready_for_coding_readiness: true
  next_candidates:
    - coding-readiness
  human_checkpoint: true
  external_action: false
  forge:
    action: commit_workspace
    draft: true
    apply_labels: []
    title: "[INIT-GATEFLOW-011] Implementation plan — Day-1 visibility and GitHub reconcile"
    body_path: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-011.md
```

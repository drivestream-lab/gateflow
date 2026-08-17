# Implementation status — INIT-GATEFLOW-019 (gateflow)

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-019 |
| Spec | `docs/specification/product/INIT-GATEFLOW-019-gateflow.md` |
| Plan | `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-019.md` |
| Updated | 2026-08-17 |
| Gate 1 | **skipped** (local backfill) |

## Wave status

| Wave | Goal | Status | Evidence |
|------|------|--------|----------|
| W0 | Ground CAP-D (`c575356`) | **coded, not grounded** — on `fix/session-grant-tenant-binding`; as-built this file; no wave-acceptance | Unit on that commit; live not claimed |
| W1 | Meta PR list + CAP-01 + join + onboard | **implemented (unit)** — catalogue / onboard / onboarded routes | `test_meta_pr_picker`; live `verify_meta_pr_picker` (human) |
| W2 | Spec start resolve/omit + CAP-01 fail-closed; implement slug default | **implemented (unit)** | `test_wave_start` 019 cases; live `verify_spec_start_binds` (human) |

## W0 capability detail (code present, spec now owns it)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Grant `tenant_id` + `programme_name` | REQ-12 | `GrantedProgrammeReadModel` + membership join | `test_auth_identity_service` | `verify_jwt_login` (human) | Also noted on 017 W3 as-built |
| Auto-connect on programme create | REQ-13 | `ProgrammeService` upsert connection | `test_programme_service` | — | Closes 013/016 Q-4 |
| Connect = programme meta | REQ-14 | `CatalogueConnectionService` | `test_programme_onboarding` | — | Empty body defaults to meta |
| Initiative list without board | REQ-15 | `InitiativeReadoutService` | `test_initiative_readout` | — | Runs still return |
| Forge labels 404 → empty | REQ-16 | `ForgeClient.find_issues_by_labels` | `test_forge_client_board` | — | |

## W1 capability detail

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| INIT-* meta PR list (last 10) | REQ-01 | `MetaPrPickerService` + `ForgeClientFactory.for_programme` | `test_list_caps_at_last_ten_init_prs` | `verify_meta_pr_picker` | Programme PAT; 401/403 → 422, 404 → 404 |
| CAP-01 per row (Redis TTL) | REQ-02 | `evaluate_read_only` + Redis page cache; `refresh=true` bypass + rewrite | `test_list_cache_hit_skips_github_and_rejoins`, `test_list_refresh_bypasses_cache_and_rewrites` | `verify_meta_pr_picker` | GET must not write `checkpoint_check`; join always from run store |
| Spec-run join per repo | REQ-03 | join on `(meta_pr_url, org, repo)` | `test_list_joins_spec_runs_per_repo` | `verify_meta_pr_picker` | Missing run ≠ fabricated; no initiative-only fallback |
| Onboard INIT-* meta PR | REQ-18 | `POST …/meta/pulls/onboard` + `programme_meta_prs` | `test_onboard_admits_init_pr`, `test_onboard_rejects_*` | `verify_meta_pr_picker` | Catalogue fetch does not insert; human applies Alembic |
| Catalogue `onboarded` flag | REQ-19 | join admitted URLs onto last-10 | `test_list_marks_onboarded_catalogue_row` | `verify_meta_pr_picker` | List never admits |
| Admitted-set list | REQ-20 | `GET …/meta/pulls/onboarded` | `test_list_onboarded_skips_github_list` | `verify_meta_pr_picker` | No GitHub last-10; CAP-01 live |

## W2 capability detail

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Resolve app+meta workspaces | REQ-04 | `WaveStartService._resolve_spec_workspace_paths` | `test_spec_omitted_paths_*` | `verify_spec_start_binds` | Explicit dirs still honored |
| Omit start_node / slug / initiative | REQ-05/06 | `SpecWaveStartRequest` + accept derive | `test_wave_start`, `test_meta_pr_intake` | `verify_spec_start_binds` | Head remains `feature/{INIT}-spec` |
| App repo only; derive when omitted | REQ-07/08 | admitted fleet derive + meta refuse + `lane_defaults[spec]` | `test_spec_omitted_org_repo_derives_single_admitted`, `test_spec_omitted_org_repo_ambiguous_422`, `test_spec_target_meta_repo_422` | `verify_spec_start_binds` | One admitted → derive; several/zero named refuse |
| CAP-01 on spec start | REQ-09 | `_require_spec_cap01` | `test_spec_cap01_not_satisfied_422_zero_enqueue` | `verify_spec_start_binds` | 422 + 0 enqueue |
| Spec start requires onboard | REQ-21 | `_require_meta_pr_onboarded` | `test_spec_not_onboarded_422_zero_enqueue` | `verify_spec_start_binds` | Skip when no programme is bound |
| Implement slug default | REQ-10 | `IMPLEMENT_DEFAULT_BRANCH_SLUG` | `test_implement_omitted_branch_slug_defaults` | — | Closeout unchanged (REQ-11) |
| Runner + model catalogue | REQ-17 | `GET /api/v1/runners` | `test_runner_catalogue` | `verify_spec_start_binds` | Implemented runners only; Cursor first-party models |

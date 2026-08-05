# Implementation status (as-built)

| Field | Value |
|-------|-------|
| Repo | drivestream-lab/gateflow |
| Updated | 2026-08-05 |
| Source | INIT-GATEFLOW-010 W0+W1 **human_approved** (W0 [#144](https://github.com/drivestream-lab/gateflow/pull/144) `0ca2376`; W1 [#146](https://github.com/drivestream-lab/gateflow/pull/146) `34e5813`); INIT-GATEFLOW-008 (006A) W0–W2 human_approved; INIT-007 W0–W2 human_approved; INIT-009 human_approved freeze; pin `v0.5.0-rc.2` ≡ submodule `6561c7c` |

## Engineering lane naming

| Name | Legacy | Status |
|------|--------|--------|
| **implement lane** | Scenario B | Live prove-it **pass** (W1) |
| **spec lane** | Scenario A | W2 — live prove-it waits on next PRD + pin CTR-01 |

## Testing harness

| Layer | Command / path | Status |
|-------|----------------|--------|
| Toolchain | `make check` | Wired (black, ruff, pyright, import-linter) |
| Unit | `make test` → `tests/unit/` | INIT-001…006 unit green on forge branch (`make test`) |
| Live verify | `tests/verify/verify_all.py` | health…board (implement-lane **separate** opt-in) |
| Implement-lane prove-it | `tests/verify/verify_implement_lane.py` | Prior live pass 2026-07-25; **forge dogfood (stage_commit) deferred** |
| CI | `.github/workflows/ci.yml` | Placeholder |

## Capability matrix (INIT-GATEFLOW-001 — human_approved)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Health liveness | scaffold | `GET /health` | `test_health` | `verify_health` | In `verify_all` |
| GitHub App webhooks | FR-1 | `POST /webhooks/github` | `test_webhook_ingress` | `verify_webhook` | Live pass |
| RunStore + jobs | FR-5, FR-17 | ORM/repos + migration | `test_run_store_models` | via webhook | |
| TriggerRouter + preconditions | FR-2–4 | `trigger_router.py` | `test_trigger_policy` | label start disabled in 002 | |
| PolicyEngine | FR-7,8,10 | `policy_engine.py` | `test_trigger_policy` | — | Pin-driven; no allowlists |
| RunOrchestrator walker + Notifier | FR-2,9,11 | `run_orchestrator.py`, `notifier.py` | `test_run_orchestrator` | worker + implement-lane | Multi-hop until gate; hop cap |
| AgentRunner + launchpad | FR-9,17 | `cursor_agent_runner.py`, `launchpad_client.py` | via orchestrator tests | implement-lane | Live local SDK; launchpad W1 stub sync |
| ToolProvider none | FR-14 | (no StageToolResolver; empty tool context) | — | — | Slot map removed with YAML programme carrier |
| Status + metrics APIs | FR-13,15 | `runs_routes`, `metrics_routes` | `test_programme_token_api` | `verify_status_metrics` | Programme token |
| Orchestration settings | FR-18 | `orchestration_settings.py` (`GATEFLOW_*`) | wave-start / policy tests | — | notifier + hop cap + findings/metrics |
| W1 runbook | FR-19 | `docs/runbooks/orchestrate-new-initiative-repo.md` | — | inspection | |
| API + worker runtime | FR-17 | `src.main` + `src.worker_main` | `test_job_worker` | `docs/runbooks/w1-runtime-api-worker.md` | Dev reload scoped to `src/*.py` + `.env` |

## Capability matrix (INIT-GATEFLOW-002 W0)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Env notifier + SlotValidator | FR-16/23/18 | `GATEFLOW_NOTIFIER` + `slot_validator.py` | `test_slot_validator`, `test_wave_start` | — | No YAML programme file |
| Adapter registry + SlotValidator | FR-17/18 | `adapter_registry.py`, `slot_validator.py` | `test_slot_validator` | — | ADR-006 |
| API implement-lane start | FR-15; REQ-14/15 | `POST /api/v1/waves/implement/start` | `test_wave_start` | `verify_wave_start` | Programme token; ADR-005/010; manual node → 400 |
| API spec-lane start | REQ-14/16/17 | `POST /api/v1/waves/spec/start` | `test_wave_start`, `test_meta_pr_intake` | `verify_spec_lane` (opt-in) | Meta PR accept + dual dirs; pin must orchestrate start_node |
| Label start disabled | FR-15 | `trigger_router.py` | `test_trigger_policy` | note in wave-start | Webhook may still 202 |
| Run list + detail timeline | FR-20 | `runs_routes`, `metrics_emitter` | token + wave-start tests | `verify_wave_start` | Live pass |
| `runs.wave_id` column | FR-15/20 | ORM/repo + Alembic `bc8abad9a701` | — | via wave-start | Human migration applied |

## Capability matrix (INIT-GATEFLOW-002 W1)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Per-node runner/model resolve + persist | FR-16 | `dispatch_plan_models` + `node_model_resolver`; API plan | `test_node_model_resolver`, orchestrator | — | Inherit from wave-start; no programme overrides |
| Pin walker until gate | FR-15 inherit | `run_orchestrator.py` loop + PolicyEngine | `test_run_orchestrator` (multi-hop + hop cap) | implement-lane | `GATEFLOW_MAX_ORCHESTRATED_HOPS` |
| PR-at-start via ForgeClient | FR-19 | **superseded (INIT-008)** — start=`ensure_branch` only; Draft PR at `wave-pr-action` | `test_pr_branch_naming`, `test_forge_client`, orchestrator | `verify_implement_lane` | `verify_pr_thread` no longer asserts `pr_number` after enqueue |
| Metrics dims + api_trigger | FR-21/22 | `metrics_emitter.py`; retention via `GATEFLOW_METRICS_RETENTION_DAYS` | `test_metrics_emitter` | `verify_pr_thread`, status/metrics, implement-lane | `by_runner`, `by_model_id` |
| Cursor happy path (unit double) | FR-17 / V-3 | `cursor_agent_runner.py` | `test_cursor_agent_runner` | — | Unit `mock-*` only (`GATEFLOW_AGENT_STUB` removed) |

## Capability matrix (INIT-GATEFLOW-002 W2)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Board APIs (status/link/create/list) | FR-24 | `board_routes.py`, `board_service.py`; ForgeClient `board_*` | `test_board_service`, `test_forge_client_board` | `verify_board` | Issues MVP + labels; idempotent EPIC/Feature; post-label list wait (GitHub index lag) |
| Worker isolation | FR-24 | orchestrator / notifier only PR+comment | `test_process_job_never_calls_board_forge_mutations` | — | Zero board mutations on job complete |
| Production gh-free | FR-25/26a | ForgeClient httpx only | source guard test | checklist | `docs/runbooks/gh-free-production-path-checklist.md` |
| Forge auth modes (`pat` \| `app`) | ADR-003 / TDD §3.5a | `GithubTokenProvider` via InfraModule; `GITHUB_AUTH_MODE` required | `test_github_token_provider`, forge init | verify_board (mode+creds) | Explicit mode; no auto; App discovers single installation |
| Laptop vs deploy transport | FR-26b | runbook | — | inspection | `docs/runbooks/laptop-gh-vs-deploy-forgeclient.md` |
| Q-4 exit gate | A-4 | narrowed MVP doc | — | inspection | `docs/specification/reports/Q4-PERMISSION-MATRIX-INIT-GATEFLOW-002-W2.md` |

## Capability matrix (INIT-GATEFLOW-003 W0)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| `cursor-sdk` + `CursorAgentSettings` | REQ-27/29 | Poetry + `cursor_agent_settings.py` | `test_cursor_agent_settings` | — | `CURSOR_API_KEY` env only |
| Local CursorAgentRunner | REQ-27/31 | `cursor_agent_runner.py` | `test_cursor_agent_runner` | W1 implement-lane **pass** | `LocalAgentOptions(cwd)`; no cloud |
| Start-gate missing key | REQ-28/29 | `slot_validator.py`; API runner/model required | `test_slot_validator`, `test_wave_start` | — | 422 before enqueue |
| Unit doubles quarantine | REQ-28 | `mock-*` skill ids | unit only | not live exit | `GATEFLOW_AGENT_STUB` removed |
| Laptop SDK spike | REQ-27 / TDD §3.3 | spike report | inspection | — | `Spike-Cursor-Local-SDK-INIT-GATEFLOW-003-W0.md` |

## Capability matrix (INIT-GATEFLOW-003 W1)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Docker cursor-sdk bridge spike | REQ-27 / TDD §3.3 | spike report | inspection | — | `Spike-Cursor-Docker-INIT-GATEFLOW-003-W1.md` **pass** |
| Failure-path stage + duration | REQ-29/30 | `run_orchestrator.py`, `metrics_emitter.py` | `test_run_orchestrator`, `test_metrics_emitter` | — | FF-05 |
| `runs.wave_duration_ms` | REQ-30 | ORM/DTO/API + finalize | `test_run_orchestrator` | `verify_implement_lane` **pass** | Alembic `7e79269bd50b`; live `492608` ms |
| Implement-lane live prove-it | REQ-27/31 | `verify_implement_lane.py` | — | **pass** 2026-07-25; harness retarget 2026-07-29 | Pass-1 stop at `live-verify` (was `wave-human-decision`); D-W1-L1 closed |
| Pin walker (env + API + pin) | inherit FR-15 | `run_orchestrator.py` + pin outcomes | multi-hop + hop-cap unit | implement-lane | Enter-at `pre-implement`; lane handoffs `human_checkpoint: false` |

## Wave status

| Initiative / Wave | Plan | Ground report | as-built status |
|-------------------|------|---------------|-----------------|
| INIT-001 W0 | Control-plane skeleton | `Ground-Report-INIT-GATEFLOW-001-W0.md` | **human_approved** |
| INIT-001 W1 | Operational control plane | `Ground-Report-INIT-GATEFLOW-001-W1.md` | **human_approved** |
| INIT-002 W0 | API wave-start + run list/detail + stubs | `Ground-Report-INIT-GATEFLOW-002-W0.md` | **human_approved** |
| INIT-002 W1 | Per-node model + PR-at-start + metrics | `Ground-Report-INIT-GATEFLOW-002-W1.md` | **human_approved** |
| INIT-002 W2 | Board APIs + gh-free deploy path | `Ground-Report-INIT-GATEFLOW-002-W2.md` | **human_approved** |
| INIT-003 W0 | Cursor SDK skeleton + start-gate | `Ground-Report-INIT-GATEFLOW-003-W0.md` | **human_approved** |
| INIT-003 W1 | Implement-lane prove-it + cycle-time + Docker spike | `Ground-Report-INIT-GATEFLOW-003-W1.md` | **human_approved** |
| INIT-005 W0 | Bound-input resolve/render + thin Cursor + handoff_path | `Ground-Report-INIT-GATEFLOW-005-BOUNDINPUT-W0.md` | **human_approved** (2026-07-28; live implement-lane prove-it deferred to W1 — D-W0-V1) |
| INIT-005 W1 | Ingest-only `handoff_path` + dual-run isolation | `Ground-Report-INIT-GATEFLOW-005-BOUNDINPUT-W1.md` | **human_approved** (2026-07-28; live implement-lane deferred D-W1-V1 / D-W0-B1 — pin baton write) |
| INIT-006 W0/W1 | Pin workspace publish via ForgeClient | ADR-009 **Accepted** | **code complete (unit)** — live dogfood deferred |
| INIT-006 W2 | External-action forge + explicit authorize | ADR-009 **Accepted**; pin forge-side-effects | **code complete (unit)** — live authorize deferred; **REQ-7 superseded for `automated` nodes** by INIT-008 |
| INIT-006 W3 | Sparse PR run-event comments | as-built (not ADR catalogue) | **code complete (unit)** |
| INIT-008 (006A) | Pin `authorization` dual mode + wave-pr after loop-spec | [`product/INIT-GATEFLOW-008-gateflow.md`](../product/INIT-GATEFLOW-008-gateflow.md) | **W0+W1+W2 human_approved** (2026-07-31) — Ground-Report W2 + live verify pass; reviewed [#99](https://github.com/drivestream-lab/gateflow/pull/99) @ `e274a53`; **prove INIT-007 first** after W2 on `develop` (REQ-17) |
| INIT-007 | Closeout start + learning ingest | product INIT-007 **Draft** | **dogfood next** after INIT-008 W2 on `develop` (REQ-17) |

## Capability matrix (INIT-GATEFLOW-005 W1)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| `HandoffReader.read_path` | REQ-8b, REQ-9 | `handoff_reader.py` | `test_handoff_workflow` | — | Fail closed missing/empty |
| Packaged ingest SSOT = stored path | REQ-8b, REQ-9 | `run_orchestrator._ingest_handoff_after_stage` | `test_packaged_ingest_*` | fail-closed on empty baton | No ambient `find_latest_handoff`; D-W0-I1 closed |
| Dual-run baton isolation | REQ-8b | distinct `{root}/{run_id}/handoff.md` | `test_dual_run_isolation_*` | — | Shared workspace decoy ignored |
| Implement-lane live prove-it | REQ-10 | `verify_implement_lane` | — | **deferred** (D-W1-V1) | Hop-1 success + prompt ids; baton empty (D-W0-B1) |

## INIT-GATEFLOW-006 — truth split

| Layer | Owns for forge / lane work |
|-------|----------------------------|
| **ADR-009** (**Accepted**) | Publish/mutate **authority** (pin SSOT, ForgeClient, dual executor pattern, publish-before-ingest) |
| **ADR-010** (**Accepted**) | Lane intake **authority** (separate start contracts; meta PR accept; dual workspace bind) |
| **Pin** (`prayog-skills/workflow.yaml` + forge-side-effects) | Per-node `forge:` wiring, action vocabulary, orchestrated edges |
| **As-built (this section)** | What is implemented, unit-covered, live-deferred |
| **Product INIT** | Still **missing** for 006 — PE should add INIT/TDD when accepting ADR |

## Capability matrix (INIT-GATEFLOW-006 W0/W1 — workspace publish)

| Capability | Spec / authority | Code | Unit | Live verify | Notes |
|------------|------------------|------|------|-------------|-------|
| Parse pin `forge` on nodes | ADR-009; pin | `forge_models.py`, `WorkflowEngine.get_node` | `test_forge_policy` | — | Absent skill forge ⇒ publish disabled |
| `handoff.forge` instance slots | pin forge-side-effects | `HandoffEnvelope.forge` | `test_forge_policy` | — | Instance only; pin wins policy |
| Path collect (ignore + denylist) | ADR-009 path class | `workspace_commit_paths.py` | `test_workspace_commit_paths` | — | Dirty tree (skills must not commit) + optional `base_ref..HEAD` safety net; excludes handoff batons + secrets |
| Resolve run-head tip SHA | ADR-009 | `ForgeClient.get_branch_tip_sha` | `test_forge_client` | — | Fed as `base_ref` into path collect |
| Commit paths to run head | ADR-009 | `ForgeClient.commit_paths_to_branch` | `test_forge_client` | — | blobs → tree → commit → ref |
| Post-hop publish before ingest | ADR-009 ordering | `run_orchestrator._publish_stage_workspace_if_needed` | `test_publish_stage_workspace_*` | **deferred** | optional empty OK; required empty fail closed; tip+ahead publish |
| `branch_slug` rejects `w{n}-` prefix | FR-19 | `pr_branch_naming.validate_branch_slug` | `test_pr_branch_naming` | — | Avoids `…-w0-w0-…` when `wave_id` already embeds |
| Implement-lane assert `stage_commit` | as-built verify | `verify_implement_lane` | — | **deferred** | Required nodes must leave timeline commits when opted in |

## Capability matrix (INIT-GATEFLOW-006 W2 — external-action forge)

| Capability | Spec / authority | Code | Unit | Live verify | Notes |
|------------|------------------|------|------|-------------|-------|
| Merge pin ⋉ handoff; `requires` fail closed | ADR-009; pin | `merge_pin_and_handoff_forge` | `test_forge_merge` | — | Invented labels / action conflict fail closed |
| STOP at external-action + pending forge event | ADR-009 explicit auth | `run_orchestrator` STOP path | walker / policy tests | — | Content hop does not mutate |
| Open draft PR + projection labels | pin `open_draft_pr` | `ForgeClient.open_draft_pr`, `ForgeActionService` | `test_forge_client`, `test_forge_action_service` | **deferred** | Never `*-lgtm` |
| Board ticket seed from plan §9 | pin `create_board_tickets`; FR-24 primitives | `ForgeActionService` → `BoardService.create_ticket` | `test_forge_action_service` | **deferred** | Idempotent EPIC + wave Features |
| Programme authorize path | TDD / as-built | `POST /api/v1/runs/{id}/forge/authorize` | `test_forge_action_service` | **deferred** | Dual executor vs human forge skills |
| Worker board isolation | FR-24 | no BoardService in `process_job` | `test_process_job_never_calls_board_forge_mutations` | — | Authorize path may call board; walker must not |

## Capability matrix (INIT-GATEFLOW-006 W2 — sparse PR comments)

| Capability | Spec / authority | Code | Unit | Live verify | Notes |
|------------|------------------|------|------|-------------|-------|
| Milestone-only PR run-event comments | as-built UX | `Notifier.posts_run_event_to_pr` | `test_notifier` | — | `stage_*` skipped; `run_stopped` posts |
| `stage_started` on RunStore timeline | as-built | `run_orchestrator` append | orchestrator tests | — | Compensates skipping PR hop chatter |

## Capability matrix (INIT-GATEFLOW-006 W3/W4 — lane starts + meta intake)

| Capability | Spec / authority | Code | Unit | Live verify | Notes |
|------------|------------------|------|------|-------------|-------|
| Separate implement/spec start APIs | ADR-010; REQ-14…16 | `waves_routes`, `wave_start_models` | `test_wave_start` | `verify_wave_start` | Legacy `/waves/start` **deleted** |
| Spec meta accept-gate | ADR-010; REQ-17 | `meta_pr_intake`, ForgeClient `get_pull_request` | `test_meta_pr_intake` | `verify_spec_lane` opt-in | Initiative derive + mismatch fail closed |
| Dual bind `workspace` + `meta_workspace` | ADR-010; REQ-18 | `BoundPromptInputs`, orchestrator | `test_prompt_resolver` (existing) | deferred until pin schemas | |
| Persist `runs.meta_pr_url` / `meta_head_sha` | REQ-17 | ORM + models | unit create path | **needs human Alembic** | See open gaps |

## INIT-GATEFLOW-006 — open gaps

| Gap | Status |
|-----|--------|
| PE accept ADR-009 | **Accepted** 2026-07-28 (Cursor chat); approved head on accept commit |
| PE accept ADR-010 | **Accepted** 2026-07-29 (Cursor chat — implement session) |
| Product INIT / TDD for 006 | **Draft** — [`product/INIT-GATEFLOW-006-gateflow.md`](../product/INIT-GATEFLOW-006-gateflow.md); Gate 1 / meta PRD TBD (INIT Q-1) |
| Live dogfood (publish + `stage_commit` on run PR) | Deferred |
| Live authorize (`open_draft_pr` / board seed) | Deferred |
| Authorize then **resume** walker to next orchestrated node | Not implemented (mutate only; run stays STOPPED) |
| Human Alembic for `runs.meta_pr_url` + `runs.meta_head_sha` | **Required before live spec start** — ORM already declares columns |
| Spec-lane skills `dispatch: orchestrated` | Pin still `manual` — prayog-skills dependency (REQ-20) |

## Capability matrix (INIT-GATEFLOW-008 W1 — automated forge)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| EA policy: explicit STOP / automated APPLY_FORGE | REQ-6, REQ-7 | `policy_engine.py` | `test_trigger_policy` | — | Missing auth → BLOCK |
| Shared `apply_external_action` + head/base | REQ-7…9, REQ-12 | `forge_action_service.py`, `forge_models.py` | forge / orchestrator tests | — | Authorize reuses apply |
| Walker automated apply → live-verify STOP | REQ-5, REQ-8, REQ-11 | `run_orchestrator._apply_automated_forge` | `test_walker_*` / Pass-1 hop test | **pass** 2026-07-30 | No authorize for automated |
| Job start ensure_branch only | REQ-9, REQ-10 | `_ensure_run_branch` | `test_ensure_branch_before_stage_*` | **pass** (verify_implement_lane) | No PR-at-start create |
| Feature map Pass-1 PR timing | REQ-16 | `tests/README.md`, `verify_implement_lane.py` | — | **pass** | PR-at-start superseded note |

## Capability matrix (INIT-GATEFLOW-008 W2 — WorkManifest prayog/v1)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Pin `workmanifest_contract` before board create | REQ-13, REQ-14 | `run_workmanifest_contract` + `execute_create_board_tickets` | `test_forge_action_service`, `test_forge_merge` | `verify_board` launchpad reject | Accept only `prayog/v1` |
| Board create remains explicit authorize | REQ-15 | pin `board-tickets-action` + policy STOP | `test_board_tickets_action_remains_explicit_*` | — | Never APPLY_FORGE |
| Feature map / as-built / REQ-17 | REQ-16, REQ-17 | as-built, `tests/README.md`, `docs/specification/README.md` | — | review | 007 dogfood after 008 on develop |

## Capability matrix (INIT-GATEFLOW-010 W0 — pin parse + purpose/owner)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Harness pin ≡ submodule tip | REQ-01 | `.harness-pin.yaml` + `prayog-skills` submodule | inspect | N/A — P15 N/A | `v0.5.0-rc.2` @ `6561c7c`; `describe --exact-match --tags HEAD` green |
| Board-status forge parse | REQ-02 | `parse_node_forge`, `WorkflowEngine.get_node` | `test_forge_policy` | N/A — P15 N/A | `update_board_status` action/status/requires; 0 BROKEN remounted nodes |
| Pin purpose/owner on resolved node | REQ-10 | `ResolvedWorkflowNode`, `WorkflowEngine._to_resolved` | `test_pin_human_checkpoint_carries_purpose_and_owner` | N/A — P15 N/A | Optional fields; absent → None |
| `run_stopped` carries pin purpose/owner | REQ-10 | `run_orchestrator._finalize_run` | `test_walker_continues_then_stops_at_gate` | N/A — P15 N/A | Stop at `live-verify` includes `purpose: live-verify` |

| Gap | Status |
|-----|--------|
| Product INIT | **Accepted** — [`product/INIT-GATEFLOW-010-gateflow.md`](../product/INIT-GATEFLOW-010-gateflow.md); PE package accept 2026-08-05 |
| W0 pin parse + stop payload | **human_approved** — merge [#144](https://github.com/drivestream-lab/gateflow/pull/144) `0ca2376`; Live-Verify skipped (P15 N/A); Learning/Ground backfill on `develop` |
| APPLY_FORGE board-status apply | **human_approved** — REQ-03 on `develop` via [#146](https://github.com/drivestream-lab/gateflow/pull/146) merge `34e5813`; Ground-Report W1 |

## Capability matrix (INIT-GATEFLOW-010 W1 — board-status apply + implement In Progress)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| APPLY_FORGE `update_board_status` | REQ-03 | `ForgeActionService.execute_update_board_status` | `test_apply_update_board_status_*`, `test_forge_merge` | `verify_implement_lane` (board hop events) | Pin status → column via `board_column_for_pin_status`; missing ticket fail-closed |
| Implement-start In Progress pre-hop | REQ-04 | `WaveStartService._apply_implement_in_progress` | `test_implement_wave_start_ok`, `test_implement_in_progress_idempotent_*` | `verify_implement_lane` (`assert_board_in_progress`) | Before enqueue; idempotent when column already In Progress |
| No same-run resume after create-tickets | REQ-11 | `PolicyEngine.evaluate_dispatch` guard | `test_policy_create_tickets_pass_stops_same_run_resume` | secondary | `board-tickets-action` pass → STOP; implement via new API |
| Live implement_lane board asserts | REQ-17 (partial) | `verify_implement_lane.py`, `tests/README.md` | — | human at `live-verify` | In Progress column + optional `update_board_status` timeline evidence |

| Gap | Status |
|-----|--------|
| W1 board-status + implement In Progress | **human_approved** — merge [#146](https://github.com/drivestream-lab/gateflow/pull/146) `34e5813`; live verify pass 2026-08-05 run `852a0a42-…`; board [#139](https://github.com/drivestream-lab/gateflow/issues/139); [`Live-Verify-INIT-GATEFLOW-010-W1.md`](../reports/Live-Verify-INIT-GATEFLOW-010-W1.md); [`Ground-Report-INIT-GATEFLOW-010-W1.md`](../reports/Ground-Report-INIT-GATEFLOW-010-W1.md) |

## Capability matrix (INIT-GATEFLOW-010 W2 — ticket gates + create predicates)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Create triple predicate gate | REQ-06 | `create_board_tickets_gate.evaluate_*` + `execute_create_board_tickets` | `test_authorize_create_board_tickets_*` | `verify_board` / `verify_create_tickets` (authorize docs) | 422 + 0 creates on any predicate fail |
| Create success epic + wave ids | REQ-07 | `BoardTicketsSeedResult` post-create contract | `test_authorize_create_board_tickets_prayog_v1`, `*_requires_wave_ids` | authorize positive path | Non-empty `epic_ticket_id` + `wave_ticket_ids[]` |
| Implement-start ticket gate | REQ-08 | `implement_ticket_gate` + `WaveStartService.start_implement_wave` | `test_implement_malformed_*`, `test_implement_unresolvable_*`, `test_implement_rejects_done_*`, `test_implement_dual_identity_disagree` | `verify_wave_start` negative probes | 400 malformed; 422 unresolvable/mismatch/Done; 0 enqueue |
| Live verify co-ship | REQ-17 (partial) | `verify_wave_start.py`, `tests/README.md` | — | human at `live-verify` | Did not claim human smoke success in loop-spec |

| Gap | Status |
|-----|--------|
| W2 ticket gates + create predicates | **implemented** — loop-spec pass 2026-08-05; board [#140](https://github.com/drivestream-lab/gateflow/issues/140); live verify pending human at `live-verify` |

## INIT-GATEFLOW-010 — both-lane factory prove-out (**human_approved** freeze)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Pin consume (`v0.5.0-rc.2` family) | REQ-1 | `.harness-pin.yaml` + submodule | `make test` regression | N/A — W0 inspection | Submodule `72ad383` == tag tip; `spec-draft` orchestrated |
| W0 prove-out checklist | REQ-2 | `W0-Prove-Out-Checklist-INIT-GATEFLOW-009.md` | — | N/A — P15 N/A | Meta Gate 1, dual workspace, token, reviewer steps |
| Spec Pass-1 live prove-out | REQ-3…REQ-9 | existing APIs + pin walker | unit regression | **live** — [`Live-Verify-INIT-GATEFLOW-009-W1.md`](../reports/Live-Verify-INIT-GATEFLOW-009-W1.md) | run `89fd636d-…` → PR [#119](https://github.com/drivestream-lab/gateflow/pull/119); stop @ `technical-review-approval` |
| Closeout Pass-2 prove-out | REQ-10…REQ-12 | closeout route (INIT-007) | `test_wave_closeout` | **live** — [`Live-Verify-INIT-GATEFLOW-009-W2.md`](../reports/Live-Verify-INIT-GATEFLOW-009-W2.md) | run `4da11692-…` on [#126](https://github.com/drivestream-lab/gateflow/pull/126) after Spec #119 merge; lifts 007 REQ-15 **for 009 exit** |
| Authorize API live | REQ-13…REQ-15 | forge authorize path | `test_forge_action_service` | **PE-waived** (INIT-009 exit) | Unit-complete; no `verify_authorize` live run this INIT — see Feature-Readiness |
| Feature readiness freeze + CI | REQ-16…REQ-20 | [`Feature-Readiness-INIT-GATEFLOW-009.md`](../reports/Feature-Readiness-INIT-GATEFLOW-009.md); `.github/workflows/ci.yml` | — | CI on PRs | Placeholder replaced with `make check-ci` toolchain + unit tests |

| Gap | Status |
|-----|--------|
| Product INIT | **Freeze** — [`product/INIT-GATEFLOW-009-gateflow.md`](../product/INIT-GATEFLOW-009-gateflow.md); Feature-Readiness **2026-08-04** |
| W0 pin + checklist | **human_approved** — merged [#126](https://github.com/drivestream-lab/gateflow/pull/126) @ `f8b4577` |
| W1 spec-lane prove-out | **live proven** — board [#122](https://github.com/drivestream-lab/gateflow/issues/122); Live-Verify W1 |
| W2 closeout prove-out | **live proven** — board [#123](https://github.com/drivestream-lab/gateflow/issues/123); Live-Verify W2 |
| W3 authorize + freeze + CI | **human_approved (partial)** — board [#124](https://github.com/drivestream-lab/gateflow/issues/124); freeze + CI shipped; authorize live **PE-waived** |

## INIT-GATEFLOW-007 — wave closeout + learning DB (draft)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Closeout start API | REQ-1…8, REQ-13 | `POST /api/v1/waves/closeout/start` | `test_wave_closeout` | `verify_wave_closeout` smoke — **human_approved** | Fixed Enter-at `learning-extract`; required PR bind; no meta / no client `start_node` |
| Pass-2 pin walker | REQ-7 | pin graph | `test_handoff_workflow` | W2 dogfood — **human_approved** | `learning-extract` → `ground-spec` → `wave-signoff` |
| Learning Postgres SSOT | REQ-9…12 | `learning_ingest_service` + `learning_schema` + Alembic `cc5feda8fe3d` | `test_learning_ingest` | W2 dogfood — **human_approved** | W1 unit + human migration; orchestrator publish→handoff→ingest; no skill→HTTP (H6) |
| Pass-2 full prove-it (implement) | REQ-14, REQ-17 | `verify_wave_closeout` `dogfood: true` | — | **human_approved** | Merged [#107](https://github.com/drivestream-lab/gateflow/pull/107) @ `cd2640d`; see [`Live-Verify-INIT-GATEFLOW-007-W2.md`](../reports/Live-Verify-INIT-GATEFLOW-007-W2.md) |
| Spec-lane closeout (REQ-15) | REQ-15 | same route | — | **lifted for INIT-009 exit** | INIT-007 Q-6 deferral superseded for programme exit of INIT-009 — see [`Live-Verify-INIT-GATEFLOW-009-W2.md`](../reports/Live-Verify-INIT-GATEFLOW-009-W2.md) + Feature-Readiness-009 (closeout Pass-2 on #126 after Spec #119 merge). Literal open-Draft-Spec tip closeout still not separately dogfooded. |

| Gap | Status |
|-----|--------|
| Product INIT | **Draft** — [`product/INIT-GATEFLOW-007-gateflow.md`](../product/INIT-GATEFLOW-007-gateflow.md); Gate 1 TBD (Q-1) |
| W0 closeout start | **human_approved** — merged [#101](https://github.com/drivestream-lab/gateflow/pull/101) @ `e1604fd`; Ground-Report W0 **pass**; live smoke **human_approved** |
| W1 learning ingest | **human_approved** — merged [#102](https://github.com/drivestream-lab/gateflow/pull/102) @ `c4ce8f6`; Ground-Report W1 **pass**; human Alembic `cc5feda8fe3d`; live `verify_all` **approved** |
| W2 Pass-2 dogfood | **human_approved** — merged [#107](https://github.com/drivestream-lab/gateflow/pull/107) @ `cd2640d`; Live-Verify **human_approved**; REQ-15 deferral **lifted for INIT-009 exit** (see INIT-009 Feature-Readiness) |
| Authorize → resume into closeout skills | **Out of scope** — Pass-2 is new closeout Enter-at |

## Verdict

INIT-GATEFLOW-001 remains **human_approved**. INIT-GATEFLOW-002 **W0**, **W1**, and **W2** are
**human_approved** (2026-07-24). INIT-GATEFLOW-003 **W0** is **human_approved** (2026-07-24).

INIT-GATEFLOW-003 **W1** is **human_approved** (2026-07-25): live **implement-lane** prove-it
pass (run `de780ba2-7841-4827-ad69-362358a8176d`, four Cursor stages success, terminal
`stopped` at `wave-human-decision`, `wave_duration_ms=492608`). Implementation on `develop`
via #44; wave-signoff on `feature/INIT-GATEFLOW-003-w1-ground-report`.

**Lane naming (2026-07-26):** prefer **spec lane** / **implement lane** over Scenario A/B.

**INIT-GATEFLOW-005 (2026-07-28):** W0 **human_approved** on
`feature/INIT-GATEFLOW-005-w0-bound-input` — PromptResolver, message-only Cursor,
`GATEFLOW_HANDOFF_ROOT` baton define/store, required `ticket_id`, Alembic
`69de74666068`.

**INIT-GATEFLOW-005 W1 (2026-07-28):** **human_approved** on
`feature/INIT-GATEFLOW-005-w1-ingest` — packaged automate ingest uses
`HandoffReader.read_path(run.handoff_path)` only; dual-run isolation unit green;
D-W0-I1 closed. Live implement-lane deferred (D-W1-V1 / D-W0-B1 — pin must write
envelope to stored path). See `Ground-Report-INIT-GATEFLOW-005-BOUNDINPUT-W1.md`.

**INIT-GATEFLOW-006 (2026-07-29):** Product INIT **draft** at
[`product/INIT-GATEFLOW-006-gateflow.md`](../product/INIT-GATEFLOW-006-gateflow.md).
**ADR-009** + **ADR-010 Accepted**. Forge unit-complete (#70); lane start APIs
cut over (implement/spec); ambient handoff scan removed; meta accept + dual bind
unit-wired. Still open: live forge dogfood, human Alembic for `runs.meta_*`,
pin orchestrate for spec-draft chain, INIT-005 W2 (out of track).

**INIT-GATEFLOW-007 (2026-08-01):** Product INIT **draft**. **W0** / **W1** / **W2**
**human_approved** (#101 / #102 / #107 @ `cd2640d`). W2: `verify_wave_closeout`
dogfood **human_approved**. **REQ-15** spec-lane closeout deferral **lifted for
INIT-009 programme exit** (2026-08-04 Feature-Readiness + Live-Verify-009-W2).
Board [#84](https://github.com/drivestream-lab/gateflow/issues/84) /
[#87](https://github.com/drivestream-lab/gateflow/issues/87).

**INIT-GATEFLOW-009 (2026-08-04):** Feature readiness **freeze** —
[`Feature-Readiness-INIT-GATEFLOW-009.md`](../reports/Feature-Readiness-INIT-GATEFLOW-009.md).
W0–W2 live proven; W3 CI + freeze shipped; **authorize live PE-waived**. Epic
[#120](https://github.com/drivestream-lab/gateflow/issues/120).

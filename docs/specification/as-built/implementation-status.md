# Implementation status (as-built)

| Field | Value |
|-------|-------|
| Repo | drivestream-lab/gateflow |
| Updated | 2026-08-08 |
| Source | INIT-GATEFLOW-012 W3 **human_approved** (board [#188](https://github.com/drivestream-lab/gateflow/issues/188); Draft PR [#194](https://github.com/drivestream-lab/gateflow/pull/194) @ `0007bff` `wave-accepted`; Ground-Report W3 **pass**); INIT-GATEFLOW-012 W2 **human_approved** (board [#187](https://github.com/drivestream-lab/gateflow/issues/187); Draft PR [#193](https://github.com/drivestream-lab/gateflow/pull/193) @ `3191407` `wave-accepted`; Ground-Report W2 **pass**); INIT-GATEFLOW-012 W1 **human_approved** (board [#186](https://github.com/drivestream-lab/gateflow/issues/186); Draft PR [#192](https://github.com/drivestream-lab/gateflow/pull/192) @ `aa4445e` `wave-accepted`; Ground-Report W1 **pass**); INIT-GATEFLOW-012 W0 **human_approved** (board [#185](https://github.com/drivestream-lab/gateflow/issues/185); Draft PR [#191](https://github.com/drivestream-lab/gateflow/pull/191) @ `0fb1f2f` `wave-accepted`; Ground-Report W0 **pass**); INIT-GATEFLOW-010 W0+W1+W2+W3 **human_approved** (W0 [#144](https://github.com/drivestream-lab/gateflow/pull/144) `0ca2376`; W1 [#146](https://github.com/drivestream-lab/gateflow/pull/146) `34e5813`; W2 [#148](https://github.com/drivestream-lab/gateflow/pull/148) `ba6d804`; W3 [#150](https://github.com/drivestream-lab/gateflow/pull/150) `85c2ec5`); INIT-GATEFLOW-011 W0+W1 **human_approved** (W0 [#171](https://github.com/drivestream-lab/gateflow/pull/171) `088d125`; W1 [#172](https://github.com/drivestream-lab/gateflow/pull/172) `3074e82`) + W2 **merged** ([#174](https://github.com/drivestream-lab/gateflow/pull/174) `ba2ab7b`) + W3 **human_approved** (board [#164](https://github.com/drivestream-lab/gateflow/issues/164); PR [#175](https://github.com/drivestream-lab/gateflow/pull/175) @ `438761a` `wave-accepted`; Ground-Report W3 **pass**) + W4 **human_approved** (board [#165](https://github.com/drivestream-lab/gateflow/issues/165); PR [#176](https://github.com/drivestream-lab/gateflow/pull/176) @ `ed3d6be` `wave-accepted`; Ground-Report W4 **pass**; merge `0774e1b`) + W5 **human_approved** (board [#166](https://github.com/drivestream-lab/gateflow/issues/166); PR [#177](https://github.com/drivestream-lab/gateflow/pull/177) @ `069989e` `wave-accepted`; Ground-Report W5 **pass**) + W6 **human_approved** (board [#167](https://github.com/drivestream-lab/gateflow/issues/167); PR [#178](https://github.com/drivestream-lab/gateflow/pull/178) @ `0b0f144` `wave-accepted`; Ground-Report W6 **pass**); INIT-GATEFLOW-008 (006A) W0–W2 human_approved; INIT-007 W0–W2 human_approved; INIT-009 human_approved freeze; pin ref `v0.5.0-rc.2` (launchpad tip family; submodule HEAD includes `live-verify`→`wave-acceptance`) |

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

## Capability matrix (INIT-GATEFLOW-012 W0 — tenant registry)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Tenant register / attach / read/list | REQ-01–09, REQ-32 | `tenant_routes`, `tenant_service`, ORM | `test_tenant_*`, `test_github_pat_probe`, `test_tenant_token` | `verify_tenant_registry` (human; P15) | PAT plaintext G1; never in responses; ADR-011 Option A; human owns Alembic `versions/` |
| Eager PAT probe (repo metadata GET) | REQ-06 | `github_pat_probe` | `test_github_pat_probe` | `verify_tenant_registry` | Per-call credential; not ForgeClient singleton |
| Tenant board default on omit | REQ-08 | `BoardService.resolve_board_default` | `test_resolve_board_default_*` | secondary | Explicit override wins |

**INIT-GATEFLOW-012 W0 status:** **human_approved** at wave-acceptance — Draft PR [#191](https://github.com/drivestream-lab/gateflow/pull/191) @ `0fb1f2f` label `wave-accepted`; Ground-Report W0 **pass**. Human DDL still required for live DB (`DDL-NOTE-INIT-GATEFLOW-012-W0-tenants.md`). Merge/publish at `wave-signoff` only.

## Capability matrix (INIT-GATEFLOW-012 W1 — repo clone/refresh)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Omitted path + registered → deterministic workspace | REQ-10 | `tenant_git_workspace_client`, `wave_start_service`, `run_orchestrator` | `test_tenant_git_workspace_client`, `test_wave_start`, `test_run_orchestrator` | `verify_workspace_lifecycle` (human; P15) | Path `{workspace_root}/{org}/{repo}`; no `Path.cwd()` for registered |
| Git auth via stored Tenant PAT | REQ-11 | `TenantGitWorkspaceClient` + repo credential lookup | client + service tests | live secondary | PAT never logged; `http.extraHeader` Basic auth |
| Explicit `workspace_path` unchanged | REQ-12 | wave-start / orchestrator branch | `test_implement_explicit_path_*` | secondary | Additive; smoke helpers pass cwd |
| Valid checkout → fetch-in-place | REQ-13 | client fetch branch | unit + live | `verify_workspace_lifecycle` | Depends on A-2 persistent disk |
| Mismatch checkout → 422 untouched | REQ-14 | client mismatch raise | unit + live | `verify_workspace_lifecycle` | Named `workspace_mismatch` |
| Omitted + unregistered → 422 0 enqueue | REQ-15 | wave-start before board/enqueue | unit + live | `verify_workspace_lifecycle` | Fail-closed; no guess |
| Per-repo lock (TF-01) | — | asyncio lock per org+repo | `test_per_repo_lock_*` | — | Independent of W4 concurrency broaden |
| Pin existing nodes 0 BROKEN (PE-1 W1 waiver) | REQ-10 gate | `.harness-pin.yaml` `v0.5.0-rc.2` | `test_all_remounted_pin_nodes_parse` | N/A | New CTR-01 shapes hard-gated for **pin-shape consume** (DEP-02); W2 coding-start waived — see PE-Waiver W2 |

**INIT-GATEFLOW-012 W1 status:** **human_approved** at wave-acceptance — Draft PR [#192](https://github.com/drivestream-lab/gateflow/pull/192) @ `aa4445e` label `wave-accepted`; Ground-Report W1 **pass**. Merge/publish at `wave-signoff` only.

## Capability matrix (INIT-GATEFLOW-012 W2 — branch create-or-reuse)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| New wave forks from live develop tip | REQ-16 | `RunOrchestrator.resolve_branch` → `ensure_branch_from_base` | `test_resolve_branch_new_wave_*` | `verify_branch_lifecycle` (human; P15) | Live base tip at fork time |
| Deterministic head naming | REQ-17 | `build_wave_head_branch` / `branch_slug_from_head_ref` | `test_pr_branch_naming` | secondary | No second scheme |
| Continuation reuses head; zero new refs | REQ-18 | `resolve_branch` continuation path | `test_resolve_branch_continuation_*` | `verify_branch_lifecycle` | No `ensure_branch_from_base` when tip exists / explicit `head_ref` |
| Never-cloned + continuation | REQ-19 | tenant clone/fetch + `checkout_branch` | checkout unit + live | `verify_branch_lifecycle` | Omitted-path only checks out (not explicit cwd) |
| Missing continuation head fail-closed | — | explicit `head_ref` + tip miss | `test_resolve_branch_explicit_head_missing_*` | secondary | Reason `continuation branch not found on remote` |
| PE-1 W2 coding-start waiver | REQ-16–19 gate | pin `v0.5.0-rc.2` | `test_all_remounted_pin_nodes_parse` | N/A | CTR-01 consume still DEP-02 |

**INIT-GATEFLOW-012 W2 status:** **human_approved** at wave-acceptance — Draft PR [#193](https://github.com/drivestream-lab/gateflow/pull/193) @ `3191407` label `wave-accepted`; Ground-Report W2 **pass**. PE waiver: `PE-Waiver-INIT-GATEFLOW-012-W2-PE1.md`. CTR-01 pin-shape consume remains DEP-02. Merge/publish at `wave-signoff` only.

## Capability matrix (INIT-GATEFLOW-012 W3 — harness-readiness)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Real harness artifact check | REQ-21 | `LaunchpadClient.sync_harness` | `test_launchpad_client` | `verify_harness_readiness` (human; P15) | Requires `.harness-pin.yaml` + `.harness/`; named `harness_artifacts_missing` |
| Gate after workspace before Enter-at | REQ-20 | `RunOrchestrator._ensure_harness_ready` + wave-start companion | orchestrator + `test_wave_start` harness cases | `verify_harness_readiness` | Fail closed; 422 / 0 enqueue on start; run FAILED if job path |
| Verified cache + force re-check | REQ-22 | `tenant_repos.harness_verified` + `force_harness_recheck` | cache/skip/force units | secondary | Column from W0 DDL-NOTE; no agent `versions/` write |
| CTR-03 consume only | — | filesystem contract | — | — | No CTR-01 pin-shape invent; remount still DEP-02 |

**INIT-GATEFLOW-012 W3 status:** **human_approved** at wave-acceptance — Draft PR [#194](https://github.com/drivestream-lab/gateflow/pull/194) @ `0007bff` label `wave-accepted`; Ground-Report W3 **pass**. CTR-01 pin-shape consume remains DEP-02. Merge/publish at `wave-signoff` only.

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
| Board APIs (status/link/create/list) | FR-24 | `board_routes.py`, `board_service.py`; ForgeClient `board_*` | `test_board_service`, `test_forge_client_board` | `verify_board` | Issues labels + Project V2 Status sync on column; idempotent EPIC/Feature; post-label list wait |
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
| Implement-lane live prove-it | REQ-27/31 | `verify_implement_lane.py` | — | **pass** 2026-07-25; harness retarget 2026-07-29; remount hygiene 2026-08-06 | Pass-1 stop at `wave-acceptance` (was `live-verify` / earlier `wave-human-decision`); D-W1-L1 closed |
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
| Open draft PR + projection labels | pin `open_draft_pr` | `ForgeClient.open_draft_pr`, `ForgeActionService` (materializes `body_path` from `signals.pr_body` when purge-app omits on-disk body) | `test_forge_client`, `test_forge_action_service` | **deferred** live authorize; unit covers signals.pr_body | Never `*-lgtm` |
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
| Walker automated apply → wave-acceptance STOP | REQ-5, REQ-8, REQ-11 | `run_orchestrator._apply_automated_forge` | `test_walker_*` / Pass-1 hop test | **pass** 2026-07-30; retarget 2026-08-06 | No authorize for automated; pin tip stop id `wave-acceptance` |
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
| Harness pin ≡ submodule tip | REQ-01 | `.harness-pin.yaml` + `prayog-skills` submodule | inspect | N/A — P15 N/A | Pin ref `v0.5.0-rc.2` (launchpad-applied tip family); consume tip graph (`wave-acceptance`, no `/verify`) |
| Board-status forge parse | REQ-02 | `parse_node_forge`, `WorkflowEngine.get_node` | `test_forge_policy` | N/A — P15 N/A | `update_board_status` action/status/requires; 0 BROKEN remounted nodes |
| Pin purpose/owner on resolved node | REQ-10 | `ResolvedWorkflowNode`, `WorkflowEngine._to_resolved` | `test_pin_human_checkpoint_carries_purpose_and_owner` | N/A — P15 N/A | Optional fields; absent → None |
| `run_stopped` carries pin purpose/owner | REQ-10 | `run_orchestrator._finalize_run` | `test_walker_continues_then_stops_at_gate` | N/A — P15 N/A | Stop at `wave-acceptance` includes `purpose: wave-acceptance` |

| Gap | Status |
|-----|--------|
| Product INIT | **Accepted** — [`product/INIT-GATEFLOW-010-gateflow.md`](../product/INIT-GATEFLOW-010-gateflow.md); PE package accept 2026-08-05 |
| W0 pin parse + stop payload | **human_approved** — merge [#144](https://github.com/drivestream-lab/gateflow/pull/144) `0ca2376`; Live-Verify skipped (P15 N/A); Learning/Ground backfill on `develop` |
| APPLY_FORGE board-status apply | **human_approved** — REQ-03 on `develop` via [#146](https://github.com/drivestream-lab/gateflow/pull/146) merge `34e5813`; Ground-Report W1 |

## Capability matrix (INIT-GATEFLOW-010 W1 — board-status apply + implement In Progress)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| APPLY_FORGE `update_board_status` | REQ-03 | `ForgeActionService.execute_update_board_status` | `test_apply_update_board_status_*`, `test_forge_merge` | `verify_implement_lane` (board hop events) | Pin status → column via `board_column_for_pin_status`; missing ticket fail-closed; label **+** Project V2 Status sync |
| Implement-start In Progress pre-hop | REQ-04 | `WaveStartService._apply_implement_in_progress` | `test_implement_wave_start_ok`, `test_implement_in_progress_idempotent_*` | `verify_implement_lane` (`assert_board_in_progress`) | Before enqueue; idempotent when column already In Progress; Project Status synced with label |
| No same-run resume after create-tickets | REQ-11 | `PolicyEngine.evaluate_dispatch` guard | `test_policy_create_tickets_pass_stops_same_run_resume` | secondary | `board-tickets-action` pass → STOP; implement via new API |
| Live implement_lane board asserts | REQ-17 (partial) | `verify_implement_lane.py`, `tests/README.md` | — | human at `wave-acceptance` | In Progress column + optional `update_board_status` timeline evidence |

| Gap | Status |
|-----|--------|
| W1 board-status + implement In Progress | **human_approved** — merge [#146](https://github.com/drivestream-lab/gateflow/pull/146) `34e5813`; live verify pass 2026-08-05 run `852a0a42-…`; board [#139](https://github.com/drivestream-lab/gateflow/issues/139); [`Live-Verify-INIT-GATEFLOW-010-W1.md`](../reports/Live-Verify-INIT-GATEFLOW-010-W1.md); [`Ground-Report-INIT-GATEFLOW-010-W1.md`](../reports/Ground-Report-INIT-GATEFLOW-010-W1.md) |

## Capability matrix (INIT-GATEFLOW-010 W2 — ticket gates + create predicates)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Create triple predicate gate | REQ-06 | `create_board_tickets_gate.evaluate_*` + `execute_create_board_tickets` | `test_authorize_create_board_tickets_*` | `verify_board` / `verify_create_tickets` (authorize docs) | 422 + 0 creates on any predicate fail |
| Create success epic + wave ids | REQ-07 | `BoardTicketsSeedResult` post-create contract | `test_authorize_create_board_tickets_prayog_v1`, `*_requires_wave_ids` | authorize positive path | Non-empty `epic_ticket_id` + `wave_ticket_ids[]` |
| Implement-start ticket gate | REQ-08 | `implement_ticket_gate` + `WaveStartService.start_implement_wave` | `test_implement_malformed_*`, `test_implement_unresolvable_*`, `test_implement_rejects_done_*`, `test_implement_dual_identity_disagree` | `verify_wave_start` negative probes | 400 malformed; 422 unresolvable/mismatch/Done; 0 enqueue |
| Board status label + Project Status | REQ-03/04 follow-on | `ForgeClient.update_issue_status` | `test_update_issue_status_*` Project Status | human board UI | Lifts INIT-002 Issues-MVP deferral for Status; fail closed if no project item / option |
| Live verify co-ship | REQ-17 (partial) | `verify_wave_start.py`, `verify_implement_lane.py`, `tests/README.md` | — | **human_approved** — [`Live-Verify-INIT-GATEFLOW-010-W2.md`](../reports/Live-Verify-INIT-GATEFLOW-010-W2.md) | run `89b7b7d9-…` → PR [#148](https://github.com/drivestream-lab/gateflow/pull/148) |

| Gap | Status |
|-----|--------|
| W2 ticket gates + create predicates | **human_approved** — merge [#148](https://github.com/drivestream-lab/gateflow/pull/148) `ba6d804`; board [#140](https://github.com/drivestream-lab/gateflow/issues/140); live-verify run `89b7b7d9-…`; [`Live-Verify-INIT-GATEFLOW-010-W2.md`](../reports/Live-Verify-INIT-GATEFLOW-010-W2.md); [`Ground-Report-INIT-GATEFLOW-010-W2.md`](../reports/Ground-Report-INIT-GATEFLOW-010-W2.md); Project Status sync on tip |

## Capability matrix (INIT-GATEFLOW-010 W3 — closeout Done + no merge/lgtm/auto-chain)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Closeout Done hop after ground-spec.pass | REQ-05 | `RunOrchestrator` automated `wave-done-action` apply | `test_closeout_walk_applies_done_then_stops_at_wave_signoff` | `verify_wave_closeout` dogfood | Timeline `forge_executed` at `wave-done-action` |
| Terminal purpose at wave-signoff | REQ-05 | `run_orchestrator._finalize_run` | same + `test_pin_human_checkpoint_carries_purpose_and_owner` | `verify_wave_closeout` | `run_stopped.payload.purpose=wave-signoff` |
| No Forge merge | REQ-09 | `ForgeActionService` + `ForgeClient.enable_auto_merge` | `test_forge_action_type_excludes_merge`, `test_forge_client_forbids_auto_merge` | secondary | Merge human-only at wave-signoff |
| Never auto-apply `*-lgtm` | REQ-16 | `parse_node_forge`, `merge_pin_and_handoff_forge`, apply guard | `test_apply_external_action_rejects_lgtm_apply_labels` | secondary | Fail closed at authorize/apply |
| No auto-chain after wave-signoff | REQ-19 | `PolicyEngine.evaluate_dispatch` guards | `test_policy_wave_signoff_pass_stops_no_auto_chain`, `test_policy_wave_complete_pass_stops_no_auto_chain` | `verify_wave_closeout` | PE starts next wave/closure via dedicated APIs |
| Live closeout co-ship | REQ-17 (partial) | `verify_wave_closeout.py`, `tests/README.md` | `test_wave_closeout` | **human_approved** — Pass-2 dogfood run `75dd6b42-…` | Done hop + purpose + no auto-chain; Learning-Extract W3 present |
| Live implement_lane (Pass-1) | REQ-17 (partial) | `verify_implement_lane.py`, `tests/README.md` | — | **human_approved** — [`Live-Verify-INIT-GATEFLOW-010-W3.md`](../reports/Live-Verify-INIT-GATEFLOW-010-W3.md) | run `5385e416-…` → PR [#150](https://github.com/drivestream-lab/gateflow/pull/150); historical stop @ `live-verify`; tip pin stop id `wave-acceptance` |

| Gap | Status |
|-----|--------|
| W3 closeout Done + guards + no auto-chain | **human_approved** — merge [#150](https://github.com/drivestream-lab/gateflow/pull/150) `85c2ec5`; board [#141](https://github.com/drivestream-lab/gateflow/issues/141) Done; Pass-1 run `5385e416-…`; Pass-2 closeout `75dd6b42-…`; [`Live-Verify-INIT-GATEFLOW-010-W3.md`](../reports/Live-Verify-INIT-GATEFLOW-010-W3.md); [`Ground-Report-INIT-GATEFLOW-010-W3.md`](../reports/Ground-Report-INIT-GATEFLOW-010-W3.md) |

## Capability matrix (INIT-GATEFLOW-010 W4 — closure Enter-at + freeze)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Closure start API (REQ-12) | REQ-12 | `POST /api/v1/initiatives/closure/start` | `test_closure_start` | `verify_initiative_closure` smoke | Programme token; 202 + run_id; malformed → 4xx |
| Done-gate (REQ-13) | REQ-13 | `closure_done_gate.assert_closure_done_gate` | `test_closure_done_gate_*` | `verify_initiative_closure` optional probe | 422; 0 enqueue; EPIC untouched on fail |
| EPIC Done before purge (REQ-14) | REQ-14 | `ClosureStartService.start_closure` | `test_closure_start_ok` | human @ wave-acceptance | Board hygiene before purge-app Enter-at |
| Closure purge walk (REQ-15) | REQ-15 | `RunOrchestrator` closure lane guards | `test_closure_walk_purge_then_pr_action_stops_at_signoff_app` | `verify_initiative_closure` stage guard | purge-app → closure PR → STOP signoff-app; never meta |
| Partial failure hygiene (REQ-20) | REQ-20 | `RunOrchestrator._partial_closure_failure_payload` | `test_closure_partial_failure_after_epic_done_records_req20` | human negative path | `partial_closure_failure`; no closure-complete claim |
| Live closure co-ship (REQ-17) | REQ-17 | `verify_initiative_closure.py`, `tests/README.md` | unit matrix | Pass-1 implement_lane **human_approved** | [`Live-Verify-INIT-GATEFLOW-010-W4.md`](../reports/Live-Verify-INIT-GATEFLOW-010-W4.md); `verify_initiative_closure` happy 202 needs all waves Done |
| Feature-readiness freeze (REQ-18) | REQ-18 | [`Feature-Readiness-INIT-GATEFLOW-010.md`](../reports/Feature-Readiness-INIT-GATEFLOW-010.md) | review | inspection | Proven vs deferred eng capabilities |

| Gap | Status |
|-----|--------|
| W4 closure Enter-at + freeze | **ground-spec pass (pending signoff)** — board [#142](https://github.com/drivestream-lab/gateflow/issues/142) Done; Draft PR [#152](https://github.com/drivestream-lab/gateflow/pull/152) open; Pass-1 run `6f14f48f-…`; Pass-2 closeout `6b917688-…`; [`Live-Verify-INIT-GATEFLOW-010-W4.md`](../reports/Live-Verify-INIT-GATEFLOW-010-W4.md); [`Ground-Report-INIT-GATEFLOW-010-W4.md`](../reports/Ground-Report-INIT-GATEFLOW-010-W4.md); human `wave-signoff` merge pending |

## Capability matrix (INIT-GATEFLOW-011 W0 — checkpoint status-check foundation)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| ForgeClient reviews / check-runs / merge fields | REQ-02 | `ForgeClient.list_reviews`, `list_check_runs`, `GithubPullRequestDocument.merged*` | `test_forge_client` | secondary | Read-only; CAP-01 evidence |
| Pin checkpoint vocabulary | REQ-02 | `WorkflowEngine.get_github_checkpoint_vocab` | `test_checkpoint_vocab` | — | Six `review_roles` keys; labels validated against contract catalog |
| Live CAP-01 evaluate | REQ-01, REQ-04, REQ-05 | `CheckpointEvidenceService.evaluate` | `test_checkpoint_evidence` | `verify_checkpoint_status` | Itemized misses; GitHub down → `could_not_verify`; 0 mutate calls |
| GET `/api/v1/checkpoints/status` | REQ-01, REQ-05, REQ-28 | `checkpoints_routes.py`, `public_paths` | `test_checkpoints_api` | `verify_checkpoint_status` | Programme-token; non-GET 405; no persistence (W1) |

| Gap | Status |
|-----|--------|
| Product INIT | **Accepted** — [`product/INIT-GATEFLOW-011-gateflow.md`](../product/INIT-GATEFLOW-011-gateflow.md); PE package accept 2026-08-06; spec PR [#159](https://github.com/drivestream-lab/gateflow/pull/159) |
| W0 checkpoint status-check foundation | **human_approved** — board [#161](https://github.com/drivestream-lab/gateflow/issues/161); PR [#171](https://github.com/drivestream-lab/gateflow/pull/171) @ `088d125` `wave-accepted`; Ground-Report W0 **pass** (GF-01 closed); L-01 open for codify; merge pending wave-signoff |
| Check persistence / history / composed readout | deferred — W1 |
| Initiative / wave visibility GETs | deferred — W2+ |

## Capability matrix (INIT-GATEFLOW-011 W1 — check persistence + composed readout)

|| Capability | Spec | Code | Unit | Live verify | Notes |
||------------|------|------|------|-------------|-------|
| Persist `checkpoint_check` run_event on every evaluate (correlated to run when resolvable) | REQ-06 | `CheckpointEvidenceService._persist_check` + `_append_checkpoint_event`; `RunEventNameType.CHECKPOINT_CHECK`; `CheckpointCheckPayloadDocument`; `RunRepository.find_run_by_pr` | `test_checkpoint_persistence` | `verify_checkpoint_history` | Skipped (logged) when no run for PR; payload carries initiative/wave from resolved run |
| Stale evidence → not_satisfied + reason; checked_sha/checked_at always present | REQ-03 | `CheckpointEvidenceService._detect_stale_reason` (approval commit_id vs head SHA) | `test_checkpoint_evidence` (stale/fresh/no-approval cases) | `verify_checkpoint_history` | Never silent pass; reason `stale — new commits since approval` |
| GET `/api/v1/checkpoints/history` marks records historical | REQ-07, REQ-28 | `CheckpointEvidenceService.list_history` + `checkpoints_routes.get_checkpoint_history`; `CheckpointHistoryResult`/`CheckpointHistoryRecord` (`historical=true`) | `test_checkpoints_api`, `test_checkpoint_persistence` | `verify_checkpoint_history` | Never claims live verdict; empty 200 when no run |
| Composed readout via initiative+wave; 404 no run found for this wave | REQ-08, REQ-28 | `CheckpointEvidenceService.evaluate_composed` + `/status` composed query params | `test_checkpoints_api`, `test_checkpoint_persistence` | `verify_checkpoint_history` | 400 when neither raw nor composed supplied; 404 distinct from malformed id |

|| Gap | Status |
||-----|--------|
|| W1 check persistence + composed readout | **human_approved** — board [#162](https://github.com/drivestream-lab/gateflow/issues/162); PR [#172](https://github.com/drivestream-lab/gateflow/pull/172) @ `3074e82` `wave-accepted`; Ground-Report W1 **pass** (no GF-* findings; Learning-Extract `items: []` — W0 L-01 did not recur); merge pending wave-signoff |
|| Initiative / wave visibility GETs | deferred — W2+ |

## Capability matrix (INIT-GATEFLOW-011 W2 — initiative list/detail Gateflow-owned)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Initiative list/detail from runs + board EPIC tickets (Gateflow-owned) | REQ-09, REQ-10 | `InitiativeReadoutService.list_initiatives` / `get_initiative`; `initiative_readout_models.py`; `initiatives_routes.py` GET `/initiatives` + `/initiatives/{id}` | `test_initiative_readout`, `test_initiatives_read_api` | `verify_initiatives_readout` | Union of distinct `initiative_id` on runs + EPIC board tickets in `org/repo`; affected_repos deduped from runs; current_stage from active run / EPIC column / latest run |
| `prd_approval=unavailable` until W3 meta bridge | REQ-09, REQ-10 | `PrdApprovalStateType.UNAVAILABLE` + `prd_approval_reason` "meta bridge not yet wired (W3)" | `test_initiative_readout`, `test_initiatives_read_api` | `verify_initiatives_readout` | W2 wires no meta PR read; W3 populates via composed CAP-01 against `prd-impact-acceptance` |
| GET-only on `/initiatives` + `/initiatives/{id}`; 401 without token; 404 unknown initiative | REQ-28 | `initiatives_routes.py` GET handlers + `verify_programme_service_token`; `/api/v1/initiatives` on `public_paths` | `test_initiatives_read_api` | `verify_initiatives_readout` | Non-GET 405; existing `POST /initiatives/closure/start` (INIT-010 W4) unchanged |

| Gap | Status |
|-----|--------|
| W2 initiative list/detail (Gateflow-owned) | **human_approved + merged** — board [#163](https://github.com/drivestream-lab/gateflow/issues/163) Done; PR [#174](https://github.com/drivestream-lab/gateflow/pull/174) merged `ba2ab7b` (accepted product tip `e9654c2` `wave-accepted`; Pass-2 docs tip `caa496e`); Ground-Report W2 **pass** (no GF-* findings; Learning-Extract `items: []`); wave-signoff complete |
| Initiative PRD-approval via meta bridge | deferred — W3 (see W3 matrix below) |

## Capability matrix (INIT-GATEFLOW-011 W3 — meta bridge + partial success)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| PRD approval via CAP-01 on meta PR (`prd-impact-acceptance`) | REQ-09 | `InitiativeReadoutService._resolve_prd_approval` → `CheckpointEvidenceService.evaluate` + `MetaPrIntakeService.parse_url` from run `meta_pr_url` | `test_initiative_readout` (meta-up satisfied / not_satisfied) | `verify_initiative_meta_bridge` | Uses `evaluate` (meta `CheckpointPrRef`), **not** `evaluate_composed` (app wave PR) |
| Meta unreachable / missing meta URL → 200 + `unavailable`; owned fields present | REQ-11 | `_map_cap01_verdict` maps CAP-01 `could_not_verify` → `unavailable`; catch transport / NotFound → `unavailable` | `test_initiative_readout` (could_not_verify, ConnectError, NotFound, invalid URL, no meta URL) | `verify_initiative_meta_bridge` | Partial success envelope — never 5xx on initiative GET for meta-down |
| GET-only / programme-token / 404 unknown (unchanged routes) | REQ-28 | existing `initiatives_routes.py` GET handlers | `test_initiatives_read_api` | `verify_initiative_meta_bridge` | No new mutate surface |

| Gap | Status |
|-----|--------|
| W3 meta bridge + partial success | **human_approved** — board [#164](https://github.com/drivestream-lab/gateflow/issues/164); PR [#175](https://github.com/drivestream-lab/gateflow/pull/175) @ `438761a` `wave-accepted`; Ground-Report W3 **pass** (no GF-* findings; Learning-Extract `items: []`); merge pending wave-signoff |
| Wave map / later CAP-04+ GETs | deferred — W4+ (see W4 matrix below) |

## Capability matrix (INIT-GATEFLOW-011 W4 — wave map readout)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Per-wave status ∈ {done, ready-to-start, blocked, active}; blocked names why | REQ-14 | `WaveMapService.get_wave_map`; `wave_map_models.py` (`WaveMapStatusType`); GET `/initiatives/{id}/waves` | `test_wave_map_service`, `test_initiatives_read_api` | `verify_wave_map` | Priority: Done column → `done`; active run → `active`; predecessor not Done → `blocked` + reason; else `ready-to-start` |
| Derived from board Feature tickets + runs only — no new wave-state store | REQ-15 | `BoardService.list_tickets(Feature)` + `RunRepository.list_runs`; wave id from Feature title `\bW\d+\b` | `test_wave_map_service` | `verify_wave_map` | No new ORM table / Alembic; REQ-15 forbids parallel store |
| GET-only `/initiatives/{id}/waves`; 401 without token; 404 unknown initiative | REQ-28 | `initiatives_routes.py` GET handler + programme token; `/api/v1/initiatives` on `public_paths` | `test_initiatives_read_api` | `verify_wave_map` | Non-GET 405; zero Forge writes from CAP-05 path |

| Gap | Status |
|-----|--------|
| W4 wave map readout | **human_approved** — board [#165](https://github.com/drivestream-lab/gateflow/issues/165); PR [#176](https://github.com/drivestream-lab/gateflow/pull/176) @ `ed3d6be` `wave-accepted`; Ground-Report W4 **pass** (no GF-* findings; Learning-Extract `items: []`); merge pending wave-signoff |
| Later CAP-04 / CAP-06+ GETs | deferred — W5+ (see W5 matrix below) |

## Capability matrix (INIT-GATEFLOW-011 W5 — spec lane readout)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Draft Spec PR link + artifacts + findings + pin next step | REQ-12 | `SpecReadoutService.get_spec_readout`; `spec_readout_models.py`; GET `/initiatives/{id}/spec` | `test_spec_readout_service`, `test_initiatives_read_api` | `verify_spec_readout` | Ready when `pr_number` or `forge_executed@spec-pr-action`; findings from handoff/stop blockers |
| Plain not-ready before `spec-pr-action`; never broken URL | REQ-13 | `readiness=not_ready` + `readiness_reason`; `draft_spec_pr_url=null` | `test_spec_readout_service` | `verify_spec_readout` | Unavailable when initiative known but no spec-lane run (`meta_pr_url`) |
| GET-only `/initiatives/{id}/spec`; 401; 404 unknown | REQ-28 | `initiatives_routes.py` GET + programme token | `test_initiatives_read_api` | `verify_spec_readout` | Non-GET 405; zero Forge writes |

| Gap | Status |
|-----|--------|
| W5 spec lane readout | **human_approved** — board [#166](https://github.com/drivestream-lab/gateflow/issues/166); PR [#177](https://github.com/drivestream-lab/gateflow/pull/177) @ `069989e` `wave-accepted`; Ground-Report W5 **pass** (no GF-* findings; Learning-Extract `items: []`); merge pending wave-signoff |
| Later CAP-06+ GETs | deferred — W6+ (see W6 matrix below) |

## Capability matrix (INIT-GATEFLOW-011 W6 — wave implementation progress)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Per-task timeline + Draft PR when `wave-pr-action` succeeded | REQ-16 | `ImplementationReadoutService.get_implementation_readout`; `implementation_readout_models.py`; GET `.../waves/{wave_id}/implementation` | `test_implementation_readout_service`, `test_initiatives_read_api` | `verify_wave_implementation` | Prefer implement-lane run (`wave_id`, no `meta_pr_url`); PR from `pr_number` or `forge_executed@wave-pr-action` |
| Named task + reason on failure / needs-input stop | REQ-17 | `failed_task_id` + `failure_reason` from stage/handoff/stop context | `test_implementation_readout_service` | `verify_wave_implementation` | Smoke asserts reason when failed_task_id present |
| GET-only implementation route; 401; 404 unknown | REQ-28 | `initiatives_routes.py` GET + programme token | `test_initiatives_read_api` | `verify_wave_implementation` | Non-GET 405; zero Forge writes |

| Gap | Status |
|-----|--------|
| W6 wave implementation progress | **human_approved** — board [#167](https://github.com/drivestream-lab/gateflow/issues/167); PR [#178](https://github.com/drivestream-lab/gateflow/pull/178) @ `0b0f144` `wave-accepted`; Ground-Report W6 **pass** (no GF-* findings; Learning-Extract `items: []`); merge pending wave-signoff |
| Later CAP-07+ GETs | deferred — W7+ (see W7 matrix below) |

## Capability matrix (INIT-GATEFLOW-011 W7 — closeout readout + drift)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Itemized closeout additions (learning / ground) | REQ-18 | `CloseoutReadoutService.get_closeout_readout`; `closeout_readout_models.py`; GET `.../waves/{wave_id}/closeout` | `test_closeout_readout_service`, `test_initiatives_read_api` | `verify_wave_closeout_readout` | Prefer implement-lane run; learning rows + stages `learning-extract` / `ground-spec` |
| Advisory drift vs wave-acceptance baseline SHA | REQ-19 | baseline from historical `checkpoint_check` (`wave-acceptance`); PR head via Forge GET | `test_closeout_readout_service` | `verify_wave_closeout_readout` | Missing baseline → `unknown_no_baseline` + plain message; mismatch → `drifted` |
| Drift never blocks closeout mechanics | REQ-20 | `advisory_only=True` always | `test_closeout_readout_service` | `verify_wave_closeout_readout` | Smoke asserts `advisory_only` true |
| GET-only closeout route; 401; 404 unknown | REQ-28 | `initiatives_routes.py` GET + programme token | `test_initiatives_read_api` | `verify_wave_closeout_readout` | Non-GET 405; zero Forge writes |

| Gap | Status |
|-----|--------|
| W7 closeout readout + drift | **human_approved** — board [#168](https://github.com/drivestream-lab/gateflow/issues/168); PR [#179](https://github.com/drivestream-lab/gateflow/pull/179) @ `6bd8336` `wave-accepted`; live smoke human at wave-acceptance |
| Later CAP-08+ GETs | deferred — W8+ (see W8 matrix below) |

## Capability matrix (INIT-GATEFLOW-011 W8 — merge confirm + completion)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Merge confirm via CAP-01 `wave-signoff` | REQ-21 | `MergeReadoutService.get_merge_readout`; `merge_readout_models.py`; GET `.../waves/{wave_id}/merge` | `test_merge_readout_service`, `test_initiatives_read_api` | `verify_merge_and_completion` | Reuses `CheckpointEvidenceService.evaluate`; PR `merged` + `merge_commit_sha` |
| Next-wave nudge after confirmed merge | REQ-22 | nudge when next CAP-05 status is `ready-to-start` | `test_merge_readout_service` | `verify_merge_and_completion` | Plain `"wave W{n+1} is now unblocked"` |
| Completion eligibility rollup | REQ-23 | `CompletionReadoutService.get_completion_readout`; GET `.../completion` | `test_completion_readout_service` | `verify_merge_and_completion` | ready_to_close / waiting_on_waves / no_waves_found |
| Pure CAP-05 reuse (no parallel status logic) | REQ-24 | calls `WaveMapService.get_wave_map` only | `test_completion_readout_service` | `verify_merge_and_completion` | Echoes `waves[]` for transparency |
| GET-only merge + completion; 401; 404 | REQ-28 | `initiatives_routes.py` + programme token | `test_initiatives_read_api` | `verify_merge_and_completion` | Non-GET 405; zero Forge writes |

| Gap | Status |
|-----|--------|
| W8 merge confirm + completion | **human_approved** — board [#169](https://github.com/drivestream-lab/gateflow/issues/169); PR [#180](https://github.com/drivestream-lab/gateflow/pull/180) @ `a0de226` `wave-accepted`; Ground-Report W8 **pass** (no GF-* findings; Learning-Extract `items: []`); merge pending wave-signoff |
| Later CAP-10 GETs | see W9 matrix below |

## Capability matrix (INIT-GATEFLOW-011 W9 — closure preview + CAP-01 reuse)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Pre-purge plan from purge allowlist | REQ-25 | `ClosurePreviewService` + `build_purge_plan_preview`; GET `.../closure` | `test_closure_preview_service`, `test_initiatives_read_api` | `verify_closure_preview` | plan_source cites artifact-write-contract; `not_yet_run` when purge-app not executed |
| Post-purge deleted/kept | REQ-26 | execution from handoff `signals.deleted` / `refused` / `missing_ok` | `test_closure_preview_service` | `verify_closure_preview` | Prefer run handoff / `run_stopped` handoff_context |
| CAP-01 closure signoff reuse | REQ-27 | `CheckpointEvidenceService.evaluate` for `initiative-closure-signoff-app` + `-meta` | `test_closure_preview_service` | `verify_closure_preview` | When `closure_pr_number` present |
| GET-only closure preview; 401; 404 | REQ-28 | `initiatives_routes.py` GET + programme token | `test_initiatives_read_api` | `verify_closure_preview` | Distinct from POST `.../closure/start`; non-GET 405 |

| Gap | Status |
|-----|--------|
| W9 closure preview + CAP-01 reuse | **human_approved** — board [#170](https://github.com/drivestream-lab/gateflow/issues/170); PR [#181](https://github.com/drivestream-lab/gateflow/pull/181) @ `1ce031f` `wave-accepted`; Ground-Report W9 **pass** (no GF-* findings; Learning-Extract `items: []`); merge pending wave-signoff |

## INIT-GATEFLOW-010 — initiative freeze (W4 exit target)

| Capability | Status |
|------------|--------|
| Eng lane tip parity (spec → tickets → implement → closeout → eng closure) | **W4 code green** — human `wave-signoff` merge pending |
| PM Enter-at / meta purge | **deferred** — out of repo scope |
| ops UI / C2 / authorize→resume | **deferred** — see Feature-Readiness |

## INIT-GATEFLOW-010 — both-lane factory prove-out (**human_approved** freeze)

| Capability | Spec | Code | Unit | Live verify | Notes |
|------------|------|------|------|-------------|-------|
| Pin consume (`v0.5.0-rc.2` tip family) | REQ-1 | `.harness-pin.yaml` + submodule | `make test` regression | N/A — W0 inspection | Tip graph: `wave-acceptance` (not `live-verify`); `spec-draft` orchestrated |
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

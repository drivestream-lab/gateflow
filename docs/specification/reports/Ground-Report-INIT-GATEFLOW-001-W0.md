# Ground report — INIT-GATEFLOW-001 W0

| Field | Value |
|-------|-------|
| Wave | W0 — Control plane skeleton |
| Spec | `docs/specification/product/INIT-GATEFLOW-001-gateflow.md` |
| Date | 2026-07-23 |
| Branch | `feature/INIT-GATEFLOW-001-w0-control-plane` |
| Status | Draft — **code complete; live evidence incomplete** |
| Review deadline | 2026-07-27 |
| Deciders | Tech lead / reviewer: @nikd10x — explicit LGTM required |

## Automated check output

`ground_command`: N/A (no Makefile ground target). Evidence: `make check`, `make test`, attempted live verify.

### `make check` (exit 0)

```
.venv/bin/black --line-length 100 src/ tests/
All done! 93 files left unchanged.
.venv/bin/ruff check --fix src/ tests/
All checks passed!
.venv/bin/pyright
0 errors, 0 warnings, 0 informations
.venv/bin/lint-imports
Layered architecture — no cross-layer imports KEPT
Contracts: 1 kept, 0 broken.
```

### `make test` (exit 0)

```
collected 24 items
tests/unit/test_forge_client.py ... PASSED (2)
tests/unit/test_handoff_workflow.py ... PASSED (5)
tests/unit/test_health.py ... PASSED (1)
tests/unit/test_job_worker.py ... PASSED (2)
tests/unit/test_programme_config.py ... PASSED (4)
tests/unit/test_run_store_models.py ... PASSED (5)
tests/unit/test_webhook_ingress.py ... PASSED (5)
24 passed
```

### Live verify `.venv/bin/python -m tests.verify.verify_webhook`

```
[ERROR] GITHUB_WEBHOOK_SECRET is required for verify_webhook
```

Also: `postgres_migrations/versions/` contains only `.gitkeep` — **no human RunStore revision applied**. Live happy-path cannot succeed until migration + running API + webhook secret.

## FR checklist

W0 scope (plan §1–§2): FR-1, FR-5, FR-6, FR-7 (resolve only), FR-12 (comments + forbid), FR-17 (partial worker), FR-18.

| FR | Spec claim | Verified artifact | Status |
|----|-----------|-------------------|--------|
| FR-1 | Webhook signature + idempotency + enqueue; 401/503 | `POST /webhooks/github`; `WebhookIngressService.enqueue_webhook_job`; unit HMAC/idempotency tests; `public_paths` includes `/webhooks` | **partial** — unit pass; live verify blocked |
| FR-5 | Postgres RunStore (runs/stages/events/jobs) | `run_store_schema.py` + repos + DTO unit tests; DDL note for human | **partial** — ORM/repos present; Alembic `versions/` empty |
| FR-6 | HandoffReader (ref + globs) | `HandoffReader.resolve_git_ref` / `find_latest_handoff`; unit fixtures | **pass** (unit) |
| FR-7 | WorkflowEngine resolve next node (no dispatch) | `WorkflowEngine.load_pin` / `resolve_next` against pin; unit `board-seed`→`pre-implement` | **pass** (resolve-only; PolicyEngine W1) |
| FR-12 | ForgeClient comments; forbid gate labels/auto-merge | `ForgeClient.post_comment`; `add_labels` / `enable_auto_merge` raise; unit forbid tests | **pass** (unit/inspection) |
| FR-17 | API + async worker; job claim | `src/worker_main.py` + `JobWorkerService.claim_and_process_one` stub; unit claim/process | **partial** — stub only; no live worker/docker proof this run |
| FR-18 | Programme config load fail-fast | `load_programme_config` in API/worker startup; unit missing/invalid | **pass** |

Out-of-wave (W1 — expected fail/not started): FR-2–4, FR-8–11, FR-13–16, FR-19.

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Dual process API + worker; jobs in Postgres | ADR-001 | **pass** (code); live claim unproven |
| Webhook on `public_paths`; signature zone | ADR-002 | **pass** |
| ForgeClient infra; handoff/workflow business | ADR-003 | **pass** |
| Programme YAML singleton; secrets in env | ADR-004 | **pass** |
| Models in `src/models/`; repos map ORM→Pydantic | pydantic-schemas / repository-pattern | **pass** |
| import-linter layers | python-tooling | **pass** |
| No agent-authored `versions/` files | database-migrations | **pass** — human revision still outstanding |
| Fail-fast missing programme config / webhook secret at startup | fail-fast / ADR-002 | **pass** (GithubSettings required field) |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Scaffold DI + Postgres/Redis lifecycle | prior scaffold | yes |
| JWT middleware + allowlist | scaffold / ADR-002 | yes — extended with `/webhooks` |
| Prior-wave Ground Report | N/A (W0 first wave) | N/A |
| Pin `prayog-skills` workflow + delivery-contract | CTR-01 / `.harness-pin.yaml` | yes — `WorkflowEngine.load_pin` reads local pin |

## Discrepancies (must fix before human checkpoint)

| ID | FR | Finding | Severity |
|----|----|---------|---------|
| D-W0-M1 | FR-5 | Human Alembic revision for RunStore tables not created/applied (`versions/` empty) | Critical |
| D-W0-V1 | FR-1 | Live `verify_webhook` not green — `GITHUB_WEBHOOK_SECRET` missing in environment used for verify; API/DB not proven | Critical |
| D-W0-V2 | FR-17 | Live worker claim against docker-compose not executed this ground run | Medium |

## Contracts produced by this wave

> Usable as W1 `/pre-implement` baseline **after** D-W0-M1/D-W0-V1 cleared (or PE explicitly defers live evidence). Until then treat live paths as unconfirmed.

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| ProgrammeConfig load | programme config loader + models | `load_programme_config` / `ProgrammeConfig.get_instance` | YAML path (`config/programme.yaml` or `PROGRAMME_CONFIG_PATH`) | Validated trigger/handoff/retry/metrics/runner/model/tools | Missing/invalid fails process start; not injector-bound | W1 |
| Webhook enqueue | webhook ingress service + route | `enqueue_webhook_job` / `POST /webhooks/github` | delivery id, event type, payload, signature validity | job id or idempotent no-op; 401 invalid sig; 503 on persist failure | No PolicyEngine/AgentRunner in request path; idempotent on delivery id | W1 TriggerRouter |
| Job claim stub | job worker service + worker entry | `claim_and_process_one` / `worker_main` loop | pending job rows | claimed then processed (stub) | SKIP LOCKED; W0 does not dispatch agents | W1 RunOrchestrator |
| RunStore persistence | run_store schema + repositories | create/enqueue/claim/mark_* / create_run / append_event | Pydantic create DTOs | Pydantic models | ORM only in repos; JSONB validated | W1 status/metrics |
| Handoff read | HandoffReader | `resolve_git_ref` / `find_latest_handoff` / `parse_handoff_yaml` | workspace root + programme globs / PR head | HandoffEnvelope | No chat fallback; fail on missing/unparsable | W1 PolicyEngine |
| Workflow resolve | WorkflowEngine | `load_pin` / `resolve_next` | handoff stage+outcome + pin files | ResolvedWorkflowNode (id, type, dispatch) | No hardcoded allowlists; contract mismatch raises | W1 PolicyEngine |
| Forge comments | ForgeClient | `post_comment`; forbid `add_labels`/`enable_auto_merge` | owner/repo/issue + body | comment id; PermissionError on forbidden ops | No gate-approval labels; no auto-merge; PAT non-prod only | W1 Notifier |

## PR instructions

> Clear D-W0-M1 + D-W0-V1 before marking the wave PR ready, **or** document PE-accepted deferral of live verify in the PR body.

Branch:   `feature/INIT-GATEFLOW-001-w0-control-plane`
PR title: `[INIT-GATEFLOW-001 W0] control-plane — implementation + ground report`
Required reviewer: prayog-pe-team / CODEOWNERS
Review deadline: 2026-07-27

After reviewer approves (when Ready = yes):
  Update as-built: W0 → human_approved
  Merge PR
  → `/pre-implement` for W1

## Ready for human checkpoint?

**no** — unit/static evidence is green and contracts are documented, but **human RunStore migration** and **live `verify_webhook`** remain Critical discrepancies (FR-1 / FR-5).

Human must (when re-grounded green, or PE defers live path explicitly):
- [ ] Review FR checklist — all W0 FRs pass or explicitly deferred
- [ ] Review §Contracts produced — accurate and complete for W1
- [ ] Mark as-built: INIT-GATEFLOW-001 W0 = human_approved

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: findings
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-001-W0.md
    digest: sha256:58fcf19a38829a4d76374d1fc42d08685ba25e58f78aba2c6206bf1adf613732
  blockers:
    - D-W0-M1
    - D-W0-V1
  signals:
    wave: W0
    contracts_produced: 7
    wave_code_complete: true
    unit_pass: true
    live_verify_pass: false
    human_migration_applied: false
    board_issue: https://github.com/drivestream-lab/gateflow/issues/6
    branch: feature/INIT-GATEFLOW-001-w0-control-plane
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
```

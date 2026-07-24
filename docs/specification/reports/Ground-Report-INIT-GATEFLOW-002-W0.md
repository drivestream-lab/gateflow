# Ground report — INIT-GATEFLOW-002 W0

| Field | Value |
|-------|-------|
| Wave | W0 — API trigger skeleton + run list/detail + stubs |
| Spec | `docs/specification/product/INIT-GATEFLOW-002-gateflow.md` |
| Date | 2026-07-24 |
| Branch | `feature/INIT-GATEFLOW-002-w0-api-trigger-skeleton` |
| Status | **human_approved** |
| Review deadline | 2026-07-28 |
| Deciders | Tech lead / reviewer: @nikd10x — human LGTM recorded 2026-07-24 (live `verify_all` green) |

## Automated check output

`ground_command`: N/A. Evidence: `make check`, `make test`, `.venv/bin/python -m tests.verify.verify_all`.

Human Alembic `bc8abad9a701_add_runs_wave_id` applied before this ground run (see `DDL-NOTE-INIT-GATEFLOW-002-W0-wave-id.md`).

### `make check` (exit 0)

```
.venv/bin/black --line-length 100 src/ tests/
All done! 125 files left unchanged.
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
collected 52 items
52 passed
```

### Live verify `.venv/bin/python -m tests.verify.verify_all` (exit 0)

```
[OK] verify_health passed
[OK] verify_webhook passed (401 / 202 / duplicate)
[OK] verify_status_metrics passed (401 / 404 / 200 metrics + run list shape)
[OK] verify_wave_start passed (401 / 2xx start / detail timeline / list filter / label ingress ack)
[OK] verify_all passed
```

## FR checklist

W0 plan scope: FR-15, FR-17, FR-18, FR-20, FR-23 skeleton, FR-16 config partial. FR-19 / FR-21 / FR-22 / full FR-16 runtime resolution are **W1** (explicitly out of this wave).

| FR | Spec claim | Verified artifact | Status |
|----|-----------|-------------------|--------|
| FR-15 | Authenticated wave-start only; dual identity; enqueue + `run_id`; label start disabled | `POST /api/v1/waves/start`; `WaveStartService`; `TriggerRouter` label reject; `test_wave_start`; `verify_wave_start` | **pass** (unit + live) |
| FR-16 | Per-node runner/model resolve + persist on stages | W0: `NodeOverride` coerce + override profile validation at start; full per-node persist/dispatch = W1 | **partial** — config shape + start validation only (plan W0) |
| FR-17 | Cursor implemented; OpenCode / Claude Code stubs registered | `AdapterRegistry.initialize`; stub runners; `test_slot_validator` | **pass** (unit) |
| FR-18 | Fail-closed stub/config before enqueue; unused stubs OK | `SlotValidator.validate_for_run`; 422 on stub notifier; `test_wave_start` / `test_slot_validator` | **pass** (unit) |
| FR-19 | PR at run start + comments on that PR | W1 scope | **deferred** — not W0 |
| FR-20 | Run list/filter + detail timeline under programme token | `GET /api/v1/runs`; enriched `GET /api/v1/runs/{id}`; `verify_wave_start` / `verify_status_metrics` | **pass** (unit + live) |
| FR-21 | Metrics dims by runner / model_id | W1 scope (INIT-001 `by_workflow_node` still live) | **deferred** — not W0 |
| FR-22 | Multi-stage metrics events incl. api_trigger | W1 scope | **deferred** — not W0 |
| FR-23 | GitHub notifier live; Slack/Teams stubs; fail-closed selection | registry ids + `notifier.default=github_comment`; stub notifier 422 | **pass** (unit; live GitHub post path unchanged from INIT-001) |
| FR-24…26 | Board APIs / gh-free | W2 scope | **deferred** — not W0 |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Programme-token mutations on allowlisted control-plane routes | ADR-005 | **pass** — `/api/v1/waves` in `public_paths` + Bearer dependency |
| Business registry + fail-closed before accept | ADR-006 | **pass** — `AdapterRegistry` + `SlotValidator` before enqueue |
| Adapters = infra; validation/orchestration = business | ADR-003 | **pass** — stub runners/notifiers under `infra_services/` |
| Programme YAML authority; secrets in env | ADR-004 | **pass** — `notifier.*` in YAML; token in env |
| Dual process; durable RunStore | ADR-001 | **pass** — run + job at accept; worker reuses `run_id` |
| Models in `src/models/`; repos map ORM↔Pydantic | pydantic-schemas / repository-pattern | **pass** |
| Human owns Alembic versions | database-migrations.mdc | **pass** — `bc8abad9a701_add_runs_wave_id` human-authored |
| import-linter layers | python-tooling | **pass** |

## Cross-spec contracts consumed

Source: `Ground-Report-INIT-GATEFLOW-001-W1.md` §Contracts produced.

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| ProgrammeConfig load | Ground-Report-001-W1 | yes — extended with `notifier` + `NodeOverride` |
| Webhook enqueue | Ground-Report-001-W1 | yes — still live-verified |
| Trigger authorize | Ground-Report-001-W1 | yes with **intentional drift** — label start disabled; `api_trigger` path added |
| Job orchestration | Ground-Report-001-W1 | yes — reuses pre-created `run_id` from API start |
| RunStore persistence | Ground-Report-001-W1 | yes — plus `wave_id` column |
| Programme-token AuthN | Ground-Report-001-W1 | yes — widened to wave-start writes (ADR-005) |
| Run status read | Ground-Report-001-W1 | yes — plus stages/events timeline + `wave_id` |
| Metrics aggregate | Ground-Report-001-W1 | yes — W0 does not add runner/model dims yet |
| Forge comments | Ground-Report-001-W1 | yes — GitHub path unchanged |

## Discrepancies (must fix before human checkpoint)

| ID | FR | Finding | Severity |
|----|----|---------|----------|
| D-W0-V1 | FR-15 | Live verify proves API start + label ingress ack; does **not** assert worker claim of `api_trigger` job → orchestrator end-to-end | Medium — accept for W0 skeleton; deepen in dogfood / W1 |
| D-W0-M1 | FR-16 | Per-node override **runtime** resolution + stage field persistence deferred to W1 (config coerce + start validation only) | Low — matches plan W0 scope |
| D-W0-L1 | FR-15 | Labelled webhook still returns 202 at ingress; start rejection is in `TriggerRouter` on worker claim | Low — documented; matches TDD §3.7 (webhook may ack non-start) |

No blocking discrepancies for W0 exit if PE accepts D-W0-V1/M1/L1 as in-scope.

## Contracts produced by this wave

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Wave start HTTP | waves route + WaveStartService | `POST /api/v1/waves/start` | Bearer programme token + body (ticket **or** initiative+wave; org/repo; optional PR/issue/workspace) | `{ run_id, job_id?, status }` | 401 without token; 400 identity; 409 concurrent; 422 stub/config; 503 store; no AgentRunner / board calls on request path | W1 |
| Dual identity resolve | WaveStartService | `_resolve_identity` | ticket and/or initiative+wave | resolved initiative, wave, issue number | Both forms must agree (`initiative:wave` ticket form) or 400 | W1 |
| Slot fail-closed | SlotValidator + AdapterRegistry | `validate_for_run` | required runner ids + notifier id + config keys | ok **or** failures `[{slot_kind, adapter_id, config_key, reason}]` | Required stub/unknown → fail; unused stubs ignored | W1 |
| Adapter catalogue | AdapterRegistry | `initialize` / `get` / `list_adapters` | opaque adapter id | capability `{implemented}` + slot kind | cursor + github_comment implemented; opencode, claude_code, slack, teams stubs | W1 |
| Label start policy | TriggerRouter | `authorize_and_check` | event type + payload | authorized + context **or** failures | Non-`api_trigger` wave start rejected for 002; webhook may still ack | W1 |
| API trigger job | WaveStartService → JobRepository | enqueue with `event_type=api_trigger` | delivery id + run_id + org/repo/wave identity | pending job row | Worker must reuse `run_id`; exclude self from concurrent check | W1 |
| Run list | runs route + MetricsEmitter | `GET /api/v1/runs` | Bearer + filters (initiative, wave, status, org, repo, limit, skip) | `{ items, limit, skip }` | 401 without token; invalid limit/skip → 400 | W1 / ops |
| Run detail timeline | runs route + MetricsEmitter | `GET /api/v1/runs/{run_id}` | Bearer + run id | header + `stages[]` + `events[]` (+ wave_id) | 401/404; timeline from RunStore only | W1 |
| Programme config v2 | ProgrammeConfig | `load_programme_config` | YAML | validated config incl. `notifier.default`, `model.overrides` as objects | Missing notifier fails load; legacy override strings coerce | W1 (`pr.*`) |
| Wave identity store | RunStore schema/repo | `create_run` / `find_active_run` / `list_runs` | wave_id + initiative_id fields | Pydantic run models | Concurrent by wave identity or PR/issue; human Alembic applied | W1 |
| Wave-start verify | tests.verify | `verify_wave_start` / `verify_all` | running API + secrets + migrated DB | exit 0 | API start primary; label smoke superseded as primary | W1 verify extend |

## PR instructions

> Commit this report + updated as-built row to the wave branch (last commit before PR is marked ready). Ground report and code are reviewed together on the same PR — do not open a separate PR for the ground report.

```
Branch:   feature/INIT-GATEFLOW-002-w0-api-trigger-skeleton
PR title: [INIT-GATEFLOW-002 W0] api-trigger-skeleton — implementation + ground report
Issue:    #12
Spec:     docs/specification/product/INIT-GATEFLOW-002-gateflow.md
Verify:   make check && make test ; .venv/bin/python -m tests.verify.verify_all
```

Required reviewer: per CODEOWNERS / prayog-pe-team  
Review deadline: 2026-07-28

After reviewer approves:
  Update as-built: INIT-GATEFLOW-002 W0 → human_approved
  Merge PR
  → `/pre-implement` for W1 (reads §Contracts produced above)

## Ready for human checkpoint?

**yes — human_approved** (2026-07-24). Live `verify_all` re-validated; D-W0-V1 / D-W0-M1 / D-W0-L1 accepted as deferred for W0 skeleton / W1.

- [x] Review FR checklist — all pass or explicitly deferred
- [x] Review §Contracts produced — accurate for W1 consumers
- [x] Mark as-built: INIT-GATEFLOW-002 W0 = human_approved

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-002-W0.md
    digest: sha256:4b2c3292d5dc413bfe7721a124ae37d39fbd77e4db2ed7ebf590fb9005674c28
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-002
    wave: W0
    board_issue: https://github.com/drivestream-lab/gateflow/issues/12
    branch: feature/INIT-GATEFLOW-002-w0-api-trigger-skeleton
    contracts_produced: 11
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_all
    unit_tests: 52 passed
    live_verify: passed
    human_alembic: bc8abad9a701_add_runs_wave_id
    human_approved: true
    deferred_frs: [FR-19, FR-21, FR-22, FR-24, FR-25, FR-26a, FR-26b]
  next_candidates:
    - wave-complete
  human_checkpoint: false
  external_action: true
```

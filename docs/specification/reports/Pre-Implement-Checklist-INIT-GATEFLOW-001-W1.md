# Pre-implement checklist — drivestream-lab/gateflow / W1 — Operational control plane

Produced by `/pre-implement` on 2026-07-23. **No product code in this stage.**

---

### Gate check (prior wave)

| Item | Required | Status |
|------|----------|--------|
| Branch context | `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | **ok** — on `develop` @ `c198620` |
| Spec PR merged | Implementation plan on integration branch | **yes** — `Implementation-Plan-INIT-GATEFLOW-001.md` on `develop` |
| Gate 2 at merge | Merged spec PR had `spec-lgtm` on head | **verified** — PR #4 MERGED; label `spec-lgtm`; merge `72b1a87` |
| Board seed | Wave issue(s) from plan §9 exist | **seeded** — EPIC #5; W0 #6 (CLOSED); W1 #7 (OPEN); both sub-issues of #5 |
| Plan source freshness | all upstream rows `CURRENT` | **current** — spec/feasibility/TDD digests match `sha256sum` on disk |
| Impact-map repo scope | revision and scope digest match canonical handoff | **match** — plan rows CURRENT (rev 3; scope digest as in plan frontmatter) |
| `check_command` | resolved | **`make check`** |
| `test_command` | resolved | **`make test`** |
| `verify_command` | resolved or N/A | **resolved** — W1 target: `.venv/bin/python -m tests.verify.verify_wave_start` (+ `verify_status_metrics`); until scripts land use `verify_all` as baseline smoke |
| `ground_command` | resolved or N/A | **N/A** — `/ground-spec` skill (no Makefile ground target) |
| Prior wave as-built row | `human_approved` | **W0 = human_approved** |
| Prior Ground Report exists | `Ground-Report-*-W0.md` | **exists** |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 complete | **complete** (N/A for W1 gate; recorded) |

**Gate verdict:** PASS

---

### Contracts consumed (from prior Ground Report)

Source: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-001-W0.md` §Contracts produced. Confirmed against `src/`.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| ProgrammeConfig load | `load_programme_config` / `ProgrammeConfig.get_instance` | YAML path / env path | Validated programme sections (trigger, handoff, retry, …) | Ground-Report-W0 | **yes** — `src/configs/programme_config_loader.py`, `src/models/programme_config_models.py` |
| Webhook enqueue | `WebhookIngressService.enqueue_webhook_job` / `POST /webhooks/github` | delivery id, event type, payload, signature validity | job id or duplicate no-op; 401/503 | Ground-Report-W0 | **yes** — live `verify_all` pass |
| Job claim stub | `JobWorkerService.claim_and_process_one` / `worker_main` | pending job rows | claimed then processed (stub) | Ground-Report-W0 | **yes** (code/unit) — **live docker claim deferred (D-W0-V2)** |
| RunStore persistence | repos create/enqueue/claim/mark_* | Pydantic create DTOs | Pydantic models | Ground-Report-W0 | **yes** — migration `36b36d3d4fc9` applied; create includes defaults |
| Handoff read | `HandoffReader.resolve_git_ref` / find / parse | workspace + programme globs | HandoffEnvelope | Ground-Report-W0 | **yes** — unit only |
| Workflow resolve | `WorkflowEngine.load_pin` / `resolve_next` | handoff stage+outcome + pin | ResolvedWorkflowNode | Ground-Report-W0 | **yes** — unit only; no dispatch |
| Forge comments | `ForgeClient.post_comment`; forbid labels/auto-merge | owner/repo/issue + body | comment id | Ground-Report-W0 | **yes** — unit/inspection; App installation token minting still deferred |

**Unconfirmed contracts** (new in W1 — no Ground Report backing yet):

- Programme-token AuthN for status/metrics (ADR-002 zone) — not implemented
- Cursor AgentRunner + LaunchpadHarnessClient (ADR-003 infra slots) — not implemented
- TriggerRouter / PolicyEngine / RunOrchestrator / Notifier / metrics emitter — not implemented
- Live worker claim (D-W0-V2) — treat as **risk** for TASK-W1-03/07 until proven

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered for W1):
  - [x] `architecture.mdc` — API mounts, public_paths, layering
  - [x] `dependency-injection.mdc` — service wiring / lifecycle
  - [x] `infra-services.mdc` — AgentRunner / launchpad / Forge as infra
  - [x] `repository-pattern.mdc` — RunStore only via repos
  - [x] `pydantic-schemas.mdc` — models in `src/models/` only
  - [x] `http-api-conventions.mdc` — status/metrics GET contracts
  - [x] `fail-fast.mdc` — precondition / pin failure behaviour
  - [x] `logging-loguru.mdc` — structured run-event logging
  - [x] `testing-verify-flows.mdc` — verify_wave_start / verify_all
  - [x] `strong-typing.mdc` / `python-imports.mdc` / `python-tooling.mdc` — quality bar
  - skipped: `database-migrations.mdc` (no new DDL planned in W1 unless metrics retention needs it — flag if schema change appears)
- [x] ADRs (keyword-matched):
  - [x] ADR-001 — dual process API+worker; durable RunStore
  - [x] ADR-002 — webhook / programme-token / JWT trust zones
  - [x] ADR-003 — Forge/AgentRunner/launchpad = infra; policy/orchestrator = business; App token prod
  - [x] ADR-004 — programme config authority (trigger label, retry budget)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-001-gateflow.md` (W1 FRs)
- [x] Plan wave section: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-001.md` § Phase W1

---

### Governance alignment

- [x] Slice spec does not contradict listed ADRs
- [x] Plan TASK MDC/ADR notes for W1 reviewed (TASK-W1-01…09)
- [x] Every initiative ADR cited for W1 is **Accepted** under `docs/specification/adr/`

---

### Must update (same change as the code)

- [ ] Product spec — only if W1 implementation changes FR contracts (prefer no drift)
- [ ] `docs/specification/as-built/implementation-status.md` — W1 verification rows
- [ ] `tests/README.md` — feature map for `verify_wave_start`, `verify_status_metrics`, `verify_all` composition
- [ ] Unit — preconditions, concurrent reject, policy dispatch/stop/retry, orchestrator branches, programme-token 401, tool none, agent fail-closed
- [ ] Live — `verify_wave_start` (label→stop); `verify_status_metrics`; keep `verify_all` green
- [ ] ADR — only if superseding Accepted ADR (PE review required)

---

### Must not

- [ ] Contradict Accepted ADRs without superseding first
- [ ] Duplicate full HTTP journeys in pytest when verify scripts own them
- [ ] Assume W0 live worker claim is proven (D-W0-V2) — prove in W1-07 or flag deferral
- [ ] Hardcode workflow node allowlists / node→tool slot maps
- [ ] Write gate-approval labels or enable auto-merge via ForgeClient
- [ ] Put programme token or App secrets in `programme.yaml`
- [ ] Define Pydantic models under `src/api/`
- [ ] Agent-authored Alembic revisions under `postgres_migrations/versions/`

---

### Suggested implementation order (from plan DEP)

1. Branch: `feature/INIT-GATEFLOW-001-w1-operational-control-plane` (or per-TASK branches in plan — prefer one wave branch unless splitting PRs)
2. TASK-W1-01 + TASK-W1-02 (trigger + policy) before TASK-W1-03
3. TASK-W1-03 (orchestrator + notifier) → wire worker stub → real handler
4. TASK-W1-06 (tools none) can parallel early
5. TASK-W1-05 (status/metrics + programme token)
6. TASK-W1-04 (AgentRunner + launchpad) before TASK-W1-08 e2e dispatch
7. TASK-W1-07 runtime docs / compose proof (clears D-W0-V2)
8. TASK-W1-08 live verify scripts
9. TASK-W1-09 runbook + as-built

### Concrete paths to create/edit (plan FILE-W1-*)

| Path | Action |
|------|--------|
| `src/business_services/trigger_router.py` | create |
| `src/business_services/policy_engine.py` | create |
| `src/business_services/run_orchestrator.py` | create |
| `src/business_services/notifier.py` | create |
| `src/business_services/metrics_emitter.py` | create |
| `src/business_services/stage_tool_resolver.py` | create |
| `src/infra_services/cursor_agent_runner.py` | create |
| `src/infra_services/launchpad_client.py` | create |
| `src/api/v1/runs_routes.py`, `metrics_routes.py` | create |
| Programme-token FastAPI dependency under `src/api/` | create |
| `src/app.py` — extend `public_paths` for programme reads | edit |
| `src/di/modules/*`, `dependency_container.py` | edit |
| `src/worker_main.py` / `job_worker_service.py` — replace stub with orchestrator | edit |
| `tests/verify/verify_wave_start.py`, `verify_status_metrics.py` | create |
| `tests/README.md`, as-built, W1 runbook under `docs/` | edit/create |

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format, lint, types, layers | `make check` |
| Unit | policy, retry, concurrent, auth, tool none, fail-closed runner | `make test` |
| Live verify | label→stop + RunStore; programme-token reads | `.venv/bin/python -m tests.verify.verify_wave_start` ; `.venv/bin/python -m tests.verify.verify_status_metrics` (add in W1-08); interim: `.venv/bin/python -m tests.verify.verify_all` |
| Ground check | W1 FRs + boundaries | `/ground-spec` (no Makefile `ground_command`) |

---

### Tracker / PR

- Initiative: **INIT-GATEFLOW-001**
- Issue: **#7** — https://github.com/drivestream-lab/gateflow/issues/7
- EPIC: **#5** — https://github.com/drivestream-lab/gateflow/issues/5
- Spec path: `docs/specification/product/INIT-GATEFLOW-001-gateflow.md`
- Verify command (board): `make check && make test` — extend issue fields when live scripts land
- ADRs in scope: ADR-001, ADR-002, ADR-003, ADR-004

---

### Merge order (if cross-module / cross-service)

N/A — single codebase `drivestream-lab/gateflow`. Internal order: policy → orchestrator → agent runner → live e2e.

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-Checklist-INIT-GATEFLOW-001-W1.md
    digest: sha256:a55381f269b3c3c9dd28d18bcddc621bcd48fdb319b30ae34ae9608ec986124d
  blockers: []
  signals:
    wave: W1
    board_issue: https://github.com/drivestream-lab/gateflow/issues/7
    epic_issue: https://github.com/drivestream-lab/gateflow/issues/5
    prior_wave: W0
    prior_as_built: human_approved
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_wave_start
    verify_command_interim: .venv/bin/python -m tests.verify.verify_all
    ground_command: N/A
    deferred_risk: D-W0-V2
    branch_suggestion: feature/INIT-GATEFLOW-001-w1-operational-control-plane
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
```

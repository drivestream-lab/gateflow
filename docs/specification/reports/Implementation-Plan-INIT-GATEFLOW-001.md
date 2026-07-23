---
goal: INIT-GATEFLOW-001 — implementation plan
initiative: INIT-GATEFLOW-001
status: Planned
date_created: 2026-07-23
source_spec: docs/specification/product/INIT-GATEFLOW-001-gateflow.md
source_spec_digest: sha256:6d0094d21994db5ec7f5903f7f01d5ab03bb2e0619802f293b59aa426dc29f00
feasibility_report: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-001.md
feasibility_digest: sha256:ea81389c06d016b5a4e16d2bf09c677d56d4573878e025859c9987553d6755c9
technical_review: docs/specification/reports/Technical-Review-INIT-GATEFLOW-001.md
technical_review_digest: sha256:30802aba2dda1c177826dd285174f2c98c87c99c2282476857ec2d082ecd34fb
prd_digest: sha256:9fa343f11f9497cd278c18ba4b87391b15cab566f285e88a7f4cda9bf700802d
impact_map: prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-001.md
impact_map_revision: 3
repo_scope_digest: sha256:f81fd7c11c9b438524032898b31b028b376bcf766cb5ef675f0ecb81f326e9a0
approved_meta_pr_head: d62a9bbcf5960c50c4429dd33bb206208dbbf246
branch: chore/INIT-GATEFLOW-001-spec-gateflow
review_deadline: 2026-07-28
deciders: PE — spec-lgtm + Approve on exact head after full package
---

# Implementation plan — INIT-GATEFLOW-001

## Source freshness and command contract

| Item | Value | Status |
|------|-------|--------|
| Spec / digest | `docs/specification/product/INIT-GATEFLOW-001-gateflow.md` / `sha256:6d0094d21994db5ec7f5903f7f01d5ab03bb2e0619802f293b59aa426dc29f00` | CURRENT |
| Feasibility / digest | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-001.md` / `sha256:ea81389c06d016b5a4e16d2bf09c677d56d4573878e025859c9987553d6755c9` | CURRENT |
| Technical review / digest | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-001.md` / `sha256:30802aba2dda1c177826dd285174f2c98c87c99c2282476857ec2d082ecd34fb` | CURRENT |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-001.md` / `3` | CURRENT |
| Repo scope digest | `sha256:f81fd7c11c9b438524032898b31b028b376bcf766cb5ef675f0ecb81f326e9a0` | CURRENT |
| Approved meta PR head | `d62a9bbcf5960c50c4429dd33bb206208dbbf246` | CURRENT |
| `check_command` | `make check` | RESOLVED |
| `test_command` | `make test` | RESOLVED |
| `verify_command` | Per-wave: `.venv/bin/python -m tests.verify.<script>` after scripts land; until then N/A for CI — live scripts planned in TASK rows | RESOLVED |
| `ground_command` | N/A — no Makefile ground target; post-merge use `/ground-spec` skill per workflow | N/A |

> Pin ref `v0.5.0-rc.2` is the W1 **target** from `.harness-pin.yaml` / product acceptance — engines load pinned YAML artifacts, not a hardcoded version string in source (see TDD).

## 0. Technical design reference

| Item | Value |
|------|-------|
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-001.md` |
| PE sign-off | [x] complete — 2026-07-23 (@nikd10x) |
| Resolved ADRs | `docs/specification/adr/adr-001-runtime-and-durable-store.md` (Accepted); `docs/specification/adr/adr-002-edge-trust-model.md` (Accepted); `docs/specification/adr/adr-003-slot-layer-ownership.md` (Accepted); `docs/specification/adr/adr-004-programme-config-authority.md` (Accepted) |
| Outstanding PM questions | none — all resolved |
| Outstanding domain questions | none — all resolved |

> Do not start W0 implementation until PE sign-off is marked complete above.

---

## 1. Requirements (REQ)

| ID | Source (spec) | Summary | Feasibility ref |
|----|---------------|---------|-----------------|
| REQ-W0-CFG | FR-18 | Programme config load (in-repo file + fail-fast) | F-06 |
| REQ-W0-STORE | FR-5 | Postgres RunStore + jobs schema/repos | F-01, F-03 |
| REQ-W0-HOOK | FR-1 | Webhook ingress signature + idempotency + enqueue | F-04 |
| REQ-W0-WORKER | FR-17 (partial) | Worker entry + job claim loop (no AgentRunner yet) | F-01 |
| REQ-W0-HAND | FR-6 | HandoffReader (ref + globs) | F-05 |
| REQ-W0-WF | FR-7 (resolve only) | WorkflowEngine load pin + resolve next node (no dispatch) | F-05 |
| REQ-W0-FORGE | FR-12 (comments) | ForgeClient comments + forbid gate labels/auto-merge | F-05, Q-1 |
| REQ-W1-TRIG | FR-3, FR-4 | TriggerRouter + wave-run preconditions | — |
| REQ-W1-POL | FR-7, FR-8, FR-10 | PolicyEngine dispatch/stop/retry | F-08 |
| REQ-W1-RUN | FR-2, FR-9, FR-11, FR-16, FR-17 | RunOrchestrator + Cursor AgentRunner + launchpad sync + Notifier | F-10 |
| REQ-W1-API | FR-13, FR-15 | Status + metrics APIs (programme token) | F-02, Q-3 |
| REQ-W1-TOOL | FR-14 | ToolProvider none + StageToolResolver | — |
| REQ-W1-DOCS | FR-19 | W1 runbook + as-built/tests README | — |

---

## 2. Implementation phases

### Phase W0 — Control plane skeleton

**GOAL-W0:** API can accept signed webhooks, persist idempotency + jobs, worker claims jobs, HandoffReader + WorkflowEngine resolve next node without AgentRunner dispatch, ForgeClient can post comments, programme config loads at startup.

| Task | Description | Codebase | Spec path | Done when | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|----------|-----------|-----------|----------------|-----------|-----------|--------|
| TASK-W0-01 | Programme config model + `config/programme.yaml` (+ example); fail-fast load in API/worker startup | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-001-gateflow.md` | Missing/invalid config fails process start; required keys validated | `make check && make test` | pydantic-schemas; fail-fast; settings not in injector | ADR-004 | `feature/INIT-GATEFLOW-001-w0-programme-config` |
| TASK-W0-02 | ORM schemas + repos for webhook deliveries, runs, stages, events, jobs; human Alembic revision applied | drivestream-lab/gateflow | same | Migrations apply; repos round-trip Pydantic DTOs | `make check && make test` | repository-pattern; database-migrations (human versions) | ADR-001 | `feature/INIT-GATEFLOW-001-w0-runstore` |
| TASK-W0-03 | `POST /webhooks/github`: signature verify, idempotency, enqueue job, 202/401/503; extend `public_paths` | drivestream-lab/gateflow | same | Unit: bad sig 401; dup delivery no second job; happy path enqueues | `make check && make test` | architecture public_paths; models in src/models | ADR-002 | `feature/INIT-GATEFLOW-001-w0-webhook` |
| TASK-W0-04 | `src/worker_main.py` + job claim (`SKIP LOCKED`); stub handler logs + marks job processed without AgentRunner | drivestream-lab/gateflow | same | Worker claims enqueued job in docker-compose | `make check && make test` | DI worker_main pattern | ADR-001 | `feature/INIT-GATEFLOW-001-w0-worker` |
| TASK-W0-05 | HandoffReader + WorkflowEngine (resolve only; load pin artifacts; no dispatch allowlists) | drivestream-lab/gateflow | same | Unit fixtures resolve next node from handoff+workflow; pin missing → explicit error | `make check && make test` | business_services; no hardcoded nodes | ADR-003 | `feature/INIT-GATEFLOW-001-w0-handoff-workflow` |
| TASK-W0-06 | ForgeClient infra: comments + audit; forbid gate-approval labels & auto-merge; App token / non-prod PAT | drivestream-lab/gateflow | same | Unit mocks assert forbidden ops never called | `make check && make test` | infra-services | ADR-003 | `feature/INIT-GATEFLOW-001-w0-forge` |
| TASK-W0-07 | Unit + first live verify scripts for webhook signature/idempotency; update tests README | drivestream-lab/gateflow | same | `tests.verify.verify_webhook` documented; health still green | `make check && make test` ; `.venv/bin/python -m tests.verify.verify_webhook` (needs local stack) | testing-verify-flows | ADR-002 | `feature/INIT-GATEFLOW-001-w0-verify` |
| TASK-W0-08 | As-built matrix: mark W0 capabilities partial/complete | drivestream-lab/gateflow | same | as-built rows updated for W0 | docs inspection | SDD as-built | — | same PR as last W0 code |

#### Files (W0)

| ID | Path | Action |
|----|------|--------|
| FILE-W0-01 | `config/programme.yaml` (+ `.example` if needed) | create |
| FILE-W0-02 | `src/models/programme_config_models.py` (name flexible) | create |
| FILE-W0-03 | `src/database/postgres/schema/run_*.py`, `job_*.py`, `webhook_*.py` | create |
| FILE-W0-04 | `src/database/postgres/repository/*` | create |
| FILE-W0-05 | `postgres_migrations/versions/*` | human create |
| FILE-W0-06 | `src/api/webhooks/*` or equiv | create |
| FILE-W0-07 | `src/app.py` public_paths | edit |
| FILE-W0-08 | `src/worker_main.py` | create |
| FILE-W0-09 | `src/business_services/handoff_reader.py`, `workflow_engine.py` | create |
| FILE-W0-10 | `src/infra_services/forge_client.py` | create |
| FILE-W0-11 | `src/di/modules/*`, `dependency_container.py` | edit |
| FILE-W0-12 | `tests/unit/**`, `tests/verify/verify_webhook.py` | create |
| FILE-W0-13 | `tests/README.md`, `docs/specification/as-built/implementation-status.md` | edit |

#### Tests (W0)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W0-U | unit | `make test` | config, signature, idempotency, resolve, forge forbid |
| TEST-W0-V | live verify | `.venv/bin/python -m tests.verify.verify_webhook` | signed webhook → job row |

---

### Phase W1 — Operational control plane

**GOAL-W1:** Label trigger → preconditions → PolicyEngine → (optional) AgentRunner dispatch → contract stop; status/metrics APIs; Notifier comments; retry budget; Docker API+worker proven; W1 runbook.

| Task | Description | Codebase | Spec path | Done when | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|----------|-----------|-----------|----------------|-----------|-----------|--------|
| TASK-W1-01 | TriggerRouter + wave-run precondition checklist; concurrent active-run reject | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-001-gateflow.md` | Unit: each failed precondition blocks; concurrent reject | `make check && make test` | fail-fast; business orchestration | ADR-002, ADR-004 | `feature/INIT-GATEFLOW-001-w1-trigger-policy` |
| TASK-W1-02 | PolicyEngine: dispatch only skill+orchestrated; stops; retry budget; never silent on pin failure | drivestream-lab/gateflow | same | Contract fixtures + gateflow dispatch fixtures pass | `make check && make test` | no hardcoded allowlists | ADR-003 | `feature/INIT-GATEFLOW-001-w1-trigger-policy` |
| TASK-W1-03 | RunOrchestrator wires job → policy → (dispatch|stop); Notifier → ForgeClient run-event comments | drivestream-lab/gateflow | same | Stop/start comments schema fields present in unit/mocks | `make check && make test` | logging structured kwargs | ADR-001, ADR-003 | `feature/INIT-GATEFLOW-001-w1-orchestrator` |
| TASK-W1-04 | Cursor AgentRunner + LaunchpadHarnessClient sync before run; fail-closed on runner failure | drivestream-lab/gateflow | same | Mock timeout → run `failed`, no advance; sync invoked before run | `make check && make test` | infra lifecycle | ADR-003; F-10 default | `feature/INIT-GATEFLOW-001-w1-agent-runner` |
| TASK-W1-05 | Programme-token status + metrics routes (`GET /api/v1/runs/{id}`, `GET /api/v1/metrics/runs`); public_paths | drivestream-lab/gateflow | same | 401 without token; 200 shape matches TDD | `make check && make test` | http-api-conventions; models in src/models | ADR-002 | `feature/INIT-GATEFLOW-001-w1-status-metrics` |
| TASK-W1-06 | StageToolResolver + None ToolProvider | drivestream-lab/gateflow | same | Empty tool context; no node→slot hardcode | `make check && make test` | — | ADR-003 | `feature/INIT-GATEFLOW-001-w1-tools` |
| TASK-W1-07 | Docker compose / runtime docs: API + worker; health 200 while worker processes | drivestream-lab/gateflow | same | Documented run; health OK | inspection + live | — | ADR-001 | `feature/INIT-GATEFLOW-001-w1-runtime-docs` |
| TASK-W1-08 | Live verify e2e smoke (label→stop) + metrics/status verify scripts; tests README feature map | drivestream-lab/gateflow | same | verify scripts exit 0 on dogfood stack | `.venv/bin/python -m tests.verify.verify_wave_smoke` (when added) | testing-verify-flows | — | `feature/INIT-GATEFLOW-001-w1-verify` |
| TASK-W1-09 | W1 runbook “Orchestrate a new initiative repo”; as-built W1 complete | drivestream-lab/gateflow | same | Runbook in docs; as-built matrix updated | docs inspection | SDD | — | same PR as docs |

#### Files (W1)

| ID | Path | Action |
|----|------|--------|
| FILE-W1-01 | `src/business_services/trigger_router.py`, `policy_engine.py`, `run_orchestrator.py`, `notifier.py`, `metrics_emitter.py`, `stage_tool_resolver.py` | create |
| FILE-W1-02 | `src/infra_services/cursor_agent_runner.py`, `launchpad_client.py` | create |
| FILE-W1-03 | `src/api/v1/runs_routes.py`, `metrics_routes.py` | create |
| FILE-W1-04 | `src/api/.../programme_token.py` (dependency) | create |
| FILE-W1-05 | `docker/` / compose / README run docs | edit |
| FILE-W1-06 | `docs/` W1 runbook | create |
| FILE-W1-07 | `tests/unit/**`, `tests/verify/verify_wave_smoke.py`, `verify_status_metrics.py` | create |
| FILE-W1-08 | `tests/README.md`, as-built | edit |

#### Tests (W1)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W1-U | unit | `make test` | policy, retry, concurrent, auth, tool none |
| TEST-W1-V | live verify | `.venv/bin/python -m tests.verify.verify_wave_smoke` | label → stop comment + RunStore |
| TEST-W1-V2 | live verify | `.venv/bin/python -m tests.verify.verify_status_metrics` | programme-token reads |

---

## 3. Dependencies (DEP)

| ID | Dependency | Blocks |
|----|------------|--------|
| DEP-01 | W0-01 config before W0-03/04/05 | webhook/worker need config |
| DEP-02 | W0-02 store before W0-03/04 | enqueue/claim need tables |
| DEP-03 | W0 complete before W1 | policy/orchestrator need skeleton |
| DEP-04 | W1-01/02 before W1-03 | orchestrator needs policy |
| DEP-05 | W1-04 before W1-08 e2e dispatch | live agent path |
| DEP-06 | Human Alembic for W0-02 | live verify DB |
| DEP-07 | GitHub App + secrets in env | live verify forge/webhook |
| DEP-08 | Pin artifacts available via harness (`.harness-pin.yaml` / sync) | WorkflowEngine |

---

## 4. Risks (RISK)

| ID | Risk | Mitigation |
|----|------|------------|
| RISK-01 | Cursor SDK container friction (F-10) | Fail-closed; spike early in W1-04; mock in CI |
| RISK-02 | public_paths drift vs new mounts | Checklist in PR; unit assert allowlist covers webhook + programme reads |
| RISK-03 | Human migration lag | Describe DDL in PR; owner runs create/apply scripts |
| RISK-04 | Accidental hardcoding of pin version or node lists | Code review + tests load YAML from pin path; ADR-003 |
| RISK-05 | ForgeClient credential misconfig | ADR-003: App prod, PAT non-prod only; fail-fast settings |
| RISK-06 | Q-2 no dedicated Postgres alert | Document 503 + GitHub retry in runbook (deferred default) |

---

## 5. Out of scope

- gateflow-ops BFF/UI
- Formal cancel API; concurrent queue/supersede
- Commit status checks; Slack/Teams
- Multi-runner / LiteLLM / real ToolProviders
- Changes to prayog-skills or launchpad product code (consume only)
- Phase B dogfood as a plan wave (post–W1 exit product phase)

---

## 6. As-built and docs tasks

> Update these in the **same PR** as the code they describe.

| Task | File | Action |
|------|------|--------|
| Update implementation-status.md | `docs/specification/as-built/implementation-status.md` | mark W0/W1 in_progress → complete |
| Update tests/README.md | `tests/README.md` | add verify module commands + feature map |
| W1 runbook | `docs/` (path chosen in W1-09) | create orchestrate-new-repo runbook |

> **ADR lifecycle** — Accepted ADRs already on branch; do not add promotion tasks.

---

## 7. Plan check summary

| Check | Status |
|-------|--------|
| P1 Every wave has REQ | PASS |
| P2 Every REQ has TASK | PASS |
| P3 FILE paths | PASS |
| P4 done when | PASS |
| P5 test/verify commands | PASS |
| P6 scope ≤ INIT | PASS |
| P7 feasibility blockers | PASS — ADRs Accepted; Q-2/F-10 deferred with defaults |
| P8 wave order | PASS |
| P9 as-built/docs tasks | PASS |
| P10 self-contained + commands | PASS |
| P11 MDC notes | PASS |
| P12 ADR Accepted cited | PASS |
| P13 TDD Accepted + PE sign-off | PASS |
| P14 WorkManifest §9 | PASS |

---

## 8. PR instructions

> Commit this plan to the **Draft spec PR** branch alongside spec, feasibility,
> and TDD. Label remains **`spec-pending`** until PE completes §10.

```
Branch:   chore/INIT-GATEFLOW-001-spec-gateflow  (Draft PR)
PR title: "[INIT-GATEFLOW-001] Spec — gateflow"
PR:       https://github.com/drivestream-lab/gateflow/pull/4
Meta PRD: https://github.com/drivestream-lab/prayog-meta/pull/9

Required reviewers: @drivestream-lab/prayog-pe-team
Review deadline: 2026-07-28

PE checklist (before spec-lgtm):
  [ ] Spec + feasibility + TDD + Accepted ADRs + this plan on current head
  [ ] §0 PE sign-off on TDD marked complete
  [ ] Wave order and dependencies make sense
  [ ] Done-when criteria are observable and testable
  [ ] WorkManifest YAML (§9) correct — wave IDs W0, W1
  [ ] P1–P14 checks all pass

After spec-lgtm + Approve + merge — **/board-seed** from §9 (post-merge only)
```

---

## 10. Gate 2 unlock (PE — after plan on head)

Present this section in chat when the plan is committed. **No GitHub side
effects** until PE completes the unlock.

| Item | Value |
|------|-------|
| Verdict | GATE OPEN REQUEST |
| Spec PR | https://github.com/drivestream-lab/gateflow/pull/4 |
| Spec PR head SHA | `{FILL_AFTER_COMMIT}` |
| Gate label (current) | `spec-pending` |
| Gate label (target) | `spec-lgtm` |
| Blocking items | none |

Provision labels when missing:

```bash
launchpad apply-gates --repo gateflow --apply
```

PE actions (all on **exact current head**):

1. Remove `spec-pending`, `spec-blocked`, `spec-revised`, `spec-stale`; add **`spec-lgtm`**
2. Submit GitHub **Approve** with attestation body (below)
3. Mark Draft PR **Ready for review**
4. Authorize merge; then **`/board-seed`** from §9

### Approve attestation body

```text
Spec package approved
initiative: INIT-GATEFLOW-001
spec_pr_head_sha: {FILL_AFTER_COMMIT}
meta_pr_head_sha: d62a9bbcf5960c50c4429dd33bb206208dbbf246
impact_map_revision: 3
prd_digest: sha256:9fa343f11f9497cd278c18ba4b87391b15cab566f285e88a7f4cda9bf700802d
scope_digest: sha256:f81fd7c11c9b438524032898b31b028b376bcf766cb5ef675f0ecb81f326e9a0
plan_digest: sha256:{FILL_PLAN_DIGEST}
artifacts:
  - docs/specification/product/INIT-GATEFLOW-001-gateflow.md
  - docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-001.md
  - docs/specification/reports/Technical-Review-INIT-GATEFLOW-001.md
  - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-001.md
```

| PE action | Remove | Add |
|-----------|--------|-----|
| Pending/new revision | `spec-lgtm`, `spec-blocked` | `spec-pending` |
| Request changes/hold | `spec-pending`, `spec-lgtm` | `spec-blocked` |
| Approve full package | `spec-pending`, `spec-blocked`, `spec-revised`, `spec-stale` | `spec-lgtm` |

---

## 9. WorkManifest seed

> **Primary:** after merge, `/board-seed` creates one GitHub Issue per wave.
> `target.project` from governance: **drivestream-lab Board**.

```yaml
# Generated by /spec-implementation-plan — 2026-07-23
# LOCAL — do not commit to prayog-skills upstream
apiVersion: launchpad/v1
kind: WorkManifest

initiative: INIT-GATEFLOW-001
# Branch naming: feature/INIT-GATEFLOW-001-w{N}-{slug}

metadata:
  title: INIT-GATEFLOW-001 — Gateflow W1 delivery control plane
  summary: |
    Build gateflow control plane: W0 skeleton (webhooks, RunStore, worker,
    handoff/workflow resolve, ForgeClient, programme config) then W1 operational
    loop (policy, AgentRunner, status/metrics, verify, runbook).
  playbook:
    - docs/specification/product/INIT-GATEFLOW-001-gateflow.md
    - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-001.md

target:
  org: drivestream-lab
  project: drivestream-lab Board

defaults:
  initiative: INIT-GATEFLOW-001
  parent: EPIC
  status: Backlog
  labels:
    - INIT-GATEFLOW-001

epic:
  id: EPIC
  repo: drivestream-lab/gateflow
  title: "[feature] INIT-GATEFLOW-001 — Gateflow delivery control plane"
  codebase: drivestream-lab/gateflow
  spec_path: docs/specification/product/INIT-GATEFLOW-001-gateflow.md
  verify_command: make check && make test
  body: |
    ## Objective

    Deliver Gateflow W1 control plane on drivestream-lab/gateflow only:
    webhook→job→policy→agent dispatch→contract stop, with status/metrics APIs.

    ## Waves

    | Wave | Goal |
    |------|------|
    | W0 | Control plane skeleton |
    | W1 | Operational control plane |

    ## References

    - Spec: docs/specification/product/INIT-GATEFLOW-001-gateflow.md
    - Implementation plan: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-001.md
    - Technical review: docs/specification/reports/Technical-Review-INIT-GATEFLOW-001.md

work:
  - id: W0
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-001 W0] Control plane skeleton"
    depends_on: []
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-001-gateflow.md
    verify_command: make check && make test
    status: Backlog
    body: |
      ## Wave goal

      API accepts signed webhooks and enqueues jobs; worker claims jobs;
      HandoffReader + WorkflowEngine resolve without AgentRunner dispatch;
      ForgeClient comments; programme config loads fail-fast.

      ## Tasks (from plan §2)

      - TASK-W0-01: Programme config load
      - TASK-W0-02: RunStore + jobs + human migration
      - TASK-W0-03: Webhook ingress
      - TASK-W0-04: Worker claim loop (stub handler)
      - TASK-W0-05: HandoffReader + WorkflowEngine resolve
      - TASK-W0-06: ForgeClient
      - TASK-W0-07: Unit + verify_webhook
      - TASK-W0-08: As-built W0 update

      ## Done when

      - [ ] All W0 tasks complete per plan

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-001-gateflow.md

  - id: W1
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-001 W1] Operational control plane"
    depends_on:
      - W0
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-001-gateflow.md
    verify_command: make check && make test
    status: Backlog
    body: |
      ## Wave goal

      Label trigger → preconditions → PolicyEngine → AgentRunner (when
      orchestrated) → contract stop; status/metrics APIs; Notifier; Docker
      API+worker; W1 runbook.

      ## Tasks (from plan §2)

      - TASK-W1-01: TriggerRouter + preconditions + concurrent reject
      - TASK-W1-02: PolicyEngine dispatch/stop/retry
      - TASK-W1-03: RunOrchestrator + Notifier
      - TASK-W1-04: Cursor AgentRunner + launchpad sync
      - TASK-W1-05: Status + metrics APIs
      - TASK-W1-06: ToolProvider none
      - TASK-W1-07: Runtime docs API+worker
      - TASK-W1-08: Live verify wave smoke + status/metrics
      - TASK-W1-09: W1 runbook + as-built

      ## Done when

      - [ ] All W1 tasks complete per plan

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-001-gateflow.md
```

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-implementation-plan
  outcome: pass
  artifact:
    path: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-001.md
    digest: sha256:4169cf0d9a2a478876c9166927daef68da76df4fe58b4d644d0eee88becd4be5
  blockers: []
  signals:
    gate2_unlock: requested
    gate2_label: spec-pending
    draft_spec_pr: https://github.com/drivestream-lab/gateflow/pull/4
    source_freshness: CURRENT
    map_revision: 3
    waves: [W0, W1]
    ready_for_board_seed: false
  next_candidates:
    - gate-2
  human_checkpoint: true
  external_action: true
```

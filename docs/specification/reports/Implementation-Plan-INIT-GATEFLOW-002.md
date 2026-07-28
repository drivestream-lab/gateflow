---
goal: INIT-GATEFLOW-002 — implementation plan
initiative: INIT-GATEFLOW-002
status: Planned
date_created: 2026-07-24
source_spec: docs/specification/product/INIT-GATEFLOW-002-gateflow.md
source_spec_digest: sha256:9d437c0ecd3cacfc0ec12ba8c9e7fa05a4ec42c543f1284fff670dc134aa3867
feasibility_report: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-002.md
feasibility_digest: sha256:33d5b40bec323cca9efcf84fa7372e50cd41bfda26036a6534935f414e7c0bac
technical_review: docs/specification/reports/Technical-Review-INIT-GATEFLOW-002.md
technical_review_digest: sha256:12106d014404b229c7afb71a3f33f6ed8e79e6ffc6dd802043fe7352e8604a89
prd_digest: sha256:2f339bae00df71e21b45e51c7551f1fb06490dd1805b96e08daca741c140332c
impact_map: prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-002.md
impact_map_revision: 1
repo_scope_digest: sha256:3662f15e366994defaf08fa43b0a5a568eb152f6a74bcff73a0b0453dba0c901
approved_meta_pr_head: 8f291367134a686baaf650835a89dba92e887051
branch: chore/INIT-GATEFLOW-002-spec-gateflow
review_deadline: 2026-07-29
deciders: PE — spec-lgtm + Approve on exact head after full package
---

# Implementation plan — INIT-GATEFLOW-002

## Source freshness and command contract

| Item | Value | Status |
|------|-------|--------|
| Spec / digest | `docs/specification/product/INIT-GATEFLOW-002-gateflow.md` / `sha256:9d437c0ecd3cacfc0ec12ba8c9e7fa05a4ec42c543f1284fff670dc134aa3867` | CURRENT |
| Feasibility / digest | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-002.md` / `sha256:33d5b40bec323cca9efcf84fa7372e50cd41bfda26036a6534935f414e7c0bac` | CURRENT |
| Technical review / digest | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-002.md` / `sha256:12106d014404b229c7afb71a3f33f6ed8e79e6ffc6dd802043fe7352e8604a89` | CURRENT |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-002.md` / `1` | CURRENT |
| Repo scope digest | `sha256:3662f15e366994defaf08fa43b0a5a568eb152f6a74bcff73a0b0453dba0c901` | CURRENT |
| Approved meta PR head | `8f291367134a686baaf650835a89dba92e887051` | CURRENT |
| `check_command` | `make check` | RESOLVED |
| `test_command` | `make test` | RESOLVED |
| `verify_command` | Per-wave: `.venv/bin/python -m tests.verify.<script>` after scripts land; aggregator `.venv/bin/python -m tests.verify.verify_all` | RESOLVED |
| `ground_command` | N/A — no Makefile ground target; post-merge use `/ground-spec` skill per workflow | N/A |

> Pin ref `v0.5.0-rc.2` remains the consumer target (unchanged from INIT-001).

## 0. Technical design reference

| Item | Value |
|------|-------|
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-002.md` |
| PE sign-off | [x] complete — 2026-07-24 (@nikd10x via Cursor chat on https://github.com/drivestream-lab/gateflow/pull/10) |
| Resolved ADRs | `docs/specification/adr/adr-001-runtime-and-durable-store.md` (Accepted); `docs/specification/adr/adr-002-edge-trust-model.md` (Accepted — programme-token row superseded by ADR-005); `docs/specification/adr/adr-003-slot-layer-ownership.md` (Accepted); `docs/specification/adr/adr-004-programme-config-authority.md` (Accepted); `docs/specification/adr/adr-005-programme-token-control-plane-mutations.md` (Accepted, `sha256:88eab40019a40c190a97c224ec96b7adbe85dd33573116f42bb35b3f102f4ad0`); `docs/specification/adr/adr-006-adapter-registry-fail-closed.md` (Accepted, `sha256:fff0c5158b9f6297eaeab1fa69318a553301ba35be431ac54a8dd42620eca20a`) |
| Outstanding PM questions | none |
| Outstanding domain questions | none |
| Deferred PE defaults (non-blocking) | Q-4 App/Projects permissions — block **W2 exit** until confirmed; Q-5 PE alert — `notify_pending` + status API; V-3 Cursor SDK — stub/`mock-*`/`GATEFLOW_AGENT_STUB` OK for W1 exit |

> Do not start W0 implementation until PE sign-off is marked complete above.

---

## 1. Requirements (REQ)

| ID | Source (spec) | Summary | Feasibility ref |
|----|---------------|---------|-----------------|
| REQ-W0-AUTH | FR-15, ADR-005 | Programme-token writes on wave-start; extend `public_paths` | C-1 |
| REQ-W0-START | FR-15 | `POST /api/v1/waves/start` dual identity + preconditions + enqueue | S-1, G-1 |
| REQ-W0-LABEL | FR-15 | Disable label-based wave start for 002 programmes | S-1 |
| REQ-W0-REG | FR-17, FR-18, FR-23, ADR-006 | Adapter registry + fail-closed SlotValidator before enqueue | S-6 |
| REQ-W0-RUNAPI | FR-20 | Run list/filter + detail timeline | S-4 |
| REQ-W0-CFG | FR-16 (partial), FR-23 | Programme config: `notifier.*`; structured override coerce | ADR-004 |
| REQ-W0-STORE | FR-15 / FR-20 | Schema/repo fields for `wave_id` / richer identity as needed (human Alembic) | G-1 |
| REQ-W0-VERIFY | FR-15, FR-20 | Unit + live verify API wave-start; replace label primary smoke | V-1, S-5 |
| REQ-W1-MODEL | FR-16 | Per-node runner + model overrides; persist four fields on stages | S-4 / FR-16 |
| REQ-W1-PR | FR-19 | PR create/update at run start via ForgeClient; comments on that PR | S-3 |
| REQ-W1-MET | FR-21, FR-22 | Metrics by node/runner/model_id; api_trigger + multi-stage events | S-4 |
| REQ-W1-CURSOR | FR-17, V-3 | Cursor path happy path (stub allowed for W1 exit per TDD) | V-3 |
| REQ-W1-VERIFY | FR-19, FR-21 | Live verify PR-thread + metrics dims | V-1 |
| REQ-W2-BOARD | FR-24 | Board APIs (status, link, create, list) + ForgeClient board ops | S-3, G-3 |
| REQ-W2-GH | FR-25, FR-26a | Production `gh`-free path verification | — |
| REQ-W2-DOCS | FR-26b | Laptop `gh` vs deploy ForgeClient runbook note | — |

---

## 2. Implementation phases

### Phase W0 — API trigger skeleton + run list/detail + stubs

**GOAL-W0:** Authenticated wave-start is the only wave start path; label trigger cannot start waves; adapter registry + fail-closed validation block stub selection before enqueue; run list/detail APIs work under programme token.

| Task | Description | Codebase | Spec path | Done when | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|----------|-----------|-----------|----------------|-----------|-----------|--------|
| TASK-W0-01 | Programme config: `notifier.default`; coerce `model.overrides` str→object; document label non-start for 002 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-002-gateflow.md` | Config loads; legacy override strings coerce; missing notifier fails fast | `make check && make test` | pydantic-schemas; fail-fast; settings not in injector | ADR-004 | `feature/INIT-GATEFLOW-002-w0-config-registry` |
| TASK-W0-02 | Adapter registry + SlotValidator (business); register cursor + opencode/claude stubs; github_comment + slack/teams stubs | drivestream-lab/gateflow | same | Unused stubs OK; required stub → structured failure before enqueue | `make check && make test` | infra vs business; DI singleton registry | ADR-006, ADR-003 | same |
| TASK-W0-03 | Human Alembic + schema/repo: `wave_id` (and any identity columns needed); concurrent lookup by wave identity | drivestream-lab/gateflow | same | Migration applies; active-run query uses wave identity | `make check && make test` | repository-pattern; human migrations only | ADR-001 | `feature/INIT-GATEFLOW-002-w0-wave-start` |
| TASK-W0-04 | WaveStartService + `POST /api/v1/waves/start` models/routes; programme-token auth; dual identity agree; preconditions; SlotValidator; enqueue; extend `public_paths` | drivestream-lab/gateflow | same | 2xx+`run_id` on success; 400/401/409/422/503 per TDD §3.1/§6 | `make check && make test` | http-api-conventions body models in `src/models/`; architecture public_paths | ADR-005, ADR-001 | same |
| TASK-W0-05 | Disable label wave-start in TriggerRouter for 002; webhook may still ack non-start events | drivestream-lab/gateflow | same | Labelled webhook does **not** create a new wave run | `make check && make test` | fail-fast explicit reject | ADR-005 (token path); product FR-15 | same |
| TASK-W0-06 | `GET /api/v1/runs` list/filter + enrich `GET /api/v1/runs/{id}` with stage/event timeline | drivestream-lab/gateflow | same | Filters + timeline reconstruct from RunStore; auth matrix | `make check && make test` | pydantic response models | ADR-005 | `feature/INIT-GATEFLOW-002-w0-run-apis` |
| TASK-W0-07 | Unit + live verify: wave-start (replace label as primary in `verify_wave_start` or add `verify_wave_start`); extend status/metrics verify for list/detail; update `tests/README.md` | drivestream-lab/gateflow | same | Documented verify scripts green on local stack | `make check && make test` ; `.venv/bin/python -m tests.verify.verify_wave_start` (or updated smoke) | testing-verify-flows | — | `feature/INIT-GATEFLOW-002-w0-verify` |
| TASK-W0-08 | As-built: mark W0 capabilities in_progress→complete for FR-15/17/18/20/23 skeleton | drivestream-lab/gateflow | same | as-built rows updated | docs inspection | SDD as-built | — | same PR as last W0 code |

#### Files (W0)

| ID | Path | Action |
|----|------|--------|
| FILE-W0-01 | `config/programme.yaml`, `config/programme.yaml.example` | edit |
| FILE-W0-02 | `src/models/programme_config_models.py`, wave/board/run list models | edit/create |
| FILE-W0-03 | `src/business_services/slot_validator.py`, adapter registry module | create |
| FILE-W0-04 | stub runner/notifier infra modules | create |
| FILE-W0-05 | `src/business_services/wave_start_service.py` | create |
| FILE-W0-06 | `src/api/v1/waves_routes.py`, `src/api/v1/__init__.py`, `src/app.py` | create/edit |
| FILE-W0-07 | `src/business_services/trigger_router.py` | edit |
| FILE-W0-08 | `src/api/v1/runs_routes.py`, metrics/run models, repos | edit |
| FILE-W0-09 | `src/database/postgres/schema/*`, `repository/*` | edit |
| FILE-W0-10 | `postgres_migrations/versions/*` | **human** create |
| FILE-W0-11 | `src/di/modules/*`, `dependency_container.py` | edit |
| FILE-W0-12 | `tests/unit/**`, `tests/verify/verify_wave_start.py` (or smoke update) | create/edit |
| FILE-W0-13 | `tests/README.md`, `docs/specification/as-built/implementation-status.md` | edit |

#### Tests (W0)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W0-U | unit | `make test` | identity, auth, stubs, label reject, list/detail |
| TEST-W0-V | live verify | `.venv/bin/python -m tests.verify.verify_wave_start` (+ status/metrics) | API start → run row; label does not start |

---

### Phase W1 — Per-node model, PR-at-start, metrics, Cursor path

**GOAL-W1:** Orchestrated nodes resolve per-node runner/model; every run opens/updates a PR at start with stage comments; metrics expose runner/model dimensions; Cursor happy path works (stub OK for exit).

| Task | Description | Codebase | Spec path | Done when | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|----------|-----------|-----------|----------------|-----------|-----------|--------|
| TASK-W1-01 | Per-node override resolution in orchestrator; persist `runner`, `model_profile`, `model_id`, `model_provider` on stages | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-002-gateflow.md` | ≥2 nodes different profiles in fixtures; invalid override blocked at start | `make check && make test` | no hardcoded node allowlists | ADR-004, ADR-006 | `feature/INIT-GATEFLOW-002-w1-model-pr-metrics` |
| TASK-W1-02 | Programme `pr.*` templates; ForgeClient `create_or_update_pull_request`; orchestrator opens/updates PR at run start; Notifier comments on that PR; `notify_pending` on PR failure | drivestream-lab/gateflow | same | PR exists before first orchestrated stage completes; same naming success/failure | `make check && make test` | infra ForgeClient; no auto-merge/gate labels | ADR-003 | same |
| TASK-W1-03 | MetricsEmitter: `api_trigger` + stage/stop events; aggregates `by_runner`, `by_model_id` on `GET /metrics/runs` | drivestream-lab/gateflow | same | Dimensions present when data exists | `make check && make test` | structured logging fields | — | same |
| TASK-W1-04 | Cursor AgentRunner path for W1 exit (stub/`GATEFLOW_AGENT_STUB`/`mock-*` allowed); launchpad sync remains pre-dispatch | drivestream-lab/gateflow | same | Documented happy path passes unit; as-built notes stub vs SDK | `make check && make test` | infra runner | ADR-003; V-3 deferred | same |
| TASK-W1-05 | Live verify PR-thread + metrics dims; update verify_all / README | drivestream-lab/gateflow | same | Verify scripts assert PR + metric keys | `make check && make test` ; live verify scripts | testing-verify-flows | — | `feature/INIT-GATEFLOW-002-w1-verify` |
| TASK-W1-06 | As-built W1 complete for FR-16/19/21/22 | drivestream-lab/gateflow | same | as-built rows updated | docs inspection | SDD | — | same PR as last W1 code |

#### Files (W1)

| ID | Path | Action |
|----|------|--------|
| FILE-W1-01 | `src/business_services/run_orchestrator.py` | edit |
| FILE-W1-02 | `src/infra_services/forge_client.py` | edit |
| FILE-W1-03 | `src/business_services/notifier.py` | edit |
| FILE-W1-04 | `src/business_services/metrics_emitter.py`, `src/api/v1/metrics_routes.py`, models | edit |
| FILE-W1-05 | `src/infra_services/cursor_agent_runner.py` | edit (as needed) |
| FILE-W1-06 | `config/programme.yaml` (`pr.*`) | edit |
| FILE-W1-07 | `tests/unit/**`, `tests/verify/**` | edit/create |
| FILE-W1-08 | as-built, `tests/README.md` | edit |

#### Tests (W1)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W1-U | unit | `make test` | overrides, PR call order, metrics dims, stub cursor |
| TEST-W1-V | live verify | `.venv/bin/python -m tests.verify.verify_pr_thread` (or extended smoke) | PR + comments + metrics |

---

### Phase W2 — Board APIs + deploy `gh`-free

**GOAL-W2:** Board dumb primitives via ForgeClient; worker never calls board APIs; production path cannot use `gh`; laptop policy documented (FR-26b).

| Task | Description | Codebase | Spec path | Done when | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|----------|-----------|-----------|----------------|-----------|-----------|--------|
| TASK-W2-01 | BoardService + `/api/v1/board/*` routes per TDD §3.3; ForgeClient board methods; EPIC/Feature idempotency; partial-failure body; `Idempotency-Key`; extend `public_paths` | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-002-gateflow.md` | Auth + create/list/status/link behaviors; bad payload 400 | `make check && make test` | http-api-conventions; models in src/models | ADR-005, ADR-003 | `feature/INIT-GATEFLOW-002-w2-board` |
| TASK-W2-02 | Integration audit: completing a wave run produces **zero** board ForgeClient mutations from worker | drivestream-lab/gateflow | same | Unit/integration audit assertion | `make check && make test` | fail-fast | product FR-24 | same |
| TASK-W2-03 | Production `gh`-free guards + inspection checklist (FR-25/26a); no subprocess `gh` in ForgeClient path | drivestream-lab/gateflow | same | Unit path guards; docs checklist passes | `make check && make test` ; inspection | ADR-003 PAT rules | ADR-003 | `feature/INIT-GATEFLOW-002-w2-gh-free` |
| TASK-W2-04 | Runbook: laptop `gh` vs deploy ForgeClient (FR-26b); board API usage notes | drivestream-lab/gateflow | same | Runbook present under docs | docs inspection | — | — | same |
| TASK-W2-05 | Live verify board APIs; update verify_all/README/as-built | drivestream-lab/gateflow | same | Board verify green; as-built W2 complete | `make check && make test` ; `.venv/bin/python -m tests.verify.verify_board` | testing-verify-flows | Q-4 exit gate | `feature/INIT-GATEFLOW-002-w2-verify` |
| TASK-W2-06 | **Exit gate:** confirm App/Projects permission matrix (Q-4) before declaring W2 done | drivestream-lab/gateflow | same | Matrix documented or board MVP narrowed | inspection | — | Q-4 deferred | same |

#### Files (W2)

| ID | Path | Action |
|----|------|--------|
| FILE-W2-01 | `src/api/v1/board_routes.py`, board models | create |
| FILE-W2-02 | `src/business_services/board_service.py` | create |
| FILE-W2-03 | `src/infra_services/forge_client.py` | edit |
| FILE-W2-04 | `src/app.py`, DI modules | edit |
| FILE-W2-05 | `tests/unit/**`, `tests/verify/verify_board.py` | create |
| FILE-W2-06 | runbook docs, as-built, `tests/README.md` | create/edit |

#### Tests (W2)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W2-U | unit | `make test` | board CRUD/idempotency/partial; worker isolation; no `gh` |
| TEST-W2-V | live verify | `.venv/bin/python -m tests.verify.verify_board` | board APIs on stack |

---

## 3. Dependencies (DEP)

| ID | Dependency | Blocks |
|----|------------|--------|
| DEP-01 | INIT-GATEFLOW-001 control plane delivered (as-built human_approved) | All waves |
| DEP-02 | prayog-skills pin `v0.5.0-rc.2` | Policy/dispatch (unchanged) |
| DEP-03 | W0 merged | W1 |
| DEP-04 | W1 merged | W2 |
| DEP-05 | GitHub App permissions for board/Projects (Q-4) | **W2 exit** (not W0/W1 start) |
| DEP-06 | Human Alembic revision for wave identity columns | W0-03 / W0-04 |

---

## 4. Risks (RISK)

| ID | Risk | Mitigation |
|----|------|------------|
| RISK-01 | Label removal breaks existing verify/operator habits | Replace primary smoke in W0; changelog/README |
| RISK-02 | App/Projects permissions insufficient | Q-4 exit gate; narrow board MVP |
| RISK-03 | Always-open PR noise on failures | Same `pr.*` naming; clear failed titles (TDD §8) |
| RISK-04 | Cursor SDK still stub at W1 exit | V-3 default — document stub path; SDK follow-on |
| RISK-05 | Agent commits Alembic versions | MDC: humans only under `postgres_migrations/versions/` |

---

## 5. Out of scope

- gateflow-ops BFF/UI
- prayog-skills / launchpad feature delivery
- Working OpenCode / Claude Code / Slack / Teams backends
- Board-column or label wave triggers
- WorkManifest/governance parsing in board APIs
- Auto-merge / gate-approval label writes
- Dogfood programme execution
- Per-user RBAC on programme APIs

---

## 6. As-built and docs tasks

| Task | File | Action |
|------|------|--------|
| Update implementation-status.md | `docs/specification/as-built/implementation-status.md` | mark each wave in_progress → complete |
| Update tests/README.md | `tests/README.md` | wire new verify scripts; mark label smoke superseded |
| W2 runbook | `docs/runbooks/` (or equiv) | laptop `gh` vs ForgeClient deploy |

> **ADR lifecycle** — Accepted ADR-005/006 already on branch; do not add promotion tasks.

---

## 7. Plan check summary

| Check | Status |
|-------|--------|
| P1 Every wave has ≥1 REQ | PASS |
| P2 Every REQ has ≥1 TASK | PASS |
| P3 Every TASK has FILE paths | PASS |
| P4 Every TASK has done when | PASS |
| P5 Test TASKs name unit/verify commands | PASS |
| P6 Scope within spec | PASS |
| P7 Feasibility blockers addressed | PASS — C-1/S-6 via Accepted ADR-005/006; Q-4/Q-5/V-3 deferred with defaults |
| P8 Wave order documented | PASS — W0→W1→W2 |
| P9 As-built/README in same PR as code | PASS — §6 |
| P10 Self-contained + commands | PASS |
| P11 MDC notes on TASKs | PASS |
| P12 ADR Accepted files cited | PASS — ADR-005/006 Accepted |
| P13 TDD Accepted + PE sign-off | PASS |
| P14 WorkManifest §9 valid | PASS — W0/W1/W2 |

---

## 8. PR instructions

> Commit this plan to the **Draft spec PR** branch. Label remains **`spec-pending`**
> until PE completes §10.

```
Branch:   chore/INIT-GATEFLOW-002-spec-gateflow
PR:       https://github.com/drivestream-lab/gateflow/pull/10
Reviewers: @drivestream-lab/prayog-pe-team
Review deadline: 2026-07-29

PE checklist (before spec-lgtm):
  [ ] Spec + feasibility + TDD + Accepted ADRs + this plan on current head
  [ ] §0 PE sign-off complete
  [ ] Wave order W0→W1→W2 makes sense
  [ ] Done-when criteria observable
  [ ] WorkManifest §9 wave IDs W0, W1, W2
  [ ] P1–P14 pass

After spec-lgtm + Approve + merge — **/board-seed** from §9 (post-merge only)
```

---

## 10. Gate 2 unlock (PE — after plan on head)

| Item | Value |
|------|-------|
| Verdict | GATE OPEN REQUEST |
| Spec PR | https://github.com/drivestream-lab/gateflow/pull/10 |
| Spec PR head SHA | `8762a1b0a722902924cd9d514ff862dffef6b260` |
| Gate label (current) | `spec-pending` |
| Gate label (target) | `spec-lgtm` |
| Blocking items | none |

```bash
launchpad apply-gates --repo gateflow --apply
```

PE actions on **exact current head**:

1. Remove `spec-pending` / `spec-blocked` / `spec-revised` / `spec-stale`; add **`spec-lgtm`**
2. GitHub **Approve** with attestation below
3. Mark Draft PR **Ready for review**
4. Authorize merge; then **`/board-seed`** from §9

### Approve attestation body

```text
Spec package approved
initiative: INIT-GATEFLOW-002
spec_pr_head_sha: 8762a1b0a722902924cd9d514ff862dffef6b260
meta_pr_head_sha: 8f291367134a686baaf650835a89dba92e887051
impact_map_revision: 1
prd_digest: sha256:2f339bae00df71e21b45e51c7551f1fb06490dd1805b96e08daca741c140332c
scope_digest: sha256:3662f15e366994defaf08fa43b0a5a568eb152f6a74bcff73a0b0453dba0c901
plan_digest: sha256:cc7f86fe7dfee20734537deaa582e8d4f220484d1f29a433b5950b7c1fdbf228
artifacts:
  - docs/specification/product/INIT-GATEFLOW-002-gateflow.md
  - docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-002.md
  - docs/specification/reports/Technical-Review-INIT-GATEFLOW-002.md
  - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-002.md
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
# Generated by /spec-implementation-plan — 2026-07-24
# LOCAL — do not commit to prayog-skills upstream
apiVersion: launchpad/v1
kind: WorkManifest

initiative: INIT-GATEFLOW-002
# Branch naming: feature/INIT-GATEFLOW-002-w{N}-{slug}

metadata:
  title: INIT-GATEFLOW-002 — API-triggered waves & platform readiness
  summary: |
    Make Gateflow API-first: wave-start API (label removed), fail-closed adapter
    registry, PR-at-run-start, richer run/metrics APIs, board forge primitives,
    ForgeClient-only production path. gateflow only; gateflow-ops deferred.
  playbook:
    - docs/specification/product/INIT-GATEFLOW-002-gateflow.md
    - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-002.md

target:
  org: drivestream-lab
  project: drivestream-lab Board

defaults:
  initiative: INIT-GATEFLOW-002
  parent: EPIC
  status: Backlog
  labels:
    - INIT-GATEFLOW-002

epic:
  id: EPIC
  repo: drivestream-lab/gateflow
  title: "[feature] INIT-GATEFLOW-002 — API-triggered waves & platform readiness"
  codebase: drivestream-lab/gateflow
  spec_path: docs/specification/product/INIT-GATEFLOW-002-gateflow.md
  verify_command: make check && make test
  body: |
    ## Objective

    Deliver API-first wave start, per-node runner/model, PR thread at run start,
    ops run/metrics APIs, and board forge primitives on drivestream-lab/gateflow
    only (ForgeClient deploy path; no gh in production).

    ## Waves

    | Wave | Goal |
    |------|------|
    | W0 | API trigger + run list/detail + stub registry |
    | W1 | Per-node model + PR-at-start + metrics + Cursor path |
    | W2 | Board APIs + gh-free deploy proof |

    ## References

    - Spec: docs/specification/product/INIT-GATEFLOW-002-gateflow.md
    - Implementation plan: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-002.md
    - Technical review: docs/specification/reports/Technical-Review-INIT-GATEFLOW-002.md

work:
  - id: W0
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-002 W0] API trigger skeleton + run list/detail + stubs"
    depends_on: []
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-002-gateflow.md
    verify_command: make check && make test
    status: Backlog
    body: |
      ## Wave goal

      Authenticated POST /api/v1/waves/start; label cannot start waves; adapter
      registry + fail-closed before enqueue; run list/detail under programme token.

      ## Tasks (from plan §2)

      - TASK-W0-01: Programme config notifier + override coerce
      - TASK-W0-02: Adapter registry + SlotValidator
      - TASK-W0-03: wave_id schema + human migration
      - TASK-W0-04: Wave-start API + public_paths
      - TASK-W0-05: Disable label wave-start
      - TASK-W0-06: Run list/detail timeline
      - TASK-W0-07: Unit + live verify wave-start
      - TASK-W0-08: As-built W0

      ## Done when

      - [ ] All W0 tasks complete per plan

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-002-gateflow.md

  - id: W1
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-002 W1] Per-node model + PR-at-start + metrics"
    depends_on:
      - W0
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-002-gateflow.md
    verify_command: make check && make test
    status: Backlog
    body: |
      ## Wave goal

      Per-node runner/model; PR open/update at run start with stage comments;
      metrics by node/runner/model_id; Cursor happy path (stub OK for exit).

      ## Tasks (from plan §2)

      - TASK-W1-01: Per-node override persistence
      - TASK-W1-02: ForgeClient PR-at-start + Notifier
      - TASK-W1-03: Metrics dimensions + api_trigger events
      - TASK-W1-04: Cursor path (stub allowed)
      - TASK-W1-05: Live verify PR + metrics
      - TASK-W1-06: As-built W1

      ## Done when

      - [ ] All W1 tasks complete per plan

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-002-gateflow.md

  - id: W2
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-002 W2] Board APIs + gh-free deploy path"
    depends_on:
      - W1
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-002-gateflow.md
    verify_command: make check && make test
    status: Backlog
    body: |
      ## Wave goal

      Board dumb primitives via ForgeClient; worker never calls board APIs;
      production gh-free verification; laptop gh policy docs; Q-4 exit gate.

      ## Tasks (from plan §2)

      - TASK-W2-01: Board routes + ForgeClient board ops
      - TASK-W2-02: Worker isolation audit
      - TASK-W2-03: gh-free production guards
      - TASK-W2-04: FR-26b runbook
      - TASK-W2-05: Board live verify + as-built
      - TASK-W2-06: Q-4 permission matrix exit gate

      ## Done when

      - [ ] All W2 tasks complete per plan
      - [ ] Q-4 confirmed or board MVP narrowed

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-002-gateflow.md
```

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-implementation-plan
  outcome: pass
  artifact:
    path: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-002.md
    digest: sha256:8491c2d0fb4355e1dd4120f6e01610a1bf3f860d8cf860c7563b25e53e45086a
  blockers: []
  signals:
    gate2_unlock: requested
    gate2_label: spec-pending
    draft_spec_pr: https://github.com/drivestream-lab/gateflow/pull/10
    source_freshness: CURRENT
    map_revision: 1
    waves: [W0, W1, W2]
    ready_for_board_seed: false
    accepted_adrs: [ADR-005, ADR-006]
  next_candidates:
    - gate-2
  human_checkpoint: true
  external_action: true
```

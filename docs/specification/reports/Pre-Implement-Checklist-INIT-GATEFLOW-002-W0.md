# Pre-implement — drivestream-lab/gateflow / W0 — API trigger skeleton + run list/detail + stubs

Produced by `/pre-implement` on 2026-07-24 for **INIT-GATEFLOW-002**. **No product code in this stage.**

---

### Gate check (prior wave)

> W0 is the first wave of this initiative — gate is PE sign-off (§0) + INIT-001 baseline `human_approved` (DEP-01), not a GATEFLOW-002 prior Ground Report.

| Item | Required | Status |
|------|----------|--------|
| Branch context | `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | **ok** — on `develop` @ `8e948f1` |
| Spec PR merged | Implementation plan on integration branch | **yes** — `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-002.md` on `develop` |
| Gate 2 at merge | Merged spec PR had `spec-lgtm` on head | **verified** — PR [#10](https://github.com/drivestream-lab/gateflow/pull/10) MERGED; label `spec-lgtm`; head `82db4fe3…` matches PE attestation comment (`spec_pr_head_sha`); merge `8e948f1…` |
| Board seed | Wave issue(s) from plan §9 exist | **seeded** — EPIC [#11](https://github.com/drivestream-lab/gateflow/issues/11); W0 [#12](https://github.com/drivestream-lab/gateflow/issues/12); W1 [#13](https://github.com/drivestream-lab/gateflow/issues/13); W2 [#14](https://github.com/drivestream-lab/gateflow/issues/14); W0–W2 are sub-issues of #11; all on **drivestream-lab Board** |
| Plan source freshness | all upstream rows `CURRENT` | **current** — spec / feasibility / TDD digests match `shasum -a 256` on disk |
| Impact-map repo scope | revision and scope digest match canonical handoff | **match** — `map_revision: 1`; gateflow scope `sha256:3662f15e366994defaf08fa43b0a5a568eb152f6a74bcff73a0b0453dba0c901` |
| `check_command` | resolved | **`make check`** |
| `test_command` | resolved | **`make test`** |
| `verify_command` | resolved or N/A | **resolved** — W0 target: `.venv/bin/python -m tests.verify.verify_wave_start` (or updated smoke); interim baseline `.venv/bin/python -m tests.verify.verify_all` |
| `ground_command` | resolved or N/A | **N/A** — `/ground-spec` skill (no Makefile ground target) |
| Prior wave as-built row | `human_approved` | **N/A for INIT-002 W0** — baseline DEP-01: INIT-GATEFLOW-001 **W0 + W1 = human_approved** in `as-built/implementation-status.md` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | **N/A** — first wave; consume INIT-001 W1 contracts as baseline |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | **complete** — 2026-07-24 (@nikd10x via Cursor chat on PR #10) |

**Gate verdict:** PASS

---

### Contracts consumed (from prior Ground Report)

> Source: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-001-W1.md` §Contracts produced (cross-initiative baseline). Confirmed against `src/`.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| ProgrammeConfig load | `ProgrammeConfig.get_instance` / YAML loader | YAML path / env | Validated sections (trigger, handoff, retry, runner, model, tools, metrics) | Ground-Report-001-W1 / W0 | **yes** — `src/models/programme_config_models.py`, `config/programme.yaml` |
| Webhook enqueue | `POST /webhooks/github` → job row | delivery id, event, payload, signature | job id or duplicate; 401/503 | Ground-Report-001-W0/W1 | **yes** — live `verify_all` |
| Trigger authorize | `TriggerRouter.authorize_and_check` | event type, delivery id, payload, programme config | authorized + context **or** precondition failures | Ground-Report-001-W1 | **yes** — label match + PC checklist; **W0 must change** label start path (FR-15) |
| Job orchestration | `RunOrchestrator.process_job` | claimed job DTO | run summary (run id, terminal status, dispatched) | Ground-Report-001-W1 | **yes** — worker path exists |
| RunStore persistence | repos create / find_active_run / events | Pydantic create DTOs | Pydantic models | Ground-Report-001-W1 | **yes** — `find_active_run(org, repo, pr\|issue)` only; **no `wave_id` column yet** |
| Programme-token AuthN | `verify_programme_service_token` | Bearer header | void or 401 | Ground-Report-001-W1 | **yes** — status/metrics; ADR-005 widens to writes |
| Run status read | `GET /api/v1/runs/{run_id}` | Bearer + run id | `RunStatusResponse` header fields only | Ground-Report-001-W1 | **yes** — **no stage/event timeline yet** (FR-20 W0) |
| Metrics aggregate | `GET /api/v1/metrics/runs` | Bearer | retention + `by_workflow_node` | Ground-Report-001-W1 | **yes** — richer dims deferred to W1 |
| `public_paths` allowlist | `src/app.py` AuthMiddleware | path prefixes | JWT bypass for listed prefixes | Ground-Report-001-W1 | **yes** — `/api/v1/runs`, `/api/v1/metrics`; **must add `/api/v1/waves`** |
| Forge comments | `Notifier` → `ForgeClient.post_comment` | org/repo/issue + event | comment id or `notify_pending` | Ground-Report-001-W1 | **yes** — GitHub-only today |

**Unconfirmed contracts** (new in INIT-002 W0 — no Ground Report backing):

- `POST /api/v1/waves/start` dual-identity body + enqueue (TDD §3.1) — **not implemented**
- Adapter registry + `SlotValidator.validate_for_run` (ADR-006 / TDD §3.4) — **not implemented**
- Programme config `notifier.*` + structured `model.overrides` object coerce (TASK-W0-01) — **missing / still `dict[str,str]`**
- RunStore `wave_id` (+ active-run by wave identity) — **schema/repo gap; human Alembic DEP-06**
- `GET /api/v1/runs` list/filter + detail timeline enrichment — **not implemented**
- Label wave-start **disabled** for 002 programmes — **still primary path** (`verify_wave_start`)

→ Treat all of the above as **implementation scope**, not assumed baselines. Do not start coding until human Alembic plan for `wave_id` is agreed (DEP-06).

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered for W0):
  - [x] `architecture.mdc` — mounts, `public_paths`, layering
  - [x] `dependency-injection.mdc` — registry / services as singletons
  - [x] `infra-services.mdc` — stub runners/notifiers stay infra
  - [x] `repository-pattern.mdc` — RunStore via repos only; ORM ↔ Pydantic at repo
  - [x] `pydantic-schemas.mdc` — wave/run models in `src/models/` only; override coerce
  - [x] `http-api-conventions.mdc` — POST body models; GET filters as query
  - [x] `fail-fast.mdc` — stub/precondition reject; no silent Cursor/GitHub fallback
  - [x] `database-migrations.mdc` — **human** owns `postgres_migrations/versions/`
  - [x] `logging-loguru.mdc` — structured kwargs (`run_id`, `wave_id`, …)
  - [x] `testing-verify-flows.mdc` — replace label primary smoke
  - [x] `strong-typing.mdc` / `python-imports.mdc` / `python-tooling.mdc` / `spec-driven-development.mdc`
  - skipped: none material — W0 touches all listed domains
- [x] ADRs (keyword-matched):
  - [x] ADR-001 — dual process; durable RunStore (wave identity columns)
  - [x] ADR-002 — trust zones (JWT / webhook / programme token) — programme-token **write** row superseded by ADR-005
  - [x] ADR-003 — adapters = infra; policy/orchestrator/registry validation = business
  - [x] ADR-004 — programme YAML authority; secrets in env
  - [x] ADR-005 — programme-token **mutations** for documented control-plane writes (`sha256:88eab400…` matches disk)
  - [x] ADR-006 — business registry + fail-closed before accept (`sha256:fff0c515…` matches plan; TDD table still cites older digest — hygiene only)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-002-gateflow.md` (FR-15, 17, 18, 20, 23 skeleton; preconditions)
- [x] Plan wave section: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-002.md` Phase W0
- [x] TDD contracts: `docs/specification/reports/Technical-Review-INIT-GATEFLOW-002.md` §3.1, §3.2, §3.4, §3.7, §6

---

### Governance alignment

- [x] Slice spec does not contradict listed Accepted ADRs
- [x] Plan TASK MDC notes and ADR notes for W0 reviewed (TASK-W0-01…08)
- [x] ADR-005 / ADR-006 are **Accepted** under `docs/specification/adr/` (not promoted during planning)
- [ ] Hygiene (non-blocking): refresh ADR-006 digest in TDD §4 table to `fff0c515…` when convenient

---

### Must update (in the same change as the code)

- [ ] Product spec — only if implementation drifts FR-15/17/18/20/23 contracts (prefer no drift)
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-002 W0 verification rows (TASK-W0-08)
- [ ] `tests/README.md` — feature map: API wave-start primary; label smoke superseded for 002
- [ ] Unit — dual identity, auth 401, stub fail-closed, label reject, list/filter, timeline
- [ ] Live — `verify_wave_start` (or updated smoke): API start → run row; label does **not** start; extend status verify for list/detail
- [ ] ADR — none expected unless PE supersedes; do not re-litigate ADR-005/006

---

### Must not

- [ ] Contradict Accepted ADRs without superseding first
- [ ] Duplicate full HTTP journeys in pytest when verify scripts own them
- [ ] Assume `wave_id` / list/timeline / registry exist without building them
- [ ] Agent-authored Alembic under `postgres_migrations/versions/` (human only — DEP-06)
- [ ] Silent fallback to Cursor or GitHub when stub selected (ADR-006)
- [ ] Put programme token / App secrets in `programme.yaml`
- [ ] Define Pydantic models under `src/api/`
- [ ] Call board APIs from wave-start or worker (FR-24 is W2; worker isolation)
- [ ] Keep label-based wave start as a supported path for 002 programmes

---

### Suggested implementation order (from plan)

1. Cut branch: `feature/INIT-GATEFLOW-002-w0-config-registry` (or one cohesive W0 branch — plan also names `…-w0-wave-start`, `…-w0-run-apis`, `…-w0-verify`)
2. **TASK-W0-01** — `notifier.default` + coerce `model.overrides` str→object; document label non-start
3. **TASK-W0-02** — adapter registry + `SlotValidator`; register cursor + stubs (opencode/claude; slack/teams)
4. **TASK-W0-03** — schema/repo `wave_id` + active-run by wave identity; **human** writes Alembic revision
5. **TASK-W0-04** — `WaveStartService` + `POST /api/v1/waves/start` + extend `public_paths`
6. **TASK-W0-05** — disable label wave-start in `TriggerRouter` for 002
7. **TASK-W0-06** — `GET /api/v1/runs` list/filter + detail timeline
8. **TASK-W0-07** — unit + live verify; update `tests/README.md`
9. **TASK-W0-08** — as-built W0 rows

### Concrete paths (plan FILE-W0-*)

| Path | Action |
|------|--------|
| `config/programme.yaml`, `config/programme.yaml.example` | edit — `notifier.*`; override shape |
| `src/models/programme_config_models.py`, wave/run list models | edit/create |
| `src/business_services/slot_validator.py`, adapter registry module | create |
| stub runner/notifier infra modules | create |
| `src/business_services/wave_start_service.py` | create |
| `src/api/v1/waves_routes.py`, `src/api/v1/__init__.py`, `src/app.py` | create/edit |
| `src/business_services/trigger_router.py` | edit — reject label start |
| `src/api/v1/runs_routes.py`, metrics/run models, repos | edit |
| `src/database/postgres/schema/*`, `repository/*` | edit — `wave_id` |
| `postgres_migrations/versions/*` | **human** create |
| `postgres_migrations/env.py` | edit if new schema module |
| `src/di/modules/*`, `dependency_container.py` | edit |
| `tests/unit/**`, `tests/verify/verify_wave_start.py` (or smoke update) | create/edit |
| `tests/README.md`, `docs/specification/as-built/implementation-status.md` | edit |

---

### W0 contract baselines (to implement against — TDD)

**Wave start — `POST /api/v1/waves/start`**

- Auth: programme service token (ADR-005); extend `public_paths` with `/api/v1/waves`
- Body: optional `ticket_id` **or** (`initiative_id` + `wave_id`); optional `org`/`repo`, workspace, PR/issue helpers
- Dual identity: if both forms present they must agree → else **400**, no run
- Success **2xx**: `{ run_id, job_id?, status }`
- Errors: **401** token; **400** identity; **409/422** precondition/stub/config list; **503** store down
- Invariants: no board API calls; no AgentRunner on request path; label not accepted as start

**SlotValidator — `validate_for_run`**

- Input: required runner ids + notifier id + config keys
- Output: ok **or** failures `[{slot_kind, adapter_id, config_key, reason}]`
- Invariant: any required `implemented=false` → fail before enqueue; unused stubs OK

**Runs — list + detail**

- `GET /api/v1/runs` filters: `initiative_id`, `wave_id`, `status_type`, `org`, `repo`, `limit`, cursor/skip
- `GET /api/v1/runs/{run_id}`: header + **full stage/event timeline** from RunStore
- Auth: programme token; invalid filter **400**; missing **404**; store down **503**

**Label policy**

- `TriggerRouter` rejects label-based wave authorization for 002; webhook may still ack non-start events

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format, lint, types, layers | `make check` |
| Unit | identity, auth, stubs, label reject, list/detail | `make test` |
| Live verify | API start → run row; label does not start; list/detail | `.venv/bin/python -m tests.verify.verify_wave_start` (+ status/metrics); interim `verify_all` until script lands |
| Ground check | W0 FRs + boundaries | `/ground-spec` (no Makefile `ground_command`) |

---

### Tracker / PR

- Initiative: **INIT-GATEFLOW-002**
- Issue: **[#12](https://github.com/drivestream-lab/gateflow/issues/12)** (W0); parent EPIC [#11](https://github.com/drivestream-lab/gateflow/issues/11)
- Spec path: `docs/specification/product/INIT-GATEFLOW-002-gateflow.md`
- Verify command: `make check && make test` ; live `.venv/bin/python -m tests.verify.verify_wave_start` (or updated smoke)
- ADRs in scope: ADR-001, ADR-003, ADR-004, ADR-005, ADR-006 (ADR-002 background)

---

### Merge order (if cross-module / cross-service)

N/A — single repo `drivestream-lab/gateflow`. Internal order: config/registry → schema+migration → wave-start API → label disable → run list/detail → verify/as-built. W1 blocked on W0 merge (DEP-03).

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-Checklist-INIT-GATEFLOW-002-W0.md
    digest: sha256:b375c35462a915440522a94579fd6c7f3a83059c87d8bbef1e4be5274f7ac61a
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-002
    wave: W0
    board_epic: https://github.com/drivestream-lab/gateflow/issues/11
    board_issue: https://github.com/drivestream-lab/gateflow/issues/12
    spec_pr: https://github.com/drivestream-lab/gateflow/pull/10
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_wave_start
    ground_command: N/A — /ground-spec skill
    gate_verdict: PASS
    pe_signoff: complete
    board_seed: complete
    source_freshness: CURRENT
    map_revision: 1
    human_alembic_required: true
  next_candidates:
    - loop-spec
  human_checkpoint: true
  external_action: false
```

# Pre-implement — drivestream-lab/gateflow / W1 — Per-node model + PR-at-start + metrics

Produced by `/pre-implement` on 2026-07-24 for **INIT-GATEFLOW-002**. **No product code in this stage.**

---

### Gate check (prior wave)

> W1 requires INIT-GATEFLOW-002 W0 Ground Report + as-built `human_approved` (DEP-03).

| Item | Required | Status |
|------|----------|--------|
| Branch context | `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | **ok** — on `develop` @ `5c4581b` |
| Spec PR merged | Implementation plan on integration branch | **yes** — `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-002.md` on `develop` |
| Gate 2 at merge | Merged spec PR had `spec-lgtm` on head | **verified** — PR [#10](https://github.com/drivestream-lab/gateflow/pull/10) MERGED; label `spec-lgtm`; head `82db4fe3…` |
| Board seed | Wave issue(s) from plan §9 exist | **seeded** — EPIC [#11](https://github.com/drivestream-lab/gateflow/issues/11); W0 [#12](https://github.com/drivestream-lab/gateflow/issues/12) CLOSED; W1 [#13](https://github.com/drivestream-lab/gateflow/issues/13) OPEN; W2 [#14](https://github.com/drivestream-lab/gateflow/issues/14); all sub-issues of #11 on **drivestream-lab Board** |
| Plan source freshness | all upstream rows `CURRENT` | **current** — spec / feasibility / TDD digests match `shasum -a 256` on disk (`9d437c0…` / `33d5b40…` / `12106d0…`) |
| Impact-map repo scope | revision and scope digest match canonical handoff | **match** — plan + TDD + PE attestation agree `map_revision: 1` and scope `sha256:3662f15e366994defaf08fa43b0a5a568eb152f6a74bcff73a0b0453dba0c901` (local `prayog-meta/` clone absent — not re-hashed from disk) |
| `check_command` | resolved | **`make check`** |
| `test_command` | resolved | **`make test`** |
| `verify_command` | resolved or N/A | **resolved** — W1 target: `.venv/bin/python -m tests.verify.verify_pr_thread` (or extended smoke); interim baseline `.venv/bin/python -m tests.verify.verify_all` |
| `ground_command` | resolved or N/A | **N/A** — `/ground-spec` skill (no Makefile ground target) |
| Prior wave as-built row | `human_approved` | **INIT-002 W0 = human_approved** in `docs/specification/as-built/implementation-status.md` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | **exists** — `docs/specification/reports/Ground-Report-INIT-GATEFLOW-002-W0.md` (**human_approved**) |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | **complete** (recorded; N/A as W1 gate — prior wave approval is the gate) |

**Gate verdict:** PASS

---

> **Living supersession (config carrier):** `config/programme.yaml` / YAML `ProgrammeConfig` load are **removed**. Live authority is env (`GATEFLOW_*`), wave-start API, and pin `workflow.yaml` — ADR-004, INIT-002 A-7, as-built, and `docs/specification/reports/README.md`. Mentions below are wave-time evidence only.


### Contracts consumed (from prior Ground Report)

> Source: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-002-W0.md` §Contracts produced. Confirmed against `src/` / `config/` / `tests/verify/`.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Wave start HTTP | `POST /api/v1/waves/start` via WaveStartService | Bearer programme token + dual-identity body | `{ run_id, job_id?, status }` | Ground-Report-002-W0 | **yes** — routes + service live; verify `verify_wave_start` |
| Dual identity resolve | WaveStartService `_resolve_identity` | ticket and/or initiative+wave | resolved initiative / wave / issue | Ground-Report-002-W0 | **yes** |
| Slot fail-closed | SlotValidator `validate_for_run` | required runner + notifier + config keys | ok or structured failures | Ground-Report-002-W0 | **yes** — W1 reuses for override/profile validity at start |
| Adapter catalogue | AdapterRegistry | opaque adapter id | capability `{implemented}` + slot kind | Ground-Report-002-W0 | **yes** — cursor + github_comment implemented; stubs registered |
| Label start policy | TriggerRouter `authorize_and_check` | event + payload | authorized context or failures | Ground-Report-002-W0 | **yes** — non-`api_trigger` start rejected |
| API trigger job | WaveStartService → JobRepository | `event_type=api_trigger` + run_id | pending job | Ground-Report-002-W0 | **yes** — worker must reuse `run_id` (**D-W0-V1**: live verify does not yet assert claim→orchestrator e2e) |
| Run list / detail timeline | MetricsEmitter + runs routes | Bearer + filters / run id | list items or header+stages+events | Ground-Report-002-W0 | **yes** |
| Programme config v2 (wave; living: removed — see supersession) | ProgrammeConfig load (wave) | YAML (wave) | validated config incl. `notifier.default`, `NodeOverride` objects | Ground-Report-002-W0 | **wave yes / living no** |
| Wave identity store | RunStore create / find_active / list | `wave_id` + identity fields | Pydantic run models | Ground-Report-002-W0 | **yes** — stage columns `runner` / `model_profile` / `model_id` / `model_provider` already on ORM+DTOs |
| Programme-token AuthN | Bearer programme token on control-plane routes | Authorization header | void or 401 | Ground-Report-002-W0 / ADR-005 | **yes** |
| Forge comments | Notifier → ForgeClient `post_comment` | org/repo/issue + body | comment id or `notify_pending` | Ground-Report-002-W0 | **yes** — comments today target issue/PR number from context; **no PR create/update** |
| Job orchestration | RunOrchestrator `process_job` | claimed job DTO | run summary | Ground-Report-002-W0 / 001-W1 | **yes** — always dispatches via `CursorAgentRunner`; profile from override or `"default"`; runner override field **not** selected |
| Metrics aggregate | MetricsEmitter `aggregate_run_metrics` | Bearer | retention + `by_workflow_node` only | Ground-Report-002-W0 | **yes** — **no `by_runner` / `by_model_id` yet**; events are `stage_completed` / stop — **no `api_trigger` event type yet** |
| Cursor AgentRunner stub | CursorAgentRunner `run_skill` | workspace + skill + model_profile | agent result | Ground-Report-001 / as-built | **yes** — stub success under `mock-*` or `GATEFLOW_AGENT_STUB` (V-3 default for W1 exit) |

**Unconfirmed contracts** (new in INIT-002 W1 — no Ground Report backing):

- Programme `pr.*` templates (wave gap at checklist time; living: no programme.yaml — PR targeting via wave-start / forge)
- ForgeClient `create_or_update_pull_request` — **not implemented** (`post_comment` + forbid-only helpers only)
- Orchestrator **PR-at-run-start** before first orchestrated stage; Notifier comments on **that** PR; `notify_pending` on PR open/update failure (Q-5 default) — **not implemented**
- Per-node **runner** selection from `NodeOverride.runner` / `runner.default` (not hardwired Cursor) + persist four fields from resolved config (today fields come from agent_result only) — **partial gap** (D-W0-M1)
- MetricsEmitter `api_trigger` (+ richer stage/stop dims) and aggregates `by_runner`, `by_model_id` on `GET /metrics/runs` — **not implemented**
- Live verify `verify_pr_thread` (PR + metric keys) — **script does not exist yet**

→ Treat all of the above as **implementation scope**. Stage ORM columns already exist — **no new Alembic expected** unless W1 discovers a schema gap (human-only if so).

**Carried risk from W0:**

- **D-W0-V1** — deepen or accept: worker claim of `api_trigger` → orchestrator path needed for PR-at-start / metrics live proof; plan live verify may need API+worker running.

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered for W1):
  - [x] `architecture.mdc` — layering; infra vs business; no board routes in W1
  - [x] `dependency-injection.mdc` — ForgeClient / runners singleton lifecycle
  - [x] `infra-services.mdc` — ForgeClient + CursorAgentRunner stay infra
  - [x] `repository-pattern.mdc` — stage field persistence via repos only
  - [x] `pydantic-schemas.mdc` — `pr.*` models in `src/models/`; metrics response dims
  - [x] `http-api-conventions.mdc` — metrics GET filters remain query; no new write bodies unless needed
  - [x] `fail-fast.mdc` — invalid override blocked at start; no silent PR success
  - [x] `logging-loguru.mdc` — structured kwargs (`run_id`, `runner`, `model_id`, `pr_number`)
  - [x] `testing-verify-flows.mdc` — `verify_pr_thread` + README feature map
  - [x] `strong-typing.mdc` / `python-imports.mdc` / `python-tooling.mdc` / `spec-driven-development.mdc`
  - skipped: `database-migrations.mdc` as primary work — stage columns already present; **re-read if any DDL appears**
  - skipped: `code-guidelines-index.mdc` — index only
- [x] ADRs (keyword-matched):
  - [x] ADR-001 — dual process; durable RunStore (stage persistence; jobs)
  - [x] ADR-003 — ForgeClient / AgentRunner = infra; orchestrator / notifier / metrics = business; no auto-merge / gate labels
  - [x] ADR-004 — programme config authority; secrets in env (`pr.*` was YAML in wave; living carrier removed)
  - [x] ADR-005 — programme-token control-plane reads (metrics/runs) unchanged; no new write surface required for W1 core
  - [x] ADR-006 — fail-closed selection still applies when resolving required runners for overrides
  - [x] ADR-002 — background trust zones (JWT/webhook); programme-token write row superseded by ADR-005
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-002-gateflow.md` (FR-16, FR-19, FR-21, FR-22; Q-2/Q-5/V-3)
- [x] Plan wave section: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-002.md` Phase W1
- [x] TDD contracts: `docs/specification/reports/Technical-Review-INIT-GATEFLOW-002.md` §3.5, §5–§8 (PR naming, metrics, Cursor V-3)
- [x] Prior Ground Report: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-002-W0.md`
- [x] `tests/README.md` — W0 feature map; W1 scripts not yet listed

---

### Governance alignment

- [x] Slice spec does not contradict listed Accepted ADRs
- [x] Plan TASK MDC notes and ADR notes for W1 reviewed (TASK-W1-01…06)
- [x] Every initiative ADR cited for W1 is **Accepted** under `docs/specification/adr/`
- [x] Deferred PE defaults for W1 exit acknowledged: **Q-5** (`notify_pending` + status API); **V-3** (stub/`mock-*`/`GATEFLOW_AGENT_STUB` OK); **Q-2** resolved in TDD §8 (`pr.*` templates)
- [ ] Q-4 App/Projects permissions — **W2 exit only**; do not block W1

---

### Must update (in the same change as the code)

- [ ] Product spec — only if implementation drifts FR-16/19/21/22 contracts (prefer no drift)
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-002 W1 verification rows (TASK-W1-06)
- [ ] `tests/README.md` — feature map: PR-thread + metrics dims; wire into `verify_all` when ready
- [ ] Unit — ≥2 node overrides; invalid override blocked; ForgeClient PR call order; metrics dims; stub Cursor path
- [ ] Live — `verify_pr_thread` (or extended smoke): PR exists + comments + metric keys; requires stack + secrets (+ worker if asserting orchestrator path)
- [ ] ADR — none expected; do not re-litigate ADR-003/004/006

---

### Must not

- [ ] Contradict Accepted ADRs without superseding first
- [ ] Duplicate full HTTP PR journeys in pytest when verify owns them
- [ ] Assume `create_or_update_pull_request` / `pr.*` / `by_runner` exist without building them
- [ ] Hardcode workflow node allowlists (FR-16 / PolicyEngine unchanged)
- [ ] Auto-merge or gate-approval label writes via ForgeClient
- [ ] Board API calls from orchestrator / worker (FR-24 is W2)
- [ ] Require real Cursor SDK for W1 exit (V-3 deferred — document stub path in as-built)
- [ ] Invent dedicated PE alert channel beyond `notify_pending` + status API (Q-5 default)
- [ ] Put secrets in committed programme config (secrets belong in env / secret store only)
- [ ] Define Pydantic models under `src/api/`
- [ ] Agent-authored Alembic under `postgres_migrations/versions/` (human only if DDL needed)
- [ ] Implement W2 board / `gh`-free production proof scope

---

### Suggested implementation order (from plan)

1. Cut branch: `feature/INIT-GATEFLOW-002-w1-model-pr-metrics` (plan also names `…-w1-verify` for verify/as-built if split)
2. **TASK-W1-01** — per-node runner/model resolution in orchestrator; persist four fields on stages; invalid override blocked at start (reuse SlotValidator / start path)
3. **TASK-W1-02** — programme `pr.*`; ForgeClient `create_or_update_pull_request`; orchestrator PR-at-start; Notifier comments on that PR; `notify_pending` on PR failure
4. **TASK-W1-03** — MetricsEmitter `api_trigger` + stage/stop events; aggregates `by_runner`, `by_model_id` on `GET /metrics/runs`
5. **TASK-W1-04** — Cursor happy path documentation + unit coverage under stub/`GATEFLOW_AGENT_STUB`/`mock-*` (V-3)
6. **TASK-W1-05** — live `verify_pr_thread` + README / `verify_all`
7. **TASK-W1-06** — as-built W1 rows for FR-16/19/21/22

### Concrete paths (plan FILE-W1-*)

| Path | Action |
|------|--------|
| `src/business_services/run_orchestrator.py` | edit — resolve overrides; PR-at-start; persist stage fields |
| `src/infra_services/forge_client.py` | edit — `create_or_update_pull_request` |
| `src/business_services/notifier.py` | edit — comment target = run PR |
| `src/business_services/metrics_emitter.py`, `src/api/v1/metrics_routes.py`, metrics models | edit — dims + `api_trigger` |
| `src/infra_services/cursor_agent_runner.py` | edit as needed — stub happy path |
| `config/programme.yaml` (wave target; **living: removed**) | edit — `pr.*`; sample overrides — see supersession |
| `src/models/programme_config_models.py` (+ metrics/run models as needed) | edit/create — `PrConfig` |
| `tests/unit/**` | edit/create — overrides, PR order, metrics dims, stub cursor |
| `tests/verify/verify_pr_thread.py` (or extended smoke), `verify_all.py` | create/edit |
| `tests/README.md`, `docs/specification/as-built/implementation-status.md` | edit |

---

### W1 contract baselines (to implement against — TDD / spec)

**Per-node model (FR-16)**

- Resolve runner + model profile per `workflow_node` for `dispatch: orchestrated` from `model.overrides` / `runner.default` / `model.profiles.default`
- Persist `runner`, `model_profile`, `model_id`, `model_provider` on every orchestrated stage
- Unknown override node / missing profile / unresolvable model → block at start (FR-18); no hardcoded node allowlists
- Done when: ≥2 nodes different profiles in fixtures; invalid override blocked

**PR-at-start (FR-19 / TDD §3.5 / §8)**

- Config:
  ```yaml
  pr:
    branch_prefix: gateflow/run-
    title_template: "[gateflow] {initiative_id} {wave_id} {run_id_short}"
    body_template: "Run `{run_id}` — status API supplementary."
  ```
- ForgeClient `create_or_update_pull_request` before first orchestrated stage completes
- Same naming keys on success and failure paths; no auto-merge; no board link
- Notifier posts stage/stop/failed comments on **that** PR
- PR open/update failure → `notify_pending` + status API (Q-5); do not invent success visibility

**Metrics (FR-21 / FR-22)**

- Emit events for API-accepted start (`api_trigger`), orchestrated stages, stops / findings loops
- `GET /api/v1/metrics/runs` exposes `by_workflow_node`, `by_runner`, `by_model_id` when data exists
- Auth same as FR-20; invalid filter → 400; store down → 503

**Cursor path (V-3)**

- W1 exit may use stub / `GATEFLOW_AGENT_STUB` / `mock-*`; document stub vs SDK in as-built
- Launchpad sync remains pre-dispatch

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format, lint, types, layers | `make check` |
| Unit | overrides (≥2), PR call order, metrics dims, stub cursor | `make test` |
| Live verify | PR + comments + metric keys | `.venv/bin/python -m tests.verify.verify_pr_thread` (or extended smoke); interim `.venv/bin/python -m tests.verify.verify_all` until script lands |
| Ground check | W1 FRs + boundaries | `/ground-spec` (no Makefile `ground_command`) |

---

### Tracker / PR

- Initiative: **INIT-GATEFLOW-002**
- Issue: **[#13](https://github.com/drivestream-lab/gateflow/issues/13)** (W1); parent EPIC [#11](https://github.com/drivestream-lab/gateflow/issues/11)
- Spec path: `docs/specification/product/INIT-GATEFLOW-002-gateflow.md`
- Verify command: `make check && make test` ; live `.venv/bin/python -m tests.verify.verify_pr_thread` (or updated smoke / `verify_all`)
- ADRs in scope: ADR-001, ADR-003, ADR-004, ADR-005, ADR-006 (ADR-002 background)
- Suggested branch: `feature/INIT-GATEFLOW-002-w1-model-pr-metrics`

---

### Merge order (if cross-module / cross-service)

N/A — single repo `drivestream-lab/gateflow`. Internal order: override resolution → PR-at-start (config + ForgeClient + orchestrator/notifier) → metrics dims/events → Cursor stub docs → live verify → as-built. W2 blocked on W1 merge (DEP-04).

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-Checklist-INIT-GATEFLOW-002-W1.md
    digest: sha256:62966757b44ef713c856ff76b49d0a75b1675a24725de320a04a39d818bacede
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-002
    wave: W1
    board_epic: https://github.com/drivestream-lab/gateflow/issues/11
    board_issue: https://github.com/drivestream-lab/gateflow/issues/13
    spec_pr: https://github.com/drivestream-lab/gateflow/pull/10
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-002-W0.md
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_pr_thread
    ground_command: N/A — /ground-spec skill
    gate_verdict: PASS
    board_seed: complete
    source_freshness: CURRENT
    map_revision: 1
    deferred_defaults: [Q-5, V-3]
    carried_risk: D-W0-V1
    suggested_branch: feature/INIT-GATEFLOW-002-w1-model-pr-metrics
  next_candidates:
    - loop-spec
  human_checkpoint: true
  external_action: false
```

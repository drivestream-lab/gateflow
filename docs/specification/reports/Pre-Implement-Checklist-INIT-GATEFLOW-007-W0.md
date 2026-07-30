# Pre-implement — drivestream-lab/gateflow / W0 — Closeout start API + Pass-2 walker + smoke verify

Produced by `/pre-implement` on 2026-07-30 for **INIT-GATEFLOW-007** (board issue [#85](https://github.com/drivestream-lab/gateflow/issues/85)). **No product code in this stage.**

---

### Gate check (prior wave)

> W0 is the first wave of this initiative — gate is spec merge + board seed + PE sign-off (§0), not a prior INIT-GATEFLOW-007 Ground Report. Cross-initiative contracts come from INIT-001…006 baselines below.

| Item | Required | Status |
|------|----------|--------|
| Branch context | `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | **ok** — on `develop` @ `560f11f` (merge of PR [#83](https://github.com/drivestream-lab/gateflow/pull/83)) |
| Spec PR merged | Implementation plan on integration branch | **yes** — `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-007.md` on `develop`; spec package merged via PR [#77](https://github.com/drivestream-lab/gateflow/pull/77) |
| Coding-readiness at merge | Merged spec/plan PR had `spec-lgtm` on head | **verified** — PR [#83](https://github.com/drivestream-lab/gateflow/pull/83) MERGED 2026-07-30; label `spec-lgtm`; head `cee50f16…`; merge `560f11f…` |
| Board seed | Wave issue(s) from plan §9 exist; TASK ids present in wave body | **seeded** — EPIC [#84](https://github.com/drivestream-lab/gateflow/issues/84); W0 [#85](https://github.com/drivestream-lab/gateflow/issues/85); W1 [#86](https://github.com/drivestream-lab/gateflow/issues/86); W2 [#87](https://github.com/drivestream-lab/gateflow/issues/87); W0–W2 are **sub-issues of #84** on drivestream-lab Board |
| Plan source freshness | all upstream rows `CURRENT` | **current (Gate 1 WAIVED)** — spec `sha256:1c613846…`; feasibility `sha256:ca40b9e2…`; TDD `sha256:4e681597…` match `shasum -a 256` on disk; impact-map / PRD / scope rows **WAIVED (Q-1)** per plan — not STALE |
| Impact-map repo scope | revision and scope digest match canonical handoff | **WAIVED (Q-1)** — plan documents Gate 1 open; engineering proceed under waive; do not claim formal CURRENT |
| `check_command` | resolved | **`make check`** |
| `test_command` | resolved | **`make test`** |
| `verify_command` | live script under `live_verify_dir` when P15 applies | **resolved** — `.venv/bin/python -m tests.verify.verify_wave_closeout` (co-ship in W0; **file absent on tip — expected pre-`/loop-spec`**) |
| `ground_command` | resolved or N/A | **N/A** — `/ground-spec` orchestrated skill (no Makefile ground target) |
| Co-shipped live verify (P15) | FILE path under `live_verify_dir` when wave adds product surface | **planned** — `tests/verify/verify_wave_closeout.py` (TASK-W0-06; create in `/loop-spec`) |
| Prior wave as-built row | `human_approved` | **N/A for INIT-007 W0** — first wave of initiative |
| Prior Ground Report exists | `reports/Ground-Report-INIT-GATEFLOW-007-W{N-1}.md` | **N/A** — W0; consume cross-initiative contracts below |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | **complete** — 2026-07-29 PE sign-off; regen keeps Accepted TDD/ADR-010; PE re-`spec-lgtm` on PR #83 head |

**Gate verdict:** PASS

---

### Contracts consumed (from prior Ground Report)

> W0 has no INIT-007 predecessor. Sources: `Ground-Report-INIT-GATEFLOW-002-W0/W1`, `Ground-Report-INIT-GATEFLOW-003-W1`, `Ground-Report-INIT-GATEFLOW-005-BOUNDINPUT-W1`, plus as-built / pin for INIT-006 forge (no INIT-006 Ground Report). Confirmed against `src/` and `prayog-skills/workflow.yaml`.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Programme-token lane start enqueue | `WaveStartService` → `_enqueue_wave` | lane body + orchestrated `start_node`; identity + workspace | `WaveStartResponse` with `run_id`; job enqueued | 002-W0 / 006 as-built | **yes** — `start_implement_wave` / `start_spec_wave` on tip |
| Active-run concurrency 409 | `RunRepository.find_active_run` | org + repo + wave/PR scope | existing run or none → `ConflictError` | 002-W0 | **yes** — `_enqueue_wave` raises 409 |
| Orchestrated Enter-at validation | `WorkflowEngine.require_orchestrated_skill` | node id string | void or validation error | 002-W0 / pin | **yes** — closeout must **fix** Enter-at to `learning-extract` (no client `start_node`) |
| Pin Pass-2 walk edges | `prayog-skills/workflow.yaml` nodes | `learning-extract` outcome `pass` | next `ground-spec`; `ground-spec` `pass` → `wave-signoff` | pin SSOT | **yes** — orchestrated + human-checkpoint STOP |
| Multi-hop orchestrator walker | `RunOrchestrator.process_job` | claimed job + pin outcomes | stages until gate / hop cap | 003-W1 | **yes** — Pass-1 unit chain through `live-verify`; Pass-2 chain **not built yet** |
| Stored baton ingest SSOT | `HandoffReader.read_path` | absolute stored path on run | `HandoffEnvelope` or fail closed | 005-W1 | **yes** — no ambient automate SSOT |
| Baton dual-write authority | run-scoped `{GATEFLOW_HANDOFF_ROOT}/{run_id}/handoff.md` | run id + envelope YAML | filesystem baton | ADR-008 / 005-W1 | **yes** — unit isolation green; live empty-baton deferral (D-W0-B1) tracked for pin |
| Forge publish policy | `_publish_stage_workspace_if_needed` | pin node `forge:` + handoff instance slots | commit to run head or fail closed | ADR-009 / 006 as-built | **yes (unit)** — live dogfood **deferred** |
| Programme-token AuthN on `/api/v1/waves/*` | `verify_programme_service_token` + `public_paths` | Bearer header | void or 401 | 001-W1 / ADR-005 | **yes** — `/api/v1/waves` prefix already public |
| Pass-1 implement lane stop | pin + `verify_implement_lane` | Enter-at `pre-implement` | terminal `stopped` @ `live-verify` | #76 / 003-W1 | **yes** — prerequisite for closeout dogfood (W2 depth) |

**Unconfirmed contracts** (W0 implementation scope or live-deferred baselines):

- `POST /api/v1/waves/closeout/start` + `CloseoutWaveStartRequest` (REQ-1, REQ-4) — **not implemented**
- `WaveStartService.start_closeout_wave` fixed Enter-at `learning-extract`; reject client `start_node` (REQ-2, REQ-5) — **not implemented**
- Pass-2 unit walker: `learning-extract` → `ground-spec` → stop `wave-signoff`; no auto `verify` (REQ-7) — **not implemented**
- Co-shipped smoke script `tests/verify/verify_wave_closeout.py` (REQ-1, REQ-7, P15) — **not on tip**
- Learning Postgres ingest hook after learning-extract hop (REQ-9) — **W1 scope**; do not assume in W0 walker tests beyond stub/mock
- INIT-006 live forge / authorize dogfood — **live unconfirmed**; unit contracts sufficient for W0 coding
- Pin packaged skill baton write on Cursor success (D-W0-B1) — **live risk** for full Pass-2; W0 smoke may soft-skip deeper stages per plan

→ Treat unconfirmed rows as **implementation scope**, not assumed baselines.

---

### Must read

- [ ] `AGENTS.md`
- [ ] MDC rules (domain-filtered for W0):
  - [ ] `architecture.mdc` — route mount, `public_paths`, layering
  - [ ] `http-api-conventions.mdc` — POST body models; programme-token mutations
  - [ ] `pydantic-schemas.mdc` — closeout models in `src/models/`; `extra=forbid`
  - [ ] `fail-fast.mdc` — 400/409 fail closed; no silent enqueue
  - [ ] `dependency-injection.mdc` — service wiring for closeout path
  - [ ] `testing-verify-flows.mdc` — co-ship live script; smoke vs W2 dogfood depth
  - [ ] `repository-pattern.mdc` — RunStore via repos (background for 409)
  - [ ] `logging-loguru.mdc` — structured kwargs on wave/closeout paths
  - skipped: `database-migrations.mdc` — no agent Alembic in W0; `infra-services.mdc` — no new adapters
- [ ] ADRs (keyword-matched):
  - [ ] ADR-001 — Postgres RunStore SSOT (background)
  - [ ] ADR-005 — programme-token control-plane mutations (closeout route)
  - [ ] ADR-007 — invocation brief / bind vars for `learning-extract`
  - [ ] ADR-008 — stored baton ingest authority
  - [ ] ADR-009 — pin forge publish (`learning-extract` optional; `ground-spec` required)
  - [ ] ADR-010 — **closeout intake §6** (third start contract; fixed Enter-at; new run + PR bind)
- [ ] Spec: `docs/specification/product/INIT-GATEFLOW-007-gateflow.md` (REQ-1…8, REQ-13, REQ-16, REQ-17 for W0)
- [ ] Plan wave section: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-007.md` Phase W0
- [ ] TDD: `docs/specification/reports/Technical-Review-INIT-GATEFLOW-007.md` (closeout body + walker)
- [ ] Board wave issue: [#85](https://github.com/drivestream-lab/gateflow/issues/85) — TASK list:
  - [ ] TASK-W0-01 — implements REQ-4, REQ-6, REQ-13 — CloseoutWaveStartRequest; forbid `start_node`/meta
  - [ ] TASK-W0-02 — implements REQ-1 — POST route + programme token
  - [ ] TASK-W0-03 — implements REQ-2, REQ-3, REQ-5, REQ-8, REQ-13 — `start_closeout_wave` enqueue
  - [ ] TASK-W0-04 — implements REQ-7, REQ-8 — unit Pass-2 walker to `wave-signoff`
  - [ ] TASK-W0-05 — implements REQ-16 — retarget unit mocks off `wave-human-decision`
  - [ ] TASK-W0-06 — implements REQ-1, REQ-7, REQ-17 — co-ship `verify_wave_closeout` smoke
  - [ ] TASK-W0-07 — implements REQ-17 — as-built W0 + README smoke vs W2 note

---

### Governance alignment

- [ ] Slice spec does not contradict any listed Accepted ADR
- [ ] Plan TASK MDC notes and ADR notes for W0 reviewed (TASK-W0-01…07)
- [ ] ADR-010 amendment (**Accepted**) governs closeout intake — no ADR-011
- [ ] Gate 1 Q-1 waive recorded — do not fake impact-map CURRENT in docs

---

### Must update (in the same change as the code)

- [ ] Product spec — only if implementation drifts REQ contracts (prefer no drift)
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-007 W0 rows (TASK-W0-07)
- [ ] `tests/README.md` — feature map: `verify_wave_closeout` smoke row (W0 create; W2 deepen)
- [ ] `tests/config.yaml.example` — closeout smoke knobs (TASK-W0-06)
- [ ] Unit — closeout models, route auth, service happy/400/409, Pass-2 walker, mock hygiene
- [ ] Live — create `tests/verify/verify_wave_closeout.py` smoke (401, validation, happy enqueue → `run_id`; soft-skip deeper Pass-2 without tip/worker)
- [ ] ADR — none expected; ADR-010 already Accepted with closeout §6

---

### Must not

- [ ] Implement against spec wording that contradicts Accepted ADR-010 closeout authority without superseding ADR
- [ ] Allow client-chosen `start_node` on closeout route (REQ-2)
- [ ] Resume a stopped Pass-1 run for Pass-2 (REQ-3 — always new run)
- [ ] Duplicate full HTTP journeys in pytest when verify script owns smoke path
- [ ] Use `{test_command}` / `make test` as live `verify_command` at `live-verify` (P15)
- [ ] Agent-author Alembic under `postgres_migrations/versions/` (W1 human migration)
- [ ] Assume learning DB ingest exists in W0 (W1 scope)

---

### Verification plan

| Layer | What it proves | Command (from plan / profile) |
|-------|----------------|--------------------------------|
| Static check | black, ruff, pyright, import-linter | `make check` |
| Unit | closeout models, route, service, Pass-2 walker, mock hygiene | `make test` |
| Live verify | closeout HTTP surface smoke (P15); human-run at `live-verify` | `.venv/bin/python -m tests.verify.verify_wave_closeout` — path `tests/verify/verify_wave_closeout.py` |
| Ground check | W0 REQs + boundaries | `/ground-spec` (no Makefile `ground_command`) |

> P15 applies: W0 **must** co-ship live script. N/A or unit-only for live verify **blocks** the gate. Agent implements script in `/loop-spec`; does **not** run it as skill success.

### Human live-verify (after loop-spec)

When checklist PASS and coding is green, the human at checkpoint `live-verify`:

- [ ] Run `.venv/bin/python -m tests.verify.verify_wave_closeout` (co-shipped smoke) against running API (+ worker if smoke asserts enqueue processing)
- [ ] Inspect closeout accept path: 401 without token, body validation, happy enqueue → `run_id`
- [ ] Paste exit evidence (command + exit code / key output) on issue #85 or PR
- [ ] Apply tip hygiene for any hotfixes before Enter-at Pass-2 closeout (W2 dogfood)

---

### Tracker / PR

- Initiative: **INIT-GATEFLOW-007**
- EPIC: [#84](https://github.com/drivestream-lab/gateflow/issues/84)
- Issue: [#85](https://github.com/drivestream-lab/gateflow/issues/85) (W0)
- Branch (plan): `feature/INIT-GATEFLOW-007-w0-closeout-start`
- Spec path: `docs/specification/product/INIT-GATEFLOW-007-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_wave_closeout`
- ADRs in scope: ADR-001, ADR-005, ADR-007, ADR-008, ADR-009, ADR-010

---

### Merge order (if cross-module / cross-service)

N/A — single repo `drivestream-lab/gateflow`. Internal order per plan: models → route + `public_paths` → `start_closeout_wave` service → Pass-2 walker unit tests → mock hygiene → co-ship verify script → as-built/README. W1 blocked on W0 merge (DEP-2). Full Pass-2 dogfood depth deferred to W2 (DEP-4).

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-Checklist-INIT-GATEFLOW-007-W0.md
    digest: sha256:19b5100adf7fe6f85299ac02d471f741aeeffee9d6243d03c3556fedc6c9aede
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-007
    wave: W0
    ticket_id: 85
    board_epic: https://github.com/drivestream-lab/gateflow/issues/84
    board_issue: https://github.com/drivestream-lab/gateflow/issues/85
    spec_pr: https://github.com/drivestream-lab/gateflow/pull/77
    plan_pr: https://github.com/drivestream-lab/gateflow/pull/83
    branch: feature/INIT-GATEFLOW-007-w0-closeout-start
    tasks:
      - TASK-W0-01
      - TASK-W0-02
      - TASK-W0-03
      - TASK-W0-04
      - TASK-W0-05
      - TASK-W0-06
      - TASK-W0-07
    implements_req:
      - REQ-1
      - REQ-2
      - REQ-3
      - REQ-4
      - REQ-5
      - REQ-6
      - REQ-7
      - REQ-8
      - REQ-13
      - REQ-16
      - REQ-17
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_wave_closeout
    live_verify_path: tests/verify/verify_wave_closeout.py
    ground_command: N/A — /ground-spec skill
    gate_verdict: PASS
    pe_signoff: complete
    board_seed: complete
    source_freshness: CURRENT_WAIVED_Q1
    p15: co-ship_smoke_w0
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
```

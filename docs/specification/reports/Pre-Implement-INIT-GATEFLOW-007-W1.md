## Pre-implement — gateflow / W1 — Learning Postgres ingest

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-007-W1.md` |
| Initiative | INIT-GATEFLOW-007 |
| Orchestrator initiative | INIT-VFYPR-9492359 |
| Orchestrator ticket | 8996322 |
| Wave | W1 |
| Date | 2026-08-01 |
| Outcome | `blocked` |
| Outcome reason | Plan §9 WorkManifest fails `prayog/v1` contract (40 errors: `launchpad/v1`, forbidden `status`, missing `exit`/`files`/`verification` on all waves); `/loop-spec` must not proceed until §9 regenerated |
| Wave head context | Bound by Forge/human context: `feature/INIT-GATEFLOW-007-w1-learning-ingest` @ `317f5c5` — **not** opened by this skill; Draft PR [#102](https://github.com/drivestream-lab/gateflow/pull/102) OPEN |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — `feature/INIT-GATEFLOW-007-w1-learning-ingest` @ `317f5c5` |
| Spec PR merged | Implementation plan on integration branch | [x] yes — PR [#83](https://github.com/drivestream-lab/gateflow/pull/83) MERGED to `develop` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — label `spec-lgtm`; merge `560f11f` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#84](https://github.com/drivestream-lab/gateflow/issues/84); W0 [#85](https://github.com/drivestream-lab/gateflow/issues/85); W1 [#86](https://github.com/drivestream-lab/gateflow/issues/86); W2 [#87](https://github.com/drivestream-lab/gateflow/issues/87) |
| WorkManifest contract | `prayog/v1` §9 passes `prayog-skills/scripts/workmanifest_contract.py` | [ ] **fail** — 40 errors (see below) |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` | [ ] **missing** — all 16 tasks lack `exit` mapping |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` | [x] N/A — W1 adds no new HTTP/lane-start surface (plan §Phase W1; P15 N/A) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — Gate 1 digests **WAIVED** (Q-1); feasibility + TDD CURRENT |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — **WAIVED** (Q-1) per plan §Source freshness |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies; else command or N/A with reason | [x] N/A — P15 N/A for W1; ingest proven by unit; live ingest evidence deferred to W2 dogfood |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` is Pass-2 pin skill (orchestrated) |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` listed | [x] N/A — no new product surface this wave |
| Prior wave as-built row | `human_approved` | [x] W0 = **human_approved** — merged [#101](https://github.com/drivestream-lab/gateflow/pull/101) @ `e1604fd` |
| Prior Ground Report exists | `reports/Ground-Report-INIT-GATEFLOW-007-W{N-1}.md` | [x] exists — `Ground-Report-INIT-GATEFLOW-007-W0.md` (outcome **pass**) |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W1 |

**WorkManifest validator output (fail closed):**

```
WorkManifest contract FAILED (40 error(s))
  [identity] apiVersion must be 'prayog/v1'; got 'launchpad/v1'
  [mutable_field] defaults.status / work[*].status forbidden
  [exit] work[W0..W2].tasks[*].exit: exit mapping is required (16 tasks)
  [files] work[W0..W2].tasks[*].files: files is required (16 tasks)
  [verification] work[0..2].verification: verification mapping is required (3 waves)
```

Command: `python prayog-skills/scripts/workmanifest_contract.py docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-007.md`

Reference shape: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-008.md` §9 (`apiVersion: prayog/v1` with per-task `files`, `exit`, wave `verification`). Closed PR [#100](https://github.com/drivestream-lab/gateflow/pull/100) (prayog/v1 backfill) was **not merged** — §9 on `develop` remains `launchpad/v1`.

**Process note:** W1 code and Draft PR #102 already exist on the bound head (likely `/loop-spec` ran ahead of a clean pre-implement gate). WorkManifest contract failure still **blocks** formal `/loop-spec` authorization per pin P16 — regenerate §9 before treating this wave as gate-clean.

**Gate verdict:** **BLOCKED** — §9 must be regenerated to `prayog/v1` before `/loop-spec` may proceed on a clean gate.

**Forge readiness (when seed / wave head absent):** Board seeded; wave head bound. No branch/ticket mutation from this skill.

---

### Contracts consumed (from prior Ground Report)

> Read `Ground-Report-INIT-GATEFLOW-007-W0.md` §Contracts produced.
> Scan `source_roots` to confirm — not spec text alone.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Closeout start HTTP | `POST /api/v1/waves/closeout/start` | `CloseoutWaveStartRequest` + programme token | `WaveStartResponse` | Ground-Report-W0; `src/api/v1/waves_routes.py` | [x] yes |
| Closeout body | `CloseoutWaveStartRequest` | identity + required `pr_number` + absolute workspace + branch targeting + runner/model; optional `prior_run_id` | validated model | Ground-Report-W0; `src/models/wave_start_models.py` | [x] yes — `extra=forbid`; no client `start_node`/meta |
| Closeout accept | `start_closeout_wave` | closeout request | new ACTIVE run + job; baton path | Ground-Report-W0; `src/business_services/wave_start_service.py` | [x] yes — fixed Enter-at; ACTIVE → 409 |
| Fixed Enter-at constant | `CLOSEOUT_START_NODE` | — | `"learning-extract"` | Ground-Report-W0; `wave_start_models.py` | [x] yes |
| Pass-2 pin graph | pin + `WorkflowEngine` | handoff stage+outcome after learning-extract / ground-spec | next ground-spec / wave-signoff | Ground-Report-W0; unit pin tests | [x] yes — verify stays manual |
| Closeout smoke verify | `tests/verify/verify_wave_closeout` | `features.wave_closeout` config | exit 0 smoke | Ground-Report-W0 | [x] yes — module present on tip |

**Unconfirmed contracts** (prior wave not yet grounded or source not found):

- None for W1 — W0 Ground Report §Contracts produced complete and source scan confirms entry points.

---

### Must read

- [x] `AGENTS.md` — constitution pin, programme board, verify commands
- [x] MDC rules (domain-filtered — W1 touches data layer, DI, schemas, fail-fast, migrations):
  - [x] `repository-pattern.mdc` — business → repository → schema layering
  - [x] `database-migrations.mdc` — human-owned `versions/`; agent updates schema + `env.py` only
  - [x] `pydantic-schemas.mdc` — models in `src/models/`; service APIs use Pydantic
  - [x] `dependency-injection.mdc` — DI bind for repositories/services
  - [x] `fail-fast.mdc` — ingest fail-closed on malformed YAML / unknown class
  - [x] `architecture.mdc` — layer boundaries (orchestrator hook placement)
  - [ ] skipped — `http-api-conventions.mdc` (no new HTTP this wave)
  - [ ] skipped — `testing-verify-flows.mdc` (P15 N/A; W2 extends W0 script)
- [x] ADRs (keyword-matched — learning ingest, Postgres, orchestrator ordering, closeout):
  - [x] ADR-001 — Postgres SSOT; human Alembic; repository boundary
  - [x] ADR-003 — slot/layer ownership (repository vs service)
  - [x] ADR-008 — baton dual-write; packaged ingest uses stored path
  - [x] ADR-009 — forge publish vs worker ingest ordering
  - [x] ADR-010 — closeout Enter-at `learning-extract`; W1 hook after that hop
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-007-gateflow.md` — REQ-9…REQ-12, REQ-17
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-007.md` W1
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/86 — TASK list (projected from plan §2; manifest lacks prayog/v1 exit proof):
  - [ ] TASK-W1-01 — implements REQ-9, REQ-10 — ORM + Pydantic learning models; `env.py` import
  - [ ] TASK-W1-02 — implements REQ-9 — **Human** Alembic revision (`./scripts/run_postgres_migration.sh`)
  - [ ] TASK-W1-03 — implements REQ-9, REQ-10, REQ-11 — `LearningRepository` + `LearningIngestService`; DI bind
  - [ ] TASK-W1-04 — implements REQ-9, REQ-11, REQ-12 — orchestrator hook after learning-extract hop (publish → ingest before ground-spec)
  - [ ] TASK-W1-05 — implements REQ-17 — as-built W1 + README learning note

---

### Governance alignment

- [x] Slice spec does not contradict any listed ADR
- [x] Plan TASK MDC notes and ADR notes for W1 reviewed (repository-pattern, database-migrations, pydantic-schemas, dependency-injection, fail-fast; ADR-001, ADR-003, ADR-009)
- [x] Every initiative ADR cited for this wave is **Accepted** in `docs/specification/adr`

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — `docs/specification/product/INIT-GATEFLOW-007-gateflow.md` — only if REQ wording drifts (unlikely)
- [ ] `docs/specification/as-built/implementation-status.md` — W1 learning ingest row
- [ ] `tests/README.md` — learning ingest feature-map note (live evidence W2)
- [ ] Unit verification scope — `tests/unit/test_learning_ingest.py` edges (parse, upsert, orchestrator order, H6)
- [ ] Live verification — N/A this wave (P15 N/A); W2 extends `verify_wave_closeout` for ingest rows
- [ ] ADR — none expected (ADR-010 closeout already Accepted)

---

### Must not

- [ ] Implement against spec wording that contradicts an Accepted ADR without superseding that ADR
- [ ] Duplicate unit verification assertions in live-verify scripts
- [ ] Assume a contract from a prior wave is correct without checking the Ground Report (W0 contracts confirmed above)
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Agent-commit Alembic revisions under `postgres_migrations/versions/` (human-owned per `database-migrations.mdc`)
- [ ] Treat skill HTTP as ingest success path (REQ-11 / pin H6)

---

### Verification plan

| Layer | What it proves | Command (from tests_readme / profile) |
|-------|----------------|---------------------------------------|
| Static check | Formatting, linting, types | `make check` |
| Unit | Learning parse/upsert, orchestrator hook order, fail-closed YAML/class | `make test` (incl. `tests/unit/test_learning_ingest.py`) |
| Live verify | Product behaviour on running stack | N/A — P15 N/A for W1; full ingest live evidence in W2 `verify_wave_closeout` dogfood |
| Ground check | Assigned wave REQs satisfied | N/A — `/ground-spec` at Pass-2 closeout |
| Migration | DDL applied for learning tables | `./scripts/run_postgres_migration.sh` (**human**) — revision `cc5feda8fe3d` present on tip |

> When P15 applies: N/A or unit-only for live verify **blocks** the gate. W1 is explicitly P15 N/A per plan.

### Human live-verify (after loop-spec)

W1 has no co-shipped live script. Human live-verify for learning ingest rows is deferred to W2 dogfood (`verify_wave_closeout` depth). At W1 `/loop-spec` completion, human still runs unit + migration apply locally.

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-007
- Issue: #86 (W1)
- EPIC: #84
- Spec path: `docs/specification/product/INIT-GATEFLOW-007-gateflow.md`
- Verify command (human): N/A — unit + W2 dogfood
- ADRs in scope: ADR-001, ADR-003, ADR-008, ADR-009, ADR-010
- Wave head: `feature/INIT-GATEFLOW-007-w1-learning-ingest` @ `317f5c5` — Draft PR #102

---

### Remediation (before re-run `/pre-implement` → `pass`)

1. Run `/spec-implementation-plan` (or PE-directed §9-only regen) to replace plan §9 with `apiVersion: prayog/v1`, per-task `files` + `exit`, wave `verification`, no forbidden `status` fields — mirror `Implementation-Plan-INIT-GATEFLOW-008.md` §9 shape.
2. Merge plan update with `spec-lgtm` if on a spec branch (PR #100 pattern was closed unmerged).
3. Re-run `python prayog-skills/scripts/workmanifest_contract.py docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-007.md` — must exit 0.
4. Re-run `/pre-implement` for W1 → expect `pass` → `/loop-spec` with `commit_workspace` on checklist.

---

### Checklist publish readiness (blocked — no commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `blocked` — WorkManifest contract fail (40 errors) |
| Next | `wave-signoff` (`human-checkpoint`) — PE/engineering decision on §9 regen |
| Forge (this hop) | **disabled** — do not publish blocked checklist to wave head |
| After unblock | `pass` → `loop-spec` with `commit_workspace` **required** on checklist |

Recommend `/commit-workspace` only after explicit authorization **and** gate `pass`. Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

W0 closeout API + smoke verify **human_approved** on `develop` @ `e1604fd` — prerequisite satisfied. W1 ingest hook runs after W0 closeout Enter-at `learning-extract` hop. W2 dogfood depends on W1 human Alembic + unit-green ingest.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: blocked
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-007-W1.md
    digest: sha256:02cae579d3a44c9d1d8337de586a901b2e2dc40f0118a1ce584090119c9422c6
  blockers:
    - TASK-W1-01
    - TASK-W1-02
    - TASK-W1-03
    - TASK-W1-04
    - TASK-W1-05
  signals:
    initiative: INIT-GATEFLOW-007
    orchestrator_initiative: INIT-VFYPR-9492359
    orchestrator_ticket: "8996322"
    wave: W1
    board_issue: "86"
    board_issue_url: https://github.com/drivestream-lab/gateflow/issues/86
    task_ids:
      - TASK-W1-01
      - TASK-W1-02
      - TASK-W1-03
      - TASK-W1-04
      - TASK-W1-05
    epic: "84"
    workmanifest_contract: fail
    workmanifest_errors: 40
    workmanifest_api_version: launchpad/v1
    required_api_version: prayog/v1
    p15: N/A
    check_command: make check
    test_command: make test
    verify_command: "N/A — P15 N/A (no new HTTP surface); unit + W2 dogfood"
    head_ref: feature/INIT-GATEFLOW-007-w1-learning-ingest
    head_sha: 317f5c586675cafd17ec31da4771b3a39808a7f5
    draft_pr: "102"
    prior_wave: W0
    prior_wave_status: human_approved
    prior_ground_report: Ground-Report-INIT-GATEFLOW-007-W0.md
    loop_spec_ahead: true
    remediation: spec-implementation-plan-regen-section-9
  next_candidates:
    - wave-signoff
  human_checkpoint: true
  external_action: false
```

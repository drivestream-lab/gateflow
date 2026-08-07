## Pre-implement — gateflow / W1 — Check persistence + composed readout

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W1.md` |
| Initiative | INIT-GATEFLOW-011 |
| Wave | W1 |
| Date | 2026-08-07 |
| Outcome | `pass` |
| Outcome reason | W1 gate checks pass: prior W0 `human_approved` (wave-accepted on tip `088d125`) with Ground-Report-W0 §Contracts produced complete; spec PR #159 merged with `spec-lgtm`; board seeded (EPIC #160 / W1 #162 with TASK-W1-01…05); WorkManifest contract clean; P15 live verify command resolved; H1–H3 spend fresh on `develop`. |
| Wave head context | Bound by Forge/human context: `develop` @ `234f66a1b4d5e9d34522cb6bceb016c5672626a4` — not opened by this skill; planned coding branch `feature/INIT-GATEFLOW-011-w1-checkpoint-persistence` (cut in `/loop-spec`) |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — `develop` @ `234f66a` (not `chore/INIT-GATEFLOW-011-spec-gateflow`) |
| Spec PR merged | Implementation plan on integration branch | [x] yes — [#159](https://github.com/drivestream-lab/gateflow/pull/159) MERGED 2026-08-07; plan on `develop` @ `234f66a` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — label `spec-lgtm` on #159; Approve @ `c5047ea` (plan present); merge commit `234f66a…` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#160](https://github.com/drivestream-lab/gateflow/issues/160); W1 [#162](https://github.com/drivestream-lab/gateflow/issues/162) lists TASK-W1-01…05; sub-issue of EPIC; `Board-Seed-INIT-GATEFLOW-011.md` B1–B8 PASS |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `python prayog-skills/scripts/workmanifest_contract.py …/Implementation-Plan-INIT-GATEFLOW-011.md` → "WorkManifest contract passed." |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [x] complete — W1 TASK-W1-01…05 in plan §9 (lines 946–1035) |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` (not unit-as-live) | [x] contract — `verification.live.applicable: true`; command `.venv/bin/python -m tests.verify.verify_checkpoint_history` (FILE co-shipped in TASK-W1-05; script absent today — expected until `/loop-spec`) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — plan §Source freshness CURRENT; live digests match (spec `0edf9b72…`, feas `61cd10b2…`, TDD `aa68a3c6…`) |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — product spec H1 `sha256:eca06cbe…`, H2 `sha256:afdc7bd5…`, H3 revision `1`, G1 `f3da8148…` unchanged on `develop` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies; else command or N/A with reason | [x] `.venv/bin/python -m tests.verify.verify_checkpoint_history` |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` is Pass-2 pin skill, not a Makefile target |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` listed | [x] `tests/verify/verify_checkpoint_history.py` (create in TASK-W1-05) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] W0 = `human_approved` — as-built `implementation-status.md` (INIT-GATEFLOW-011 W0 row); `wave-accepted` on tip `088d125` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] exists — `Ground-Report-INIT-GATEFLOW-011-W0.md` (2026-08-07; outcome `pass`; §Contracts produced complete) |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W1 (not first wave); gate is prior-wave Ground Report + human_approved |

**Gate verdict:** PASS — W1 pre-flight gates satisfied; ready for `/loop-spec` after checklist publish.

**Board process note (read-only):** Wave ticket [#162](https://github.com/drivestream-lab/gateflow/issues/162) programme-board Status is **Todo** (not In Progress). Pin chain `wave-in-progress-action` → `pre-implement` is an automated orch hop; this skill does not mutate board status. Signal only — does not fail the gate table above.

**Forge readiness (when seed / wave head absent):** not required — seed complete; head bound to `develop`. Planned coding branch per plan: `feature/INIT-GATEFLOW-011-w1-checkpoint-persistence` (opened in `/loop-spec`, not here).

---

### Contracts consumed (from prior Ground Report)

> Read `Ground-Report-INIT-GATEFLOW-011-W0.md` §Contracts produced.
> For each contract this slice depends on, confirm the actual built interface
> matches what this wave's spec assumes. Scan `src/` to confirm — do not rely
> on spec text alone.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Live CAP-01 evaluate (W1 wraps with persist + stale) | `CheckpointEvidenceService.evaluate` | `checkpoint_id: str`, `pr_ref: CheckpointPrRef` (owner/repo/number) | `CheckpointStatusResult` (verdict ∈ {satisfied, not_satisfied, could_not_verify}, `checked_sha`, `checked_at`, `missing_items[]`) | Ground-Report-W0; `src/business_services/checkpoint_evidence_service.py:42` | [x] yes — present; W1 adds persist (TASK-W1-01) + stale (TASK-W1-02) around same evaluate |
| Pin checkpoint vocabulary (W1 reuses; stale uses head SHA vs evidence timing) | `WorkflowEngine.get_github_checkpoint_vocab` | pinned delivery-contract at process tip | `CheckpointGithubVocab` → six checkpoint ids → labels + review_roles + required check-runs | Ground-Report-W0; `src/business_services/workflow_engine.py:129` | [x] yes — present; no per-phase hardcoding |
| ForgeClient evidence reads (W1 unchanged read surface) | `ForgeClient.list_reviews` / `list_check_runs` / `get_pull_request` | org, repo, pr_number / head SHA | review / check-run / PR documents (incl. merge fields) | Ground-Report-W0; `src/infra_services/forge_client.py:427/445/466` | [x] yes — read methods present; W1 must not add write APIs on CAP-01 path (REQ-05/28) |
| HTTP status surface (W1 adds `/history` + composed readout under same prefix) | `GET /api/v1/checkpoints/status` | query: checkpoint_id, owner, repo, pr_number + programme token | `CheckpointStatusResult` JSON | Ground-Report-W0; `src/api/v1/checkpoints_routes.py:15`; `/api/v1/checkpoints` on `public_paths` (`src/app.py:85`) | [x] yes — `/status` present; `/history` absent today (W1 TASK-W1-03); composed readout route absent (W1 TASK-W1-04) |
| Live verify CAP-01 (W1 adds `verify_checkpoint_history`) | `tests/verify/verify_checkpoint_status.py` | programme knobs; optional `GATEFLOW_CHECKPOINT_PR` | exit 0 under prereqs | Ground-Report-W0; `tests/verify/verify_checkpoint_status.py` | [x] yes — present; W1 co-ships `verify_checkpoint_history.py` (TASK-W1-05) |
| Run-event persistence surface (W1 adds `checkpoint_check` event type) | `RunEventRepository.append_event` | `RunEventCreate` (run_id, `event_type`, payload) | `RunEventModel` | as-built INIT-001/006; `src/database/postgres/repository/run_store_repository.py:287`; `src/models/run_store_models.py:148`; `src/models/policy_types.py:25` (`RunEventNameType`) | [x] yes — append_event + RunEventCreate + RunEventNameType enum present; W1 TASK-W1-01 extends enum + payload |
| Programme-token control-plane auth (W1 reuses for new GET routes) | `verify_programme_service_token` + `public_paths` | Bearer programme token | void / 401 | ADR-005; `src/api/v1/programme_token.py`; `src/app.py` | [x] yes — pattern live; `/api/v1/checkpoints` already on `public_paths` (W0) |

**Unconfirmed contracts** (prior wave not yet grounded or source not found):
- None blocking W1 — all W0 contracts consumed are confirmed in source; the run-event persistence surface is as-built from prior INITs (not a W0 contract, but a stable prior capability W1 extends).
- W1 does **not** depend on W2+ (initiative read-out, wave map, etc.) — those are later waves.

### Must read

- [x] `AGENTS.md` — constitution pin (`v0.5.0-rc.2`), programme board (drivestream-lab Board), verify command pointers, delivery bootstrap
- [x] MDC rules (domain-filtered — files read for this slice's domains):
  - [x] `.cursor/rules/architecture.mdc` — layered `api` → `business_services` → `database.repository` → `database.schema`; W1 reintroduces persistence (TASK-W1-01 touches repository + ORM-adjacent models)
  - [x] `.cursor/rules/repository-pattern.mdc` — W1 modifies `run_store_repository.py` (ORM confined to repo); business service exchanges Pydantic with repo; no ORM in `checkpoint_evidence_service.py`
  - [x] `.cursor/rules/pydantic-schemas.mdc` — checkpoint DTOs + run-event payload in `src/models/` only; `RunEventNameType` enum with `Type` suffix; `extra="forbid"` for internal DTOs
  - [x] `.cursor/rules/http-api-conventions.mdc` — `GET /checkpoints/history` + composed readout use query params (filters); no write bodies; path identifies resource where applicable
  - [x] `.cursor/rules/fail-fast.mdc` — stale evidence → `not_satisfied` (never silent pass); GitHub down → `could_not_verify`; 404 `no run found for this wave` distinct from malformed id
  - [x] `.cursor/rules/infra-services.mdc` — ForgeClient read-only surface unchanged; no new infra service this wave
  - [x] `.cursor/rules/dependency-injection.mdc` — `CheckpointEvidenceService` already registered (W0); W1 may add repo dependency via constructor `@inject` (RepositoryModule provider for session factory)
  - [x] `.cursor/rules/strong-typing.mdc` — `checked_sha`/`checked_at` typed (`Optional[str]` / `datetime`); verdict enum; no `dict` at service boundary
  - [x] `.cursor/rules/testing-verify-flows.mdc` — co-ship `tests/verify/verify_checkpoint_history.py`; feature-map row in `tests/README.md`; unit owns persist/stale logic, live owns smoke
  - [x] `.cursor/rules/spec-driven-development.mdc` — same-PR as-built row (TASK-W1-05) + product spec as-built baseline after W1
  - [ ] `.cursor/rules/database-migrations.mdc` — review only if W1 adds a column/table; plan TASK-W1-01 modifies `policy_types.py` (enum) + `run_store_models.py` (payload) — **no new ORM table / no Alembic revision expected** (reuses existing `run_events` table + JSONB payload); if a column is needed, agent updates `schema/` + `env.py` only and **describes** DDL for human migration (do not commit `versions/`)
  - [ ] `.cursor/rules/logging-loguru.mdc` — skipped beyond inherited service logger (no new observability surface; persist path uses `self.logger` kwargs for checkpoint_id/checked_sha/verdict)
- [x] ADRs (keyword-matched — checkpoint persistence, ForgeClient read, programme token, pin SSOT, run store):
  - [x] ADR-001 — runtime + durable store (**Accepted**; W1 persists check records into existing `run_events` store — cite only; no new store)
  - [x] ADR-003 — ForgeClient in infra; evidence orchestration in business (**Accepted**; W1 unchanged read surface)
  - [x] ADR-004 — programme config authority (**Accepted**; pin consume-only)
  - [x] ADR-005 — programme-token control-plane reads/writes zone; `public_paths` allowlist (**Accepted**; new GET routes under existing `/api/v1/checkpoints` prefix already on `public_paths`)
  - [x] ADR-009 — pin `forge:` mutate authority; CAP-01 must not call write Forge actions (**Accepted**; persist path must not add Forge writes)
  - [x] ADR-010 — lane intake authority (**Accepted**; not directly touched by W1 — cite only)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` — W1 REQs REQ-03, REQ-06, REQ-07, REQ-08 (+ REQ-28 global guard); negative/failure paths table (stale, 404 no run, GitHub down)
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-011.md` W1 (lines 161–200, 940–1069)
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/162 — TASK list (projected from WorkManifest; not a second authority):
  - [ ] TASK-W1-01 — implements REQ-06 — depends_on: [] — files: `policy_types.py`, `run_store_models.py`, `run_store_repository.py`, `checkpoint_evidence_service.py`, `test_checkpoint_persistence.py` (create) — exit proof: `make test` exit 0
  - [ ] TASK-W1-02 — implements REQ-03 — depends_on: [TASK-W1-01] — files: `checkpoint_evidence_service.py`, `test_checkpoint_evidence.py` — exit proof: `make test` exit 0
  - [ ] TASK-W1-03 — implements REQ-07, REQ-28 — depends_on: [TASK-W1-01] — files: `checkpoints_routes.py`, `test_checkpoints_api.py` — exit proof: `make test` exit 0
  - [ ] TASK-W1-04 — implements REQ-08, REQ-28 — depends_on: [TASK-W1-02, TASK-W1-03] — files: `checkpoint_evidence_service.py`, `checkpoints_routes.py`, `test_checkpoints_api.py` — exit proof: `make test` exit 0
  - [ ] TASK-W1-05 — implements REQ-03, REQ-06, REQ-07, REQ-08, REQ-28 — depends_on: [TASK-W1-04] — files: `verify_checkpoint_history.py` (create), `tests/README.md`, `implementation-status.md` — exit proof: `make check && make test` (+ human live verify at wave-acceptance)

---

### Governance alignment

- [x] Slice spec does not contradict any listed ADR — GET-only CAP-01/02; zero mutate from new path (ADR-009/005); persistence reuses existing durable store (ADR-001)
- [x] Plan TASK MDC notes and ADR notes for W1 reviewed (architecture, http-api-conventions, pydantic-schemas, fail-fast; ADR-001/003/005/009)
- [x] Every initiative ADR cited for W1 is **Accepted** in `docs/specification/adr/` (zero NEW-ADR from TDD; W1 introduces no new architectural decision)

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` as-built baseline after W1 exit (persistence + history + composed readout live)
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-GATEFLOW-011 W1 verification row (REQ-03/06/07/08/28)
- [ ] `tests/README.md` — feature-map row for `verify_checkpoint_history` (CAP-02 persistence + composed readout)
- [ ] Unit verification scope — `test_checkpoint_persistence` (create), `test_checkpoint_evidence` (stale), `test_checkpoints_api` (history + composed 404); edges: stale-never-pass, 404 `no run found for this wave` distinct from malformed id, GitHub down → `could_not_verify`, history records marked historical
- [ ] Live verification — co-shipped `tests/verify/verify_checkpoint_history.py` (human-run at `wave-acceptance`); smoke only — does not duplicate unit assertions
- [ ] ADR — no supersede required (ADR_REQUIRED=0 for W1)

---

### Must not

- [ ] Implement against spec wording that contradicts an Accepted ADR without first superseding that ADR
- [ ] Duplicate unit verification assertions in live smoke scripts (unit owns persist/stale logic; live owns smoke on running stack)
- [ ] Assume a contract from a prior wave is correct without checking the Ground Report (or flagging it as unconfirmed above)
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Call `apply_labels`, review create/update, merge, or `update_board_status` from any CAP-01/02 path (REQ-05 / REQ-28)
- [ ] Substitute a historical record for a live verdict when the caller needs a current decision (REQ-07)
- [ ] Report stale evidence as `satisfied` — new commits since approval → `not_satisfied` with reason `stale — new commits since approval` (REQ-03)
- [ ] Commit any file under `postgres_migrations/versions/` (human-only; agent updates `schema/` + `env.py` and describes DDL if needed)

---

### Verification plan

| Layer | What it proves | Command (from tests_readme / profile) |
|-------|----------------|---------------------------------------|
| Static check | Formatting, linting, types, import layers | `make check` |
| Unit | Persist `checkpoint_check` run_event on every evaluate; stale → `not_satisfied` + reason; `checked_sha`/`checked_at` always present; history marks records historical; composed readout via initiative+wave; 404 `no run found for this wave` distinct from malformed id; non-GET rejected | `make test` |
| Live verify | Product behaviour on running stack (human-run at `wave-acceptance`) — persist/stale/404 smoke | `.venv/bin/python -m tests.verify.verify_checkpoint_history` |
| Ground check | Assigned wave REQs satisfied; boundaries respected | N/A — `/ground-spec` Pass-2 pin skill after learning-extract |

> When P15 applies: N/A or unit-only for live verify **blocks** the gate.
> Agent implements the script in `/loop-spec`; does **not** run it as success.
> Policy: live-smoke-policy (P15 applicable — new GET surface: `/checkpoints/history` + composed readout).

### Human wave-acceptance (after loop-spec + Draft PR)

When checklist PASS and coding is green, the human at checkpoint
`wave-acceptance`:

- [ ] Run `.venv/bin/python -m tests.verify.verify_checkpoint_history` (API+worker up; programme token; `tests/config.yaml`; fixture PR where GitHub evidence required)
- [ ] Experience / inspect CAP-02 responses — persisted records retrievable via history (marked historical); composed readout resolves initiative+wave; 404 `no run found for this wave` on unresolved pairing; no GitHub/board writes
- [ ] Signal accept with GitHub label `wave-accepted` on the tip — content skills do **not** apply labels; that `pass` is **human approved**
- [ ] Apply tip hygiene for any hotfixes before Enter-at Pass-2 closeout
- [ ] Optional/legacy notes may land in `Live-Verify-*` — not required for the gate

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-011
- Issue: #162 — https://github.com/drivestream-lab/gateflow/issues/162
- EPIC: #160 — https://github.com/drivestream-lab/gateflow/issues/160
- Spec path: `docs/specification/product/INIT-GATEFLOW-011-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_checkpoint_history`
- ADRs in scope: ADR-001, ADR-003, ADR-004, ADR-005, ADR-009, ADR-010
- Wave head: bound by Forge/human context — `develop` (planned coding branch: `feature/INIT-GATEFLOW-011-w1-checkpoint-persistence`)

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — W1 gates satisfied; WorkManifest clean; P15 live command resolved; prior W0 human_approved |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-INIT-GATEFLOW-011-W1.md` to bound `head_ref` (`develop` or wave branch once cut) |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR (checklist + code on tip) |

Recommend `/commit-workspace` after explicit authorization. Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

N/A — W1 is single-repo CAP-02 (persistence + history + composed readout) layered on W0 evaluate(). W2+ (initiative read-out, wave map, etc.) depend on W1 persistence (REQ-06 records) but are later waves — not blocked by W1 merge order within this wave.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W1.md
    digest: sha256:132a1c45c03d34f3d50fc08de2103dcb8d0f20db99482b2946e04a0d89e36b48
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    delivery_wave: W1
    ticket_id: "162"
    ticket_url: https://github.com/drivestream-lab/gateflow/issues/162
    epic_ticket_id: "160"
    epic_ticket_url: https://github.com/drivestream-lab/gateflow/issues/160
    wave_head: develop
    wave_head_sha: 234f66a1b4d5e9d34522cb6bceb016c5672626a4
    wave_branch_planned: feature/INIT-GATEFLOW-011-w1-checkpoint-persistence
    prior_wave: W0
    prior_wave_approved: true
    prior_wave_tip_sha: 088d125c67d6306c1d1ddba28ee5cb01c1ec9f3d
    tasks:
      - TASK-W1-01
      - TASK-W1-02
      - TASK-W1-03
      - TASK-W1-04
      - TASK-W1-05
    implements_reqs:
      - REQ-03
      - REQ-06
      - REQ-07
      - REQ-08
      - REQ-28
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_checkpoint_history
    ground_command: "N/A — /ground-spec pin skill"
    board_wave_status: Todo
    spec_pr: https://github.com/drivestream-lab/gateflow/pull/159
    spec_merge_commit: 234f66a1b4d5e9d34522cb6bceb016c5672626a4
    workmanifest_contract: pass
    p15_applicable: true
    h1_prd_digest: sha256:eca06cbe986d619db58ae3ca84f4ec0987c19aa19b8f1485693280c6a655e4dd
    h2_repo_scope_digest: sha256:afdc7bd51bcd0c12f614feebf338bdc78766396bb84777121a2565c0ecc7966d
    h3_impact_map_revision: "1"
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
```

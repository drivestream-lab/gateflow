## Pre-implement — gateflow / W2 — Initiative list/detail (Gateflow-owned)

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W2.md` |
| Initiative | INIT-GATEFLOW-011 |
| Wave | W2 |
| Date | 2026-08-07 |
| Outcome | `pass` |
| Outcome reason | W2 gate checks pass: prior W1 `human_approved` (`wave-accepted` on tip `3074e82`; PR #172 merged `ba9b909`) with Ground-Report-W1 §Contracts produced complete; spec PR #159 merged with `spec-lgtm` (merge commit `234f66a1…`); board seeded (EPIC #160 / W2 #163 with TASK-W2-01…03); WorkManifest contract clean; P15 live verify command resolved; H1–H3 spend fresh on `develop`. |
| Wave head context | Bound by Forge/human context: `develop` @ `7e5ad7e` (after W1 merge + harness sync) — not opened by this skill; planned coding branch `feature/INIT-GATEFLOW-011-w2-initiatives-owned` (cut in `/loop-spec`) |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — `develop` @ `7e5ad7e` (not `chore/INIT-GATEFLOW-011-spec-gateflow`) |
| Spec PR merged | Implementation plan on integration branch | [x] yes — [#159](https://github.com/drivestream-lab/gateflow/pull/159) MERGED 2026-08-07; plan on `develop` @ `234f66a` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — `gh pr view 159` → labels `["spec-lgtm"]`; mergeCommit `234f66a1b4d5e9d34522cb6bceb016c5672626a4`; mergedAt 2026-08-07T02:57:19Z |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#160](https://github.com/drivestream-lab/gateflow/issues/160); W2 [#163](https://github.com/drivestream-lab/gateflow/issues/163) (OPEN, title `[INIT-GATEFLOW-011 W2] Initiative list/detail (Gateflow-owned)`, label `INIT-GATEFLOW-011`); `Board-Seed-INIT-GATEFLOW-011.md` B1–B8 PASS; sub-issue of EPIC per seed |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `.venv/bin/python prayog-skills/scripts/workmanifest_contract.py …/Implementation-Plan-INIT-GATEFLOW-011.md` → "WorkManifest contract passed." |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [x] complete — W2 TASK-W2-01…03 in plan §9 (lines 1079–1132); each has `exit.criteria`, `exit.proof.kind=command`, `command`, `expected`, `evidence_expected` |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` (not unit-as-live) | [x] contract — `verification.live.applicable: true`; command `.venv/bin/python -m tests.verify.verify_initiatives_readout` (FILE co-shipped in TASK-W2-03; script absent today — expected until `/loop-spec`) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — plan §Source freshness CURRENT; live digests match (plan is walk-time, may be purged at closure) |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — product spec H1 `sha256:eca06cbe…`, H2 `sha256:afdc7bd5…`, H3 revision `1`, G1 `f3da8148…` unchanged on `develop` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies; else command or N/A with reason | [x] `.venv/bin/python -m tests.verify.verify_initiatives_readout` |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` is Pass-2 pin skill, not a Makefile target |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` listed | [x] `tests/verify/verify_initiatives_readout.py` (create in TASK-W2-03) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] W1 = `human_approved` — as-built `implementation-status.md` (INIT-GATEFLOW-011 W1 row); `wave-accepted` on tip `3074e82`; PR #172 merged `ba9b909` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] exists — `Ground-Report-INIT-GATEFLOW-011-W1.md` (2026-08-07; outcome `pass`; §Contracts produced complete) |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W2 (not first wave); gate is prior-wave Ground Report + human_approved |

**Gate verdict:** PASS — W2 pre-flight gates satisfied; ready for `/loop-spec` after checklist publish.

**Board process note (read-only):** Wave ticket [#163](https://github.com/drivestream-lab/gateflow/issues/163) programme-board Status is **Todo** (not In Progress). Pin chain `wave-in-progress-action` → `pre-implement` is an automated orch hop; this skill does not mutate board status. Signal only — does not fail the gate table above.

**Forge readiness (when seed / wave head absent):** not required — seed complete; head bound to `develop`. Planned coding branch per plan: `feature/INIT-GATEFLOW-011-w2-initiatives-owned` (opened in `/loop-spec`, not here).

### Contracts consumed (from prior Ground Report)

> Read `Ground-Report-INIT-GATEFLOW-011-W1.md` §Contracts produced.
> For each contract this slice depends on, confirm the actual built interface
> matches what this wave's spec assumes. Scan `src/` to confirm — do not rely
> on spec text alone.

W2 is the **initiative list/detail (Gateflow-owned)** slice. It is composed
from **runs + board tickets** only; the `prd_approval` field is explicitly
`unavailable` until W3 (REQ-09 partial / REQ-10). W2 therefore does **not**
directly consume W1's checkpoint contracts (persistence / stale / history /
composed readout) — those feed **W3** (initiative detail PRD approval via
composed CAP-01) per the W1 Ground Report §Contracts produced "Next wave"
column. W2's dependencies are the **as-built stable surfaces** below plus
the W0/W1 **structural precedents** (route / service / model shapes).

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Run data (initiative list/detail composition) | `RunRepository.list_runs` / `get_run` | `session`, `initiative_id?`, `wave_id?`, `status_type?`, `org?`, `repo?`, `limit`, `skip` | `list[RunModel]` / `Optional[RunModel]` (carries `id`, `org`, `repo`, `pr_number?`, `issue_number?`, `initiative_id?`, `wave_id?`, `status_type`, `workflow_node?`, `meta_pr_url?`) | as-built INIT-001/002; `src/database/postgres/repository/run_store_repository.py:177/188/251` | [x] yes — present; W2 reads runs to derive affected repos + in-flight run link + current stage |
| Board ticket data (initiative current stage / affected repos) | `BoardService.list_tickets` | `org`, `repo`, `initiative_id?`, `ticket_type?`, `state` | `BoardTicketListResponse` (`tickets[]` of `BoardTicketResource`: `ticket_id`, `number`, `title`, `state`, `ticket_type?`, `initiative_id?`, `column?`, `html_url?`) | as-built INIT-002 W2; `src/business_services/board_service.py:406` | [x] yes — present; W2 reads EPIC + wave Feature tickets to derive current stage (column) + affected repos; **read-only** — no board mutations from CAP-03 path (REQ-28) |
| Programme-token control-plane auth (new GET routes) | `verify_programme_service_token` + `public_paths` | Bearer programme token | void / 401 | ADR-005; `src/api/v1/programme_token.py`; `src/app.py:76` | [x] yes — pattern live; `/api/v1/initiatives` already on `public_paths` (`src/app.py:81`); W2 adds GET routes under existing prefix |
| HTTP GET-only route precedent (CAP-03 shape) | `GET /api/v1/checkpoints/status` / `/history` | query params + programme token | Pydantic response model JSON | Ground-Report-W0/W1; `src/api/v1/checkpoints_routes.py:39/78` | [x] yes — GET-only precedent; W2 follows same query-param + `Depends(verify_programme_service_token)` shape; non-GET must 405 (REQ-28) |
| Business service precedent (BaseBusinessService + @inject + getter) | `CheckpointEvidenceService` (`@inject` `__init__`, `get_checkpoint_evidence_service`) | collaborators via constructor | Pydantic in/out | Ground-Report-W0; `src/business_services/checkpoint_evidence_service.py:45/499` | [x] yes — W2 `InitiativeReadoutService` follows same `BaseBusinessService` + `@inject` + `get_*_service()` pattern |
| Pydantic v2 model precedent (DTOs in `src/models/` only) | `checkpoint_models.py` (DTOs + enums with `Type` suffix + `extra="forbid"`) | — | — | Ground-Report-W0; `src/models/checkpoint_models.py` | [x] yes — W2 `initiative_readout_models.py` follows same placement + `Type`-suffix enum + `extra="forbid"` rules |
| Existing initiatives router (modify — add GET list/detail) | `src/api/v1/initiatives_routes.py` (today: only `POST /initiatives/closure/start` from INIT-010 W4) | — | — | as-built INIT-010 W4; `src/api/v1/initiatives_routes.py:15` | [x] yes — file exists with `POST /initiatives/closure/start`; W2 adds `GET /initiatives` + `GET /initiatives/{initiative_id}` to the same router (already composed in `src/api/v1/__init__.py:8/15`) |
| DI registration (modify — bind new service) | `BusinessServicesModule.configure` | `Binder` | void | as-built; `src/di/modules/business_services_module.py:26` | [x] yes — module present; W2 adds `binder.bind(InitiativeReadoutService, scope=singleton)` |

**Unconfirmed contracts** (prior wave not yet grounded or source not found):
- None blocking W2. W2 does **not** depend on W3+ (meta bridge, wave map, etc.) — those are later waves.
- W2 explicitly defers `prd_approval` population to W3 (composed CAP-01 against `prd-impact-acceptance` on the meta PR). The W1 Ground Report §Contracts produced "Composed readout" row names W3 as its consumer — not W2.

### Must read

- [x] `AGENTS.md` — constitution pin (`v0.5.0-rc.2`), programme board (drivestream-lab Board), verify command pointers, delivery bootstrap
- [x] MDC rules (domain-filtered — files read for this slice's domains):
  - [x] `.cursor/rules/architecture.mdc` — layered `api` → `business_services` → `database.repository` → `database.schema`; W2 adds a business service + routes + models (no ORM in services/api; repos return Pydantic)
  - [x] `.cursor/rules/repository-pattern.mdc` — W2 reads runs via `RunRepository` (Pydantic out); no ORM in `InitiativeReadoutService`; board data via `BoardService` (business, not repo)
  - [x] `.cursor/rules/pydantic-schemas.mdc` — initiative read-out DTOs in `src/models/initiative_readout_models.py` only; never define models in `src/api/`; `Type`-suffix enums; `extra="forbid"` for internal DTOs; `Field(default=…)` keyword form
  - [x] `.cursor/rules/http-api-conventions.mdc` — `GET /initiatives` + `GET /initiatives/{initiative_id}` use query params (filters/pagination on GET) + path for resource id; no write bodies; GET-only (REQ-28)
  - [x] `.cursor/rules/fail-fast.mdc` — unknown initiative id → 404 (distinct from malformed); fields present or explicitly `unavailable` (REQ-09); no silent defaults
  - [x] `.cursor/rules/dependency-injection.mdc` — `InitiativeReadoutService` uses `@inject` on `__init__`; bind in `BusinessServicesModule` `scope=singleton`; `get_initiative_readout_service()` delegates to `provide_service`; settings not injected
  - [x] `.cursor/rules/strong-typing.mdc` — initiative read-out fields typed (id `str`, stage enum, repos `list[str]`, run link `Optional[str]`); no `dict`/`Any` at service boundary
  - [x] `.cursor/rules/testing-verify-flows.mdc` — co-ship `tests/verify/verify_initiatives_readout.py`; feature-map row in `tests/README.md`; unit owns logic (mocked RunRepository/BoardService), live owns smoke
  - [x] `.cursor/rules/spec-driven-development.mdc` — same-PR as-built row (TASK-W2-03) + product spec as-built baseline after W2
  - [x] `.cursor/rules/infra-services.mdc` — no new infra service this wave; ForgeClient not directly used by CAP-03 (board reads go through `BoardService` which already wraps ForgeClient read methods)
  - [x] `.cursor/rules/logging-loguru.mdc` — service uses `self.logger` with kwargs (initiative_id, fields); no secrets
  - [ ] `.cursor/rules/database-migrations.mdc` — N/A for W2 (no new table/column; reads existing `runs` + board via ForgeClient); review only if a column is needed — none expected
- [x] ADRs (keyword-matched — initiative read-out, programme token, board, pin SSOT, run store):
  - [x] ADR-001 — runtime + durable store (**Accepted**; W2 reads existing `runs` store — cite only; no new store)
  - [x] ADR-003 — ForgeClient in infra; orchestration in business (**Accepted**; W2 board reads via `BoardService` → ForgeClient; no new infra)
  - [x] ADR-005 — programme-token control-plane reads zone; `public_paths` allowlist (**Accepted**; new GET routes under existing `/api/v1/initiatives` prefix already on `public_paths`)
  - [x] ADR-009 — pin `forge:` mutate authority; CAP-03 must not call write Forge actions (**Accepted**; W2 read-only — no `apply_labels`/review/merge/`update_board_status`)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` — W2 REQs REQ-09 (partial), REQ-10 (+ REQ-28 global guard); negative/failure paths table (unknown initiative → 404; fields present or `unavailable`)
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-011.md` W2 (lines 223–277, 1070–1153)
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/163 — TASK list (projected from WorkManifest; not a second authority):
  - [ ] TASK-W2-01 — implements REQ-09, REQ-10 — depends_on: [] — files: `src/business_services/initiative_readout_service.py` (create), `src/models/initiative_readout_models.py` (create), `tests/unit/test_initiative_readout.py` (create), `src/di/modules/business_services_module.py` (modify) — exit proof: `make test` exit 0
  - [ ] TASK-W2-02 — implements REQ-09, REQ-10, REQ-28 — depends_on: [TASK-W2-01] — files: `src/api/v1/initiatives_routes.py` (modify), `tests/unit/test_initiatives_read_api.py` (create) — exit proof: `make test` exit 0
  - [ ] TASK-W2-03 — implements REQ-09, REQ-10, REQ-28 — depends_on: [TASK-W2-02] — files: `tests/verify/verify_initiatives_readout.py` (create), `tests/README.md` (modify), `docs/specification/as-built/implementation-status.md` (modify) — exit proof: `make check && make test` (+ human live verify at wave-acceptance)

---

### Governance alignment

- [x] Slice spec does not contradict any listed ADR — GET-only CAP-03; zero mutate from new path (ADR-009/005); reads existing durable store (ADR-001); board reads via business service (ADR-003)
- [x] Plan TASK MDC notes and ADR notes for W2 reviewed (architecture, http-api-conventions, pydantic-schemas, fail-fast; ADR-001/003/005/009)
- [x] Every initiative ADR cited for W2 is **Accepted** in `docs/specification/adr/` (zero NEW-ADR from TDD; W2 introduces no new architectural decision)

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` as-built baseline after W2 exit (initiative list/detail Gateflow-owned live; `prd_approval=unavailable` until W3)
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-GATEFLOW-011 W2 verification row (REQ-09 partial / REQ-10 / REQ-28)
- [ ] `tests/README.md` — feature-map row for `verify_initiatives_readout` (CAP-03 Gateflow-owned list/detail)
- [ ] Unit verification scope — `test_initiative_readout` (service logic: list/detail fields present or `unavailable`; affected repos derived from runs; current stage from board column; in-flight run link), `test_initiatives_read_api` (GET-only 405 on non-GET; 401 without token; 404 unknown initiative; programme-token enforced); edges: unknown initiative → 404 distinct from malformed, fields `unavailable` not absent, no board/Forge writes from path
- [ ] Live verification — co-shipped `tests/verify/verify_initiatives_readout.py` (human-run at `wave-acceptance`); smoke only — does not duplicate unit assertions
- [ ] ADR — no supersede required (ADR_REQUIRED=0 for W2)

---

### Must not

- [ ] Implement against spec wording that contradicts an Accepted ADR without first superseding that ADR
- [ ] Duplicate unit verification assertions in live smoke scripts (unit owns list/detail logic; live owns smoke on running stack)
- [ ] Assume a contract from a prior wave is correct without checking the Ground Report (or flagging it as unconfirmed above)
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Call `apply_labels`, review create/update, merge, or `update_board_status` from any CAP-03 path (REQ-05 / REQ-28)
- [ ] Populate `prd_approval` from Gateflow-owned data alone — it is `unavailable` until W3 (composed CAP-01 against `prd-impact-acceptance` on the meta PR)
- [ ] Introduce a parallel initiative SoT — REQ-10 requires composition from runs + board tickets (+ at most one read-only meta read in W3), no new source of truth
- [ ] Commit any file under `postgres_migrations/versions/` (human-only; W2 adds no table/column)

---

### Verification plan

| Layer | What it proves | Command (from tests_readme / profile) |
|-------|----------------|---------------------------------------|
| Static check | Formatting, linting, types, import layers | `make check` |
| Unit | Initiative list/detail returns Gateflow-owned fields (id, affected repos, current stage, in-flight run link) with `prd_approval=unavailable`; GET-only guard (405 on non-GET); 401 without programme token; 404 unknown initiative distinct from malformed; no board/Forge writes from path | `make test` |
| Live verify | Product behaviour on running stack (human-run at `wave-acceptance`) — list/detail smoke | `.venv/bin/python -m tests.verify.verify_initiatives_readout` |
| Ground check | Assigned wave REQs satisfied; boundaries respected | N/A — `/ground-spec` Pass-2 pin skill after learning-extract |

> When P15 applies: N/A or unit-only for live verify **blocks** the gate.
> Agent implements the script in `/loop-spec`; does **not** run it as success.
> Policy: [live-smoke-policy.md](../../../prayog-skills/skills/development/pre-implement/references/live-smoke-policy.md).
> P15 applicable — new GET product surface: `/api/v1/initiatives` + `/api/v1/initiatives/{initiative_id}`.

### Human wave-acceptance (after loop-spec + Draft PR)

When checklist PASS and coding is green, the human at checkpoint
`wave-acceptance`:

- [ ] Run `.venv/bin/python -m tests.verify.verify_initiatives_readout` (API+worker up; programme token; `tests/config.yaml`)
- [ ] Experience / inspect CAP-03 responses — list returns initiatives with Gateflow-owned fields (affected repos, current stage, in-flight run link); detail returns the same for one initiative; `prd_approval=unavailable`; unknown initiative → 404; no GitHub/board writes
- [ ] Signal accept with GitHub label `wave-accepted` on the tip — content skills do **not** apply labels; that `pass` is **human approved**
- [ ] Apply tip hygiene for any hotfixes before Enter-at Pass-2 closeout
- [ ] Optional/legacy notes may land in `Live-Verify-*` — not required for the gate

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-011
- Issue: #163 — https://github.com/drivestream-lab/gateflow/issues/163
- EPIC: #160 — https://github.com/drivestream-lab/gateflow/issues/160
- Spec path: `docs/specification/product/INIT-GATEFLOW-011-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_initiatives_readout`
- ADRs in scope: ADR-001, ADR-003, ADR-005, ADR-009
- Wave head: bound by Forge/human context — `develop` @ `7e5ad7e` (planned coding branch: `feature/INIT-GATEFLOW-011-w2-initiatives-owned`)

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — W2 gates satisfied; WorkManifest clean; P15 live command resolved; prior W1 human_approved |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-INIT-GATEFLOW-011-W2.md` to bound `head_ref` (`develop` or wave branch once cut) |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR (checklist + code on tip) |

Recommend `/commit-workspace` after explicit authorization. Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

N/A — W2 is single-repo CAP-03 (initiative list/detail from Gateflow-owned runs+board) with `prd_approval=unavailable`. W3 (meta bridge + partial success) depends on W2 and will populate `prd_approval` via composed CAP-01 — not blocked by W2 merge order within this wave.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W2.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    delivery_wave: W2
    ticket_id: "163"
    ticket_url: https://github.com/drivestream-lab/gateflow/issues/163
    epic_ticket_id: "160"
    epic_ticket_url: https://github.com/drivestream-lab/gateflow/issues/160
    wave_head: develop
    wave_head_sha: 7e5ad7e
    wave_branch_planned: feature/INIT-GATEFLOW-011-w2-initiatives-owned
    prior_wave: W1
    prior_wave_approved: true
    prior_wave_tip_sha: 3074e82b7b54bbbd6d015f0420d255fd81a30ea1
    tasks:
      - TASK-W2-01
      - TASK-W2-02
      - TASK-W2-03
    implements_reqs:
      - REQ-09
      - REQ-10
      - REQ-28
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_initiatives_readout
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


## Pre-implement — gateflow / W3 — Meta bridge + partial success

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W3.md` |
| Initiative | INIT-GATEFLOW-011 |
| Wave | W3 |
| Date | 2026-08-07 |
| Outcome | `pass` |
| Outcome reason | W3 gate checks pass: prior W2 `human_approved` + merged (#174 `ba2ab7b`) with Ground-Report-W2 §Contracts produced complete; spec PR #159 merged with `spec-lgtm`; board seeded (EPIC #160 / W3 #164 with TASK-W3-01…03, Status In Progress); WorkManifest contract clean; P15 live verify command resolved; H1–H3 spend fresh on `develop`. |
| Wave head context | Bound by Forge/human context: `develop` @ `3d588db` (after W2 wave-signoff merge record) — not opened by this skill; planned coding branch `feature/INIT-GATEFLOW-011-w3-meta-bridge` (cut in `/loop-spec`) |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — `develop` @ `3d588db` (not `chore/INIT-GATEFLOW-011-spec-gateflow`) |
| Spec PR merged | Implementation plan on integration branch | [x] yes — [#159](https://github.com/drivestream-lab/gateflow/pull/159) MERGED 2026-08-07; plan on `develop` @ `234f66a` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — `gh pr view 159` → labels `["spec-lgtm"]`; mergeCommit `234f66a1b4d5e9d34522cb6bceb016c5672626a4`; mergedAt 2026-08-07T02:57:19Z |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#160](https://github.com/drivestream-lab/gateflow/issues/160); W3 [#164](https://github.com/drivestream-lab/gateflow/issues/164) (OPEN, title `[INIT-GATEFLOW-011 W3] Meta bridge + partial success`, label `INIT-GATEFLOW-011`); TASK-W3-01…03 in body; `Board-Seed-INIT-GATEFLOW-011.md` B1–B8 PASS; programme Status **In Progress** |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `.venv/bin/python prayog-skills/scripts/workmanifest_contract.py …/Implementation-Plan-INIT-GATEFLOW-011.md` → "WorkManifest contract passed." |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [x] complete — W3 TASK-W3-01…03 in plan §9 (lines 1174–1223); each has `exit.criteria`, `exit.proof.kind=command`, `command`, `expected`, `evidence_expected` |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` (not unit-as-live) | [x] contract — `verification.live.applicable: true`; command `.venv/bin/python -m tests.verify.verify_initiative_meta_bridge` (FILE co-shipped in TASK-W3-03; script absent today — expected until `/loop-spec`) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — plan §Source freshness CURRENT; live digests match (plan is walk-time, may be purged at closure) |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — product spec H1 `sha256:eca06cbe…`, H2 `sha256:afdc7bd5…`, H3 revision `1`, G1 `f3da8148…` unchanged on `develop` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies; else command or N/A with reason | [x] `.venv/bin/python -m tests.verify.verify_initiative_meta_bridge` |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` is Pass-2 pin skill, not a Makefile target |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` listed | [x] `tests/verify/verify_initiative_meta_bridge.py` (create in TASK-W3-03) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] W2 = `human_approved + merged` — as-built `implementation-status.md` (INIT-GATEFLOW-011 W2 row); tip `e9654c2` `wave-accepted`; PR #174 merged `ba2ab7b` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] exists — `Ground-Report-INIT-GATEFLOW-011-W2.md` (2026-08-07; outcome `pass`; §Contracts produced complete for W3) |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W3 (not first wave); gate is prior-wave Ground Report + human_approved |

**Gate verdict:** PASS — W3 pre-flight gates satisfied; ready for `/loop-spec` after checklist publish.

**Forge readiness (when seed / wave head absent):** not required — seed complete; head bound to `develop`; board W3 already In Progress. Planned coding branch per plan: `feature/INIT-GATEFLOW-011-w3-meta-bridge` (opened in `/loop-spec`, not here).

---

### Contracts consumed (from prior Ground Report)

> Read `Ground-Report-INIT-GATEFLOW-011-W2.md` §Contracts produced (and W0/W1 CAP-01
> contracts named as W3 consumers). Confirm against `src/` — do not rely on
> spec text alone.

W3 completes CAP-03 PRD-approval by wiring a **read-only meta bridge**: populate
`prd_approval` / `prd_approval_reason` via CAP-01 against checkpoint
`prd-impact-acceptance` on the initiative's **meta PR**. Meta unreachable →
HTTP 200 with meta fields `unavailable` and Gateflow-owned fields still present
(REQ-11). No new routes — extends existing GET list/detail behaviour.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Initiative list (Gateflow-owned) | `InitiativeReadoutService.list_initiatives` / `GET /api/v1/initiatives` | `org`, `repo`, `limit`, `skip` + programme token | `InitiativeListResult` (`initiatives[]` with `prd_approval`, owned fields) | Ground-Report-W2 | [x] yes — `src/business_services/initiative_readout_service.py`; `src/api/v1/initiatives_routes.py`; W3 modifies service only (no new route) |
| Initiative detail (Gateflow-owned) | `InitiativeReadoutService.get_initiative` / `GET /api/v1/initiatives/{initiative_id}` | `initiative_id` + `org`, `repo` + programme token | `InitiativeReadout` (same fields as list item); 404 when neither runs nor EPIC | Ground-Report-W2 | [x] yes — present; W3 extends `_build_item` / detail path with meta-derived `prd_approval` |
| `prd_approval` field contract | `PrdApprovalStateType` on `InitiativeListItem` / `InitiativeReadout` | — | `satisfied` \| `not_satisfied` \| `could_not_verify` \| `unavailable` | Ground-Report-W2 | [x] yes — `src/models/initiative_readout_models.py`; W2 always `unavailable` with reason `"meta bridge not yet wired (W3)"`; W3 replaces that stub |
| Live CAP-01 evaluate (meta PR target) | `CheckpointEvidenceService.evaluate(checkpoint_id, pr_ref)` | checkpoint id `prd-impact-acceptance` + `CheckpointPrRef` (meta owner/repo/number) | `CheckpointStatusResult` (`verdict` ∈ {satisfied, not_satisfied, could_not_verify}, `checked_sha`/`checked_at`, `missing_items`) | Ground-Report-W0 | [x] yes — `evaluate` at `checkpoint_evidence_service.py:…`; vocab includes `prd-impact-acceptance` in `checkpoint_models.py`; read-only Forge evidence |
| ForgeClient evidence reads | `ForgeClient.get_pull_request` / `list_reviews` / `list_check_runs` | org/repo/PR | PR / review / check-run documents | Ground-Report-W0 | [x] yes — used inside CAP-01; same App credentials for meta (TDD PE-3 / Q-2) |
| Meta PR URL parse precedent | `MetaPrIntakeService.parse_url` | meta PR URL string | `MetaPrRef` (owner, repo, pr_number) | as-built; `meta_pr_intake.py` | [x] yes — parse shape live; W3 maps to `CheckpointPrRef` for `evaluate` |
| Run `meta_pr_url` durable field | `RunModel.meta_pr_url` / `RunRepository` | initiative runs | optional URL string on run rows | as-built INIT-001/wave-start | [x] yes — `run_store_models.py` / schema column; W3 resolves meta PR from initiative runs (not from `evaluate_composed`, which targets the **app** wave PR) |
| Programme-token auth on existing GETs | `verify_programme_service_token` | Bearer programme token | void / 401 | ADR-005; Ground-Report-W2 | [x] yes — no route change required |
| Composed readout (`evaluate_composed`) | `CheckpointEvidenceService.evaluate_composed(initiative_id, wave_id, checkpoint_id)` | initiative + **wave** + checkpoint → app PR | `CheckpointStatusResult` or 404 `no run found for this wave` | Ground-Report-W1 | [x] yes present — **do not use for meta PRD line**: it resolves the app `org/repo/pr_number`, not `meta_pr_url`. W3 composes CAP-01 into initiative readout via `evaluate` + meta ref (see Unconfirmed / design note) |

**Unconfirmed contracts** (prior wave not yet grounded or source not found):
- None blocking W3.
- **Design note for `/loop-spec` (not a gate fail):** Ground-Report-W1/W2 prose says "composed CAP-01" for W3 — that means **compose CAP-01 into the initiative readout**, not call `evaluate_composed` (wave-scoped app PR). Resolve meta PR from run `meta_pr_url` → `CheckpointPrRef` → `evaluate("prd-impact-acceptance", …)`. When no `meta_pr_url` is resolvable → `prd_approval=unavailable` with an explicit reason (not a 5xx). Meta/GitHub transport failure → `unavailable` + HTTP 200 (REQ-11), owned fields unchanged. Map CAP-01 `verdict` → `PrdApprovalStateType` 1:1 for the three live verdicts; reserve `unavailable` for meta-down / missing-ref paths.

---

### Must read

- [x] `AGENTS.md` — constitution pin (`v0.5.0-rc.2`), programme board, verify command pointers, delivery bootstrap
- [x] MDC rules (domain-filtered — files read for this slice's domains):
  - [x] `.cursor/rules/architecture.mdc` — layered `api` → `business_services` → repo/infra; W3 extends business service only (inject `CheckpointEvidenceService`; no ORM in services)
  - [x] `.cursor/rules/dependency-injection.mdc` — add collaborator via `@inject` constructor on `InitiativeReadoutService`; bind already present for both services; no settings injection
  - [x] `.cursor/rules/infra-services.mdc` — no new infra; ForgeClient remains behind CAP-01 / BoardService
  - [x] `.cursor/rules/repository-pattern.mdc` — continue runs via `RunRepository` (Pydantic out); no schema imports in business
  - [x] `.cursor/rules/pydantic-schemas.mdc` — reuse `PrdApprovalStateType` / existing DTOs; no models under `src/api/`; map CAP-01 verdict → enum
  - [x] `.cursor/rules/http-api-conventions.mdc` — no new routes; existing GET query/path contract unchanged
  - [x] `.cursor/rules/fail-fast.mdc` — meta-down is **product-specified** partial success (REQ-11), not silent swallow of owned-field failure; unknown initiative still 404
  - [x] `.cursor/rules/strong-typing.mdc` — typed verdict/enum mapping; no `dict` at service boundary
  - [x] `.cursor/rules/testing-verify-flows.mdc` — co-ship `tests/verify/verify_initiative_meta_bridge.py`; unit owns meta-up/meta-down logic; live owns smoke
  - [x] `.cursor/rules/spec-driven-development.mdc` — same-PR as-built W3 row + tests README feature map
  - [x] `.cursor/rules/logging-loguru.mdc` — log meta bridge outcomes with kwargs (`initiative_id`, `prd_approval`, reason); no secrets
  - [ ] `.cursor/rules/database-migrations.mdc` — N/A (no new table/column; reads existing `meta_pr_url`)
- [x] ADRs (keyword-matched — meta bridge, CAP-01, programme token, pin mutate authority):
  - [x] ADR-001 — runtime + durable store (**Accepted**; W3 reads existing runs / CAP-01 persistence side-effect unchanged)
  - [x] ADR-003 — ForgeClient in infra; orchestration in business (**Accepted**; meta evidence via CAP-01 → ForgeClient)
  - [x] ADR-005 — programme-token control-plane reads (**Accepted**; existing GET routes)
  - [x] ADR-009 — pin forge mutate authority (**Accepted**; CAP-03 path remains read-only — REQ-28)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` — W3 REQs REQ-09 (complete), REQ-11 (+ REQ-28 global); failure path: meta unreachable → 200 + `unavailable`
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-011.md` W3 (lines 279–329, 1165–1255)
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/164 — TASK list (projected from WorkManifest; not a second authority):
  - [ ] TASK-W3-01 — implements REQ-09 — depends_on: [] — files: `src/business_services/initiative_readout_service.py` (modify), `tests/unit/test_initiative_readout.py` (modify) — exit proof: `make test` exit 0 — PRD approval via CAP-01 against `prd-impact-acceptance` on meta PR
  - [ ] TASK-W3-02 — implements REQ-11 — depends_on: [TASK-W3-01] — files: same service + unit tests (modify) — exit proof: `make test` exit 0 — meta unreachable → HTTP 200; meta fields `unavailable`; owned fields present
  - [ ] TASK-W3-03 — implements REQ-09, REQ-11, REQ-28 — depends_on: [TASK-W3-02] — files: `tests/verify/verify_initiative_meta_bridge.py` (create), `tests/README.md` (modify), `docs/specification/as-built/implementation-status.md` (modify) — exit proof: `make check && make test` (+ human live verify at wave-acceptance)

---

### Governance alignment

- [x] Slice spec does not contradict any listed ADR — GET-only; zero mutate from CAP-03 (ADR-009/005); meta evidence via existing ForgeClient (ADR-003); durable runs store (ADR-001)
- [x] Plan TASK MDC notes and ADR notes for W3 reviewed (architecture, http-api-conventions, pydantic-schemas, fail-fast; ADR-001/003/005/009)
- [x] Every initiative ADR cited for W3 is **Accepted** in `docs/specification/adr/` (zero NEW-ADR; W3 introduces no new architectural decision)

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` as-built baseline after W3 (PRD approval populated; REQ-11 partial success live)
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-GATEFLOW-011 W3 verification row (REQ-09 complete / REQ-11 / REQ-28)
- [ ] `tests/README.md` — feature-map row for `verify_initiative_meta_bridge` (CAP-03 meta bridge)
- [ ] Unit verification scope — `test_initiative_readout`: meta-up maps CAP-01 verdict → `prd_approval`; meta-down / missing `meta_pr_url` → `unavailable` with reason + owned fields still present; no Forge writes; list + detail both populate; edges: GitHub/meta transport failure ≠ 5xx on initiative GET
- [ ] Live verification — co-shipped `tests/verify/verify_initiative_meta_bridge.py` (human-run at `wave-acceptance`); smoke meta-up + meta-down paths; does not duplicate unit assertions
- [ ] ADR — no supersede required (ADR_REQUIRED=0 for W3)

---

### Must not

- [ ] Implement against spec wording that contradicts an Accepted ADR without first superseding that ADR
- [ ] Duplicate unit verification assertions in live smoke scripts
- [ ] Assume a contract from a prior wave is correct without checking the Ground Report (or flagging it as unconfirmed above)
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Call `apply_labels`, review create/update, merge, or `update_board_status` from any CAP-03 path (REQ-05 / REQ-28)
- [ ] Call `evaluate_composed` for the PRD-approval line (that resolves the **app** wave PR, not meta)
- [ ] Fail the whole initiative GET with 5xx when meta is unreachable — REQ-11 requires 200 + `unavailable`
- [ ] Introduce a parallel initiative SoT (REQ-10) — meta is evidence only via GitHub REST
- [ ] Commit any file under `postgres_migrations/versions/` (human-only; W3 adds no table/column)
- [ ] Add new mutating or non-GET product routes

---

### Verification plan

| Layer | What it proves | Command (from tests_readme / profile) |
|-------|----------------|---------------------------------------|
| Static check | Formatting, linting, types, import layers | `make check` |
| Unit | PRD approval populated from CAP-01 on meta PR when reachable; meta-down / missing meta ref → `prd_approval=unavailable` with owned fields present and HTTP 200; GET-only / no Forge writes; list+detail both updated | `make test` |
| Live verify | Product behaviour on running stack (human-run at `wave-acceptance`) — meta-up + meta-down smoke | `.venv/bin/python -m tests.verify.verify_initiative_meta_bridge` |
| Ground check | Assigned wave REQs satisfied; boundaries respected | N/A — `/ground-spec` Pass-2 pin skill after learning-extract |

> When P15 applies: N/A or unit-only for live verify **blocks** the gate.
> Agent implements the script in `/loop-spec`; does **not** run it as success.
> Policy: [live-smoke-policy.md](../../../prayog-skills/skills/development/pre-implement/references/live-smoke-policy.md).
> P15 applicable — changed GET product surface behaviour on `/api/v1/initiatives` + `/api/v1/initiatives/{initiative_id}` (`prd_approval` population).

### Human wave-acceptance (after loop-spec + Draft PR)

When checklist PASS and coding is green, the human at checkpoint
`wave-acceptance`:

- [ ] Run `.venv/bin/python -m tests.verify.verify_initiative_meta_bridge` (API+worker up; programme token; `tests/config.yaml`; fixture with/without reachable meta as knobs allow)
- [ ] Experience / inspect CAP-03 — meta-up: `prd_approval` ∈ {satisfied, not_satisfied, could_not_verify}; meta-down: `unavailable` + owned fields still returned; no GitHub/board writes
- [ ] Signal accept with GitHub label `wave-accepted` on the tip — content skills do **not** apply labels; that `pass` is **human approved**
- [ ] Apply tip hygiene for any hotfixes before Enter-at Pass-2 closeout
- [ ] Optional/legacy notes may land in `Live-Verify-*` — not required for the gate

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-011
- Issue: #164 — https://github.com/drivestream-lab/gateflow/issues/164
- EPIC: #160 — https://github.com/drivestream-lab/gateflow/issues/160
- Spec path: `docs/specification/product/INIT-GATEFLOW-011-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_initiative_meta_bridge`
- ADRs in scope: ADR-001, ADR-003, ADR-005, ADR-009
- Wave head: bound by Forge/human context — `develop` @ `3d588db` (planned coding branch: `feature/INIT-GATEFLOW-011-w3-meta-bridge`)

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — W3 gates satisfied; WorkManifest clean; P15 live command resolved; prior W2 human_approved |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-INIT-GATEFLOW-011-W3.md` to bound `head_ref` (`develop` or wave branch once cut) |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR (checklist + code on tip) |

Recommend `/commit-workspace` after explicit authorization. Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

N/A — W3 is single-repo CAP-03 extension (meta bridge into existing initiative readout). Depends on W2 contracts already merged to `develop`. No cross-service code change in `prayog-meta` (evidence-only via GitHub REST).

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W3.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    delivery_wave: W3
    ticket_id: "164"
    ticket_url: https://github.com/drivestream-lab/gateflow/issues/164
    epic_ticket_id: "160"
    epic_ticket_url: https://github.com/drivestream-lab/gateflow/issues/160
    wave_head: develop
    wave_head_sha: 3d588dbe20b1f685f4a2526af2f4b6e43036c055
    wave_branch_planned: feature/INIT-GATEFLOW-011-w3-meta-bridge
    prior_wave: W2
    prior_wave_approved: true
    prior_wave_tip_sha: e9654c2d4475f6e50a9e721e27dcdc8d8ce9f3de
    prior_wave_merge_sha: ba2ab7bc9ddd620eebb83c4d8c283c2fd29f10d6
    tasks:
      - TASK-W3-01
      - TASK-W3-02
      - TASK-W3-03
    implements_reqs:
      - REQ-09
      - REQ-11
      - REQ-28
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_initiative_meta_bridge
    ground_command: "N/A — /ground-spec pin skill"
    board_wave_status: In Progress
    spec_pr: https://github.com/drivestream-lab/gateflow/pull/159
    spec_merge_commit: 234f66a1b4d5e9d34522cb6bceb016c5672626a4
    workmanifest_contract: pass
    p15_applicable: true
    live_verify_path: tests/verify/verify_initiative_meta_bridge.py
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    commit_workspace: required
    head_ref: develop
    paths:
      - docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W3.md
```

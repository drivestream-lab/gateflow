## Pre-implement — gateflow / W1 — Identity directory + grant/detach

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-017-W1.md` |
| Initiative | INIT-GATEFLOW-017 |
| Wave | W1 |
| Date | 2026-08-14 |
| Outcome | `pass` |
| Outcome reason | W0 Ground Report + as-built `human_approved`; spec merged with `spec-lgtm`; board seeded; WorkManifest clean; P15 live command is `verify_identity_directory`; H1–H3 match live durable roots. |
| Wave head context | Bound by Forge/human context: `develop` @ `06d1cc1ac3bb64b264d57905345e6efbfbe84936` — not opened by this skill |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — on `develop` @ `06d1cc1ac3bb64b264d57905345e6efbfbe84936` (W0 merge [#249](https://github.com/drivestream-lab/gateflow/pull/249)) |
| Spec PR merged | Implementation plan on integration branch | [x] yes — PR [#243](https://github.com/drivestream-lab/gateflow/pull/243) MERGED; plan on `develop` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — label `spec-lgtm`; `mergeCommit` `0cd555abf26f73976d1d9bae034f6ee1fdb1f27d` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#244](https://github.com/drivestream-lab/gateflow/issues/244); W1 [#246](https://github.com/drivestream-lab/gateflow/issues/246) body lists TASK-W1-01…05 and `Part of #244` |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `.venv/bin/python prayog-skills/scripts/workmanifest_contract.py docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-017.md --base-path .` |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [x] complete — TASK-W1-01…05 |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` (not unit-as-live) | [x] contract — `.venv/bin/python -m tests.verify.verify_identity_directory` (create; not `make test`) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — plan § Source freshness |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — H3 `1`; H2 `sha256:3d39ee6d5947bcd18c3e0b46de16709b3fdddeefeb0e8d5bbae8ecf98b1e5834` |
| Product-spec H1–H3 spend freshness | live durable roots match citations | [x] current — H1 `sha256:c0fe55040928a13976133edde5cf71f0524815c17c0a8de79173ed3fa0657f67`; G1 `601b00e0a74510a6af1c33bc80ca27260995c094` (meta PR [#42](https://github.com/drivestream-lab/prayog-meta/pull/42)) |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies | [x] `.venv/bin/python -m tests.verify.verify_identity_directory` |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` uses as-built + spec citations; no dedicated ground script |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` | [x] `tests/verify/verify_identity_directory.py` (FILE-W1-11, **create**) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] W0 = `human_approved` — PR [#249](https://github.com/drivestream-lab/gateflow/pull/249) @ `3da2d02` `wave-accepted` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] exists — `docs/specification/reports/Ground-Report-INIT-GATEFLOW-017-W0.md` outcome `pass` |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W1; W0 PE sign-off already complete |

**Gate verdict:** PASS — ready for Forge `commit_workspace` (this checklist) then `/loop-spec`.

**Forge readiness (when seed / wave head absent):** not required. Wave head is `develop`. Coding branch `feature/INIT-GATEFLOW-017-w1-identity-directory` is cut by `/commit-workspace` / Forge — not this skill.

---

### Contracts consumed (from prior Ground Report)

> Read `Ground-Report-INIT-GATEFLOW-017-W0.md` §Contracts produced.
> Confirmed against `source_roots` on `develop` @ `06d1cc1`.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Identity row | `UserIdentityRepository` create / get_by_id / get_by_credential_identifier | credential, password hash, role, display name, status, session epoch | `UserIdentityReadModel` | Ground-Report-W0 | [x] yes — no `tenant_id`; unique credential; `password_hash` still on persist DTO |
| Membership grant | `ProgrammeMembershipRepository` create_membership / get_by_identity_and_programme | identity id + programme id | `ProgrammeMembershipReadModel` | Ground-Report-W0 | [x] yes — unique pair only; **no list/delete yet** |
| Session gate | `require_role` / `assert_live_session` | AuthContext (`sub`, role, session_epoch) | same or 401 `suspended` / `session_epoch_mismatch` | Ground-Report-W0 | [x] yes — W1 must increment epoch on suspend and password-set |
| Programme scope | `require_programme_scope` | user id + path tenant | AuthContext or 403 `not_granted` | Ground-Report-W0 | [x] yes — unused by directory routes (platform_admin factory acts) |
| JWT mint | `AuthIdentityService.mint_user_jwt` | user id, role, session epoch | JWT `sub` / `role` / `session_epoch` | Ground-Report-W0 | [x] yes — **grant must not call mint** |
| Login snapshot | `POST /api/auth/login` | email + password | token + `grants` array | Ground-Report-W0 | [x] yes — W0 `grants` always empty; **do not populate in W1** (W3 enter/snapshot) |
| Status vocabulary | `IdentityStatusType` | wire string | `active` \| `suspended` | Ground-Report-W0 | [x] yes — already on tree (`src/models/identity_status_types.py`) |
| Wipe vs identity | `ProgrammeWipeService.wipe_programme` | programme id | wipe result | Ground-Report-W0 | [x] yes — does not delete identity rows; membership cascade wipe remains W2 |

**Unconfirmed contracts** (needed by W1, not in §9 file list or not produced by W0):

- `UserIdentityRepository` has no list/search, no status/password/epoch update. TASK-W1-02 must add those methods (compile-safe) even though `user_identity_repository.py` is not in the W1 `files[]` list.
- `ProgrammeMembershipRepository` has no list-by-identity, list-by-programme, or delete. TASK-W1-03 must add those methods even though `programme_membership_repository.py` is not in the W1 `files[]` list.
- `UserIdentityReadModel` still includes `password_hash`. Directory HTTP/read models in `identity_models.py` must omit password and hash (REQ-30). Do not strip the persist DTO — login still needs the hash.
- `IdentityStatusType` already exists (W0). TASK-W1-01 `action: create` on that file is **reuse / no rewrite of accepted members**.
- `require_role` emits 403 `role_forbidden`. REQ-22 / TDD §6 want directory/grant 403 `wrong actor`. Do **not** globally rename `role_forbidden` (014 unit tests). Add a directory-actor dependency on identity/grant routes that raises `wrong actor`.
- Duplicate email is **409** `duplicate email` (TDD §3.4 / §6 `ConflictError`), not 422.
- Grant of seeded `platform_admin` is 422 (REQ-05). Identify seed by `RoleType.PLATFORM_ADMIN` on the identity row.
- 014 `POST /api/v1/programmes/{id}/tenant-admins` stays mounted until W2. New grants live beside it at `/programmes/{id}/grants`.
- `GET /api/auth/me` and `POST /api/auth/session/programme` are **W3** — do not add them here.

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered):
  - [x] `architecture.mdc` — routers → business → repo; `*_service` suffix
  - [x] `pydantic-schemas.mdc` — models in `src/models/` only; `extra=forbid`; `Field(default=...)`
  - [x] `http-api-conventions.mdc` — body-only writes; GET query for list/search
  - [x] `dependency-injection.mdc` — `@inject`; bind new service in module + `_BUSINESS_SERVICE_TYPES`
  - [x] `repository-pattern.mdc` — no ORM in business/API; Pydantic at repo boundary
  - [x] `testing-verify-flows.mdc` — new live script; do not duplicate full HTTP journeys in pytest
  - [x] `fail-fast.mdc` — named refusals; no silent create-on-grant
  - [x] `strong-typing.mdc` — no `dict` service APIs
  - [x] `python-imports.mdc` — top-of-file imports; DI bootstrap exception only
  - [x] `logging-loguru.mdc` — static message + kwargs; never log password/hash
  - skipped: `infra-services.mdc` (no new outbound client); `database-migrations.mdc` (no schema change in W1); `python-tooling.mdc` (commands resolved)
- [x] ADRs (keyword-matched — identity / grant / session / JWT / durable store):
  - [x] ADR-019 — Accepted — no remint on grant; increment `session_epoch` on suspend/password-set
  - [x] ADR-001 — Accepted — Postgres is sole durable store
  - [x] ADR-014 — Accepted — JWT-only product edge
  - skipped: ADR-002–013, 015–018 (not this slice)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-017-gateflow.md` — W1 spends REQ-01…14 (except 15–21 owned later), REQ-22, REQ-24, REQ-25, REQ-28, REQ-29, REQ-30
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-017.md` W1
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/246 — TASK list (projection only):
  - [ ] TASK-W1-01 — implements REQ-01, REQ-30 — depends_on: [] — files: `identity_models.py` create; `identity_status_types.py` create (reuse) — exit: read models omit password — proof: `make check`
  - [ ] TASK-W1-02 — implements REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-12, REQ-13, REQ-14, REQ-25, REQ-29, REQ-30 — depends_on: [TASK-W1-01] — files: `identity_directory_service.py` create; DI modules modify; `test_identity_directory_service.py` create — exit: named enter/suspend/password refusals; epoch increments — proof: `pytest tests/unit/test_identity_directory_service.py -q`
  - [ ] TASK-W1-03 — implements REQ-05, REQ-06, REQ-07, REQ-08, REQ-09, REQ-10, REQ-11, REQ-24, REQ-28 — depends_on: [TASK-W1-02] — files: directory service + unit test modify — exit: grant idempotent; unknown 422; no JWT — proof: same pytest
  - [ ] TASK-W1-04 — implements REQ-22 — depends_on: [TASK-W1-03] — files: `identity_routes.py` create; `programme_admin_routes.py` modify; `api/v1/__init__.py` modify; `test_identity_routes.py` create — exit: tenant_admin 403 `wrong actor`; platform_admin 200 — proof: `pytest tests/unit/test_identity_routes.py -q`
  - [ ] TASK-W1-05 — implements REQ-01, REQ-02, REQ-04, REQ-05, REQ-06, REQ-09, REQ-10, REQ-11, REQ-12, REQ-14, REQ-22, REQ-30 — depends_on: [TASK-W1-04] — files: `verify_identity_directory.py` create — exit: live enter → list → grant → detach → suspend → password-set — proof: human `{verify_command}`

**DAG for `/loop-spec`:** TASK-W1-01 → TASK-W1-02 → TASK-W1-03 → TASK-W1-04 → TASK-W1-05.

---

### Governance alignment

- [x] Slice spec does not contradict ADR-019 / ADR-001 / ADR-014
- [x] Plan TASK MDC notes and ADR notes for W1 reviewed
- [x] ADR-019 is **Accepted** — grant does not remint; epoch increment is the kill switch

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — no REQ rewrite unless a contract word changes
- [ ] `docs/specification/as-built/implementation-status.md` — W1 pointer row (not `human_approved` until `wave-acceptance`)
- [ ] `Implementation-Status-INIT-GATEFLOW-017.md` — W1 capability detail
- [ ] `tests/README.md` — feature map row for `verify_identity_directory`
- [ ] Unit — enter refusals; list/search; suspend/unsuspend/password epoch; grant/detach/idempotent/unknown; platform_admin not grantable; wrong actor
- [ ] Live — create `tests/verify/verify_identity_directory.py`; marker `prayog:covers:` lists TASK-W1-05 REQs
- [ ] ADR — do not rewrite Accepted ADR-019

---

### Must not

- [ ] Implement against spec wording that contradicts Accepted ADR-019 (no remint on grant)
- [ ] Duplicate unit verification assertions in live smoke (live = happy journey + one wrong-actor probe)
- [ ] Populate login `grants` or add `/api/auth/me` / enter-programme (W3)
- [ ] Delete `POST /api/v1/programmes/{id}/tenant-admins` or historic `POST /api/v1/tenants/{id}/users` (W2)
- [ ] Rewrite `provision_programme_tenant_admin` (W2 / FF-03)
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Run `./scripts/run_postgres_migration.sh` (human-owned; W0 revision must already be applied for live)
- [ ] Put Pydantic models under `src/api/`
- [ ] Return password or `password_hash` on list/search/membership
- [ ] Globally rename `role_forbidden` on all `require_role` callers

---

### Verification plan

| Layer | What it proves | Command (from tests_readme / profile) |
|-------|----------------|---------------------------------------|
| Static check | Formatting, linting, types, layers | `make check` |
| Unit | Enter/list/suspend/password; grant/detach; wrong actor | `make test` |
| Live verify | Enter → list → grant → detach → suspend → password-set on running stack (human at `wave-acceptance`) | `.venv/bin/python -m tests.verify.verify_identity_directory` |
| Ground check | Assigned wave REQs satisfied; boundaries respected | N/A — `/ground-spec` uses as-built + spec citations |

> P15 applies (new identity/grant HTTP surface). N/A or unit-only for live verify would block this gate — it does not. Agent implements the script in `/loop-spec`; does **not** run live verify as success.

### Human wave-acceptance (after loop-spec + Draft PR)

When checklist PASS and coding is green, the human at checkpoint
`wave-acceptance`:

- [ ] Confirm W0 Alembic `9713e795e01c` is applied (`./scripts/run_postgres_migration.sh head` if needed)
- [ ] `make run` with JWT key material, `auth.platform_admin`, and at least one onboarded programme in `tests/config.yaml`
- [ ] Run `.venv/bin/python -m tests.verify.verify_identity_directory`
- [ ] Signal accept with GitHub label `wave-accepted` on the tip — content skills do **not** apply labels
- [ ] Optional/legacy notes may land in `Live-Verify-*` — not required for the gate

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-017
- Issue: [#246](https://github.com/drivestream-lab/gateflow/issues/246) (EPIC [#244](https://github.com/drivestream-lab/gateflow/issues/244))
- Spec path: `docs/specification/product/INIT-GATEFLOW-017-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_identity_directory`
- ADRs in scope: ADR-019 (primary), ADR-001, ADR-014
- Wave head: bound by Forge/human context — `develop` @ `06d1cc1ac3bb64b264d57905345e6efbfbe84936` (Forge/human may bind `feature/INIT-GATEFLOW-017-w1-identity-directory` before coding)

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — W1 gates satisfied |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-INIT-GATEFLOW-017-W1.md` to bound `head_ref` |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR (checklist + code already on tip) |

Recommend `/commit-workspace` after explicit authorization, then `/loop-spec`. Do not open the PR here. Do not create the feature branch here.

---

### Merge order (if cross-module / cross-service)

N/A — W1 is gateflow-only. `gateflow-ops` consumes CTR-01/CTR-02 later; no ops change in this wave.

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-017-W1.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-017
    wave: W1
    board_epic: "https://github.com/drivestream-lab/gateflow/issues/244"
    board_wave_issue: "https://github.com/drivestream-lab/gateflow/issues/246"
    board_seed: seeded
    spec_pr: "https://github.com/drivestream-lab/gateflow/pull/243"
    spec_lgtm_at_merge: true
    workmanifest_contract: pass
    tasks:
      - TASK-W1-01
      - TASK-W1-02
      - TASK-W1-03
      - TASK-W1-04
      - TASK-W1-05
    check_command: "make check"
    test_command: "make test"
    verify_command: ".venv/bin/python -m tests.verify.verify_identity_directory"
    ground_command: null
    wave_head: develop
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-017-W0.md
    prior_as_built: human_approved
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    draft: false
    title: "docs(INIT-GATEFLOW-017): Pre-Implement W1 PASS checklist"
    body_path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-017-W1.md
```

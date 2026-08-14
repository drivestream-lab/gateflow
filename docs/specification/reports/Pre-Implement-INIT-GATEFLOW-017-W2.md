## Pre-implement — gateflow / W2 — Delete 014 doors + wipe collaborator

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-017-W2.md` |
| Initiative | INIT-GATEFLOW-017 |
| Wave | W2 |
| Date | 2026-08-14 |
| Outcome | `pass` |
| Outcome reason | W1 Ground Report + as-built `human_approved`; spec merged with `spec-lgtm`; board seeded; WorkManifest clean; P15 live command is `verify_dead_doors_deleted`; H1–H3 match live durable roots. |
| Wave head context | Bound by Forge/human context: `develop` @ `1e107d49d6eba33ad8cbf7e11f8d1f45d333a043` — not opened by this skill |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — on `develop` @ `1e107d49d6eba33ad8cbf7e11f8d1f45d333a043` (W1 merge [#250](https://github.com/drivestream-lab/gateflow/pull/250)) |
| Spec PR merged | Implementation plan on integration branch | [x] yes — PR [#243](https://github.com/drivestream-lab/gateflow/pull/243) MERGED; plan on `develop` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — label `spec-lgtm`; `mergeCommit` `0cd555abf26f73976d1d9bae034f6ee1fdb1f27d` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#244](https://github.com/drivestream-lab/gateflow/issues/244); W2 [#247](https://github.com/drivestream-lab/gateflow/issues/247) body lists TASK-W2-01…04 and `Part of #244` |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `.venv/bin/python prayog-skills/scripts/workmanifest_contract.py docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-017.md --base-path .` |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [x] complete — TASK-W2-01…04 |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` (not unit-as-live) | [x] contract — `.venv/bin/python -m tests.verify.verify_dead_doors_deleted` (extend; not `make test`) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — plan § Source freshness |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — H3 `1`; H2 `sha256:3d39ee6d5947bcd18c3e0b46de16709b3fdddeefeb0e8d5bbae8ecf98b1e5834` |
| Product-spec H1–H3 spend freshness | live durable roots match citations | [x] current — H1 `sha256:c0fe55040928a13976133edde5cf71f0524815c17c0a8de79173ed3fa0657f67`; G1 `601b00e0a74510a6af1c33bc80ca27260995c094` (meta PR [#42](https://github.com/drivestream-lab/prayog-meta/pull/42)) |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies | [x] `.venv/bin/python -m tests.verify.verify_dead_doors_deleted` |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` uses as-built + spec citations; no dedicated ground script |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` | [x] `tests/verify/verify_dead_doors_deleted.py` (FILE-W2-10, **extend**) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] W1 = `human_approved` — PR [#250](https://github.com/drivestream-lab/gateflow/pull/250) @ `b224fe6` `wave-accepted` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] exists — `docs/specification/reports/Ground-Report-INIT-GATEFLOW-017-W1.md` outcome `pass` |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W2; W0 PE sign-off already complete |

**Gate verdict:** PASS — ready for Forge `commit_workspace` (this checklist) then `/loop-spec`.

**Forge readiness (when seed / wave head absent):** not required. Wave head is `develop`. Coding branch `feature/INIT-GATEFLOW-017-w2-delete-doors-wipe` is cut by `/commit-workspace` / Forge — not this skill.

---

### Contracts consumed (from prior Ground Report)

> Read `Ground-Report-INIT-GATEFLOW-017-W1.md` §Contracts produced.
> Confirmed against `source_roots` on `develop` @ `1e107d4`.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Enter identity | `IdentityDirectoryService.enter_identity` / `POST /api/v1/identities` | display name, email, password | IdentityRead (`tenant_admin`, grants empty) | Ground-Report-W1 | [x] yes — 409 `duplicate email`; 422 named refusals; no password on output |
| Grant / detach | `grant` / `detach` / `POST\|DELETE /api/v1/programmes/{id}/grants` | programme id + identity id | membership pair | Ground-Report-W1 | [x] yes — idempotent; no JWT mint; 422 unknown identity/programme / `platform_admin not grantable` |
| Membership views | `list_grants` / `list_members` | identity id or programme id | membership pairs or IdentityRead list | Ground-Report-W1 | [x] yes — identity remains after last detach |
| Directory actor | `require_directory_admin` | AuthContext | same or 403 `wrong actor` | Ground-Report-W1 | [x] yes — do not rename global `role_forbidden` |
| Identity read shape | `IdentityReadModel` | — | id, display_name, email, status, role, grants | Ground-Report-W1 | [x] yes — `extra=forbid`; no password |
| 014 attach door | `ProgrammeService.attach_tenant_admin` / `POST /api/v1/programmes/{id}/tenant-admins` | credential + password | attach response + `access_token` | Ground-Report-W1 | [x] yes — **still mounted**; W2 deletes this |
| Wipe vs identity | `ProgrammeWipeService.wipe_programme` | programme id | wipe result | Ground-Report-W0 / W1 | [x] yes — does not delete identity rows today; memberships CASCADE on programme delete (`ondelete=CASCADE`); identity FK is `RESTRICT` |
| Login snapshot | `POST /api/auth/login` | email + password | token + `grants` array | Ground-Report-W0 | [x] yes — `grants` still empty; **do not populate** (W3) |

**Unconfirmed contracts** (needed by W2, not in §9 file list or not produced by W1):

- Historic `POST /api/v1/tenants/{id}/users` (`attach_tenant_user` in `tenant_routes.py`) was **not** a W1 contract. It is still mounted. TASK-W2-02 deletes it (REQ-20 / A-7).
- `ProgrammeWipeService` has no membership or identity collaborator. TASK-W2-03 must leave identity rows (FF-02) and keep ACTIVE-run **409**. Memberships for the wiped programme must be gone. Pair-delete `ProgrammeMembershipRepository.delete_membership` exists (W1); there is **no** `delete_for_programme`. Either iterate `list_by_programme` or rely on programme-row CASCADE. Adding `delete_for_programme` is compile-safe and **not** in W2 `files[]`.
- `provision_programme_tenant_admin` (`tests/_helpers/verify_jwt_auth.py`) still POSTs `/tenant-admins` and returns `(jwt, tenant_id, programme_id)`. After W0, login JWT has **no** `tenant_id` claim. Rewrite must take `tenant_id` from the programme-create body/response, not `tenant_id_from_token`. Keep the return tuple so callers outside `files[]` keep compiling (`verify_programme_connect`, `verify_repo_selection`, `verify_workspace_lifecycle`, `verify_branch_lifecycle`, `verify_catalogue_refresh`, `verify_harness_status`).
- Helper path is **enter → grant → login** (FF-03). Grant must not remint. Do **not** call `POST /api/auth/session/programme` (W3).
- `verify_dead_doors_deleted.py` today only asserts `POST /api/v1/tenants` gone (014 REQ-34). **Extend** it: keep that probe; add 014 `POST …/tenant-admins` and 012 `POST …/tenants/{id}/users` absent/refused. Do not replace the script or drop the register-gone case.
- `verify_programme_onboarding.py` still POSTs `/tenant-admins`. Drop attach JWT provision; onboard create / catalogue stay (REQ-27).
- `AttachTenantAdminRequest` / `AttachTenantAdminResponse` in `programme_models.py` become unused after TASK-W2-01. Optional unused-model cleanup is **not** in `files[]` — only if `make check` requires it.
- Do not delete `/programmes/{id}/grants` when removing `/tenant-admins`.

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered):
  - [x] `architecture.mdc` — routers → business; do not leave attach on the programme admin router
  - [x] `http-api-conventions.mdc` — deleted doors are absent (404/405), not query-param refusals
  - [x] `fail-fast.mdc` — wipe ACTIVE 409 unchanged; named conflict; no silent identity delete
  - [x] `repository-pattern.mdc` — wipe talks to repos only; no ORM in the service
  - [x] `testing-verify-flows.mdc` — extend live scripts; do not duplicate unit journeys
  - [x] `dependency-injection.mdc` — if wipe gains a membership/identity repo, `@inject` + existing bind
  - [x] `python-imports.mdc` — top-of-file imports
  - skipped: `pydantic-schemas.mdc` (no new request bodies); `infra-services.mdc` (no new client); `database-migrations.mdc` (no schema change); `python-tooling.mdc` (commands resolved); `logging-loguru.mdc` (existing wipe logs); `strong-typing.mdc` (no new service API shape)
- [x] ADRs (keyword-matched — doors / wipe / membership / JWT):
  - [x] ADR-019 — Accepted — no remint door; membership is SSOT; grant does not mint
  - [x] ADR-001 — Accepted — Postgres is sole durable store
  - [x] ADR-014 — Accepted — JWT-only product edge (claim shape already superseded in part by ADR-019)
  - skipped: ADR-002–013, 015–018 (not this slice)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-017-gateflow.md` — W2 spends REQ-10 (wipe half), REQ-15, REQ-20, REQ-21, REQ-27
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-017.md` W2
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/247 — TASK list (projection only):
  - [ ] TASK-W2-01 — implements REQ-21 — depends_on: [] — files: `programme_service.py`, `programme_admin_routes.py`, `test_programme_service.py` modify — exit: `POST …/tenant-admins` absent (404/405) — proof: `make test`
  - [ ] TASK-W2-02 — implements REQ-20 — depends_on: [] — files: `tenant_routes.py` modify — exit: `POST …/tenants/{id}/users` absent (404/405) — proof: `make test`
  - [ ] TASK-W2-03 — implements REQ-10, REQ-15, REQ-21 — depends_on: [TASK-W2-01] — files: `programme_wipe_service.py`, `test_programme_wipe_service.py` modify — exit: wipe removes memberships; identity row remains; ACTIVE 409 — proof: `pytest tests/unit/test_programme_wipe_service.py -q`
  - [ ] TASK-W2-04 — implements REQ-21, REQ-27 — depends_on: [TASK-W2-01] — files: `verify_jwt_auth.py`, `verify_programme_onboarding.py`, `verify_wipe_cutover.py`, `verify_dead_doors_deleted.py`, `verify_old_doors_refused.py` modify — exit: helper enter→grant→login; dead-door live asserts 014/012 gone — proof: human `{verify_command}`

**DAG for `/loop-spec`:** TASK-W2-01 ∥ TASK-W2-02 → TASK-W2-03 → TASK-W2-04. Manifest `depends_on` for 03/04 is only TASK-W2-01; run TASK-W2-02 before TASK-W2-04 so the live script can assert the historic users door is gone.

---

### Governance alignment

- [x] Slice spec does not contradict ADR-019 / ADR-001 / ADR-014
- [x] Plan TASK MDC notes and ADR notes for W2 reviewed (FF-02 wipe collaborator; FF-03 verify helper — TDD_ONLY, no extra ADR)
- [x] ADR-019 is **Accepted** — deleting the remint attach door is the product cut; grant stays no-mint

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — no REQ rewrite unless a contract word changes
- [ ] `docs/specification/as-built/implementation-status.md` — W2 pointer row (not `human_approved` until `wave-acceptance`)
- [ ] `Implementation-Status-INIT-GATEFLOW-017.md` — W2 capability detail
- [ ] `tests/README.md` — drop attach-as-provision from the 014 onboard row; note 017 W2 dead-door + helper rewrite
- [ ] Unit — attach method/route gone; historic users route gone; wipe keeps identity; ACTIVE 409 unchanged
- [ ] Live — extend `tests/verify/verify_dead_doors_deleted.py`; marker `prayog:covers:` adds REQ-20, REQ-21 (keep existing 014 delete/REQ-34)
- [ ] ADR — do not rewrite Accepted ADR-019

---

### Must not

- [ ] Implement against spec wording that contradicts Accepted ADR-019 (no remint on grant; helper must login, not attach-mint)
- [ ] Duplicate unit verification assertions in live smoke (live = deleted-path probes + onboard still creates)
- [ ] Populate login `grants` or add `/api/auth/me` / enter-programme (W3)
- [ ] Delete `/api/v1/programmes/{id}/grants` when removing `/tenant-admins`
- [ ] Delete identity rows on programme wipe (FF-02)
- [ ] Change programme onboard / catalogue APIs except identity/grant (REQ-27)
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Run `./scripts/run_postgres_migration.sh`
- [ ] Put Pydantic models under `src/api/`
- [ ] Change the `provision_programme_tenant_admin` return tuple shape without updating every caller

---

### Verification plan

| Layer | What it proves | Command (from tests_readme / profile) |
|-------|----------------|---------------------------------------|
| Static check | Formatting, linting, types, layers | `make check` |
| Unit | Attach/users doors gone; wipe keeps identity; ACTIVE 409 | `make test` |
| Live verify | 014 attach and 012 users paths absent/refused on running stack (human at `wave-acceptance`) | `.venv/bin/python -m tests.verify.verify_dead_doors_deleted` |
| Ground check | Assigned wave REQs satisfied; boundaries respected | N/A — `/ground-spec` uses as-built + spec citations |

> P15 applies (deleted HTTP doors + helper rewrite). N/A or unit-only for live verify would block this gate — it does not. Agent extends the script in `/loop-spec`; does **not** run live verify as success.

### Human wave-acceptance (after loop-spec + Draft PR)

When checklist PASS and coding is green, the human at checkpoint
`wave-acceptance`:

- [ ] Confirm W0 Alembic `9713e795e01c` is applied
- [ ] `make run` with JWT key material and `auth.platform_admin`
- [ ] Run `.venv/bin/python -m tests.verify.verify_dead_doors_deleted`
- [ ] Optional inspect: `.venv/bin/python -m tests.verify.verify_programme_onboarding` still creates a programme (REQ-27)
- [ ] Signal accept with GitHub label `wave-accepted` on the tip — content skills do **not** apply labels
- [ ] Optional/legacy notes may land in `Live-Verify-*` — not required for the gate

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-017
- Issue: [#247](https://github.com/drivestream-lab/gateflow/issues/247) (EPIC [#244](https://github.com/drivestream-lab/gateflow/issues/244))
- Spec path: `docs/specification/product/INIT-GATEFLOW-017-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_dead_doors_deleted`
- ADRs in scope: ADR-019 (primary), ADR-001, ADR-014
- Wave head: bound by Forge/human context — `develop` @ `1e107d49d6eba33ad8cbf7e11f8d1f45d333a043` (Forge/human may bind `feature/INIT-GATEFLOW-017-w2-delete-doors-wipe` before coding)

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — W2 gates satisfied |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-INIT-GATEFLOW-017-W2.md` to bound `head_ref` |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR (checklist + code already on tip) |

Recommend `/commit-workspace` after explicit authorization, then `/loop-spec`. Do not open the PR here. Do not create the feature branch here.

---

### Merge order (if cross-module / cross-service)

N/A — W2 is gateflow-only. `gateflow-ops` consumes CTR-01/CTR-02 later; no ops change in this wave.

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-017-W2.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-017
    wave: W2
    board_epic: "https://github.com/drivestream-lab/gateflow/issues/244"
    board_wave_issue: "https://github.com/drivestream-lab/gateflow/issues/247"
    board_seed: seeded
    spec_pr: "https://github.com/drivestream-lab/gateflow/pull/243"
    spec_lgtm_at_merge: true
    workmanifest_contract: pass
    tasks:
      - TASK-W2-01
      - TASK-W2-02
      - TASK-W2-03
      - TASK-W2-04
    check_command: "make check"
    test_command: "make test"
    verify_command: ".venv/bin/python -m tests.verify.verify_dead_doors_deleted"
    ground_command: null
    wave_head: develop
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-017-W1.md
    prior_as_built: human_approved
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    draft: false
    title: "docs(INIT-GATEFLOW-017): Pre-Implement W2 PASS checklist"
    body_path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-017-W2.md
```

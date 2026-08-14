## Pre-implement — gateflow / W3 — Enter programme + isolation + as-built

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-017-W3.md` |
| Initiative | INIT-GATEFLOW-017 |
| Wave | W3 |
| Date | 2026-08-14 |
| Outcome | `pass` |
| Outcome reason | W2 Ground Report + as-built `human_approved`; spec merged with `spec-lgtm`; board seeded; WorkManifest clean; P15 live command is `verify_cross_programme_isolation`; H1–H3 match live durable citations. |
| Wave head context | Bound by Forge/human context: `develop` @ `2e3040c0522ebd049a1158f0acba96ec872458a1` — not opened by this skill |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — on `develop` @ `2e3040c0522ebd049a1158f0acba96ec872458a1` (W2 Pass-2 merge [#252](https://github.com/drivestream-lab/gateflow/pull/252); implementation merge [#251](https://github.com/drivestream-lab/gateflow/pull/251)) |
| Spec PR merged | Implementation plan on integration branch | [x] yes — PR [#243](https://github.com/drivestream-lab/gateflow/pull/243) MERGED; plan on `develop` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — label `spec-lgtm`; `mergeCommit` `0cd555abf26f73976d1d9bae034f6ee1fdb1f27d` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#244](https://github.com/drivestream-lab/gateflow/issues/244); W3 [#248](https://github.com/drivestream-lab/gateflow/issues/248) body lists TASK-W3-01…03 and `Part of #244` |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `.venv/bin/python prayog-skills/scripts/workmanifest_contract.py docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-017.md --base-path .` |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [x] complete — TASK-W3-01…03 |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` (not unit-as-live) | [x] contract — `.venv/bin/python -m tests.verify.verify_cross_programme_isolation` (extend; not `make test`) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — plan § Source freshness |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — H3 `1`; H2 `sha256:3d39ee6d5947bcd18c3e0b46de16709b3fdddeefeb0e8d5bbae8ecf98b1e5834` |
| Product-spec H1–H3 spend freshness | live durable roots match citations | [x] current — H1 `sha256:c0fe55040928a13976133edde5cf71f0524815c17c0a8de79173ed3fa0657f67`; G1 `601b00e0a74510a6af1c33bc80ca27260995c094` (meta PR [#42](https://github.com/drivestream-lab/prayog-meta/pull/42)) |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies | [x] `.venv/bin/python -m tests.verify.verify_cross_programme_isolation` |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` uses as-built + spec citations; no dedicated ground script |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` | [x] `tests/verify/verify_cross_programme_isolation.py` (FILE-W3-05, **extend**); also extend `tests/verify/verify_jwt_login.py` (FILE-W3-06) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] W2 = `human_approved` — PR [#251](https://github.com/drivestream-lab/gateflow/pull/251) @ `a40ab9c` `wave-accepted` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] exists — `docs/specification/reports/Ground-Report-INIT-GATEFLOW-017-W2.md` outcome `pass` |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W3; W0 PE sign-off already complete |

**Gate verdict:** PASS — ready for Forge `commit_workspace` (this checklist) then `/loop-spec`.

**Forge readiness (when seed / wave head absent):** not required. Wave head is `develop`. Coding branch `feature/INIT-GATEFLOW-017-w3-enter-programme` is cut by `/commit-workspace` / Forge — not this skill.

---

### Contracts consumed (from prior Ground Report)

> Read `Ground-Report-INIT-GATEFLOW-017-W2.md` §Contracts produced.
> Confirmed against `source_roots` on `develop` @ `2e3040c` (codegraph MCP
> `search_graph` on `data-repos-prayog-gateflow` + direct reads).

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| 014 attach door gone | former `POST /api/v1/programmes/{id}/tenant-admins` | — | 404 or 405 | Ground-Report-W2 | [x] yes — no `attach_tenant_admin`; W3 must not call attach |
| Historic users door gone | former `POST /api/v1/tenants/{id}/users` | — | 404 or 405 | Ground-Report-W2 | [x] yes |
| Wipe collaborator | `ProgrammeWipeService.wipe_programme` | programme id | wipe result | Ground-Report-W2 | [x] yes — memberships gone; identity remains; ACTIVE 409 `active_run` |
| Provision helper | `enter_grant_login` / `provision_programme_tenant_admin` | programme id + email + password | identity JWT + tenant id + programme id | Ground-Report-W2 | [x] yes — enter → grant → login; tenant id from programme create/GET, not JWT claim |
| Grant path (unchanged) | `POST\|DELETE /api/v1/programmes/{id}/grants` | programme id + identity id | membership pair | Ground-Report-W2 | [x] yes — only grant door; no mint |
| Onboard / catalogue (unchanged) | `ProgrammeService.validate_then_create` | onboard body | programme + catalogue | Ground-Report-W2 | [x] yes — REQ-27 |
| Login snapshot | `POST /api/auth/login` | email + password | token + `grants` array | Ground-Report-W2 | [x] yes — `grants` still always `[]`; **W3 populates** from memberships |
| Directory enter | `POST /api/v1/identities` | name, email, password | IdentityRead | Ground-Report-W2 | [x] yes — still the enter door |

**Unconfirmed contracts** (needed by W3, not produced as a finished enter-programme surface):

- `GET /api/auth/me` and `POST /api/auth/session/programme` **do not exist**. Only `POST /api/auth/login` is mounted (`login_routes.py` + `app.include_router(..., prefix="/api")`).
- `AuthMiddleware` treats `/api/auth` as a **prefix** public path (`app.py`). `GET /me` and `POST /session/programme` need a live Bearer. Narrow `public_paths` to `/api/auth/login` (exact/prefix of login only). `src/app.py` is **not** in W3 `files[]` — compile-safe extra if those routes otherwise see `request.state.auth is None`.
- `AuthIdentityService` has `UserIdentityRepository` only. Listing grants / checking a grant needs `ProgrammeMembershipRepository` (already bound in `RepositoryModule`). Inject it; do not add a new DI module.
- `mint_user_jwt` must stay `sub` / `role` / `session_epoch` — **no remint** on enter (ADR-019 Option B). Enter returns a snapshot, not a new `access_token`.
- `require_programme_scope` already refuses missing membership with reason `not_granted`. Product/plan enter-programme exit uses `not granted`. Use the **spec string** `not granted` on the new enter door. Do not rename the existing delivery-scope reason unless `make check` forces one shared constant.
- `require_tenant_resolved` already gates delivery (catalogue connection, etc.) as `tenant_admin` + membership; `platform_admin` is `wrong actor` / role forbidden. Isolation live script must hit a real delivery entry point (e.g. catalogue connection or include-repo), not only a synthetic 403.
- `verify_cross_programme_isolation.py` is still the 014 W2 script: `SMOKE_TENANT_A_TOKEN` / `SMOKE_TENANT_B_TOKEN` and “attached tenant_admins”. **Rewrite** to enter → grant → login → enter-programme; two programmes; refuse the other; `platform_admin` delivery 403. Do not POST `/tenant-admins`.
- `verify_jwt_login.py` already covers empty `grants` + no `tenant_id` claim. Extend: after a grant, login/me snapshot lists that programme; zero-grant identity stays signed in and cannot enter/deliver. Keep existing platform_admin login 200.
- FILE-W3-07 says **create** `Implementation-Status-INIT-GATEFLOW-017.md` — the file **already exists** (W0–W2 detail). **Modify** it (add W3 capability; list W0–W3). Collapse the three 017 “Capability matrix” pointer sections in `implementation-status.md` into **exactly one** index row pointing at the detail file (TASK-W3-03 exit / artifact-write-contract). Do not append a fourth table.
- `tests/README.md` is not in W3 `files[]` but the feature-map row for isolation / enter-programme must be updated in the same change (skill must-update).
- Login `grants` field type is `list[ProgrammeMembershipReadModel]` (`identity_id`, `programme_id`). Reuse it; do not invent a second grant DTO.
- Enter-programme POST is **body-only** (`http-api-conventions.mdc`): one Pydantic model in `src/models/auth_models.py` (programme id). Not query.

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered):
  - [x] `architecture.mdc` — JWT verify; `public_paths` must list actually public prefixes; routers → business
  - [x] `http-api-conventions.mdc` — POST enter-programme is a JSON body model, not query
  - [x] `pydantic-schemas.mdc` — models only in `src/models/`; no `BaseModel` under `src/api/`
  - [x] `fail-fast.mdc` — 403 `not granted` / `wrong actor`; no silent enter
  - [x] `dependency-injection.mdc` — inject membership repo on `AuthIdentityService`; settings stay `get_instance()`
  - [x] `testing-verify-flows.mdc` — extend live scripts; do not duplicate unit journeys
  - [x] `python-imports.mdc` — top-of-file imports
  - [x] `strong-typing.mdc` — service in/out are Pydantic, not `dict`
  - skipped: `repository-pattern.mdc` (no new ORM/repo); `infra-services.mdc` (no new client); `database-migrations.mdc` (no schema); `python-tooling.mdc` (commands resolved); `logging-loguru.mdc` (existing auth logs)
- [x] ADRs (keyword-matched — enter / session / JWT / isolation / delivery tenant):
  - [x] ADR-019 — Accepted — no remint; membership is SSOT; `session_epoch` kill switch
  - [x] ADR-016 — Accepted — `runs.tenant_id` from **path tenant after membership**, not from a reminted claim
  - [x] ADR-014 — Accepted — JWT-only product edge (claim shape superseded in part by ADR-019)
  - [x] ADR-001 — Accepted — Postgres is sole durable store (no Redis session)
  - skipped: ADR-002–013, 015, 017–018 (not this slice)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-017-gateflow.md` — W3 spends REQ-16, REQ-17, REQ-18, REQ-19, REQ-23, REQ-26 (+ REQ-27 as-built)
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-017.md` W3
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/248 — TASK list (projection only):
  - [ ] TASK-W3-01 — implements REQ-16, REQ-18, REQ-26 — depends_on: [] — files: `login_routes.py`, `auth_identity_service.py`, `auth_models.py`, `test_auth_identity_service.py` modify — exit: enter granted 200 snapshot; not granted 403; no remint; tenant_admin me has no factory roster — proof: `pytest tests/unit/test_auth_identity_service.py -q`
  - [ ] TASK-W3-02 — implements REQ-16, REQ-17, REQ-19, REQ-23 — depends_on: [TASK-W3-01] — files: `verify_cross_programme_isolation.py`, `verify_jwt_login.py` modify — exit: live enter granted, refuse other, two-programme delivery, platform_admin delivery 403 — proof: human `{verify_command}`
  - [ ] TASK-W3-03 — implements REQ-19, REQ-27 — depends_on: [TASK-W3-02] — files: `Implementation-Status-INIT-GATEFLOW-017.md` **modify** (plan says create; file exists), `implementation-status.md` modify — exit: exactly one 017 index row pointing at the detail file; detail lists W0–W3 — proof: review

**DAG for `/loop-spec`:** TASK-W3-01 → TASK-W3-02 → TASK-W3-03.

---

### Governance alignment

- [x] Slice spec does not contradict ADR-019 / ADR-016 / ADR-014 / ADR-001
- [x] Plan TASK MDC notes and ADR notes for W3 reviewed (body-only POST; P15 extend isolation; ADR-016 path tenant after membership)
- [x] ADR-019 is **Accepted** — enter-programme is authorization, not a second mint

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — no REQ rewrite unless a contract word changes
- [ ] `docs/specification/as-built/implementation-status.md` — **one** 017 pointer row (collapse W0/W1/W2 sections); not `human_approved` until `wave-acceptance`
- [ ] `Implementation-Status-INIT-GATEFLOW-017.md` — add W3 capability; keep W0–W2 rows
- [ ] `tests/README.md` — isolation / enter-programme feature-map row (enter → grant → login → enter-programme)
- [ ] Unit — enter granted 200; not granted 403; no new JWT; me has grants and no factory roster; login snapshot populated
- [ ] Live — extend `tests/verify/verify_cross_programme_isolation.py` and `verify_jwt_login.py`; marker `prayog:covers:` adds REQ-16, REQ-17, REQ-19, REQ-23 (keep existing isolation / login markers that still apply)
- [ ] ADR — do not rewrite Accepted ADR-019 or ADR-016

---

### Must not

- [ ] Implement against spec wording that contradicts Accepted ADR-019 (no remint; no programme/`tenant_id` claim)
- [ ] Duplicate unit verification assertions in live smoke (live = enter + two-programme delivery + platform_admin 403)
- [ ] Call deleted `POST …/tenant-admins` or `POST …/tenants/{id}/users`
- [ ] Change grant/detach or onboard/catalogue APIs (REQ-27)
- [ ] Put factory identity roster on `tenant_admin` me (REQ-26)
- [ ] Let `platform_admin` run delivery (REQ-23)
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Run `./scripts/run_postgres_migration.sh`
- [ ] Put Pydantic models under `src/api/`
- [ ] Append a new 017 capability table to the shared as-built index

---

### Verification plan

| Layer | What it proves | Command (from tests_readme / profile) |
|-------|----------------|---------------------------------------|
| Static check | Formatting, linting, types, layers | `make check` |
| Unit | Enter granted / not granted; no remint; me has no factory roster | `make test` |
| Live verify | Enter granted, refuse other programme, two-programme delivery, platform_admin 403 (human at `wave-acceptance`) | `.venv/bin/python -m tests.verify.verify_cross_programme_isolation` |
| Ground check | Assigned wave REQs satisfied; boundaries respected | N/A — `/ground-spec` uses as-built + spec citations |

> P15 applies (new enter-programme HTTP surface + isolation rewrite). N/A or unit-only for live verify would block this gate — it does not. Agent extends the script in `/loop-spec`; does **not** run live verify as success.

### Human wave-acceptance (after loop-spec + Draft PR)

When checklist PASS and coding is green, the human at checkpoint
`wave-acceptance`:

- [ ] Confirm W0 Alembic `9713e795e01c` is applied
- [ ] `make run` with JWT key material and `auth.platform_admin`
- [ ] Run `.venv/bin/python -m tests.verify.verify_cross_programme_isolation`
- [ ] Optional inspect: `.venv/bin/python -m tests.verify.verify_jwt_login` (grants field; zero-grant still signed in)
- [ ] Signal accept with GitHub label `wave-accepted` on the tip — content skills do **not** apply labels
- [ ] Optional/legacy notes may land in `Live-Verify-*` — not required for the gate

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-017
- Issue: [#248](https://github.com/drivestream-lab/gateflow/issues/248) (EPIC [#244](https://github.com/drivestream-lab/gateflow/issues/244))
- Spec path: `docs/specification/product/INIT-GATEFLOW-017-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_cross_programme_isolation`
- ADRs in scope: ADR-019 (primary), ADR-016, ADR-014, ADR-001
- Wave head: bound by Forge/human context — `develop` @ `2e3040c0522ebd049a1158f0acba96ec872458a1` (Forge/human may bind `feature/INIT-GATEFLOW-017-w3-enter-programme` before coding)

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — W3 gates satisfied |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-INIT-GATEFLOW-017-W3.md` to bound `head_ref` |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR (checklist + code already on tip) |

Recommend `/commit-workspace` after explicit authorization, then `/loop-spec`. Do not open the PR here. Do not create the feature branch here.

---

### Merge order (if cross-module / cross-service)

N/A — W3 is gateflow-only. `gateflow-ops` consumes CTR-04 later; no ops change in this wave.

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-017-W3.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-017
    wave: W3
    board_epic: "https://github.com/drivestream-lab/gateflow/issues/244"
    board_wave_issue: "https://github.com/drivestream-lab/gateflow/issues/248"
    board_seed: seeded
    spec_pr: "https://github.com/drivestream-lab/gateflow/pull/243"
    spec_lgtm_at_merge: true
    workmanifest_contract: pass
    tasks:
      - TASK-W3-01
      - TASK-W3-02
      - TASK-W3-03
    check_command: "make check"
    test_command: "make test"
    verify_command: ".venv/bin/python -m tests.verify.verify_cross_programme_isolation"
    ground_command: null
    wave_head: develop
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-017-W2.md
    prior_as_built: human_approved
    codegraph_provider: mcp-user-prayog-fleet-cbm
    grounding_depth: light
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    draft: false
    title: "docs(INIT-GATEFLOW-017): Pre-Implement W3 PASS checklist"
    body_path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-017-W3.md
```

## Pre-implement — gateflow / W1 — Programme validate-then-create + tenant_admin attach + agent catalogue

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-014-W1.md` |
| Initiative | INIT-GATEFLOW-014 |
| Wave | W1 |
| Date | 2026-08-11 |
| Outcome | `pass` |
| Outcome reason | Prior W0 Ground Report + `human_approved`; W0 merged to `develop`; WorkManifest contract clean; board #216 seeded under EPIC #214; P15 live scripts declared; W0 contracts confirmed in `source_roots`. |
| Wave head context | Bound by Forge/human context: `develop` @ `e17319d` (W0 merge [#220](https://github.com/drivestream-lab/gateflow/pull/220)) — not opened by this skill. No `feature/INIT-GATEFLOW-014-w1-*` yet; cut from `develop` before `/loop-spec` (or bind `develop` for checklist publish only). |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — integration head `develop` @ `e17319d` (W0 merge); workspace may still sit on merged W0 feature tip — bind `develop` / cut `feature/…-w1-*` for publish+coding |
| Spec PR merged | Implementation plan on integration branch | [x] yes — PR [#212](https://github.com/drivestream-lab/gateflow/pull/212) MERGED; plan on tree |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — `spec-lgtm` on [#212](https://github.com/drivestream-lab/gateflow/pull/212); head `4df184c…` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present; waves are **sub-issues of the EPIC** | [x] seeded — EPIC [#214](https://github.com/drivestream-lab/gateflow/issues/214); W1 [#216](https://github.com/drivestream-lab/gateflow/issues/216) `parent`=#214; body lists TASK-W1-01…07 |
| WorkManifest contract | `prayog/v1` §9 passes `workmanifest_contract.py` | [x] pass — `.venv/bin/python prayog-skills/scripts/workmanifest_contract.py … --base-path .` |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` | [x] complete — TASK-W1-01…07 |
| Live-verification contract | P15: `verification.live` applicable + script under `live_verify_dir` | [x] contract — `verify_programme_onboarding` (§9 primary) + `verify_agent_catalogue` (TEST-W1-L2 / FILE-W1-19) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current |
| Impact-map repo scope | revision and scope digest match | [x] match — H3 `1`; H2 `sha256:53bb4c4f204888154afc40385c7e717f92d39f98463fcc6e97694e465a0ac9ef` |
| Product-spec H1–H3 spend freshness | live durable roots match citations | [x] current — H1 `sha256:e8c5103ea55a16823bf6a4e5c10bfc34be8e9f94efee12f6a3da69722fc3ea3e` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script when P15 | [x] `.venv/bin/python -m tests.verify.verify_programme_onboarding` **and** `.venv/bin/python -m tests.verify.verify_agent_catalogue` |
| `ground_command` | resolved or N/A | [x] N/A — `/ground-spec` uses as-built + spec |
| Co-shipped live verify (P15) | FILE under `live_verify_dir` | [x] `tests/verify/verify_programme_onboarding.py` (FILE-W1-18); `tests/verify/verify_agent_catalogue.py` (FILE-W1-19) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] W0 = **human_approved** — `Implementation-Status-INIT-GATEFLOW-014.md`; index row; PR [#220](https://github.com/drivestream-lab/gateflow/pull/220) `wave-accepted` then MERGED `e17319d` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] exists — `Ground-Report-INIT-GATEFLOW-014-W0.md` (outcome pass; §Contracts produced) |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W1 |

**Gate verdict:** PASS — ready for Forge `commit_workspace` (this checklist onto bound head) then `/loop-spec`.

**Notes (non-blocking):**
- W1 board [#216](https://github.com/drivestream-lab/gateflow/issues/216) Status may still be Todo until optional in-progress action.
- Naming collision (TASK-W1-07): existing INIT-013 `programme_routes` / `ProgrammeOnboardingService` / `TenantProgrammeConnectionSchema` are **meta-catalogue connection**, not the new Programme entity — rename before or with admin routes to avoid symbol clash.
- Human-owned Alembic for new Programme + catalogue tables (agents describe DDL; humans create/apply revisions).

**Blocker registry:** none open.

---

### Contracts consumed (from prior Ground Report)

> Read `Ground-Report-INIT-GATEFLOW-014-W0.md` §Contracts produced.
> Confirmed against `source_roots` on W0-merged tip.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Role vocabulary | `RoleType` / `AuthContext` (`src/models/role_types.py`, `auth_models.py`) | role wire string | `platform_admin` \| `tenant_admin` | Ground-Report-W0 | [x] yes |
| User identity store | `UserIdentityRepository.create_identity` / `get_by_credential_identifier` | credential_identifier, password_hash, role, optional tenant_id | `UserIdentityReadModel` | Ground-Report-W0 | [x] yes — W1 attach creates `tenant_admin` rows here |
| JWT mint | `AuthIdentityService.mint_user_jwt` | user_id, role, optional tenant_id | Gateflow JWT claims | Ground-Report-W0 | [x] yes — attach/list live flows mint or login as `platform_admin` |
| Login API | `POST /api/auth/login` | LoginRequest | LoginResponse or 401 | Ground-Report-W0 | [x] yes |
| Seed platform_admin | `scripts/seed_platform_admin.py` | env defaults | user_id + access_token; idempotent | Ground-Report-W0 | [x] yes — live verify prerequisite |
| Middleware claim gate | `AuthMiddleware.dispatch` | Bearer JWT | AuthContext or 401 | Ground-Report-W0 | [x] yes — **do not** shrink product `public_paths` in W1 (W2) |
| PAT probe + meta clone (reuse) | `GithubPatProbe` + existing onboarding clone/parse patterns | PAT + org/repo | probe ok / catalogue candidates | INIT-013 as-built + `programme_onboarding_service.py` | [x] yes — W1 `ProgrammeService.validate_then_create` reuses probe/clone **before** durable Programme row; distinct from meta-connection entity |

**Unconfirmed contracts** (net-new this wave — no prior Ground Report):
- Programme persistence shape (PAT plaintext, workspace root, reserved App fields, lane defaults)
- `ProgrammeService.validate_then_create` fail-closed transaction boundary
- `platform_admin`-only programme admin HTTP surface
- Attach `tenant_admin` ↔ Programme membership + idempotency
- Platform agent catalogue provision + `resolve_effective_runner` (must not consult `CursorAgentSettings` / env)

---

### Must read

- [x] `AGENTS.md`
- [x] MDC (domain-filtered):
  - [x] `architecture.mdc` — layered layout; `*_service` naming
  - [x] `repository-pattern.mdc` — ORM only in repos
  - [x] `database-migrations.mdc` — human Alembic for new tables
  - [x] `pydantic-schemas.mdc` — models in `src/models/` only; enums
  - [x] `http-api-conventions.mdc` — POST body models for create/attach/provision
  - [x] `dependency-injection.mdc` — `@inject`; no `is_configured()` silent skip for required catalogue (TDD E2)
  - [x] `fail-fast.mdc` — zero partial Programme rows on validation failure
  - [x] `infra-services.mdc` — PAT probe / git clients stay infra; business owns validate-then-create
  - [x] `testing-verify-flows.mdc` — co-ship verify scripts; human at wave-acceptance
  - [x] `strong-typing.mdc`, `python-imports.mdc`, `logging-loguru.mdc`
- [x] ADRs (keyword-matched):
  - [x] **ADR-014** (Accepted) — JWT edge; W1 must not invent a second verifier; allowlist shrink still W2
  - [x] **ADR-015** (Accepted) — Programme owns PAT; W1 stores PAT on Programme row; factory cutover is W2
  - [x] **ADR-012** — catalogue discovery input for meta parse reuse during validate-then-create
  - skipped deep: ADR-016 (W2 tenant-scoped run/board)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-014-gateflow.md` (REQ-08–22, REQ-40–42, REQ-44–45, REQ-47 attach slice)
- [x] Plan wave section / §9: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-014.md` W1
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/216 — TASK projection:
  - [ ] TASK-W1-01 — REQ-08,11,12,14 — `programme_schema.py` + `programme_repository.py` — persist PAT/workspace/reserved App fields — proof: `pytest tests/unit/test_programme_repository.py -q`
  - [ ] TASK-W1-02 — REQ-08,09,10,13 — depends TASK-W1-01 — `programme_service.py` validate-then-create — bad PAT/meta → 0 rows; agent-key field → 422 — proof: `pytest tests/unit/test_programme_service.py -v`
  - [ ] TASK-W1-03 — REQ-08,17,18 — depends TASK-W1-02 — `programme_admin_routes.py` — platform_admin create/list; tenant_admin → 403 — proof: `pytest tests/unit/test_programme_admin_routes.py -v`
  - [ ] TASK-W1-04 — REQ-15,16,44,47 — depends TASK-W1-03 — attach tenant_admin; unknown programme reject; idempotent re-attach — proof: `pytest tests/unit/test_programme_service.py -k attach -v`
  - [ ] TASK-W1-05 — REQ-19,20,40,45 — `platform_agent_catalogue_schema` + repository — blank key → 0 usable row — proof: `pytest tests/unit/test_platform_agent_catalogue_repository.py -q`
  - [ ] TASK-W1-06 — REQ-21,22,41,42 — depends TASK-W1-05 — `platform_agent_catalogue_service` + provision route + `verify_agent_catalogue.py` — caller runner / lane default / reject unprovisioned; never consult env Cursor settings — proof: `pytest tests/unit/test_platform_agent_catalogue_service.py -v`
  - [ ] TASK-W1-07 — REQ-08 — depends TASK-W1-03 — rename meta-connection symbols (`programme_routes` → `catalogue_connection_routes`, etc.) + co-ship `verify_programme_onboarding.py` — proof: `make check` with zero old symbol refs outside rename diff

**DAG order for `/loop-spec`:**  
`(TASK-W1-01 → TASK-W1-02 → TASK-W1-03 → TASK-W1-04)` and `(TASK-W1-05 → TASK-W1-06)` may proceed in parallel after W0 baseline; **TASK-W1-07** after TASK-W1-03 (rename vs new admin routes). Prefer completing rename early enough that new Programme routes never collide with old names.

---

### Governance alignment

- [x] Slice spec does not contradict ADR-014 / ADR-015 for W1 scope
- [x] Plan TASK MDC notes and ADR notes for this wave reviewed
- [x] ADR-014, ADR-015, ADR-012 **Accepted** in `docs/specification/adr/`

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] `docs/specification/as-built/implementation-status.md` — INIT-GATEFLOW-014 W1 capability rows
- [ ] `docs/specification/as-built/Implementation-Status-INIT-GATEFLOW-014.md` — W1 status
- [ ] `tests/README.md` — feature map for `verify_programme_onboarding` + `verify_agent_catalogue` (distinct from INIT-013 `verify_programme_connect`)
- [ ] Unit tests listed in FILE-W1-03/05/07/10/12
- [ ] Live verify scripts FILE-W1-18 / FILE-W1-19 (human-run at `wave-acceptance`)
- [ ] DDL notes for human Alembic (Programme + catalogue tables) under `docs/specification/reports/`
- [ ] ADR — only if this wave would supersede Accepted ADR (not expected)

---

### Must not

- [ ] Shrink product `/api/v1/*` `public_paths` (W2 / ADR-014 consequences)
- [ ] Consult `CursorAgentSettings` / env `CURSOR_API_KEY` inside `resolve_effective_runner` (REQ-41)
- [ ] Leave partial Programme/Tenant rows on validation failure (REQ-09/10)
- [ ] Accept agent keys on Programme onboard body (REQ-13)
- [ ] Confuse new Programme entity with INIT-013 meta-catalogue connection (TASK-W1-07)
- [ ] Agent-authored files under `postgres_migrations/versions/`
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill

---

### Verification plan

| Layer | What it proves | Command (from tests_readme / profile) |
|-------|----------------|---------------------------------------|
| Static check | Format, lint, types, layers | `make check` |
| Unit | Programme repo/service/routes; catalogue repo/service; attach edges | `make test` (targeted files per TASK exit proofs) |
| Live verify | Onboarding + attach/list smoke; catalogue provision/resolve smoke | `.venv/bin/python -m tests.verify.verify_programme_onboarding`; `.venv/bin/python -m tests.verify.verify_agent_catalogue` |
| Ground check | Assigned W1 REQs; boundaries | N/A — `/ground-spec` manual + as-built |

> P15 applies: both live FILEs must be co-shipped in `/loop-spec`. Agent does **not** run them as skill success. Human runs at `wave-acceptance`.

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] Run both `{verify_command}` scripts (API up; fixture meta + non-prod test PAT)
- [ ] Experience / inspect create/reject/attach/list/provision/resolve
- [ ] Signal accept with GitHub label `wave-accepted` on the tip
- [ ] Tip hygiene before Pass-2 Enter-at
- [ ] Cleanup synthetic Programme + catalogue rows per plan live intent

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-014
- Issue: [#216](https://github.com/drivestream-lab/gateflow/issues/216)
- Spec path: `docs/specification/product/INIT-GATEFLOW-014-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_programme_onboarding` and `.venv/bin/python -m tests.verify.verify_agent_catalogue`
- ADRs in scope: ADR-014, ADR-015, ADR-012
- Wave head: bind `develop` @ `e17319d` or cut `feature/INIT-GATEFLOW-014-w1-*` from it — not opened here

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — gates satisfied; W0 contracts confirmed |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-INIT-GATEFLOW-014-W1.md` to bound `head_ref` |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR |

Recommend `/commit-workspace` after explicit authorization (bind `develop` or W1 feature branch first). Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

N/A — single-repo wave. Soft dependency: W0 already merged to `develop` (`e17319d`).

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-014-W1.md
  blockers: []
  signals:
    wave: W1
    initiative: INIT-GATEFLOW-014
    board_issue: "https://github.com/drivestream-lab/gateflow/issues/216"
    tasks:
      - TASK-W1-01
      - TASK-W1-02
      - TASK-W1-03
      - TASK-W1-04
      - TASK-W1-05
      - TASK-W1-06
      - TASK-W1-07
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_programme_onboarding
    verify_command_secondary: .venv/bin/python -m tests.verify.verify_agent_catalogue
    ground_command: null
    prior_wave: W0
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-014-W0.md
    head_ref_hint: develop
    head_sha_hint: e17319dc0fbef5ad3c723ec26dab75fb8ed82797
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    head_ref: develop
```

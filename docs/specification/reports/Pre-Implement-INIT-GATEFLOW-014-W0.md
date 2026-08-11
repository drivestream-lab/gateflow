## Pre-implement — gateflow / W0 — Seed platform_admin + JWT mint/login edge

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-014-W0.md` |
| Initiative | INIT-GATEFLOW-014 |
| Wave | W0 |
| Date | 2026-08-11 |
| Outcome | `blocked` |
| Outcome reason | Board seed partial — wave issues exist with TASK ids but are not GitHub sub-issues of EPIC #214 (PI-02). PI-01 (`spec-lgtm`) cleared on re-check. |
| Wave head context | Bound by Forge/human context: `develop` @ `b6a33a7` — not opened by this skill |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — on `develop` (not `chore/*-spec-*`) |
| Spec PR merged | Implementation plan on integration branch | [x] yes — PR [#212](https://github.com/drivestream-lab/gateflow/pull/212) MERGED to `develop` (`mergeCommit` `ae77433…`); plan present at `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-014.md` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — label `spec-lgtm` present on closed PR #212 (re-applied 2026-08-11T02:05:28Z by @nikd10x; `spec-pending` removed); Approve @0xbeefdead `commit_id` `4df184c…` matches `headRefOid` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body; waves are **sub-issues of the EPIC** | [ ] partial — EPIC [#214](https://github.com/drivestream-lab/gateflow/issues/214) + waves [#215](https://github.com/drivestream-lab/gateflow/issues/215)–[#219](https://github.com/drivestream-lab/gateflow/issues/219) exist on `drivestream-lab Board` (Todo); W0 body lists TASK-W0-01…06 and prose “Part of #214”; GraphQL `parent: null` / EPIC `subIssues: []` / `trackedIssues: []` — **not** formal sub-issues (**PI-02**) |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — re-validated this session |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [x] complete — W0 TASK-W0-01…06 in §9 YAML |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` (not unit-as-live) | [x] contract — `applicable: true`; `.venv/bin/python -m tests.verify.verify_jwt_login`; FILE `tests/verify/verify_jwt_login.py` (to create in `/loop-spec`) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — H3 rev `1`; H2 `sha256:53bb4c4f204888154afc40385c7e717f92d39f98463fcc6e97694e465a0ac9ef` |
| Product-spec H1–H3 spend freshness | live durable roots match citations | [x] current — H1 `shasum -a 256` = `e8c5103ea55a16823bf6a4e5c10bfc34be8e9f94efee12f6a3da69722fc3ea3e` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies; else command or N/A with reason | [x] `.venv/bin/python -m tests.verify.verify_jwt_login` |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` uses as-built + spec citations |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` listed | [x] path — `tests/verify/verify_jwt_login.py` (planned FILE-W0-12) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] N/A — W0 first wave of INIT-GATEFLOW-014 |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] N/A — W0 |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] complete — 2026-08-10, @nikd10x, Draft spec PR #212 |

**Gate verdict:** BLOCKED — wave issues not linked as GitHub sub-issues of EPIC #214 (**PI-02**). Do not start `/loop-spec` until PI-02 is cleared and `/pre-implement W0` re-runs to PASS.

**Resolved since prior checklist:** **PI-01** — `spec-lgtm` restored on PR #212 (2026-08-11); Approve `commit_id` matches `headRefOid`.

**Forge readiness (board seed partial):** Issues already exist — do **not** re-seed duplicates via blind `/create-board-tickets`. Human/Forge must link [#215](https://github.com/drivestream-lab/gateflow/issues/215)–[#219](https://github.com/drivestream-lab/gateflow/issues/219) as **sub-issues** of EPIC [#214](https://github.com/drivestream-lab/gateflow/issues/214) (GitHub parent/sub-issue relationship — prose “Part of #214” is insufficient). Optional: move W0 [#215](https://github.com/drivestream-lab/gateflow/issues/215) → In Progress (still Todo). This skill does **not** mutate GitHub.

**Blocker registry (this report):**

| Id | Gate | Status | Evidence |
|----|------|--------|----------|
| PI-01 | Coding-readiness `spec-lgtm` | **resolved** | Label present on #212; Approve `4df184c…` = `headRefOid` |
| PI-02 | Board sub-issue seed | **open** | #215 `parent: null`; EPIC #214 `subIssues.nodes: []` |

---

### Contracts consumed (from prior Ground Report)

> W0 has no prior Ground Report. Baseline contracts below are confirmed from
> `source_roots` (as-built + live code), not from a prior wave Ground Report.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| JWT verify middleware sets request auth | `AuthMiddleware.dispatch` (`src/common/auth/middleware.py`) | `Authorization: Bearer <jwt>`; config issuer/audience/algorithm/keys; `public_paths` allowlist | On success: `request.state.auth` = `AuthContext` (`user_id`, optional `tenant_id`, `role` as string, optional `owner_id`); on failure: HTTP 401 envelope `UNAUTHORIZED` | as-built + source | [x] yes — product prefixes still on `public_paths` in `src/app.py` (W0 must **not** change allowlist; deferred W2 per plan E6) |
| Auth context DTO | `AuthContext` (`src/models/auth_models.py`) | construction fields as above | validated model `extra=forbid`; `role: str` today | source | [x] yes — W0 TASK-W0-01 retypes `role` to `RoleType` enum |
| App composition mounts AuthMiddleware | `create_app` (`src/app.py`) | `JWTSettings` + `AuthConfig` | middleware chain includes `AuthMiddleware` | source | [x] yes |
| Login / seed / user-identity persistence | (not built) | — | — | — | [ ] NO — unconfirmed / net-new this wave |

**Unconfirmed contracts** (prior wave not yet grounded or source not found):
- Login API request/response wire shape (`POST /api/auth/login`) — net-new; define per TDD / plan TASK-W0-05.
- User identity store schema/repository — net-new; TASK-W0-03/04.
- Exact minted JWT claim set (`sub`, `role`, `tenant_id`, `iss`/`aud`/`exp`/`iat`) — TDD §3.1/E5 and ADR-014; middleware currently defaults missing `role` to `"tenant_admin"` — W0 TASK-W0-06 aligns claim extraction without a second verification stack.
- Codegraph MCP returned no matches previously; contracts confirmed via direct `source_roots` reads.

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered):
  - [x] `architecture.mdc` — JWT verification, `api/auth/`, `public_paths`
  - [x] `pydantic-schemas.mdc` — Domain enums (`RoleType`), models in `src/models/` only
  - [x] `http-api-conventions.mdc` — POST login body model
  - [x] `repository-pattern.mdc` — user identity ORM in repository only
  - [x] `dependency-injection.mdc` — seed script `configure_container()`
  - [x] `fail-fast.mdc` — invalid login / bad JWT refuse closed
  - [x] `testing-verify-flows.mdc` — unit vs live; co-ship `tests/verify/`
  - [x] `strong-typing.mdc` — closed role vocabulary
  - [x] `python-imports.mdc` — top-of-file imports
  - [x] `database-migrations.mdc` — human-owned Alembic if schema lands
  - [x] `logging-loguru.mdc` — structured kwargs for new services
  - [ ] skipped: `infra-services.mdc` — no new outbound infra client this wave
- [x] ADRs (keyword-matched):
  - [x] ADR-014 — JWT-only product edge; reuse `AuthMiddleware` (**Accepted**)
  - [ ] ADR-015 / ADR-016 — out of W0 scope
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-014-gateflow.md` (W0: REQ-01–07, REQ-43, REQ-47)
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-014.md` W0
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/215 — TASK list (projection only):
  - [ ] TASK-W0-01 — REQ-06 — `src/models/role_types.py` create; `src/models/auth_models.py` modify — exit: reject non-enum role; proof: `make check && pytest tests/unit/test_auth_middleware.py -k role -q`
  - [ ] TASK-W0-02 — REQ-05 — `tests/unit/test_auth_middleware.py` create — exit: 6+ negative 401 cases; proof: `pytest tests/unit/test_auth_middleware.py -v`
  - [ ] TASK-W0-03 — REQ-01 — user identity schema + repository create — exit: create+read by credential id; proof: `pytest tests/unit/test_user_identity_repository.py -q`
  - [ ] TASK-W0-04 — REQ-01, REQ-47 — `scripts/seed_platform_admin.py` create — exit: double-run → one row, two valid JWTs
  - [ ] TASK-W0-05 — REQ-02, REQ-03, REQ-43 — `auth_identity_service.py` + `login_routes.py` create — exit: happy 200+JWT / invalid 401 `UNAUTHORIZED`
  - [ ] TASK-W0-06 — REQ-04, REQ-06, REQ-07 — `middleware.py` claim extraction only; `tests/verify/verify_jwt_login.py` create — exit: JWT round-trips to correct `AuthContext`

---

### Governance alignment

- [x] Slice spec does not contradict Accepted ADR-014 for W0
- [x] Plan TASK MDC / ADR notes for W0 reviewed
- [x] ADR-014 **Accepted** in `docs/specification/adr/`

---

### Must update (in the same change as the code — via `/loop-spec`)

> Do **not** start until gate verdict is PASS on re-run.

- [ ] Product spec — only if behavior text drifts
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-GATEFLOW-014 W0 row
- [ ] `tests/README.md` — feature map for `verify_jwt_login`
- [ ] Unit: `tests/unit/test_auth_middleware.py`, `test_auth_identity_service.py`, `test_user_identity_repository.py`
- [ ] Live: `tests/verify/verify_jwt_login.py` (human-run at `wave-acceptance`)
- [ ] ADR — no supersession expected in W0

---

### Must not

- [ ] Implement against Accepted ADR contradictions without superseding
- [ ] Duplicate unit assertions in live smoke
- [ ] Assume prior-wave contracts without Ground Report (or flag unconfirmed)
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Change `public_paths` product-prefix allowlist in W0 (deferred to W2)
- [ ] Invent a second JWT verification stack (ADR-014)

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | Format, lint, types, layers | `make check` |
| Unit | Role enum, middleware negatives, identity repo, login paths, claim shape | `make test` |
| Live verify | Seed-mint + login happy + login refuse (human at `wave-acceptance`) | `.venv/bin/python -m tests.verify.verify_jwt_login` |
| Ground check | W0 REQs / boundaries | N/A — `/ground-spec` vs as-built + spec |

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] Run `.venv/bin/python -m tests.verify.verify_jwt_login`
- [ ] Signal accept with GitHub label `wave-accepted` on the tip

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-014
- Issue: [#215](https://github.com/drivestream-lab/gateflow/issues/215) (EPIC [#214](https://github.com/drivestream-lab/gateflow/issues/214))
- Spec path: `docs/specification/product/INIT-GATEFLOW-014-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_jwt_login`
- ADRs in scope: ADR-014 (W0)
- Wave head: `develop` @ `b6a33a7`

---

### Checklist publish readiness (blocked — not pass)

| Field | Value |
|-------|-------|
| Workflow outcome | `blocked` — PI-02 unsatisfied |
| Next | `wave-signoff` (`human-checkpoint`) — `human_checkpoint: true`, `external_action: false` |
| Forge (this hop) | `commit_workspace` to publish updated blocked checklist when authorized |
| Remediation | Link #215–#219 as sub-issues of #214; re-run `/pre-implement W0` |
| Later | Only after re-run **pass**: `/commit-workspace` → `/loop-spec` |

---

### Merge order (if cross-module / cross-service)

N/A — W0 single-repo (gateflow).

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: blocked
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-014-W0.md
  blockers:
    - PI-02
  signals:
    initiative: INIT-GATEFLOW-014
    wave: W0
    board_epic: "https://github.com/drivestream-lab/gateflow/issues/214"
    board_wave_issue: "https://github.com/drivestream-lab/gateflow/issues/215"
    board_seed: partial
    spec_pr: "https://github.com/drivestream-lab/gateflow/pull/212"
    spec_lgtm_at_merge: true
    pe_signoff: complete
    workmanifest_contract: pass
    pi_01_status: resolved
    pi_02_status: open
    tasks:
      - TASK-W0-01
      - TASK-W0-02
      - TASK-W0-03
      - TASK-W0-04
      - TASK-W0-05
      - TASK-W0-06
    check_command: "make check"
    test_command: "make test"
    verify_command: ".venv/bin/python -m tests.verify.verify_jwt_login"
    ground_command: null
    wave_head: develop
    remediation:
      - link_issues_215_219_as_subissues_of_214
      - re_run_pre_implement_W0
    codegraph_provider: degraded-none
    grounding_depth: light
  next_candidates:
    - wave-signoff
  human_checkpoint: true
  external_action: false
  forge:
    action: commit_workspace
    draft: false
    title: "docs(INIT-GATEFLOW-014): Pre-Implement W0 blocked — PI-02 only"
    body_path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-014-W0.md
```

## Pre-implement — gateflow / W0 — Seed platform_admin + JWT mint/login edge

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-014-W0.md` |
| Initiative | INIT-GATEFLOW-014 |
| Wave | W0 |
| Date | 2026-08-11 |
| Outcome | `pass` |
| Outcome reason | All W0 gates satisfied: PE sign-off, spec-lgtm on merged tip, WorkManifest pass, board EPIC+#215–#219 with formal sub-issue links, commands + P15 live contract resolved. |
| Wave head context | Bound by Forge/human context: `develop` @ `51975e6` — not opened by this skill |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — on `develop` |
| Spec PR merged | Implementation plan on integration branch | [x] yes — PR [#212](https://github.com/drivestream-lab/gateflow/pull/212) MERGED (`ae77433…`); plan on tree |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — label `spec-lgtm` present; Approve @0xbeefdead `commit_id` `4df184c…` = `headRefOid` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present; waves are **sub-issues of the EPIC** | [x] seeded — EPIC [#214](https://github.com/drivestream-lab/gateflow/issues/214); waves [#215](https://github.com/drivestream-lab/gateflow/issues/215)–[#219](https://github.com/drivestream-lab/gateflow/issues/219) as `subIssues`; #215 `parent` = #214; W0 body lists TASK-W0-01…06 |
| WorkManifest contract | `prayog/v1` §9 passes `workmanifest_contract.py` | [x] pass |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` | [x] complete — TASK-W0-01…06 |
| Live-verification contract | P15: `verification.live` applicable + script under `live_verify_dir` | [x] contract — `.venv/bin/python -m tests.verify.verify_jwt_login` |
| Plan source freshness | all upstream rows `CURRENT` | [x] current |
| Impact-map repo scope | revision and scope digest match | [x] match — H3 `1`; H2 `sha256:53bb4c4f204888154afc40385c7e717f92d39f98463fcc6e97694e465a0ac9ef` |
| Product-spec H1–H3 spend freshness | live durable roots match citations | [x] current — H1 `e8c5103ea55a16823bf6a4e5c10bfc34be8e9f94efee12f6a3da69722fc3ea3e` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script when P15 | [x] `.venv/bin/python -m tests.verify.verify_jwt_login` |
| `ground_command` | resolved or N/A | [x] N/A — `/ground-spec` uses as-built + spec |
| Co-shipped live verify (P15) | FILE under `live_verify_dir` | [x] `tests/verify/verify_jwt_login.py` (FILE-W0-12) |
| Prior wave as-built row | `human_approved` | [x] N/A — W0 first wave |
| Prior Ground Report exists | W{N-1} | [x] N/A — W0 |
| Plan PE sign-off (W0 only) | §0 marked complete | [x] complete — 2026-08-10, @nikd10x, PR #212 |

**Gate verdict:** PASS — ready for Forge `commit_workspace` (this checklist) then `/loop-spec`.

**Notes (non-blocking):** W0 [#215](https://github.com/drivestream-lab/gateflow/issues/215) board Status is still **Todo** (optional `wave-in-progress-action`). PI-01/PI-02 from prior blocked checklists are **resolved**.

**Blocker registry:** none open.

---

### Contracts consumed (from prior Ground Report)

> W0 has no prior Ground Report. Baseline from `source_roots`.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| JWT verify middleware sets request auth | `AuthMiddleware.dispatch` (`src/common/auth/middleware.py`) | Bearer JWT; issuer/audience/algorithm/keys; `public_paths` | `request.state.auth` = `AuthContext` or HTTP 401 `UNAUTHORIZED` | source | [x] yes — product prefixes still public; W0 must **not** change allowlist (W2) |
| Auth context DTO | `AuthContext` (`src/models/auth_models.py`) | user_id, optional tenant_id, role str, optional owner_id | `extra=forbid` model | source | [x] yes — TASK-W0-01 retypes `role` → `RoleType` |
| App mounts AuthMiddleware | `create_app` (`src/app.py`) | `JWTSettings` + `AuthConfig` | middleware wired | source | [x] yes |
| Login / seed / user-identity persistence | (not built) | — | — | — | [ ] NO — net-new W0 |

**Unconfirmed contracts:**
- `POST /api/auth/login` wire shape — TASK-W0-05
- User identity schema/repository — TASK-W0-03/04
- Exact claim set (`sub`, `role`, `tenant_id`, `iss`/`aud`/`exp`/`iat`) — TDD §3.1/E5 + ADR-014; middleware today defaults missing `role` to `"tenant_admin"` — TASK-W0-06 aligns without a second verifier

---

### Must read

- [x] `AGENTS.md`
- [x] MDC (domain-filtered): `architecture.mdc`, `pydantic-schemas.mdc`, `http-api-conventions.mdc`, `repository-pattern.mdc`, `dependency-injection.mdc`, `fail-fast.mdc`, `testing-verify-flows.mdc`, `strong-typing.mdc`, `python-imports.mdc`, `database-migrations.mdc`, `logging-loguru.mdc`
  - skipped: `infra-services.mdc` (no new outbound client)
- [x] ADRs: **ADR-014** (Accepted) — JWT-only edge; reuse `AuthMiddleware`
  - ADR-015/016 out of W0 scope
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-014-gateflow.md` (REQ-01–07, REQ-43, REQ-47)
- [x] Plan §9: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-014.md` W0
- [x] Board: https://github.com/drivestream-lab/gateflow/issues/215 — TASK projection:
  - [ ] TASK-W0-01 — REQ-06 — `src/models/role_types.py` create; `src/models/auth_models.py` modify — reject non-enum role; proof: `make check && pytest tests/unit/test_auth_middleware.py -k role -q`
  - [ ] TASK-W0-02 — REQ-05 — depends TASK-W0-01 — `tests/unit/test_auth_middleware.py` create — 6+ negative 401 cases
  - [ ] TASK-W0-03 — REQ-01 — user identity schema + repository create — create+read by credential id
  - [ ] TASK-W0-04 — REQ-01, REQ-47 — depends TASK-W0-03 — `scripts/seed_platform_admin.py` — double-run → one row, two JWTs
  - [ ] TASK-W0-05 — REQ-02, REQ-03, REQ-43 — depends TASK-W0-03 — `auth_identity_service.py` + `login_routes.py` — happy 200+JWT / invalid 401
  - [ ] TASK-W0-06 — REQ-04, REQ-06, REQ-07 — depends TASK-W0-05 — `middleware.py` claim extraction only + `tests/verify/verify_jwt_login.py` — JWT round-trips to correct `AuthContext`

**DAG order for `/loop-spec`:** TASK-W0-01 → TASK-W0-02; TASK-W0-03 → TASK-W0-04 and TASK-W0-05 → TASK-W0-06. (01∥03 may proceed in parallel.)

---

### Governance alignment

- [x] Spec does not contradict ADR-014 for W0
- [x] Plan TASK MDC / ADR notes reviewed
- [x] ADR-014 **Accepted** in `docs/specification/adr/`

---

### Must update (same change as code — via `/loop-spec`)

- [ ] `docs/specification/as-built/implementation-status.md` — INIT-GATEFLOW-014 W0 row
- [ ] `tests/README.md` — feature map for `verify_jwt_login`
- [ ] Unit: `test_auth_middleware.py`, `test_auth_identity_service.py`, `test_user_identity_repository.py`
- [ ] Live: `tests/verify/verify_jwt_login.py` (human-run at `wave-acceptance`)
- [ ] ADR — no supersession in W0

---

### Must not

- [ ] Contradict Accepted ADR without superseding
- [ ] Duplicate unit assertions in live smoke
- [ ] Assume unconfirmed contracts without flagging
- [ ] Open branch / commit / push / PR / labels / board issues from this skill
- [ ] Change `public_paths` product-prefix allowlist in W0 (deferred W2)
- [ ] Invent a second JWT verification stack (ADR-014)

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | Format, lint, types, layers | `make check` |
| Unit | Role enum, middleware negatives, identity repo, login paths, claim shape | `make test` |
| Live verify | Seed-mint + login happy + refuse (human at `wave-acceptance`) | `.venv/bin/python -m tests.verify.verify_jwt_login` |
| Ground check | W0 REQs / boundaries | N/A — `/ground-spec` |

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] Run `.venv/bin/python -m tests.verify.verify_jwt_login` (API up; JWT key material)
- [ ] Label tip `wave-accepted` (skills do not apply labels)

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-014
- Issue: [#215](https://github.com/drivestream-lab/gateflow/issues/215) (EPIC [#214](https://github.com/drivestream-lab/gateflow/issues/214))
- Spec path: `docs/specification/product/INIT-GATEFLOW-014-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_jwt_login`
- ADRs in scope: ADR-014
- Wave head: `develop` @ `51975e6` (Forge/human may bind `feature/INIT-GATEFLOW-014-w0-*` before coding)

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — gates satisfied |
| Next | `loop-spec` (`skill`) — `human_checkpoint: false`, `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish this PASS checklist to bound `head_ref` |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR |

Recommend `/commit-workspace` after explicit authorization, then `/loop-spec`. Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

N/A — W0 single-repo (gateflow).

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-014-W0.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-014
    wave: W0
    board_epic: "https://github.com/drivestream-lab/gateflow/issues/214"
    board_wave_issue: "https://github.com/drivestream-lab/gateflow/issues/215"
    board_seed: seeded
    spec_pr: "https://github.com/drivestream-lab/gateflow/pull/212"
    spec_lgtm_at_merge: true
    pe_signoff: complete
    workmanifest_contract: pass
    pi_01_status: resolved
    pi_02_status: resolved
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
    codegraph_provider: degraded-none
    grounding_depth: light
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    draft: false
    title: "docs(INIT-GATEFLOW-014): Pre-Implement W0 PASS checklist"
    body_path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-014-W0.md
```

## Pre-implement — gateflow / W0 — Seed platform_admin + JWT mint/login edge

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-014-W0.md` |
| Initiative | INIT-GATEFLOW-014 |
| Wave | W0 |
| Date | 2026-08-10 |
| Outcome | `blocked` |
| Outcome reason | Spec merge coding-readiness incomplete (`spec-lgtm` not on merged tip) and board seed partial (wave issues exist but are not GitHub sub-issues of EPIC #214). |
| Wave head context | Bound by Forge/human context: `develop` @ `a8ea0c5` — not opened by this skill |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — on `develop` (not `chore/*-spec-*`) |
| Spec PR merged | Implementation plan on integration branch | [x] yes — PR [#212](https://github.com/drivestream-lab/gateflow/pull/212) MERGED to `develop` (`mergeCommit` `ae77433…`); plan present at `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-014.md` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [ ] missing — timeline: `spec-lgtm` labeled 13:24:23Z then **unlabeled** 13:24:59Z; re-labeled `spec-pending`; Approve by @0xbeefdead on `4df184c…` (matches `headRefOid`) but label absent at merge 13:26:07Z; post-merge labels still only `spec-pending` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [ ] partial — EPIC [#214](https://github.com/drivestream-lab/gateflow/issues/214) + waves [#215](https://github.com/drivestream-lab/gateflow/issues/215)–[#219](https://github.com/drivestream-lab/gateflow/issues/219) exist on `drivestream-lab Board` (Todo); W0 body lists TASK-W0-01…06 and “Part of #214”; GraphQL `parent: null` / EPIC `subIssues: []` — **not** formal sub-issues |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `python3 prayog-skills/scripts/workmanifest_contract.py docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-014.md --base-path .` → “WorkManifest contract passed.” |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [x] complete — W0 TASK-W0-01…06 in §9 YAML |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` (not unit-as-live) | [x] contract — `applicable: true`; `.venv/bin/python -m tests.verify.verify_jwt_login`; FILE `tests/verify/verify_jwt_login.py` (to create in `/loop-spec`) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — plan § Source freshness all CURRENT |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — H3 rev `1`; H2 `sha256:53bb4c4f204888154afc40385c7e717f92d39f98463fcc6e97694e465a0ac9ef` matches local meta impact map + product-spec citations |
| Product-spec H1–H3 spend freshness | live durable roots match citations | [x] current — H1 `shasum -a 256` of `prayog-meta/prd/INIT-GATEFLOW-014.md` = `e8c5103ea55a16823bf6a4e5c10bfc34be8e9f94efee12f6a3da69722fc3ea3e` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies; else command or N/A with reason | [x] `.venv/bin/python -m tests.verify.verify_jwt_login` |
| `ground_command` | resolved or N/A with reason | [x] N/A — repo has no dedicated ground-truth script; `/ground-spec` uses as-built + spec citations |
| Co-shipped live verify (P15) | If wave adds/changes product surface: FILE path under `live_verify_dir` listed | [x] path — `tests/verify/verify_jwt_login.py` (planned FILE-W0-12) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] N/A — W0 first wave of INIT-GATEFLOW-014 |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] N/A — W0; no prior Ground Report required |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] complete — 2026-08-10, @nikd10x, Draft spec PR #212 |

**Gate verdict:** BLOCKED — `spec-lgtm` not retained on merged spec PR tip (**PI-01**); wave issues not linked as GitHub sub-issues of EPIC #214 (**PI-02**). Do not start `/loop-spec` until both are cleared and `/pre-implement W0` re-run.

**Forge readiness (when seed / wave head absent):** Issues already exist — do **not** blindly re-seed duplicates. Human/Forge must (1) restore coding-readiness attestation for merged tip of [#212](https://github.com/drivestream-lab/gateflow/pull/212) (`spec-lgtm` on the approved head / merge evidence chain), and (2) link [#215](https://github.com/drivestream-lab/gateflow/issues/215)–[#219](https://github.com/drivestream-lab/gateflow/issues/219) as **sub-issues** of EPIC [#214](https://github.com/drivestream-lab/gateflow/issues/214). Optional: move W0 [#215](https://github.com/drivestream-lab/gateflow/issues/215) → In Progress via `wave-in-progress-action` (still Todo). This skill does **not** mutate GitHub.

**Blocker registry (this report):**

| Id | Gate | Evidence |
|----|------|----------|
| PI-01 | Coding-readiness `spec-lgtm` | PR #212 timeline unlabeled `spec-lgtm` before merge; current labels = `spec-pending` only |
| PI-02 | Board sub-issue seed | `gh api graphql` issue #215 `parent: null`; EPIC #214 `subIssues.nodes: []` |

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
- Login API request/response wire shape (`POST /api/auth/login`) — net-new; define per TDD / plan TASK-W0-05; no Ground Report backing.
- User identity store schema/repository — net-new; TASK-W0-03/04.
- Exact minted JWT claim set (`sub`, `role`, `tenant_id`, `iss`/`aud`/`exp`/`iat`) — specified in TDD §3.1/E5 and ADR-014; middleware currently defaults missing `role` to `"tenant_admin"` (fail-soft) — W0 must align claim extraction with enum + ADR-014 (TASK-W0-06) without inventing a second verification stack.
- Codegraph MCP (`user-prayog-fleet-cbm` / `data-repos-prayog-gateflow`) returned no matches for these symbols this session — contracts confirmed via direct `source_roots` reads only.

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered — list files read for this slice's domains):
  - [x] `architecture.mdc` — JWT verification, `api/auth/`, `public_paths`, service layout
  - [x] `pydantic-schemas.mdc` — Domain enums (`RoleType`), models in `src/models/` only
  - [x] `http-api-conventions.mdc` — POST login body model, not query
  - [x] `repository-pattern.mdc` — user identity ORM confined to repository
  - [x] `dependency-injection.mdc` — seed script uses `configure_container()`; settings via `get_instance()`
  - [x] `fail-fast.mdc` — invalid login / bad JWT refuse closed
  - [x] `testing-verify-flows.mdc` — unit vs live; co-ship `tests/verify/`
  - [x] `strong-typing.mdc` — no bare `str` for closed role vocabulary
  - [x] `python-imports.mdc` — top-of-file imports; service module naming
  - [x] `database-migrations.mdc` — human-owned Alembic if schema lands (note: W0 creates schema modules; human DDL workflow)
  - [x] `logging-loguru.mdc` — structured kwargs (skim for new services)
  - [ ] skipped: `infra-services.mdc` — no new outbound infra client this wave
  - [ ] skipped: `code-guidelines-index.mdc` — index only
  - [ ] skipped: `spec-driven-development.mdc` / `python-tooling.mdc` — process/tooling already carried by plan commands
- [x] ADRs (keyword-matched — list ids):
  - [x] ADR-014 — JWT-only product edge; reuse existing `AuthMiddleware` decode path; no second verification stack (**Accepted**)
  - [ ] ADR-015 — Programme-scoped forge credentials — out of W0 scope (W1/W2)
  - [ ] ADR-016 — Tenant-scoped run/board/checkpoint auth — out of W0 scope (W2)
  - Superseded context (do not implement against): ADR-002 / ADR-005 / ADR-011 zone model — superseded by ADR-014
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-014-gateflow.md` (W0: REQ-01–07, REQ-43, REQ-47)
- [x] Plan wave section / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-014.md` W0
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/215 — TASK list (projected from WorkManifest; not a second authority):
  - [ ] TASK-W0-01 — implements REQ-06 — depends_on: [] — files: `src/models/role_types.py` create; `src/models/auth_models.py` modify — exit: `AuthContext(role=...)` rejects non-enum string; proof: `make check && pytest tests/unit/test_auth_middleware.py -k role -q`
  - [ ] TASK-W0-02 — implements REQ-05 — depends_on: [TASK-W0-01] — files: `tests/unit/test_auth_middleware.py` create — exit: 6+ negative-path 401 cases; proof: `pytest tests/unit/test_auth_middleware.py -v`
  - [ ] TASK-W0-03 — implements REQ-01 — depends_on: [] — files: user identity schema + repository create — exit: create+read by credential id; proof: `pytest tests/unit/test_user_identity_repository.py -q`
  - [ ] TASK-W0-04 — implements REQ-01, REQ-47 — depends_on: [TASK-W0-03] — files: `scripts/seed_platform_admin.py` create — exit: double-run → one row, two valid JWTs; proof: seed script twice; live also via `verify_jwt_login`
  - [ ] TASK-W0-05 — implements REQ-02, REQ-03, REQ-43 — depends_on: [TASK-W0-03] — files: `auth_identity_service.py` + `login_routes.py` create — exit: happy 200+JWT / invalid 401 `UNAUTHORIZED` zero token; proof: `pytest tests/unit/test_auth_identity_service.py -v`
  - [ ] TASK-W0-06 — implements REQ-04, REQ-06, REQ-07 — depends_on: [TASK-W0-05] — files: `middleware.py` modify (claim extraction only); `tests/verify/verify_jwt_login.py` create — exit: minted JWT round-trips to correct `AuthContext`; proof: `pytest … -k claim_shape`; evidence_expected includes `wave-accepted` on tip

---

### Governance alignment

- [x] Slice spec does not contradict Accepted ADR-014 for W0 (mint/login + middleware claim shape; no second verifier; `public_paths` product-prefix removal deferred to W2)
- [x] Plan TASK MDC notes and ADR notes for W0 reviewed (enums, pytest scope, repository isolation, DI for seed, HTTP POST body, ADR-014 claim shape)
- [x] Every initiative ADR cited for this wave is **Accepted** in `docs/specification/adr/` — W0 cites ADR-014 only; ADR-015/016 Accepted but not in W0 TASK ADR notes as blockers

---

### Must update (in the same change as the code — via `/loop-spec`)

> Do **not** start until gate verdict is PASS on re-run.

- [ ] Product spec — `docs/specification/product/INIT-GATEFLOW-014-gateflow.md` (as-built citations / status only if behavior text drifts; prefer as-built for live matrix)
- [ ] `docs/specification/as-built/implementation-status.md` — verification row for INIT-GATEFLOW-014 W0
- [ ] `tests/README.md` — feature map row for `verify_jwt_login`
- [ ] Unit verification scope — `tests/unit/test_auth_middleware.py`, `test_auth_identity_service.py`, `test_user_identity_repository.py`
- [ ] Live verification — co-shipped `tests/verify/verify_jwt_login.py` (human-run at `wave-acceptance`)
- [ ] ADR — no supersession expected in W0 (ADR-014 already Accepted)

---

### Must not

- [ ] Implement against spec wording that contradicts an Accepted ADR without first superseding that ADR
- [ ] Duplicate unit verification assertions in live smoke scripts
- [ ] Assume a contract from a prior wave is correct without checking the Ground Report (or flagging it as unconfirmed above)
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Change `public_paths` product-prefix allowlist in W0 (deferred to W2)
- [ ] Invent a second JWT verification stack alongside `AuthMiddleware` (ADR-014)

---

### Verification plan

| Layer | What it proves | Command (from tests_readme / profile) |
|-------|----------------|---------------------------------------|
| Static check | Formatting, linting, types, layers | `make check` |
| Unit | Role enum, middleware negatives, identity repo, login service paths, claim shape | `make test` (targeted: auth middleware / identity / auth_identity unit modules per plan TEST-W0-U) |
| Live verify | Seed-mint + login happy + login refuse on running stack (human at `wave-acceptance`) | `.venv/bin/python -m tests.verify.verify_jwt_login` |
| Ground check | Assigned W0 REQs satisfied; boundaries respected | N/A — `/ground-spec` vs as-built + spec (no runnable ground command) |

> P15 applies: live verify is required; unit-only would block.
> Agent implements the script in `/loop-spec`; does **not** run it as success.
> Policy: live-smoke-policy.md.

### Human wave-acceptance (after loop-spec + Draft PR)

When checklist PASS and coding is green, the human at checkpoint
`wave-acceptance`:

- [ ] Run `.venv/bin/python -m tests.verify.verify_jwt_login` (API up; JWT key material configured)
- [ ] Experience / inspect seed + login paths to the depth env access allows
- [ ] Signal accept with GitHub label `wave-accepted` on the tip — content skills do **not** apply labels
- [ ] Apply tip hygiene for any hotfixes before Enter-at Pass-2 closeout
- [ ] Optional/legacy notes may land in `Live-Verify-*` — not required for the gate

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-014
- Issue: [#215](https://github.com/drivestream-lab/gateflow/issues/215) (EPIC [#214](https://github.com/drivestream-lab/gateflow/issues/214))
- Spec path: `docs/specification/product/INIT-GATEFLOW-014-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_jwt_login`
- ADRs in scope: ADR-014 (W0); ADR-015/016 later waves
- Wave head: bound by Forge/human context — `develop` (coding branch not cut until gates pass)

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `blocked` — PI-01 + PI-02 unsatisfied |
| Next | `wave-signoff` (`human-checkpoint`) — `human_checkpoint: true`, `external_action: false` |
| Forge (this hop) | Publish this blocked checklist via `commit_workspace` when authorized; **do not** open Draft PR or start `/loop-spec` |
| Remediation (human/Forge) | Restore `spec-lgtm` attestation chain for PR #212; link wave issues as sub-issues of #214; re-run `/pre-implement W0` |
| Later | Only after re-run **pass**: `/commit-workspace` checklist → `/loop-spec` → `wave-pr-action` |

Recommend `/commit-workspace` only to publish this blocked artifact after explicit authorization. Do not open the PR here. Do not implement.

---

### Merge order (if cross-module / cross-service)

N/A — W0 is single-repo (gateflow); no cross-service merge dependency for this wave.

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: blocked
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-014-W0.md
  blockers:
    - PI-01
    - PI-02
  signals:
    initiative: INIT-GATEFLOW-014
    wave: W0
    board_epic: "https://github.com/drivestream-lab/gateflow/issues/214"
    board_wave_issue: "https://github.com/drivestream-lab/gateflow/issues/215"
    board_seed: partial
    spec_pr: "https://github.com/drivestream-lab/gateflow/pull/212"
    spec_lgtm_at_merge: false
    pe_signoff: complete
    workmanifest_contract: pass
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
      - restore_spec_lgtm_attestation_on_pr_212
      - link_issues_215_219_as_subissues_of_214
      - re_run_pre_implement_W0
    codegraph_provider: mcp-user-prayog-fleet-cbm
    grounding_depth: light
  next_candidates:
    - wave-signoff
  human_checkpoint: true
  external_action: false
  forge:
    action: commit_workspace
    draft: false
    title: "docs(INIT-GATEFLOW-014): Pre-Implement W0 blocked checklist"
    body_path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-014-W0.md
```

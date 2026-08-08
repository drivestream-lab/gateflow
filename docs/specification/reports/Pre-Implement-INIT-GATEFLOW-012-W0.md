## Pre-implement — drivestream-lab/gateflow / W0 — Tenant registry (data model + API)

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-012-W0.md` |
| Initiative | INIT-GATEFLOW-012 |
| Wave | W0 |
| Date | 2026-08-08 |
| Outcome | `pass` |
| Outcome reason | Spec merged with `spec-lgtm`; board seeded; WorkManifest contract pass; PE sign-off complete; H1–H3 CURRENT; P15 live verify co-shipped in plan |
| Wave head context | Bound context today: `develop` @ `b83006c2e7cdc8be96e1d4260f32c47c1328c56a` — not opened by this skill. Planned coding head from plan: `feature/INIT-GATEFLOW-012-w0-tenant-registry` (cut outside this skill before `/loop-spec`) |

---

### Gate check (prior wave)

> W0 has no prior Ground Report. Gate = plan §0 PE sign-off + spec merge + board seed.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — on `develop` (not `chore/*-spec-*`) |
| Spec PR merged | Implementation plan on integration branch | [x] yes — [#183](https://github.com/drivestream-lab/gateflow/pull/183) MERGED; plan on `develop` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — label `spec-lgtm` on closed PR; mergeCommit `b83006c…` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — [#185](https://github.com/drivestream-lab/gateflow/issues/185) sub-issue of EPIC [#184](https://github.com/drivestream-lab/gateflow/issues/184); body has TASK-W0-* |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` | [x] complete — TASK-W0-01…10 |
| Live-verification contract | P15: `verification.live` applicable + script under `live_verify_dir` | [x] contract — `.venv/bin/python -m tests.verify.verify_tenant_registry` |
| Plan source freshness | upstream H1–H3 / G1 CURRENT (plan digests walk-time only) | [x] current — H1/H2/H3/G1 match live meta |
| Impact-map repo scope | revision and scope digest match | [x] match — rev `1`; scope `sha256:85e75d8b…` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live under `live_verify_dir` (P15) | [x] `.venv/bin/python -m tests.verify.verify_tenant_registry` |
| `ground_command` | resolved or N/A | [x] N/A — `/ground-spec` is Pass-2 pin skill, not a Makefile target |
| Co-shipped live verify (P15) | FILE under `live_verify_dir` | [x] `tests/verify/verify_tenant_registry.py` (create in TASK-W0-09) |
| Prior wave as-built row | `human_approved` | [x] N/A — W0 first wave |
| Prior Ground Report exists | Ground-Report-W{N-1} | [x] N/A — W0 first wave |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] complete — 2026-08-08 @nikd10x; TDD Accepted; ADR-011 Accepted |

**Gate verdict:** PASS

---

### Contracts consumed (from prior Ground Report)

> No prior Ground Report (W0). Confirmed existing seams by scanning `src/` — net-new domain with precedents only.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Programme-token Bearer dependency precedent (pattern only; not reused for tenant zone) | `src/api/v1/programme_token.py` → `verify_programme_service_token` | Authorization Bearer header | void or UnauthorizedError | as-built / source | [x] yes — shape to mirror for ADR-011 Option A; **do not** populate JWT auth context |
| Board create request override precedent (REQ-08) | `BoardTicketCreateRequest` / `BoardService` | `project_owner` / `project_number` caller-supplied | ticket create response | `src/models/board_models.py`, `src/business_services/board_service.py` | [x] yes — tenant default applies when omitted; explicit wins |
| DI + repository layering | `RepositoryModule` / `InfraModule` / `BusinessServicesModule` | injected collaborators | singleton services | `src/di/modules/*` | [x] yes |
| Alembic human-owned versions | `postgres_migrations/env.py` imports schema modules | schema registration | metadata for migrations | `database-migrations.mdc` | [x] yes — agent updates schema + env.py only |

**Unconfirmed contracts** (net-new this wave — no Ground Report backing):
- Tenant aggregate persistence (`tenants` / `tenant_repos` / `tenant_users`) — **new**; human DDL required before live verify
- `github_pat_probe` per-call PAT read-access probe — **new** infra (not ForgeClient singleton credential)
- Tenant-scoped bearer token store/lookup — **new** fourth trust zone per ADR-011
- `POST/GET /api/v1/tenants*` routes — **new** product surface (P15)

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered for this slice):
  - [x] `architecture.mdc` — layer boundaries; JWT middleware stays untouched (G3)
  - [x] `http-api-conventions.mdc` — body-only POST; models from `src/models/`
  - [x] `pydantic-schemas.mdc` — tenant DTOs; no `pat` on responses
  - [x] `repository-pattern.mdc` — ORM only in repository
  - [x] `database-migrations.mdc` — no agent `versions/` files
  - [x] `dependency-injection.mdc` — `@inject` + module bindings
  - [x] `infra-services.mdc` — PAT probe as infra client
  - [x] `fail-fast.mdc` — 400/401/422 fail closed
  - [x] `logging-loguru.mdc` — never log PAT; IDs as kwargs
  - [x] `testing-verify-flows.mdc` — co-ship live verify
  - [x] `strong-typing.mdc` / `python-imports.mdc` — typed boundaries; top-level imports
- [x] ADRs (keyword-matched):
  - [x] ADR-011 — tenant-scoped bearer-token trust zone (**Accepted**) — REQ-03/04
  - [x] ADR-001 — Postgres SSOT / repo-only ORM / human Alembic — schema work
  - [x] ADR-002 / ADR-005 — existing trust zones unchanged; fourth zone is ADR-011 only
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` (REQ-01–09, REQ-32)
- [x] Plan wave section / §9: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-012.md` W0
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/185 — TASK list (projection):
  - [x] TASK-W0-01 — REQ-01,02,07,32 — models create — exit: absolute path + no pat on responses — command
  - [x] TASK-W0-02 — REQ-01,02,09 — schema + env.py + DDL-NOTE — exit: metadata registered; no agent versions/ — review
  - [x] TASK-W0-03 — REQ-01,02,04,32 — tenant repository + DI — exit: ORM↔Pydantic; no pat on read DTOs — command
  - [x] TASK-W0-04 — REQ-06 — github_pat_probe + DI — exit: ok/reason itemized; no persist — command
  - [x] TASK-W0-05 — REQ-01–09,32 (subset) — TenantService + DI — exit: all-or-nothing + one-time token — command
  - [x] TASK-W0-06 — REQ-03,04,05,32 — tenant_token + routes + mount — exit: 401 before body — command
  - [x] TASK-W0-07 — REQ-08 — board_service default apply — exit: omit→default; explicit wins — command
  - [x] TASK-W0-08 — REQ-01–04,06,07,32 — unit tests create — exit: matrix green — command
  - [x] TASK-W0-09 — REQ-04,06,32 — verify_tenant_registry + README — exit: live exit 0 — command
  - [x] TASK-W0-10 — REQ-01–09,32 — as-built row — exit: accurate W0 status — review

---

### Governance alignment

- [x] Slice spec does not contradict Accepted ADR-011 (fourth zone; Bearer dependency; no AuthMiddleware reuse)
- [x] Plan TASK MDC notes and ADR notes for W0 reviewed
- [x] ADR-011 is **Accepted** in `docs/specification/adr/`

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — only if OpenAPI field names deferred (Q-1) need a note; behavior already normative
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-012 W0 verification row (TASK-W0-10)
- [ ] `tests/README.md` — feature-map row for `verify_tenant_registry` (TASK-W0-09)
- [ ] Unit verification — `tests/unit/test_tenant_*.py`, `test_github_pat_probe.py`, `test_tenant_token.py`
- [ ] Live verification — `tests/verify/verify_tenant_registry.py` (human-run at `wave-acceptance`)
- [ ] ADR — none to supersede this wave (ADR-011 already Accepted)
- [ ] Human DDL — apply revision from `DDL-NOTE-INIT-GATEFLOW-012-W0-tenants.md` before live verify

---

### Must not

- [ ] Implement against wording that contradicts ADR-011 (e.g. reactivating JWT AuthMiddleware for tenant routes)
- [ ] Echo or log PAT / tenant bearer secret values
- [ ] Write files under `postgres_migrations/versions/` (human-owned)
- [ ] Treat board issue body as a second libre authority — spend TASK ids from WorkManifest / board projection only
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Claim live verify success inside `/loop-spec` — human runs smoke at `wave-acceptance`

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format, lint, types, layers | `make check` |
| Unit | register/attach/read; 400/401/422; no-pat; probe itemization | `make test` |
| Live verify | running API: register + attach + GET; 401/422 negatives; no pat in bodies (REQ-04,06,32) | `.venv/bin/python -m tests.verify.verify_tenant_registry` |
| Ground check | Pass-2 only | N/A — `/ground-spec` pin skill |

> P15 applies (new HTTP routes). Agent implements `verify_tenant_registry.py` in `/loop-spec`; does **not** run it as success evidence.

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] Run `.venv/bin/python -m tests.verify.verify_tenant_registry` (API up; human-applied tenant DDL; non-prod PAT)
- [ ] Confirm register returns token once; list/detail omit `pat`; bad PAT → itemized 422; bad token → 401
- [ ] Signal accept with GitHub label `wave-accepted` on the tip
- [ ] Cleanup synthetic tenant rows / scratch `workspace_root`
- [ ] Stop on non-zero exit or unexpected 5xx — do not start Pass-2

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-012
- Issue: [#185](https://github.com/drivestream-lab/gateflow/issues/185) (EPIC [#184](https://github.com/drivestream-lab/gateflow/issues/184))
- Spec path: `docs/specification/product/INIT-GATEFLOW-012-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_tenant_registry`
- ADRs in scope: ADR-011 (Accepted); ADR-001 (schema/migrations)
- Wave head: bound by Forge/human — currently `develop`; expected coding branch `feature/INIT-GATEFLOW-012-w0-tenant-registry`

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — all W0 gates satisfied; checklist ready for Forge publish |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish this file onto bound `head_ref` |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR |

Recommend `/commit-workspace` after explicit authorization (and after wave head is bound if coding will not land on `develop`). Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

N/A for W0 within gateflow. **External:** human Alembic apply before live verify. W1+ depend on W0 tenant registry + remounted `prayog-skills` pin (PE-1) — not this wave.

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-012-W0.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-012
    wave: W0
    board_issue: "https://github.com/drivestream-lab/gateflow/issues/185"
    epic_issue: "https://github.com/drivestream-lab/gateflow/issues/184"
    tasks:
      - TASK-W0-01
      - TASK-W0-02
      - TASK-W0-03
      - TASK-W0-04
      - TASK-W0-05
      - TASK-W0-06
      - TASK-W0-07
      - TASK-W0-08
      - TASK-W0-09
      - TASK-W0-10
    check_command: "make check"
    test_command: "make test"
    verify_command: ".venv/bin/python -m tests.verify.verify_tenant_registry"
    ground_command: "N/A — Pass-2 pin skill"
    workmanifest_contract: pass
    p15: true
    source_freshness: CURRENT
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    # Pin: pre-implement forge.commit_workspace = required.
    # Publish Pre-Implement-INIT-GATEFLOW-012-W0.md onto bound head_ref
    # (feature/INIT-GATEFLOW-012-w0-tenant-registry once cut, or develop if that is the bound head).
    # This skill does not mutate.
```

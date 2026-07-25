# Feasibility report — INIT-GATEFLOW-001

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-001 |
| Spec | `docs/specification/product/INIT-GATEFLOW-001-gateflow.md` |
| Spec digest | `sha256:3d3d3ef3c4a96144e8044df46064f13107d14986b8366e956cc898501dcb20cf` |
| PRD digest | `sha256:9fa343f11f9497cd278c18ba4b87391b15cab566f285e88a7f4cda9bf700802d` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-001.md` / `3` |
| Repo scope digest | `sha256:f81fd7c11c9b438524032898b31b028b376bcf766cb5ef675f0ecb81f326e9a0` |
| Approved meta PR head | `d62a9bbcf5960c50c4429dd33bb206208dbbf246` |
| Impact-map approval | Review `4763369852` by `0xbeefdead`, APPROVED `2026-07-23T10:54:32Z` on matching head |
| Source freshness | CURRENT — meta PR #9 head + APPROVED review + PRD/map digests + gateflow scope digest match spec header |
| Repo | drivestream-lab/gateflow |
| Date | 2026-07-23 |
| Branch | `chore/INIT-GATEFLOW-001-spec-gateflow` — Draft spec PR #4 |
| Initiative segment | `INIT-GATEFLOW-001` |
| Status | Draft |
| Review deadline | 2026-07-28 |
| Deciders | PM: programme PM · Domain SME: prayog-pe-team |

## Summary

INIT-GATEFLOW-001 is **buildable** on the current Python FastAPI scaffold: DI, Postgres/Redis lifecycle, JWT middleware, Alembic skeleton, and health unit tests are present. **All domain control-plane capabilities are greenfield gaps** (webhooks, RunStore, worker, PolicyEngine, AgentRunner, ForgeClient, status/metrics APIs, programme config). No Accepted ADRs exist; several **NEW-ADR** decisions are required before an implementation plan. Recommendation: keep Gate 2 `spec-pending`, run `/spec-technical-review` next (workflow `findings` → `spec-technical-review`).

**Findings:** 11 total (0 Critical, 5 Should fix, 3 Verify, 3 Gap)

## Baseline snapshot (F1)

| Area | Current state | Evidence |
|------|---------------|----------|
| Unit tests | `tests/unit/` with health only; `make test` → pytest `tests/unit/` | `tests/unit/test_health.py`, `Makefile` `test` target, `pyproject.toml` `testpaths = ["tests/unit"]` |
| Live verify | Placeholder; manual health md; no `verify_*.py` | `tests/verify/01-health-detailed.md`, `tests/README.md` |
| As-built | Populated this run with scaffold matrix | `docs/specification/as-built/implementation-status.md` |
| Toolchain | `make check` wired; CI workflow placeholder | `Makefile`, `.importlinter`, `.github/workflows/ci.yml` |
| Source | FastAPI scaffold; empty business/repo DI tuples | `src/app.py`, `src/di/dependency_container.py` `_BUSINESS_SERVICE_TYPES = ()` |

## Traceability matrix

| Spec ref / wave | Spec claim | Code evidence | Unit | Verify | Status |
|-----------------|------------|---------------|------|--------|--------|
| FR-1 webhook ingress | Signed GitHub App webhooks, idempotency, fast ack | No webhook router/handler under `src/api/` | — | — | gap |
| FR-2 concurrent reject | Reject second run same PR/issue | No RunStore / active-run query | — | — | gap |
| FR-3 trigger label | Config `trigger.label` / `gateflow:run-wave` | No programme config loader | — | — | gap |
| FR-4 preconditions | Wave-run checklist before dispatch | No PolicyEngine / TriggerRouter | — | — | gap |
| FR-5 RunStore Postgres | Runs/stages/events/jobs | `BasePostgres` only; `postgres_migrations/versions/` empty | — | — | gap |
| FR-6 HandoffReader | PR head / default_branch + globs | No handoff reader module | — | — | gap |
| FR-7 WorkflowEngine + PolicyEngine | Pin `v0.5.0-rc.2` dispatch | Pin present as submodule; no engine | — | — | gap |
| FR-8 contract stops | Stop human/external/decision/terminal | — | — | — | gap |
| FR-9 AgentRunner Cursor | Adapter + failure stop | No runner; no worker entrypoint | — | — | gap |
| FR-10 retry budget | Config default 3; exhaust → stop+comment | — | — | — | gap |
| FR-11 Notifier comments | Run event schema → ForgeClient | — | — | — | gap |
| FR-12 ForgeClient | Comments, run-status labels; forbid gate labels | No GitHub client under `infra_services/` | — | — | gap |
| FR-13 metrics v0 | `GET /metrics/runs`, 90-day retention | `api_router` empty | — | — | gap |
| FR-14 ToolProvider none | StageToolResolver empty | — | — | — | gap |
| FR-15 status API + programme token | Read-only JSON + service token | JWT middleware only; no programme-token auth | — | — | gap |
| FR-16 model profile default | Programme config `model.profiles` | — | — | — | gap |
| FR-17 API + async worker | Dual process + launchpad sync | `src/main.py` HTTP only; no `worker_main.py` | — | — | gap |
| FR-18 programme config | Keys in gateflow repo | No config file/module | — | — | gap |
| FR-19 W1 runbook | Orchestrate new initiative repo | No runbook doc | — | — | gap |
| Scaffold health | Existing | `GET /health` | `test_health.py` | manual md | exists |

## ADR pass (pre-T2)

| ADR id | Domain matched | Status |
|--------|----------------|--------|
| — | `docs/specification/adr/` empty | SKIPPED — no ADR files; all architecture choices → NEW-ADR |

## MDC pass (pre-T2)

| MDC file | Domain covered | Read / skipped |
|----------|----------------|----------------|
| `architecture.mdc` | Layout, entrypoints, JWT, public_paths | read |
| `dependency-injection.mdc` | DI, worker entry, lifecycle | read |
| `infra-services.mdc` | External clients, session factory | read |
| `repository-pattern.mdc` | Repo ↔ ORM, JSONB | read |
| `pydantic-schemas.mdc` | Models in `src/models/`, enums | read |
| `http-api-conventions.mdc` | Body/query/path | read |
| `database-migrations.mdc` | Human-owned Alembic | read |
| `logging-loguru.mdc` | Structured logging | read |
| `testing-verify-flows.mdc` | verify vs unit | read |
| `fail-fast.mdc` | No silent skip | read |
| `python-tooling.mdc` | check/test layout | read |
| `spec-driven-development.mdc` | Spec discipline | read |
| `python-imports.mdc` | Import placement | read |
| `strong-typing.mdc` | Typing | read |
| `code-guidelines-index.mdc` | Index only | skipped — index |

## ADR traceability (F13)

| Spec ref / wave | Relevant ADR(s) | Status | Finding |
|-----------------|-----------------|--------|---------|
| FR-17 dual API+worker | NEW-ADR | missing ADR | F-01 |
| FR-15 programme token vs JWT middleware | NEW-ADR | missing ADR | F-02 |
| FR-5 RunStore + job queue schema ownership | NEW-ADR | missing ADR | F-03 |
| FR-1 webhook public path + signature auth | NEW-ADR | missing ADR | F-04 |
| FR-7/9 PolicyEngine vs AgentRunner / ForgeClient slot boundaries | NEW-ADR | missing ADR | F-05 |
| FR-18 programme config format/location | NEW-ADR | missing ADR | F-06 |
| CTR-01 pin consumption | N/A (external pin SSOT) | aligned intent | — |

## Governance findings (F13–F14)

| ID | Check | Spec quote | Governing doc | Finding |
|----|-------|------------|---------------|---------|
| F-01 | F13 | FR-17 “API process + async worker (Postgres job table)” | NEW-ADR; `dependency-injection.mdc` Entry points | Need Accepted ADR for worker process + job claim model before plan |
| F-02 | F13 | FR-15 “authenticated via programme service token” | NEW-ADR; `architecture.mdc` JWT verification | Spec introduces non-JWT auth; must ADR how it coexists with `AuthMiddleware` / `public_paths` |
| F-03 | F13 | FR-5 PostgreSQL RunStore | NEW-ADR; `repository-pattern.mdc`, `database-migrations.mdc` | Schema + repo boundaries + human migrations — document in ADR |
| F-04 | F13/F14 | FR-1 webhook signature validation | NEW-ADR; `architecture.mdc` public_paths | Webhook must be public (no user JWT) and signature-verified — ADR + MDC-aligned mounting |
| F-05 | F13 | FR-9/12 AgentRunner / ForgeClient slots | NEW-ADR; `infra-services.mdc` | Outbound GitHub + Cursor clients are infra; PolicyEngine is business — ADR slot ownership |
| F-06 | F13 | FR-18 programme config in gateflow repo | NEW-ADR | File format, load path, fail-fast on missing keys |
| F-07 | F14 | FR-15 status/metrics under API | `http-api-conventions.mdc`, `pydantic-schemas.mdc` | Models must live in `src/models/`; route bodies not inline — note for TDD (not conflict yet) |
| F-08 | F14 | FR-7 “never silent no-op” on pin unavailable | `fail-fast.mdc` | Aligned — keep explicit in TDD tests |

## Findings by severity

### Critical

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| — | — | None | No Accepted ADR contradictions; freshness CURRENT |

### Should fix

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| F-01 | F13 | NEW-ADR: dual-process API + async worker + Postgres job queue | Spec FR-17; `src/main.py` HTTP-only; DI.mdc documents `worker_main.py` pattern |
| F-02 | F13 | NEW-ADR: programme service token auth vs existing JWT `AuthMiddleware` | Spec FR-15 Q-3; `src/app.py` `public_paths=["/health", "/internal"]` |
| F-03 | F13 | NEW-ADR: RunStore / job schema + repository boundaries | Spec FR-5; `schema/__init__.py` empty; `versions/.gitkeep` |
| F-04 | F13 | NEW-ADR: webhook ingress auth (signature) and public route mount | Spec FR-1; no webhook module |
| F-09 | F6 | Spec header still says “Spec PR: pending”; as-built was missing at draft time | Spec References; remediated as-built this commit; update Spec PR link on next spec edit |

### Verify

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| F-10 | F10 | A-3 Cursor SDK in container still open — blocks FR-9 confidence | Spec Assumptions A-3 status open |
| F-11 | F3/F8 | No live-verify scripts or CI gate for domain FRs; CI workflow is placeholder | `tests/verify/`, `.github/workflows/ci.yml` |
| F-12 | F9 | CTR-01…04 must be proven with contract fixtures / Forge mocks when built | Spec Cross-service contracts; `prayog-skills/tests/fixtures/workflow_scenarios.json` available in pin |

### Gap

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| F-13 | F2 | All FR-1…FR-19 domain capabilities absent in `src/` | Explore inventory; grep zero domain symbols |
| F-14 | F4 | Unit coverage only health; planned PolicyEngine/ForgeClient/unit areas missing | `tests/unit/test_health.py` |
| F-15 | F11 | W1 effort drivers: GitHub App + Cursor SDK + dual-process + contract engine (high complexity surface) | Spec FR-1, FR-9, FR-17, FR-7 |

## Impact surface

| Wave / area | Likely files/modules | Test touch |
|-------------|----------------------|------------|
| W0 skeleton | `src/api/v1/*_routes.py`, `src/infra_services/forge_client.py`, `src/business_services/{handoff,workflow,trigger}_*.py`, `src/database/postgres/schema/run_*.py`, repos, programme config | unit: signature, idempotency, handoff parse; verify: webhook smoke |
| W1 PolicyEngine + worker | `src/worker_main.py` (or equiv), PolicyEngine, AgentRunner adapter, job claim, Notifier | unit: dispatch policy, retry budget, stops; verify: e2e label→stop |
| Metrics / status | `src/api/v1/runs_routes.py`, metrics service, programme-token dep | unit: auth; verify: `GET` status/metrics |
| Migrations | Human `postgres_migrations/versions/*` | inspection |
| Docs | W1 runbook under `docs/` | inspection |

## Risks & assumptions

| ID | Risk / assumption | Mitigation |
|----|-------------------|------------|
| R-1 | Cursor SDK container friction (A-3) | Spike in technical review; fail-closed AgentRunner |
| R-2 | Auth middleware collision (JWT vs programme token vs webhook public) | NEW-ADR F-02/F-04 before coding routes |
| R-3 | Webhook delivery gaps / idempotency | FR-1 event id persistence; verify duplicate delivery |
| R-4 | Human migration lag vs schema | Follow `database-migrations.mdc`; describe DDL in PR for owner |
| A-9 | JWT remains for future routes | Confirm in auth ADR |

## Recommended spec edits

- Update References “Spec PR: pending” → https://github.com/drivestream-lab/gateflow/pull/4
- After TDD: cite NEW-ADR ids for F-01…F-06 in Cross-service / NFR / auth sections
- Add explicit verify script names under evidence columns once planned in technical review
- Keep Q-1…Q-3; resolve Q-3 inside auth ADR (default already stated)

---

## Open items by lane

> Routing rubric: product scope / UX → PM · engineering decisions / ADR → PE ·
> business source-of-truth → Domain SME · naming drift / inferred fixes → Auto-fix.

| ID | Lane | Question / item | Blocking | Owner | Status | Required by | Default if deferred | Evidence | Resolution reference |
|----|------|-----------------|----------|-------|--------|-------------|---------------------|----------|----------------------|
| Q-1 | PE | ForgeClient auth: App token only vs PAT in dev? | no | PE | open | technical review / W0 | App preferred; PAT scoped dev-only (FR-14) | Spec Q-1; IM-05 | pending — meta #9 / TDD |
| Q-2 | PE | Postgres-down alert channel beyond 503? | no | PE | open | plan / ops runbook | GitHub retries + operator watch | Spec Q-2 | pending |
| Q-3 | PE | Exact status/metrics paths vs `public_paths` / programme-token | no for merge; **yes for plan** | PE | open | technical review | `/api/v1` + programme-token dep | Spec Q-3; F-02 | pending TDD |
| F-01 | PE | NEW-ADR dual API+worker+job queue | yes for plan | PE | open | technical review | DI `worker_main` + Postgres jobs per Decision #6 | FR-17; DI.mdc | pending TDD |
| F-02 | PE | NEW-ADR programme-token auth model | yes for plan | PE | open | technical review | Programme token; webhook public; JWT elsewhere | FR-15; `src/app.py` | pending TDD |
| F-03 | PE | NEW-ADR RunStore schema/repos | yes for plan | PE | open | technical review | Postgres only; human Alembic | FR-5 | pending TDD |
| F-04 | PE | NEW-ADR webhook public + signature | yes for plan | PE | open | technical review | Public path + App signature | FR-1 | pending TDD |
| F-05 | PE | NEW-ADR slot ownership (infra vs business) | yes for plan | PE | open | technical review | Forge/Cursor=infra; Policy=business | FR-9/12; infra.mdc | pending TDD |
| F-06 | PE | NEW-ADR programme config format | yes for plan | PE | open | technical review | YAML in repo; fail-fast missing keys | FR-18 | pending TDD |
| F-10 | PE | Confirm Cursor SDK worker runtime (A-3) | no for merge; yes for W1 exit confidence | PE | open | technical review / W1 | Spike + documented constraint | Spec A-3 | pending |
| AF-1 | auto-fix | Create baseline as-built matrix | no | agent | resolved | feasibility | — | F5/F6 | this commit `implementation-status.md` |
| AF-2 | auto-fix | Point Spec PR reference to #4 | no | agent | open | next spec edit | — | Spec References | pending (product spec edit deferred per skill) |

### PM questions (product scope, UX, priority)

#### Blocking — must resolve before spec merge

None.

#### Defer — can proceed with documented assumption

None new beyond meta IM-05 already non-blocking.

### PE questions (engineering decisions — resolved by `/spec-technical-review`)

#### Blocking for implementation plan

1. F-01 Dual-process worker + job queue ADR
2. F-02 Programme service token vs JWT middleware ADR
3. F-03 RunStore / migrations ADR
4. F-04 Webhook ingress auth + public mount ADR
5. F-05 Infra vs business slot ownership ADR
6. F-06 Programme config format/location ADR
7. Q-3 Exact route mounts (fold into F-02)

#### Defer with default

1. Q-1 ForgeClient PAT-in-dev — default FR-14
2. Q-2 Ops alert for Postgres 503 — default operator/GitHub retry
3. F-10 Cursor SDK container — spike during TDD; default fail-closed runner

### Domain clarifications (business source-of-truth)

| # | Question | Suggested SME | Blocks |
|---|----------|---------------|--------|
| — | None | — | — |

### Auto-fixable (agent resolves — no human needed)

| # | Item | Fix |
|---|------|-----|
| AF-1 | Missing as-built | Added scaffold matrix `docs/specification/as-built/implementation-status.md` |
| AF-2 | Spec PR still “pending” | Update References on next authorized product-spec edit |

---

## Check summary

| Check | Status | Findings |
|-------|--------|----------|
| F1 Baseline snapshot | PASS | Scaffold + health unit + placeholder verify + as-built now present |
| F2 Spec → code map | PASS | Matrix complete; all domain FRs = gap (expected) |
| F3 Spec → verify map | PASS | No false claims of existing verify scripts; F-11 notes absence |
| F4 Spec → unit map | PASS | Health exists; domain unit areas planned/gap F-14 |
| F5 As-built drift | PASS | Spec Overview matches scaffold; as-built created this run |
| F6 Docs drift | PASS w/ Should fix | AGENTS paths exist; Spec PR link stale (F-09/AF-2); tests README honest |
| F7 Overlap risk | PASS | No duplicated unit+verify journeys yet |
| F8 CI vs live boundary | PASS w/ Verify | Unit=CI intent; live verify local; CI placeholder F-11 |
| F9 Cross-service touch | PASS w/ Verify | CTR-01…05 documented; tests planned F-12 |
| F10 Assumptions | PASS w/ Verify | A-3/A-9 open tracked F-10 |
| F11 Effort drivers | PASS | High: forge+agent+worker+policy (F-15) |
| F12 PM questions | PASS | No blocking PM gaps |
| F13 ADR conformance | FAIL→findings | No Accepted ADRs; NEW-ADR F-01…F-06 (Should fix for plan) |
| F14 MDC conformance | PASS | No hard conflicts; auth/webhook need ADR alignment F-04/F-07/F-08 |

**Feasibility outcome:** `findings` (route to `/spec-technical-review`)

---

## Next steps

> This report lives on the spec PR branch alongside the spec draft.
> The spec PR is the engineering review surface; product Q&A uses the meta PRD PR.

**PM questions** → none blocking; IM-05/Q-1 remains on meta PRD PR if PE wants PM echo.

**PE questions** → discuss on Draft spec PR #4; run `/spec-technical-review` next.
  Do **not** set `spec-lgtm` until feasibility + TDD/ADRs + plan are on head.

**Domain clarifications** → none.

**Auto-fixable** → AF-1 done this commit; AF-2 on next spec edit.

```
Draft spec PR: chore/INIT-GATEFLOW-001-spec-gateflow  (spec-pending)
When ready:
  [x] Source freshness is CURRENT
  [x] All blocking PM questions answered (none)
  [x] All blocking Domain clarifications answered (none)
  [ ] Spec updated for AF-2 Spec PR link (optional)
  [x] Feasibility report committed on branch
  [ ] Proceed: /spec-technical-review (PE NEW-ADR questions exist)
  [ ] After TDD + Accepted ADRs + plan on branch:
      PE sets spec-lgtm + Approve on exact head → Ready for review → merge
  [ ] After merge: board-seed from plan §9 — then /pre-implement → /loop-spec
```

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: initiative-feasibility
  outcome: findings
  artifact:
    path: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-001.md
    digest: sha256:5f62b3cbd0232d5cf014ee0dbfa8d203686d13c007c2ab41ce0487b9f4dfa2b0
  blockers:
    - F-01
    - F-02
    - F-03
    - F-04
    - F-05
    - F-06
  signals:
    draft_spec_pr: https://github.com/drivestream-lab/gateflow/pull/4
    gate2_label: spec-pending
    source_freshness: CURRENT
    map_revision: 3
    prd_digest: sha256:9fa343f11f9497cd278c18ba4b87391b15cab566f285e88a7f4cda9bf700802d
    scope_digest: sha256:f81fd7c11c9b438524032898b31b028b376bcf766cb5ef675f0ecb81f326e9a0
    finding_counts:
      critical: 0
      should_fix: 5
      verify: 3
      gap: 3
    lane_counts:
      pm: 0
      pe: 10
      domain: 0
      auto_fix: 2
    new_adr: true
    new_adr_ids: [F-01, F-02, F-03, F-04, F-05, F-06]
    ripple_action: continue
  next_candidates:
    - spec-technical-review
  human_checkpoint: false
  external_action: false
```

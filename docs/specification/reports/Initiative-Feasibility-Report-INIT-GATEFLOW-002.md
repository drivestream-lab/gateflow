# Feasibility report — INIT-GATEFLOW-002

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-002 |
| Spec | `docs/specification/product/INIT-GATEFLOW-002-gateflow.md` |
| Spec digest | `sha256:a3a1fd7cb1058f05b13bfe3e1a84355e965000dea0306a69392e060d0258d093` |
| PRD digest | `sha256:2f339bae00df71e21b45e51c7551f1fb06490dd1805b96e08daca741c140332c` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-002.md` / `1` |
| Repo scope digest | `sha256:3662f15e366994defaf08fa43b0a5a568eb152f6a74bcff73a0b0453dba0c901` |
| Approved meta PR head | `8f291367134a686baaf650835a89dba92e887051` |
| Impact-map approval | Review `4770823317` by `0xbeefdead`, APPROVED `2026-07-24T06:49:29Z` on matching head; label `impact-map-lgtm` |
| Source freshness | CURRENT — meta PR #10 head + APPROVED review + PRD/map digests + gateflow scope digest match spec header; repo not deferred/blocked |
| Repo | drivestream-lab/gateflow |
| Date | 2026-07-24 |
| Branch | `chore/INIT-GATEFLOW-002-spec-gateflow` — Draft spec PR #10 |
| Initiative segment | `INIT-GATEFLOW-002` |
| Status | Draft |
| Review deadline | 2026-07-29 |
| Deciders | PM: programme PM · Domain SME: prayog-pe-team |

## Summary

INIT-GATEFLOW-002 is **buildable on the delivered INIT-001 control plane**, but it is
**not a thin delta**: wave-start API, label-trigger removal, adapter registries,
PR-at-run-start, board APIs, and multi-dimension metrics are largely **gaps** over
partial foundations (programme-token reads, ForgeClient comments, Cursor stub,
label webhook path). One **Critical** governance conflict remains: Accepted
**ADR-002** scopes the programme token to **read-only** status/metrics, while
FR-15/FR-24 require **write** APIs on the same token. Recommendation: keep Gate 2
`spec-pending`, amend/supersede ADR-002 in `/spec-technical-review`, then plan
W0→W1→W2.

**Findings:** 14 total (1 Critical, 6 Should fix, 3 Verify, 4 Gap)

## Baseline snapshot (F1)

| Area | Current state | Evidence |
|------|---------------|----------|
| Unit tests | `tests/unit/` — 12 modules (health, webhook, trigger/policy, orchestrator, programme token API, forge forbid, RunStore DTOs, etc.) | `tests/unit/*.py`, `pyproject.toml` `testpaths = ["tests/unit"]`, `Makefile` `test` |
| Live verify | `verify_health`, `verify_webhook`, `verify_status_metrics`, `verify_wave_smoke` (+ `verify_all`) | `tests/verify/`, `tests/README.md` feature map (INIT-001 only) |
| As-built | W0+W1 **human_approved**; label webhook → worker → status/metrics | `docs/specification/as-built/implementation-status.md` (Updated 2026-07-23) |
| Toolchain | `make check` (black/ruff/pyright/import-linter); CI placeholder | `Makefile`, `.github/workflows/ci.yml` |
| Source | Full control-plane modules under `src/` (API + worker) | `src/main.py`, `src/worker_main.py`, `src/business_services/*`, `src/infra_services/forge_client.py` |

## ADR pass (pre-T2)

| ADR id | Domain matched | Status |
|--------|----------------|--------|
| ADR-001 | Dual API+worker, Postgres RunStore | Accepted — aligned (002 keeps topology) |
| ADR-002 | Programme token / public_paths / webhook trust zones | Accepted — **conflict** with FR-15/FR-24 writes (see F13-1) |
| ADR-003 | ForgeClient / AgentRunner infra slots | Accepted — extend surface; registry policy may need NEW-ADR |
| ADR-004 | Programme config in gateflow repo | Accepted — aligned (extend keys for `notifier` / `pr.*` / richer overrides) |

## MDC pass (pre-T2)

| MDC file | Domain covered | Read / skipped |
|----------|----------------|----------------|
| `architecture.mdc` | Layout, public_paths, JWT | read |
| `dependency-injection.mdc` | `@inject`, infra/business lifecycle | read |
| `infra-services.mdc` | ForgeClient / runners as infra | read |
| `http-api-conventions.mdc` | POST body models for wave-start / board | read |
| `pydantic-schemas.mdc` | Models only in `src/models/` | read |
| `repository-pattern.mdc` | ORM isolation | read |
| `database-migrations.mdc` | Human-owned Alembic for schema adds | read |
| `fail-fast.mdc` | Stub fail-closed / no silent fallback | read |
| `testing-verify-flows.mdc` | verify vs unit boundary | read |
| `logging-loguru.mdc` | Structured logging | skipped — no wording conflict |
| `python-imports.mdc` / `python-tooling.mdc` / `strong-typing.mdc` | Tooling | skipped — not initiative-specific |
| `spec-driven-development.mdc` | Process | skipped — process only |
| `code-guidelines-index.mdc` | Index | skipped |

## Traceability matrix

| Spec ref / wave | Spec claim | Code evidence | Unit | Verify | Status |
|-----------------|------------|---------------|------|--------|--------|
| FR-15 W0 | Authenticated wave-start API; dual identity; label trigger removed | No POST wave-start under `src/api/v1/`; `TriggerRouter` still label-authorizes (`trigger_router.py`); `config/programme.yaml` `trigger.label` | `test_trigger_policy.py` (label path) | `verify_wave_smoke` (label) | gap (+ label path **exists** — must change) |
| FR-16 W1 | Per-node runner + model overrides | `ModelConfig.overrides: dict[str, str]` profile-only; `run_orchestrator.py` uses `runner.default` always | `test_programme_config.py` | — | partial |
| FR-17 W0 | Cursor live + OpenCode/Claude stubs registered | Only `CursorAgentRunner` bound in `infra_module.py` | via orchestrator | — | partial (cursor only) |
| FR-18 W0 | Fail-closed stub/config validation at start | No pre-enqueue registry validation; Cursor fails closed mid-dispatch only | `test_run_orchestrator.py` | — | gap |
| FR-19 W1 | PR open/update at run start; comments on that PR | `ForgeClient.post_comment` only; no PR create/update | `test_forge_client.py` (forbid only) | — | gap |
| FR-20 W0 | Run list/filter + detail timeline | `GET /runs/{run_id}` header only (`runs_routes.py`, `RunStatusResponse`) | `test_programme_token_api.py` | `verify_status_metrics` | partial |
| FR-21 W1 | Metrics by node, runner, `model_id` | `aggregate_run_metrics` → `by_workflow_node` only | `test_programme_token_api.py` | `verify_status_metrics` | partial |
| FR-22 W1 | Multi-stage metrics events incl. API trigger | `stage_completed` + `run_stopped`; no `api_trigger` event | orchestrator tests | — | partial |
| FR-23 W0/W1 | Notifier GitHub live + Slack/Teams stubs | `Notifier` → ForgeClient only; no `notifier` config key | — | — | partial |
| FR-24 W2 | Board APIs (status, link, create, list) | No board routes; ForgeClient has no board/PR methods | — | — | gap |
| FR-25 / FR-26a W2 | Production ForgeClient-only / no `gh` | HTTP ForgeClient; PAT blocked in `PRODUCTION`; no explicit `gh` forbid test | `test_forge_client.py` | — | partial |
| FR-26b | Laptop `gh` policy docs (non-runtime) | No 002 runbook yet | — | — | gap (docs) |
| inherit | Contract stops, handoff, PolicyEngine, job worker | Present from INIT-001 | `test_handoff_workflow`, `test_trigger_policy`, `test_job_worker` | wave smoke (enqueue) | exists |
| inherit | Cursor SDK real path | `CursorAgentRunner` stub unless `GATEFLOW_AGENT_STUB` / `mock-*` | orchestrator | — | partial (W1 happy path still stub) |

## ADR traceability (F13)

| Spec ref / wave | Relevant ADR(s) | Status | Finding |
|-----------------|-----------------|--------|---------|
| FR-15 / FR-20 / FR-21 / FR-24 | ADR-002 | **conflict** | F13-1 — programme-token **writes** vs ADR-002 “control-plane **reads**” |
| FR-17 / FR-18 / FR-23 | ADR-003 + **NEW-ADR** | missing ADR | F13-2 — adapter registry + fail-closed start selection not decided in Accepted ADRs |
| FR-19 / FR-24 / FR-25 | ADR-003 | aligned (extend) | Widen ForgeClient surface; keep forbid gate-labels/auto-merge |
| FR-16 / programme config | ADR-004 | aligned (extend) | Add `notifier`, `pr.*`, richer overrides in gateflow config |
| Runtime / RunStore | ADR-001 | aligned | Keep API + worker + Postgres jobs |

## Governance findings (F13–F14)

| ID | Check | Spec quote | Governing doc | Finding |
|----|-------|------------|---------------|---------|
| F13-1 | F13 | FR-15 / FR-24: programme service token authenticates wave-start and board **mutations** | ADR-002: “Programme control-plane **reads** (status/metrics)” | Critical conflict — amend/supersede ADR-002 before plan |
| F13-2 | F13 | FR-17/18/23 stub registry + block entire run at start | ADR-003 (slot ownership only) | NEW-ADR for selection/fail-closed policy |
| F14-1 | F14 | Wave-start / board POST bodies | `http-api-conventions.mdc` | Aligned if TDD uses Pydantic bodies in `src/models/` (default Q-1) |
| F14-2 | F14 | Schema adds for wave_id / PR refs / richer events | `database-migrations.mdc` | Human-owned Alembic required — plan must not agent-commit versions |
| F14-3 | F14 | Label verify remains primary smoke | `testing-verify-flows.mdc` | Docs/verify drift — replace label smoke with API wave-start for 002 |

## Findings by severity

### Critical

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| C-1 | F13 | Spec FR-15/FR-24 programme-token **write** APIs contradict Accepted ADR-002 read-only programme control-plane zone. Blocks clean implementation without ADR amend/supersede. | Spec FR-15/FR-24 + Q-6; ADR-002 recommendation table “Programme control-plane **reads**”; `programme_token.py` docstring “status/metrics routes”; `app.py` `public_paths` for `/api/v1/runs`, `/api/v1/metrics` only |

### Should fix

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| S-1 | F2 / F5 | Label trigger path is still the live wave-start mechanism; FR-15 requires removal for 002 programmes — must be an explicit breaking change in code + verify + as-built. | `trigger_router.py` PC-01 label check; `config/programme.yaml` `trigger.label`; `verify_wave_smoke.py`; as-built row “TriggerRouter” |
| S-2 | F2 | No AgentRunner/Notifier **registry**; OpenCode/Claude/Slack/Teams stubs absent; fail-closed validation at **start** missing. | `infra_module.py` binds only `CursorAgentRunner` + `ForgeClient`; `notifier.py` GitHub-only; no `notifier` in `ProgrammeConfig` |
| S-3 | F2 | ForgeClient lacks PR create/update and board primitives required by FR-19/FR-24. | `forge_client.py`: `post_comment`, forbid helpers only |
| S-4 | F2 / F4 | Run APIs lack list/filter and stage/event timeline; metrics lack runner/`model_id` dimensions. | `RunStatusResponse` fields; `RunMetricsResponse.by_workflow_node` only; `metrics_emitter.py` |
| S-5 | F6 | `tests/README.md` feature map and as-built are INIT-001-centric; will mislead 002 verify planning. | `tests/README.md` “Feature map (INIT-GATEFLOW-001)”; as-built Updated 2026-07-23 |
| S-6 | F13 | NEW-ADR needed for adapter registry + fail-closed start selection (FR-17/18/23). | ADR-003 covers ownership, not selection policy |

### Verify

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| V-1 | F3 | Live verify for wave start today is **label** smoke; 002 needs API wave-start verify + board verify (W2) + `gh`-free production-path inspection. | `tests/verify/verify_wave_smoke.py`, `verify_all.py` |
| V-2 | F8 | CI remains unit/`make check` only; live verify stays local — document 002 scripts the same way. | `tests/README.md`, `.github/workflows/ci.yml` placeholder |
| V-3 | F10 | Spec A-1 “001 delivered” matches as-built human_approved; Cursor **SDK** still stub — W1 “Cursor happy path” may still need stub env or real SDK work (carry INIT-001 deferred D-W1-A1). | `cursor_agent_runner.py`; as-built “Deferred: real Cursor SDK” |

### Gap

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| G-1 | F2 | Wave identity (ticket **or** initiative+wave; dual agree) and concurrent key by wave identity not modeled. | `TriggerContext` has `initiative_id` optional; concurrent via `find_active_run` on org/repo/pr\|issue; no `wave_id` |
| G-2 | F2 | `model.overrides` is `dict[str, str]` (profile name); FR-16 needs runner override fields per node. | `programme_config_models.py` `ModelConfig.overrides` |
| G-3 | F11 | W2 board create/list + Projects permissions (Q-4/A-4) is largest external risk. | Spec Q-4; PRD A3 |
| G-4 | F9 | CTR-04 consumer (gateflow-ops) deferred — provider contracts must still be documented in-repo for future BFF. | Impact map CTR-04; no OpenAPI docs package yet |

## Impact surface

| Wave / area | Likely files/modules | Test touch |
|-------------|----------------------|------------|
| W0 — wave-start API + label disable + stubs + run list/detail | `src/api/v1/*`, `trigger_router.py`, `programme_config_models.py`, `run_store_*`, DI modules | New unit: wave-start auth/identity/preconditions; update `verify_wave_smoke` → API start; extend `test_programme_token_api` |
| W1 — per-node model, PR-at-start, metrics dims, Cursor path | `run_orchestrator.py`, `forge_client.py`, `notifier.py`, `metrics_emitter.py`, `cursor_agent_runner.py`, programme `pr.*` / overrides | Unit fixtures ≥2 overrides; forge PR tests; metrics dimension tests; live PR-thread verify |
| W2 — board APIs + gh-free proof | New board routes/models; ForgeClient board methods; deploy verification doc/test | Board API unit + verify; production-path inspection |

## Risks & assumptions

| ID | Risk / assumption | Mitigation |
|----|-------------------|------------|
| R-1 | ADR-002 amend delayed → blocked writes | Treat C-1 as first TDD/ADR item; default = extend programme-token zone to documented write routes |
| R-2 | GitHub App permissions insufficient for Projects/board create/list | Q-4 before W2 exit; narrow board MVP if needed |
| R-3 | Always-open PR noise on failed runs | Same naming + clear failed titles (Q-2); PE templates in TDD |
| R-4 | Label removal breaks existing operator muscle memory / verify | Changelog + runbook; replace verify scripts in same wave as API start |
| R-5 | Real Cursor SDK still deferred | Spec W1 “Cursor happy path” may accept controlled stub until SDK lands — PE confirm in TDD |
| A-spec | Spec assumptions A-1…A-9 | A-4 open; others confirmed or open with defaults |

## Recommended spec edits

- Record Spec PR URL `#10` in the INIT-GATEFLOW-002 header References (currently `pending`).
- State explicitly that ADR-002 **must be amended/superseded** (not only Q-6 default) as a Gate 2 dependency before W0 write routes land.
- Clarify W1 Cursor “happy path”: real SDK vs `GATEFLOW_AGENT_STUB` / mock skills acceptable for wave exit (align with as-built deferred D-W1-A1).
- Name planned verify modules for API wave-start and board APIs (replace label smoke as primary).
- Optional: note `model.overrides` shape change (`str` → structured override object) as a breaking config change from INIT-001 H1.

---

## Open items by lane

> Routing rubric: product scope / UX → PM · engineering decisions / ADR → PE ·
> business source-of-truth → Domain SME · naming drift / inferred fixes → Auto-fix.

| ID | Lane | Question / item | Blocking | Owner | Status | Required by | Default if deferred | Evidence | Resolution reference |
|----|------|-----------------|----------|-------|--------|-------------|---------------------|----------|----------------------|
| C-1 | PE | Amend/supersede ADR-002 for programme-token write routes (wave-start, board) | yes | PE | open | technical review | Extend ADR-002 trust zone to documented write routes; keep JWT separate | ADR-002 vs FR-15/24 | pending TDD/ADR |
| S-6 | PE | NEW-ADR: adapter registry + fail-closed start selection | yes | PE | open | technical review | Registry by id; validate required slots before enqueue; unused stubs OK | FR-17/18/23; ADR-003 gap | pending TDD/ADR |
| Q-1 | PE | Exact HTTP paths/schemas FR-15/20/21/24 | no | PE | open | technical review | `/api/v1` + programme token + Pydantic models | Spec Q-1 | pending |
| Q-2 | PE | PR naming / `pr.branch_prefix` templates | no | PE | open | W1 | Programme config keys; same success/failure naming | Spec Q-2 | pending |
| Q-3 | PE | Board list filters | no | PE | open | W2 | Narrow filters in TDD | Spec Q-3 | pending |
| Q-4 | PE | App/Projects permission matrix (A-4) | no | PE | open | W2 exit | Confirm before W2 exit; narrow scope if missing | Spec Q-4 | pending |
| Q-5 | PE | PE alert on PR open/update failure | no | PE | open | W1 | status API + `notify_pending` | Spec Q-5 | pending |
| V-3 | PE | Cursor SDK vs stub for W1 exit | no | PE | open | W1 plan | Stub/mock allowed for W1 exit if documented; SDK follow-on | `cursor_agent_runner.py`; as-built | pending |
| AF-1 | auto-fix | Spec References Spec PR `pending` | no | eng | resolved | spec branch hygiene | Set to gateflow PR #10 | Spec References | https://github.com/drivestream-lab/gateflow/pull/10 |
| AF-2 | auto-fix | `tests/README.md` still INIT-001-only feature map | no | eng | resolved | W0 verify planning | Add 002 planned verify rows | `tests/README.md` | this commit |

### PM questions (product scope, UX, priority)

#### Blocking — must resolve before spec merge
None.

#### Defer — can proceed with documented assumption
None new beyond PRD Decisions already locked. No PM lane items from this feasibility pass.

### PE questions (engineering decisions — resolved by `/spec-technical-review`)

#### Blocking for implementation plan
1. **C-1** — ADR-002 amend/supersede for programme-token writes.
2. **S-6** — NEW-ADR for adapter registry + fail-closed start validation.

#### Defer with default
1. **Q-1…Q-5** — paths, PR templates, board filters, permissions, alert channel (defaults in spec).
2. **V-3** — Cursor stub acceptable for W1 exit unless PE requires SDK.

### Domain clarifications (business source-of-truth)

| # | Question | Suggested SME | Blocks |
|---|----------|---------------|--------|
| — | None identified this pass | — | — |

### Auto-fixable (agent resolves — no human needed)

| # | Item | Fix |
|---|------|-----|
| AF-1 | Spec References Spec PR `pending` | Point to https://github.com/drivestream-lab/gateflow/pull/10 — **done** |
| AF-2 | tests/README INIT-001-only map | Add 002 planned verify section — **done** |

---

## Check summary

| Check | Status | Findings |
|-------|--------|----------|
| F1 Baseline snapshot | PASS | Unit/verify/as-built/toolchain inventoried |
| F2 Spec → code map | FAIL | Multiple gaps/partials (S-1…S-4, G-1/G-2); expected for pre-impl |
| F3 Spec → verify map | FAIL | Label smoke only; API/board verify missing (V-1) |
| F4 Spec → unit map | FAIL | No wave-start/registry/PR/board unit areas yet (S-2…S-4) |
| F5 As-built drift | FAIL | As-built matches 001 delivered; 002 claims are future — S-1/S-5 |
| F6 Docs drift | FAIL | tests/README + as-built 001-centric (S-5) |
| F7 Overlap risk | PASS | No duplicate unit+verify journeys yet for 002 APIs |
| F8 CI vs live boundary | PASS | Documented; V-2 notes keep boundary |
| F9 Cross-service touch | PASS | CTR-01…05 cited; CTR-04 consumer deferred (G-4) |
| F10 Assumptions | PASS | A-4 open tracked; A-1 evidenced; V-3 Cursor caveat |
| F11 Effort drivers | PASS | W0/W1/W2 impact surface recorded |
| F12 PM questions | PASS | No blocking PM gaps |
| F13 ADR conformance | FAIL | C-1 Critical ADR-002 conflict; S-6 NEW-ADR |
| F14 MDC conformance | PASS | F14-1…3 notes; no hard MDC contradiction if TDD follows conventions |

**Feasibility verdict:** **FINDINGS** — buildable with governance work; do **not** skip `/spec-technical-review`.

---

## Next steps

> This report lives on the spec PR branch alongside the spec draft.
> The spec PR is the engineering review surface; product Q&A uses the meta PRD PR.

**PM questions** → none this pass (meta PR #10 already Gate-1 approved).

**PE questions** → discuss on Draft spec PR #10; run `/spec-technical-review` next
(workflow `findings` → `spec-technical-review`). Accept ADR-002 amend + NEW-ADR
in files before `/spec-implementation-plan`. Do **not** set `spec-lgtm` until the
full package includes the implementation plan.

**Domain clarifications** → none.

**Auto-fixable items** → AF-1/AF-2 resolved on this branch.

```
Draft spec PR: chore/INIT-GATEFLOW-002-spec-gateflow  (spec-pending)
When ready:
  [x] Source freshness is CURRENT
  [x] All blocking PM questions answered (none)
  [x] All blocking Domain clarifications answered (none)
  [x] AF-1 / AF-2 auto-fixes committed
  [ ] Proceed: /spec-technical-review (PE questions C-1, S-6 + Q-1…Q-5, V-3)
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
    path: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-002.md
    digest: sha256:71dfb8e4ee2132d4c39ec0fb8d6fa01d5a1a20984b51d43605534bf5338de4b5
  blockers:
    - C-1
    - S-6
  signals:
    draft_verdict: FINDINGS
    source_freshness: CURRENT
    critical_count: 1
    should_fix_count: 6
    verify_count: 3
    gap_count: 4
    new_adr: true
    adr_conflict: ADR-002
    ripple_action: continue
    map_revision: 1
    prd_digest: sha256:75ea335bc3636a0e7ef6db1ce6ad325c861492bac448deef71f3cddc83c4093c
    scope_digest: sha256:75ea335bc3636a0e7ef6db1ce6ad325c861492bac448deef71f3cddc83c4093c
    meta_pr: https://github.com/drivestream-lab/prayog-meta/pull/10
    spec_pr: https://github.com/drivestream-lab/gateflow/pull/10
    lane_pm: 0
    lane_pe_blocking: 2
    lane_domain: 0
    lane_auto_fix: 0
    auto_fix_resolved: [AF-1, AF-2]
    gate2_label: spec-pending
  next_candidates:
    - spec-technical-review
  human_checkpoint: false
  external_action: false
```

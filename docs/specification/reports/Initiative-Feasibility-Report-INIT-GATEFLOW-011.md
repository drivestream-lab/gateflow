# Feasibility report — INIT-GATEFLOW-011

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-011 |
| Spec | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` |
| Spec digest | `sha256:0edf9b72b5e66e9edb9686faddbe24ced7bfe5ca30aed4462dead234d7376ac4` |
| PRD digest | `sha256:eca06cbe986d619db58ae3ca84f4ec0987c19aa19b8f1485693280c6a655e4dd` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-011.md` / `1` |
| Repo scope digest | `sha256:afdc7bd51bcd0c12f614feebf338bdc78766396bb84777121a2565c0ecc7966d` |
| Approved meta PR head | `f3da8148f3e861fad4720a3491f11f1fdc0145aa` |
| Impact-map approval | [@0xbeefdead APPROVED](https://github.com/drivestream-lab/prayog-meta/pull/30#pullrequestreview-4876719066) 2026-08-06T16:28:58Z on `f3da8148…` — [prayog-meta#30](https://github.com/drivestream-lab/prayog-meta/pull/30) |
| Source freshness | **CURRENT** — H1/H2/H3 match live meta @ `f3da8148…`; G1 APPROVED + `impact-map-lgtm`; Draft spec PR [#159](https://github.com/drivestream-lab/gateflow/pull/159) tip `e0384fd`; Gate 2 `spec-pending` |
| Prior stage | `/spec-draft` → `pass` → `/commit-workspace` + `/open-draft-pr` (#159) |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-06 |
| Branch | `chore/INIT-GATEFLOW-011-spec-gateflow` — Draft spec PR [#159](https://github.com/drivestream-lab/gateflow/pull/159) |
| Initiative segment | `INIT-GATEFLOW-011` |
| Status | Draft |
| Review deadline | 2026-08-11 |
| Deciders | PM: programme · Domain SME: N/A (eng control-plane visibility) |

## Summary

INIT-GATEFLOW-011 is **buildable in this repo** against the current codebase and
pinned `v0.5.0-rc.2` tip. Gate 1 / H1–H3 authority is current. The product
surface (GET `/checkpoints/*`, GET `/initiatives/*` read-outs) is **greenfield**
as the spec’s as-built baseline states; foundations already exist
(`ForgeClient.get_pull_request`, `MetaPrIntakeService` shape, RunStore timeline,
`BoardService.list_tickets`, programme-token auth, on-disk
`delivery-contract.yaml`). Largest W0 engineering drivers are confirmed code
gaps (PRD A6): no `list_reviews` / `list_check_runs` / merge state on ForgeClient,
and contract `github.labels`/`review_roles` are loaded then discarded in
`WorkflowEngine.load_pin`. No Accepted ADR conflicts; no blocking PM/domain
items. Spec Q-1…Q-4 remain non-blocking with documented defaults for TDD.
Proceed to `/spec-technical-review` on **`pass`**.

**Findings:** 8 total (0 Critical, 0 Should fix, 3 Verify, 5 Gap)

### Derived counts (lane × severity)

| Lane | Blocking open | Non-blocking open | Resolved |
|------|---------------|-------------------|----------|
| PM | 0 | 1 (Q-1 OpenAPI fields) | 0 |
| PE / ADR | 0 | 3 (Q-2…Q-4) | 0 |
| Domain | 0 | 0 | 0 |
| Auto-fix | 0 | 0 | 0 |

| Severity | Unresolved count |
|----------|------------------|
| Critical | 0 |
| Should fix | 0 |
| Verify / Gap (informational) | 8 |

### Selected workflow outcome

| Field | Value |
|-------|-------|
| Outcome | `pass` |
| Rationale | Source freshness CURRENT; zero unresolved blocking PE/ADR/PM/domain items; greenfield gaps are expected implementation work already scoped by wave table |
| Next (from workflow) | `spec-technical-review` |

Informational Gap/Verify observations do **not** select `findings`. Technical
review remains required per pin (pass and findings both route there).

## Baseline snapshot (F1)

| Area | Current state | Evidence |
|------|---------------|----------|
| Toolchain | `make check` (black, ruff, pyright, import-linter) | `Makefile`; `.harness/profile.yaml` |
| Unit tests | `make test` → `tests/unit/` (34 modules); meta intake + forge + board + runs covered; **no** checkpoint/initiative read-out tests | `tests/unit/`; `test_meta_pr_intake.py`, `test_forge_client.py` |
| Live verify | 12 scripts under `tests/verify/`; **no** INIT-011 checkpoint/visibility script yet | `tests/README.md`; `tests/verify/*.py` |
| Pin consume | `.harness-pin.yaml` `agent_skills.ref: v0.5.0-rc.2`; `WorkflowEngine` loads `prayog-skills/delivery-contract.yaml` but retains only `_contract_id` | `workflow_engine.py` L28–52; `delivery-contract.yaml` L157–223 |
| As-built | INIT-001…010 matrices; **no INIT-011 section yet** (updated 2026-08-06) | `docs/specification/as-built/implementation-status.md` |
| CI | Placeholder / `make check` + unit per as-built | as-built testing harness table |

### ADR pass (pre-T2)

| ADR | Domain matched | Status |
|-----|----------------|--------|
| ADR-001 | Durable store / RunStore | Accepted — read |
| ADR-002 / ADR-005 | Programme-token control-plane auth | Accepted — read |
| ADR-003 | ForgeClient infra vs business | Accepted — skim |
| ADR-004 | Programme / pin config authority | Accepted — read |
| ADR-009 | Forge mutate authority (must not write) | Accepted — read |
| ADR-010 | Meta intake / dual workspace | Accepted — skim |
| ADR-006…008 | Adapters / handoff / invocation | Skipped — not in 011 product surface |

### MDC pass (pre-T2)

| MDC file | Domain | Read / skipped |
|----------|--------|----------------|
| `architecture.mdc` | Layering, API mounts | read |
| `http-api-conventions.mdc` | GET query vs body | read |
| `infra-services.mdc` | ForgeClient / HTTP clients | read |
| `repository-pattern.mdc` | RunStore persistence | read |
| `pydantic-schemas.mdc` | Models in `src/models/` | read |
| `dependency-injection.mdc` | Service lifecycle | read |
| `fail-fast.mdc` | No silent cache-as-current | read |
| `testing-verify-flows.mdc` | verify vs unit | read |
| `database-migrations.mdc` | Human Alembic | read |
| Others (logging, imports, tooling, …) | not primary for this INIT | skipped |

## Traceability matrix

| Spec REQ / wave | Spec claim | Code evidence | Unit | Verify | Status |
|-----------------|------------|---------------|------|--------|--------|
| REQ-01 / W0 | Status-check accepts pin checkpoint id + PR refs; read-only | No service/route; pin ids exist in `delivery-contract.yaml` `review_roles` | — | — | **gap** |
| REQ-02 / W0 | Evidence from pin `github.labels` + `review_roles` live at head | Contract on disk; `WorkflowEngine.load_pin` discards `contract_raw` after id extract (`workflow_engine.py`) | — | — | **gap** (loader partial) |
| REQ-04 / W0 | Itemized missing items | No response model | — | — | **gap** |
| REQ-05 / W0 | 0 writes from status-check path | ForgeClient forbids `*-lgtm` writes (`forge_client.py`); path absent | `test_forge_client` (label guard) | — | **partial** (guards exist; path N/A) |
| REQ-03,06–08 / W1 | `checked_sha`/`checked_at`, persist, history, composed read-out | RunStore `run_events` JSONB substrate (`run_store_schema.py`); no check event type / history API | `test_run_timeline` | — | **gap** (substrate partial) |
| REQ-09–11 / W2–W3 | Initiative list/detail + meta bridge | `POST /initiatives/closure/start` only (`initiatives_routes.py`); `MetaPrIntake` + `get_pull_request` for meta | `test_meta_pr_intake`, `test_closure_start` | — | **gap** (GET surface) |
| REQ-14–15 / W4 | Wave map statuses | `BoardService.list_tickets` + `GET /runs` filters | `test_board_service` | `verify_board` | **gap** (composition) |
| REQ-12–13 / W5 | Spec-lane read-out | Run timeline + wave-start persist PR; no `/initiatives/{id}/spec` | `test_wave_start` | `verify_spec_lane` (lane, not read-out) | **gap** |
| REQ-16–17 / W6 | Implementation task progress | `GET /runs/{id}` stages/events (`runs_routes.py`) | `test_run_timeline` | `verify_status_metrics` | **partial** |
| REQ-18–20 / W7 | Closeout + drift | Closeout mutate exists; no drift baseline records / GET closeout | `test_wave_closeout` | `verify_wave_closeout` | **gap** |
| REQ-21–24 / W8 | Merge confirm + completion | No merge state on PR doc; `closure_done_gate` mutate-only Done semantics | `test_closure_start` | `verify_initiative_closure` | **partial** (Done-gate) / **gap** (GET) |
| REQ-25–27 / W9 | Closure preview + CAP-01 reuse | No preview route; purge skill manifests not exposed via API | — | — | **gap** |
| REQ-28 / all | GET-only; 0 new writes | No CAP routes yet; mutate surface remains INIT-010 | code inventory | — | **exists** (vacuously for new surface) |

## ADR traceability (F13)

| Spec REQ / wave | Relevant ADR(s) | Status | Finding |
|-----------------|-----------------|--------|---------|
| CAP-02 / W1 check persistence | ADR-001 (Postgres RunStore SSOT) | aligned | N/A — table vs `run_events` shape is TDD within ADR-001 |
| All new GET routes / auth | ADR-005 (programme-token control-plane) | aligned | N/A — extend allowlisted mounts + `Depends(verify_programme_service_token)` |
| REQ-05 / REQ-28 no forge writes | ADR-009 (pin forge mutate authority) | aligned | N/A — this INIT must not invoke mutate forge actions |
| CAP-01 vs MetaPrIntake | ADR-010 (lane intake) | aligned | N/A — intake remains accept-gate; CAP-01 is separate read reconcile (PE Q-4 for TDD shape) |
| CTR-01 contract vocabulary | ADR-004 (pin/config authority) | aligned | N/A — expose pin contract sections without redesigning ownership |
| NEW-ADR | — | none required | No undocumented strategic alternative clears ADR qualification bar; reversible choices stay in TDD |

## Governance findings (F13–F14)

| ID | Check | Spec quote | Governing doc | Finding |
|----|-------|------------|---------------|---------|
| FF-01 | F14 | "Target API surface … `GET /api/v1/checkpoints/status`" | `http-api-conventions.mdc`; `architecture.mdc` | Gap (info): routes named in PRD/spec (G7) are product-normative; handlers must use Pydantic models from `src/models/` and programme-token deps — record for TDD, not a conflict |
| FF-02 | F14 | "Every CAP-01 call persists a check record … into Gateflow's existing run/timeline store" | `database-migrations.mdc`; ADR-001 | Verify (info): if TDD chooses a sibling table (vs `run_events`), human owns Alembic revision — plan must not agent-commit `versions/` |

## Findings by severity

### Critical

_None._

### Should fix

_None._

### Verify (informational)

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-03 | F3 | No live verify script yet for checkpoint status-check or initiative visibility; plan must name `tests/verify/` modules per wave exit | `tests/verify/` inventory; `tests/README.md` feature maps stop at INIT-010 |
| FF-04 | F8 | CI remains toolchain + unit; live reconcile verify stays local/board Verify column (same as prior INITs) | `testing-verify-flows.mdc`; as-built CI placeholder |
| FF-02 | F14 | Alembic ownership if CAP-02 adds tables | `database-migrations.mdc` |

### Gap (informational)

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-05 | F2 / F5 | CAP-01…10 product surface absent; spec as-built correctly records gap | No `checkpoints_routes.py`; `initiatives_routes.py` is POST-only |
| FF-06 | F2 / F10 | ForgeClient lacks `list_reviews` / `list_check_runs` / merged state (PRD A6 confirmed) | `forge_client.py` `get_pull_request`; `GithubPullRequestDocument` fields only title/body/state/labels/head/base |
| FF-07 | F2 | `delivery-contract.yaml` vocabulary not retained after `load_pin` | `workflow_engine.py` keeps `_contract_id` only |
| FF-08 | F5 | As-built has no INIT-011 matrix yet (expected until first wave grounds) | `implementation-status.md` |
| FF-09 | F4 | No unit modules for checkpoint evidence / initiative read-outs yet | `tests/unit/` listing |

## Impact surface

| Wave / area | Likely files/modules | Test touch |
|-------------|----------------------|------------|
| W0 ForgeClient + models | `src/infra_services/forge_client.py`; `src/models/meta_pr_models.py` (or sibling) | `test_forge_client.py` extend |
| W0 evidence resolver + GET status | new business service; `src/api/v1/checkpoints_routes.py`; `WorkflowEngine` contract accessor; `src/app.py` `public_paths` | new unit + `verify_checkpoint_*` |
| W1 persistence + history | `run_store_*` schema/repo/models; checkpoints history route | `test_run_store_models` / new |
| W2–W3 initiative GETs | extend `initiatives_routes.py` or sibling read router; compose runs + board + meta | unit + verify |
| W4–W9 composed read-outs | initiative wave/spec/closeout/merge/completion/closure GETs; reuse CAP-01/05 + `closure_done_gate` semantics | unit + verify per wave |
| Docs | `tests/README.md` feature map; as-built matrix | inspection |

## Risks & assumptions

| ID | Risk / assumption | Mitigation |
|----|-------------------|------------|
| A-6 | ForgeClient extension underestimated as “reuse only” | Spec Q-3 default: include in W0; confirmed by code |
| R-1 | Silent cache of GitHub evidence recreates stale-pass | Spec fail-closed on unreachable; fail-fast.mdc |
| R-2 | CAP-02 unbounded event growth | Reuse RunStore retention; no new storage tier (spec A-3) |
| R-3 | Meta App installation lacks `prayog-meta` | Spec Q-2 default same credentials; W3 verify |
| A-7 | MetaPrIntake is not CAP-01 | Confirmed — initiative derive only |

## Recommended spec edits

- None required for feasibility **pass**. Optional clarity (non-blocking): note that existing `initiatives_routes.py` is **closure mutate only**, so CAP-03+ GETs are additive siblings under the same mount prefix.

---

## Open items by lane

| ID | Lane | Question / item | Blocking | Owner | Status | Required by | Default if deferred | Evidence | Resolution reference |
|----|------|-----------------|----------|-------|--------|-------------|---------------------|----------|----------------------|
| Q-1 | PM / PE | Exact OpenAPI / problem+json field names (PRD OQ-01) | no | PE | open | OpenAPI / implement | Route paths + HTTP semantics remain normative | Spec Q-1; Appendix A | pending TDD/OpenAPI |
| Q-2 | PE | Meta bridge same App credentials vs separate read scope | no | PE | open | W3 | Same ForgeClient/App | Spec Q-2; `meta_pr_intake.py` already fetches meta PRs | pending TDD |
| Q-3 | PE | W0 includes ForgeClient `list_reviews` / `list_check_runs` / merge fields | no | PE | open | W0 | **Include extension in W0** | FF-06; PRD A6 | default accepted |
| Q-4 | PE | CAP-01 generalize `MetaPrIntakeService` vs new service beside it | no | PE | open | technical review | New read-only evidence service sharing ForgeClient; leave intake accept-gate unchanged (ADR-010) | Spec Q-4; `meta_pr_intake.py` | pending TDD |

### PM questions (product scope, UX, priority)

#### Blocking — must resolve before spec merge

_None._

#### Defer — can proceed with documented assumption

1. **Q-1** — OpenAPI field names deferred; route shapes + 400/404/200 stay normative.

### PE questions (engineering decisions — resolved by `/spec-technical-review`)

#### Blocking for implementation plan

_None._

#### Defer with default

1. **Q-2** — same credentials for meta bridge.
2. **Q-3** — ForgeClient read extension in W0.
3. **Q-4** — new CAP-01 service beside MetaPrIntake (default); TDD confirms module graph.

### Domain clarifications (business source-of-truth)

| # | Question | Suggested SME | Blocks |
|---|----------|---------------|--------|
| — | None | — | — |

### Auto-fixable (agent resolves later — not inside this skill)

| # | Item | Fix |
|---|------|-----|
| — | None identified this run | — |

---

## Check summary

| Check | Status | Findings |
|-------|--------|----------|
| F1 Baseline snapshot | PASS | Toolchain, unit, verify, as-built inventoried |
| F2 Spec → code map | PASS | Gaps expected; foundations mapped |
| F3 Spec → verify map | PASS | FF-03 informational — no 011 scripts yet |
| F4 Spec → unit map | PASS | FF-09 informational |
| F5 As-built drift | PASS | Spec as-built accurate; FF-08 matrix deferred to ground |
| F6 Docs drift | PASS | README/AGENTS/rules/ADR index consistent; 011 feature map TBD at implement |
| F7 Overlap risk | PASS | N/A until verify scripts land — follow testing-verify-flows (no dual full journeys) |
| F8 CI vs live boundary | PASS | FF-04 informational |
| F9 Cross-service touch | PASS | CTR-01 pin file present; CTR-02/03 GitHub REST read-only — no foreign repo code |
| F10 Assumptions | PASS | A-6/A-7 confirmed; A-3 substrate partial |
| F11 Effort drivers | PASS | See Impact surface (W0 client+resolver heaviest) |
| F12 PM questions | PASS | Q-1 non-blocking |
| F13 ADR conformance | PASS | Aligned ADR-001/004/005/009/010; no NEW-ADR |
| F14 MDC conformance | PASS | FF-01/FF-02 informational only |

**Check PASS** = zero unresolved blocking findings (informational OK).

**Draft verdict:** PASS

---

## Next steps

> Persist this report locally alongside the spec draft. Fill `handoff.forge` for
> `/commit-workspace` onto Draft spec PR [#159](https://github.com/drivestream-lab/gateflow/pull/159) —
> **do not** commit, push, open PRs, or apply labels inside this skill.
> Gate 2 stays **`spec-pending`**.

**PM questions** → none blocking; Q-1 optional on meta PRD [#30](https://github.com/drivestream-lab/prayog-meta/pull/30).

**PE questions** → discuss on Draft spec PR #159; run `/spec-technical-review` next.

**Domain clarifications** → none.

**Auto-fixable items** → none.

### Forge readiness

| Item | Value |
|------|-------|
| Local report path | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-011.md` |
| Target branch | `chore/INIT-GATEFLOW-011-spec-gateflow` |
| Recommended forge | `/commit-workspace` (Gate 2 stays `spec-pending`) |
| Mutations performed by this skill | **none** |

```
Draft spec PR: chore/INIT-GATEFLOW-011-spec-gateflow  (spec-pending) #159
When ready:
  [x] Source freshness is CURRENT
  [x] All blocking PM questions answered (none)
  [x] All blocking Domain clarifications answered (none)
  [ ] Spec updated only if answers change behavior (N/A)
  [x] Feasibility clean → proceed: /spec-technical-review
  [ ] After TDD (+ ADRs if any) + plan on branch (Forge publish):
      PE sets spec-lgtm + Approve on exact head → merge
  [ ] After merge: `/create-board-tickets` from plan §9
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: initiative-feasibility
  outcome: pass
  artifact:
    path: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-011.md
    digest: sha256:bd8920bec78c6b07fa56624e810fcdc8ab14beb75957827ace27dd435da70709
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    spec_pr: "https://github.com/drivestream-lab/gateflow/pull/159"
    spec_pr_head: "e0384fd5bdb1fc53ec2c7e8eac905643782d5474"
    source_freshness: CURRENT
    new_adr: false
    d_checks: pass
    findings_total: 8
    findings_critical: 0
    findings_should_fix: 0
    findings_verify_gap: 8
    nonblocking_questions: "Q-1,Q-2,Q-3,Q-4"
    lane_pm_blocking: 0
    lane_pe_blocking: 0
    lane_domain_blocking: 0
  next_candidates:
    - spec-technical-review
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    draft: true
    apply_labels: []
    title: "[INIT-GATEFLOW-011] Feasibility — Day-1 visibility and GitHub reconcile"
    body_path: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-011.md
```

# INIT-GATEFLOW-009 — spec slice for gateflow

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-009 |
| PRD | `prayog-meta/prd/INIT-GATEFLOW-009.md` |
| PRD digest | `sha256:76ab22b3c197b9d0cb6b08e6cea379c4e07b3a471b8a88203fddca6014c1c012` |
| Meta PR | https://github.com/drivestream-lab/prayog-meta/pull/23 |
| Meta PR approved head | **pending Gate 1** — current head `6660aa4fefbcd80324cb970aa5bab642d3e5e0a1` (no tech-lead APPROVED review; label `impact-map-pending`) |
| Impact map | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-009.md` |
| Impact-map revision | `1` |
| Repo scope digest | `sha256:d0a2b62632113db0fa64cb7d7e63dc393fa5a8217092dda242a99b3392978e9b` |
| Tech-lead approval | **pending** — required per `sdd-delivery/v2` (`impact-map-lgtm` + GitHub Approve on exact head) |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-03 |
| Status | Draft — dev review required; **Gate 1 closed** until meta PR #23 approved |

## Overview

This initiative is a **live prove-out**, not a rebuild: Gateflow must demonstrate
that the existing factory delivers a **Draft Spec PR whose tip contains committed
artifacts** from orchestrated content steps (spec lane), that **wrap-up** works on
that PR, that the **authorize API** gates sensitive forge steps, and that a
**feature readiness freeze** plus **basic automated PR checks** protect the gains.

Gateflow owns orchestration, ForgeClient publish/open, authorize API, CI wiring,
and in-repo freeze records. **prayog-meta** hosts PRD/impact map (Gate 1 only).
**prayog-skills** is consume-only (`v0.5.0-rc.2` family). **gateflow-ops** is
deferred until after the freeze.

**As-built baseline (2026-08-03):** Implement lane and Pass-1 automated forge
(INIT-008) are **human_approved**. Spec lane start, meta intake, automated
`spec-pr-action`, publish path, and authorize API exist in code (unit-covered);
**live spec Pass-1**, **spec wrap-up**, **live authorize**, and **CI** remain
unproven. Placeholder `.github/workflows/ci.yml` must be replaced (REQ-05).

**Delivery waves (product-normative; plan may refine):**

| Wave | Intent | Exit REQs |
|------|--------|-----------|
| **W0** | Confirm skills pin + meta fixtures / reviewer checklist before W1 | REQ-01 (partial), assumptions A-01…A-02 |
| **W1** | Live Draft Spec PR tip deliverable + honest stop + reviewer confirmation | REQ-01…REQ-06 |
| **W2** | Spec wrap-up live prove-out on that Draft Spec PR | REQ-07 |
| **W3** | Authorize API live prove-out; feature readiness freeze; basic PR checks | REQ-08…REQ-12 |

## Functional requirements

| ID | Requirement | PRD source | Condition / event | Observable result | Evidence layer |
|----|-------------|-----------|-------------------|-------------------|----------------|
| REQ-01 | Spec wave start is accepted only when programme meta preconditions are satisfied (bound meta PR, meta workspace, app workspace, pin-orchestrated `start_node`). | PRD REQ-01 §US-1; CAP-01; Error table | **When** PE calls `POST /api/v1/waves/spec/start` with programme token and required bind fields | **Then** run is enqueued with stored `meta_pr_url` / `meta_head_sha` when intake passes; **when** preconditions fail, start returns fail-closed (no run counted as spec prove-out success) | unit + live verify |
| REQ-02 | After each orchestrated content hop with pin `forge.commit_workspace: required`, Gateflow publishes produced workspace artifacts to the **run head** before ingesting handoff and advancing. | PRD REQ-01 §US-1 bullets 2–4; CAP-01; Architecture Path A | **When** a content skill (e.g. `spec-draft`, `initiative-feasibility`) completes with `outcome: pass` and dirty/ahead paths exist | **Then** ForgeClient commits those paths to the run branch; empty required publish fails closed; tip SHA advances | unit + live verify + PR tip inspection |
| REQ-03 | Automated `spec-pr-action` opens or updates the **Draft Spec PR** on the run head without interactive authorize when pin marks the node `authorization: automated` and `handoff.forge` requires are complete. | PRD REQ-01 §US-1 bullets 3–4; CAP-01; INIT-008 REQ-12 | **When** walker reaches `spec-pr-action` after successful `spec-draft` publish | **Then** Draft Spec PR exists, is linked on the run record (`pr_number`), and projects `spec-pending`; no `*-lgtm` labels written | unit + live verify + PR inspection |
| REQ-04 | Spec Pass-1 walker stops at the first honest human or manual boundary per pin; it does not invent merge, gate approvals, or skip human-checkpoint nodes. | PRD REQ-01 §US-1 bullet 5; CAP-01; Non-Goals | **When** the next pin node is `dispatch: manual` or `type: human-checkpoint` (e.g. `spec-implementation-plan`, `spec-human-decision`, `technical-review-approval`) | **Then** run status is `stopped` with stop reason and handoff context persisted; walker does not auto-continue past that gate | unit + live verify + timeline inspection |
| REQ-05 | A live prove-out run leaves a Draft Spec PR whose tip includes committed outputs from the automated steps executed in that run; an empty Draft Spec PR does **not** satisfy this initiative. | PRD REQ-01 Success Criteria; REQ-02 §US-2 bullets 1–2; CAP-01, CAP-02 | **When** W1 live verify completes the orchestrated hops through the first honest stop | **Then** human reviewer can confirm on the PR that expected artifact paths (e.g. `docs/specification/product/INIT-GATEFLOW-009-gateflow.md`) are on the tip; prove-out record cites PR URL | live verify + human inspection |
| REQ-06 | Live verify script documents and exercises the spec Pass-1 chain through the manual stop (or legitimate blocked stop at `spec-human-decision`). | PRD REQ-01; Evaluation strategy; as-built gap | **When** operator runs the documented spec-lane verify command with dogfood knobs enabled | **Then** script asserts start accept, Cursor success on hops that ran, terminal `stopped` at a valid gate, and `pr_number` when `spec-pr-action` was reached | live verify (`tests/verify/verify_spec_lane.py`) |
| REQ-07 | After W1 tip confirmation, spec **wrap-up** is live-proven on the same Draft Spec PR through wave sign-off; prior “spec wrap-up skipped” programme note is lifted. | PRD REQ-02 §US-2 bullet 3; CAP-02; W2 | **When** PE starts wrap-up on the confirmed Draft Spec PR per existing shared wrap-up path | **Then** wrap-up walk completes through wave sign-off with committed artifacts on the PR tip; programme records wrap-up as proven | live verify + wave sign-off record |
| REQ-08 | On a sensitive external-action marked `authorization: explicit`, the run **stops** and does not perform the forge side effect until programme authorize succeeds. | PRD REQ-03 §US-3 bullet 1; CAP-03; Path B | **When** walker would next execute an explicit external-action (e.g. `create_board_tickets`) | **Then** run is `stopped` with pending forge; no board/issue side effect appears yet | unit + live verify |
| REQ-09 | Calling `POST /api/v1/runs/{id}/forge/authorize` with approval performs the pending forge side effect; calling without approval or in wrong state does not. | PRD REQ-03 §US-3 bullets 2–3; CAP-03; Error table | **When** PE submits authorize with `authorized=true` on a stopped run at explicit forge gate | **Then** side effect is visible (e.g. board tickets); **when** denied or wrong state, no side effect and run remains fail-closed | unit + live verify |
| REQ-10 | At least one **live** recorded run demonstrates stop → authorize API → side effect; paper-only waiver is not an exit path for this initiative. | PRD REQ-03 §US-3 bullet 4; Success Criteria; Locked decisions | **When** W3 authorize prove-out is executed | **Then** Live-Verify report cites run id, stop event, authorize call, and observable side effect | live verify report |
| REQ-11 | Feature readiness freeze package lists **features proven** vs **features deferred** using feature names (not horizon nicknames); includes coding-lane baseline, spec Draft Spec PR, authorize API, wrap-up, basic PR checks; names ops portal as deferred. | PRD REQ-04 §US-4; CAP-04 | **When** W3 freeze is published | **Then** committed artifact under `docs/specification/` (and referenced meta planning note if programme adds one) states proven/deferred lists; as-built updated to match | inspection |
| REQ-12 | Placeholder CI is replaced with **basic automated PR checks** that fail closed on Gateflow repo PRs (minimum: existing `make check` + `make test`; branch/PR hygiene as applicable). | PRD REQ-05 §US-5; CAP-05; Success Criteria | **When** a PR is opened or updated against `develop`/`main`/`feature/**` | **Then** GitHub check run `ci` executes real lint/unit steps and fails on violation; orchestrated PR behavior matches Gateflow repo CI policy | CI workflow + inspection |

> **Id convention:** `REQ-*` canonical (`prayog-skills/references/id-conventions.md`).
> Every row traces to PRD `CAP-01`…`CAP-05` / `REQ-01`…`REQ-05` or named §sections.

**Inherited (reuse — do not rebuild):** INIT-001…008 control plane, lane starts
(ADR-010), ForgeClient publish/authorize (ADR-009), bound-input + baton ingest
(INIT-005), automated vs explicit external-action (INIT-008), closeout/learning
(INIT-007 — spec-lane closeout REQ-15 was PE-waived for implement-first dogfood).

**Explicit non-goals:** Rebuild coding start/walker/wrap-up/authorize; ops portal
UI; second coding agent; Slack/Teams; exhaustive skill matrix; auto-merge;
authorize-then-resume old run; skills pin redesign; PE-waive Gate 1 ceremony;
IDE confirm prompts as Gateflow human gate.

## Negative and failure paths

| REQ | Condition | Required behavior | Evidence |
|-----|-----------|-------------------|----------|
| REQ-01 | Missing meta PR / meta folder / invalid intake | Start fails closed; no empty Draft Spec PR counted as success | unit + live verify |
| REQ-02 | Required publish with nothing to commit | Fail closed; run records failure; tip without step outputs ≠ success | unit |
| REQ-02 | Forge/commit I/O error mid-walk | Run records failure; partial tip without committed outputs ≠ success | unit + timeline |
| REQ-03 | Automated `spec-pr-action` with incomplete `handoff.forge` requires | Fail closed; no Draft Spec PR counted as success | unit |
| REQ-05 | Draft Spec PR opened with no committed step outputs | Does **not** satisfy REQ-05 / initiative success | PR inspection |
| REQ-08 | Sensitive step reached while run not stopped | Must not mutate before authorize | unit + live verify |
| REQ-09 | Authorize deny / wrong state / API unavailable | No side effect; prove-out remains fail until live path works | unit + live verify |
| REQ-04 | Walker attempts to skip manual/human-checkpoint node | Stop at gate; no silent advance | unit + live verify |

## Out of scope for this repo

- **gateflow-ops** — ops portal / BFF UI (deferred per impact map §3; after freeze)
- **prayog-meta** — PRD/impact-map authoring (Gate 1 host only); optional vision note at freeze is programme hygiene, not gateflow engineering delivery
- **prayog-skills** — pin/skill package changes (consume `v0.5.0-rc.2` family only)
- **launchpad** — product work (monitor harness remount only)
- Rebuilding coding-lane, authorize, learning, or metrics subsystems already baselined

## Cross-service contracts

| Contract ID | Provider / owner | Consumer / owner | Entry point | Input shape | Output shape | Invariants | Errors | Compatibility / versioning | Contract-test location |
|-------------|------------------|------------------|-------------|-------------|--------------|------------|--------|----------------------------|------------------------|
| CTR-01 | prayog-skills / PE | gateflow | Pinned `sdd-delivery/v2` workflow + delivery contract + handoff envelope; consume skills tip | pin YAML + submodule ref | resolved nodes, forge policy, orchestrated spec chain | Missing `authorization` on external-action → invalid pin; spec-draft orchestrated on active tip | Fail closed on pin load | `v0.5.0-rc.2` family consume only | `test_forge_policy`, pin load tests |
| CTR-02 | gateflow / PE | GitHub (forge) | ForgeClient publish + `open_draft_pr` for spec lane | workspace paths; title/body/head/base | commit SHA; PR number; projection labels | Never write `*-lgtm`; no merge action; content skills never mutate | I/O / auth → fail closed | ADR-003; INIT-008 automated path | `test_forge_client`, `verify_spec_lane` |
| CTR-03 | gateflow / PE | GitHub / board | Programme authorize → sensitive forge (e.g. board tickets) | `authorized`, run context, pending action | tickets/issues visible | Explicit-only mutate; API trigger not IDE typing | Deny/wrong state → no mutate | INIT-006 / INIT-008 explicit path | `test_forge_action_service`, live verify W3 |

## Non-functional requirements

| Area | Requirement or N/A rationale | Acceptance / evidence |
|------|------------------------------|-----------------------|
| Security | Programme token on starts/authorize; no auto-merge; Forge never writes `*-lgtm`; authorize API authenticated | unit + inspection |
| Reliability | Fail closed on missing Gate 1 (spec-draft blocked), required empty publish, incomplete forge requires, authorize errors | unit + live verify |
| Performance / capacity | N/A — prove-out initiative; no new SLA targets beyond existing worker/API | inspection |
| Observability | Run timeline + `run_stopped` payload include stage, outcome, blockers, next_candidates for ops portal | unit + live verify |
| Privacy / data handling | PR bodies from workspace paths; no secret materialization in artifacts | inspection |
| Migration / compatibility | Reuse existing APIs/pin; no parallel approval paths outside `sdd-delivery/v2` | docs |
| Rollback / recovery | Pin rollback or disable worker; explicit authorize remains for board seed | runbook inspection |
| Operations / support | Documented verify commands for spec Pass-1, wrap-up, authorize prove-outs | `tests/README.md`, Live-Verify reports |

## Assumptions

| ID | Assumption | Evidence | Owner | Status | Invalidated when |
|----|------------|----------|-------|--------|------------------|
| A-01 | Skills tip `v0.5.0-rc.2` family is remounted/consumed for prove-outs | PRD A-01; as-built pin note | PE | confirmed | Pin family changes |
| A-02 | Meta PR + meta folder fixtures available before W1 | PRD A-02; meta PR #23 exists locally | programme | **open** until Gate 1 approved | Meta PR rejected or fixtures missing |
| A-03 | PE can call authorize API with programme service token | PRD A-03; as-built authorize path | PE | confirmed | Token path removed |
| A-04 | Production forge uses GitHub App / ForgeClient (not `gh` as cloud success path) | PRD A-04; ADR-003 | PE | confirmed | Transport policy changes |
| A-05 | Gate 1 follows `sdd-delivery/v2` meta PR path (`impact-map-*` + Approve) — **no PE-waive** for this INIT | PRD A-05; Locked decisions | PE | confirmed | PE attempts waive |
| A-06 | Human Alembic for `runs.meta_pr_url` / `meta_head_sha` applied before live spec start | as-built INIT-006 gap | PE | open | Columns live in target env |

## Spec questions (ambiguities — need PM or domain confirmation before feasibility)

| ID | Lane | Question | Owner | Blocking | Required by | Default if deferred | Status | Resolution link |
|----|------|----------|-------|----------|-------------|---------------------|--------|-----------------|
| Q-1 | PE | Gate 1: meta PR #23 requires tech-lead **Approve** on head `6660aa4…` with `impact-map-lgtm` before spec lane can emit `pass` / open Draft Spec PR via automated forge. Proceed with local draft only until approved? | PE | **yes** | spec-draft / spec-pr-action | Stop at `spec-human-decision`; no Draft Spec PR via automated path | **open** | https://github.com/drivestream-lab/prayog-meta/pull/23 |
| Q-2 | PE | W3 authorize live prove-out: use `create_board_tickets` as the canonical side effect, or another explicit external-action? | PE | no | W3 live verify | **Board ticket seed** from plan §9 (existing explicit node) | open | — |
| Q-3 | PE | CI scope: is `make check` + `make test` sufficient for “basic automated PR checks”, or require additional branch-name/hygiene gate in W3? | PE | no | W3 / REQ-12 | **`make check` + `make test`** in `ci` job; hygiene follow-up if needed | open | — |
| Q-4 | PE | Feature freeze vision/planning note: gateflow-only as-built + report, or also require prayog-meta planning doc update in same merge window? | PE | no | W3 / REQ-11 | **Gateflow freeze report + as-built**; meta note optional same window per PRD “lean same package” | open | — |

## Draft check summary (D1–D12)

| Check | Status | Evidence / findings |
|-------|--------|---------------------|
| D1 Approved handoff current | **FAIL** | Meta PR #23 OPEN; label `impact-map-pending`; **zero** GitHub reviews; no tech-lead APPROVED on head `6660aa4fefbcd80324cb970aa5bab642d3e5e0a1`. PRD digest matches impact map (`sha256:76ab22…`). Repo affected with scope digest `sha256:d0a2b626…`. |
| D2 Complete PRD traceability | **PASS** | REQ-01…REQ-12 map to PRD CAP-01…05 / REQ-01…05 and named §sections. |
| D3 Repo-bounded scope | **PASS** | Matches impact map revision 1 gateflow-only scope; gateflow-ops deferred; meta/skills consume-only. |
| D4 Observable acceptance | **PASS** | Every REQ has condition/event, observable result, evidence layer; implementation-neutral. |
| D5 Negative/failure paths | **PASS** | Negative table covers start reject, empty PR, commit/forge failure, authorize deny/unavailable. |
| D6 Assumptions/questions | **PASS** | Assumptions recorded; Q-1 blocking with owner/default; Q-2…Q-4 non-blocking with defaults. |
| D7 Cross-repository contracts | **PASS** | CTR-01…03 from impact map §6 with semantic entry points. |
| D8 NFR applicability | **PASS** | Eight NFR rows with rationale or N/A. |
| D9 As-built alignment | **PASS** | Distinguishes existing (spec start, automated spec-pr, authorize unit) vs prove-out gaps (live spec, wrap-up, CI placeholder). |
| D10 Dependency order | **PASS** | W0→W1→W2→W3 matches impact map §7; prayog-skills pin before gateflow waves. |
| D11 Zero unresolved blockers | **FAIL** | **Q-1** material — Gate 1 not approved; blocks `pass` and automated Draft Spec PR prove-out. |
| D12 Output completeness | **PASS** | Header, REQs, NFR, contracts, questions, check summary, outcome, PR readiness present. |

**Draft verdict:** **FAIL**

**Selected workflow outcome:** `blocked`
**Outcome reason:** D1 FAIL — Gate 1 closed (`impact-map-pending`, no APPROVED review on current meta head); Q-1 material blocker remains. Spec draft persisted locally for dev review; PR BLOCKED until Gate 1 opens.

Do not advance to `/initiative-feasibility` or authorize automated `spec-pr-action` until Gate 1 approves meta PR #23 head and spec-draft re-runs with `outcome: pass`.

## PR readiness handoff

| Item | Value |
|------|-------|
| Workflow outcome | `blocked` — Gate 1 not approved on meta PR #23 |
| Verdict | **PR BLOCKED** |
| Existing spec PR | none |
| Proposed branch | `chore/INIT-GATEFLOW-009-spec-gateflow` |
| Proposed base | `develop` |
| Proposed title | `[INIT-GATEFLOW-009] Spec — both-lane factory prove-out (gateflow)` |
| PR type | **Draft** (entire spec lifecycle) |
| Local artifacts to publish | `docs/specification/product/INIT-GATEFLOW-009-gateflow.md`, `docs/specification/reports/PR-body-INIT-GATEFLOW-009-spec.md` |
| Forge readiness | **not filled** — `handoff.forge` only on `outcome: pass`; Gate 1 must approve first |
| Reviewer | @drivestream-lab/prayog-pe-team |
| Initial Gate 2 label | `spec-pending` (after Gate 1 + re-run pass) |
| Additional invalidation label | none |
| Blocking items | **Q-1** — Gate 1 approval on https://github.com/drivestream-lab/prayog-meta/pull/23 |

**No GitHub side effects have occurred.** After Gate 1 approval, re-run `/spec-draft` for `pass`, then authorize `/commit-workspace` / automated `spec-pr-action` or `/open-draft-pr`.

### Proposed Draft PR body

See `docs/specification/reports/PR-body-INIT-GATEFLOW-009-spec.md`.

## Developer review

- [ ] Scope matches approved impact-map repo scope digest (after Gate 1)
- [ ] REQs have condition/event, observable result, and evidence layer
- [ ] Contracts are semantic; no architecture decisions in REQs
- [ ] Gate 1 approved on meta PR #23 head before claiming PR READY
- [ ] Developer confirmed draft is ready for feasibility

## References

- PRD: `prayog-meta/prd/INIT-GATEFLOW-009.md`
- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/23
- Impact map: `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-009.md` (revision 1)
- As-built: `docs/specification/as-built/implementation-status.md`
- Pin consumer guide: `prayog-skills/docs/for-gateflow.md`
- Predecessor specs: `INIT-GATEFLOW-008-gateflow.md`, `INIT-GATEFLOW-007-gateflow.md`

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-draft
  outcome: blocked
  artifact:
    path: docs/specification/product/INIT-GATEFLOW-009-gateflow.md
    digest: sha256:e240ea6393f37800b6e95489acff3f3e0f325a4bcbb50d6f9c0e890a252c314c
  blockers:
    - Q-1
  signals:
    pr_ready: false
    gate1_closed: true
    meta_pr: "https://github.com/drivestream-lab/prayog-meta/pull/23"
    meta_pr_head: "6660aa4fefbcd80324cb970aa5bab642d3e5e0a1"
    impact_map_revision: 1
    prd_digest: sha256:76ab22b3c197b9d0cb6b08e6cea379c4e07b3a471b8a88203fddca6014c1c012
    scope_digest: sha256:d0a2b62632113db0fa64cb7d7e63dc393fa5a8217092dda242a99b3392978e9b
    d_checks: fail
    d1_status: fail
    d11_status: fail
    initiative: INIT-GATEFLOW-009
    nonblocking_questions: "Q-2,Q-3,Q-4"
  next_candidates:
    - spec-human-decision
  human_checkpoint: true
  external_action: false
```

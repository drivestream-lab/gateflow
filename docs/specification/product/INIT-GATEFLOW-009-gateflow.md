# INIT-GATEFLOW-009 — spec slice for gateflow

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-009 |
| PRD | `prayog-meta/prd/INIT-GATEFLOW-009.md` |
| PRD digest | `sha256:76ab22b3c197b9d0cb6b08e6cea379c4e07b3a471b8a88203fddca6014c1c012` |
| Meta PR | https://github.com/drivestream-lab/prayog-meta/pull/23 |
| Meta PR approved head | **pending Gate 1** — current head `6660aa4fefbcd80324cb970aa5bab642d3e5e0a1`; label `impact-map-pending`; zero APPROVED reviews |
| Impact map | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-009.md` |
| Impact-map revision | `1` |
| Repo scope digest | `sha256:d0a2b62632113db0fa64cb7d7e63dc393fa5a8217092dda242a99b3392978e9b` |
| Tech-lead approval | **not yet submitted** — Gate 1 closed until GitHub APPROVE on exact head with attestation matching map revision 1 and PRD digest |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-03 |
| Status | Draft — dev review required; **Gate 1 blocked** — do not treat as PR READY until meta PR approved |

## Overview

This INIT is a **prove-out**, not a rebuild: demonstrate that the existing Gateflow
factory delivers the **spec lane** the same way the implement lane is already trusted —
especially that a **Draft Spec PR tip contains committed artifacts** from orchestrated
content steps, that **wrap-up** is live-proven on that PR, that the **authorize API**
gates sensitive forge (not IDE typing), that a **feature readiness freeze** is written,
and that **basic automated PR checks** replace placeholder CI.

**In scope (gateflow only):** live prove-out wiring, verify scripts, as-built/reports
freeze records, and CI hardening per approved impact-map scope digest. **Out of scope:**
rebuilding orchestrator/walker/authorize APIs (reuse INIT-006/008), ops portal
(gateflow-ops deferred), skills pin redesign (consume `v0.5.0-rc.2` family only),
inventing parallel approval paths outside **`sdd-delivery/v2`**.

**As-built baseline (2026-07-30):** Spec lane start + meta intake unit-wired; automated
`spec-pr-action` and post-hop `commit_workspace` unit-covered (INIT-008); live forge
dogfood and authorize live prove **deferred**; CI is placeholder; spec-lane closeout
was PE-waived for INIT-007 — **this INIT requires spec wrap-up live prove** (REQ-02).

**Delivery waves (product-normative; plan may refine):**

| Wave | Intent | Exit REQs |
|------|--------|-----------|
| **W0** | Confirm skills pin tip + meta fixtures (PR #23 head, dual workspaces, reviewer checklist) | Preconditions for W1 |
| **W1** | Live Draft Spec PR tip deliverable + honest stop | REQ-01 |
| **W2** | Spec wrap-up live prove on confirmed Draft Spec PR | REQ-02 |
| **W3** | Authorize API live prove; feature readiness freeze; basic CI | REQ-03, REQ-04, REQ-05 |

## Functional requirements

| ID | Requirement | PRD source | Condition / event | Observable result | Evidence layer |
|----|-------------|-----------|-------------------|-------------------|----------------|
| REQ-01 | Spec wave orchestration shall leave **committed artifacts on the Draft Spec PR tip** after each orchestrated content step that produces durable output, per pin `forge.commit_workspace` and Gateflow publish process. | PRD CAP-01 / REQ-01; US-1 | **Given** a spec wave started with valid meta PR + dual workspace bind **When** orchestrated hops `spec-draft` (and later content hops such as `initiative-feasibility`) complete successfully **Then** Gateflow publishes produced files to the run head and the Draft Spec PR tip (opened/updated via automated `spec-pr-action` when pin requires) contains those artifacts — not only local workspace copies | Draft Spec PR exists; run record references `pr_number`; PR tip tree includes spec-draft output (e.g. `docs/specification/product/INIT-GATEFLOW-009-gateflow.md`) and later step outputs when run; human reviewer can confirm tip vs steps run | live verify (`verify_spec_lane`) + human PR tip inspection |
| REQ-02 | Programme shall **live-prove spec wrap-up** on the Draft Spec PR after human tip confirmation, lifting any prior “spec wrap-up skipped” note. | PRD CAP-02 / REQ-02; US-2 | **Given** REQ-01 satisfied and a human reviewer confirmed the Draft Spec PR tip **When** closeout/wrap-up is started on that PR and walked through wave sign-off **Then** wrap-up completes with committed closeout artifacts on the PR and programme records success — empty Draft Spec PR does not count | Wrap-up run reaches terminal success; PR tip gains wrap-up outputs; as-built no longer marks spec wrap-up as skipped/deferred for this prove-out | live verify + wave sign-off record + as-built update |
| REQ-03 | Sensitive forge shall **stop until authorize API approval**; approve performs side effect; deny/wrong state does not. Live prove is **required** — no paper waiver exit. | PRD CAP-03 / REQ-03; US-3 | **Given** a run whose next node is an `external-action` with `authorization: explicit` (e.g. `board-tickets-action`) **When** the walker reaches that node **Then** run stops with pending forge and **no** side effect until `POST /api/v1/runs/{id}/forge/authorize` with approval; deny/wrong state leaves side effect absent | Timeline shows STOP before mutate; authorized call creates visible forge outcome (e.g. board tickets); unauthorized call does not | live verify script + inspection |
| REQ-04 | Gateflow shall publish a **feature readiness freeze** listing proven vs deferred capabilities using **feature names** (not horizon nicknames as headline). | PRD CAP-04 / REQ-04; US-4 | **Given** W1–W3 prove-outs recorded **When** freeze package is written **Then** as-built (and linked reports) enumerate proven features (coding lane baseline, spec Draft Spec PR deliverable, authorize API, spec wrap-up, basic PR checks) and deferred features (ops portal UI, second coding agents, Slack/Teams, programme-wide self-dogfood) | Committed freeze section in `implementation-status.md` and/or linked report matches live evidence | inspection |
| REQ-05 | Gateflow PRs shall run **real basic automated checks** instead of placeholder CI. | PRD CAP-05 / REQ-05; US-5 | **Given** a pull request targeting `develop` or `main` **When** CI workflow runs **Then** checks execute repo toolchain (`make check`, `make test` or equivalent) and **fail closed** on failure — job name remains `ci` for branch protection compatibility | CI workflow runs lint/typecheck/unit; failing tests fail the check | CI run + inspection |

> **Id convention:** `REQ-*` canonical (`prayog-skills/references/id-conventions.md`).
> This INIT assigns **REQ-01…REQ-05** aligned to PRD product id map.
> Observable acceptance is implementation-neutral; evidence names proof layer only.

**Inherited (reuse — not re-specified unless prove-out gaps):** INIT-001…008 control plane;
spec/implement lane starts (ADR-010); ForgeClient publish + dual `authorization`
(ADR-009/008); baton ingest (INIT-005); board primitives (INIT-002 W2); programme
token auth; pin `sdd-delivery/v2` Gate 2 on spec PR.

## Negative and failure paths

| REQ | Condition | Required behavior | Evidence |
|-----|-----------|-------------------|----------|
| REQ-01 | Spec start rejected (missing meta PR / folder bind) | Start fails closed; no empty Draft Spec PR counted as success | unit + live verify |
| REQ-01 | Forge/commit failure mid-walk | Run records failure; tip without committed step outputs **does not** satisfy REQ-01 | live verify + timeline |
| REQ-01 | Empty Draft Spec PR opened | Does **not** satisfy success criteria or REQ-01 | human inspection |
| REQ-01 | Run silently skips honest human/manual stop | Timeline shows stop at first manual boundary; no invented merge/gate approvals | live verify + reviewer |
| REQ-02 | Wrap-up attempted before tip confirmation | Prove-out invalid until reviewer confirmation recorded | inspection |
| REQ-02 | Wrap-up skipped or paper-only | Does **not** satisfy REQ-02 or initiative success | as-built + live record |
| REQ-03 | Authorize with `authorized=false` or wrong run state | 4xx; no forge side effect | unit + live verify |
| REQ-03 | Authorize API unavailable / timeout | Side effect not performed; prove-out fails until live path works | live verify |
| REQ-04 | Freeze lists feature as proven without live evidence | Freeze invalid — must match verify records | inspection |
| REQ-05 | CI placeholder or always-green stub | Does **not** satisfy REQ-05 | CI inspection |

## Out of scope for this repo

- **gateflow-ops** — ops portal / BFF UI (deferred until after REQ-04 freeze)
- **prayog-skills** — pin package authoring or new RC; consume only
- **prayog-meta** — PRD/impact-map hosting (Gate 1); optional vision note at freeze is programme meta hygiene, not gateflow engineering delivery
- Rebuilding coding start, walker, wrap-up APIs, learning store, or authorize endpoint semantics
- Second coding agent, Slack/Teams, exhaustive skill bake-offs
- Auto-merge; authorize-then-resume into a different run without explicit restart
- IDE “please confirm” prompts as Gateflow human gate (authorize API is the gate)
- PE-waive or parallel Gate 1 ceremony outside **`sdd-delivery/v2`**
- INIT-007 implement-lane closeout re-prove (already human_approved)

## Cross-service contracts

| Contract ID | Provider / owner | Consumer / owner | Entry point | Input shape | Output shape | Invariants | Errors | Compatibility / versioning | Contract-test location |
|-------------|------------------|------------------|-------------|-------------|--------------|------------|--------|----------------------------|------------------------|
| CTR-01 | prayog-skills / PE | gateflow | Pinned `sdd-delivery/v2` workflow + delivery contract + handoff envelope | pin YAML + handoff | resolved stage/outcome + forge requires | Remount/consume `v0.5.0-rc.2` family only; pin SSOT | Missing/unknown authorization → fail closed | Unchanged — consume only | `test_forge_policy`, pin load tests |
| CTR-02 | gateflow / PE | GitHub (forge) | Logical: publish workspace to run head; open/update Draft Spec PR | paths, title, body, head/base from run context | commit SHA, PR number, projection labels | Never write `*-lgtm`; no merge action; content skills never mutate | Forge I/O errors → fail closed | ADR-003/009; automated `spec-pr-action` per INIT-008 | `test_forge_client`, `verify_spec_lane` |
| CTR-03 | gateflow / PE | GitHub / board | Logical: authorize-gated sensitive forge (e.g. board ticket seed) | programme authorize + merged pin ⋉ handoff | board issues visible | Explicit authorization only for board create; idempotent EPIC/Feature | Deny/wrong state → no mutate | INIT-002 W2 board MVP | `test_forge_action_service`, live authorize script |

## Non-functional requirements

| Area | Requirement or N/A rationale | Acceptance / evidence |
|------|------------------------------|-----------------------|
| Security | Programme token on starts/authorize; no auto-merge; Forge never writes `*-lgtm`; production forge stays GitHub App / ForgeClient path | unit + inspection |
| Reliability | Fail closed on missing meta preconditions, required empty publish, incomplete `handoff.forge` requires, forge failures mid-walk | unit + live verify |
| Performance / capacity | N/A new SLAs — prove-out records cycle time as signal only, not exit gate | inspection |
| Observability | Run timeline records api_trigger, stage success, forge apply/stop, authorize events; metrics dims inherited from INIT-003 | live verify + unit |
| Privacy / data handling | PR bodies from workspace paths; no secret materialization in published trees | path collect denylist inspection |
| Migration / compatibility | Open runs stay on current pin until explicit remount; human Alembic for `runs.meta_*` before live spec start | runbook + as-built |
| Rollback / recovery | Pin rollback or disable worker; explicit authorize remains for board; CI failure blocks merge until fixed | runbook inspection |
| Operations / support | Document reviewer checklist for tip confirmation; feature freeze readable by programme sponsor | docs in reports/as-built |

## Assumptions

| ID | Assumption | Evidence | Owner | Status | Invalidated when |
|----|------------|----------|-------|--------|------------------|
| A-1 | Skills pin `v0.5.0-rc.2` family is remounted/consumed for prove-outs | PRD A-01; harness pin record | PE | confirmed | Pin family changes |
| A-2 | Meta PR + meta folder fixtures available before W1 | PRD A-02; PR #23 exists locally | PE | confirmed | Meta PR withdrawn |
| A-3 | PE can call authorize API with programme service token | PRD A-03; existing lab path | PE | confirmed | Auth path removed |
| A-4 | Production forge uses GitHub App / ForgeClient (not `gh` as cloud success path) | PRD A-04; ADR-003 | PE | confirmed | Forge transport changes |
| A-5 | Gate 1 follows `sdd-delivery/v2` meta PR path (`impact-map-*` + Approve) | PRD A-05; impact map §12 | PE | **open** — PR #23 not yet approved | APPROVED review on head |
| A-6 | Human Alembic for `runs.meta_pr_url` / `runs.meta_head_sha` applied before live spec start | as-built INIT-006 gap | PE | open | Migration applied |
| A-7 | `verify_spec_lane` is the primary live exit script for W1 REQ-01 | tests/README; verify script docstring | PE | confirmed | PE selects alternate verify |

## Spec questions (ambiguities — need PM or domain confirmation before feasibility)

| ID | Lane | Question | Owner | Blocking | Required by | Default if deferred | Status | Resolution link |
|----|------|----------|-------|----------|-------------|---------------------|--------|-----------------|
| Q-1 | PE | Gate 1: tech-lead **APPROVED** review on meta PR #23 head `6660aa4…` with attestation matching map revision 1 and PRD digest — when will Gate 1 close? | PE | **yes** | spec-draft `pass` / W1 start | Do not advance spec PR or claim PR READY | **open** | https://github.com/drivestream-lab/prayog-meta/pull/23 |
| Q-2 | PE | Human Alembic for `runs.meta_pr_url` / `runs.meta_head_sha` — applied in target dogfood environment before W1 live prove? | PE | **yes** (live W1) | W1 live verify | Spec start may 422 or omit meta bind — live prove blocked | open | as-built INIT-006 gaps |
| Q-3 | PE | REQ-03 live prove: use **`board-tickets-action`** on a spec-lane run, or a dedicated chore run — which runbook path is canonical? | PE | no | W3 live verify | **`board-tickets-action`** after spec Gate 2 package exists on PR | open | — |
| Q-4 | PM | REQ-04 vision/planning note: gateflow writes as-built freeze only, or also commit a lean note under `prayog-meta/planning/` in the same freeze PR? | PM | no | W3 freeze | **gateflow as-built + linked report only**; meta note optional separate meta chore | open | PRD REQ-04 “same package” |
| Q-5 | PE | REQ-02 wrap-up Enter-at: reuse **`POST /api/v1/waves/closeout/start`** with spec PR bind (same as implement), or a spec-specific entry — any intake difference beyond PR URL? | PE | no | W2 plan | Reuse closeout start with Draft Spec PR URL bind; no new API | open | INIT-007 closeout API |

## Draft check summary (D1–D12)

| Check | Status | Evidence / findings |
|-------|--------|---------------------|
| D1 Approved handoff current | **FAIL** | Meta PR #23 OPEN; label `impact-map-pending`; **zero** APPROVED reviews; head `6660aa4fefbcd80324cb970aa5bab642d3e5e0a1`. PRD digest matches impact map (`sha256:76ab22…`). Repo affected with scope digest `sha256:d0a2b626…`. **Gate 1 closed.** |
| D2 Complete PRD traceability | **PASS** | REQ-01…05 map to PRD CAP-01…05 / REQ-01…05; each cites PRD section |
| D3 Repo-bounded scope | **PASS** | Matches impact-map gateflow scope digest; gateflow-ops/prayog-meta eng delivery excluded |
| D4 Observable acceptance | **PASS** | All REQs have condition/event, observable result, evidence layer |
| D5 Negative/failure paths | **PASS** | Negative table covers empty PR, forge fail, authorize deny, CI placeholder |
| D6 Assumptions/questions | **PASS** | A-1…A-7 recorded; Q-1…Q-5 with owners/defaults; Q-1 blocking |
| D7 Cross-repository contracts | **PASS** | CTR-01…03 semantic boundaries |
| D8 NFR applicability | **PASS** | Eight NFR rows |
| D9 As-built alignment | **PASS** | Baseline deferred items vs prove-out targets explicit |
| D10 Dependency order | **PASS** | Aligns impact map §7: pin → W0 fixtures → W1 tip → W2 wrap-up → W3 authorize/freeze/CI |
| D11 Zero unresolved blockers | **FAIL** | Q-1 Gate 1 approval blocking; Q-2 blocking for live W1 |
| D12 Output completeness | **PASS** | Header, REQs, NFR, contracts, questions, check summary, PR readiness present |

**Draft verdict:** **FAIL**

**Selected workflow outcome:** `blocked`
**Outcome reason:** D1 FAIL — Gate 1 not approved on meta PR #23 (`impact-map-pending`, no tech-lead APPROVE on head); D11 FAIL — blocking Q-1 open. Spec draft persisted locally for dev review; **PR BLOCKED** until Gate 1 closes.

Do not advance to `/initiative-feasibility` or authorize Forge `spec-pr-action` until outcome is `pass`.

## PR readiness handoff

| Item | Value |
|------|-------|
| Workflow outcome | `blocked` — Gate 1 not approved; blocking Q-1 |
| Verdict | **PR BLOCKED** |
| Existing spec PR | none |
| Proposed branch | `chore/INIT-GATEFLOW-009-spec-gateflow` |
| Proposed base | `develop` |
| Proposed title | `[INIT-GATEFLOW-009] Spec — both-lane factory prove-out (gateflow)` |
| PR type | **Draft** (entire spec lifecycle) |
| Local artifacts to publish | `docs/specification/product/INIT-GATEFLOW-009-gateflow.md` |
| Forge readiness | **incomplete** — do not fill `handoff.forge` until outcome `pass` and Gate 1 approved |
| Reviewer | @drivestream-lab/prayog-pe-team |
| Initial Gate 2 label | `spec-pending` (after Gate 1 closes and spec PR opens) |
| Additional invalidation label | none |
| Blocking items | Q-1 Gate 1 approval; Q-2 Alembic before W1 live |

**No GitHub side effects have occurred.**

### Proposed Draft PR body

```markdown
## Initiative

INIT-GATEFLOW-009 — Both-lane delivery factory prove-out (gateflow)

## Meta handoff

- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/23
- Approved meta head: `{pending — Gate 1}`
- Impact-map revision: 1
- PRD digest: `sha256:76ab22b3c197b9d0cb6b08e6cea379c4e07b3a471b8a88203fddca6014c1c012`
- Repo scope digest: `sha256:d0a2b62632113db0fa64cb7d7e63dc393fa5a8217092dda242a99b3392978e9b`

## Spec path

`docs/specification/product/INIT-GATEFLOW-009-gateflow.md`

## Summary

- REQ-01…REQ-05 — prove spec lane Draft Spec PR tip, wrap-up, authorize API, feature freeze, basic CI
- Reuse INIT-006/008 forge + lane infrastructure; no rebuild
- Blocking: Gate 1 approval on meta PR #23 (Q-1)

## Gate 2 — spec package readiness

Initial label: `spec-pending`

- [ ] Gate 1 `impact-map-lgtm` + Approve on meta PR head
- [ ] Spec slice published on this PR head (via Forge `/commit-workspace` / `spec-pr-action`)
- [ ] Feasibility report (later Forge publish)
- [ ] Technical design + ADRs (later Forge publish)
- [ ] Implementation plan §9 (later Forge publish)
- [ ] PE sets `spec-lgtm` on exact final head before merge

Requested reviewer: @drivestream-lab/prayog-pe-team
```

## Developer review

- [ ] Scope matches the approved impact-map repo scope digest
- [ ] REQs have condition/event, observable result, and evidence layer
- [ ] Contracts are semantic (logical operation); no architecture decisions in REQs
- [ ] Gate 1 approved on meta PR #23 before Forge publish
- [ ] No blocking question remains
- [ ] Developer confirmed draft is ready for feasibility

## References

- PRD: `prayog-meta/prd/INIT-GATEFLOW-009.md`
- Impact map: `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-009.md`
- Meta PR: https://github.com/drivestream-lab/prayog-meta/pull/23
- As-built: `docs/specification/as-built/implementation-status.md`
- Predecessor forge/lane: `docs/specification/product/INIT-GATEFLOW-008-gateflow.md`, `INIT-GATEFLOW-006-gateflow.md`
- Live verify (W1): `tests/verify/verify_spec_lane.py`
- ADR: `docs/specification/adr/adr-009-pin-forge-publish-mutate-authority.md`, `adr-010-lane-intake-and-dual-workspace-authority.md`

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-draft
  outcome: blocked
  artifact:
    path: docs/specification/product/INIT-GATEFLOW-009-gateflow.md
    digest: sha256:bda5a8cb544bbdda9dde99d65be6318845e7fd67c46182c9715a8b97b31ebca1
  blockers:
    - Q-1
  signals:
    pr_ready: false
    gate1_blocked: true
    meta_pr: "https://github.com/drivestream-lab/prayog-meta/pull/23"
    meta_pr_head: "6660aa4fefbcd80324cb970aa5bab642d3e5e0a1"
    impact_map_revision: 1
    prd_digest: "sha256:76ab22b3c197b9d0cb6b08e6cea379c4e07b3a471b8a88203fddca6014c1c012"
    scope_digest: "sha256:d0a2b62632113db0fa64cb7d7e63dc393fa5a8217092dda242a99b3392978e9b"
    d_checks: fail
    d1: fail
    d11: fail
    initiative: INIT-GATEFLOW-009
    ticket_id: "2162245"
  next_candidates:
    - spec-human-decision
  human_checkpoint: true
  external_action: false
```

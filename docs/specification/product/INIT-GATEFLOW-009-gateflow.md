# INIT-GATEFLOW-009 — spec slice for gateflow

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-009 |
| PRD | `prayog-meta/prd/INIT-GATEFLOW-009.md` |
| PRD digest | `sha256:76ab22b3c197b9d0cb6b08e6cea379c4e07b3a471b8a88203fddca6014c1c012` |
| Meta PR | https://github.com/drivestream-lab/prayog-meta/pull/23 |
| Meta PR approved head | `6660aa4fefbcd80324cb970aa5bab642d3e5e0a1` |
| Impact map | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-009.md` |
| Impact-map revision | `1` |
| Repo scope digest | `sha256:d0a2b62632113db0fa64cb7d7e63dc393fa5a8217092dda242a99b3392978e9b` |
| Tech-lead approval | GitHub APPROVED @ `6660aa4fefbcd80324cb970aa5bab642d3e5e0a1` by `0xbeefdead` (2026-08-03); label `impact-map-lgtm` |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-03 |
| Status | Draft — dev review required before Forge publish |

## Overview

This INIT is a **prove-out**, not a rebuild: Gateflow already implements the spec
lane, forge publish, authorize API, and wrap-up paths from prior INITs. This repo
**records and live-proves** that the existing factory delivers the same PR-tip
artifacts a careful human developer would leave after a spec wave — plus an
honest stop, required spec wrap-up, a live authorize path, a feature-readiness
freeze, and real basic PR checks.

**In scope (gateflow):** live Draft Spec PR tip deliverable with Gateflow-owned
commits (PRD REQ-01 / CAP-01); required spec wrap-up prove-out (PRD REQ-02 /
CAP-02); live authorize API stop→approve→side-effect (PRD REQ-03 / CAP-03);
feature-readiness / as-built freeze records (PRD REQ-04 / CAP-04); replace
placeholder CI with basic automated PR checks (PRD REQ-05 / CAP-05). Adhere to
`sdd-delivery/v2`; consume prayog-skills pin **`v0.5.0-rc.2` family** only.

**Out of scope (this repo):** ops portal / gateflow-ops UI; prayog-meta PRD or
impact-map authoring; prayog-skills pin redesign; second coding agent; Slack/Teams;
auto-merge; authorize-then-resume into the next orchestrated hop; IDE confirm
prompts as the Gateflow human gate; parallel Gate 1 ceremonies.

**Ownership boundary:** this spec states observable product behavior, acceptance,
field meaning, invariants, errors, and compatibility. It cites existing ADR/pin
constraints but does **not** choose implementation architecture — those questions
route to feasibility / technical review.

**As-built baseline (2026-08-03):** Implement lane live-proven; spec lane code and
unit coverage exist; `verify_spec_lane` opt-in script present; forge publish +
automated `spec-pr-action` wired (INIT-008); live forge dogfood and live authorize
**deferred**; CI is placeholder; spec-lane closeout was PE-waived under INIT-007
but **this INIT requires** live spec wrap-up per PRD REQ-02.

**Delivery waves (product-normative; plan may refine):**

| Wave | Intent | Exit REQs |
|------|--------|-----------|
| **W0** | Pin tip confirmed; meta PR + dual-workspace fixtures; reviewer checklist ready | REQ-1 |
| **W1** | Draft Spec PR tip deliverable live-proven; honest stop; human reviewer confirms tip | REQ-2, REQ-3 |
| **W2** | Spec wrap-up live-proven on that Draft Spec PR; prior “spec wrap-up skipped” note lifted | REQ-4 |
| **W3** | Authorize API live-proven; feature-readiness freeze; basic automated PR checks | REQ-5, REQ-6, REQ-7 |

## Functional requirements

| ID | Requirement | PRD source | Condition / event | Observable result | Evidence layer |
|----|-------------|-----------|-------------------|-------------------|----------------|
| REQ-1 | **W0 readiness:** Spec wave start is accepted only when programme meta PR preconditions and dual-workspace bind (`workspace` + `meta_workspace`) are satisfied; intended skills pin (`v0.5.0-rc.2` family) is recorded as consumed; prove-out fixtures and reviewer checklist exist before W1. | PRD REQ-01 AC-1; PRD §5 W0; PRD A-01, A-02; CAP-01 | **When** PE calls spec wave start with bound meta PR URL/head and workspace paths | **Then** start succeeds only if meta accept-gate passes; run record stores initiative/wave identity and meta bind; rejection is fail-closed with no empty Draft Spec PR counted as success | unit (`test_meta_pr_intake`, `test_wave_start`) + inspection (W0 checklist) |
| REQ-2 | **Draft Spec PR tip deliverable:** After each orchestrated content step in the spec lane that produces durable artifacts, Gateflow publishes those artifacts to the run head and the Draft Spec PR tip contains them; a later content step (e.g. initiative-feasibility) adds **new** files onto the **same** PR tip; the PR is findable from the run record. | PRD REQ-01 AC-2–4; CAP-01; PRD §4 Path A | **When** spec lane walks orchestrated hops through at least `spec-draft` and automated `spec-pr-action`, with optional further content hops before the first honest manual stop | **Then** run timeline shows stage commits/publish events; run detail exposes `pr_number`; PR tip at stop includes committed outputs from automated steps (not an empty shell); ordering of publish hops is Gateflow-owned per pin | live verify (`verify_spec_lane`) + PR tip inspection + unit (forge publish / open_draft_pr) |
| REQ-3 | **Honest stop + human tip confirmation:** The spec Pass-1 walk stops at the first pin-declared human/manual boundary; it does not invent merge, gate approvals, or silent skip of human ownership; a human reviewer can confirm on the PR that tip contents match the steps run. | PRD REQ-01 AC-5–6; PRD REQ-02 AC-1; CAP-01, CAP-02; PRD Success Criteria “Honest stop” | **When** the walker reaches the first manual gate (happy path: `spec-implementation-plan`; blocked path: `spec-human-decision`; findings path: `technical-review-approval`) | **Then** run terminal state is `stopped` at that node; stop reason and handoff context are recorded; prove-out evidence includes PR URL and short reviewer confirmation that tip artifacts match steps run; empty Draft Spec PR does **not** satisfy success | live verify + human inspection record + timeline |
| REQ-4 | **Spec wrap-up live prove-out (required):** After REQ-3 tip confirmation, wrap-up is live-proven on that Draft Spec PR through wave sign-off; any prior programme note that spec wrap-up was skipped is lifted. | PRD REQ-02 AC-3; CAP-02; PRD §5 W2; PRD Locked decisions | **When** PE starts closeout/wrap-up bound to the confirmed Draft Spec PR and walks the pin closeout chain through `wave-signoff` | **Then** wrap-up completes with wave sign-off record; learning/ground artifacts publish per existing closeout path; programme records show spec wrap-up no longer deferred/skipped for this prove-out | live verify + wave sign-off record + as-built update |
| REQ-5 | **Authorize API live prove-out (required):** On a sensitive forge step marked `authorization: explicit`, the run stops without performing the side effect until programme authorize succeeds; approve performs the side effect (e.g. board tickets); deny/wrong state does not; success requires a recorded **live** stop→authorize→side-effect run (no paper waiver exit). | PRD REQ-03; CAP-03; PRD Error Handling; PRD Locked decisions | **When** walker reaches an explicit external-action (e.g. `board-tickets-action`) during a scripted prove-out | **Then** run stops with pending forge; `POST /api/v1/runs/{id}/forge/authorize` with approval performs mutate; deny/timeout/unavailable leaves side effect undone; live verify record documents the chain | live verify + inspection (`verify_board` or equivalent live record) + unit (`test_forge_action_service`) |
| REQ-6 | **Feature readiness freeze (gateflow portion):** Gateflow publishes a written feature-readiness record listing capabilities proven vs deferred, using **feature names** (not horizon nicknames), and updates as-built to match the freeze package. | PRD REQ-04; CAP-04; PRD §5 W3 | **When** W1–W3 prove-outs complete or defer | **Then** committed freeze artifact in this repo names proven items (coding-lane baseline, spec Draft Spec PR deliverable, authorize API path, spec wrap-up, basic PR checks) and deferred items (ops portal UI, second coding agents, Slack/Teams, programme-wide self-dogfood); as-built rows align with the record | inspection + as-built diff |
| REQ-7 | **Basic automated PR checks:** Replace placeholder CI with real basic checks that fail closed on orchestrated Gateflow PRs; human-developer PRs follow the existing human PR workflow — this INIT does not invent branch-protection settings. | PRD REQ-05; CAP-05 | **When** a pull request is opened or updated against `develop`/`main` | **Then** the `ci` job runs non-placeholder checks (examples: branch/PR hygiene, lint, unit); failing checks fail the workflow; orchestrated PR hygiene matches Gateflow repo conventions | CI run + inspection |

> **Id convention:** `REQ-*` canonical (`prayog-skills/references/id-conventions.md`).
> This slice assigns **REQ-1…REQ-7** tracing to PRD **REQ-01…REQ-05** / **CAP-01…CAP-05**.
> Legacy display alias `FR-{nn}` ≡ `REQ-{nn}` (same number).

**Inherited (reuse — do not rebuild):** spec/implement lane start APIs (ADR-010);
forge publish + automated `spec-pr-action` (ADR-009 / INIT-008); authorize API
(INIT-006); board primitives (INIT-002 W2); closeout start + learning ingest
(INIT-007); run timeline / metrics; programme token auth; pin `sdd-delivery/v2`
handoff envelope; `verify_spec_lane` harness.

**Explicit non-goals:** rebuilding orchestrator/walker/authorize/learning; ops portal;
skills pin RC cut; auto-merge; authorize-then-resume walker; treating IDE confirm
as Gateflow authorize; PE-waive Gate 1/2 ceremonies outside GitHub PR + labels +
Approve.

## Negative and failure paths

| REQ | Condition | Required behavior | Evidence |
|-----|-----------|-------------------|----------|
| REQ-1 | Missing/invalid meta PR or meta folder preconditions | Spec start rejected fail-closed; no empty Draft Spec PR counted as success | unit + live verify |
| REQ-2 | Commit/forge failure mid-walk; required publish with nothing to publish | Run records failure; tip without committed step outputs does **not** count as success | unit + live verify |
| REQ-2 | Empty Draft Spec PR opened (no step outputs on tip) | Does **not** satisfy REQ-2 / PRD Success Criteria | PR inspection |
| REQ-3 | Walker attempts merge/gate approval or skips manual stop | Must not occur; timeline shows honest stop | live verify + timeline |
| REQ-4 | Wrap-up started without prior tip confirmation | Prove-out invalid for initiative success until tip confirmed and wrap-up re-run | inspection |
| REQ-5 | Authorize deny, wrong state, timeout, or API unavailable | No forge side effect; prove-out recorded fail until live path works | unit + live verify |
| REQ-5 | Paper-only waiver for authorize exit | **Not** an exit path for this INIT | programme record |
| REQ-7 | Basic check failure on orchestrated PR | CI job fails; PR not silently green | CI logs |

## Out of scope for this repo

- **gateflow-ops** — ops portal / BFF UI (deferred to next INIT after freeze)
- **prayog-meta** — PRD, impact map, optional vision/planning note packaging (programme meta hygiene; not gateflow engineering delivery)
- **prayog-skills** — pin authoring / new RC (consume `v0.5.0-rc.2` family only)
- **launchpad** — product delivery (monitor remount hygiene only)
- Rebuilding coding-lane start, walker, wrap-up, authorize, learning, or metrics APIs
- Second coding agent live prove-out; Slack/Teams alerts
- Auto-merge; authorize-then-resume into next orchestrated skill hop

## Cross-service contracts

| Contract ID | Provider / owner | Consumer / owner | Entry point | Input shape | Output shape | Invariants | Errors | Compatibility / versioning | Contract-test location |
|-------------|------------------|------------------|-------------|-------------|--------------|------------|--------|----------------------------|------------------------|
| CTR-01 | prayog-skills / PE | gateflow | Pinned `sdd-delivery/v2` workflow + delivery contract + handoff; consume `v0.5.0-rc.2` family tip | pin YAML + handoff envelope | stage outcomes + forge requires | Missing authorization invalid; pin SSOT; content skills never mutate | Fail closed on invalid pin/handoff | Active pin tip | `test_forge_policy`, `test_handoff_workflow` |
| CTR-02 | gateflow / PE | GitHub (forge) | Draft Spec PR commit/open/update via ForgeClient | run head, paths, title/body | commit SHA, PR number/url | Never write `*-lgtm`; no merge action; tip matches published artifacts | I/O / incomplete requires ⇒ fail closed | ADR-003; INIT-008 automated `spec-pr-action` | `test_forge_client`, `verify_spec_lane` |
| CTR-03 | gateflow / PE | GitHub / board | Programme authorize → sensitive forge side effect | `POST …/forge/authorize`, plan/manifest slots when required | board tickets / PR mutate result | Explicit nodes STOP until authorize; automated nodes never skip requires | Deny/wrong state ⇒ no mutate | INIT-006 / INIT-008 | `test_forge_action_service`, live authorize record |

## Non-functional requirements

| Area | Requirement or N/A rationale | Acceptance / evidence |
|------|------------------------------|-----------------------|
| Security | Programme token on starts/authorize; production forge on GitHub App / ForgeClient (no `gh` as cloud success path); secrets never published; Forge never writes `*-lgtm` | unit + runbook inspection |
| Reliability | Fail closed on missing preconditions, incomplete forge requires, required empty publish, authorize unavailable | unit + live verify |
| Performance / capacity | N/A — prove-out initiative; no new cycle-time exit gates | inspection |
| Observability | Run timeline records stage commits, forge apply/stop, and terminal stop reason; metrics APIs remain available for prove-out evidence | live verify + `verify_all` |
| Privacy / data handling | PR bodies sourced from workspace paths; no credential materialization in artifacts | inspection |
| Migration / compatibility | Reuse existing APIs/pin; open runs stay on current pin family; INIT-007 spec-closeout PE-waive superseded for **this** INIT wrap-up requirement only | as-built note |
| Rollback / recovery | Pin/worker disable; explicit authorize remains for board; placeholder CI rollback documented if checks block emergency fixes | runbook inspection |
| Operations / support | Prove-out scripts and reviewer checklist documented; feature-readiness freeze readable by programme sponsor | freeze package + docs |

## Assumptions

| ID | Assumption | Evidence | Owner | Status | Invalidated when |
|----|------------|----------|-------|--------|------------------|
| A-1 | Skills pin `v0.5.0-rc.2` family is remounted/consumed for prove-outs | PRD A-01; harness pin record | PE | confirmed | Pin family changes |
| A-2 | Meta PR + meta folder fixtures available before W1 | PRD A-02; Gate 1 approved meta PR #23 | PE | confirmed | Meta PR closed without merge |
| A-3 | PE can call authorize API with programme service token | PRD A-03; existing lab path | PE | confirmed | Token path revoked |
| A-4 | Production forge uses GitHub App / ForgeClient | PRD A-04; as-built gh-free checklist | PE | confirmed | Forge transport changes |
| A-5 | Gate 1 follows `sdd-delivery/v2` meta PR path (`impact-map-lgtm` + Approve) | Meta PR #23 APPROVED @ head; label present | PE | confirmed | Approval/head mismatch |
| A-6 | Human Alembic for `runs.meta_pr_url` / `runs.meta_head_sha` applied before live spec start | as-built open gap | PE | open | Migration applied |
| A-7 | `verify_spec_lane` is the primary Pass-1 live script for W1 unless PE directs otherwise | `tests/verify/verify_spec_lane.py`; tests README | PE | confirmed | PE selects alternate script |

## Spec questions (ambiguities — need PM or domain confirmation before feasibility)

| ID | Lane | Question | Owner | Blocking | Required by | Default if deferred | Status | Resolution link |
|----|------|----------|-------|----------|-------------|---------------------|--------|-----------------|
| Q-1 | PE | Has human Alembic for `runs.meta_pr_url` / `runs.meta_head_sha` been applied in the live prove-out environment before W1? | PE | no (blocks **live** W1 only, not spec draft) | W1 live verify | Fail closed on spec start if columns missing — apply migration first | open | as-built §006 open gaps |
| Q-2 | PE | Authorize live prove-out: dedicated scripted verify vs manual live record acceptable? | PE | no | W3 live verify | Manual live record with run id + board/issue URLs satisfies PRD REQ-03 | open | PRD “live verify record” |
| Q-3 | PE | Exact CI check set beyond “non-placeholder” (lint only vs lint+unit vs branch naming gate)? | PE | no | W3 / plan | **`make check` + `make test`** in `ci` job; branch naming enforced via existing PR hygiene conventions | open | PRD REQ-05 examples |
| Q-4 | PM | Vision/planning note in freeze package: gateflow links to meta doc path only, or duplicate summary row in gateflow freeze artifact? | PM | no | W3 freeze | Gateflow freeze lists features; meta vision note updated in same programme package (lean same package) | open | PRD REQ-04 AC-4 |

## Draft check summary (D1–D12)

| Check | Status | Evidence / findings |
|-------|--------|---------------------|
| D1 Approved handoff current | **PASS** | Meta PR #23 head `6660aa4…` = tech-lead APPROVED review commit; label `impact-map-lgtm`; impact-map revision 1; PRD digest matches map frontmatter; gateflow affected with scope digest `d0a2b626…`; not deferred/blocked |
| D2 Complete PRD traceability | **PASS** | CAP-01…05 → REQ-1…7; every REQ cites PRD REQ-01…05 / § / AC |
| D3 Repo-bounded scope | **PASS** | Matches impact-map scope digest; meta/ops/skills/launchpad excluded |
| D4 Observable acceptance | **PASS** | Every REQ has condition/event, observable result, evidence layer; implementation-neutral |
| D5 Negative/failure paths | **PASS** | Negative table covers start reject, empty PR, forge fail, authorize deny, CI fail |
| D6 Assumptions/questions | **PASS** | A-1…A-7 with status; Q-1…Q-4 non-blocking with defaults |
| D7 Cross-repository contracts | **PASS** | CTR-01…03 semantic boundaries per impact map §6 |
| D8 NFR applicability | **PASS** | Eight NFR rows populated or N/A with reason |
| D9 As-built alignment | **PASS** | Baseline vs prove-out target distinguished; reuse vs new checks explicit |
| D10 Dependency order | **PASS** | W0→W1→W2→W3 matches impact map §7; prayog-skills pin consume first |
| D11 Zero unresolved blockers | **PASS** | No material PM/PE/domain blocker; Q-1…Q-4 non-blocking with defaults |
| D12 Output completeness | **PASS** | Header, REQs, NFR, contracts, questions, checks, PR readiness, handoff+forge |

**Draft verdict:** **PASS**

**Selected workflow outcome:** `pass`
**Outcome reason:** D1–D12 PASS; Gate 1 approved handoff current; zero unresolved material questions; PR READY for Forge `open_draft_pr`.

## PR readiness handoff

| Item | Value |
|------|-------|
| Workflow outcome | `pass` — D-checks PASS; Gate 1 approved |
| Verdict | **PR READY** |
| Existing spec PR | none |
| Proposed branch | `chore/INIT-GATEFLOW-009-spec-gateflow` |
| Proposed base | `develop` |
| Proposed title | `[INIT-GATEFLOW-009] Spec — both-lane factory prove-out (gateflow)` |
| PR type | **Draft** |
| Local artifacts to publish | `docs/specification/product/INIT-GATEFLOW-009-gateflow.md` |
| Forge readiness | `handoff.forge` filled below; recommend `/commit-workspace` then automated `spec-pr-action` — **not** inside this skill |
| Reviewer | @drivestream-lab/prayog-pe-team |
| Initial Gate 2 label | `spec-pending` |
| Additional invalidation label | none |
| Blocking items | none for publish |

**No GitHub side effects from `/spec-draft`.**

### Proposed Draft PR body

```markdown
## Initiative

INIT-GATEFLOW-009 — both-lane delivery factory prove-out (gateflow)

## Meta handoff

- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/23
- Approved meta head: `6660aa4fefbcd80324cb970aa5bab642d3e5e0a1`
- Impact-map revision: 1
- PRD digest: `sha256:76ab22b3c197b9d0cb6b08e6cea379c4e07b3a471b8a88203fddca6014c1c012`
- Repo scope digest: `sha256:d0a2b62632113db0fa64cb7d7e63dc393fa5a8217092dda242a99b3392978e9b`

## Spec path

`docs/specification/product/INIT-GATEFLOW-009-gateflow.md`

## Summary

- REQ-1…REQ-7 — prove-out reuse: Draft Spec PR tip deliverable, honest stop, required spec wrap-up, live authorize API, feature-readiness freeze, basic CI
- Open non-blocking: Q-1…Q-4 (defaults recorded)

## Gate 2 — spec package readiness

Initial label: `spec-pending`

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
- [ ] No blocking question remains
- [ ] Developer confirmed draft is ready for feasibility

## References

- PRD: `prayog-meta/prd/INIT-GATEFLOW-009.md`
- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/23
- Impact map: `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-009.md`
- As-built: `docs/specification/as-built/implementation-status.md`
- Predecessor pin consume: `docs/specification/product/INIT-GATEFLOW-008-gateflow.md`
- Live verify: `tests/verify/verify_spec_lane.py`

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-draft
  outcome: pass
  artifact:
    path: docs/specification/product/INIT-GATEFLOW-009-gateflow.md
    digest: sha256:e6a4e2bf42b4202b0609e3a97d5f938bab48c304a658f4d19a58fd3de4ef85e9
  blockers: []
  signals:
    pr_ready: true
    initiative: INIT-GATEFLOW-009
    map_revision: 1
    meta_pr_head: "6660aa4fefbcd80324cb970aa5bab642d3e5e0a1"
    prd_digest: sha256:76ab22b3c197b9d0cb6b08e6cea379c4e07b3a471b8a88203fddca6014c1c012
    scope_digest: sha256:d0a2b62632113db0fa64cb7d7e63dc393fa5a8217092dda242a99b3392978e9b
    d_checks: pass
    nonblocking_questions: "Q-1,Q-2,Q-3,Q-4"
  next_candidates:
    - spec-pr-action
  human_checkpoint: false
  external_action: true
  forge:
    action: open_draft_pr
    draft: true
    apply_labels:
      - spec-pending
    title: "[INIT-GATEFLOW-009] Spec — both-lane factory prove-out (gateflow)"
    body_path: docs/specification/product/INIT-GATEFLOW-009-gateflow.md
```

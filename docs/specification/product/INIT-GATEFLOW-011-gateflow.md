# INIT-GATEFLOW-011 — spec slice for gateflow

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-011 |
| PRD | `prayog-meta/prd/INIT-GATEFLOW-011.md` |
| PRD digest (H1) | `sha256:eca06cbe986d619db58ae3ca84f4ec0987c19aa19b8f1485693280c6a655e4dd` |
| Meta PR | https://github.com/drivestream-lab/prayog-meta/pull/30 |
| Meta PR approved head (G1) | `f3da8148f3e861fad4720a3491f11f1fdc0145aa` |
| Impact map | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-011.md` |
| Impact-map revision (H3) | `1` |
| Repo scope digest (H2) | `sha256:afdc7bd51bcd0c12f614feebf338bdc78766396bb84777121a2565c0ecc7966d` |
| Tech-lead approval | [@0xbeefdead APPROVED](https://github.com/drivestream-lab/prayog-meta/pull/30#pullrequestreview-4876719066) 2026-08-06T16:28:58Z on `f3da8148f3e861fad4720a3491f11f1fdc0145aa` — attestation: map_revision 1, prd_digest match, artifact `prd/reports/Impact-Map-INIT-GATEFLOW-011.md` |
| Architecture constraints (existing) | Pin SSOT [`prayog-skills/workflow.yaml`](../../../prayog-skills/workflow.yaml), [`delivery-contract.yaml`](../../../prayog-skills/delivery-contract.yaml) @ `v0.5.0-rc.2`; [`adr-009`](../adr/adr-009-pin-forge-publish-mutate-authority.md) / [`adr-010`](../adr/adr-010-lane-intake-and-dual-workspace-authority.md) (**Accepted** — mutate/intake authority unchanged; this INIT adds **no** write surface) |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-06 |
| Status | Draft — dev review required before Forge publish |

> **H4 citations:** The H1–H3 (and G1) rows above are the durable authority
> carrier for mid-lane freshness. Feas / TDD / plan digests are walk-time only
> and may be purged at initiative closure.

## Overview

Gateflow cannot yet answer **"what's going on right now?"** or **"did I actually
finish what I think I finished?"**. This INIT delivers a **read-only Day-1
visibility + GitHub reconcile** layer on top of INIT-GATEFLOW-010's eng-lane
executor: one reusable **checkpoint status-check** (CAP-01/02) that evaluates
any in-scope checkpoint PR against the pinned contract's own
`github.labels` + `review_roles` vocabulary, plus **initiative / wave / phase
read-outs** (CAP-03–10) covering every Day-1 phase in PRD scope.

**Scope boundary (this repo only):** all new product surface is **GET-only**
under programme-token auth (PRD Appendix A / G1). Zero mutating routes; zero
`apply_labels` / review create-update / merge / `update_board_status` from any
new path (REQ-28). No screens (`gateflow-ops` deferred). No `prayog-meta`
process change; no pin redesign (`prayog-skills` consume-only).

**Ownership:** this spec defines observable behavior, acceptance, field meaning,
invariants, errors, and compatibility. Module/ADR choices (e.g. how
`ForgeClient` is extended, check-record persistence shape, whether CAP-01
generalizes `MetaPrIntakeService`) are **deferred to feasibility / technical
review** — not decided here.

**As-built baseline (2026-08-06):** INIT-GATEFLOW-010 W0–W3 **human_approved**;
W4 tip pending human merge. Existing reconcile precedent:
`MetaPrIntakeService.accept()` + `ForgeClient.get_pull_request` (labels + head
SHA only — **no** reviews / check-runs / merged state today, per PRD A6/A7).
Run list/detail, board list, wave starts, and metrics already exist; **no**
`/api/v1/checkpoints/*` or `/api/v1/initiatives/*` read-outs yet.

**Delivery waves (product-normative; PRD §5):**

| Wave | Intent | Exit REQs |
|------|--------|-----------|
| **W0** | Checkpoint status-check foundation (live GitHub evidence; ForgeClient read extension; no persistence) | REQ-01, REQ-02, REQ-04, REQ-05 |
| **W1** | Check persistence + general checkpoint read-out (`checked_sha`/`checked_at` + stale) | REQ-03, REQ-06, REQ-07, REQ-08 |
| **W2** | Initiative list/detail from Gateflow-owned data | REQ-09 (partial), REQ-10 |
| **W3** | Initiative read-out + prayog-meta read-only bridge | REQ-09 (complete), REQ-11 |
| **W4** | Wave map read-out | REQ-14, REQ-15 |
| **W5** | Spec lane read-out | REQ-12, REQ-13 |
| **W6** | Wave implementation progress read-out | REQ-16, REQ-17 |
| **W7** | Closeout read-out + drift safeguard (depends on W1) | REQ-18, REQ-19, REQ-20 |
| **W8** | Merge confirm + next-wave nudge + completion eligibility | REQ-21, REQ-22, REQ-23, REQ-24 |
| **W9** | Closure preview + CAP-01 reuse for closure sign-off | REQ-25, REQ-26, REQ-27 |

REQ-28 is a **global** guard across all waves.

## Functional requirements

| ID | Requirement | PRD source | Condition / event | Observable result | Evidence layer | Wave |
|----|-------------|-----------|-------------------|-------------------|----------------|------|
| REQ-01 | Checkpoint status-check accepts a pin checkpoint node id ∈ {`coding-readiness`, `wave-acceptance`, `wave-signoff`, `initiative-closure-signoff-app`, `initiative-closure-signoff-meta`, `prd-impact-acceptance`} plus PR-resolving identifiers (initiative/wave or explicit org/repo/PR); call is read-only | PRD REQ-01; CAP-01; US-1 | Caller invokes status-check | Response returned; 0 GitHub writes | unit + live verify | W0 |
| REQ-02 | Evidence set is resolved from pinned `delivery-contract.yaml` (`github.labels` present/blocking + `review_roles` review state + required CI check-run conclusions), evaluated **live** at current PR head — never hardcoded per phase | PRD REQ-02; CAP-01; A1; G2 | Live status-check | Verdict matches pin vocabulary for that checkpoint; evidence class per PRD mapping table (label+review vs review/merge-only) | unit | W0 |
| REQ-03 | Every status-check response includes `checked_sha` (PR head at call time) and `checked_at`; if satisfying label/review predates a later commit on the same PR → verdict `NOT SATISFIED` with reason `stale — new commits since approval` (never silent `pass`) | PRD REQ-03; CAP-01; D2; G3 | New commit after approval evidence | Stale never reported as pass; version fields always present | unit + live verify | W1 |
| REQ-04 | Non-pass responses list each missing/unsatisfied item by name (label, review, check-run) — not a single boolean | PRD REQ-04; CAP-01; D3 | Any failing check | Itemized miss list present | unit | W0 |
| REQ-05 | Status-check path never calls `apply_labels`, review create/update, merge, or `update_board_status` | PRD REQ-05; CAP-01; D1 | Any status-check call | 0 write calls from path | code guard + live verify | W0 |
| REQ-06 | Every CAP-01 call persists a check record (checkpoint id, PR reference, `checked_sha`, `checked_at`, verdict, missing items) into Gateflow's existing run/timeline store, correlated to initiative/wave when resolvable | PRD REQ-06; CAP-02; G4 | Any CAP-01 call | Record retrievable via history read-out | unit | W1 |
| REQ-07 | History read-out returns prior persisted check records explicitly labeled **historical**; historical records must never be substituted for a live verdict when the caller needs a current decision | PRD REQ-07; CAP-02; G5 | History call | Response marks records historical and distinct from live status-check | unit | W1 |
| REQ-08 | General checkpoint read-out composes live CAP-01 with initiative/wave/run identifiers Gateflow already resolves (caller supplies initiative+wave, not raw org/repo/PR) | PRD REQ-08; CAP-02; Phases 5/9/11/13 | Phase-scoped checkpoint call | Composed response; unresolved pairing → **404** with reason `no run found for this wave` (distinct from malformed id) | unit + live verify | W1 |
| REQ-09 | Initiative list/detail returns id, name/description, PRD approval state (CAP-01 evidence against `prd-impact-acceptance`), affected repos, current stage (plain language), and link to any in-flight run — fields present or explicitly `unavailable` | PRD REQ-09; CAP-03; US-3 | List/detail call | All fields present or marked unavailable | unit + live verify | W2 (Gateflow-owned) / W3 (PRD approval complete) |
| REQ-10 | Initiative read-out is composed only from Gateflow-owned data (runs, board tickets) plus at most one read-only meta PR/label read — no new source of truth | PRD REQ-10; CAP-03; D4 | Any initiative read-out | No parallel inventable SoT | inspection | W2 |
| REQ-11 | When prayog-meta is unreachable, Gateflow-owned fields still return **200**; meta-derived field marked `unavailable` (partial success, not full failure) | PRD REQ-11; CAP-03 | Meta unreachable | Partial success envelope | unit + live verify | W3 |
| REQ-12 | Spec-lane read-out returns Draft Spec PR link (from `spec-pr-action`), plain-language generated artifacts, findings/open questions from feasibility/technical-review stages, and exact next step from pin | PRD REQ-12; CAP-04; US-4 | Spec walk in progress or done | Fields resolved from pin + run state | unit + live verify | W5 |
| REQ-13 | If spec walk has not reached `spec-pr-action`, read-out states that plainly — no broken/missing link presented as a URL | PRD REQ-13; CAP-04 | No Draft Spec PR yet | Explicit not-ready message | unit | W5 |
| REQ-14 | Wave map returns per-wave status ∈ {`done`, `ready-to-start`, `blocked`, `active`}; when `blocked`, names why (e.g. predecessor not Done) | PRD REQ-14; CAP-05; US-5 | Initiative with waves | Status + block reason when applicable | unit + live verify | W4 |
| REQ-15 | Wave status derived only from existing board ticket + run state — no new wave-state store | PRD REQ-15; CAP-05; D4 | Any wave-map call | Derivation from existing data only | inspection | W4 |
| REQ-16 | In-progress wave read-out returns task-by-task progress from run timeline; returns Draft PR link when `wave-pr-action` succeeds | PRD REQ-16; CAP-06; US-6 | Wave in progress | Per-task status (not single spinner) + PR link when available | unit + live verify | W6 |
| REQ-17 | On task failure or run stop (`needs-input`), read-out names which task and why | PRD REQ-17; CAP-06 | Task fails / needs-input | Named task + reason | unit | W6 |
| REQ-18 | Closeout read-out lists what closeout added (lessons captured, learning-store records) after `learning-extract` / `ground-spec` complete | PRD REQ-18; CAP-07; US-7 | Closeout complete | Itemized additions | unit + live verify | W7 |
| REQ-19 | Drift safeguard compares wave-acceptance-time head SHA (persisted REQ-06 record) vs closeout-time PR head; if different → flag "product code changed after acceptance"; if no baseline recorded → `unknown — no baseline recorded` (never silent skip / false no-drift) | PRD REQ-19; CAP-07; A2 | SHA differs or no baseline | Explicit drift or no-baseline flag | unit + live verify | W7 |
| REQ-20 | Drift safeguard is **advisory only** — does not block or fail closeout mechanics (`learning-extract` → `ground-spec` → `wave-done-action` → `wave-signoff` unchanged) | PRD REQ-20; CAP-07; D1; D6 | Any closeout | Closeout proceeds regardless of flag | unit | W7 |
| REQ-21 | Merge confirm reuses CAP-01 evidence rules against `wave-signoff` to report merged state + merge commit SHA, or itemized missing items (e.g. not yet merged) | PRD REQ-21; CAP-08; US-8 | Merge-confirm call | Merged/not-merged + evidence | unit + live verify | W8 |
| REQ-22 | After confirmed merge, if next wave is now unblocked (predecessor Done), response surfaces "wave W`n+1` is now unblocked" | PRD REQ-22; CAP-08 | Predecessor now Done | Nudge present | unit + live verify | W8 |
| REQ-23 | Completion eligibility reports "ready to close" **iff** every `wave_ticket_ids` entry is board Done (same semantics as INIT-GATEFLOW-010 REQ-13); else "waiting on wave N" naming blockers; empty/unresolvable `wave_ticket_ids` → distinct "no waves found" — never "ready to close" | PRD REQ-23; CAP-09; US-9 | Any initiative | Correct rollup state | unit + live verify | W8 |
| REQ-24 | Completion eligibility is a pure rollup of CAP-05 wave-map data — no second GitHub/board query with different logic | PRD REQ-24; CAP-09 | Any completion call | Single derivation reused | inspection | W8 |
| REQ-25 | Closure preview (pre-purge) lists what will be deleted vs kept, sourced from the purge skill's own manifest/plan — this INIT does not independently invent the delete list | PRD REQ-25; CAP-10; US-10 | Before purge runs | List matches purge plan; "not yet run" when skill not executed | unit + live verify | W9 |
| REQ-26 | Closure preview (post-purge) lists what was actually deleted/kept for before/after comparison | PRD REQ-26; CAP-10 | After purge runs | Actual deleted/kept list | unit + live verify | W9 |
| REQ-27 | Once closure PR exists, reuses CAP-01 to confirm `initiative-closure-signoff-app` / `initiative-closure-signoff-meta` on current head before/after merge — no separate approval-checking logic | PRD REQ-27; CAP-10 | Closure PR exists | Same CAP-01 evidence rules | unit + live verify | W9 |
| REQ-28 | No capability CAP-01–CAP-10 introduces POST/PUT/PATCH/DELETE product routes or calls `apply_labels`, review create/update, merge, or `update_board_status` | PRD REQ-28; G1; D1 | Any Appendix A route | Route inventory = GET-only; 0 write calls from new paths | code guard + live verify | all |

### Checkpoint evidence mapping (product-normative)

Copied from PRD for engineering acceptance (SSOT remains pinned
`delivery-contract.yaml` @ tip):

| Checkpoint (pin node id) | Required label | Blocking labels | Evidence class |
|--------------------------|----------------|-----------------|----------------|
| `prd-impact-acceptance` | `impact-map-lgtm` | `impact-map-blocked`, `impact-map-revised`, `impact-map-stale` | Label + review (`engineering-gate` / meta-pm) |
| `coding-readiness` | `spec-lgtm` | `spec-blocked`, `spec-revised`, `spec-stale` | Label + review (`engineering-gate` / app) |
| `wave-acceptance` | `wave-accepted` | *(none declared)* | Label + review (`engineering-gate` / app) |
| `wave-signoff` | *(none)* | — | Review/merge state only |
| `initiative-closure-signoff-app` | *(none)* | — | Review/merge state only |
| `initiative-closure-signoff-meta` | *(none)* | — | Review/merge state only |

### Target API surface (already named in PRD Appendix A / G7)

| Route | Capability |
|-------|------------|
| `GET /api/v1/checkpoints/status` | CAP-01 |
| `GET /api/v1/checkpoints/history` | CAP-02 |
| `GET /api/v1/initiatives` | CAP-03 |
| `GET /api/v1/initiatives/{initiative_id}` | CAP-03 |
| `GET /api/v1/initiatives/{initiative_id}/spec` | CAP-04 |
| `GET /api/v1/initiatives/{initiative_id}/waves` | CAP-05 |
| `GET /api/v1/initiatives/{initiative_id}/waves/{wave_id}/implementation` | CAP-06 |
| `GET /api/v1/initiatives/{initiative_id}/waves/{wave_id}/closeout` | CAP-07 |
| `GET /api/v1/initiatives/{initiative_id}/waves/{wave_id}/merge` | CAP-08 |
| `GET /api/v1/initiatives/{initiative_id}/completion` | CAP-09 |
| `GET /api/v1/initiatives/{initiative_id}/closure` | CAP-10 |

Exact response / problem+json field names → **Q-1** (OQ-01); route shapes and
HTTP semantics above are normative.

## Negative and failure paths

| REQ | Condition | Required behavior | Why it matters | Evidence |
|-----|-----------|-------------------|----------------|----------|
| REQ-01 / REQ-08 | Unresolvable checkpoint id or PR reference | **404**; minimal GitHub calls beyond resolution attempt | Prevents fake pass on bad identifiers | unit + verify |
| REQ-08 | Initiative+wave supplied but no run/PR exists yet | **404** with reason `no run found for this wave` | Distinct from malformed id — PE must not treat "not started" as "malformed" | unit + verify |
| REQ-03 | Satisfying evidence dated before a later commit | `NOT SATISFIED`, reason `stale — new commits since approval`; persist check record (REQ-06) | Stops proceed-on-stale-approval regressions | unit + verify |
| REQ-28 / G1 | Request includes mutating parameter / non-GET method on new surface | **400** (or method not allowed); 0 GitHub write attempted | Structural D1 enforcement | unit + code guard |
| REQ-11 | prayog-meta unreachable during initiative read-out | **200** with meta field `unavailable`; Gateflow-owned fields still returned | Avoids full outage of visibility when meta is down | unit + verify |
| REQ-25 | Closure preview before purge skill has run | **200** with "not yet run" plan preview from manifest; no delete | Transparency without inventing delete actions | unit + verify |
| REQ-01 / REQ-02 | GitHub API unreachable or rate-limited during live status-check | Fail closed: "could not verify — GitHub unreachable"; **never** present cached/stale verdict as current | Ties to D2 — silent cache would recreate the stale-pass bug | unit + verify |
| REQ-19 | No persisted `wave-acceptance` check record for wave | Explicit `unknown — no baseline recorded` (not silent skip / false clean) | Drift silence before merge is the production failure mode | unit + verify |
| REQ-23 | Empty or unresolvable `wave_ticket_ids` | Distinct "no waves found" — never "ready to close" | Prevents false closure readiness (matches 010 Done-gate intent) | unit + verify |

## Out of scope for this repo

- **gateflow-ops** screens / UI (deferred consumer of Appendix A)
- **prayog-skills** pin / workflow / contract redesign (consume-only @ `v0.5.0-rc.2`)
- **prayog-meta** process / PRD workflow changes (meta is evidence source only via GitHub REST)
- Phase 3 (spec engineering review), Phase 4 (spec approval/merge), Phase 8 (code/feature verification) — human/GitHub today
- Phase 14 meta closure
- Automatic label / approval / merge actions (hard boundary, unchanged from INIT-010)
- Webhook-driven auto-progression ("developer asks Gateflow to check" for Day-1)
- Any POST/PUT/PATCH/DELETE product routes introduced by this INIT

## Cross-service contracts

| Contract ID | Provider / owner | Consumer / owner | Entry point | Input shape | Output shape | Invariants | Errors | Compatibility / versioning | Contract-test location |
|-------------|------------------|------------------|-------------|-------------|--------------|------------|--------|----------------------------|------------------------|
| CTR-01 | prayog-skills / prayog-pe-team | gateflow | Resolve checkpoint evidence vocabulary from pinned `delivery-contract.yaml` (`github.labels`, `review_roles`) at remounted tip | Checkpoint node id + pin tip | Required/blocking labels + review_roles entry for that checkpoint | Labels/roles never hardcoded per phase; tip family `v0.5.0-rc.2` | Missing pin / unknown checkpoint id → fail closed | Consume pin tip only; redesign is separate INIT | unit (fixture pin) + inspection |
| CTR-02 | GitHub REST (PR evidence) / prayog-pe-team | gateflow | Read-only PR evidence for CAP-01: labels, reviews, check-runs, head SHA, merge state | org/repo/PR (or resolved from run) | Live evidence at call time | Read-only; no write scopes required for new paths | Unreachable/rate-limit → fail closed (no cached current verdict) | New read methods required vs today's `get_pull_request` (PRD A6) — design in TDD | unit (fixture PR) + verify |
| CTR-03 | GitHub REST against `prayog-meta` repo / prayog-pe-team | gateflow | Read-only meta PR/label state for initiative PRD-approval line (CAP-03) | Meta PR reference for initiative | Labels + head/review evidence for `prd-impact-acceptance` | Same REST edge as CTR-02, different target repo; no prayog-meta code change | Meta unreachable → field `unavailable`, not full failure (REQ-11) | Credential scope → Q-2 | unit + verify (W3) |

## Non-functional requirements

| Area | Requirement or N/A rationale | Acceptance / evidence |
|------|------------------------------|-----------------------|
| Security | Programme service token on all new routes (existing pattern). New paths require **read-only** GitHub capability only. Never apply `*-lgtm` / `wave-accepted` from this INIT. No secrets in check records or verify artifacts. | Route auth tests + code guard (REQ-05/28) |
| Reliability | Live checks fail closed on GitHub unavailability; initiative read-outs degrade partially when meta is down (REQ-11). No silent cache-as-current. | unit + verify |
| Performance / capacity | N/A as product SLO this INIT — read-outs must complete under normal GitHub/API latency; no new capacity claim beyond existing ForgeClient patterns | inspection / verify smoke |
| Observability | Persist check records (REQ-06); history labeled historical (REQ-07); structured logs for check verdict + checkpoint id + checked_sha (no secrets) | unit + inspection |
| Privacy / data handling | No PII beyond existing GitHub/PR identifiers already in Gateflow run store; check records store SHAs/verdicts/missing item names only | inspection |
| Migration / compatibility | Additive GET surface; no change to existing mutate/start routes. Check-record persistence must not break existing run/timeline consumers | unit regression on run APIs |
| Rollback / recovery | Feature is read-only — rollback = disable new routes / ignore new tables; no board/GitHub write to reverse | inspection |
| Operations / support | Document verify commands in `tests/README.md` per wave; PE can reconcile any checkpoint without asking a colleague | live verify + docs |

## Assumptions

| ID | Assumption | Evidence | Owner | Status | Invalidated when |
|----|------------|----------|-------|--------|------------------|
| A-1 | Pin `delivery-contract.yaml` `github.labels` + `review_roles` remain SSOT for checkpoint evidence | PRD A1; tip contract file | PE | confirmed | Pin tip changes vocabulary shape (separate INIT) |
| A-2 | "Current version" = PR head SHA at call time; evidence compared to SHA it applied against | PRD A2 / D2 / G3 | PE | confirmed | Product redefines version identity |
| A-3 | Existing run/timeline store can host check records without a parallel product SoT | PRD A3; as-built RunStore | PE | confirmed | Persistence design requires separate product store (ADR) |
| A-4 | Meta bridge is same GitHub REST edge with different owner/repo (no new transport) | PRD A4; `ForgeClient.get_pull_request` | PE | confirmed | Meta requires separate auth product (see Q-2) |
| A-5 | Outline §0 remount complete; checkpoint ids/`wave-accepted` vocabulary match tip | PRD A5; as-built remount hygiene 2026-08-06; harness pin `v0.5.0-rc.2` | PE | confirmed | Tip family changes node ids |
| A-6 | CAP-01 requires new GitHub read surface beyond today's `get_pull_request` (reviews, check-runs, merge state) | PRD A6; code inspection | PE | confirmed | Upstream client already provides them |
| A-7 | `MetaPrIntakeService` is shape precedent only — does not check `impact-map-lgtm`/reviews today | PRD A7 | PE | confirmed | Intake already satisfies CAP-01 (it does not) |
| A-8 | INIT-GATEFLOW-010 eng-lane executor remains the mutate path; this INIT observes only | Impact map / predecessor | PE | confirmed | Product asks this INIT to mutate |

## Spec questions (ambiguities — need PM or domain confirmation before feasibility)

| ID | Lane | Question | Owner | Blocking | Required by | Default if deferred | Status | Resolution link |
|----|------|----------|-------|----------|-------------|---------------------|--------|-----------------|
| Q-1 | PE | Exact problem+json / OpenAPI response field names for Appendix A routes (PRD OQ-01 / IM-01) | PE | no | OpenAPI / implement waves | Route paths + 400/404/200 semantics remain normative; field names deferred to OpenAPI pass | open | pending |
| Q-2 | PE | Does the prayog-meta read (CTR-03 / REQ-09/11) reuse the same GitHub App/`ForgeClient` credentials as gateflow↔app repos, or a separate read-only scope? (PRD OQ-02 / IM-02) | PE | no | W3 | Same credentials; revisit only if `prayog-meta` is outside the App installation | open | pending |
| Q-3 | PE | Confirm W0 explicitly includes `ForgeClient` read extension (`list_reviews`, `list_check_runs`, merged/mergeable on PR document), not pure reuse of `get_pull_request` (IM-03) | PE | no | W0 kickoff | **Include extension in W0** (PRD Risks + impact map default) | open | pending — default accepted for draft |
| Q-4 | PE / architecture | Should CAP-01 generalize `MetaPrIntakeService` shape vs sit beside it? Module names / ADR need? | PE | no | feasibility / technical review | Record for TDD — **no product decision in this draft** | open | pending |

## Draft check summary (D1–D12)

| Check | Status | Evidence / findings |
|-------|--------|---------------------|
| D1 Approved handoff current | PASS | Meta PR #30 head `f3da8148…` = tech-lead APPROVED review `commit_id`; label `impact-map-lgtm`; H1 digest match; H3 rev 1; H2 gateflow affected `sha256:afdc7bd5…`; not deferred/blocked |
| D2 Complete PRD traceability | PASS | CAP-01…10 + REQ-28 map to REQ-01…28; every REQ cites PRD CAP/REQ/US |
| D3 Repo-bounded scope | PASS | Matches H2 payload; deferred gateflow-ops + prayog-skills consume-only; meta not eng delivery |
| D4 Observable acceptance | PASS | Each REQ has condition/event, observable result, evidence layer; architecture deferred to Q-4 |
| D5 Negative/failure paths | PASS | Covers PRD error table + stale/drift/empty-waves; why-it-matters filled |
| D6 Assumptions/questions | PASS | A-1…A-8; Q-1…Q-4 non-blocking with defaults |
| D7 Cross-repository contracts | PASS | CTR-01…03 semantic; no outbound write contract |
| D8 NFR applicability | PASS | All areas specified or N/A with reason |
| D9 As-built alignment | PASS | Existing MetaPrIntake + get_pull_request (partial); no checkpoints/initiatives GET surface; 010 mutate baseline unchanged |
| D10 Dependency order | PASS | Matches impact map §7: pin → W0…W9 → deferred ops |
| D11 Zero unresolved blockers | PASS | No blocking PM/PE/domain question; defaults recorded for Q-1…Q-3 |
| D12 Output completeness | PASS | Header H4, tables, checks, outcome, PR readiness, dev review present |

**Draft verdict:** PASS

**Selected workflow outcome:** `pass`
**Outcome reason:** D1–D12 PASS; Gate 1 approved on current meta head; zero material unresolved questions after clarification loop (Q-1…Q-4 non-blocking with defaults).

Do not advance to `/initiative-feasibility` unless the workflow outcome is
`pass`, the draft verdict is PASS, and the developer review below is complete.

## PR readiness handoff

| Item | Value |
|------|-------|
| Workflow outcome | `pass` — Gate 1 current; full traceability; no material blockers |
| Verdict | PR READY |
| Existing spec PR | none |
| Proposed branch | `chore/INIT-GATEFLOW-011-spec-gateflow` |
| Proposed base | `develop` |
| Proposed title | `[INIT-GATEFLOW-011] Spec — Day-1 visibility and GitHub reconcile (gateflow)` |
| PR type | **Draft** (entire spec lifecycle) |
| Local artifacts to publish | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md`, `docs/specification/README.md` |
| Forge readiness | fill `handoff.forge` for `open_draft_pr`; recommend `/commit-workspace` then orchestrator `spec-pr-action` / `/open-draft-pr` — do not commit/push/open PR inside this skill |
| Reviewer | @drivestream-lab/prayog-pe-team |
| Initial Gate 2 label | `spec-pending` |
| Additional invalidation label | none |
| Blocking items | none |

**No GitHub side effects have occurred.** Persist the draft locally, present
this section in chat, and ask whether to authorize Forge publish
(`/commit-workspace` / `/open-draft-pr` or Gateflow ForgeClient). Continue only
after explicit authorization.

### Proposed Draft PR body

```markdown
## Initiative

INIT-GATEFLOW-011 — Day-1 visibility and GitHub reconcile (gateflow only)

## Meta handoff

- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/30
- Approved meta head: `f3da8148f3e861fad4720a3491f11f1fdc0145aa`
- Impact-map revision: 1
- PRD digest: `sha256:eca06cbe986d619db58ae3ca84f4ec0987c19aa19b8f1485693280c6a655e4dd`
- Repo scope digest: `sha256:afdc7bd51bcd0c12f614feebf338bdc78766396bb84777121a2565c0ecc7966d`

## Spec path

`docs/specification/product/INIT-GATEFLOW-011-gateflow.md`

## Summary

- Full INIT scope: reusable checkpoint status-check (CAP-01/02) + visibility read-outs (CAP-03…10); REQ-01…28; all GET-only
- Waves W0–W9 per PRD §5 (foundation → closure preview)
- Open engineering questions: Q-1…Q-4 (non-blocking; defaults documented)

## Gate 2 — spec package readiness

Initial label: `spec-pending`

- [ ] Spec slice published on this PR head (via Forge `/commit-workspace` / `/open-draft-pr`)
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

## After Draft PR creation

PE controls Gate 2 labels on the spec PR. Never infer approval from labels
alone — `spec-lgtm` requires matching artifacts on the exact PR head.

Provision labels before PR creation when missing:

```bash
launchpad apply-gates --repo gateflow --apply
```

| PE action | Remove | Add |
|-----------|--------|-----|
| Pending/new revision | `spec-lgtm`, `spec-blocked` | `spec-pending` |
| Request changes/hold | `spec-pending`, `spec-lgtm` | `spec-blocked` |
| Approve full package | `spec-pending`, `spec-blocked`, `spec-revised`, `spec-stale` | `spec-lgtm` |

## References

- PRD: `prayog-meta/prd/INIT-GATEFLOW-011.md` @ meta PR #30
- Impact map: `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-011.md` revision 1
- Predecessor: [`INIT-GATEFLOW-010-gateflow.md`](INIT-GATEFLOW-010-gateflow.md) (eng-lane executor parity)
- As-built: `docs/specification/as-built/implementation-status.md`
- Pin: `prayog-skills` @ `v0.5.0-rc.2` (`delivery-contract.yaml`, `workflow.yaml`)

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-draft
  outcome: pass
  artifact:
    path: docs/specification/product/INIT-GATEFLOW-011-gateflow.md
    digest: sha256:24992c66382dfa1c34a458105a625887fbd84c813428094e4fcd08f0fa938218
  blockers: []
  signals:
    pr_ready: true
    initiative: INIT-GATEFLOW-011
    meta_pr: "https://github.com/drivestream-lab/prayog-meta/pull/30"
    meta_pr_head: "f3da8148f3e861fad4720a3491f11f1fdc0145aa"
    map_revision: 1
    prd_digest: "sha256:eca06cbe986d619db58ae3ca84f4ec0987c19aa19b8f1485693280c6a655e4dd"
    scope_digest: "sha256:afdc7bd51bcd0c12f614feebf338bdc78766396bb84777121a2565c0ecc7966d"
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
    title: "[INIT-GATEFLOW-011] Spec — Day-1 visibility and GitHub reconcile (gateflow)"
    body_path: docs/specification/product/INIT-GATEFLOW-011-gateflow.md
```

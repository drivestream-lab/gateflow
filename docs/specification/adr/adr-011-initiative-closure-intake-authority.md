# ADR-011 — Initiative closure intake authority

| Field | Value |
|-------|-------|
| Status | Draft |
| Initiative | INIT-GATEFLOW-010 |
| Feasibility finding | PE-1 (F13 NEW-ADR signal for REQ-12–15) |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-010.md` |
| Source spec | `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` |
| Source spec digest | `sha256:0016f090e69903f3e1624ac218b0c96ebb3ba37d9966cbcbf6da988012061843` |
| product_constraints | `[REQ-12, REQ-13, REQ-14, REQ-15, REQ-18, REQ-20]` |
| changes_user_visible_behavior | `false` |
| spec_amendment_required | `false` |
| supersedes | none |
| superseded_by | none |
| Relates to | Extends ADR-010 (lane intake family); ADR-005 (programme-token mutations); ADR-009 (forge apply for purge-app / closure PR nodes); ADR-001 (run persistence) |
| Decision owner | PE |
| Approval evidence | Pending |
| Approved head | Pending |

> If `changes_user_visible_behavior` or `spec_amendment_required` would be
> `true`, **stop**: amend and re-approve the product spec before this ADR may
> become Accepted. Approved REQ-12–15 already define Enter-at path, HTTP
> semantics, Done-gate, EPIC Done hygiene, and purge walk — this ADR decides
> **internal intake authority** only.

## Product decisions excluded

- Exact HTTP path string — owned by approved **REQ-12** (`POST /api/v1/initiatives/closure/start`)
- 400 vs 422 side-effect table for malformed vs Done-gate failure — owned by spec negative paths + PRD error table
- Whether PM Enter-at or meta purge run in this INIT — out of scope (spec § out of scope)
- EPIC → Done timing relative to purge — owned by **REQ-14** (before purge-app dispatch)
- Pin node ids for purge-app / closure PR / signoff — pin SSOT; Gateflow consumes only

## Context

**ADR-010** (Accepted) defines three distinct programme-token **start** intake
shapes: implement lane, spec lane (dual workspace), and wave closeout Pass-2
(fixed Enter-at `learning-extract` with existing wave PR bind). It explicitly
does **not** catalogue every future Enter-at.

INIT-GATEFLOW-010 adds a **fourth** Enter-at for **engineering initiative
closure** (W4): programme token + required body binds (`initiative`,
`epic_ticket_id`, non-empty `wave_ticket_ids[]`, app workspace), Done-gate on
all wave tickets, EPIC Done hygiene before purge, then automated walk
`purge-initiative-artifacts-app` → `initiative-closure-pr-action-app` → STOP
`initiative-closure-signoff-app`. This is **not** wave closeout (Pass-2) and
**not** implement/spec lane start.

Without an explicit intake authority decision, implementers could:
- overload wave closeout route with optional closure fields (ADR-010 anti-pattern),
- resume a stopped wave run instead of new-run Enter-at,
- apply purge before Done-gate or mutate EPIC after failed purge (REQ-13/14/20 violations).

W0–W3 delivery does **not** require this ADR to be Accepted; closure route and
validators ship in W4. Draft status records the decision before planning W4.

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Amend **ADR-010** §7 “Initiative closure intake” (mirror §6 closeout) | Single lane-intake ADR; INIT-007 closeout precedent | Touches Accepted ADR-010 again; W4-only concern mixed with earlier lanes |
| B — **Separate ADR-011** (this file) extending ADR-010’s “separate contracts” principle | Keeps ADR-010 stable for W0–W3; clear W4 acceptance gate; relates without rewriting Accepted text | One more ADR file to accept at W4 |
| C — Document only in TDD / plan without ADR | Faster W4 start | Incompatible implementers could merge intake shapes; fails NEW-ADR disposition |

## Recommendation

**Option B — ADR-011 as initiative-closure intake authority**, aligned with
ADR-010 Option B (“separate start contracts; shared enqueue/run core”).

1. **Fourth distinct start contract.** `POST /api/v1/initiatives/closure/start`
   is a dedicated authenticated mutation surface (programme token per ADR-005).
   Request body must **not** share a mega-model with implement/spec/closeout
   starts. Undifferentiated alias routes are forbidden at cutover.
2. **Intake authority** = caller-supplied initiative identity +
   `epic_ticket_id` + non-empty `wave_ticket_ids[]` + absolute app
   `workspace` (+ org/repo binds per TDD validator). Client must **not** choose
   arbitrary `start_node`; Enter-at is **fixed** to the pin orchestrated entry
   for initiative closure (pin SSOT for skill id — Gateflow validates it exists
   and is orchestrated).
3. **New run only.** Closure start creates a **new** `run_id`; it does **not**
   resume Pass-1 implement, spec, or wave-closeout runs. Concurrent **ACTIVE**
   run for the same initiative scope fails closed (existing RunStore policy /
   ADR-005 catalogue).
4. **Done-gate before enqueue (REQ-13).** Validator resolves every
   `wave_ticket_ids[]` entry via BoardService; any not board Done → **422**, 0
   enqueue, no purge, EPIC not mutated. Malformed/empty binds → **400**.
5. **EPIC Done hygiene (REQ-14).** After Done-gate passes and before
   dispatching `purge-initiative-artifacts-app`, business applies EPIC → Done
   via BoardService (not a pin external-action node). Failure → terminal run
   failure; partial success handling per REQ-20.
6. **Walk authority.** Post-enqueue orchestration follows pin edges only;
   never dispatch `purge-initiative-artifacts-meta`; never merge closure PR
   (human signoff nodes per ADR-009 explicit authorization).
7. **Merge-at-acceptance option.** PE may later fold this ADR into an ADR-010
   amendment (INIT-007 closeout precedent) by supersession — until then,
   ADR-011 is the canonical Draft for W4 planning.

Exact Pydantic field names, repository columns, and route module paths remain
**TDD §3 / implementation plan** — not this ADR.

## Consequences

- OpenAPI stays lane-honest; closure body cannot be submitted to implement/spec/closeout routes.
- W4 plan and verify (`verify_closure`) have a stable authority reference before coding.
- Done-gate and EPIC hygiene are business-layer validators (ADR-003 layering), not pin overlays.
- ADR-010 remains unchanged on Accepted head until PE optionally supersedes via amendment.

## Revisit triggers

- Product merges initiative closure into wave closeout single body (supersede ADR-011).
- Product adds meta purge Enter-at in gateflow scope (new ADR or ADR-010 amendment).
- Pin removes automated purge-app node or changes authorization mode (reconcile with ADR-009).
- PE elects to fold ADR-011 into ADR-010 §7 instead of standalone Accepted ADR-011.

## Lifecycle — Accepted immutability and supersession

Once `Status: Accepted`, do **not** rewrite the accepted body in place.
To change the decision:

1. create a new ADR that `supersedes` this one,
2. set this ADR's `superseded_by` to the new id and status `Superseded`,
3. record owner, date, and review evidence on both files.

## Acceptance finalization

After PE review comments are resolved and PE explicitly states the decision is
ready for acceptance — **and** product-boundary fields remain `false` —
update the file before final GitHub approval:

```text
Status: Accepted
Decision owner: @{pe-name}
Approval evidence: {review/comment URL}
Approved head: {full SHA to be approved}
product_constraints: [REQ-12, REQ-13, REQ-14, REQ-15, REQ-18, REQ-20]
changes_user_visible_behavior: false
spec_amendment_required: false
```

The formal PE GitHub Approve must be on the final commit containing this
Accepted metadata. No file changes occur after that approval (publish via
Forge `/commit-workspace` — not inside content skills).

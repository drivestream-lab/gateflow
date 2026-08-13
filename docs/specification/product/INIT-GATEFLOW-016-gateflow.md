# INIT-GATEFLOW-016 — spec slice for gateflow

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-016 |
| PRD | **pending** — `prayog-meta/prd/INIT-GATEFLOW-016.md` not filed |
| PRD digest (H1) | **pending** — Gate 1 not run |
| Meta PR | **pending** |
| Meta PR approved head (G1) | **pending** |
| Impact map | **pending** — `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-016.md` |
| Impact-map revision (H3) | **pending** |
| Repo scope digest (H2) | **pending** |
| Tech-lead approval | **pending** — this file is a pre-Gate-1 engineering spec from chat-locked product decisions (2026-08-13). It is **not** an approved impact-map slice. |
| Architecture constraints (existing) | [`adr-014`](../adr/adr-014-jwt-only-product-edge-trust-zone.md) (**Accepted** — JWT-only product edge; claim shape `sub` / `role` / `tenant_id`). Revisit trigger on that record: finer binding than role + a single programme. This INIT's product intent (N:N membership + active-session programme) **requires a successor ADR** — not chosen here (Q-2). [`INIT-GATEFLOW-014`](INIT-GATEFLOW-014-gateflow.md) REQ-06 / REQ-15 / REQ-47 define today's 1:1 attach+JWT behaviour this INIT **breaks and replaces**. |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-13 |
| Status | Draft — **Gate 1 incomplete**; dev review of product behaviour is in progress; do not run `/initiative-feasibility` until a meta PRD + approved impact map exist and this header's H1–H3 / G1 are filled |

> **H4 citations:** H1–H3 / G1 above are **not** attested. Feasibility is blocked on Q-1. CAP/REQ ids in this file are the intended product vocabulary for the forthcoming PRD — remapping is forbidden once Gate 1 assigns the same numbers; if the PRD uses different numbers, this spec must be revised to cite them 1:1.

## Overview

INIT-GATEFLOW-014 made Gateflow-issued user JWTs the product edge and introduced
Programme + `tenant_admin` attach. Attach today **creates a login identity and
binds it to exactly one Programme in one call**, and may mint that person's JWT
as a side effect. A person has no display name; `tenant_admin` cannot belong to
two programmes (`credential_conflict`). Ops portal (deferred UI) needs a
**directory of people** and a **map people ↔ programmes** surface.

This INIT, **gateflow only**, replaces that attach contract with:

1. **Person directory** — create / read / update identifying fields (`display_name`,
   login identifier, `status`) and password, with or without a programme.
2. **Programme membership** — attach / detach an existing person to one or more
   programmes; the only programme role remains `tenant_admin`.
3. **Session** — login (and a current-caller snapshot) returns the person plus
   their programmes; a multi-programme caller **selects** one programme before
   programme-scoped product calls; the active session remains bound to **one**
   programme (cross-programme access still fails closed).
4. **Cutover** — the combined create+attach+JWT call is **removed** (breaking;
   lab is not live). Existing identities are **backfilled** into memberships.
   Teaching/verify use the new path in this INIT — no dual attach window.

**Scope boundary (this repo only):** CAP-01…CAP-04 / REQ-01–REQ-29 below.
Out of this repo: `gateflow-ops` screens (deferred **consumer** of these APIs);
SSO / IdP; encrypting secrets; per-repo ACL; new programme role types;
`platform_admin` as a programme membership; dual person-role on one login
(one identity is not both `platform_admin` and `tenant_admin`). INIT-013
catalogue connect/select and INIT-014 Programme onboard stay as they are except
where attach/login contracts change.

**Ownership:** this spec defines observable behaviour, acceptance, field
meaning, invariants, errors, and compatibility. Persistence layout, route
paths, JWT claim encoding for zero/N memberships, and which ADR supersedes
ADR-014 are **deferred to feasibility / technical review** (Q-2, Q-3).

**As-built baseline (2026-08-13, verified against local checkout):**

| Existing behaviour | Evidence |
|---|---|
| Login identity is `credential_identifier` + `password_hash` + person `role` (`platform_admin` \| `tenant_admin`) + optional `tenant_id`; **no** display name or status | `user_identity_schema.py`; `UserIdentityReadModel` |
| `platform_admin` attach is `POST` programme tenant-admins with identifier **and password**; creates identity or idempotent re-attach **same** programme; different programme → `credential_conflict`; response includes `access_token` | `ProgrammeService.attach_tenant_admin`; INIT-014 REQ-15, REQ-47 |
| JWT for `tenant_admin` carries `tenant_id`; programme-scoped routes require path tenant = JWT tenant | `AuthIdentityService.mint_user_jwt`; `require_programme_scope` |
| Login response is `{access_token, token_type}` only | `LoginResponse` |
| `GET /api/v1/programmes` is `platform_admin` only; no current-caller snapshot API | `programme_admin_routes.py` |
| `tenant_users` records a string identity under a tenant; **not** JWT login | INIT-012 REQ-04; `POST /tenants/{id}/users` |
| Lab is not a published live product; breaking API and schema change is accepted for this INIT | Product decision 2026-08-13 |

**Intended PRD capabilities (pre-Gate-1; become PRD `CAP-*` when filed):**

| CAP | Intent |
|-----|--------|
| **CAP-01** | Person directory (identifying fields, password, disable) |
| **CAP-02** | Map existing people to programmes (N:N; `tenant_admin` only) |
| **CAP-03** | Login / current-caller snapshot / select active programme |
| **CAP-04** | Breaking cutover + backfill + wipe membership rules + verify rewrite |

**Delivery waves (product-normative; gateflow-scoped):**

| Wave | Intent | Exit REQs |
|------|--------|-----------|
| **W0** | Durable person identifying fields + durable memberships; backfill; directory **read**; current-caller snapshot **read** | REQ-03, REQ-15, REQ-21, REQ-22, REQ-24, REQ-28 |
| **W1** | Create / patch / disable / set password; attach / detach / list members; **remove** combined attach+JWT door | REQ-01, REQ-02, REQ-04–REQ-13, REQ-23, REQ-26, REQ-27 |
| **W2** | Login snapshot; 0 / 1 / N session rules; select programme; cross-programme refuse | REQ-14, REQ-16–REQ-20 |
| **W3** | Wipe membership cascade; teaching/verify prove old attach gone | REQ-25, REQ-29 |

## Functional requirements

| ID | Requirement | PRD source | Condition / event | Observable result | Evidence layer | Wave |
|----|-------------|-----------|-------------------|-------------------|----------------|------|
| REQ-01 | `platform_admin` can create a **person** with login identifier, password, and display name **without** naming a programme | CAP-01 | Create-person call | Person exists; can later log in; 0 memberships; password never returned | unit + verify | W1 |
| REQ-02 | A person has `status` `active` or `disabled`; a disabled person cannot obtain a session | CAP-01 | Login after disable | Named refuse; 0 token | unit + verify | W1 |
| REQ-03 | `platform_admin` can list and read people with identifying fields (display name, login identifier, status, person-level role) and each person's programme memberships (programme identity + programme role) | CAP-01 | List/read call | Rows present; password hash, password, and GitHub PAT absent | unit + verify | W0 |
| REQ-04 | `platform_admin` can change a person's display name and status | CAP-01 | Patch call | Subsequent read/list shows new values | unit + verify | W1 |
| REQ-05 | `platform_admin` can set a person's password after create | CAP-01 | Set-password call then login | New password authenticates; old does not | unit + verify | W1 |
| REQ-06 | `platform_admin` can attach an **existing** person to an onboarded Programme as `tenant_admin` | CAP-02 | Attach call | Membership exists; person can use that programme after a valid session bind | unit + verify | W1 |
| REQ-07 | Attaching the same person to the same programme again is idempotent (no second conflicting membership) | CAP-02 | Repeat attach | Success; still one membership for that pair | unit + verify | W1 |
| REQ-08 | One person may hold membership on **more than one** Programme at the same time | CAP-02 | Attach to programme A then B | Both memberships visible on person read and on each programme's member list | unit + verify | W1 |
| REQ-09 | Detach removes **only** that programme membership; the person record remains; other memberships remain | CAP-02 | Detach call | That pair gone; person still listable | unit + verify | W1 |
| REQ-10 | `platform_admin` can list members of a Programme | CAP-02 | List-members call | Attached people visible with identifying fields; secrets absent | unit + verify | W1 |
| REQ-11 | A person whose person-level role is `platform_admin` cannot be attached as a programme member | CAP-02 | Attach of platform person | Named refuse; 0 membership | unit + verify | W1 |
| REQ-12 | Create-person, attach, and detach **never** issue a user JWT | CAP-02; CAP-04 | Those calls succeed | Response has no access token; session is obtained only via login or select-programme | unit + verify | W1 |
| REQ-13 | Attach or detach for an unknown Programme is refused; 0 membership change | CAP-02 | Bad programme id | Named refuse | unit + verify | W1 |
| REQ-14 | Successful login returns a session token **and** a snapshot: person identifying fields + the caller's programme memberships (id, name, programme role). Password and PAT absent | CAP-03 | Login | Snapshot matches directory; token usable per REQ-16–REQ-19 | unit + verify | W2 |
| REQ-15 | An authenticated caller can read the same snapshot for **themselves** (current-caller read) | CAP-03 | Current-caller read | Same fields as login snapshot; other people's data not included | unit + verify | W0 |
| REQ-16 | A `tenant_admin` with **zero** programme memberships cannot perform programme-scoped product operations | CAP-03 | Programme-scoped call | Named refuse (`programme_not_mapped` or equivalent); 0 state change | unit + verify | W2 |
| REQ-17 | A `tenant_admin` with **exactly one** membership is session-bound to that programme without an extra select step | CAP-03 | Login then programme-scoped call for that programme | Authorized | unit + verify | W2 |
| REQ-18 | A `tenant_admin` with **two or more** memberships must select a programme before programme-scoped calls succeed | CAP-03 | Login then call without select | Named refuse until select succeeds | unit + verify | W2 |
| REQ-19 | Select-programme binds the session to that programme **only if** the caller is a member | CAP-03 | Select member vs non-member | Member → subsequent calls for that programme authorized; non-member → named refuse; 0 bind | unit + verify | W2 |
| REQ-20 | A session bound to programme A cannot act on programme B's resources | CAP-03; INIT-014 REQ-31 | JWT/session for A on B's path | Named refuse; 0 state change | unit + verify | W2 |
| REQ-21 | The only **programme** role type remains `tenant_admin` | CAP-02; INIT-014 REQ-16 | Attach / membership read | No additional programme role values | inspection | W0 |
| REQ-22 | `platform_admin` is a **person-level** role only — not granted or removed by programme membership | CAP-01; CAP-02 | Directory vs attach | Platform people have 0 memberships; mapping APIs stay `platform_admin` | unit + inspection | W0 |
| REQ-23 | The INIT-014 combined create+attach+JWT call is **gone** (breaking). Callers that still use it fail; 0 create/attach via that door | CAP-04 | Old attach URL/body | Absent or refused (404/405/401); new create+attach path is the only way | unit + verify | W1 |
| REQ-24 | Existing login identities are backfilled: each prior 1:1 `tenant_admin` binding becomes a membership; display name is filled if missing (login identifier is an acceptable fill) | CAP-04 | After migrate | List people shows prior admins and their one programme; they can still log in | verify + inspection | W0 |
| REQ-25 | Wiping a Programme removes memberships **for that programme only**. The person remains if they have other memberships; if they have none, the person remains as an unassigned directory row (not auto-deleted) | CAP-04; INIT-014 REQ-35 | Wipe after N:N attach | Wiped programme has 0 members; other programmes unchanged | unit + verify | W3 |
| REQ-26 | Creating a person with an identifier that already exists is refused; 0 second person | CAP-01 | Duplicate create | Named conflict; original row unchanged | unit + verify | W1 |
| REQ-27 | `tenant_admin` cannot use person-directory create/list/patch or programme member map/unmap APIs | CAP-01; CAP-02; INIT-014 REQ-30 | `tenant_admin` JWT on those calls | Named refuse; 0 change | unit + verify | W1 |
| REQ-28 | GitHub PAT and person passwords are never present on directory, membership, login snapshot, or current-caller responses | CAP-01; INIT-014 REQ-07 | Any success body | No `pat` / `github_pat` / `password` / `password_hash` | unit + verify | W0 |
| REQ-29 | Live verify and teaching docs for attach/login use the new create → attach → login (→ select) path in this INIT; they do not document the removed door | CAP-04 | Verify + `tests/README.md` | Old attach not instructed; new path proven | verify + inspection | W3 |

> **Id convention:** `REQ-*` is canonical. Condition/event + observable result
> are acceptance (implementation-neutral). Evidence names how it will be proved.

### Target capability surface (illustrative — engineering owns exact routes)

| Capability | Notes |
|------------|-------|
| Create / list / get / patch person; set password; disable | `platform_admin`; CAP-01 |
| Attach / detach / list programme members | `platform_admin`; CAP-02; attach body is person id, not password |
| Login snapshot + current-caller snapshot + select programme | CAP-03 |
| *(removed)* Combined programme tenant-admins create+JWT | CAP-04 |

Exact paths, JSON field names, and error body fields → technical review (Q-2).

## Negative and failure paths

| REQ | Condition | Required behavior | Why it matters | Evidence |
|-----|-----------|-------------------|----------------|----------|
| REQ-02 | Login for `disabled` person | Named refuse; 0 token | Disabled operators must not keep a working door | unit + verify |
| REQ-11 | Attach `platform_admin` person to a programme | Named refuse; 0 membership | Prevents collapsing platform blast radius into a tenant session | unit + verify |
| REQ-12 | Attach success | No access token in response | Mapping must not impersonate the person | unit + verify |
| REQ-13 | Attach unknown programme | Named refuse; 0 membership | Same class as INIT-014 REQ-44 | unit + verify |
| REQ-16 | Zero memberships, programme-scoped call | Named refuse; 0 state change | Unassigned people must not inherit another programme's workspace | unit + verify |
| REQ-18 | N memberships, no select | Named refuse on programme-scoped calls | Prevents an ambiguous “which programme?” session | unit + verify |
| REQ-19 | Select a programme the caller is not a member of | Named refuse; session unchanged | Membership is the only grant | unit + verify |
| REQ-20 | Session for A on B | Named refuse; 0 state change | Multi-programme must not weaken INIT-014 isolation | unit + verify |
| REQ-23 | Old combined attach door | Gone or refused; 0 durable write via that door | No dual path while backfilling | unit + verify |
| REQ-26 | Duplicate login identifier | Named conflict; 0 second person | Directory identity must stay unique | unit + verify |
| REQ-27 | `tenant_admin` on directory/mapping | Named refuse | Mapping is a platform operation | unit + verify |

## Out of scope for this repo

- `gateflow-ops` UI / assignment screens — deferred consumer of CAP-01…03 APIs
- Full IdP / SSO — Gateflow-issued password login remains (INIT-014 non-goal)
- New programme role types beyond `tenant_admin` (INIT-014 REQ-16 preserved)
- One login that is both `platform_admin` and `tenant_admin`
- Per-repo ACL inside a programme (INIT-012 REQ-05 unchanged)
- Using or extending `tenant_users` as the login directory
- Auto-connect of programme meta at Programme create (INIT-013 connect remains)
- Scoping `GET /tenants` list to the caller (separate hardening; not this INIT)
- Encrypting DB secrets
- GitHub App runtime activation (INIT-014 REQ-14)

## Cross-service contracts

| Contract ID | Provider / owner | Consumer / owner | Entry point | Input shape | Output shape | Invariants | Errors | Compatibility / versioning | Contract-test location |
|-------------|------------------|------------------|-------------|-------------|--------------|------------|--------|----------------------------|------------------------|
| CTR-01 | gateflow / prayog-pe-team | Product callers: verify scripts, future `gateflow-ops`, humans | Person directory + programme membership + session snapshot under Gateflow-issued JWT | `platform_admin` JWT for directory/map; person credentials for login; select-programme with that person's JWT | Person identifying fields + membership list; session token; **never** password or PAT | Membership N:N; active session one programme; old combined attach door gone | Named refuse on disable, not-member, role mismatch, unknown programme, duplicate identifier | **Breaking** relative to INIT-014 REQ-15/47 — no dual attach window | unit + verify |

> Entry point is semantic. Concrete paths belong to technical review.

## Non-functional requirements

| Area | Requirement or N/A rationale | Acceptance / evidence |
|------|------------------------------|-----------------------|
| Security | Directory/mapping is `platform_admin` only. Attach does not mint the person's JWT. Session isolation remains one active programme (REQ-20). PAT and passwords never in responses. Disable stops login. | unit + verify |
| Reliability | Create, attach, detach, disable, wipe fail closed with named reasons and no partial conflicting membership. Duplicate identifier and unknown programme do not write. | unit + verify |
| Performance / capacity | N/A as a product SLO — directory and membership reads/writes are per-admin operations; no new capacity claim. | inspection |
| Observability | Structured logs for create/attach/detach/disable/login/select (user id, programme id, named reason); never password, PAT, or raw JWT. | inspection |
| Privacy / data handling | Display name and login identifier are organisational operator identity, not end-user PII beyond what INIT-014 already stores. | inspection |
| Migration / compatibility | **Breaking** API cutover (REQ-23). Durable backfill of existing 1:1 bindings (REQ-24). Schema change is in scope (lab not live). Teaching/verify rewritten this INIT (REQ-29). | unit + verify + inspection |
| Rollback / recovery | After W1 merge, restoring INIT-014 attach requires an explicit revert — no dual door. Backfill is forward-only once applied. | inspection |
| Operations / support | `platform_admin` onboards Programme (INIT-014), creates the person, then attaches. Unassigned people are supported. Ops portal is not required to ship the APIs. | verify + inspection |

## Assumptions

| ID | Assumption | Evidence | Owner | Status | Invalidated when |
|----|------------|----------|-------|--------|------------------|
| A-1 | Lab/product is not live; breaking API and DB schema change is acceptable | Product decision 2026-08-13 | PM | confirmed | A published external caller must be dual-supported |
| A-2 | `gateflow-ops` is a later consumer; this INIT ships APIs only | INIT-014 out-of-scope; this spec out-of-scope | PM | confirmed | Portal is in-scope for the same INIT |
| A-3 | Password is required at person create; admin may rotate later (REQ-05) | Product decision 2026-08-13 | PM | confirmed | Invite-only / passwordless create is required |
| A-4 | One login is not both `platform_admin` and `tenant_admin` | Product decision 2026-08-13 | PM | confirmed | Dual person-role is required |
| A-5 | INIT-013 connect and fleet select/deselect stay `tenant_admin` and unchanged except session bind | This spec out-of-scope | PE | confirmed | Auto-connect at onboard is pulled into this INIT |
| A-6 | Forthcoming PRD will use the same CAP-01…04 / REQ-01…29 numbering, or this spec will be revised to cite the PRD 1:1 | Pre-Gate-1 draft | PM | open | Gate 1 map uses different ids |

## Spec questions (ambiguities)

| ID | Lane | Question | Owner | Blocking | Required by | Default if deferred | Status | Resolution link |
|----|------|----------|-------|----------|-------------|---------------------|--------|-----------------|
| Q-1 | PM | File `prayog-meta` PRD + impact map for INIT-GATEFLOW-016 and complete Gate 1 (H1–H3 / G1). Until then this spec cannot enter feasibility. | PM | **yes** | Gate 1 / feasibility | **None** — cannot defer | open | pending |
| Q-2 | PE | How is “no active programme” vs “one active programme” represented on the session token vs current-caller snapshot? (claim present/absent, or snapshot-only) | PE | no | technical review | Session token omits programme bind until REQ-17/19 apply; snapshot always lists memberships | open | pending |
| Q-3 | PE | Persistence/layout for person vs membership, and which ADR supersedes ADR-014 for N:N bind | PE | no | technical review | **None** as product default — engineering owns; product invariant is REQ-08 + REQ-20 | open | pending |

## Draft check summary (D1–D12)

| Check | Status | Evidence / findings |
|-------|--------|---------------------|
| D1 Approved handoff current | NEEDS INPUT | No meta PRD, impact map, or tech-lead APPROVED review. Q-1. |
| D2 Complete PRD traceability | NEEDS INPUT | REQs cite intended CAP-01…04; PRD not filed (A-6). |
| D3 Repo-bounded scope | PASS | Gateflow APIs only; ops UI / SSO / other repos listed out of scope. |
| D4 Observable acceptance | PASS | Each REQ has condition, observable result, evidence, wave. |
| D5 Negative/failure paths | PASS | Disable, unknown programme, not-member, cross-programme, old door, duplicate id, role refuse. |
| D6 Assumptions/questions | PASS | A-1…A-6; Q-1 blocking; Q-2/Q-3 non-blocking with defaults. |
| D7 Cross-repository contracts | PASS | CTR-01 semantic; ops portal named as future consumer. |
| D8 NFR applicability | PASS | All NFR rows present; performance N/A with reason. |
| D9 As-built alignment | PASS | Baseline table distinguishes 014 attach vs this INIT. |
| D10 Dependency order | PASS | After 014 JWT/Programme; does not depend on 015 metrics. Connect leftover not in scope. |
| D11 Zero unresolved blockers | FAIL | Q-1 blocks Gate 1 / feasibility. |
| D12 Output completeness | PASS | Header (pending Gate 1 marked), tables, checks, outcome, PR readiness. |

**Draft verdict:** NEEDS INPUT (Gate 1 / PRD missing)

**Selected workflow outcome:** `needs-input`
**Outcome reason:** D1/D2/D11 — no approved meta PRD or impact map; product behaviour is drafted locally for review.

Do not advance to `/initiative-feasibility` until Q-1 is resolved and H1–H3 / G1 are real.

## PR readiness handoff

| Item | Value |
|------|-------|
| Workflow outcome | `needs-input` — Gate 1 / PRD missing (Q-1) |
| Verdict | **PR BLOCKED** for spec-lane publish as an approved slice; local draft may be reviewed in-repo |
| Existing spec PR | none |
| Proposed branch | `chore/INIT-GATEFLOW-016-spec-gateflow` (after Gate 1) |
| Proposed base | `develop` |
| Proposed title | `[INIT-GATEFLOW-016] Spec — gateflow` |
| PR type | **Draft** (entire spec lifecycle) |
| Local artifacts to publish | `docs/specification/product/INIT-GATEFLOW-016-gateflow.md`, `docs/specification/README.md` |
| Forge readiness | **not filled** — `open_draft_pr` only when outcome is `pass` |
| Reviewer | @prayog-pe-team |
| Initial Gate 2 label | `spec-pending` (after Gate 1) |
| Additional invalidation label | none |
| Blocking items | Q-1 |

**No GitHub side effects have occurred.**

### Proposed Draft PR body

```markdown
## Initiative

INIT-GATEFLOW-016 — Person directory + programme membership (breaking replace of 014 attach)

## Meta handoff

- Meta PRD PR: pending (Q-1)
- Approved meta head: pending
- Impact-map revision: pending
- PRD digest: pending
- Repo scope digest: pending

## Spec path

`docs/specification/product/INIT-GATEFLOW-016-gateflow.md`

## Summary

- CAP-01…04 / REQ-01–REQ-29: directory, N:N attach, session select, breaking cutover
- Open: Q-1 (Gate 1) blocking; Q-2/Q-3 PE non-blocking

## Gate 2 — spec package readiness

Blocked until Gate 1.

Requested reviewer: @prayog-pe-team
```

## Developer review

- [ ] Scope matches an **approved** impact-map repo scope digest (blocked on Q-1)
- [x] REQs have condition/event, observable result, and evidence layer
- [x] Contracts are semantic; no persistence/ADR choice in REQs
- [ ] No blocking question remains (Q-1 open)
- [ ] Developer confirmed draft is ready for feasibility (not until Gate 1)

## After Draft PR creation

PE controls Gate 2 labels on the spec PR. Not applicable until Gate 1 + `pass`.

## References

- PRD: pending `prayog-meta/prd/INIT-GATEFLOW-016.md`
- Prior attach contract: [`INIT-GATEFLOW-014-gateflow.md`](INIT-GATEFLOW-014-gateflow.md) REQ-15, REQ-47, REQ-06
- ADR-014: [`adr-014-jwt-only-product-edge-trust-zone.md`](../adr/adr-014-jwt-only-product-edge-trust-zone.md)

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-draft
  outcome: needs-input
  artifact:
    path: docs/specification/product/INIT-GATEFLOW-016-gateflow.md
  blockers:
    - Q-1
  signals:
    gate1_pending: true
    pre_prd_local_draft: true
  next_candidates:
    - spec-human-decision
  human_checkpoint: true
  external_action: false
```

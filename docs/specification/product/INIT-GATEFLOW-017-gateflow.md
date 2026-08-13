# INIT-GATEFLOW-017 — spec slice for gateflow

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-017 |
| PRD | `prayog-meta/prd/INIT-GATEFLOW-017.md` |
| PRD digest (H1) | `sha256:c0fe55040928a13976133edde5cf71f0524815c17c0a8de79173ed3fa0657f67` |
| Meta PR | https://github.com/drivestream-lab/prayog-meta/pull/42 |
| Meta PR approved head (G1) | `601b00e0a74510a6af1c33bc80ca27260995c094` |
| Impact map | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-017.md` |
| Impact-map revision (H3) | `1` |
| Repo scope digest (H2) | `sha256:3d39ee6d5947bcd18c3e0b46de16709b3fdddeefeb0e8d5bbae8ecf98b1e5834` |
| Tech-lead approval | [@0xbeefdead APPROVED](https://github.com/drivestream-lab/prayog-meta/pull/42#pullrequestreview-4927360675) 2026-08-13T13:04:05Z on `601b00e0a74510a6af1c33bc80ca27260995c094` — attestation: `initiative: INIT-GATEFLOW-017`, `map_revision: 1`, `prd_digest` match, `artifact: prd/reports/Impact-Map-INIT-GATEFLOW-017.md`; label `impact-map-lgtm`; meta PR **merged** |
| Architecture constraints (existing) | [`adr-014`](../adr/adr-014-jwt-only-product-edge-trust-zone.md) (**Accepted** — JWT-only product edge; claim shape `sub` / `role` / optional `tenant_id`). Revisit trigger on that record: finer binding than role + a single programme. This INIT's product intent (one identity sign-in; many programme grants; programme is authorization, not a second login) **requires a successor ADR** — not chosen here (Q-1). [`adr-016`](../adr/adr-016-tenant-scoped-run-board-checkpoint-authorization.md) (**Accepted** — programme-scoped delivery reads/writes). [`INIT-GATEFLOW-014`](INIT-GATEFLOW-014-gateflow.md) REQ-06 / REQ-15 / REQ-47 define today's 1:1 create+bind+JWT behaviour this INIT **deletes**. Historic handle-attach [`INIT-GATEFLOW-012`](INIT-GATEFLOW-012-gateflow.md) `POST /tenants/{id}/users` is **purged** (PRD REQ-20). Local pre-Gate-1 [`INIT-GATEFLOW-016`](INIT-GATEFLOW-016-gateflow.md) invite stories are **not** this repo's product truth. |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-13 |
| Status | Draft — dev review required before Forge publish |

> **H4 citations:** The H1–H3 (and G1) rows above are the durable authority
> carrier for mid-lane freshness. Feas / TDD / plan digests are walk-time only
> and may be purged at initiative closure — see
> [`artifact-write-contract.md`](../../../prayog-skills/references/artifact-write-contract.md).

## Overview

INIT-GATEFLOW-014 made Gateflow-issued user JWTs the product edge and introduced
Programme + `tenant_admin` attach. Attach today **creates a login identity and
binds it to exactly one Programme in one call**, and mints that person's JWT as
a side effect. A person has no name; login identifier is not required to be an
email; a `tenant_admin` cannot belong to two programmes (`credential_conflict`).

This INIT, **gateflow only**, replaces that identity model with:

1. **Enter identity** — `platform_admin` creates a factory identity (name, unique
   email, password) with role `tenant_admin` and **zero programmes**.
2. **Grant / detach** — `platform_admin` grants an **existing** identity entry to
   one or more onboarded programmes (no new login, no password collected); detach
   removes that grant only.
3. **Sign-in once, enter a granted programme** — email + password yields a
   current sign-in; the caller sees only programmes they were granted and reaches
   013/016 delivery by **entering** one. Programme is authorization, not a second
   login (IM-01 default). Zero grants: signed in, no delivery.
4. **Suspend / unsuspend / set password** — suspend blocks sign-in and every
   further product act including reads, without cancelling in-flight waves;
   password-set kills the prior sign-in.
5. **Cutover** — 014 create+bind is **deleted** (not dual-model). Historic
   handle-attach / invite is **purged**. Leftover 014 bind rows in a lab database
   are wiped (OQ-01 default). Seeded `platform_admin` remains the only
   factory-admin path and is **not** grantable as `tenant_admin` (OQ-03 default).

**Scope boundary (this repo only):** CAP-01…CAP-06 / PRD REQ-01…REQ-30 /
CTR-01–04 **provider** per the approved impact-map H2 payload. Out of this repo:
`gateflow-ops` console (CTR-01–04 **consumer**; sequenced after this provider);
SSO / IdP; delete identity; change email after entry; self-serve password; extra
programme roles; encrypting stored secrets; rewriting 013/016 delivery except
removing invite; programme wipe / un-onboard (stays the existing 014 wipe act).

**Ownership:** this spec defines observable behaviour, acceptance, field
meaning, invariants, errors, and compatibility. Persistence layout, route paths,
JWT claim encoding for zero/N grants, and which ADR supersedes ADR-014 are
**deferred to feasibility / technical review** — not decided here (Q-1, Q-5).

**As-built baseline (2026-08-13, verified against local checkout + codegraph
`data-repos-prayog-gateflow` then confirmed by source read):**

| Existing behaviour | Evidence | This INIT |
|---|---|---|
| Login identity is `credential_identifier` + `password_hash` + person `role` (`platform_admin` \| `tenant_admin`) + optional `tenant_id`; **no** name, email-shape rule, or suspend flag | `user_identity_schema.py`; `UserIdentityReadModel` | **changed** — name required; email unique login; suspend |
| `platform_admin` attach is `POST …/programmes/{id}/tenant-admins` with identifier **and password**; creates identity or idempotent re-attach **same** programme; different programme → `credential_conflict`; response includes `access_token` | `ProgrammeService.attach_tenant_admin`; INIT-014 REQ-15, REQ-47 | **deleted** (REQ-21) |
| JWT for `tenant_admin` carries `tenant_id`; programme-scoped routes require path tenant = JWT tenant | `AuthIdentityService.mint_user_jwt`; `require_programme_scope`; ADR-014 / ADR-016 | **changed** product: one identity sign-in then enter a granted programme; claim encoding → Q-1 |
| Login response is `{access_token, token_type}` only; identifier is not required to be an email | `LoginRequest` / `LoginResponse`; `POST /api/auth/login` | **changed** — email login; resolve granted programmes (CTR-03/04) |
| `GET /api/v1/programmes` is `platform_admin` only; no factory identity list; no who-can-enter | `programme_admin_routes.py` | **new** identity/grant read surfaces (REQ-04, REQ-11) |
| Historic `POST /api/v1/tenants/{tenant_id}/users` records a string handle under a tenant; **not** a JWT login | `tenant_routes.py` `attach_tenant_user`; INIT-012 REQ-04 | **purged** (REQ-20) |
| Seeded `platform_admin` is the only factory-admin create path | `scripts/seed_platform_admin.py`; INIT-014 REQ-01, REQ-47 | **kept** (REQ-05, A3) |
| Programme onboard / catalogue show stay as 014 | `ProgrammeService.validate_then_create`; INIT-014 REQ-08–14, REQ-48–49 | **kept** (REQ-27, A1) |
| Lab is not a published live product; breaking API and schema change is accepted | Product decision in PRD Lock 5 / OQ-01 | **kept** |

**PRD capabilities (this repo, H2):**

| CAP | Intent |
|-----|--------|
| **CAP-01** | Enter and find identities (name, unique email, password write-only; role `tenant_admin`) |
| **CAP-02** | Grant and refuse programme entry (existing identity; detach; many programmes; who-can-enter) |
| **CAP-03** | Suspend, unsuspend, and set password (prior sign-in dead; in-flight waves continue) |
| **CAP-04** | `tenant_admin` works every programme they were granted (one sign-in; enter one; keep 013/016 delivery) |
| **CAP-05** | One membership story; 014 bind and invite gone |
| **CAP-06** | Programme onboard and catalogue stay as they are |

Wave split (gateflow API vs gateflow-ops console) is **not** product-normative
here — IM-03 / Q-2, required by implementation plan. Default: this repo ships
enter+grant **before** ops identity screens (kill line).

## Functional requirements

| ID | Requirement | PRD source | Condition / event | Observable result | Evidence layer |
|----|-------------|-----------|-------------------|-------------------|----------------|
| REQ-01 | `platform_admin` enters a human with name, email, and a password, with no programme required | PRD REQ-01; CAP-01; Lock 4 | Valid entry by `platform_admin` | Identity exists on the factory list with that name and email; role is `tenant_admin`; they can later sign in with that email and password; they belong to no programme yet | unit / live verify |
| REQ-02 | Email is the sign-in identifier and is unique in the factory | PRD REQ-02; CAP-01; J6 | Second entry uses an email that already exists | Refused (`duplicate email`); no second identity; first identity unchanged | unit / live verify |
| REQ-03 | Login identifier must be an email | PRD REQ-03; CAP-01; Lock 3 | Entry or sign-in identifier is empty, has no `@`, or has no domain part | Refused (`not an email`); no identity created (entry) / no sign-in (sign-in) | unit |
| REQ-04 | `platform_admin` can list factory identities and find an identity by name or email | PRD REQ-04; CAP-01; J1 | `platform_admin` searches the entered list | Identities whose name contains the query (case-insensitive) or whose email equals the query (case-insensitive exact) are shown; no match shows an empty result, not an error | live verify / inspection |
| REQ-05 | Entering a human creates `tenant_admin`, not `platform_admin`. Seeded `platform_admin` remains the only factory-admin path and is **not** grantable as `tenant_admin` on a programme | PRD REQ-05; CAP-01; Lock 2; OQ-03 default | Identity entry succeeds; grant names the seeded `platform_admin` | New identity cannot perform `platform_admin` acts; seeded `platform_admin` is unchanged; grant of that seeded identity is refused; 0 grant | unit / live verify |
| REQ-06 | `platform_admin` grants an existing factory identity entry to an onboarded programme | PRD REQ-06; CAP-02; Lock 4 | Identity exists; programme exists; not already granted that programme | Identity may enter that programme after sign-in; no new login is created; password is not collected | unit / live verify |
| REQ-07 | Grant of an identity already granted that programme is idempotent | PRD REQ-07; CAP-02; J1 edge | Repeat grant of the same identity to the same programme | Success; still one grant; identity unchanged | unit |
| REQ-08 | An identity that has not been entered cannot be granted | PRD REQ-08; CAP-02; J1 abandon | Grant names an email/identity that is not on the factory list | Refused (`unknown identity`); no grant | unit / live verify |
| REQ-09 | One identity may be granted more than one programme | PRD REQ-09; CAP-02; Lock 6; A5 | Grant the same identity a second programme | Both grants exist; one email; one password; they can enter either programme | unit / live verify |
| REQ-10 | `platform_admin` detaches an identity from a programme | PRD REQ-10; CAP-02; Lock 9; J13 | Detach of an existing grant | That grant is gone; identity remains; other grants remain; programme remains. Detach of the last grant leaves a zero-programme identity that can still sign in (unless suspended) | unit / live verify |
| REQ-11 | `platform_admin` can see who can enter a given programme, and which programmes a given identity can enter, without opening a delivery screen | PRD REQ-11; CAP-02; J10 | `platform_admin` opens identity or programme membership | Membership is visible as identities ↔ programmes; password absent (REQ-30) | live verify / inspection |
| REQ-12 | Suspended identity cannot sign in and cannot continue product acts | PRD REQ-12; CAP-03; Lock 10; J4 | `platform_admin` suspends an identity | Sign-in refused (`suspended`); any current sign-in cannot continue any product act, including reads; grants unchanged | unit / live verify |
| REQ-13 | Unsuspend restores sign-in; grants unchanged | PRD REQ-13; CAP-03; J9 | `platform_admin` unsuspends | Identity can sign in and work every programme they are still granted | unit / live verify |
| REQ-14 | `platform_admin` sets a new password; previous sign-in stops working | PRD REQ-14; CAP-03; Lock 11; J8 | Password set for that identity | They can sign in only with the new password; prior sign-in cannot continue | unit / live verify |
| REQ-15 | Detach or suspend does not cancel waves already running | PRD REQ-15; CAP-03; Lock 12; J5 | Detach or suspend while a wave is in flight on that programme's repo | In-flight wave continues; that identity cannot start or authorize further work (detach: in that programme; suspend: anywhere). After detach, that programme is not enterable (reads included). After suspend, an open sign-in cannot continue any product act, including reads | unit / live verify |
| REQ-16 | After one identity sign-in, a `tenant_admin` sees only programmes they were granted and reaches delivery by entering one. Programme is authorization, not a second login | PRD REQ-16; CAP-04; Lock 7; IM-01 default | Sign-in with at least one grant | They can include repos, run waves, and look at metrics in an **entered** granted programme; they cannot enter a programme they were not granted (`not granted`). Claim/token encoding is engineering (Q-1) | live verify |
| REQ-17 | The same identity can run delivery in two programmes they were granted | PRD REQ-17; CAP-04; J2; A2 | Identity is granted two programmes with different repos | They can start work in both (after entering each); existing **one active wave per repo** still holds | live verify |
| REQ-18 | A signed-in identity with zero programmes cannot run delivery | PRD REQ-18; CAP-04; Lock 14; J3 | Sign-in with no programme grant | They are signed in; they can observe that they belong to no programme; no programme delivery is available | live verify |
| REQ-19 | `tenant_admin` can still include catalogue repos, run waves, and look at metrics in a programme they were granted | PRD REQ-19; CAP-04; CAP-06 | Granted identity enters that programme | 013/016 delivery acts succeed; invite is absent | live verify / inspection |
| REQ-20 | There is no invite act. Historic handle-attach that cannot sign in is gone | PRD REQ-20; CAP-05; Lock 8; J7; J11 | `tenant_admin` or any actor attempts invite / `POST /api/v1/tenants/{tenant_id}/users` (INIT-012 attach) | Act is gone (absent or refused); no membership created that way | live verify / inspection |
| REQ-21 | Membership is not created by minting a login bound to one programme in the same act. The 014 create+bind door is deleted. Leftover 014 1:1 bind rows in a lab database are wiped; no dual-model compatibility path | PRD REQ-21; CAP-05; Lock 5; J12; OQ-01 default | Actor attempts 014-style create+bind (new email + password as grant); leftover bind rows at cutover | Refused or impossible; identity entry and grant remain separate; that 014 act is gone; leftover bind rows are not a live membership path | unit / live verify |
| REQ-22 | `tenant_admin` cannot enter identities, grant, detach, suspend, or set password | PRD REQ-22; CAP-05; Lock 1; J11 | `tenant_admin` attempts those acts | Refused (`wrong actor`); 0 state change | unit / live verify |
| REQ-23 | `platform_admin` cannot include repos, start or authorize waves, or operate programme metrics | PRD REQ-23; CAP-05; Lock 15; A1 | `platform_admin` attempts those acts | Refused (`wrong actor`); 0 state change | unit / live verify |
| REQ-24 | A suspended identity may still be granted or detached; suspend only blocks sign-in and product acts (including reads) | PRD REQ-24; CAP-02; J4 edge | Grant or detach while suspended | Membership changes; they still cannot sign in until unsuspended | unit |
| REQ-25 | Name is required at identity entry and is shown on the factory list. Name is a display label, not unique | PRD REQ-25; CAP-01; A4 | Entry without a name | Refused (`missing name`); no identity | unit |
| REQ-26 | `tenant_admin` does not see other identities or the factory identity list | PRD REQ-26; CAP-04; Lock 15; J14 | Signed-in `tenant_admin` opens delivery | No factory identity list; no roster of other identities on the programme | live verify / inspection |
| REQ-27 | `platform_admin` still onboards a programme and its meta repo, stores the parsed catalogue, and can show that catalogue | PRD REQ-27; CAP-06; A1 | Programme onboard by `platform_admin` | Catalogue is visible to `platform_admin`; include-into-delivery remains a `tenant_admin` act after grant (REQ-19). Onboard APIs are unchanged this INIT except identity/grant | live verify / inspection |
| REQ-28 | Grant or detach naming a programme that is not onboarded is refused | PRD REQ-28; CAP-02 | Grant or detach names a programme that does not exist | Refused (`unknown programme`); 0 membership change | unit / live verify |
| REQ-29 | Entry without a password is refused | PRD REQ-29; CAP-01 | Entry without a password | Refused (`missing password`); no identity | unit |
| REQ-30 | After set, password is never returned on list, search, or membership views | PRD REQ-30; CAP-01; J8/J10 | `platform_admin` lists, searches, or views membership | Password is not shown or returned. GitHub PAT remains absent on these surfaces (INIT-014 REQ-07, unchanged) | live verify / inspection |

> **Id convention:** `REQ-*` is canonical (`prayog-skills/references/id-conventions.md`).
> Numbered 1:1 with the PRD. Do not invent wave-scoped `REQ-W*` ids.
>
> **Behavioral acceptance vs evidence:** Condition/event + observable result are
> the product acceptance statement (implementation-neutral). Evidence layer
> names how it will be proved later — not the implementation design.
>
> **Named refusals (product vocabulary):** `duplicate email`, `not an email`,
> `missing name`, `missing password`, `unknown identity`, `unknown programme`,
> `not granted`, `suspended`, `wrong actor`. Invalid sign-in credentials remain
> a named unauthorized outcome (CTR-03; existing INIT-014 login refuse).

## Negative and failure paths

| REQ | Condition | Required behavior | Why it matters | Evidence |
|-----|-----------|-------------------|-----------------|----------|
| REQ-02 | Duplicate email | Refuse (`duplicate email`); existing identity untouched | Two logins for one human is the failure mode this INIT exists to stop | unit / live verify |
| REQ-03 | Identifier is empty, has no `@`, or has no domain part | Refuse (`not an email`) | Lock 3: login is email | unit |
| REQ-05 | Grant of seeded `platform_admin` as `tenant_admin` | Refuse; 0 grant; seeded admin unchanged | Lock 2 / OQ-03: entering a human is not `platform_admin`; seed is not a delivery identity | unit / live verify |
| REQ-08 | Grant of unknown identity | Refuse (`unknown identity`) | Enter-then-grant; no silent create | unit / live verify |
| REQ-10 | Detach last programme | Identity remains; zero programmes; they can still sign in (unless suspended) | Identity ≠ grant | unit / live verify |
| REQ-12 | Suspend while a sign-in is open | Current sign-in cannot continue any product act, including reads | “Cannot sign in” is not enough if the tab stays live | unit / live verify |
| REQ-14 | Password set while a sign-in is open | Prior sign-in unusable; new password only | Stolen or rotated credentials must kill the live session | unit / live verify |
| REQ-15 | Detach during an in-flight wave | Wave continues; they cannot start/authorize in that programme; that programme is not enterable (reads included) | Waves belong to the programme/repo, not the identity | unit / live verify |
| REQ-16 | Enter a programme they were not granted | Refused (`not granted`) / not available | Grant is the gate | live verify |
| REQ-18 | Zero programmes | Signed in; no delivery | Entry-without-programme is real | live verify |
| REQ-20 | Invite / historic `POST …/tenants/{id}/users` | Gone | Lock 8 — one membership story | live verify / inspection |
| REQ-21 | Create+bind grant | Gone; leftover bind rows wiped | Lock 5 / OQ-01 — no dual model | unit / live verify |
| REQ-22 | `tenant_admin` grants entry / enters identities / suspends / sets password | Refuse (`wrong actor`); 0 state change | Lock 1 | unit / live verify |
| REQ-23 | `platform_admin` runs delivery | Refuse (`wrong actor`); 0 state change | Role split | unit / live verify |
| REQ-24 | Grant or detach while suspended | Membership changes; they still cannot sign in | Suspend is not a membership freeze | unit |
| REQ-25 | Entry without a name | Refuse (`missing name`); no identity | Name is required | unit |
| REQ-26 | `tenant_admin` looks for other identities | Not shown | Lock 15 | live verify / inspection |
| REQ-28 | Grant or detach of a programme that is not onboarded | Refuse (`unknown programme`); 0 membership change | Programme must exist before grant | unit / live verify |
| REQ-29 | Entry without a password | Refuse (`missing password`); no identity | Password is required at entry | unit |
| REQ-30 | List, search, or membership view returns or displays a password | Not shown; 0 leak | Password is write-only after set | live verify / inspection |
| CTR-03 | Sign-in with unknown email or wrong password | Named unauthorized; 0 sign-in | Existing 014 login refuse kept; email uniqueness does not leak whether the email exists beyond the named unauthorized | unit / live verify |
| CTR-01–04 | Missing / malformed / expired JWT on identity or grant acts | Unauthorized; 0 state change | JWT-only product edge (ADR-014) is unchanged | unit |

Timeouts and lab-scale capacity limits are **N/A** (NFR performance). Partial
create is forbidden: entry/grant/detach either take effect or refuse with a
named reason (PRD reliability).

## Out of scope for this repo

- `gateflow-ops` console screens (enter/find/grant/detach/who-can-enter/suspend/password, programme enter, purge invite UI) — **affected consumer**, depends on this provider (impact map §7)
- Invite / `tenant_admin` “add a teammate” as a product act (PRD non-goal; REQ-20 is the gateflow purge)
- Delete identity; change email after entry
- Self-serve password change
- Extra programme roles beyond `tenant_admin`
- A separate identity provider or SSO
- Rewriting 013/016 Mission Control delivery (repos, waves, metrics, board, scorecard) except removing invite
- Programme wipe / un-onboard of a programme (stays the existing 014 wipe act; wiping a programme makes it unknown per REQ-28)
- `platform_admin` including repos, starting or authorizing waves, or operating programme metrics as `tenant_admin`
- Encrypting stored secrets (014 plaintext-accepted posture unchanged)
- A company people directory product or display-name-as-SSO
- Document updates to `prd/INIT-GATEFLOW-014.md` / `prd/INIT-GATEFLOW-016.md` (OQ-04 / OQ-02 — PM follow-on in prayog-meta)

## Cross-service contracts

| Contract ID | Provider / owner | Consumer / owner | Entry point | Input shape | Output shape | Invariants | Errors | Compatibility / versioning | Contract-test location |
|-------------|------------------|------------------|-------------|-------------|--------------|------------|--------|----------------------------|------------------------|
| CTR-01 | gateflow / prayog-pe-team | gateflow-ops / prayog-pe-team | Enter identity; list/search identities; suspend; unsuspend; set password | Name, email (login), password (write-only at enter/set), actor `platform_admin` | Identity: name, email, suspended or not, role `tenant_admin`. Password never read back | Email unique. Entry does not create a programme grant. Entry is not `platform_admin`. Seeded `platform_admin` is not grantable as `tenant_admin` | `duplicate email`; `not an email`; `missing name`; `missing password`; `wrong actor` | **new** — breaking vs 014 attach-creates-identity | unit + planned `tests/verify/` identity scripts |
| CTR-02 | gateflow / prayog-pe-team | gateflow-ops / prayog-pe-team | Grant programme entry; detach; list who can enter a programme; list programmes an identity can enter | Existing identity + onboarded programme; actor `platform_admin` | Grant: this identity may enter this programme as `tenant_admin` | Identity must already exist. Grant does not set password. Many grants per identity. Detach is not programme wipe. Idempotent re-grant | `unknown identity`; `unknown programme`; `wrong actor` | **new** (replaces 014 create+bind attach) | unit + planned `tests/verify/` |
| CTR-03 | gateflow / prayog-pe-team | gateflow-ops / prayog-pe-team | Sign-in | Email + password → a current sign-in as that identity | Sign-in usable for subsequent enter/delivery per CTR-04 | Suspended identity cannot obtain a sign-in. After suspend, an open sign-in cannot continue any product act, including reads. After password set, prior sign-in is unusable | Invalid credentials; `suspended` | **changed** vs 014 login (email unique; not programme-bound 1:1) | unit + `verify_jwt_login` successor |
| CTR-04 | gateflow / prayog-pe-team | gateflow-ops / prayog-pe-team | Resolve which programmes this sign-in may enter; enter one granted programme | Current sign-in | Only grants of the signed-in identity; delivery only after enter | `platform_admin` sign-in does not become delivery. `tenant_admin` cannot enter a non-granted programme. `tenant_admin` does not receive the factory identity list. Programme is authorization, not a second login | `not granted`; `wrong actor` | **new** | unit + live verify |

Exact HTTP paths, JSON field names, and JWT claim encoding are **not** this
table — they belong to technical review (Q-1, Q-5). Logical operations and
field meaning above are the product contract.

## Non-functional requirements

| Area | Requirement or N/A rationale | Acceptance / evidence |
|------|------------------------------|-----------------------|
| Security | Only `platform_admin` performs identity and grant acts (REQ-22). Delivery stays `tenant_admin` (REQ-23). Password is never shown after set (REQ-30). Suspend and password-set end the prior sign-in (REQ-12, REQ-14). JWT-only product edge (ADR-014) remains; GitHub PAT is never a caller Bearer (INIT-014 REQ-07) | unit + live verify |
| Reliability | Membership change must not cancel in-flight waves (REQ-15). Enter/grant/detach either take effect or refuse with a named reason; no half-created identity (REQ-02, REQ-08, REQ-28, REQ-29) | unit + live verify |
| Performance / capacity | N/A — lab-scale identity list; no programme volume target this INIT | inspection |
| Observability | Named refusal reasons listed above. Structured logs for identity/grant/suspend/password-set/sign-in using existing `get_logger()` / `self.logger` conventions; no password, password hash, or PAT in logs. `platform_admin` can inspect membership without a delivery screen (REQ-11) | unit + inspection |
| Privacy / data handling | Name and email are factory identity. Password is write-only after set (REQ-30). `tenant_admin` does not see other identities (REQ-26) | live verify / inspection |
| Migration / compatibility | 014 create+bind and 016 invite / historic handle-attach are not product paths (REQ-20, REQ-21). That 014 bind is deleted, not left as compatibility (Lock 5, OQ-01). Leftover bind rows wiped. Breaking; lab is not live | unit + live verify |
| Rollback / recovery | Unsuspend reverses suspend. Detach reverses grant. Password-set cannot restore the old password (`platform_admin` sets a new one). No delete-identity this INIT | inspection + unit |
| Operations / support | `platform_admin` enters humans and grants entry (Lock 15; console is ops). Support path for a locked-out `tenant_admin` is `platform_admin`-set password or unsuspend, not self-serve. Teaching/verify for attach/login use enter → grant → sign-in → enter-programme; they do not document 014 create+bind | live verify + `tests/README.md` |

## Assumptions

| ID | Assumption | Evidence | Owner | Status | Invalidated when |
|----|------------|----------|-------|--------|------------------|
| A-1 | Programme onboard from meta, catalogue parse/store/show, and `platform_admin` seeing that catalogue stay as they are except identity/grant | PRD A1; confirmed by inspection — `programme_admin_routes.py` / `ProgrammeService.validate_then_create` | PE | confirmed | This INIT is asked to redesign programme create |
| A-2 | One active wave per repo remains true and is not reopened here | PRD A2; INIT-012 concurrency as-built | PE | confirmed | Delivery concurrency is a different INIT |
| A-3 | Seeded `platform_admin` remains the only factory-admin creation path | PRD A3; `scripts/seed_platform_admin.py`; REQ-05 | PE | confirmed | Product adds “enter a `platform_admin`” |
| A-4 | Name is a display label, not unique | PRD A4; REQ-01, REQ-04, REQ-25 | PE | confirmed | Unique names are required (new REQ) |
| A-5 | At least one human will need a second programme before membership data is treated as production-precious (kill line) | PRD A5; REQ-09, REQ-17 | PE | confirmed | Product asks to ship ops identity screens on remaining 1:1 bind |
| A-6 | Enter-then-grant is acceptable `platform_admin` cost (extra step vs 014 one-call) | PRD A6; REQ-01, REQ-06 | PE | confirmed | `platform_admin` refuses the split — do not collapse grant back into create |
| A-7 | Historic `POST /api/v1/tenants/{tenant_id}/users` is the gateflow surface PRD means by “invite / historic handle-attach that cannot sign in” | PRD REQ-20; INIT-012 REQ-04; `tenant_routes.py` `attach_tenant_user`; local 016 spec | PE | confirmed | A different invite door is discovered in this repo |
| A-8 | Existing 014 programme wipe remains the wipe act; a wiped programme is thereafter unknown (REQ-28), so grants cannot authorize enter | PRD Lock 13 / non-goal; INIT-014 REQ-35 / REQ-46 | PE | confirmed | Product requires an explicit grant-cascade wipe REQ beyond “unknown programme” |

## Spec questions (ambiguities — need PM or domain confirmation before feasibility)

| ID | Lane | Question | Owner | Blocking | Required by | Default if deferred | Status | Resolution link |
|----|------|----------|-------|----------|-------------|---------------------|--------|-----------------|
| Q-1 | PE | Session vs 014 programme-bound JWT: one sign-in then **enter** a granted programme (CTR-03/04) vs minting a per-programme token. ADR-014 revisit trigger is finer binding than role + a single programme | PE | no | technical review | Product: one identity sign-in; programme is authorization, not a second login (written into REQ-16). Schema / claim encoding / successor ADR is engineering | open | Impact map IM-01; ADR-014 revisit |
| Q-2 | PE | Wave split: gateflow API waves vs gateflow-ops console waves, given kill line (no identity screens on 1:1 bind) | PE | no | spec-implementation-plan | Sequential: gateflow enter+grant live, then ops screens | open | Impact map IM-03 |
| Q-3 | PM | After this INIT is promoted, 016’s invite stories in `prd/INIT-GATEFLOW-016.md` need a document update | PM | no | later (prayog-meta `/update-documents`) | Track as follow-on; 017 product truth is “no invite” (REQ-20) | open | PRD OQ-02 |
| Q-4 | PM | After this INIT is promoted, 014’s create+bind (REQ-15) and programme-bound JWT (REQ-06, REQ-31) in `prd/INIT-GATEFLOW-014.md` need a document update | PM | no | later (prayog-meta `/update-documents`) | Track as follow-on; 017 product truth is REQ-21 / REQ-09 / REQ-16; no dual model | open | PRD OQ-04 |
| Q-5 | PE | Exact HTTP paths and JSON field names for CTR-01–04 (PRD contracts are semantic) | PE | no | technical review / OpenAPI | Logical operations and field meaning in the contract table stay normative; paths/keys deferred | open | pending |
| Q-6 | PE | INIT-GATEFLOW-016 invite (CAP-A) vs 017 REQ-20 — 016 PRD is merged; ops must not ship invite | PE | no | Before ops W0 identity screens | 017 wins; do not ship invite | open | Impact map IM-02 |

PRD OQ-01 (leftover bind rows) and OQ-03 (seeded `platform_admin` not grantable)
are **resolved into REQ-21 and REQ-05** using the PRD defaults; they are not
open spec questions.

## Draft check summary (D1–D12)

| Check | Status | Evidence / findings |
|-------|--------|---------------------|
| D1 Approved handoff current | PASS | Meta PR [#42](https://github.com/drivestream-lab/prayog-meta/pull/42) head `601b00e0a74510a6af1c33bc80ca27260995c094` = tech-lead APPROVED review `commit_id` ([review](https://github.com/drivestream-lab/prayog-meta/pull/42#pullrequestreview-4927360675)); label `impact-map-lgtm`; H1 PRD digest matches (`sha256:c0fe55040928a13976133edde5cf71f0524815c17c0a8de79173ed3fa0657f67`, verified via `shasum -a 256` of the file at that SHA); H3 revision 1; H2 gateflow affected `sha256:3d39ee6d5947bcd18c3e0b46de16709b3fdddeefeb0e8d5bbae8ecf98b1e5834`; not deferred/blocked |
| D2 Complete PRD traceability | PASS | CAP-01…06 map to REQ-01…30 1:1 with the PRD; every REQ row cites PRD REQ/CAP/Lock/OQ/IM ids |
| D3 Repo-bounded scope | PASS | Matches H2 payload exactly; `gateflow-ops` is the consumer (out of this file's REQ ownership); `prayog-skills` / `launchpad` / `prayog-meta` not affected for delivery |
| D4 Observable acceptance | PASS | Each REQ states condition/event, observable result, evidence layer; architecture (routes, JWT claims, successor ADR) deferred to Q-1/Q-5, not decided in REQ rows |
| D5 Negative/failure paths | PASS | PRD §7 rows plus invalid credentials, missing JWT, grant-of-seed-admin, and password-set-kills-session, each with why-it-matters |
| D6 Assumptions/questions | PASS | A-1…A-8 (A-1…A-6 from PRD; A-7/A-8 from source inspection); Q-1…Q-6 all non-blocking with explicit defaults; OQ-01/OQ-03 written into REQ-21/REQ-05 |
| D7 Cross-repository contracts | PASS | CTR-01–04 semantic (logical operations); transport/module realization deferred; contract-test location planned under `tests/verify/` |
| D8 NFR applicability | PASS | All 8 areas specified or N/A with reason |
| D9 As-built alignment | PASS | Overview as-built table distinguishes existing (onboard, seed, JWT edge), changed (login identifier, 1:1 JWT bind), deleted (create+bind), purged (handle-attach), and new (factory list, grant/detach, suspend) |
| D10 Dependency order | PASS | Matches impact map §7: gateflow (this spec, CTR-01–04 provider) → gateflow-ops (consumer). Kill line: do not ship ops identity screens while 014 create+bind still creates membership |
| D11 Zero unresolved blockers | PASS | No blocking PM/PE/domain question; material OQ-01/OQ-03 defaults written into REQs; Q-1…Q-6 non-blocking |
| D12 Output completeness | PASS | Header H4, all required tables, check summary, selected workflow outcome, PR readiness handoff, and dev-review checklist present with no placeholders presented as fact |

**Draft verdict:** PASS

**Selected workflow outcome:** `pass`
**Outcome reason:** D1–D12 PASS; Gate 1 approved on current meta PR head; PRD digest verified byte-for-byte; zero unresolved material questions after the clarification loop (OQ-01/OQ-03 defaults written into REQ-21/REQ-05; Q-1…Q-6 non-blocking with recorded defaults).

Do not advance to `/initiative-feasibility` unless the workflow outcome is
`pass`, the draft verdict is PASS, and the developer review below is complete.

## PR readiness handoff

| Item | Value |
|------|-------|
| Workflow outcome | `pass` — Gate 1 current; full traceability; no material blockers |
| Verdict | PR READY |
| Existing spec PR | none |
| Proposed branch | `chore/INIT-GATEFLOW-017-spec-gateflow` |
| Proposed base | `develop` |
| Proposed title | `[INIT-GATEFLOW-017] Spec — One human, many programmes, one login (gateflow)` |
| PR type | **Draft** (entire spec lifecycle) |
| Local artifacts to publish | `docs/specification/product/INIT-GATEFLOW-017-gateflow.md`; `docs/specification/README.md` if listing this INIT as active |
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

INIT-GATEFLOW-017 — One human, many programmes, one login (gateflow only)

## Meta handoff

- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/42
- Approved meta head: `601b00e0a74510a6af1c33bc80ca27260995c094`
- Impact-map revision: 1
- PRD digest: `sha256:c0fe55040928a13976133edde5cf71f0524815c17c0a8de79173ed3fa0657f67`
- Repo scope digest: `sha256:3d39ee6d5947bcd18c3e0b46de16709b3fdddeefeb0e8d5bbae8ecf98b1e5834`

## Spec path

`docs/specification/product/INIT-GATEFLOW-017-gateflow.md`

## Summary

- CAP-01…06 / REQ-01…30: enter-then-grant identity APIs; many programme grants; suspend/password; one sign-in then enter a granted programme; delete 014 create+bind; purge historic handle-attach
- Provider of CTR-01–04; `gateflow-ops` is the consumer (out of this repo)
- Open engineering questions: Q-1…Q-6 (non-blocking; defaults documented). OQ-01/OQ-03 defaults written into REQ-21/REQ-05

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

- PRD: `prayog-meta/prd/INIT-GATEFLOW-017.md` @ meta PR [#42](https://github.com/drivestream-lab/prayog-meta/pull/42)
- Outline: `prayog-meta/prd/INIT-GATEFLOW-017-outline.md`
- Impact map: `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-017.md` revision 1
- Predecessor (deleted door): [`INIT-GATEFLOW-014-gateflow.md`](INIT-GATEFLOW-014-gateflow.md) REQ-06 / REQ-15 / REQ-47
- Historic handle-attach (purged): [`INIT-GATEFLOW-012-gateflow.md`](INIT-GATEFLOW-012-gateflow.md) `POST /tenants/{id}/users`
- Local pre-Gate-1 016 (invite not product truth): [`INIT-GATEFLOW-016-gateflow.md`](INIT-GATEFLOW-016-gateflow.md)
- As-built: `docs/specification/as-built/implementation-status.md`
- Source grounding: `src/business_services/programme_service.py` (`attach_tenant_admin`), `src/business_services/auth_identity_service.py`, `src/models/auth_models.py`, `src/api/v1/programme_admin_routes.py`, `src/api/v1/tenant_routes.py` (`attach_tenant_user`), `src/database/postgres/schema/user_identity_schema.py`

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-draft
  outcome: pass
  artifact:
    path: docs/specification/product/INIT-GATEFLOW-017-gateflow.md
  blockers: []
  signals:
    pr_ready: true
    initiative: INIT-GATEFLOW-017
    meta_pr: "https://github.com/drivestream-lab/prayog-meta/pull/42"
    meta_pr_head: "601b00e0a74510a6af1c33bc80ca27260995c094"
    map_revision: 1
    prd_digest: "sha256:c0fe55040928a13976133edde5cf71f0524815c17c0a8de79173ed3fa0657f67"
    scope_digest: "sha256:3d39ee6d5947bcd18c3e0b46de16709b3fdddeefeb0e8d5bbae8ecf98b1e5834"
    d_checks: pass
    nonblocking_questions: "Q-1,Q-2,Q-3,Q-4,Q-5,Q-6"
    codegraph_provider: mcp-user-prayog-fleet-cbm
    grounding_depth: deep
  next_candidates:
    - spec-pr-action
  human_checkpoint: false
  external_action: true
  forge:
    action: open_draft_pr
    draft: true
    apply_labels:
      - spec-pending
    title: "[INIT-GATEFLOW-017] Spec — One human, many programmes, one login (gateflow)"
    body_path: docs/specification/product/INIT-GATEFLOW-017-gateflow.md
```

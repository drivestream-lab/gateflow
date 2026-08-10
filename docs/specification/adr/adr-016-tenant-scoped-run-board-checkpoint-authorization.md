# ADR-016 — Tenant-scoped run, board, and checkpoint authorization

| Field | Value |
|-------|-------|
| Status | Accepted |
| Initiative | INIT-GATEFLOW-014 |
| Feasibility finding | N/A — originates from spec Q-4 (engineering data-model question, not a feasibility `NEW-ADR` Finding); promoted to `ADR_REQUIRED` at technical review per the ADR qualification rubric |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-014.md` |
| Source spec | `docs/specification/product/INIT-GATEFLOW-014-gateflow.md` |
| Source spec digest | `sha256:ba84792a5372ace145280aaa09730de368e5500f87c9cab4b6c6d7284e3258df` |
| product_constraints | `[REQ-23, REQ-24, REQ-31]` |
| changes_user_visible_behavior | `false` |
| spec_amendment_required | `false` |
| supersedes | none |
| superseded_by | none |
| Decision owner | @nikd10x |
| Approval evidence | Explicit PE acceptance by @nikd10x on 2026-08-10 via Cursor chat, Draft spec PR [#212](https://github.com/drivestream-lab/gateflow/pull/212) |
| Approved head | `ae67a38cf79de838ed2f80cbb46b2efaca4888ab` |
| Lint evidence | adr_boundary_lint.py 1/1, PASS, sha256:e68a20da519bfc1647f917407fe2e891162b8e9964c77ae47e12f1233eef5439 |

> If `changes_user_visible_behavior` or `spec_amendment_required` would be
> `true`, **stop**: amend and re-approve the product spec before this ADR may
> become Accepted. Do not invent scope, UX, acceptance, priority, or business
> rules here.

## Product decisions excluded

- See REQ-23, REQ-24, REQ-31.

## Context

`RunSchema`, board-ticket, and checkpoint records carry no tenant/programme
identifier today; reads and writes filter only by `org`/`repo`/`initiative_id`.
REQ-24 and REQ-31 require authorizing a caller's scope against these records,
needing a durable attribution path. `TenantRepoSchema` already keys
`org`+`repo` to a `tenant_id`, and `Tenant` is the binding target REQ-23
authorizes against; Programme is one further join from Tenant. REQ-35's
cutover wipe (PM-confirmed as a full pre-INIT data reset, not an in-place
migration over live rows) means no row predating this column exists at
introduction — the attribution path only needs to cover rows created from
this INIT forward. Duplicating a scoping column on every table is avoidable
if one table becomes the attribution root the others join through.

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Add `programme_id` to `RunSchema`, board-ticket, and checkpoint tables independently | No joins at read time | Three columns; duplicates an attribution fact derivable elsewhere |
| B — Runtime-only join through `TenantRepoSchema` (org+repo → tenant_id), no schema change | No migration | Recomputed per call; not durable if a repo's tenant registration later changes |
| C — Add `tenant_id` to `RunSchema` only; dependent records derive it through an existing `run_id` link | One new column; reuses an existing FK; durable | Records without a `run_id` link need a documented fallback |

## Recommendation

**Option C.** `RunSchema` gains a required `tenant_id` column set at run
creation from the JWT-bound tenant (REQ-23). Board-ticket and checkpoint
records that reference a `run_id` derive tenant, and Programme one join
further, through that link, rather than a duplicate scoping column — this
join is the attribution mechanism the REQ-24/REQ-31 constraint set binds.

## Consequences

- `RunSchema` requires a new, **non-nullable** `tenant_id` foreign-key
  column — a human-owned Alembic revision per `database-migrations.mdc`,
  introduced against an already-reset database (REQ-35 cutover), so no
  nullable/backfill path is needed.
- Board-ticket or checkpoint shapes with no existing `run_id` link need a
  documented fallback in the implementation plan, not an assumed one.

## Revisit triggers

- A single repo becomes shareable across more than one tenant, invalidating
  org+repo as a stable tenant-attribution key.
- A board ticket or checkpoint record is created with no `run_id` link,
  requiring its own scoping column after all.
- A future initiative needs to import or migrate historical rows from a
  prior deployment, reopening the nullable/backfill question this record
  avoided by assuming a reset database at introduction.

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
product_constraints: [REQ-23, REQ-24, REQ-31]
changes_user_visible_behavior: false
spec_amendment_required: false
Lint evidence: adr_boundary_lint.py {sources_checked}/{N expected}, PASS,
  sha256:{hex}
```

`Lint evidence` must match this exact shape — `adr_boundary_lint.py N/M,
PASS|FAIL, sha256:<hex>` — presence alone (`yes`, `TBD`, `-`) fails the
shape check and is rejected. Generate the line with:

```bash
python scripts/adr_boundary_lint.py {this file} --strict \
  --source-text <req_text_file> --source-text <feasibility_evidence_file> \
  --approved-req-id <every approved REQ-* in the spec> \
  --finding-text-file <feasibility_finding_file> \
  --print-evidence
```

and paste the printed line verbatim — do not hand-write the hash.

The formal PE GitHub Approve must be on the final commit containing this
Accepted metadata. No file changes occur after that approval (publish via
Forge `/commit-workspace` — not inside content skills).

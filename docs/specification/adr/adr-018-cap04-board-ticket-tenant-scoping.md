# ADR-018 — CAP-04 board/EPIC-ticket tenant scoping

| Field | Value |
|-------|-------|
| Status | Draft |
| Initiative | INIT-GATEFLOW-015 |
| Feasibility finding | FF-02 |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-015.md` |
| Source spec | `docs/specification/product/INIT-GATEFLOW-015-gateflow.md` |
| Source spec digest | `sha256:17579cbe26dcba3eeaf6fa6512480c9e485141deb663ed805387055fe2e97d36` |
| product_constraints | `[REQ-20, REQ-21, REQ-23]` |
| changes_user_visible_behavior | `false` |
| spec_amendment_required | `false` |
| supersedes | none |
| superseded_by | none |
| Decision owner | PE |
| Approval evidence | Pending |
| Approved head | Pending |

## Product decisions excluded

- See REQ-20, REQ-21, REQ-23.

## Context

ADR-016 Option C attributes tenant scope through a record's `run_id` link.
`BoardTicketResource` — the EPIC/Feature read projection
`InitiativeReadoutService` composes against for REQ-20/REQ-21 — carries no
`run_id` and no `tenant_id`; it is a GitHub-derived projection, not a
Gateflow-owned table. An EPIC ticket can exist with zero runs, which REQ-23's
tenant-scoping constraint must still cover. ADR-016's own revisit trigger #2
("a board ticket... record is created with no `run_id` link, requiring its
own scoping column after all") is the exact case this finding concerns.

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Reuse the existing org+repo → `tenant_id` lookup (`TenantRepository.find_workspace_credential_by_org_repo`, already fail-closed on ambiguous registration) as a read-time classification | Already implemented and tested; no new table; keeps the approved denominator intact | Second tenant-attribution mechanism now exists alongside ADR-016 Option C, scoped to reads only |
| B — Narrow the composition's denominator to records that already carry a `run_id` | Zero new join logic; ADR-016 Option C alone suffices | Forecloses on approved REQ-21 scope — not evaluated as a live option here |
| C — Add a durable `tenant_id` column to a Gateflow-owned board-ticket table | Matches ADR-016's column pattern | No such table exists; nothing to persist a column on |

## Recommendation

**Option A**, satisfying REQ-20/REQ-21/REQ-23 without amending their scope.
`TenantRepository.find_workspace_credential_by_org_repo` already performs
this exact org+repo → tenant lookup and already fails closed on the
multi-tenant ambiguity ADR-016 named when it rejected this mechanism for
**durable write attribution**. Reusing it as a **read-time** classification
for one composition does not reopen that durability concern — no row is
written using it — and keeps the composition's scope intact.

## Consequences

- CAP-04's composition depends on two tenant-attribution mechanisms (ADR-016
  `run_id` join for run-bearing records; this ADR's org+repo lookup for
  run-less EPIC tickets) rather than one.
- Inherits ADR-016's own trigger risk: a repo shared across tenants breaks
  org+repo as a stable key here too, not only for ADR-016's write path.

## Revisit triggers

- A repo becomes registered under more than one tenant (same trigger ADR-016
  already names) — both mechanisms need reconciling together.
- A Gateflow-owned board-ticket store is introduced for other reasons,
  making Option C viable and preferable to two coexisting mechanisms.

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
product_constraints: [REQ-20, REQ-21, REQ-23]
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

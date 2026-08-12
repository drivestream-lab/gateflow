# ADR-017 — Wave lane attribution for metrics grouping

| Field | Value |
|-------|-------|
| Status | Accepted |
| Initiative | INIT-GATEFLOW-015 |
| Feasibility finding | FF-01 |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-015.md` |
| Source spec | `docs/specification/product/INIT-GATEFLOW-015-gateflow.md` |
| Source spec digest | `sha256:17579cbe26dcba3eeaf6fa6512480c9e485141deb663ed805387055fe2e97d36` |
| product_constraints | `[REQ-16]` |
| changes_user_visible_behavior | `false` |
| spec_amendment_required | `false` |
| supersedes | none |
| superseded_by | none |
| Decision owner | @nikd10x |
| Approval evidence | Explicit PE acceptance by @nikd10x on 2026-08-12 via Cursor chat, Draft spec PR [#228](https://github.com/drivestream-lab/gateflow/pull/228) |
| Approved head | `4505eabf5e09a1409065d8067c26bd0608e505b6` |
| Lint evidence | adr_boundary_lint.py 2/2, PASS, sha256:71f8bbc5c40019519d9059341e9e28aebb1217e894c6c2b3d275c7b802da722a |

## Product decisions excluded

- See REQ-16.

## Context

`LaneType` (spec/implement/closeout) is resolved at wave-start and threaded
into the async job's payload dict, but no lane-equivalent value is persisted
on `RunSchema`, `StageSchema`, or `RunEventSchema`. No durable column or
JSONB field exists to hold the grouping dimension REQ-16 requires today.

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Add a `lane` column to `RunSchema`, set from the job payload at run creation | Indexed, first-class query column | New non-nullable-or-backfilled column; human Alembic revision gates delivery |
| B — Derive a classification heuristically from unrelated already-persisted fields (e.g. non-null `meta_pr_url` implying the spec path) | No schema change | Closeout runs have no comparably reliable field, producing an undocumented-until-observed misclassification rate |
| C — Persist the lane value into the existing JSONB `payload` on `stage_completed`/`run_stopped` events, at the same call sites already being touched for REQ-01's outcome-vocabulary fix | No new column, no human Alembic; `payload` is already in scope holding the job's lane value at those exact call sites; matches the established `runner`/`model_id`/`stop_reason` payload-field precedent | Not a first-class indexed column; a query must scan/aggregate over JSONB |

## Recommendation

**Option C**, satisfying REQ-16. The call sites that already need to change
this initiative (`record_stage_duration` / `append_event` for
`stage_completed`, and `_finalize_run`'s `run_stopped` append) already hold
the job payload the lane value lives in, and JSONB payload fields are the
established pattern for this kind of per-event dimension. This avoids a
schema migration purely for a grouping dimension while the outcome-vocabulary
work already reopens the same write path.

## Consequences

- Lane becomes an additional queryable JSONB field, not an indexed column —
  acceptable at current read-volume; no migration on the critical path.
- A future feature needing indexed/filterable lane queries at larger scale
  would still need a schema promotion later (Option A), a known, named
  follow-up rather than a blocker now.

## Revisit triggers

- Query performance at scale requires an indexed `lane` column instead of a
  JSONB scan.
- A second feature independently needs lane as a first-class column,
  amortizing the migration cost across two consumers instead of one.

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
product_constraints: [REQ-16]
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

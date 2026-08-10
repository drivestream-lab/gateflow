# ADR-015 — Programme-scoped forge credential resolution

| Field | Value |
|-------|-------|
| Status | Accepted |
| Initiative | INIT-GATEFLOW-014 |
| Feasibility finding | FF-02 (`Initiative-Feasibility-Report-INIT-GATEFLOW-014.md`) |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-014.md` |
| Source spec | `docs/specification/product/INIT-GATEFLOW-014-gateflow.md` |
| Source spec digest | `sha256:ba84792a5372ace145280aaa09730de368e5500f87c9cab4b6c6d7284e3258df` |
| product_constraints | `[REQ-11, REQ-14, REQ-25]` |
| changes_user_visible_behavior | `false` |
| spec_amendment_required | `false` |
| supersedes | `ADR-003 (forge-credential clause only — infra/business layer split unaffected)` |
| superseded_by | none |
| Decision owner | @nikd10x |
| Approval evidence | Explicit PE acceptance by @nikd10x on 2026-08-10 via Cursor chat, Draft spec PR [#212](https://github.com/drivestream-lab/gateflow/pull/212) |
| Approved head | Recorded at publish — see `/commit-workspace` result for the exact spec PR head containing this Accepted metadata |
| Lint evidence | adr_boundary_lint.py 2/2, PASS, sha256:275d49b933484ffe0dc7dc273c5c6ad9a84374802f4b76b4b2ad17e4aee8e377 |

> If `changes_user_visible_behavior` or `spec_amendment_required` would be
> `true`, **stop**: amend and re-approve the product spec before this ADR may
> become Accepted. Do not invent scope, UX, acceptance, priority, or business
> rules here.

## Product decisions excluded

- See REQ-11, REQ-14, REQ-25.

## Context

`ForgeClient` is a DI singleton constructed once at process `initialize()`;
its `AppInstallationTokenProvider` collaborator hard-fails unless exactly one
App installation exists (ADR-003). A credential resolved once per process
cannot satisfy REQ-25's per-programme scoping. REQ-14 keeps GitHub App
runtime activation out of scope, and REQ-11 requires the Programme's own
stored PAT as the runtime credential — a resolution mechanism is needed that
does not reopen App-installation multiplicity.

## Options considered

Multi-installation GitHub App (one install per programme) is **not** a live
option — REQ-14 keeps GitHub App runtime activation out of scope this
initiative regardless of engineering preference. The open question is
construction mechanism only, given PAT is the fixed credential type:

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Resolve PAT inline at each `ForgeClient` call site | Fewest new types | Duplicated at every call site; no single seam to test |
| B — Programme PAT as an explicit per-call parameter on existing methods | No new construction type | Every method signature changes; leaks credential handling into business call sites |
| C — `ForgeClient` construction becomes a per-programme factory keyed on Programme PAT, mirroring the existing `PostgresSessionFactory` Protocol pattern | Reuses an established precedent; keeps `ForgeClient` an infra type; one seam to test | Replaces a bound singleton with a provider constructed per programme |

## Recommendation

**Option C.** A `ForgeClientFactory` (infra) resolves a `ForgeClient` instance
per Programme, constructed with that Programme's stored PAT as the Bearer
source — replacing `AppInstallationTokenProvider`/`PatTokenProvider`'s
single, process-global token resolution for programme-scoped forge/git
operations. `ForgeClient` remains an infra type per ADR-003's layer split;
only its construction lifecycle changes from a DI singleton to a
factory-resolved, per-programme instance.

## Consequences

- The single-App-installation constraint no longer applies to programme-scoped
  forge/git calls; App-mode token resolution becomes unused for this path
  (code may remain dormant pending a later App-activation initiative).
- `ForgeClient`'s DI registration changes from a bound singleton to a
  provider invoked with a Programme identifier.
- Programme PAT-in-production is the runtime credential for programme-scoped
  forge/git; the spec's Security NFR already accepts plaintext PAT storage
  with no non-production carve-out — no new risk class beyond REQ-11/REQ-14.

## Revisit triggers

- A later initiative activates GitHub App runtime credentials per programme,
  superseding the PAT-only resolution this record establishes.
- A programme-scoped forge/git call needs to run outside any Programme
  context (no such call is known to exist today).

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
product_constraints: [REQ-11, REQ-14, REQ-25]
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

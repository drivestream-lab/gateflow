# Ground report — INIT-GATEFLOW-013 W0

| Field | Value |
|-------|-------|
| Wave | W0 — Connect programme + catalogue discovery |
| Spec | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` |
| Initiative | INIT-GATEFLOW-013 |
| Date | 2026-08-09 |
| Wave head (exact) | `feature/INIT-GATEFLOW-013-w0-programme-connect` @ `4b9bd696c2bad987ace5640e975d5f61fc11abcb` — reviewed head for sign-off |
| PR URL | https://github.com/drivestream-lab/gateflow/pull/205 |
| Status | Ready for wave-signoff |
| Review deadline | 2026-08-11 |
| Deciders | Tech lead / reviewer — merge at wave-signoff (human only) |
| Outcome | pass |
| Outcome reason | All W0-assigned REQs mapped to artifacts; wave-accepted on tip; Contracts produced complete; no Blocking GF-* |
| Assigned REQs | REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, REQ-28 |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution-INIT-GATEFLOW-013-W0 | 473 passed (2026-08-09); catalogue/onboarding/git-ref units |
| Ground | manual `src/` + `tests/**` scan (`ground_command` N/A) | Entry points and fail-closed paths present |
| Accept | `wave-accepted` on tip of PR #205 @ `4b9bd69` | Human approved at wave-acceptance |

## Automated ground check output

N/A — no Makefile `ground_command`. Manual scan of wave-assigned entry points and tests documented in REQ checklist below.

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-01 | Connect clones/syncs programme meta via existing git client | `ProgrammeOnboardingService.connect_programme` → `TenantGitWorkspaceClient.resolve_workspace`; optional `ref` | pass |
| REQ-02 | Connect uses existing tenant auth | `verify_tenant_bearer_token` on programme routes; no new credential type | pass |
| REQ-03 | No separate programme credential | Connect uses `get_tenant_workspace_auth` (tenant PAT); no new credential fields in models | pass |
| REQ-04 | Connect fail-closed; named reason; no partial retain | `TenantGitWorkspaceError` → 422 `details.reason`; rmtree on failed new clone; unit `test_connect_git_failure_*` | pass |
| REQ-05 | Catalogue candidates from synced records | `GET …/programme/catalogue` → `parse_candidates`; unit + verify FILE | pass |
| REQ-06 | Malformed catalogue rejected; no partial list | `CatalogueParseError` named reasons; `test_catalogue_parser` | pass |
| REQ-07 | Catalogue reflects latest sync (not frozen at first connect) | Parser reads current checkout path; reconnect updates `last_synced_at` via upsert; full refresh API is W4 | pass (W0 path; W4 completes refresh surface) |
| REQ-28 | Exactly one programme connection (upsert) | `uq_tenant_programme_connections_tenant_id` + `upsert_programme_connection`; verify reconnect path | pass |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Catalogue YAML is discovery-input, not GATEFLOW_* knobs | ADR-012 Accepted | pass |
| Models only in `src/models/`; routes import models | pydantic-schemas / architecture | pass |
| ORM confined to schema/repo | repository-pattern | pass |
| No agent writes under `postgres_migrations/versions/` | database-migrations; DDL note only | pass |
| Tenant bearer zone for new routes | ADR-011 | pass |
| Workspace layout reuse | ADR-010; same `{root}/{org}/{repo}` | pass |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| `TenantGitWorkspaceClient.resolve_workspace` | INIT-012 W1 as-built / live code | yes — extended with optional `ref` |
| Tenant bearer + path `tenant_id` match | ADR-011 / tenant routes | yes |
| Tenant PAT + absolute `workspace_root` | INIT-012 W0 registry | yes |

## Discrepancies (must fix before human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|---------|
| — | — | none | — |

## Learning cited

| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| — | — | Learning-Extract has `items: []` (no human_fix) — nothing to cite |

## Contracts produced by this wave

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Programme connection row | repository + ORM | upsert/get by tenant_id | tenant_id, org, repo, optional ref, last_synced_at | connection DTO (no PAT) | Exactly one row per tenant | W1 select |
| Programme connect API | programme routes / onboarding service | PUT `/api/v1/tenants/{tenant_id}/programme/connect` | bearer + body org/repo/optional ref | connection record | Fail-closed git; upsert not second row | W1 |
| Programme connection read | same | GET `…/programme/connection` | bearer + tenant_id | connection DTO | 422 if not connected | W1–W4 |
| Catalogue parse | `engine/catalogue_parser` | `parse_candidates(meta_root, org=)` | absolute synced meta tree + org | list of candidates or named parse error | No partial list; ADR-012 discovery-input | W1 select validation |
| Catalogue API | programme routes | GET `…/programme/catalogue` | bearer + tenant_id | programme_org + candidates | Requires connection; fail-closed parse | W1 |
| Git resolve + optional ref | TenantGitWorkspaceClient | `resolve_workspace(credential, *, ref=)` | credential + optional ref | workspace path + clone\|fetch mode | Default branch unchanged when ref omitted | W2 setup |

## Exact-head merge package (for wave-signoff)

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/205 @ `4b9bd696c2bad987ace5640e975d5f61fc11abcb`
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-013-W0.md`
- Accept evidence: `wave-accepted` on tip (wave-acceptance) — human approved already
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-013-W0.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-013-W0.md`
- As-built: W0 recorded `human_approved` from wave-acceptance (evidence tip + label)
- Required merge fields (human fills at `wave-signoff`): `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [ ] Review REQ checklist — all wave-assigned REQs pass or explicitly deferred
- [ ] Review §Contracts produced — accurate for W1 `/pre-implement`
- [ ] Confirm reviewed head SHA matches `4b9bd696c2bad987ace5640e975d5f61fc11abcb` (or newer tip if hotfixed)
- [ ] Confirm human_approved already from wave-acceptance
- [ ] Merge the wave PR manually at wave-signoff — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge

## Ready for wave-signoff (merge)?

yes — G1–G10 satisfied; no Blocking GF-*; Contracts produced complete

## Check summary (G1–G10)

| Check | Status |
|-------|--------|
| G1 Wave scope | PASS — W0 REQs only |
| G2 Ground evidence | PASS — manual scan; ground_command N/A |
| G3 Assigned-REQ coverage | PASS |
| G4 Acceptance evidence | PASS — wave-accepted on tip |
| G5 ADR boundaries | PASS |
| G6 MDC boundaries | PASS |
| G7 Contracts consumed/produced | PASS |
| G8 Learning citations | PASS — empty extract cited |
| G9 GF-* findings | PASS — none |
| G10 Complete handoff | PASS |

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-013-W0.md
  blockers: []
  signals:
    wave: W0
    contracts_produced: 6
    assigned_reqs: [REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, REQ-28]
    reviewed_head_sha: 4b9bd696c2bad987ace5640e975d5f61fc11abcb
    pr_url: https://github.com/drivestream-lab/gateflow/pull/205
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "200"
    status: done
    commit_workspace:
      action: commit_workspace
      head_ref: feature/INIT-GATEFLOW-013-w0-programme-connect
```

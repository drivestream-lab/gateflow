# Ground report — INIT-GATEFLOW-013 W4

| Field | Value |
|-------|-------|
| Wave | W4 — Catalogue refresh |
| Spec | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` |
| Initiative | INIT-GATEFLOW-013 |
| Date | 2026-08-10 |
| Wave head (exact) | `feature/INIT-GATEFLOW-013-w4-catalogue-refresh` @ `670799edbdac4977db77a8d32ded722a08b64c20` — reviewed head for sign-off (Pass-1 tip at `wave-accepted`) |
| PR URL | https://github.com/drivestream-lab/gateflow/pull/209 |
| Status | Ready for wave-signoff |
| Review deadline | 2026-08-12 |
| Deciders | Tech lead / reviewer — merge at wave-signoff (human only) |
| Outcome | pass |
| Outcome reason | All W4-assigned REQs mapped to artifacts; wave-accepted on tip; Contracts produced complete; no Blocking GF-* |
| Assigned REQs | REQ-07, REQ-24, REQ-25 |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution-INIT-GATEFLOW-013-W4 | 490 passed (2026-08-10); refresh success/fail/not-connected; membership writers not called |
| Ground | manual `src/` + `tests/**` scan (`ground_command` N/A) | `POST …/catalogue/refresh` → `refresh_catalogue` → `resolve_workspace` + upsert; no tenant_repos mutate |
| Accept | `wave-accepted` on tip of PR #209 @ `670799e` | Human approved at wave-acceptance |

## Automated ground check output

N/A — no Makefile `ground_command`. Manual scan of wave-assigned entry points and tests documented in REQ checklist below.

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-07 | Candidate list reflects most recently synced copy (not frozen at connect) | Refresh re-syncs meta then GET catalogue; verify asserts prior candidates still present / growth allowed; ADR-012 | pass |
| REQ-24 | Connected tenant can refresh programme shared records at any time | `POST …/programme/catalogue/refresh`; `refresh_catalogue`; bumps `last_synced_at` on success; git fail → named 422 without upsert | pass |
| REQ-25 | Refresh never changes already-selected repos — only what's newly available | No `list`/`add`/`remove` tenant_repos in refresh path; unit asserts writers not awaited; verify re-select → `already_selected` + same active set | pass |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Catalogue discovery from latest sync | ADR-012 Accepted | pass |
| Workspace path via existing git client | ADR-010 | pass |
| Tenant bearer on programme routes | ADR-011 | pass |
| On-demand only (no scheduler) | Spec Q-4 / plan W4 | pass |
| Models in `src/models/` only | pydantic-schemas | pass |
| Routes → business only | architecture / http-api-conventions | pass |
| Fail-fast named git reasons; IDs as log kwargs | fail-fast / logging-loguru | pass |
| Do not call status / sync_harness from refresh | Ground-Report W3 / ADR-013 out of mutate scope | pass |
| Co-shipped live verify | testing-verify-flows | pass |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Programme connection row + `last_synced_at` | Ground-Report W0 | yes — refresh upserts same org/repo/ref |
| Git resolve + optional ref | Ground-Report W0 | yes — `resolve_workspace(credential, ref=connection.ref)` |
| Catalogue parse + GET catalogue | Ground-Report W0 / ADR-012 | yes — post-refresh catalogue read |
| Active-list writers (must not call) | Ground-Report W1 | yes — refresh avoids membership APIs |
| Provenance / readiness untouched | Ground-Report W3 | yes — no status/filesystem evaluators on refresh |
| Tenant bearer zone | ADR-011 | yes |

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
| Catalogue refresh | ProgrammeOnboardingService + programme routes | `POST …/programme/catalogue/refresh` | tenant bearer; connected tenant; empty body | connection DTO with updated `last_synced_at` | Re-syncs stored org/repo/ref; no connect body required | initiative-closure / ops |
| Selections unchanged on refresh | `refresh_catalogue` | before/after membership | identical `tenant_repos` set | Never calls add/remove/list writers | initiative-closure |
| Fail-closed refresh | same | git / resolve error | 422 named reason | No upsert / no membership or readiness writes | initiative-closure |
| Catalogue reflects latest sync | GET `…/programme/catalogue` after refresh | — | candidates from re-synced tree | Prior candidates retained; growth allowed (REQ-07) | initiative-closure |

> Last eng wave for INIT-GATEFLOW-013 on gateflow — next programme hop is initiative closure (not W5 `/pre-implement`).

## Exact-head merge package (for wave-signoff)

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/209 — expected reviewed head `670799edbdac4977db77a8d32ded722a08b64c20` (+ Pass-2 docs tip after commit_workspace)
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-013-W4.md`
- Accept evidence: `wave-accepted` on tip (wave-acceptance) — human approved already
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-013-W4.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-013-W4.md`
- As-built: W4 recorded `human_approved` from wave-acceptance (evidence tip + label)
- Required merge fields (human fills at `wave-signoff`): `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [ ] Review REQ checklist — all wave-assigned REQs pass or explicitly deferred
- [ ] Review §Contracts produced — accurate for initiative-closure / ops consumers
- [ ] Confirm reviewed head SHA matches PR #209 tip at merge time
- [ ] Confirm human_approved already from wave-acceptance
- [ ] Merge the wave PR manually at wave-signoff — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge

## Ready for wave-signoff (merge)?

yes — G1–G10 satisfied; no Blocking GF-*; Contracts produced complete

## Check summary (G1–G10)

| Check | Status |
|-------|--------|
| G1 Wave scope | PASS — W4 REQs only (REQ-07, 24, 25) |
| G2 Ground evidence | PASS — manual scan; ground_command N/A |
| G3 Assigned-REQ coverage | PASS |
| G4 Acceptance evidence | PASS — wave-accepted on tip |
| G5 ADR boundaries | PASS — ADR-012/010/011 |
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
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-013-W4.md
  blockers: []
  signals:
    wave: W4
    contracts_produced: 4
    assigned_reqs: [REQ-07, REQ-24, REQ-25]
    reviewed_head_sha: 670799edbdac4977db77a8d32ded722a08b64c20
    pr_url: https://github.com/drivestream-lab/gateflow/pull/209
    last_eng_wave: true
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "204"
    status: done
    commit_workspace:
      action: commit_workspace
      head_ref: feature/INIT-GATEFLOW-013-w4-catalogue-refresh
```

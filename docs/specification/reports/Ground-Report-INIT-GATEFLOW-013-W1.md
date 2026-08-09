# Ground report — INIT-GATEFLOW-013 W1

| Field | Value |
|-------|-------|
| Wave | W1 — Select/deselect repos; retire repos[] |
| Spec | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` |
| Initiative | INIT-GATEFLOW-013 |
| Date | 2026-08-09 |
| Wave head (exact) | `feature/INIT-GATEFLOW-013-w1-repo-selection` @ `7d8fefc10a75a11e60a1ec764045d0f5e8114acf` — reviewed head for sign-off |
| PR URL | https://github.com/drivestream-lab/gateflow/pull/206 |
| Status | Ready for wave-signoff |
| Review deadline | 2026-08-11 |
| Deciders | Tech lead / reviewer — merge at wave-signoff (human only) |
| Outcome | pass |
| Outcome reason | All W1-assigned REQs mapped to artifacts; wave-accepted on tip; Contracts produced complete; no Blocking GF-* |
| Assigned REQs | REQ-08, REQ-09, REQ-10, REQ-11, REQ-12, REQ-13, REQ-26, REQ-27 |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution-INIT-GATEFLOW-013-W1 | 478 passed (2026-08-09); selection + registration units |
| Ground | manual `src/` + `tests/**` scan (`ground_command` N/A) | Select/deselect entry points, fail-closed reasons, registry reject present |
| Accept | `wave-accepted` on tip of PR #206 @ `7d8fefc` | Human approved at wave-acceptance |

## Automated ground check output

N/A — no Makefile `ground_command`. Manual scan of wave-assigned entry points and tests documented in REQ checklist below.

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-08 | Select and save subset of current candidates as active repos | `POST …/programme/repos/select` → `ProgrammeOnboardingService.select_repos` → `add_tenant_repos`; unit `test_select_admits_in_catalogue`; verify FILE | pass |
| REQ-09 | Out-of-catalogue select rejected; 0 active-list change | `details.reason=out_of_catalogue` before persist; `test_select_rejects_out_of_catalogue_zero_change`; verify asserts 422 | pass |
| REQ-10 | Re-selection validated against *current* catalogue | Select always `parse_candidates` on synced meta checkout (not frozen snapshot); already-selected skips probe | pass |
| REQ-11 | New select runs GithubPatProbe; failure rejects; 0 change | Probe loop on `new_admits` only; `probe_failed` 422; `test_select_probe_failure_zero_change` | pass |
| REQ-12 | Registration rejects non-empty `repos[]` | `TenantService.register_tenant` → 422 `repos_not_allowed`; `test_register_rejects_non_empty_repos`; verify_tenant_registry + verify_repo_selection | pass |
| REQ-13 | No alternate API admits `tenant_repos` after cutover | Registration creates `repos=[]`; only selection `add_tenant_repos` writes membership; PM-1 dependents updated to connect→select | pass |
| REQ-26 | Deselect changes membership only (clone/readiness not cleared via update) | `remove_tenant_repo` deletes membership row; no harness_verified write / no rmtree; `test_deselect_removes_membership` | pass |
| REQ-27 | Deselect blocked while ACTIVE run | `RunRepository.find_active_run` → 422 `active_run`; `test_deselect_blocked_by_active_run` | pass |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Catalogue remains discovery authority for select validation | ADR-012 Accepted | pass |
| Tenant bearer on select/deselect | ADR-011; `verify_tenant_bearer_token` | pass |
| Models only in `src/models/`; routes import models | pydantic-schemas / architecture | pass |
| ORM confined to repository | repository-pattern | pass |
| No agent writes under `postgres_migrations/versions/` | database-migrations | pass |
| Setup/status not required for admit (W2/W3) | plan W1 scope; `pending_setup` outcome | pass |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Programme connection required before select | Ground-Report W0 | yes — 422 `programme_not_connected` |
| Catalogue parse from synced meta | Ground-Report W0 / ADR-012 | yes — `parse_candidates` at select time |
| GithubPatProbe.verify_read_access | INIT-012 / W0 pre-implement | yes — reused at new admits |
| find_active_run(org, repo) | INIT-012 as-built | yes — deselect guard |
| Tenant bearer + path tenant_id | ADR-011 | yes |

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
| Registration without repos | tenant register API / TenantService | `POST /api/v1/tenants` | name, pat, workspace_root; `repos` absent or empty | tenant + empty repos + one-time bearer | Non-empty `repos` → 422 `repos_not_allowed`; 0 tenant_repos rows | W2+ |
| Select active list | programme onboarding / routes | `POST /api/v1/tenants/{tenant_id}/programme/repos/select` | bearer + `{repos:[{org,repo},…]}` | `results[]` + `active_repos` | ⊂ current catalogue; new admits PAT-probed; fail → 0 change; `pending_setup` until W2 | W2 setup wire |
| Deselect membership | same | `POST …/programme/repos/deselect` | bearer + `{org,repo}` | org/repo + updated `active_repos` | ACTIVE run → 422 `active_run`; membership row removed only | W2–W4 |
| Per-repo admit result | selection models | select response | batch | outcomes `pending_setup` \| `already_selected` (probe/out-of-catalogue via 422) | Setup/status outcomes reserved for W2/W3 | W2/W3 |
| Active-list writers | TenantRepository | `list_tenant_repos` / `add_tenant_repos` / `remove_tenant_repo` | tenant_id + refs | membership DTOs | Selection path only after REQ-13 | W2+ |

## Exact-head merge package (for wave-signoff)

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/206 — expected reviewed head `7d8fefc10a75a11e60a1ec764045d0f5e8114acf` (+ Pass-2 docs tip after commit_workspace)
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-013-W1.md`
- Accept evidence: `wave-accepted` on tip (wave-acceptance) — human approved already
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-013-W1.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-013-W1.md`
- As-built: W1 recorded `human_approved` from wave-acceptance (evidence tip + label)
- Required merge fields (human fills at `wave-signoff`): `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [ ] Review REQ checklist — all wave-assigned REQs pass or explicitly deferred
- [ ] Review §Contracts produced — accurate for W2 `/pre-implement`
- [ ] Confirm reviewed head SHA matches PR #206 tip at merge time
- [ ] Confirm human_approved already from wave-acceptance
- [ ] Merge the wave PR manually at wave-signoff — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge

## Ready for wave-signoff (merge)?

yes — G1–G10 satisfied; no Blocking GF-*; Contracts produced complete

## Check summary (G1–G10)

| Check | Status |
|-------|--------|
| G1 Wave scope | PASS — W1 REQs only |
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
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-013-W1.md
  blockers: []
  signals:
    wave: W1
    contracts_produced: 5
    assigned_reqs: [REQ-08, REQ-09, REQ-10, REQ-11, REQ-12, REQ-13, REQ-26, REQ-27]
    reviewed_head_sha: 7d8fefc10a75a11e60a1ec764045d0f5e8114acf
    pr_url: https://github.com/drivestream-lab/gateflow/pull/206
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "201"
    status: done
    commit_workspace:
      action: commit_workspace
      head_ref: feature/INIT-GATEFLOW-013-w1-repo-selection
```

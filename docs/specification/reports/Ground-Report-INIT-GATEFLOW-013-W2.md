# Ground report — INIT-GATEFLOW-013 W2

| Field | Value |
|-------|-------|
| Wave | W2 — Setup chosen repos (batch) |
| Spec | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` |
| Initiative | INIT-GATEFLOW-013 |
| Date | 2026-08-10 |
| Wave head (exact) | `feature/INIT-GATEFLOW-013-w2-repo-setup` @ `96be30fecf6a000fc77d232d879c8272a17f2856` — reviewed head for sign-off |
| PR URL | https://github.com/drivestream-lab/gateflow/pull/207 |
| Status | Ready for wave-signoff |
| Review deadline | 2026-08-12 |
| Deciders | Tech lead / reviewer — merge at wave-signoff (human only) |
| Outcome | pass |
| Outcome reason | All W2-assigned REQs mapped to artifacts; wave-accepted on tip; Contracts produced complete; no Blocking GF-* |
| Assigned REQs | REQ-14, REQ-15, REQ-16 |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution-INIT-GATEFLOW-013-W2 | 479 passed (2026-08-10); setup isolation + outcome shape |
| Ground | manual `src/` + `tests/**` scan (`ground_command` N/A) | select → resolve_workspace per new admit; ok/setup_failed; verify asserts checkout |
| Accept | `wave-accepted` on tip of PR #207 @ `96be30f` | Human approved at wave-acceptance |

## Automated ground check output

N/A — no Makefile `ground_command`. Manual scan of wave-assigned entry points and tests documented in REQ checklist below.

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-14 | Newly selected repos set up via same workspace mechanism | `select_repos` → `TenantGitWorkspaceClient.resolve_workspace` after admit; layout `{workspace_root}/{org}/{repo}`; unit admit→ok; verify asserts `.git` checkout | pass |
| REQ-15 | Setup failures isolated; peers proceed | Per-repo try/except `TenantGitWorkspaceError`; `test_select_setup_isolation_mixed_batch`; membership retained for failing peer | pass |
| REQ-16 | Per-repo setup result with specific failure reason | Outcomes `ok` / `setup_failed` (+ `reason`); `already_selected` skips setup; Wave-Execution + models | pass |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Workspace authority unchanged — no caller-supplied path / second git stack | ADR-010 Accepted | pass |
| Tenant bearer on select unchanged | ADR-011 | pass |
| Infra reuse `TenantGitWorkspaceClient` only | infra-services / plan TASK notes | pass |
| Models only in `src/models/` | pydantic-schemas | pass |
| Business orchestrates; no ORM in service | repository-pattern / architecture | pass |
| Fail-fast named reasons; IDs as log kwargs | fail-fast / logging-loguru | pass |
| No Launchpad status in this wave | plan W2 scope; ADR-013 deferred to W3 | pass |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Select admit + probe before setup | Ground-Report W1 | yes — probe/catalogue still all-or-nothing; setup after persist |
| Active-list writers `add_tenant_repos` / `list_tenant_repos` | Ground-Report W1 | yes — membership kept even if setup fails |
| `resolve_workspace` + `TenantGitWorkspaceError.reason` | Ground-Report W0 / ADR-010 | yes — reused per new admit |
| Tenant workspace auth (root + PAT) | Ground-Report W0/W1 | yes — credential for resolve |
| Programme connection required | Ground-Report W0/W1 | yes — unchanged |
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
| Setup-on-select batch | ProgrammeOnboardingService | `select_repos` (same HTTP select) | newly admitted `{org,repo}` after probe/admit | per-repo `ok` or `setup_failed` + named reason | Peers independent; one setup fail does not roll back other admits or block peers | W3 status |
| Workspace layout on success | TenantGitWorkspaceClient | `resolve_workspace(credential)` | tenant PAT + workspace_root + org/repo | path present under `{root}/{org}/{repo}` | ADR-010 layout; partial clone cleaned on failure when path did not exist before | W3+ |
| Select response setup outcomes | programme_selection_models | `ProgrammeSelectResponse.results[]` | batch | `ok` \| `already_selected` \| `setup_failed` | `already_selected` skips resolve; probe/out-of-catalogue remain 422 before admit | W3 may add status outcomes |
| Admit retained on setup fail | select + tenant_repos | after `add_tenant_repos` | setup error | membership still listed in `active_repos` | Partial success (D5); status evaluator (W3) must not assume checkout exists without checking outcome | W3 |

## Exact-head merge package (for wave-signoff)

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/207 — expected reviewed head `96be30fecf6a000fc77d232d879c8272a17f2856` (+ Pass-2 docs tip after commit_workspace)
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-013-W2.md`
- Accept evidence: `wave-accepted` on tip (wave-acceptance) — human approved already
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-013-W2.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-013-W2.md`
- As-built: W2 recorded `human_approved` from wave-acceptance (evidence tip + label)
- Required merge fields (human fills at `wave-signoff`): `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [ ] Review REQ checklist — all wave-assigned REQs pass or explicitly deferred
- [ ] Review §Contracts produced — accurate for W3 `/pre-implement`
- [ ] Confirm reviewed head SHA matches PR #207 tip at merge time
- [ ] Confirm human_approved already from wave-acceptance
- [ ] Merge the wave PR manually at wave-signoff — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge

## Ready for wave-signoff (merge)?

yes — G1–G10 satisfied; no Blocking GF-*; Contracts produced complete

## Check summary (G1–G10)

| Check | Status |
|-------|--------|
| G1 Wave scope | PASS — W2 REQs only (REQ-14–16) |
| G2 Ground evidence | PASS — manual scan; ground_command N/A |
| G3 Assigned-REQ coverage | PASS |
| G4 Acceptance evidence | PASS — wave-accepted on tip |
| G5 ADR boundaries | PASS — ADR-010/011; ADR-013 not in scope |
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
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-013-W2.md
  blockers: []
  signals:
    wave: W2
    contracts_produced: 4
    assigned_reqs: [REQ-14, REQ-15, REQ-16]
    reviewed_head_sha: 96be30fecf6a000fc77d232d879c8272a17f2856
    pr_url: https://github.com/drivestream-lab/gateflow/pull/207
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "202"
    status: done
    commit_workspace:
      action: commit_workspace
      head_ref: feature/INIT-GATEFLOW-013-w2-repo-setup
```

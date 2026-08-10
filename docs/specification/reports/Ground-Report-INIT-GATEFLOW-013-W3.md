# Ground report — INIT-GATEFLOW-013 W3

| Field | Value |
|-------|-------|
| Wave | W3 — Launchpad status readiness + dual evaluators |
| Spec | `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` |
| Initiative | INIT-GATEFLOW-013 |
| Date | 2026-08-10 |
| Wave head (exact) | `feature/INIT-GATEFLOW-013-w3-status-readiness` @ `b693bdbb405883361ca279d1aba24654357301f4` — reviewed head for sign-off (Pass-1 tip at `wave-accepted`) |
| PR URL | https://github.com/drivestream-lab/gateflow/pull/208 |
| Status | Ready for wave-signoff |
| Review deadline | 2026-08-12 |
| Deciders | Tech lead / reviewer — merge at wave-signoff (human only) |
| Outcome | pass |
| Outcome reason | All W3-assigned REQs mapped to artifacts; wave-accepted on tip; Contracts produced complete; no Blocking GF-* |
| Assigned REQs | REQ-17, REQ-18, REQ-19, REQ-20, REQ-21, REQ-22, REQ-23 |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution-INIT-GATEFLOW-013-W3 | 487 passed (2026-08-10); status client, dual gate, selection/status outcomes |
| Ground | manual `src/` + `tests/**` scan (`ground_command` N/A) | inspect-only client; readiness_source; select/refresh; dual gates |
| Accept | `wave-accepted` on tip of PR #208 @ `b693bdb` | Human approved at wave-acceptance |

## Automated ground check output

N/A — no Makefile `ground_command`. Manual scan of wave-assigned entry points and tests documented in REQ checklist below.

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-17 | Real readiness check (status) against synced checkout for selected set-up repos | `LaunchpadStatusClient.inspect_status` after setup `ok` in `select_repos`; `verify_harness_status`; Wave-Execution W3 | pass |
| REQ-18 | Setup tool inspect-only — never apply/mutate | Client argv guard + unit `test_build_status_argv_inspect_only`; OPS-NOTE; ADR-013 Option B separate client | pass |
| REQ-19 | Per-repo check isolation (partial success) | Select batch status after setup; `STATUS_FAILED` keeps membership; peers independent (mirrors setup D5) | pass |
| REQ-20 | Tool unavailable distinct from repo not-ready | `tool_unavailable` reason; `test_inspect_status_tool_unavailable` | pass |
| REQ-21 | Real check becomes stored readiness for INIT-admitted repos | `readiness_source=launchpad_status` on new admits; `mark_harness_verified` on status success; dual gate prefers status | pass |
| REQ-22 | Pre-INIT repos keep existing readiness untouched | Status path writes only status-sourced rows; NULL/filesystem → `sync_harness`; force-recheck on filesystem never calls status (`test_filesystem_force_recheck_never_calls_status`) | pass |
| REQ-23 | On-demand refresh replaces stored answer in place | `POST …/repos/readiness/refresh` + `refresh_readiness`; status-sourced only | pass |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Dual evaluators; separate inspect-only status client (Option B) | ADR-013 Accepted | pass |
| Workspace authority unchanged | ADR-010 | pass |
| Tenant bearer on programme routes | ADR-011 | pass |
| Status client is `BaseInfraService`; DI + `_INFRA_SERVICE_TYPES` | infra-services / dependency-injection | pass |
| Settings via `get_instance()` (`APP_LAUNCHPAD_CLI_PATH`) | dependency-injection | pass |
| Models only in `src/models/` | pydantic-schemas | pass |
| Schema + human Alembic `versions/` (agent does not invent DDL ownership) | database-migrations | pass — human revision `03c11e20fdff` included |
| Business orchestrates; no ORM in service | repository-pattern | pass |
| Fail-fast named reasons; IDs as log kwargs | fail-fast / logging-loguru | pass |
| Co-shipped live verify under `tests/verify/` | testing-verify-flows | pass |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Setup-on-select batch (`ok` / `setup_failed`) | Ground-Report W2 | yes — status only after setup `ok` |
| Workspace layout `{root}/{org}/{repo}` | Ground-Report W2 / ADR-010 | yes — status inspect target |
| Admit retained on setup fail | Ground-Report W2 | yes — no status for failed setup |
| Select admit + probe all-or-nothing | Ground-Report W1 | yes — unchanged |
| Active-list writers | Ground-Report W1 | yes — + `readiness_source` |
| Filesystem harness evaluator retained | Ground-Report W2 / ADR-013 | yes — NULL/filesystem path |
| Harness cache writers | as-built / tenant_service | yes — status path marks verified |
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
| Inspect-only status client | LaunchpadStatusClient | `inspect_status(workspace_path, meta_config_dir, …)` | repo checkout + programme meta dir | ready / fail with named reason | Never invoke apply/mutate argv; missing binary → `tool_unavailable` | W4+ |
| Provenance column | tenant_repos | `readiness_source` | admit / refresh | `launchpad_status` \| `filesystem` \| NULL | New programme admits set `launchpad_status`; status path never rewrites pre-INIT NULL/filesystem rows | W4 |
| Status-after-setup select | ProgrammeOnboardingService | `select_repos` | newly admitted after setup `ok` | `ok` / `status_failed` (+ reason); membership kept | Skip status when setup failed; peers independent | W4 |
| Refresh in place | programme routes + onboarding | `POST …/repos/readiness/refresh` | status-sourced org/repo list | updated harness_verified / verdict | Reject or no-op for non-status provenance | W4 |
| Dual harness gate | wave_start / run_orchestrator | `_ensure_harness_ready` (equiv.) | org/repo + force flag | allow / 422 `never_checked` | Status path uses inspect; filesystem uses `sync_harness`; force on filesystem never calls status | W4 |

## Exact-head merge package (for wave-signoff)

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/208 — expected reviewed head `b693bdbb405883361ca279d1aba24654357301f4` (+ Pass-2 docs tip after commit_workspace)
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-013-W3.md`
- Accept evidence: `wave-accepted` on tip (wave-acceptance) — human approved already
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-013-W3.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-013-W3.md`
- As-built: W3 recorded `human_approved` from wave-acceptance (evidence tip + label)
- Required merge fields (human fills at `wave-signoff`): `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [ ] Review REQ checklist — all wave-assigned REQs pass or explicitly deferred
- [ ] Review §Contracts produced — accurate for W4 `/pre-implement`
- [ ] Confirm reviewed head SHA matches PR #208 tip at merge time
- [ ] Confirm human_approved already from wave-acceptance
- [ ] Merge the wave PR manually at wave-signoff — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge

## Ready for wave-signoff (merge)?

yes — G1–G10 satisfied; no Blocking GF-*; Contracts produced complete

## Check summary (G1–G10)

| Check | Status |
|-------|--------|
| G1 Wave scope | PASS — W3 REQs only (REQ-17–23) |
| G2 Ground evidence | PASS — manual scan; ground_command N/A |
| G3 Assigned-REQ coverage | PASS |
| G4 Acceptance evidence | PASS — wave-accepted on tip |
| G5 ADR boundaries | PASS — ADR-013/010/011 |
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
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-013-W3.md
  blockers: []
  signals:
    wave: W3
    contracts_produced: 5
    assigned_reqs: [REQ-17, REQ-18, REQ-19, REQ-20, REQ-21, REQ-22, REQ-23]
    reviewed_head_sha: b693bdbb405883361ca279d1aba24654357301f4
    pr_url: https://github.com/drivestream-lab/gateflow/pull/208
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "203"
    status: done
    commit_workspace:
      action: commit_workspace
      head_ref: feature/INIT-GATEFLOW-013-w3-status-readiness
```

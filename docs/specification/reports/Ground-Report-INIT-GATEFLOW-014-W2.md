# Ground report — INIT-GATEFLOW-014 W2

| Field | Value |
|-------|-------|
| Wave | W2 — JWT cutover; refuse old doors; per-programme ForgeClient; tenant-scoped runs; catalogue agents |
| Spec | `docs/specification/product/INIT-GATEFLOW-014-gateflow.md` |
| Initiative | INIT-GATEFLOW-014 |
| Date | 2026-08-11 |
| Wave head (exact) | Accept tip `0c8e8a5782f794802eddc2200e98e22010c8263e` (`wave-accepted`); Pass-2 / reviewed head `eb51e9fe62f01f4df7c19750dec2fd0b4f089073` |
| PR URL (if any) | https://github.com/drivestream-lab/gateflow/pull/222 — read-only context |
| Status | Draft |
| Review deadline | 2026-08-13 |
| Deciders | Tech lead / reviewer — merge at wave-signoff only |
| Outcome | pass |
| Outcome reason | Wave-assigned REQs mapped to artifacts; Contracts produced complete; `wave-accepted` on tip; no Blocking GF-* |
| Assigned REQs | REQ-04, REQ-23–REQ-26, REQ-28–REQ-33, REQ-41 (WorkManifest TASK-W2-01…06 `implements`) |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | Wave-Execution / `make test` | Pass-1: **544** passed; re-confirmed at Pass-2 gather |
| Ground | N/A — no `ground_command`; manual `src/` + `tests/**` scan | Entry points and tests cited per REQ |
| Accept | `wave-accepted` on PR #222 tip `0c8e8a5` (2026-08-11 @nikd10x) | Human approved at wave-acceptance |

## Automated ground check output

N/A — profile `ground_command` is N/A. Manual scan performed.

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-04 | Product APIs accept only Gateflow-issued JWT | `src/app.py` `public_paths` shrunk; Appendix-C routes use `require_role`; `verify_jwt_cutover.py` | pass |
| REQ-23 | `tenant_admin` JWT authorizes its programme | `require_programme_scope` / `require_tenant_resolved`; path tenant routes; unit `test_auth_dependencies` | pass |
| REQ-24 | `tenant_admin` authorizes control-plane for programme | waves/runs/board/checkpoints/initiatives/metrics/forge → `require_role(TENANT_ADMIN)` | pass |
| REQ-25 | Outbound forge/git uses programme stored credential | `ForgeClientFactory.for_programme` + `ProgrammePatTokenProvider`; `test_forge_client_factory` | pass |
| REQ-26 | Agent dispatch loads credential only from DB catalogue | `SlotValidator` catalogue check; `CursorAgentRunner.run_skill(credential=…)`; orchestrator fetches catalogue credential | pass |
| REQ-28 | Webhooks remain signature-checked | `src/api/webhooks/github_routes.py` inspect — no JWT/`require_role`; `/webhooks` still public | pass |
| REQ-29 | Unauthenticated product calls fail closed | middleware + shrunk `public_paths`; flipped programme/tenant token tests | pass |
| REQ-30 | Role mismatch fails closed | `require_role` 403 `role_forbidden`; `test_auth_dependencies` | pass |
| REQ-31 | Cross-programme access fails closed | `require_programme_scope`; `RunRepository.get_run`/`list_runs` `tenant_id`; `verify_cross_programme_isolation.py` | pass |
| REQ-32 | Programme service token refused | not on allowlist → 401; `test_programme_token_api` flipped | pass |
| REQ-33 | Tenant bearer refused | not on allowlist → 401; `test_tenant_token` / `test_tenant_routes` flipped | pass |
| REQ-41 | Env Cursor key never authorizes dispatch | zero `CursorAgentSettings.has_api_key()` in `slot_validator.py`; catalogue-only failures | pass |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Shrink product `public_paths`; refuse old doors (do not delete yet) | ADR-014 | pass — delete doors = W3 |
| Per-programme ForgeClient factory (Option C) | ADR-015 | pass |
| `runs.tenant_id` only; join-through-run_id | ADR-016 | pass — board/checkpoint derive via run when linked |
| Human Alembic / versions ownership | `database-migrations.mdc` | pass — human squashed baseline `5e85268f844f_first_version.py` (includes `runs.tenant_id`) |
| ORM confined to repositories | `repository-pattern.mdc` | pass |
| Webhooks outside JWT product edge | ADR-014 / REQ-28 | pass |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Programme store / `get_pat` | Ground-Report-W1 | yes — factory uses programme PAT |
| Attach tenant_admin + JWT `tenant_id` | Ground-Report-W1 | yes — programme scope deps |
| `require_role` | Ground-Report-W1 | yes — expanded with programme scope |
| Agent catalogue provision/resolve | Ground-Report-W1 | yes — SlotValidator/CursorAgentRunner catalogue-only |
| Catalogue connection routes under `/tenants/{id}/programme/*` | Ground-Report-W1 | yes — JWT deps swapped |
| RoleType / AuthContext / middleware | Ground-Report-W0 | yes |

## Discrepancies (must fix before human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| — | — | none | — |

## Learning cited

| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| — | — | Learning-Extract items empty — no open L-* |

## Contracts produced by this wave

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| JWT product edge | `AuthMiddleware` + `public_paths` | product `/api/v1/*` | Gateflow JWT Bearer | AuthContext or 401 | Old programme/tenant shared-secret Bearers refused (modules still present until W3) | W3 delete doors |
| Role + programme scope | `require_role` / `require_programme_scope` / `require_tenant_resolved` | FastAPI Depends | AuthContext + path tenant | AuthContext / TenantResolvedContext or 403 | Role mismatch + cross-tenant path refused | W3+ |
| Per-programme ForgeClient | `ForgeClientFactory` / `ProgrammePatTokenProvider` | `for_programme(pat)` | programme PAT string | ForgeClient instance | No App-install / env PAT fallback on this path | W3+ |
| Tenant-attributed runs | `RunSchema.tenant_id` + `RunRepository` | create / get_run / list_runs | tenant_id required at create; optional scope filter | RunModel | Non-null FK to tenants; cross-tenant get → miss | W3 wipe guard uses ACTIVE runs |
| Catalogue-only agents | `SlotValidator` + `CursorAgentRunner` (+ orchestrator) | validate_for_run / run_skill | catalogue credential | ok/fail; agent result | Never `CursorAgentSettings.has_api_key()` for accept/dispatch | W4 teaching |
| Webhooks unchanged | `github_routes` | signature verify | HMAC payload | enqueue | Still on `public_paths`; no JWT deps | — |

## Exact-head merge package (for wave-signoff)

- PR URL: https://github.com/drivestream-lab/gateflow/pull/222
- Accept tip (`wave-accepted`): `0c8e8a5782f794802eddc2200e98e22010c8263e`
- Reviewed head SHA (Pass-2 tip): `eb51e9fe62f01f4df7c19750dec2fd0b4f089073`
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-014-W2.md`
- Accept evidence: `wave-accepted` on accept tip — human approved already
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-014-W2.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-014-W2.md`
- Optional/legacy Live-Verify path: n/a
- As-built: W2 `human_approved` from wave-acceptance
- Required merge fields (human fills at `wave-signoff`): `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [ ] Review REQ checklist — all wave-assigned REQs pass or explicitly deferred
- [ ] Review §Contracts produced — accurate and complete for next wave
- [ ] Confirm reviewed head SHA matches the package above
- [ ] Confirm human_approved already recorded at wave-acceptance
- [ ] Merge the wave PR manually at wave-signoff (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for wave-signoff (merge)?

yes — G1–G10 satisfied; no Blocking GF-*; Contracts produced ready for W3 `/pre-implement`

## Checks (G1–G10)

| ID | Result |
|----|--------|
| G1 | PASS — W2 assigned REQs only |
| G2 | PASS — ground_command N/A; manual scan + unit cited |
| G3 | PASS — all assigned REQs in checklist |
| G4 | PASS — Wave-Execution + unit + wave-accepted |
| G5 | PASS — ADR-014, ADR-015, ADR-016 |
| G6 | PASS — domain MDC |
| G7 | PASS — consumed W0/W1 contracts + produced W2 contracts |
| G8 | PASS — Learning-Extract present; no L-* to cite |
| G9 | PASS — no GF-* open |
| G10 | PASS — report + as-built + merge package; commit via follow-on commit-workspace only |

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-014-W2.md
  blockers: []
  signals:
    wave: W2
    contracts_produced: 6
    assigned_reqs:
      - REQ-04
      - REQ-23
      - REQ-24
      - REQ-25
      - REQ-26
      - REQ-28
      - REQ-29
      - REQ-30
      - REQ-31
      - REQ-32
      - REQ-33
      - REQ-41
    accept_tip: 0c8e8a5782f794802eddc2200e98e22010c8263e
    pr_url: https://github.com/drivestream-lab/gateflow/pull/222
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "https://github.com/drivestream-lab/gateflow/issues/217"
```

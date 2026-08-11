# Ground report — INIT-GATEFLOW-014 W1

| Field | Value |
|-------|-------|
| Wave | W1 — Programme validate-then-create + tenant_admin attach + agent catalogue |
| Spec | `docs/specification/product/INIT-GATEFLOW-014-gateflow.md` |
| Initiative | INIT-GATEFLOW-014 |
| Date | 2026-08-11 |
| Wave head (exact) | Accept tip `ecb7fbd863b0b6b4ed305cc83acc98aff2a69f5b` (`wave-accepted`); Pass-2 / reviewed head `f4830f45036e5e450acecd89370d10a957993bde` |
| PR URL (if any) | https://github.com/drivestream-lab/gateflow/pull/221 — read-only context |
| Status | Draft |
| Review deadline | 2026-08-13 |
| Deciders | Tech lead / reviewer — merge at wave-signoff only |
| Outcome | pass |
| Outcome reason | Wave-assigned REQs mapped to artifacts; Contracts produced complete; `wave-accepted` on tip; no Blocking GF-* |
| Assigned REQs | REQ-08–REQ-22, REQ-40–REQ-42, REQ-44, REQ-45, REQ-47 (attach/idempotent slice) |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | Wave-Execution / `make test` | Pass-1: 525 passed |
| Ground | N/A — no `ground_command`; manual `src/` + `tests/**` scan | Entry points and tests cited per REQ |
| Accept | `wave-accepted` on PR #221 tip `ecb7fbd` (2026-08-11 @nikd10x) | Human approved at wave-acceptance |

## Automated ground check output

N/A — profile `ground_command` is N/A. Manual scan performed.

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-08 | platform_admin validate-then-create Programme | `ProgrammeService.validate_then_create`; `POST /api/v1/programmes`; unit + verify script | pass |
| REQ-09 | Validation before durable create | PAT probe + meta clone/parse before transaction | pass |
| REQ-10 | Validation failure → 0 Programme/Tenant rows | `test_programme_service` bad PAT/meta asserts no create | pass |
| REQ-11 | Programme stores own PAT | `ProgrammeSchema.github_pat`; not returned on `ProgrammeReadModel` | pass |
| REQ-12 | Workspace root at onboard | `workspace_root` on request + schema | pass |
| REQ-13 | Agent keys rejected on onboard | `ProgrammeOnboardRequest` rejects `agent_key` fields | pass |
| REQ-14 | GitHub App fields reserved unused | nullable `github_app_id` / `github_installation_id` | pass |
| REQ-15 | Attach tenant_admin | `attach_tenant_admin` + route; JWT with tenant_id | pass |
| REQ-16 | Only one programme role type (`tenant_admin`) | attach always `RoleType.TENANT_ADMIN` | pass |
| REQ-17 | platform_admin list programmes | `GET /api/v1/programmes` + `require_role(PLATFORM_ADMIN)` | pass |
| REQ-18 | platform_admin cannot onboard/deboard repos or start runs | No such capability added on admin routes; control-plane cutover remains W2 | pass (W1 scope) |
| REQ-19 | Provision Cursor into DB catalogue | `POST /api/v1/agent-catalogue`; catalogue service | pass |
| REQ-20 | Catalogue reserves slots for other runners | unique `runner_id`; credential optional at storage | pass |
| REQ-21 | Effective runner: caller or lane default | `resolve_effective_runner` | pass |
| REQ-22 | Missing/unprovisioned runner rejected | unit + verify script negative path | pass |
| REQ-40 | Catalogue is durable DB table | `platform_agent_catalogue` schema + repo | pass |
| REQ-41 | Env Cursor key never authorizes resolve | no `CursorAgentSettings` consult in resolve path | pass (W1; SlotValidator cutover = W2) |
| REQ-42 | Per-lane defaults | `lane_defaults` JSONB + `PUT …/lane-defaults` | pass |
| REQ-44 | Attach unknown programme rejected | unit + verify | pass |
| REQ-45 | Blank agent credential rejected | provision service + verify | pass |
| REQ-47 | Idempotent re-attach | attach reuses same identity | pass (attach slice; seed was W0) |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Reuse AuthMiddleware; admin routes JWT-gated | ADR-014 | pass — `/programmes` not on `public_paths` |
| Programme owns PAT; factory later | ADR-015 | pass — storage only in W1 |
| ORM in repositories only | `repository-pattern.mdc` | pass |
| Human Alembic for new tables | `database-migrations.mdc` | pass — DDL note; no agent `versions/` |
| Meta-connection rename (AF-1) | TDD E4 | pass — `catalogue_connection_*`; URLs unchanged |
| Do not shrink product `public_paths` | plan E6 / W2 | pass |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| RoleType / AuthContext / JWT mint / identity store | Ground-Report-W0 | yes |
| GithubPatProbe + TenantGitWorkspaceClient + catalogue parse | INIT-013 as-built / source | yes — reused before durable create |

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
| Programme store | `ProgrammeRepository` / `ProgrammeSchema` | create / get_by_id / list / get_pat / update_lane_defaults | PAT, workspace, meta, lane_defaults | `ProgrammeReadModel` (no PAT) | PAT plaintext on row; App fields unused | W2 forge factory |
| Validate-then-create | `ProgrammeService.validate_then_create` | onboard request | meta + workspace + PAT | `ProgrammeCreateResult` + child tenant | Fail closed before TX; no agent_key | W2+ |
| Attach tenant_admin | `ProgrammeService.attach_tenant_admin` | programme_id + credentials | identity → TENANT_ADMIN + tenant_id | JWT + user_id | Unknown programme → reject; idempotent | W2 |
| Role gate | `require_role` | FastAPI Depends | AuthContext | AuthContext or 403 | platform_admin for admin routes | W2 expand |
| Agent catalogue | `PlatformAgentCatalogueService` | provision / resolve_effective_runner | runner_id, credential; lane + optional caller | entry / `EffectiveRunner` | Never consults CursorAgentSettings/env | W2 SlotValidator |
| Meta-connection rename | `CatalogueConnectionService` / routes | existing `/tenants/{id}/programme/*` | unchanged wire | unchanged | Distinct from Programme entity | W2 auth swap on these routes |

## Exact-head merge package (for wave-signoff)

- PR URL: https://github.com/drivestream-lab/gateflow/pull/221
- Accept tip (`wave-accepted`): `ecb7fbd863b0b6b4ed305cc83acc98aff2a69f5b`
- Reviewed head SHA (Pass-2 tip): `f4830f45036e5e450acecd89370d10a957993bde` — merge PR tip if a follow-up stamp commit lands
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-014-W1.md`
- Accept evidence: `wave-accepted` on accept tip — human approved already
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-014-W1.md`
- Optional/legacy Live-Verify path: n/a
- As-built: W1 `human_approved` from wave-acceptance
- Required merge fields (human fills at `wave-signoff`): `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [ ] Review REQ checklist — all wave-assigned REQs pass or explicitly deferred
- [ ] Review §Contracts produced — accurate and complete for next wave
- [ ] Confirm reviewed head SHA matches the package above
- [ ] Confirm human_approved already recorded at wave-acceptance
- [ ] Merge the wave PR manually at wave-signoff (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for wave-signoff (merge)?

yes — G1–G10 satisfied; no Blocking GF-*; Contracts produced ready for W2 `/pre-implement`

## Checks (G1–G10)

| ID | Result |
|----|--------|
| G1 | PASS — W1 assigned REQs only |
| G2 | PASS — ground_command N/A; manual scan + unit cited |
| G3 | PASS — all assigned REQs in checklist |
| G4 | PASS — Wave-Execution + unit + wave-accepted |
| G5 | PASS — ADR-014, ADR-015 |
| G6 | PASS — domain MDC |
| G7 | PASS — consumed W0 contracts + produced W1 contracts |
| G8 | PASS — Learning-Extract present; no L-* to cite |
| G9 | PASS — no GF-* open |
| G10 | PASS — report + as-built + merge package; no commit from this skill |

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-014-W1.md
  blockers: []
  signals:
    wave: W1
    contracts_produced: 6
    assigned_reqs:
      - REQ-08
      - REQ-09
      - REQ-10
      - REQ-11
      - REQ-12
      - REQ-13
      - REQ-14
      - REQ-15
      - REQ-16
      - REQ-17
      - REQ-18
      - REQ-19
      - REQ-20
      - REQ-21
      - REQ-22
      - REQ-40
      - REQ-41
      - REQ-42
      - REQ-44
      - REQ-45
      - REQ-47
    reviewed_head_sha: f4830f45036e5e450acecd89370d10a957993bde
    pr_url: https://github.com/drivestream-lab/gateflow/pull/221
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "https://github.com/drivestream-lab/gateflow/issues/216"
```

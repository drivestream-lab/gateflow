# Ground report — INIT-GATEFLOW-014 W4

| Field | Value |
|-------|-------|
| Wave | W4 — Prove absence + rewrite teaching surfaces |
| Spec | `docs/specification/product/INIT-GATEFLOW-014-gateflow.md` |
| Initiative | INIT-GATEFLOW-014 |
| Date | 2026-08-11 |
| Wave head (exact) | Accept tip `30a3ed2ab518af74c00cadb2de046431763b1449` (`wave-accepted`); Pass-2 / reviewed head filled after `/commit-workspace` |
| PR URL (if any) | https://github.com/drivestream-lab/gateflow/pull/226 — read-only context |
| Status | Draft |
| Review deadline | 2026-08-13 |
| Deciders | Tech lead / reviewer — merge at wave-signoff only |
| Outcome | pass |
| Outcome reason | Wave-assigned REQs mapped to artifacts; Contracts produced complete; `wave-accepted` on tip; no Blocking GF-*; last eng wave for INIT-014 |
| Assigned REQs | REQ-36, REQ-37, REQ-38 (WorkManifest TASK-W4-01…03 `implements`) |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | Wave-Execution / `make test` | Pass-1: **540** passed; re-confirmed at Pass-2 gather (**540** passed) |
| Ground | N/A — no `ground_command`; manual `tests/**` + docs scan | Verify rewrite + teaching docs cited per REQ |
| Accept | `wave-accepted` on PR #226 tip `30a3ed2` | Human approved at wave-acceptance (Draft converted / labeled) |

## Automated ground check output

N/A — profile `ground_command` is N/A. Manual scan performed.

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-36 | Verify scripts prove JWT happy path | `tests/_helpers/verify_jwt_auth.py`; rewritten Appendix-C / remaining consumers under `tests/verify/`; `verify_all` aggregator; Wave-Execution TASK-W4-01; zero `PROGRAMME_SERVICE_TOKEN` under `tests/verify/` | pass |
| REQ-37 | Verify scripts prove refusal of programme token, tenant bearer, open register | `tests/verify/verify_old_doors_refused.py` (opaque token→401, opaque bearer→401, `POST /tenants`→401/404/405); extends W2/W3 negative proofs | pass |
| REQ-38 | Teaching surfaces describe JWT + per-programme GitHub + DB catalogue only | `tests/README.md` JWT-only invocation examples; as-built W4 matrix; no `PROGRAMME_SERVICE_TOKEN` teaching in README | pass |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| JWT-only product teaching (no old doors) | ADR-014 | pass — verify clients use Gateflow JWT; PAT never as Authorization |
| Live verify ownership vs pytest | `testing-verify-flows.mdc` | pass — smoke scripts co-shipped; unit not duplicated for full HTTP journeys |
| Fail-closed negative paths | `fail-fast.mdc` | pass — old-door script asserts named refusal statuses |
| No secrets in logs/prints | `logging-loguru.mdc` | pass — scripts print `[OK]`/`[ERROR]` without token values |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Dead doors removed (`POST /tenants` gone; token modules deleted) | Ground-Report-W3 | yes — teaching/negative scripts assert absence/401 |
| JWT product edge + role scope | Ground-Report-W2 | yes — control-plane verify uses tenant_admin JWT |
| Login / seed platform_admin | Ground-Report-W0 | yes — helper `login_platform_admin` / seed |
| Programme create + attach tenant_admin | Ground-Report-W1 | yes — `provision_programme_tenant_admin` for scripts needing a tenant |

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
| JWT verify client helper | `tests/_helpers/verify_jwt_auth.py` | `require_tenant_admin_token` / `provision_programme_tenant_admin` / `login_platform_admin` | env JWT or login + optional programme PAT for create | Gateflow JWT (+ tenant_id when provisioned) | PAT never used as product Authorization | Initiative closure / ops dogfood |
| JWT teaching / happy-path smoke | rewritten `tests/verify/*` + `verify_all` | `.venv/bin/python -m tests.verify.verify_all` | running API + tenant_admin JWT | exit 0 | Zero `PROGRAMME_SERVICE_TOKEN` under `tests/verify/` | Initiative exit gate |
| Consolidated old-door refusal | `verify_old_doors_refused.py` | `.venv/bin/python -m tests.verify.verify_old_doors_refused` | running API | exit 0 | Opaque programme token→401; opaque tenant bearer→401; open register→401/404/405 | Initiative exit gate |
| Teaching docs JWT-only | `tests/README.md` + as-built INIT-014 | doc review | — | JWT + per-programme PAT examples only | No old-door invocation copy | Initiative closure docs |

> W4 is the last engineering wave for INIT-GATEFLOW-014. Next programme hop is initiative closure (not W5 coding).

## Exact-head merge package (for wave-signoff)

- PR URL: https://github.com/drivestream-lab/gateflow/pull/226
- Accept tip (`wave-accepted`): `30a3ed2ab518af74c00cadb2de046431763b1449`
- Pass-2 / reviewed head: 
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-014-W4.md`
- Accept evidence: `wave-accepted` on tip — human approved already
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-014-W4.md`
- As-built: W4 `human_approved` from wave-acceptance
- Required merge fields (human fills at `wave-signoff`): `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [ ] Review REQ checklist — all wave-assigned REQs pass
- [ ] Review §Contracts produced — accurate for initiative closure
- [ ] Confirm reviewed head SHA matches the package above
- [ ] Confirm human_approved already recorded at wave-acceptance
- [ ] Merge the wave PR manually at wave-signoff (human only)
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for wave-signoff (merge)?

yes — G1–G10 satisfied for teaching/verify wave; no Blocking GF-*; Contracts produced complete; accept on tip

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-014-W4.md
  blockers: []
  signals:
    wave: W4
    contracts_produced: 4
    assigned_reqs: [REQ-36, REQ-37, REQ-38]
    accept_tip: 30a3ed2ab518af74c00cadb2de046431763b1449
    pr_url: https://github.com/drivestream-lab/gateflow/pull/226
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "https://github.com/drivestream-lab/gateflow/issues/219"
    commit_workspace: required
```

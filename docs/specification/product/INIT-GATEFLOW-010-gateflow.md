# INIT-GATEFLOW-010 — spec slice for gateflow

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-010 |
| Wave ticket (this run) | W0 — tip contract parse + purpose/owner |
| PRD | `prayog-meta/prd/INIT-GATEFLOW-010.md` |
| PRD digest (H1) | `sha256:457f19617113171c973abdbc15d1afaa00df2f6947ab4567b57d8440bd88b206` |
| Meta PR | https://github.com/drivestream-lab/prayog-meta/pull/28 |
| Meta PR approved head (G1) | `df0f5a5c09b6c4f951463bb42f277305310aaa80` |
| Impact map | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-010.md` |
| Impact-map revision (H3) | `1` |
| Repo scope digest (H2) | `sha256:09c89c143c14401c8812738c162c05a2f5e504cabafd1818ee72eb4e9b781532` |
| Tech-lead approval | @0xbeefdead APPROVED 2026-08-05T09:32:32Z on `df0f5a5c09b6c4f951463bb42f277305310aaa80` — attestation: map_revision 1, prd_digest match, artifact `prd/reports/Impact-Map-INIT-GATEFLOW-010.md` |
| Architecture | [`adr-009-pin-forge-publish-mutate-authority.md`](../adr/adr-009-pin-forge-publish-mutate-authority.md) (**Accepted**); [`adr-010-lane-intake-and-dual-workspace-authority.md`](../adr/adr-010-lane-intake-and-dual-workspace-authority.md) (**Accepted**); pin SSOT [`prayog-skills/workflow.yaml`](../../../prayog-skills/workflow.yaml), [`references/forge-side-effects.md`](../../../prayog-skills/references/forge-side-effects.md), [`delivery-contract.yaml`](../../../prayog-skills/delivery-contract.yaml) |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-05 |
| Status | Draft — dev review required before Forge publish |

> **H4 citations:** The H1–H3 (and G1) rows above are the durable authority
> carrier for mid-lane freshness. Feas / TDD / plan digests are walk-time only
> and may be purged at initiative closure.

## Overview

Gateflow must **execute** the pinned engineering lifecycle against
`sdd-delivery/v2` @ **`v0.5.0-rc.2`**: spec → tickets → implement (per wave) →
closeout (per wave) → eng initiative closure (purge-app only). Today the remounted
pin declares board-status hops (`wave-in-progress-action`, `wave-done-action`) and
checkpoint `purpose` / `owner`, but Gateflow cannot parse `update_board_status`
( walker **BLOCK** on those nodes), does not model pin `forge.status` or `ticket`
requires, and drops `purpose` / `owner` on resolve/stop events.

This spec productizes **tip-faithful eng-lane executor parity** in gateflow only.
Primary delivery is gateflow; PM Enter-at and meta purge remain out of scope.

**W0 exit (this wave ticket):** pin consume hygiene (REQ-01); parse all remounted
nodes including board-status hops with `status` + `ticket` requires (REQ-02 parse
slice); expose pin `purpose` / `owner` on resolved nodes and stop timeline
(REQ-10); **0 BROKEN** `get_node` across the pin; unit green.

**Later waves (normative exits — not W0 scope):** W1 wires APPLY_FORGE board
status + implement-start In Progress (REQ-03, REQ-04); W2 ticket gate + create
predicates (REQ-06–REQ-08); W3 closeout Done + no auto-chain (REQ-05, REQ-09,
REQ-16, REQ-19); W4 closure Enter-at + freeze (REQ-12–REQ-15, REQ-17–REQ-18,
REQ-20).

**Out of scope:** gateflow-ops UI; prayog-skills pin redesign; meta purge orch;
Forge merge / auto `*-lgtm`; same-run create→implement resume; ops UI / second
agent / Slack; Initiative C2 probes; discovering wave tickets via
`list_tickets(initiative_id)` alone (label asymmetry — caller passes
`wave_ticket_ids[]`).

**As-built baseline (2026-08-05):** Submodule `6561c7c` ≡ tag family `v0.5.0-rc.2`;
`.harness-pin.yaml` `agent_skills.ref: v0.5.0-rc.2`. `ForgeActionType` lacks
`update_board_status` — `get_node('wave-in-progress-action')` / `get_node('wave-done-action')`
fail closed. `ResolvedWorkflowNode` has no `purpose` / `owner`. INIT-009 freeze
proved spec/closeout/authorize paths; **010** closes pin executor gaps for board
status + closure Enter-at.

## Delivery waves (product-normative)

| Wave | Intent | Exit REQs |
|------|--------|-----------|
| **W0** | Parse board-status hops + `status` + `ticket`; purpose/owner; all remounted nodes `get_node`; unit green | REQ-01, REQ-02 (parse), REQ-10 |
| **W1** | Wire APPLY_FORGE board-status; implement-start In Progress before `pre-implement` (idempotent) | REQ-03, REQ-04, REQ-11 |
| **W2** | Ticket gate (400/422); create predicates hard-fail; verify tickets + implement (partial REQ-17) | REQ-06–REQ-08, REQ-17 (partial) |
| **W3** | Closeout Done → `wave-signoff`; spec Pass-1 verify; wave-complete no auto-chain | REQ-05, REQ-09, REQ-16, REQ-17, REQ-19 |
| **W4** | Closure Enter-at + Done-gate + EPIC Done programme hygiene + purge walk + REQ-20; closure verify; freeze | REQ-12–REQ-15, REQ-17–REQ-18, REQ-20 |

## Functional requirements

| ID | Requirement | PRD source | Condition / event | Observable result | Evidence layer |
|----|-------------|-----------|-------------------|-------------------|----------------|
| REQ-01 | Consume pin family **`v0.5.0-rc.2`** only. Harness `.harness-pin.yaml` `agent_skills.ref` **must equal** the prayog-skills submodule commit/tag used at runtime. No pin redesign or new RC in this INIT. | PRD REQ-01; CAP-06; A3 | Before W1+ lane verify | Pin load succeeds; `spec-draft` is `dispatch: orchestrated`; harness pin == submodule SHA/tag | unit + inspection |
| REQ-02 | Gateflow **parses** pin board-status external-action nodes: `forge.action: update_board_status`, pin `forge.status` (`in_progress` \| `done`), and `forge.requires: [ticket]`. `WorkflowEngine.get_node` succeeds for **every** node id in remounted `workflow.yaml` (including `wave-in-progress-action` and `wave-done-action`) — **0 BROKEN**. | PRD REQ-02; CAP-06; G1 | Pin load / unit parse | No `ValueError` on board-status nodes; parsed policy exposes action, status enum, and ticket require | unit |
| REQ-03 | When an automated board-status hop executes (W1+), Gateflow applies pin `forge.status` to the run-bound board ticket per BoardService column+state contract. | PRD REQ-03; CAP-06; G1 | Automated `update_board_status` APPLY_FORGE | Board shows In Progress or Done for the ticket | unit + verify |
| REQ-04 | Accepted **`POST /api/v1/waves/implement/start`** applies In Progress for run `ticket_id` **before** dispatching `pre-implement`. Already board In Progress → idempotent accept (no error solely for `in_progress`). | PRD REQ-04; CAP-03; G8-A1; US-3 | Implement-start accepted | Timeline shows In Progress hop before first coding skill; board column matches | verify |
| REQ-05 | Closeout walk applies Done after `ground-spec.pass`, then terminal stop at **`wave-signoff`** with pin `purpose: wave-signoff` visible. | PRD REQ-05; CAP-04; US-4 | Closeout Enter-at through Pass-2 | Done hop recorded; terminal purpose `wave-signoff` | verify |
| REQ-06 | Create-tickets path hard-fails unless all three node predicates pass: `spec-pr-merged`, `implementation-plan-current`, `workmanifest-contract-pass`. | PRD REQ-06; CAP-02; G2; US-2 | Create authorize/apply | **422** (or authorize fail); **0** board creates on failure | unit + verify |
| REQ-07 | Create success returns **`epic_ticket_id`** and **`wave_ticket_ids[]`** for downstream implement-start and closure-start binds. | PRD REQ-07; CAP-02; G9-A1 | Create success | Response fields present and persisted for PE reuse | unit + verify |
| REQ-08 | Implement-start requires non-empty `ticket_id`; **board-resolves** ticket on org/repo; ticket must agree with `initiative_id` + `wave_id`; missing/malformed → **400**; unresolvable/mismatch/already Done → **422**; **0 enqueue**. | PRD REQ-08; CAP-03; G5; US-3; error table | Bad/missing ticket request | No run enqueued; HTTP semantics match product error table | unit + verify |
| REQ-09 | Gateflow performs **no** Forge merge action; human owns `spec-merge` and signoff merges. | PRD REQ-09; CAP-06; G6 | Any eng walk | No merge API/action invoked by Gateflow | code guard + verify |
| REQ-10 | Resolved workflow nodes and run stop/resolution events expose pin **`purpose`** when set, and pin **`owner`** when set (human-checkpoint and external-action nodes). | PRD REQ-10; CAP-01/CAP-06; G7; US-7 | Walker STOP at checkpoint or after resolve | Run timeline / status API includes purpose (and owner when pin declares it) | unit |
| REQ-11 | Create-tickets success does **not** resume into implement/coding on the same run; coding starts only via a new implement-start. | PRD REQ-11; CAP-02; G8; US-2 | After create completes | Same run does not dispatch `pre-implement` | unit + verify |
| REQ-12 | **`POST /api/v1/initiatives/closure/start`** accepts programme token + required body binds; missing/malformed → **400**; valid → **202** + `run_id`. | PRD REQ-12; CAP-05; G3–G4; US-5 | Closure start request | HTTP + enqueue semantics per error table | unit + verify |
| REQ-13 | Closure **Done-gate:** every entry in `wave_ticket_ids[]` must be board **Done** (pin `status: done` contract); else **422**, no purge, EPIC not mutated. | PRD REQ-13; CAP-05; G9-A1; US-5 | Closure start with wave list | Fail closed when any wave not Done | unit + verify |
| REQ-14 | After Done-gate passes, set **`epic_ticket_id` → Done** before dispatching `purge-initiative-artifacts-app` — programme board hygiene (**not** a pin external-action node). | PRD REQ-14; CAP-05; draft lock; US-5 | Closure enter accepted | EPIC Done on board before purge hop | verify |
| REQ-15 | Closure walk: `purge-initiative-artifacts-app` → automated `initiative-closure-pr-action-app` → STOP `initiative-closure-signoff-app`; never dispatch meta purge. | PRD REQ-15; CAP-05; G3; US-5 | Closure run | Terminal stop at signoff-app; no meta purge node | verify |
| REQ-16 | Automated forge applies only pin-declared `apply_labels`; **never** labels ending in **`-lgtm`**. | PRD REQ-16; CAP-06; G10; US-7 | Any `open_draft_pr` / label projection | Label audit shows no auto approval labels | unit + verify |
| REQ-17 | Verify suite under `tests/verify/` covers spec, tickets, implement (with In Progress), closeout (with Done), and closure lanes; programme exit requires exit 0 under knobs. | PRD REQ-17; CAP-01…05; G11 | Programme prove-out | Live-Verify records + script exit 0 | live verify |
| REQ-18 | Feature-readiness freeze lists **proven** eng lanes vs **deferred** (PM Enter-at, meta purge, ops UI, C2, authorize→resume). | PRD REQ-18; CAP-06; US-7 | W4 exit | Freeze doc under `docs/specification/reports/` | inspection |
| REQ-19 | After `wave-signoff` / `wave-complete`, Gateflow does **not** auto-start next wave or closure; PE starts next implement-start or closure-start deliberately. | PRD REQ-19; CAP-04; G8; US-6 | Wave signoff complete | No auto-chain to implement/closure | unit + verify |
| REQ-20 | If EPIC → Done succeeds but purge-app or closure Draft PR fails: record failure; **do not** claim closure complete; PE may re-enter / compensate. | PRD REQ-20; CAP-05; VF-09; US-5 | Partial failure after EPIC Done | Failure recorded; no false success claim | unit + verify |

> **Id convention:** `REQ-*` is canonical per
> [`id-conventions.md`](../../../prayog-skills/references/id-conventions.md).
> PRD `CAP-*` / `REQ-*` ids are cited in PRD source column — same numbers.

**W0 slice note:** REQ-02 **apply** behaviour is REQ-03 (W1). W0 proves parse +
model completeness only. REQ-04–REQ-20 are normative initiative exits deferred to
later waves per table above.

**Inherited (unless superseded):** INIT-001…009 control plane; ADR-009 publish
before ingest + dual `authorization`; ADR-010 lane intake + dual workspace;
INIT-008 automated `spec-pr-action` / `wave-pr-action`; ForgeClient transport;
programme token; never write `*-lgtm`.

## Negative and failure paths

| REQ | Condition | Required behavior | Evidence |
|-----|-----------|-------------------|----------|
| REQ-02 | Unknown `forge.action` (e.g. unparsed `update_board_status`) | `get_node` fail closed; walker must not silently skip board-status nodes | unit |
| REQ-02 | Invalid `forge.status` value on board-status node | Parse fail closed at pin load / get_node | unit |
| REQ-03 | Board-status hop with missing `ticket` at apply time | Fail closed hop; no silent skip (PRD error table) | unit + verify |
| REQ-06 | Any create predicate fails | **422**; 0 tickets created | unit + verify |
| REQ-08 | Missing/malformed `ticket_id` on implement-start | **400**; 0 enqueue | unit + verify |
| REQ-08 | Unresolvable ticket or initiative/wave mismatch | **422**; 0 enqueue | unit + verify |
| REQ-08 | Ticket already board Done | **422**; 0 enqueue | unit + verify |
| REQ-08 | Ticket already In Progress | Accept idempotently; proceed | unit + verify |
| REQ-12 | Closure missing/malformed required fields or empty `wave_ticket_ids` | **400**; 0 enqueue | unit + verify |
| REQ-13 | Any listed wave not board Done | **422**; no purge; EPIC not mutated | unit + verify |
| REQ-16 | Handoff or pin attempts `*-lgtm` in apply_labels | Reject / fail closed | unit |
| REQ-20 | EPIC Done ok; purge-app or closure PR fails | Run failure recorded; closure not claimed complete | unit + verify |
| US-1 / spec | Spec start with empty `meta_workspace` | **400**; 0 enqueue | unit + verify (non-regression) |

## Out of scope for this repo

- **gateflow-ops** / Mission Control UI (deferred — REQ-18)
- **prayog-meta** eng delivery (PRD/map host only)
- **prayog-skills** workflow redesign (consume tip `v0.5.0-rc.2` only)
- PM / requirements Enter-at (`validate-requirements` … Gate 1 meta lane)
- `purge-initiative-artifacts-meta` and meta closure PR/signoff orch
- Same-run authorize→resume after create-tickets into implement
- Implement-start auto-creates board tree or picks first wave
- Forge merge / `delete_branch`; auto `*-lgtm`
- Discovering wave tickets via `list_tickets(initiative_id)` alone (§8 outline —
  closure must use explicit `wave_ticket_ids[]`)

## Cross-service contracts

| Contract ID | Provider / owner | Consumer / owner | Entry point | Input shape | Output shape | Invariants | Errors | Compatibility / versioning | Contract-test location |
|-------------|------------------|------------------|-------------|-------------|--------------|------------|--------|----------------------------|------------------------|
| CTR-01 | prayog-skills / PE | gateflow | Pinned `workflow.yaml` + `sdd-delivery/v2` @ `v0.5.0-rc.2` | pin YAML + delivery contract | Parsed nodes, forge policy, handoff envelope | Consume only; no pin redesign | Invalid pin ⇒ fail closed | `v0.5.0-rc.2` family frozen (A3) | `test_forge_policy`, `test_handoff_workflow`, pin contract tests |
| CTR-02 | GitHub (forge/board) | gateflow | Board create/status + Draft PRs via ForgeClient | org/repo, ticket ids, status enum, PR fields | issues, column+state, PR numbers | Board Done/In Progress = pin `status` vocabulary (A1) | I/O / auth ⇒ fail closed | ADR-003 forge transport | `test_board_service`, `test_forge_client`, verify scripts |
| CTR-03 | gateflow / PE | GitHub (forge/board) | Outbound forge: `open_draft_pr`, `create_board_tickets`, `update_board_status` | handoff.forge slots + pin requires | PR/ticket side effects | Never merge; never `*-lgtm`; ticket from run for status hops | Missing requires ⇒ fail closed | INIT-008 automated vs explicit split | `test_forge_action_service`, `test_forge_merge`, verify suite |

## Non-functional requirements

| Area | Requirement or N/A rationale | Acceptance / evidence |
|------|------------------------------|-----------------------|
| Security | Programme service token on lane/forge routes (existing); no secrets in handoff/verify artifacts; never auto-apply `*-lgtm` | unit + inspection |
| Reliability | Fail closed on missing ticket at board-status apply, predicate failures, Done-gate miss, incomplete forge requires | unit + verify |
| Performance / capacity | N/A — correctness and pin parity over cycle-time KPIs for this INIT | inspection |
| Observability | Run timeline records stage hops, forge apply/pending, stop reason, pin `purpose`/`owner` when present | unit + verify |
| Privacy / data handling | No secrets in committed verify artifacts or handoff batons | inspection |
| Migration / compatibility | Additive APIs (`closure/start`); existing spec/implement/closeout routes preserved (non-regression US-1) | unit |
| Rollback / recovery | Disable new closure route or worker; prior INIT-009 proven lanes remain baseline; REQ-20 partial-fail re-enter | runbook inspection |
| Operations / support | `tests/README.md` + verify scripts document lane knobs; W4 freeze names proven vs deferred | docs + inspection |

## Assumptions

| ID | Assumption | Evidence | Owner | Status | Invalidated when |
|----|------------|----------|-------|--------|------------------|
| A-1 | Board **Done** / **In Progress** = pin `status: done` \| `in_progress` as applied by board-status hops / BoardService contract | PRD A1; IM | PE | confirmed | Board vocabulary changes |
| A-2 | PE retains `epic_ticket_id` + `wave_ticket_ids[]` from create-tickets for implement-start and closure-start | PRD A2 | PE | confirmed | API response shape changes |
| A-3 | Pin tip family `v0.5.0-rc.2` frozen for INIT delivery; harness ref == submodule tip | PRD A3; `.harness-pin.yaml`; submodule `6561c7c` | PE | confirmed | Mid-INIT tip retag |
| A-4 | Meta PR #28 Gate 1 approval on head `df0f5a5…` remains valid for spec start preconditions | Meta PR review attestation | PE | confirmed | Head moves without re-approval |
| A-5 | INIT-009 proven spec/closeout baseline is non-regression floor for US-1 | Feature-Readiness-009 | PE | confirmed | Pin graph regresses spec lane |

## Spec questions (ambiguities — need PM or domain confirmation before feasibility)

| ID | Lane | Question | Owner | Blocking | Required by | Default if deferred | Status | Resolution link |
|----|------|----------|-------|----------|-------------|---------------------|--------|-----------------|
| Q-1 | PE | Exact problem+json / OpenAPI error body field names (**PRD OQ-01** / IM-01) | PE | no | OpenAPI / spec PR follow-up | Defer field names; HTTP **400**/**422** semantics remain normative per PRD error table | open | PRD OQ-01 |
| Q-2 | PE | W0 unit scope: is a dedicated pin-walk test asserting **all** node ids sufficient, or must W0 also include a minimal orchestrator resolve smoke for board-status nodes? | PE | no | W0 implement plan | All-node `get_node` unit + existing workflow contract tests | open | W0 plan |
| Q-3 | PM | Parallel open GATEFLOW meta PRs (#10–#23) sequencing vs this INIT (**IM-02**) | PM | no | Gate 1 scheduling | Proceed; distinct INIT ids | open | IM-02 |

## Draft check summary (D1–D12)

| Check | Status | Evidence / findings |
|-------|--------|---------------------|
| D1 Approved handoff current | **PASS** | Meta PR #28 head `df0f5a5…` = tech-lead APPROVED review commit; H1 prd_digest + H3 map_revision 1 match; gateflow affected with H2 scope digest; not deferred/blocked |
| D2 Complete PRD traceability | **PASS** | CAP-01…06 / PRD REQ-01…20 each map to spec REQ-01…20; every REQ cites PRD CAP/REQ or §/US |
| D3 Repo-bounded scope | **PASS** | gateflow eng delivery only; gateflow-ops/prayog-skills/meta eng excluded per impact map |
| D4 Observable acceptance | **PASS** | Every REQ has condition/event, observable result, evidence layer; implementation-neutral |
| D5 Negative/failure paths | **PASS** | Table covers parse fail, ticket gate, predicates, Done-gate, partial closure |
| D6 Assumptions/questions | **PASS** | A-1…A-5 confirmed/open with evidence; Q-1…Q-3 non-blocking with defaults |
| D7 Cross-repository contracts | **PASS** | CTR-01…03 semantic boundaries per impact map §6 |
| D8 NFR applicability | **PASS** | Eight rows specified or N/A with reason |
| D9 As-built alignment | **PASS** | Baseline gaps (unparsed board-status, missing purpose/owner) distinguished from W1+ apply targets |
| D10 Dependency order | **PASS** | W0→W4 + prayog-skills consume-first per impact map §7 |
| D11 Zero unresolved blockers | **PASS** | Impact map §10: none blocking; Q-1…Q-3 non-material |
| D12 Output completeness | **PASS** | Header H4, tables, check summary, outcome, PR readiness present |

**Draft verdict:** **PASS**

**Selected workflow outcome:** `pass`  
**Outcome reason:** D1–D12 PASS; Gate 1 CURRENT on meta #28; zero material open questions; PR READY for Forge `spec-pr-action`.

Do not advance to `/initiative-feasibility` until this artifact is on the Draft spec PR head via Forge publish.

## PR readiness handoff

| Item | Value |
|------|-------|
| Workflow outcome | `pass` — D1–D12 PASS; Gate 1 approved; no material blockers |
| Verdict | **PR READY** |
| Existing spec PR | none |
| Proposed branch | `chore/INIT-GATEFLOW-010-spec-gateflow` |
| Proposed base | `develop` |
| Proposed title | `[INIT-GATEFLOW-010] Spec — eng-lane pin tip executor parity (gateflow)` |
| PR type | **Draft** (entire spec lifecycle) |
| Local artifacts to publish | `docs/specification/product/INIT-GATEFLOW-010-gateflow.md`, `docs/specification/README.md` |
| Forge readiness | fill `handoff.forge` for `open_draft_pr`; recommend `/commit-workspace` then orchestrator `spec-pr-action` |
| Reviewer | @drivestream-lab/prayog-pe-team |
| Initial Gate 2 label | `spec-pending` |
| Additional invalidation label | none |
| Blocking items | none |

**No GitHub side effects have occurred.** Persist the draft locally; authorize Forge publish separately.

### Proposed Draft PR body

```markdown
## Initiative

INIT-GATEFLOW-010 — Engineering-lane pin tip executor parity (gateflow only)

## Meta handoff

- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/28
- Approved meta head: `df0f5a5c09b6c4f951463bb42f277305310aaa80`
- Impact-map revision: 1
- PRD digest: `sha256:457f19617113171c973abdbc15d1afaa00df2f6947ab4567b57d8440bd88b206`
- Repo scope digest: `sha256:09c89c143c14401c8812738c162c05a2f5e504cabafd1818ee72eb4e9b781532`

## Spec path

`docs/specification/product/INIT-GATEFLOW-010-gateflow.md`

## Summary

- REQ-01…02, REQ-10: W0 — parse board-status hops + purpose/owner; 0 BROKEN get_node
- REQ-03…05, REQ-11: W1 — APPLY_FORGE board status + implement In Progress
- REQ-06…08: W2 — create predicates + implement ticket gate
- REQ-09, REQ-16, REQ-19, REQ-17 (partial): W3 — closeout Done + no auto-chain + verify
- REQ-12…15, REQ-17–18, REQ-20: W4 — closure Enter-at + freeze
- Open engineering questions: Q-1…Q-3 (non-blocking; defaults documented)

## Gate 2 — spec package readiness

Initial label: `spec-pending`

- [ ] Spec slice published on this PR head (via Forge `/commit-workspace` / `spec-pr-action`)
- [ ] Feasibility report (later Forge publish)
- [ ] Technical design + ADRs (later Forge publish)
- [ ] Implementation plan §9 (later Forge publish)
- [ ] PE sets `spec-lgtm` on exact final head before merge

Requested reviewer: @drivestream-lab/prayog-pe-team
```

## Developer review

- [ ] Scope matches approved impact-map repo scope digest
- [ ] REQs have condition/event, observable result, and evidence layer
- [ ] Contracts are semantic; no architecture decisions smuggled into REQs
- [ ] No blocking question remains
- [ ] Developer confirmed draft is ready for feasibility

## References

- PRD: `prayog-meta/prd/INIT-GATEFLOW-010.md`
- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/28
- Impact map: `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-010.md`
- As-built: `docs/specification/as-built/implementation-status.md`
- Predecessor freeze: `docs/specification/reports/Feature-Readiness-INIT-GATEFLOW-009.md`

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-draft
  outcome: pass
  artifact:
    path: docs/specification/product/INIT-GATEFLOW-010-gateflow.md
    digest: sha256:7d934b06fc0dbcdfba9a77775a1726670d30922bd0c98e5a5aaf9d74fb2bb64b
  blockers: []
  signals:
    pr_ready: true
    wave_ticket: W0
    map_revision: 1
    source_prd_digest: sha256:457f19617113171c973abdbc15d1afaa00df2f6947ab4567b57d8440bd88b206
    repo_scope_digest: sha256:09c89c143c14401c8812738c162c05a2f5e504cabafd1818ee72eb4e9b781532
    meta_pr_head: df0f5a5c09b6c4f951463bb42f277305310aaa80
    req_count: 20
    open_questions: [Q-1, Q-2, Q-3]
  next_candidates:
    - spec-pr-action
  human_checkpoint: false
  external_action: true
  forge:
    action: open_draft_pr
    draft: true
    apply_labels:
      - spec-pending
    title: "[INIT-GATEFLOW-010] Spec — eng-lane pin tip executor parity (gateflow)"
    body_path: docs/specification/product/INIT-GATEFLOW-010-gateflow.md
```

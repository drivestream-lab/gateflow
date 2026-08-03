# INIT-GATEFLOW-009 — spec slice for gateflow

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-009 |
| PRD | `prayog-meta/prd/INIT-GATEFLOW-009.md` |
| PRD digest | `sha256:76ab22b3c197b9d0cb6b08e6cea379c4e07b3a471b8a88203fddca6014c1c012` |
| Meta PR | https://github.com/drivestream-lab/prayog-meta/pull/23 |
| Meta PR approved head | `6660aa4fefbcd80324cb970aa5bab642d3e5e0a1` |
| Impact map | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-009.md` |
| Impact-map revision | `1` |
| Repo scope digest | `sha256:d0a2b62632113db0fa64cb7d7e63dc393fa5a8217092dda242a99b3392978e9b` |
| Tech-lead approval | @0xbeefdead APPROVED 2026-08-03T10:47:39Z on `6660aa4fefbcd80324cb970aa5bab642d3e5e0a1` — attestation: map_revision 1, prd_digest match, artifact `prd/reports/Impact-Map-INIT-GATEFLOW-009.md` |
| Architecture | [`adr-009-pin-forge-publish-mutate-authority.md`](../adr/adr-009-pin-forge-publish-mutate-authority.md) (**Accepted**); [`adr-010-lane-intake-and-dual-workspace-authority.md`](../adr/adr-010-lane-intake-and-dual-workspace-authority.md) (**Accepted**); pin SSOT [`prayog-skills/workflow.yaml`](../../../prayog-skills/workflow.yaml), [`references/forge-side-effects.md`](../../../prayog-skills/references/forge-side-effects.md), [`delivery-contract.yaml`](../../../prayog-skills/delivery-contract.yaml) |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-03 |
| Status | Draft — dev review required before Forge publish |

## Overview

This initiative **proves** the existing Gateflow factory for the **spec lane** and the
**authorize API** path — it does **not** rebuild coding start, walker, wrap-up,
learning, metrics, or pin design. Programme success means:

1. A spec wave leaves a **Draft Spec PR whose tip contains committed artifacts** from
   automated orchestrated steps (same deliverable a careful human developer would open).
2. A **human reviewer** confirms tip contents; **spec-lane wrap-up** is then
   **live-proven** on that PR through wave sign-off (required — supersedes INIT-007
   REQ-15 PE deferral for **this** initiative exit).
3. A **live** run demonstrates **stop → authorize API → sensitive forge side effect**
   (no IDE typing as the Gateflow human gate).
4. A **feature readiness** freeze record names proven vs deferred capabilities (ops
   portal deferred as next).
5. **Placeholder CI** is replaced with real basic automated PR checks.

**Product intent:** reuse INIT-001…008 control plane, lane starts, forge publish,
automated `spec-pr-action`, closeout (INIT-007), and explicit authorize (INIT-006/008).
Change set is prove-out scripts, records, CI, and as-built — not parallel product APIs.

**Out of scope:** ops portal / gateflow-ops UI; second coding agent; Slack/Teams;
rebuilding implement-lane trust; auto-merge; authorize→resume into the **same** Pass-1
run; skills pin redesign or new RC; inventing approval paths outside **`sdd-delivery/v2`**.

**As-built baseline (2026-08-03):** Implement-lane Pass-1 **human_approved**; INIT-008
W0–W2 **human_approved**; INIT-007 W0–W2 **human_approved** (implement closeout);
`spec-draft` is **`dispatch: orchestrated`** on pin `v0.5.0-rc.2` family; automated
`spec-pr-action` wired; `verify_spec_lane.py` scaffold deepened for W1 dogfood; spec-lane
closeout live **deferred** under 007 Q-6; authorize mutate **unit-complete**, live
**deferred**; CI workflow is **placeholder**; meta PR Gate 1 **approved** on #23 head.

**Delivery waves (product-normative; plan may refine):**

| Wave | Intent | Exit REQs |
|------|--------|-----------|
| **W0** | Confirm skills pin consume-only; meta/fixture + reviewer checklist ready | REQ-1…REQ-2 |
| **W1** | Live **Draft Spec PR tip deliverable** + honest Pass-1 stop + reviewer attestation | REQ-3…REQ-9 |
| **W2** | **Spec wrap-up** live-proven on that PR through wave sign-off | REQ-10…REQ-12 |
| **W3** | **Authorize API** live-proven; feature readiness freeze; basic CI | REQ-13…REQ-20 |

## Functional requirements

| ID | Requirement | PRD source | Condition / event | Observable result | Evidence layer |
|----|-------------|-----------|-------------------|-------------------|----------------|
| REQ-1 | Record and consume the prayog-skills tip in the **`v0.5.0-rc.2` family** only. Harness pin (`agent_skills.ref`) **must match** the submodule commit used at runtime. No pin redesign or new RC in this INIT. | PRD A-01; IM CTR-01; scope digest | Before any W1+ prove-out | Pin load resolves `spec-draft` orchestrated + `spec-pr-action` automated; harness pin == submodule SHA/tag | inspection + unit |
| REQ-2 | W0 prove-out readiness: documented checklist covers meta PR accept preconditions (`meta_pr_url`, approved head, digest match), dual workspace paths (`workspace`, `meta_workspace`), programme token, reviewer tip-inspection steps, and live-verify config knobs. | PRD W0; A-02 | Before W1 live start | Checklist artifact exists under `docs/specification/reports/` or runbook; PE can execute without inventing fixtures | inspection |
| REQ-3 | **`POST /api/v1/waves/spec/start`** accepts when meta accept-gate passes (programme PR + meta folder + digest/head alignment per ADR-010). Rejects fail closed when preconditions fail. | PRD REQ-01; CAP-01; error table | Spec start request with programme token | 202 + `run_id` on success; 4xx + 0 enqueue on reject; no empty Draft Spec PR counted as W1 success | unit + live verify |
| REQ-4 | After each orchestrated **content** hop in spec Pass-1 whose pin marks `forge.commit_workspace: required`, Gateflow publishes produced workspace artifacts to the **run head** before ingest/handoff continuation so the remote tip can accumulate step outputs. | PRD REQ-01; CAP-01; ADR-009 | Successful `spec-draft`, `initiative-feasibility`, and other orchestrated content hops on the active pin graph | Run timeline shows stage commits; remote branch tip advances when files were produced; required-empty publish fails closed | unit + live verify |
| REQ-5 | When the walker reaches automated **`spec-pr-action`**, ForgeClient opens or updates the **Draft Spec PR** without interactive authorize; run record exposes **`pr_number`** (and PR URL derivable). Never apply `*-lgtm` labels. | PRD REQ-01; CAP-01; INIT-008 REQ-12 | Walker outcome `pass` from `spec-draft` with complete `handoff.forge` requires | Draft Spec PR exists; `pr_number` populated on run; projection label `spec-pending` applied per pin | unit + live verify |
| REQ-6 | When a **later** orchestrated content step on the **same** spec Pass-1 run produces new files (e.g. feasibility report), Gateflow commits them onto the **same** PR tip (same run head / head_ref binding). | PRD REQ-01; CAP-01 | Second+ content hop after `spec-pr-action` on same run | PR tip at inspection time includes artifacts from all automated steps executed; not only the first hop | live verify + inspection |
| REQ-7 | Spec Pass-1 walker **stops** at the first honest human/manual boundary on the active pin (e.g. `spec-implementation-plan` with `dispatch: manual`, or a resolved `human-checkpoint`). It does **not** perform merge, set `spec-lgtm`, or invent PE gate approvals. | PRD REQ-01; CAP-01; Non-Goals | Walker reaches manual gate or human-checkpoint | Terminal run status `stopped` at expected node; timeline shows no forbidden forge mutate after stop | unit + live verify |
| REQ-8 | W1 prove-out evidence package includes: run id, PR URL, automated steps executed, and **human reviewer attestation** that the PR tip contains committed outputs from those steps. An **empty** Draft Spec PR (no committed step outputs) **does not** satisfy initiative success. | PRD REQ-01/02; CAP-01/02; Success Criteria | After W1 live run completes | Live-Verify report + reviewer sign-off row; as-built updated | live verify + inspection |
| REQ-9 | **`tests/verify/verify_spec_lane.py`** (opt-in) documents and executes the W1 Pass-1 prove-out: meta accept → orchestrated hops → automated `spec-pr-action` → stop at valid manual/human gate; exit 0 when dogfood knobs enabled. | PRD REQ-01; IM scope; as-built | `features.spec_lane.enabled: true` + worker/API/postgres live | Script exit 0; asserts Cursor success on executed hops, `pr_number` when reached, terminal `stopped` | live verify |
| REQ-10 | After W1 tip confirmation, **spec-lane wrap-up** via existing **`POST /api/v1/waves/closeout/start`** (INIT-007) on **that Draft Spec PR** walks Pass-2: `learning-extract` → `ground-spec` → stop at **`wave-signoff`**. Required for INIT-009 success (not PE-waived). | PRD REQ-02; CAP-02; INIT-007 REQ-7 | Closeout start bound to W1 PR + workspace | Pass-2 timeline stages success; terminal `stopped` at `wave-signoff`; learning/ground artifacts on tip when pin expects | live verify |
| REQ-11 | W2 success **lifts** any prior programme/as-built note that spec-lane wrap-up was skipped or deferred (including INIT-007 REQ-15 deferral **for programme exit of this INIT**). | PRD REQ-02; CAP-02 | W2 live prove-out pass recorded | as-built row shows spec wrap-up **live proven**; deferral note removed or superseded | inspection |
| REQ-12 | W2 prove-out evidence includes PR URL, closeout run id, Pass-2 skill stages, and reviewer confirmation through wave sign-off intent (human merge/sign-off remains human-owned). | PRD REQ-02; CAP-02 | W2 live run complete | Live-Verify report under `docs/specification/reports/` | live verify + inspection |
| REQ-13 | When the next pin node is `external-action` with **`authorization: explicit`** (e.g. `board-tickets-action`), the run **STOPs** with pending forge and performs **no** sensitive side effect until programme **`POST /api/v1/runs/{id}/forge/authorize`** with approval. | PRD REQ-03; CAP-03; INIT-008 REQ-7 | Walker would reach explicit external-action | Run `stopped` with pending forge event; board/merge side effect absent | unit + live verify |
| REQ-14 | Authorize with **`authorized=true`** on the pending explicit action executes the forge side effect (default prove-out: **`create_board_tickets`** when plan §9 + WorkManifest contract pass). Deny, wrong run state, or missing approval performs **no** side effect. | PRD REQ-03; CAP-03; error table | Authorize API called after STOP | Approve path: tickets/issues visible; deny path: unchanged forge state | unit + live verify |
| REQ-15 | W3 prove-out **requires** a recorded **live** run demonstrating stop → authorize API → visible side effect. Paper-only or unit-only waiver is **not** a valid INIT-009 exit. | PRD REQ-03; locked decisions | W3 dogfood execution | Live-Verify report names run id, stop node, authorize call, side-effect evidence | live verify |
| REQ-16 | Publish a **feature readiness freeze** record in this repo listing **proven** capabilities (coding-lane baseline, spec Draft Spec PR deliverable, authorize API path, spec wrap-up, basic CI) vs **deferred** capabilities (ops portal UI, second coding agents, Slack/Teams, programme-wide self-dogfood). Headline language uses **feature names**, not internal horizon nicknames. | PRD REQ-04; CAP-04 | W3 closeout of prove-out programme | Freeze doc under `docs/specification/reports/` (or as-built section) with proven/deferred tables | inspection |
| REQ-17 | The freeze package **includes** a checklist item to update the programme vision/planning note (`prayog-meta/planning/gateflow-programme-vision.md`) in the **same** freeze package — meta hygiene, not a separate affected engineering repo. | PRD REQ-04; locked decision | W3 freeze publication | Freeze checklist references planning note path + owner | inspection |
| REQ-18 | **`docs/specification/as-built/implementation-status.md`** updated to match the feature readiness record and live prove-out outcomes (W1–W3 rows). | PRD REQ-04; Success Criteria | Each wave lands | as-built matrix reflects live/deferred accurately | inspection |
| REQ-19 | Replace placeholder **`.github/workflows/ci.yml`** with **basic automated PR checks** that fail when regressions occur (minimum: repo toolchain — e.g. `make check` and/or `make test` — on pull requests to protected branches). | PRD REQ-05; CAP-05 | PR opened against `develop`/`main` | CI job fails when lint/unit fail; passes on green tree | CI run + inspection |
| REQ-20 | Orchestrated Gateflow prove-out PRs are subject to the same CI fail-closed behaviour. This INIT does **not** invent GitHub branch-protection settings; human-developer PR workflow remains unchanged. | PRD REQ-05; CAP-05 | Gateflow repo PR in prove-out | Required `ci` job reflects real checks, not echo placeholder | inspection |

> **Id convention:** `REQ-*` canonical. This INIT assigns **REQ-1…REQ-20**.
> PRD product ids **`REQ-01…REQ-05`** / **`CAP-01…CAP-05`** are cited in PRD source —
> do not conflate numbering.

**Inherited (unless superseded above):** INIT-001…008 control plane; ADR-009 publish
before ingest; ADR-010 meta intake + dual workspace; INIT-007 closeout route and learning
ingest; INIT-008 dual `authorization`; ForgeClient transport; programme token; never
write `*-lgtm`.

**Explicit non-goals:** rebuild implement lane; ops portal; authorize→resume Pass-1;
IDE confirm prompts as Gateflow authorize; auto-merge; skills package changes.

## Negative and failure paths

| REQ | Condition | Required behavior | Evidence |
|-----|-----------|-------------------|----------|
| REQ-3 | Spec start rejected (missing/invalid meta PR, folder, digest, head) | Fail closed; 0 enqueue; W1 success not claimed | unit + live verify |
| REQ-4 | Required `commit_workspace` with nothing publishable after content hop | Fail closed; run records failure; tip without outputs does not count | unit |
| REQ-4 | Forge/commit I/O error mid-walk | Run failure recorded; incomplete tip does not satisfy REQ-8 | live verify |
| REQ-5 | Automated `spec-pr-action` with incomplete `handoff.forge` requires | Fail closed; no PR; no silent success | unit |
| REQ-7 | Walker attempts merge or approval label mutate | Must not occur | unit + inspection |
| REQ-8 | Empty Draft Spec PR opened | Does **not** satisfy W1 / initiative KPI | inspection |
| REQ-10 | Closeout start without valid PR bind / workspace | 4xx; 0 enqueue | unit |
| REQ-13 | Sensitive step reached | STOP before side effect | unit + live verify |
| REQ-14 | Authorize deny / wrong state / timeout | No forge side effect; W3 not passed until live path works | unit + live verify |
| REQ-19 | CI check failure on PR | Workflow run conclusion failure | CI |

## Out of scope for this repo

- **gateflow-ops** / ops portal BFF UI (deferred — next initiative after freeze)
- **prayog-skills** pin authoring or new RC (consume `v0.5.0-rc.2` family only)
- **prayog-meta** engineering delivery (PRD/map hosting only; optional planning note update is programme hygiene in freeze package)
- Rebuilding coding-lane walker, metrics, or second AgentRunner
- Auto-merge, authorize→resume Pass-1, IDE prompts as authorize substitute
- Exhaustive all-skills matrix bake-off (one honest spec path suffices)

## Cross-service contracts

| Contract ID | Provider / owner | Consumer / owner | Entry point | Input shape | Output shape | Invariants | Errors | Compatibility / versioning | Contract-test location |
|-------------|------------------|------------------|-------------|-------------|--------------|------------|--------|----------------------------|------------------------|
| CTR-01 | prayog-skills / PE | gateflow | Pinned `sdd-delivery/v2` workflow + handoff envelope | pin YAML + delivery contract | orchestrated spec lane graph | Consume only; no pin redesign | Invalid/missing pin ⇒ fail closed | `v0.5.0-rc.2` family | `test_handoff_workflow`, pin load tests |
| CTR-02 | gateflow / PE | GitHub (forge) | `commit_workspace` + automated `open_draft_pr` on run head | paths, title/body/head/base | commit SHA, PR number, projection labels | Never `*-lgtm`; no merge action | I/O ⇒ fail closed | ADR-003; INIT-008 automated | `test_forge_client`, walker tests |
| CTR-03 | gateflow / PE | GitHub / board | `POST …/forge/authorize` → explicit forge (e.g. `create_board_tickets`) | authorized flag + run context | issues/labels created | Explicit only; worker isolation elsewhere | Deny/wrong state ⇒ no mutate | INIT-006/008 | `test_forge_action_service`, live verify |
| CTR-04 | gateflow / PE | programme callers | `POST /api/v1/waves/spec/start` + meta accept-gate | meta PR URL/head + dual workspace + identity | run accepted | ADR-010 intake authority | Precondition fail ⇒ 4xx | Additive fields only | `test_meta_pr_intake`, `verify_spec_lane` |
| CTR-05 | gateflow / PE | programme callers | `POST /api/v1/waves/closeout/start` | PR bind + workspace + branch targeting | Pass-2 run to `wave-signoff` | New run; fixed Enter-at `learning-extract` | 4xx/409 fail closed | INIT-007 | `test_wave_closeout`, live verify |

## Non-functional requirements

| Area | Requirement or N/A rationale | Acceptance / evidence |
|------|------------------------------|-----------------------|
| Security | Programme token on starts/authorize; no `*-lgtm` auto-apply; production forge via GitHub App/ForgeClient (not `gh` cloud success path) | unit + inspection |
| Reliability | Fail closed on meta accept miss, required-empty publish, incomplete forge requires, authorize deny | unit + live verify |
| Performance / capacity | N/A — prove-out correctness over cycle-time KPIs (PRD excludes numeric cycle-time exit gates) | inspection |
| Observability | Run timeline records api_trigger, stage commits, automated/explicit forge, terminal stop reason + handoff context | live verify |
| Privacy / data handling | PR bodies from workspace paths; no secrets in commits or freeze records | inspection |
| Migration / compatibility | Additive prove-out scripts/reports/CI; no breaking API removal | inspection |
| Rollback / recovery | Disable spec/closeout routes or worker; prior human_approved lanes remain baseline | runbook inspection |
| Operations / support | Document W0 checklist, `verify_spec_lane`, closeout sequence, authorize dogfood in `tests/README.md` + reports | docs |

## Assumptions

| ID | Assumption | Evidence | Owner | Status | Invalidated when |
|----|------------|----------|-------|--------|------------------|
| A-1 | Skills tip `v0.5.0-rc.2` family is remounted/consumed for prove-outs | PRD A-01; IM CTR-01 | PE | confirmed | Pin family changes |
| A-2 | Meta PR #23 Gate 1 approval on head `6660aa4…` remains valid for spec start preconditions | Meta PR review + `impact-map-lgtm` | PE | confirmed | Map revision stale / head moves without re-approval |
| A-3 | PE can call authorize API with programme service token | PRD A-03; as-built | PE | confirmed | Auth model changes |
| A-4 | Production forge uses GitHub App / ForgeClient | PRD A-04; ADR-003 | PE | confirmed | Transport swap |
| A-5 | Gate 1 follows **`sdd-delivery/v2`** meta PR path | PRD A-05; locked decisions | PE | confirmed | Alternate ceremony invented |
| A-6 | INIT-007 closeout route is sufficient for W2 (no new closeout API) | INIT-007 delivered W0–W2 | PE | confirmed | Product splits spec closeout |
| A-7 | W1 minimum automated path follows active pin (orchestrated `spec-draft` → automated `spec-pr-action` → orchestrated feasibility chain → manual/human stop) | `verify_spec_lane.py`; pin rc.2 | PE | confirmed | Pin graph changes |
| A-8 | W3 authorize prove-out uses **`board-tickets-action`** unless PE selects another explicit node | Pin day-one explicit set | PE | open | PE names alternate explicit action |

## Spec questions (ambiguities — need PM or domain confirmation before feasibility)

| ID | Lane | Question | Owner | Blocking | Required by | Default if deferred | Status | Resolution link |
|----|------|----------|-------|----------|-------------|---------------------|--------|-----------------|
| Q-1 | PE | W1 live prove-out: is **`initiative-feasibility` pass → `spec-technical-review`** on the active pin part of the minimum success path, or is stop at **`spec-implementation-plan`** after feasibility sufficient? | PE | no | W1 / verify script | Follow **`verify_spec_lane`** happy chain on active pin (includes feasibility; stop at first manual/human gate reached) | open | `tests/verify/verify_spec_lane.py` |
| Q-2 | PE | W3 authorize prove-out: confirm **`board-tickets-action`** as the live side-effect target (vs another explicit node). | PE | no | W3 live verify | **`create_board_tickets`** after plan §9 WorkManifest contract pass | open | A-8 |
| Q-3 | PE | Freeze record location: standalone report vs as-built-only section? | PE | no | W3 | **`docs/specification/reports/Feature-Readiness-INIT-GATEFLOW-009.md`** + as-built summary row | open | REQ-16 |
| Q-4 | PE | CI minimum bar: **`make check` + `make test`** sufficient for REQ-19, or add branch-name lint job? | PE | no | W3 / CI PR | **`make check` && `make test`** on `ubuntu-latest` with Poetry setup | open | REQ-19 |

## Draft check summary (D1–D12)

| Check | Status | Evidence / findings |
|-------|--------|---------------------|
| D1 Approved handoff current | **PASS** | Meta PR #23 head `6660aa4…` = tech-lead APPROVED review commit; prd_digest + map_revision 1 match; gateflow affected, not deferred; scope digest recorded |
| D2 Complete PRD traceability | **PASS** | CAP-01…05 / PRD REQ-01…05 each map to REQ-3…20 (plus W0 REQ-1…2); every REQ cites PRD CAP/REQ or § |
| D3 Repo-bounded scope | **PASS** | gateflow prove-out only; gateflow-ops/prayog-skills/meta eng delivery excluded |
| D4 Observable acceptance | **PASS** | Every REQ has condition/event, observable result, evidence layer |
| D5 Negative/failure paths | **PASS** | Table covers start reject, publish fail, empty PR, authorize deny, CI fail |
| D6 Assumptions/questions | **PASS** | A-1…A-8 with status; Q-1…Q-4 non-blocking with defaults |
| D7 Cross-repository contracts | **PASS** | CTR-01…05 semantic boundaries |
| D8 NFR applicability | **PASS** | Eight rows |
| D9 As-built alignment | **PASS** | Baseline vs prove-out targets distinguished (spec wrap-up + authorize live deferred today) |
| D10 Dependency order | **PASS** | W0 → W1 → W2 → W3 per impact map §7; skills pin consume first |
| D11 Zero unresolved blockers | **PASS** | Impact map §10: none blocking; Q-1…Q-4 non-material with defaults |
| D12 Output completeness | **PASS** | Header digests, tables, check summary, outcome, PR readiness, handoff |

**Draft verdict:** **PASS**

**Selected workflow outcome:** `pass`  
**Outcome reason:** D1–D12 PASS; Gate 1 CURRENT on meta #23; zero material open questions; PR READY for Forge `spec-pr-action`.

Do not advance to `/initiative-feasibility` until this artifact is on the Draft spec PR head via Forge publish.

## PR readiness handoff

| Item | Value |
|------|-------|
| Workflow outcome | `pass` — D1–D12 PASS; Gate 1 approved; no material blockers |
| Verdict | **PR READY** |
| Existing spec PR | none |
| Proposed branch | `chore/INIT-GATEFLOW-009-spec-gateflow` |
| Proposed base | `develop` |
| Proposed title | `[INIT-GATEFLOW-009] Spec — both-lane factory prove-out (gateflow)` |
| PR type | **Draft** (entire spec lifecycle) |
| Local artifacts to publish | `docs/specification/product/INIT-GATEFLOW-009-gateflow.md`, `docs/specification/README.md` |
| Forge readiness | fill `handoff.forge` for `open_draft_pr`; recommend `/commit-workspace` then orchestrator `spec-pr-action` |
| Reviewer | @drivestream-lab/prayog-pe-team |
| Initial Gate 2 label | `spec-pending` |
| Additional invalidation label | none |
| Blocking items | none |

**No GitHub side effects have occurred.** Persist the draft locally; authorize Forge publish separately.

### Proposed Draft PR body

```markdown
## Initiative

INIT-GATEFLOW-009 — Both-lane delivery factory prove-out (gateflow only)

## Meta handoff

- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/23
- Approved meta head: `6660aa4fefbcd80324cb970aa5bab642d3e5e0a1`
- Impact-map revision: 1
- PRD digest: `sha256:76ab22b3c197b9d0cb6b08e6cea379c4e07b3a471b8a88203fddca6014c1c012`
- Repo scope digest: `sha256:d0a2b62632113db0fa64cb7d7e63dc393fa5a8217092dda242a99b3392978e9b`

## Spec path

`docs/specification/product/INIT-GATEFLOW-009-gateflow.md`

## Summary

- REQ-1…9: W0 readiness + live Draft Spec PR tip deliverable (orchestrated spec Pass-1 + automated spec-pr + honest stop)
- REQ-10…12: required spec-lane wrap-up live prove-out on that PR
- REQ-13…15: live authorize API stop → approve → side effect
- REQ-16…18: feature readiness freeze + as-built
- REQ-19…20: replace placeholder CI with basic automated checks
- Open engineering questions: Q-1…Q-4 (non-blocking; defaults documented)

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

- PRD: `prayog-meta/prd/INIT-GATEFLOW-009.md` @ meta PR #23
- Impact map: `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-009.md` revision 1
- Predecessors: INIT-007 (closeout), INIT-008 (automated forge), INIT-006 (forge authority)
- Verify: `tests/verify/verify_spec_lane.py` (W1); closeout / authorize live (W2–W3)

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-draft
  outcome: pass
  artifact:
    path: docs/specification/product/INIT-GATEFLOW-009-gateflow.md
    digest: sha256:d2f937b8a168540e46bc48da11127be69811ed776e035f627590e1a9860dc8e3
  blockers: []
  signals:
    pr_ready: true
    initiative: INIT-GATEFLOW-009
    meta_pr: "https://github.com/drivestream-lab/prayog-meta/pull/23"
    meta_pr_head: "6660aa4fefbcd80324cb970aa5bab642d3e5e0a1"
    map_revision: 1
    prd_digest: "sha256:76ab22b3c197b9d0cb6b08e6cea379c4e07b3a471b8a88203fddca6014c1c012"
    scope_digest: "sha256:d0a2b62632113db0fa64cb7d7e63dc393fa5a8217092dda242a99b3392978e9b"
    d_checks: pass
    nonblocking_questions: "Q-1,Q-2,Q-3,Q-4"
  next_candidates:
    - spec-pr-action
  human_checkpoint: false
  external_action: true
  forge:
    action: open_draft_pr
    draft: true
    apply_labels:
      - spec-pending
    title: "[INIT-GATEFLOW-009] Spec — both-lane factory prove-out (gateflow)"
    body_path: docs/specification/product/INIT-GATEFLOW-009-gateflow.md
```

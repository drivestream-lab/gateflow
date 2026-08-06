# INIT-GATEFLOW-008 — spec slice for gateflow (006A forge authorization)

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-008 |
| Brand / lineage | **006A** — follow-on to INIT-GATEFLOW-006 forge authority (wire id must be `INIT-{COMPONENT}-{digits}`; `006A` is not a valid wave-start id) |
| PRD | **PE-waived Gate 1** — pin-consume catch-up (006A); no `prayog-meta` PRD or Impact-Map required for this draft (same posture as INIT-GATEFLOW-006). Traceability to pin `for-gateflow.md` + forge-side-effects + delivery-contract. |
| PRD digest | **waived** — no meta PRD (Q-1 resolved 2026-07-30) |
| Meta PR | **waived** |
| Meta PR approved head | **waived** |
| Impact map | **waived** — no Impact-Map-INIT-GATEFLOW-008 |
| Impact-map revision | **waived** |
| Repo scope digest | **waived** — gateflow-only intended (pin consume) |
| Tech-lead approval | **PE waive Gate 1** recorded in Spec Q-1 (2026-07-30); formal Gate 2 package still PE-owned |
| Architecture | [`adr-009-pin-forge-publish-mutate-authority.md`](../adr/adr-009-pin-forge-publish-mutate-authority.md) (**Accepted** — **must amend or supersede** for dual `authorization`); [`adr-010-lane-intake-and-dual-workspace-authority.md`](../adr/adr-010-lane-intake-and-dual-workspace-authority.md) (**Accepted**); pin SSOT [`prayog-skills/docs/for-gateflow.md`](../../../prayog-skills/docs/for-gateflow.md), [`references/forge-side-effects.md`](../../../prayog-skills/references/forge-side-effects.md), [`delivery-contract.yaml`](../../../prayog-skills/delivery-contract.yaml) |
| Repo | drivestream-lab/gateflow |
| Date | 2026-07-30 |
| Status | Draft — **`/spec-draft` outcome `pass`** (Gate 1 waived Q-1); PR READY for Forge `spec-pr-action`; ADR-009 amend still required before implement |

## Overview

Prayog-skills remounted the delivery pin with two Gateflow-facing contract changes
that **break** INIT-GATEFLOW-006 product language and ADR-009 consequences as
written:

1. **`authorization: explicit | automated`** on every `external-action` (required;
   missing/unknown → invalid pin). Day-one: `spec-pr-action` and `wave-pr-action`
   are **`automated`**; board / PRD / merge external-actions remain **`explicit`**.
2. **Implement Pass-1 Draft PR placement:** after coding, not before:
   `pre-implement` → `loop-spec` → `wave-pr-action` → `wave-acceptance`, with
   `commit_workspace: required` on both content hops. No interactive STOP between
   checklist and coding. First Draft PR tip already has checklist + code.

This INIT productizes Gateflow **consume** of that pin: parse, walker/ForgeClient
algorithm, retirement of implement **PR-at-start** as Draft PR creator, run-context
`head_ref` / `base_ref` for automated `open_draft_pr`, and WorkManifest
`prayog/v1` + pinned validator before board create.

**Product intent:** programme `implement/start` (one call) walks uninterrupted
through coding; ForgeClient opens the wave Draft PR when pin says `automated`
and requires are complete; humans still own `wave-acceptance`, `wave-signoff`, and
all `explicit` external-actions (authorize API). Content skills never mutate.
Pin remains policy SSOT — no laptop overlay, no env backdoor that reinterprets
`explicit` as automated.

**Why before INIT-007:** closeout / learning (007) dogfood needs a sane Pass-1
PR story (no early empty PR, automated wave open after code). **Do not** live-prove
INIT-007 until this INIT is implemented. After this INIT lands, **prove INIT-007
first** (Pass-1 + closeout path), not a separate 008 live circus unless TDD adds one.

**Out of scope:** INIT-007 closeout/learning implementation; C2 (probes,
security-gate, parallel_safe, auto-merge / delete_branch); env or API flags that
override pin `authorization`; inventing merge Forge actions; skill `git commit` /
`gh` as success; Gateflow-local WorkManifest schema as SSOT.

**As-built baseline (2026-07-30):** Submodule may already contain the new pin tip
while `.harness-pin.yaml` still names `v0.5.0-rc.2` — **harness pin record must
match consumed SHA/tag** before claiming remount. Gateflow still treats all
`external-action` as STOP and opens Draft PRs via PR-at-start. INIT-006 REQ-7
(“always STOP until authorize”) is **superseded** by this INIT for `automated`
nodes only.

**Delivery waves (product-normative; plan may refine):**

| Wave | Intent | Exit REQs |
|------|--------|-----------|
| **W0** | Remount pin record; parse required `authorization`; fail closed on omit/unknown; ADR-009 amendment Draft→Accepted path started | REQ-1…REQ-4 |
| **W1** | Post-hop Forge algorithm: `explicit` STOP+authorize vs `automated` ForgeClient.apply; Pass-1 edges; retire implement PR-at-start; head/base from run context | REQ-5…REQ-12 |
| **W2** | WorkManifest `prayog/v1` + pinned contract validator before `create_board_tickets`; as-built + verify map; unit prove automated wave/spec PR (live Pass-1 prove deferred to INIT-007 dogfood) | REQ-13…REQ-17 |

## Functional requirements

| ID | Requirement | Source | Acceptance criteria | Evidence type |
|----|-------------|--------|---------------------|---------------|
| REQ-1 | Remount / record the prayog-skills tip that defines `authorization` and Pass-1 `wave-pr-action` placement. `.harness-pin.yaml` `agent_skills.ref` (tag or immutable SHA) **must match** the submodule commit consumed at runtime. No laptop overlay of `workflow.yaml`. | Pin for-gateflow; SDD remount | Pin load in tests/CI resolves nodes `wave-pr-action`, `authorization` on all external-actions; harness pin == submodule | unit + inspection |
| REQ-2 | Parse pin `nodes[<id>].authorization` for every `type: external-action`. Allowed values: **`explicit`** \| **`automated`**. Missing or unknown → **fail closed** (no schema default). | delivery-contract `forge.external_action.authorization`; forge-side-effects | Unit: omit/unknown reject; day-one matrix: `wave-pr-action`/`spec-pr-action` = automated; board/prd/merges = explicit | unit |
| REQ-3 | Carry `authorization` on resolved workflow node types used by policy/orchestrator (not only raw YAML). | ADR-009 amend; pin algorithm | Unit: `get_node` / resolve exposes enum | unit |
| REQ-4 | **Amend ADR-009** (or superseding ADR Accepted in this INIT) so external-action mutate is gated by pin `authorization`: `explicit` ⇒ interactive/programme authorize then ForgeClient; `automated` ⇒ ForgeClient when requires complete, **no** interactive STOP. Content skills still never mutate; no merge Forge action. | ADR-009 Accepted text conflict | ADR file Accepted with dual mode; INIT-006 REQ-7 marked superseded in as-built/006 note | inspection |
| REQ-5 | After a successful content hop, apply pin `forge.commit_workspace` via ForgeClient to the **run head** (existing ADR-009 / INIT-006 publish path). `pre-implement` and `loop-spec` are **`required`** on the remounted pin — empty publish fail closed. | Pin workflow; forge-side-effects algorithm | Unit: required empty fails; dirty∪ahead publish still valid | unit |
| REQ-6 | Resolve next node from pin `(stage, outcome)`. **Do not** treat “all `external-action` ⇒ STOP” as true. | Pin for-gateflow hard rule 5 | Unit: policy/orchestrator branches on `authorization` | unit |
| REQ-7 | When next is `external-action` with **`authorization: explicit`**: STOP with pending forge; mutate only via existing programme **`POST /api/v1/runs/{id}/forge/authorize`** (`authorized=true`) or documented dual-executor human forge path. | INIT-006 REQ-8 retain for explicit | Unit: board-tickets / prd-pr still STOP; authorize executes | unit |
| REQ-8 | When next is `external-action` with **`authorization: automated`**: **no** interactive STOP and **no** require `/forge/authorize` for that hop. Merge pin ⋉ handoff; if any pin `forge.requires` slot missing → **fail closed**. Else ForgeClient.apply (`open_draft_pr` / future actions) in the orchestrator path, then continue `outcomes.pass`. | Pin algorithm; day-one automated nodes | Unit walker: after `loop-spec` publish, automated `wave-pr-action` opens PR without authorize mock; continues toward `wave-acceptance` STOP | unit |
| REQ-9 | For automated (and explicit) `open_draft_pr`, bind **`head_ref` / `base_ref` from run context** (wave-start identity / stored targeting) when pin `requires` lists them. Handoff supplies instance slots such as `title` / `body_path`. Do not invent pin `forge.head` enums. | Pin wave-pr requires; ADR-009 head binding | Unit: missing run head/base → fail closed; same head used for both prior `commit_workspace` hops and open | unit |
| REQ-10 | **Retire PR-at-start Draft PR create** for implement jobs (and for spec jobs that open via `spec-pr-action`). Must not skip or duplicate `wave-pr-action` / `spec-pr-action`. Optional **ensure_branch-only** before first publish is allowed; PR create only via Forge `open_draft_pr`. | Pin for-gateflow; partner remount note | Unit: implement start does not call create PR before skills; PR number appears after automated/explicit open | unit |
| REQ-11 | Implement Pass-1 walk (remounted pin): Enter-at `pre-implement` → required publish → `loop-spec` → required publish → automated `wave-pr-action` → STOP `wave-acceptance` → park `wave-awaiting-closeout` on pass. **No** authorize STOP between `pre-implement` and `loop-spec`. | Pin Pass-1 | Unit multi-hop; verify feature map updated | unit |
| REQ-12 | Spec Draft PR: when pin marks `spec-pr-action` **automated**, same automated apply rules as REQ-8 (after `spec-draft` required publish). Explicit nodes unchanged. | Pin day-one | Unit: automated spec-pr path without authorize | unit |
| REQ-13 | Before `create_board_tickets`, validate plan §9 WorkManifest via the **pinned** contract (`delivery-contract.yaml` → `workmanifest_spec` + `scripts/workmanifest_contract.py`). Accept only **`apiVersion: prayog/v1`** + **`kind: WorkManifest`**. Reject `launchpad/v1` and unsupported pairs fail closed. | Pin WorkManifest Initiative B | Unit: reject launchpad/v1; pass prayog/v1 fixture | unit |
| REQ-14 | BoardService **projects** epic/wave/task text onto issues; board bodies are **not** a second WorkManifest SSOT. Do **not** write runtime status/observed evidence into the approved manifest. | Pin for-gateflow | Inspection + unit: create path does not mutate approved manifest intent fields | unit + inspection |
| REQ-15 | Honor pin board prereq naming for contract pass (e.g. `workmanifest-contract-pass` when present on `board-tickets-action`). `create_board_tickets` remains **`authorization: explicit`**. | Pin workflow | Unit: explicit STOP + authorize still required for board seed | unit |
| REQ-16 | Update as-built + `tests/README.md` feature map: dual authorization; Pass-1 edges; PR-at-start removed; WorkManifest pin validator; mark INIT-006 REQ-7 superseded for automated nodes. | SDD | Docs rows match code | inspection |
| REQ-17 | **Ordering vs INIT-007:** do not claim INIT-007 Pass-1 live dogfood complete until this INIT’s W0–W1 behavior is on `develop`. After this INIT merges, **first** live prove-it priority is INIT-007 (which exercises Pass-1 including automated wave PR as a prerequisite). Dedicated 008 live verify is optional if 007 prove covers the chain. | PE sequencing 2026-07-30 | As-built / plan state this dependency | inspection |

> **Id convention:** `REQ-*` canonical. This INIT assigns **REQ-1…REQ-17**.
> Traceability: prayog-skills remount notes, `for-gateflow.md`, forge-side-effects
> consumer algorithm, delivery-contract, INIT-006 (supersede REQ-7 for automated),
> ADR-009 amendment.

**Inherited (unless superseded above):** INIT-001…006 control plane, lane starts,
BOUNDINPUT, ForgeClient transport, dual executor for **explicit** nodes, sparse
notifier, programme token. INIT-007 closeout/learning REQs remain separate and
**blocked for dogfood** until this INIT is implemented.

**Explicit non-goals:** env/`auto_open_draft_pr` API that overrides pin
`authorization`; treating `outcomes.pass` alone as skip-STOP; ForgeClient merge;
C2 capabilities; implementing INIT-007 inside this INIT.

## Negative and failure paths

| REQ | Condition | Required behavior | Evidence |
|-----|-----------|-------------------|----------|
| REQ-1 | Harness pin SHA ≠ submodule / overlay YAML | Fail closed or refuse “remounted” claim; no silent drift | inspection |
| REQ-2 | External-action missing `authorization` | Pin load / get_node fails | unit |
| REQ-5 | Required `commit_workspace` with nothing to publish | Fail closed; do not open PR / advance as success | unit |
| REQ-8 | Automated node with incomplete `handoff.forge` requires | Fail closed; no PR; no fake STOP waiting forever | unit |
| REQ-9 | Automated open without run head/base | Fail closed | unit |
| REQ-10 | PR-at-start still creates Draft PR on implement | Must not occur after this INIT | unit |
| REQ-13 | `launchpad/v1` or bad kind | Reject before board create | unit |
| REQ-7 / REQ-15 | Authorize on wrong node / `authorized=false` | 4xx; no mutate | unit |

## Out of scope for this repo

- **INIT-GATEFLOW-007** closeout HTTP / learning DB (implement after this INIT; dogfood 007 first thereafter)
- Authoring prayog-skills packages (consume remount only)
- Env or API flags that reinterpret `explicit` as automated
- Auto-merge / `delete_branch` / merge Forge action
- C2 probes, security-gate/T13, `parallel_safe`
- gateflow-ops UI; second AgentRunner
- Gate 1 meta PRD authoring (see Spec questions)

## Cross-service contracts

| Contract ID | Provider / owner | Consumer / owner | Entry point | Input shape | Output shape | Invariants | Errors | Compatibility | Contract-test location |
|-------------|------------------|------------------|-------------|-------------|--------------|------------|--------|---------------|------------------------|
| CTR-01 | prayog-skills / PE | gateflow | Pin `authorization` + forge-side-effects algorithm | pin YAML | explicit STOP vs automated apply | Missing authorization invalid; pin SSOT | Fail closed | Active pin tip | `test_forge_policy`, walker tests |
| CTR-02 | gateflow / PE | GitHub | ForgeClient `commit_workspace` / `open_draft_pr` | paths / title/body/head/base | commit SHA, PR number | No `*-lgtm`; no merge action; content ≠ mutate | I/O ⇒ fail closed | ADR-003 | `test_forge_client`, forge action tests |
| CTR-03 | prayog-skills / PE | gateflow | WorkManifest contract + validator | plan §9 YAML | validated manifest | `prayog/v1` only; board projection ≠ SSOT | Unsupported version ⇒ fail closed | Pin delivery-contract | unit validator + board authorize |
| CTR-04 | gateflow / PE | programme | `POST …/forge/authorize` | authorized + workspace + head/base | mutate result | **Required only for `explicit`** | Wrong state ⇒ 4xx | INIT-006 retain | `test_forge_action_service` |

Inherited: INIT-006 CTR forge publish; INIT-005 baton; lane start APIs (ADR-010).

## Non-functional requirements

| Area | Requirement or N/A rationale | Acceptance / evidence |
|------|------------------------------|-----------------------|
| Security | Programme token on starts/authorize; secrets never published; no `*-lgtm`; automated mutate still ForgeClient-only | unit + inspection |
| Reliability | Fail closed on missing authorization, incomplete requires, required empty publish | unit |
| Performance / capacity | N/A new SLAs | inspection |
| Observability | Timeline events for stage_commit and automated/explicit forge apply; structured logs with authorization mode | unit |
| Privacy / data handling | PR titles/bodies from workspace paths — no secret materialization | inspection |
| Migration / compatibility | Open initiatives stay on old pin until explicit remount; document INIT-006 REQ-7 supersession | docs |
| Rollback / recovery | Pin rollback or disable worker; explicit authorize remains for board | runbook inspection |
| Operations / support | One implement start for Pass-1 PR when automated; authorize still for explicit nodes | docs / README |

## Assumptions

| ID | Assumption | Evidence | Owner | Status | Invalidated when |
|----|------------|----------|-------|--------|------------------|
| A-1 | Pin tip with `authorization` + post-`loop-spec` `wave-pr-action` is the consume target | prayog CHANGELOG / for-gateflow / workflow.yaml | PE | confirmed | Pin reverts placement |
| A-2 | Day-one automated set is only `spec-pr-action` + `wave-pr-action` | Pin day-one table | PE | confirmed | Pin flips more nodes to automated |
| A-3 | ADR-009 can be amended in-repo under this INIT without waiting for a new meta PRD | 006 catch-up posture; **Q-1 Gate 1 waived 2026-07-30** | PE | **confirmed** | PE rescinds waive |
| A-4 | INIT-007 dogfood waits until this INIT is on `develop` | PE sequencing 2026-07-30 | PE | confirmed | PE reorders |
| A-5 | `head_ref`/`base_ref` may be satisfied from run context without copying into handoff YAML | Partner remount + ADR-009 head binding | PE | confirmed | Pin requires handoff-only slots |
| A-6 | Skills leave dirty trees; Forge publishes (no skill git commit) | Partner + #89 | PE | confirmed | Skills regain local commit duty |

## Spec questions (ambiguities — need PE confirmation)

| ID | Lane | Question | Owner | Blocking | Required by | Default if deferred | Status | Resolution link |
|----|------|----------|-------|----------|-------------|---------------------|--------|-----------------|
| Q-1 | PE | Gate 1: retrospective meta PRD + Impact-Map for INIT-GATEFLOW-008 (006A) with APPROVED head, **or** explicit PE waive of Gate 1 for pin-consume catch-up (same posture as INIT-006 draft)? | PE | **yes** (was material for `/spec-draft` `pass`) | feasibility / board-seed | — | **resolved** | **PE waive Gate 1** (2026-07-30) — proceed on pin docs; no meta Impact-Map required for this INIT draft |
| Q-2 | PE | Amend ADR-009 in place vs new ADR-011 superseding dual authorization? | PE | no | technical review | Prefer **amend ADR-009** with dual mode; keep one forge authority ADR | open | — |
| Q-3 | PE | Ensure-branch-only before first publish — required or optional? | PE | no | plan / W1 | **Yes** ensure_branch from base; never create PR at start | open | — |
| Q-4 | PE | Exact harness pin string (new tag vs SHA `355f403` / successor)? | PE | no | W0 remount | Pin immutable SHA until tag cut; update harness when tagged | open | — |
| Q-5 | PE | Is a dedicated `verify_implement_lane` assert for automated PR required in 008, or is INIT-007 live prove sufficient evidence? | PE | no | W2 | Unit in 008; live chain evidence via **007 dogfood first** after merge | open | — |

## Draft check summary (D1–D12) — `/spec-draft` re-run 2026-07-30

| Check | Status | Evidence / findings |
|-------|--------|---------------------|
| D1 Approved handoff current | **PASS (waived)** | Q-1 **PE waive Gate 1** (2026-07-30). CURRENT handoff = pin `for-gateflow.md` + forge-side-effects + delivery-contract + this INIT (same posture as INIT-006 draft). |
| D2 Complete PRD traceability | **PASS (waived PRD)** | Every REQ cites pin section / INIT-006 supersession / ADR-009 amend need under waive |
| D3 Repo-bounded scope | PASS | gateflow consume only; pin authored upstream; 007 out of scope |
| D4 Observable acceptance | PASS | Acceptance criteria + evidence type on REQ-1…17 |
| D5 Negative/failure paths | PASS | Negative table present |
| D6 Assumptions/questions | PASS | A-1…A-6 confirmed/open appropriately; **zero material** open questions (Q-1 resolved; Q-2…Q-5 non-blocking + defaults) |
| D7 Cross-repository contracts | PASS | CTR-01…04 |
| D8 NFR applicability | PASS | Eight rows |
| D9 As-built alignment | PASS | Baseline vs target called out; 008 not started in code |
| D10 Dependency order | PASS | W0 remount/parse/ADR → W1 algorithm/PR-at-start → W2 WorkManifest/docs; 007 after implement |
| D11 Zero unresolved blockers | PASS | No material Gate/PM blockers; ADR-009 amend is REQ-4 / TDD work (not a spec-draft blocker) |
| D12 Output completeness | PASS | Header, waves, REQs, NFR, contracts, questions, PR readiness, handoff+forge |

**Draft verdict:** **PASS**

**Selected workflow outcome:** `pass`  
**Outcome reason:** D1–D12 PASS under Gate 1 waive; zero unresolved material questions; sources CURRENT for waived handoff; PR READY for Forge publish.

Next pin node: **`spec-pr-action`** (`authorization: automated`). Do **not** implement product code from this skill. Refresh `/initiative-feasibility` after Draft PR head has this artifact (expect `findings` for ADR-009). INIT-007 dogfood remains blocked until this INIT is implemented.

## PR readiness handoff

| Item | Value |
|------|-------|
| Workflow outcome | `pass` — Gate 1 waived; D-checks PASS |
| Verdict | **PR READY** |
| Existing spec PR | none |
| Proposed branch | `chore/INIT-GATEFLOW-008-spec-gateflow` |
| Proposed base | `develop` |
| Proposed title | `[INIT-GATEFLOW-008] Spec — 006A forge authorization + wave-pr after loop-spec` |
| PR type | **Draft** |
| Local artifacts to publish | `docs/specification/product/INIT-GATEFLOW-008-gateflow.md` (primary); also README + as-built pointer rows if co-published |
| Forge readiness | `handoff.forge` filled below for `open_draft_pr`; recommend `/commit-workspace` then automated `spec-pr-action` / `/open-draft-pr` — **not** inside this skill |
| Reviewer | @drivestream-lab/prayog-pe-team |
| Initial Gate 2 label | `spec-pending` |
| Additional invalidation label | none |
| Blocking items | none for publish; ADR-009 amend before **implement** |

**No GitHub side effects from `/spec-draft`.**

### Proposed Draft PR body

```markdown
## Initiative

INIT-GATEFLOW-008 — 006A forge authorization + Pass-1 wave-pr placement

## Meta handoff

- Meta PRD PR: **waived** (Q-1 Gate 1 waive 2026-07-30)
- Approved meta head: **waived**
- Impact-map revision: **waived**
- PRD digest: **waived** — trace pin `for-gateflow.md` + forge-side-effects
- Repo scope digest: **waived** — gateflow-only pin consume

## Spec path

`docs/specification/product/INIT-GATEFLOW-008-gateflow.md`

## Summary

- REQ-1…REQ-17 — pin `authorization` dual mode; automated wave/spec PR; retire PR-at-start; WorkManifest prayog/v1
- Blocks INIT-007 dogfood until implemented; then prove 007 first
- Open non-blocking: Q-2…Q-5 (defaults recorded)

## Gate 2 — spec package readiness

Initial label: `spec-pending`

- [ ] Spec slice published on this PR head (via Forge `/commit-workspace` / `spec-pr-action`)
- [ ] Feasibility report (later Forge publish)
- [ ] Technical design + ADR-009 amend (later Forge publish)
- [ ] Implementation plan §9 (later Forge publish)
- [ ] PE sets `spec-lgtm` on exact final head before merge

Requested reviewer: @drivestream-lab/prayog-pe-team
```

## Developer review

- [x] Scope matches waived Gate 1 / pin-consume boundary
- [x] REQs have acceptance + evidence layer
- [x] Contracts are semantic; ADR amend required but not decided here beyond REQ-4
- [x] No blocking Gate/PM question remains
- [ ] Developer confirms Draft PR publish via Forge (human authorize if walking manually)

## References

- Pin: `prayog-skills/docs/for-gateflow.md`, `references/forge-side-effects.md`, `delivery-contract.yaml` (submodule tip `355f403` as of draft)
- Predecessor: `docs/specification/product/INIT-GATEFLOW-006-gateflow.md` (REQ-7 supersession)
- ADR: `docs/specification/adr/adr-009-pin-forge-publish-mutate-authority.md` (amend under this INIT)
- Parked: `docs/specification/product/INIT-GATEFLOW-007-gateflow.md`
- Feasibility (stale until re-run on PR head): `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-008.md`

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-draft
  outcome: pass
  artifact:
    path: docs/specification/product/INIT-GATEFLOW-008-gateflow.md
    digest: sha256:209bdadcd07481feffdc1e795caae5fb946b340a2078c3d049346c2b26acfc9c
  blockers: []
  signals:
    pr_ready: true
    gate1_waived: true
    gate1_waived_at: "2026-07-30"
    initiative: INIT-GATEFLOW-008
    brand: 006A
    blocks_init_007_dogfood: true
    d_checks: pass
    nonblocking_questions: "Q-2,Q-3,Q-4,Q-5"
  next_candidates:
    - spec-pr-action
  human_checkpoint: false
  external_action: true
  forge:
    action: open_draft_pr
    draft: true
    apply_labels:
      - spec-pending
    title: "[INIT-GATEFLOW-008] Spec — 006A forge authorization + wave-pr after loop-spec"
    body_path: docs/specification/product/INIT-GATEFLOW-008-gateflow.md
```

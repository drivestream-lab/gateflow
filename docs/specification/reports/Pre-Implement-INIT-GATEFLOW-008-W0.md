## Pre-implement — gateflow / W0 — Authorization parse + Pass-1 unit hygiene

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-008-W0.md` |
| Initiative | INIT-GATEFLOW-008 (brand **006A**) |
| Wave | W0 |
| Date | 2026-07-30 |
| Outcome | `pass` |
| Outcome reason | Spec merged + board seeded + WorkManifest pass + plan PE sign-off; P15 N/A; no prior-wave gate |
| Wave head context | Recommended bind: `feature/INIT-GATEFLOW-008-w0-auth-parse` from `develop` @ `d7d974a` — **not** opened by this skill; current checkout is `develop` |

---

### Gate check (prior wave)

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — on `develop` @ `d7d974a` |
| Spec PR merged | Implementation plan on integration branch | [x] yes — PR [#91](https://github.com/drivestream-lab/gateflow/pull/91) MERGED |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — labels include `spec-lgtm`; merge `d7d974a` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids in body | [x] seeded — EPIC [#92](https://github.com/drivestream-lab/gateflow/issues/92); W0 [#93](https://github.com/drivestream-lab/gateflow/issues/93) parent=92 |
| WorkManifest contract | `prayog/v1` §9 passes validator | [x] pass |
| TASK exit proof | Every W0 `TASK-*` has exit criteria + proof | [x] complete |
| Live-verification contract | When P15 applies | [x] N/A — W0 no new product surface (`verification.live.applicable: false`) |
| Plan source freshness | CURRENT / WAIVED Gate 1 | [x] current (waived digests) |
| Impact-map repo scope | waived Gate 1 | [x] match (waived) |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live when P15 | [x] N/A — P15 N/A (unit + inspect only) |
| `ground_command` | resolved or N/A | [x] N/A — `/ground-spec` Pass-2 pin skill |
| Co-shipped live verify (P15) | FILE under `live_verify_dir` | [x] N/A (no surface) |
| Prior wave as-built row | `human_approved` | [x] N/A — first wave of INIT-008 |
| Prior Ground Report exists | W{N-1} | [x] N/A — W0 |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 complete | [x] complete — 2026-07-30 |

**Gate verdict:** **PASS**

**Forge readiness:** `commit_workspace` **required** — publish this checklist onto bound wave `head_ref` (create/cut `feature/INIT-GATEFLOW-008-w0-auth-parse` outside this skill if unbound). Do **not** open Draft PR here.

---

### Contracts consumed (from prior Ground Report)

> W0 of INIT-008 — no prior Ground Report for this initiative.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Pin workflow load | `WorkflowEngine.load_pin` / `get_node` / `_to_resolved` | pin YAML node map | `ResolvedWorkflowNode` (forge policy today; **no** `authorization` yet) | as-built + `src/` | [x] yes — gap is the work |
| Pin tip with `authorization` | `prayog-skills/workflow.yaml` EA nodes | `authorization: explicit\|automated` | — | submodule `355f403` (= `v0.5.0-rc.2` tip) | [x] yes |
| ADR-009 dual mode | Accepted ADR file | — | dual authorization Option D | `adr-009-…md` | [x] yes — Accepted |

**Unconfirmed contracts:** none blocking W0. W1 will consume authorization on policy/orchestrator (not required for W0 exit).

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered):
  - [x] `fail-fast.mdc` — omit/unknown authorization fail closed
  - [x] `strong-typing.mdc` / `pydantic-schemas.mdc` — enum + ResolvedWorkflowNode
  - [x] `testing-verify-flows.mdc` — unit vs live (W0 unit-only)
  - [x] `spec-driven-development.mdc` — as-built same change
  - [x] `architecture.mdc` — models in `src/models`, business parse in WorkflowEngine
- [x] ADRs:
  - [x] ADR-009 — pin forge + dual `authorization` (Accepted amendment)
  - [x] ADR-003 — ForgeClient remains infra (unchanged this wave)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-008-gateflow.md` (REQ-1…4, REQ-16)
- [x] Plan / §9: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-008.md` W0
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/93 — TASK list (projection):
  - [x] **TASK-W0-01** — REQ-1 — depends_on: [] — inspect `.harness-pin.yaml`; modify as-built — exit: harness ref matches submodule tip — proof: command `git -C prayog-skills describe` / rev-parse
  - [x] **TASK-W0-02** — REQ-2, REQ-3 — depends_on: TASK-W0-01 — modify `forge_types.py`, `handoff_models.py`, `workflow_engine.py` — exit: omit/unknown fail; node carries enum — proof: `make check && make test`
  - [x] **TASK-W0-03** — REQ-2, REQ-11 — depends_on: TASK-W0-02 — modify `test_handoff_workflow.py`, `test_forge_policy.py` — exit: Pass-1 unit edges green (`loop-spec`→`wave-pr-action`; pre-implement commit required) — proof: `make test`
  - [x] **TASK-W0-04** — REQ-4 — depends_on: [] — inspect ADR-009 — exit: Status Accepted + amendment — proof: review
  - [x] **TASK-W0-05** — REQ-16 — depends_on: TASK-W0-02 — modify as-built — exit: W0 rows + INIT-006 REQ-7 supersession note — proof: review

---

### Governance alignment

- [x] Slice does not contradict Accepted ADR-009 (implements dual-mode consume parse)
- [x] Plan TASK MDC/ADR notes reviewed
- [x] ADR-009 is **Accepted** in `docs/specification/adr/`

---

### Must update (same change as code — via `/loop-spec`)

- [ ] Product spec — only if wire contract wording drifts (prefer leave Draft→as-built)
- [ ] `docs/specification/as-built/implementation-status.md` — W0 parse/consume + 006 REQ-7 superseded note (TASK-W0-01/05)
- [ ] `tests/README.md` — **not required for W0** (Pass-1 string update is W1/W2); optional note if unit map changes
- [ ] Unit tests — auth parse + remounted Pass-1 edges (TASK-W0-02/03)
- [ ] Live verification — N/A this wave
- [ ] ADR — no further amend in W0 (already Accepted)

---

### Must not

- [ ] Implement automated apply / PR-at-start retirement (W1)
- [ ] Call pin WorkManifest validator / board changes (W2)
- [ ] Soft-default missing `authorization` on EA nodes
- [ ] Open branch / commit / push / PR / labels / board issues from this skill
- [ ] Treat board issue text as SSOT over plan §9

---

### Implementation sketch (for `/loop-spec` — not executed here)

1. **TASK-W0-01:** Confirm `.harness-pin.yaml` `agent_skills.ref: v0.5.0-rc.2` resolves to submodule HEAD `355f403` (tag tip match). Record CURRENT remount in as-built if missing.
2. **TASK-W0-02:** Add `AuthorizationModeType` (`explicit` \| `automated`) in `src/models/forge_types.py`. Extend `ResolvedWorkflowNode` with optional/required `authorization` when `node_type == "external-action"`. In `WorkflowEngine._to_resolved`, parse and **fail closed** on missing/unknown for EA nodes only.
3. **TASK-W0-03:** Update `tests/unit/test_handoff_workflow.py` (`loop-spec` pass → `wave-pr-action`) and `tests/unit/test_forge_policy.py` (pre-implement `commit_workspace` **required**). Add unit coverage for omit/unknown and day-one matrix (`wave-pr-action`/`spec-pr-action` automated; board/prd explicit).
4. **TASK-W0-04:** Inspect ADR-009 Accepted (no code).
5. **TASK-W0-05:** As-built INIT-008 W0 + supersession note for INIT-006 REQ-7 on automated nodes.

**Current gap evidence:** `ResolvedWorkflowNode` has no `authorization`; `ForgeActionType` / commit modes only in `forge_types.py`; pin already has `authorization` on EA nodes.

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format/lint/types/layers | `make check` |
| Unit | auth parse fail-closed; Pass-1 pin edges; day-one matrix | `make test` |
| Live verify | N/A — P15 N/A | N/A |
| Ground check | `/ground-spec` after Pass-2 (not this wave) | N/A |

### Human live-verify (after loop-spec)

- [ ] N/A for W0 — no co-shipped live script; human checkpoint still follows pin after later waves / wave-pr

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-008
- Issue: [#93](https://github.com/drivestream-lab/gateflow/issues/93)
- EPIC: [#92](https://github.com/drivestream-lab/gateflow/issues/92)
- Spec path: `docs/specification/product/INIT-GATEFLOW-008-gateflow.md`
- Plan: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-008.md`
- Verify command (human): N/A — P15 N/A
- ADRs in scope: ADR-009 (Accepted)
- Wave head: bind `feature/INIT-GATEFLOW-008-w0-auth-parse` (plan §2 Branch column) before `/commit-workspace` / `/loop-spec`

---

### Checklist publish readiness (on `pass`)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — W0 gate satisfied |
| Next | `loop-spec` (`skill`) — `human_checkpoint: false`, `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish this file to bound `head_ref` |
| Later | After `/loop-spec` code publish → `wave-pr-action` (automated open_draft_pr) |

Recommend: bind wave branch → `/commit-workspace` (this checklist) → `/loop-spec`.

---

### Merge order (if cross-module / cross-service)

N/A — gateflow-only; W0 before W1 (authorization field required for policy branch).

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-008-W0.md
    digest: sha256:0f441dcc057297c740626deb339f381d448aa984c3bc5b5bd01f18914ef77990
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-008
    wave: W0
    board_issue: "93"
    epic: "92"
    tasks: "TASK-W0-01,TASK-W0-02,TASK-W0-03,TASK-W0-04,TASK-W0-05"
    check_command: make check
    test_command: make test
    verify_command: "N/A — P15 N/A"
    recommended_head_ref: feature/INIT-GATEFLOW-008-w0-auth-parse
    base_ref: develop
    integration_sha: d7d974aafa674a9c553484728935b63297a3c85f
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    # Pin: pre-implement commit_workspace = required.
    # Publish Pre-Implement artifact onto bound wave head_ref before loop-spec.
```

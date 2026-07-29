# Ground report — INIT-GATEFLOW-005-BOUNDINPUT W2

| Field | Value |
|-------|-------|
| Wave | W2 — Multi-skill packaged dogfood |
| Spec | `docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md` |
| Date | 2026-07-29 |
| Branch | `feature/INIT-GATEFLOW-005-w2-dogfood` — same branch as wave code |
| Status | Draft |
| Review deadline | 2026-07-31 |
| Deciders | Tech lead / reviewer: per CODEOWNERS — explicit LGTM required |
| Board issue | https://github.com/drivestream-lab/gateflow/issues/57 |
| Plan | `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-005-BOUNDINPUT.md` Phase W2 |
| HEAD (at ground) | `bb1fa79` |

## Automated check output

`ground_command`: N/A (no Makefile ground target; manual REQ validation + toolchain).

```text
$ make check
black / ruff / pyright / lint-imports — all pass
Contracts: 1 kept, 0 broken (layered architecture)

$ make test
178 passed in ~2.2s
```

Live prove-it (`verify_implement_lane`): **partial — orchestrated run in progress**.

During active orchestrated run `d781caaa-d023-499f-ade9-0124f282a83c`, standalone
`verify_implement_lane` correctly returns **409 CONFLICT** (concurrent guard). In-run
evidence is the live prove-it for this wave chain.

```text
$ curl -s http://127.0.0.1:8080/health
{"status":"ok"}

$ .venv/bin/python -m tests.verify.verify_implement_lane
[ERROR] wave-start failed 409: Active run already exists … existing_run_id=d781caaa-d023-499f-ade9-0124f282a83c
```

**Expected** during orchestrated run — full standalone script re-runs after run
reaches `stopped` at `wave-human-decision`.

### In-run live evidence (run `d781caaa-…`)

| Check | Result |
|-------|--------|
| API + worker running | **pass** — health 200 |
| Run identity | **pass** — `INIT-GATEFLOW-005` / `W2` / ticket `57` / issue `#57` |
| Baton dual-write (D-W0-B1) | **partial pass** — stored path non-empty (1607 B); latest envelope `stage: verify`, `outcome: pass` |
| RunStore Cursor stages | **pending** — run `active`; stages empty while worker processes chain |
| Multi-skill evidence file | **pending** — agent writes at `features.implement_lane.evidence` on lane completion |
| Full four-hop + `stage_commit` | **pending** — closes when run reaches `wave-human-decision` |

## REQ checklist

W2 plan scope: **REQ-10** multi-skill packaged dogfood (≥2 orchestrated skills with
prompt telemetry; pin SSOT; no Gateflow allowlist). Prior-wave REQs remain in force.

| REQ | Spec claim (W2 slice) | Verified artifact | Status |
|-----|----------------------|-------------------|--------|
| REQ-10 | Prove-it: live Cursor hop(s) with pin packages for `dispatch: orchestrated` skills; substrate for any packaged skill under pin policy; W2 requires ≥2 skill ids with `prompt_id` / `prompt_revision` | `tests/verify/verify_implement_lane.py` — `≥2` orchestrated skill gate + evidence markdown table; `test_require_orchestrated_skill_*`; `test_run_orchestrator` prompt persistence; pin `workflow.yaml` implement-lane nodes; live run `d781caaa-…` | **pass** (unit + harness code); **partial** (live chain in progress — D-W1-V1) |

Inherited W0/W1 REQs (REQ-1…9, REQ-8a/8b):

| REQ | Notes | Status this wave |
|-----|-------|------------------|
| REQ-1…7, REQ-8a | Bound-input substrate from Ground-Report-005-W0 | **pass** (not re-proven beyond toolchain) |
| REQ-8b | Stored-path ingest only | **pass** (W1 human_approved; D-W0-I1 closed) |
| REQ-9 | Fail closed before AgentRunner / ingest | **pass** (unit retained) |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Pin dispatch SSOT — no Gateflow skill allowlist | ADR-006 / plan W2 | **pass** — `WorkflowEngine.require_orchestrated_skill`; `PolicyEngine` docstring; unit rejects manual nodes |
| Message-only Cursor; persist prompt ids | ADR-007 | **pass** — unchanged from W0/W1 |
| Stored-path ingest + baton dual-write | ADR-008 | **pass** — ingest SSOT unchanged; pin templates now instruct baton write (partial live proof) |
| Layered imports | import-linter | **pass** |
| Live verify vs unit separation | testing-verify-flows | **pass** — overlap check: unit covers resolver/policy/ingest; live covers RunStore timeline + evidence block |
| Forge `stage_commit` on required nodes | ADR-009 (as-built authority) | **pending live** — harness asserts `loop-spec` / `ground-spec` when chain completes |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|------------------|--------|--------|
| Stored-path handoff ingest | Ground-Report-005-W1 | **yes** |
| Packaged automate ingest SSOT | Ground-Report-005-W1 | **yes** |
| PromptResolver + thin Cursor | Ground-Report-005-W0 | **yes** |
| Baton define/store | Ground-Report-005-W0 | **yes** |
| Wave-start required `ticket_id` | Ground-Report-005-W0 | **yes** |
| Pin orchestrated implement-lane set | pin `workflow.yaml` | **yes** — `[pre-implement, loop-spec, verify, ground-spec]` |
| Implement-lane verify harness (W1) | Ground-Report-005-W1 | **yes** — extended for multi-skill (TASK-W2-01) |

## Discrepancies (must fix before / during human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| D-W1-V1 | REQ-10 | Full implement-lane live not green yet; run `d781caaa-…` still `active`; RunStore stages pending; standalone verify deferred (409) | **Medium** — accept for W2 unit/harness exit if PE agrees; **blocking for INIT-005 complete** until four-hop chain + evidence file |
| D-W0-V1 | REQ-10 | Alias of D-W1-V1 (carried from W0) | Medium |
| D-W0-B1 | REQ-8b / pin | Baton dual-write **improved** — verify envelope durable at stored path; prior hops (pre-implement) and post-ground-spec baton + full chain still pending | **Medium** — partial closure; full close when all four hops write envelopes |
| D-W0-I1 | REQ-8b | Ambient not automate SSOT | **closed** (W1) |

No additional **gateflow code** blockers for W2 REQ-10 harness/docs exit if PE accepts D-W1-V1 live deferral.

## Contracts produced by this wave

(REQUIRED — final wave of INIT-005; documents substrate for downstream inits / ops.)

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Pin orchestrated dispatch | `WorkflowEngine` | `require_orchestrated_skill` | node id from pin walker | `ResolvedWorkflowNode` or fail closed | No Gateflow skill allowlist; manual nodes rejected | initiative complete |
| Multi-skill prompt telemetry | `RunOrchestrator` → `CursorAgentRunner` | packaged automate hop | skill_id + bind map | stage with `prompt_id` == node id, non-null `prompt_revision` | Pin package SSOT; message == render | initiative complete |
| Multi-skill verify evidence | `tests.verify.verify_implement_lane` | opt-in live | `features.implement_lane` config | ≥2 skill rows + markdown evidence block; terminal `stopped` | Four lane nodes; ADR-009 `stage_commit` when publish applies | initiative complete / ops |
| BOUNDINPUT feature map | `tests/README.md` | inspection | — | documented verify/unit matrix | REQ-10 exit criteria explicit | ops |
| W0/W1 contracts retained | PromptResolver, read_path ingest, baton define/store, ticket bind | (see Ground-Report-005-W0/W1) | — | — | Still valid | initiative complete |
| Implement-lane live prove-it exit | verify harness + as-built W2 matrix | live + unit | wave-start + handoff root + Cursor key | green chain or documented deferral ids | Concurrent 409 guard; baton at `{GATEFLOW_HANDOFF_ROOT}/{run_id}/handoff.md` | ops re-run after merge |

## PR instructions

> Commit this report + updated as-built row to the wave branch (last commit
> before PR is marked ready). Ground report and code are reviewed together
> on the same PR — do not open a separate PR for the ground report.

```
Branch:   feature/INIT-GATEFLOW-005-w2-dogfood
PR title: [INIT-GATEFLOW-005 W2] multi-skill dogfood — implementation + ground report
Issue:    #57
Spec:     docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md
Verify:   make check && make test
          (opt-in live) .venv/bin/python -m tests.verify.verify_implement_lane
```

Required reviewer: per CODEOWNERS in this repo  
Review deadline: 2026-07-31

After reviewer approves:
  Update as-built: INIT-005 W2 → human_approved  
  Merge PR  
  → INIT-005 initiative complete (no W3); re-run standalone live verify post-merge

## Ready for human checkpoint?

**yes** — W2 unit/harness exit satisfied; live implement-lane chain in progress on
orchestrated run `d781caaa-…` (D-W1-V1 / partial D-W0-B1). PE may accept deferral
for W2 signoff (same pattern as W1) or require full green standalone verify before LGTM.

Human must:
- [ ] Review REQ checklist — REQ-10 harness pass; live partial (D-W1-V1)
- [ ] Review §Contracts produced — accurate for INIT-005 closure
- [ ] Accept or reject live deferral (full chain + evidence file)
- [ ] Mark as-built: INIT-GATEFLOW-005-BOUNDINPUT W2 = human_approved

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-005-BOUNDINPUT-W2.md
    digest: sha256:6adb5fb46b0df8c228240ff3307baa06fbcb26c2c0e4307194b72c3c0ff6be06
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-005-BOUNDINPUT
    wave: W2
    ticket_id: "57"
    wave_issue: https://github.com/drivestream-lab/gateflow/issues/57
    board_issue: https://github.com/drivestream-lab/gateflow/issues/57
    epic_issue: https://github.com/drivestream-lab/gateflow/issues/54
    implements_req: [REQ-10]
    branch: feature/INIT-GATEFLOW-005-w2-dogfood
    head_sha: bb1fa79839a28d656d65392fe6af8fe81bc9c840
    contracts_produced: 6
    check_command: make check
    test_command: make test
    verify_command: make check && make test ; .venv/bin/python -m tests.verify.verify_implement_lane
    unit_tests: 178 passed
    live_implement_lane: in_progress
    live_run_id: d781caaa-d023-499f-ade9-0124f282a83c
    verify_implement_lane_standalone: deferred_409_active_run
    baton_dual_write: partial
    implement_lane_evidence: /Users/kumar.deepak1/Workspace/handson/drivestream-lab/run_gateflow/evidence/implement-lane-live.json
    pin_orchestrated_skills: [pre-implement, loop-spec, verify, ground-spec]
    discrepancies_open: [D-W1-V1, D-W0-B1, D-W0-V1]
    discrepancies_closed: [D-W0-I1]
    adr_primary: docs/specification/adr/adr-006-adapter-registry-fail-closed.md
    overlap_check: no_unit_live_duplicate
  next_candidates:
    - wave-human-decision
  human_checkpoint: true
  external_action: false
  forge:
    action: commit_workspace
```

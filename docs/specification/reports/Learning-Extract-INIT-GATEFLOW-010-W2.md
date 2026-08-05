# Learning extract — INIT-GATEFLOW-010 W2

| Field | Value |
|-------|-------|
| Wave | W2 — Ticket gates + create predicates |
| Initiative | INIT-GATEFLOW-010 |
| Branch / head | `feature/INIT-GATEFLOW-010-w2-implement-lane` @ `be637054c78572847166a4ddc3d2df3afff85020` |
| Pass-1 tip (approx) | `3795ab7` — loop-spec workspace publish (REQ-06/07/08 + verify co-ship) |
| PR | [#148](https://github.com/drivestream-lab/gateflow/pull/148) (Draft — open for Pass-2 closeout) |
| Board | [#140](https://github.com/drivestream-lab/gateflow/issues/140) |
| human_fix_detected | **yes** |
| Date | 2026-08-05 |

## Learnings

| ID | Class | Summary | Evidence | Codify hint | Status |
|----|-------|---------|----------|-------------|--------|
| L-01 | SPEC | Board column apply (`update_board_status`, implement-start In Progress) must sync GitHub Projects V2 **Status** single-select, not only `gateflow/column:*` labels — REQ-03/CTR-02 “Board shows In Progress” was met on labels but programme board UI stayed Todo until human GraphQL sync | commit `dd8412f`; `src/infra_services/forge_client.py` (`resolve_issue_project_status_targets`, `set_project_item_status`); Live-Verify W2 note (Status Todo pre-fix) | product spec CTR-02 / REQ-03 — dual-write label + Project Status | open |
| L-02 | HARNESS | `verify_implement_lane` asserts column label only; live verify passed while Project Status field was stale — harness would not catch label-only apply | `tests/verify/verify_implement_lane.py`; Live-Verify-INIT-GATEFLOW-010-W2.md (label OK, Status Todo) | `tests/verify/verify_implement_lane` or board verify helper | open |

**human_fix_detected rationale:** After Pass-1 publish (`3795ab7`), human live-verify run `89b7b7d9-…` passed label assert but exposed Project Status UI drift. Human patch `dd8412f` adds Project V2 Status sync to `ForgeClient.update_issue_status` (+ unit coverage in `test_forge_client_board`). Tip `be63705` is docs-only (`human_approved` backfill).

## Signals

- verify_evidence: `.venv/bin/python -m tests.verify.verify_implement_lane` — exit 0; [`Live-Verify-INIT-GATEFLOW-010-W2.md`](Live-Verify-INIT-GATEFLOW-010-W2.md)
- check/test at Pass-1: `make check` / `make test` (248 passed) per Wave-Execution W2; post-fix unit adds Project Status GraphQL cases
- notes: Keep PR [#148](https://github.com/drivestream-lab/gateflow/pull/148) open through `/ground-spec`; W0 L-01 (closeout-before-merge) applies — do not merge until Pass-2 complete; redeploy tip `dd8412f`+ to align live board Status UI

## Ready for ground-spec?

**yes** — human fix captured (L-01, L-02); Live-Verify + Wave-Execution present; tip stable after Status-sync patch; proceed to Ground Report / §Contracts produced.

```yaml
learning_extract:
  initiative: INIT-GATEFLOW-010
  wave: W2
  human_fix_detected: true
  items:
    - id: L-01
      class: SPEC
      summary: >
        Board column apply must sync GitHub Projects V2 Status single-select,
        not only gateflow/column labels; REQ-03/CTR-02 board-visible In
        Progress requires dual-write.
      evidence:
        - "commit:dd8412f59e40cb71c9cb7244f096dd391ab42b68"
        - "src/infra_services/forge_client.py"
        - "docs/specification/reports/Live-Verify-INIT-GATEFLOW-010-W2.md"
      codify_hint:
        target: spec
        ref: "CTR-02 / REQ-03 board column+Status contract"
      status: open
    - id: L-02
      class: HARNESS
      summary: >
        verify_implement_lane asserts column label only; does not assert Project
        V2 Status field — live verify passed while board UI Status was stale.
      evidence:
        - "tests/verify/verify_implement_lane.py"
        - "docs/specification/reports/Live-Verify-INIT-GATEFLOW-010-W2.md"
      codify_hint:
        target: harness
        ref: "tests/verify/verify_implement_lane"
      status: open
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: learning-extract
  outcome: pass
  artifact:
    path: docs/specification/reports/Learning-Extract-INIT-GATEFLOW-010-W2.md
    digest: sha256:pending
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-010
    wave: W2
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/140"
    ticket_id: "140"
    pr_number: 148
    pr_url: "https://github.com/drivestream-lab/gateflow/pull/148"
    pass1_tip_sha: "3795ab7c20495e2af01f927e5d05c00c31b55e3f"
    human_fix_sha: "dd8412f59e40cb71c9cb7244f096dd391ab42b68"
    tip_sha: "be637054c78572847166a4ddc3d2df3afff85020"
    human_fix_detected: true
    learning_item_count: 2
    live_verify_run_id: "89b7b7d9-5247-429d-95fc-b22fd5c3e844"
    verify_command: ".venv/bin/python -m tests.verify.verify_implement_lane"
  next_candidates:
    - ground-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    commit_workspace: optional
    head_ref: feature/INIT-GATEFLOW-010-w2-implement-lane
    paths:
      - docs/specification/reports/Learning-Extract-INIT-GATEFLOW-010-W2.md
```

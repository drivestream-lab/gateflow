# Learning extract — INIT-GATEFLOW-007 W1

| Field | Value |
|-------|-------|
| Wave | W1 — Learning Postgres ingest |
| Initiative | INIT-GATEFLOW-007 |
| Branch / head | `feature/INIT-GATEFLOW-007-w1-learning-ingest` @ `317f5c586675cafd17ec31da4771b3a39808a7f5` |
| Pass-1 tip (approx) | `2eff882` — Draft PR #102 recorded; before verify RCA fix |
| PR | [#102](https://github.com/drivestream-lab/gateflow/pull/102) (Draft) |
| Board | [#86](https://github.com/drivestream-lab/gateflow/issues/86) |
| human_fix_detected | **yes** |
| Date | 2026-08-01 |

## Learnings

| ID | Class | Summary | Evidence | Codify hint | Status |
|----|-------|---------|----------|-------------|--------|
| L-01 | HARNESS | `verify_pr_thread` still required `pr_number` within 30s of enqueue after INIT-008 moved Draft PR to `wave-pr-action` (ensure_branch-only at start). Misleading failure text blamed worker/forge credentials. | `tests/verify/verify_pr_thread.py` (pre-fix); tip `317f5c5`; as-built INIT-008 W1 row | harness / `verify_pr_thread` + feature map | open |
| L-02 | HARNESS | Board create idempotency false-missed when GitHub Issues `labels=` list returned `[]` ~480ms after successful label PATCH; second POST created duplicate issue. | `logs/gateflow_20260801.log` Content-Length 2; issues #103/#104; `BoardService` post-label wait | harness / `board_service` + `verify_board` Idempotency-Key | open |

## Signals

- verify_evidence: `.venv/bin/python -m tests.verify.verify_all` — human confirmed pass after tip `317f5c5`
- check/test at tip: `make check` / `make test` (**215** passed) including `test_learning_ingest`, `test_board_service`
- notes: W1 product live ingest dogfood remains W2; P15 N/A for learning HTTP surface

## Ready for ground-spec?

**yes** — human_fix_detected with two HARNESS items; tip stable for Ground Report.

```yaml
learning_extract:
  initiative: INIT-GATEFLOW-007
  wave: W1
  human_fix_detected: true
  items:
    - id: L-01
      class: HARNESS
      summary: >
        verify_pr_thread asserted PR-at-start within 30s after INIT-008 moved
        Draft PR to wave-pr-action; failure text blamed forge credentials.
      evidence:
        - "tests/verify/verify_pr_thread.py"
        - "docs/specification/as-built/implementation-status.md"
        - "317f5c586675cafd17ec31da4771b3a39808a7f5"
      codify_hint:
        target: harness
        ref: "verify_pr_thread"
      status: open
    - id: L-02
      class: HARNESS
      summary: >
        GitHub Issues labels= list lag after PATCH caused board idempotent
        replay to create a duplicate ticket; need post-label visibility wait.
      evidence:
        - "logs/gateflow_20260801.log"
        - "src/business_services/board_service.py"
        - "tests/verify/verify_board.py"
      codify_hint:
        target: harness
        ref: "board_service"
      status: open
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: learning-extract
  outcome: pass
  artifact:
    path: docs/specification/reports/Learning-Extract-INIT-GATEFLOW-007-W1.md
  blockers: []
  signals:
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/86"
    pr_number: 102
    pr_url: "https://github.com/drivestream-lab/gateflow/pull/102"
    tip_sha: "317f5c586675cafd17ec31da4771b3a39808a7f5"
    human_fix_detected: true
    learning_item_count: 2
  next_candidates:
    - ground-spec
  human_checkpoint: false
  external_action: false
```

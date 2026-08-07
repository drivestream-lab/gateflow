# Learning extract — INIT-GATEFLOW-011 W0

| Field | Value |
|-------|-------|
| Wave | W0 — Checkpoint status-check foundation (CAP-01) |
| Initiative | INIT-GATEFLOW-011 |
| Branch / head | `feature/INIT-GATEFLOW-011-w0-checkpoint-status` @ `088d125c67d6306c1d1ddba28ee5cb01c1ec9f3d` |
| Pass-1 tip (product) | `ee9f706` — loop-spec CAP-01 content SHA |
| PR | [#171](https://github.com/drivestream-lab/gateflow/pull/171) (open) |
| Board | [#161](https://github.com/drivestream-lab/gateflow/issues/161) |
| human_fix_detected | **no** |
| Date | 2026-08-07 |

## Learnings

| ID | Class | Summary | Evidence | Codify hint | Status |
|----|-------|---------|----------|-------------|--------|
| L-01 | SKILL | Wave tip acceptance was signaled with `spec-lgtm` (Gate 2 / coding-readiness vocabulary) instead of `wave-accepted` (`wave-acceptance` checkpoint). Humans and agents confuse the two labels; CAP-01 Pass-1 must require the pin node label only. | PR [#171](https://github.com/drivestream-lab/gateflow/pull/171) tip `088d125` labels=`[spec-lgtm]`; pin `wave-acceptance` → label `wave-accepted`; chat attested live verify | `wave-acceptance` / AGENTS Pass-1 checklist; CAP-01 verify docs | open |

**human_fix_detected rationale:** After Pass-1 publish (`ee9f706` + forge tip `088d125`), no post-verify product-code tip patches (no `.py` / test delta in the fix window). Tip matches W0 WorkManifest (TASK-W0-01…05). Process miss is acceptance-label vocabulary (L-01), not a product fix window.

## Signals

- verify_evidence: human attested `.venv/bin/python -m tests.verify.verify_checkpoint_status` (chat 2026-08-07); Wave-Execution did **not** claim live smoke as agent success
- check/test at Pass-1: Wave-Execution `make check` / `make test` (**283 passed**); re-proof at extract: **283 passed**
- notes: Tip still lacks `wave-accepted`; Ground Report must fail-closed on G2/G4 accept until that label is on tip

## Ready for ground-spec?

**yes** — learning captured; Wave-Execution + unit green; proceed to Ground Report. Expect Ground **blocked** / Blocking GF until `wave-accepted` is on tip.

```yaml
learning_extract:
  initiative: INIT-GATEFLOW-011
  wave: W0
  human_fix_detected: false
  items:
    - id: L-01
      class: SKILL
      summary: >
        Wave tip acceptance used spec-lgtm instead of wave-accepted;
        enforce pin checkpoint label vocabulary at wave-acceptance.
      evidence:
        - "https://github.com/drivestream-lab/gateflow/pull/171"
        - "tip_sha:088d125c67d6306c1d1ddba28ee5cb01c1ec9f3d"
        - "labels:[spec-lgtm]"
        - "pin:wave-acceptance → wave-accepted"
      codify_hint:
        target: skill
        ref: "wave-acceptance / AGENTS Pass-1 label checklist"
      status: open
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: learning-extract
  outcome: pass
  artifact:
    path: docs/specification/reports/Learning-Extract-INIT-GATEFLOW-011-W0.md
    digest: sha256:8f6f1d33366a0d8376d20d7f95859d2738ba1f9922345e4c819bc6470a9474a2
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    wave: W0
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/161"
    ticket_id: "161"
    epic_ticket_id: "160"
    pr_number: 171
    pr_url: "https://github.com/drivestream-lab/gateflow/pull/171"
    pass1_tip_sha: "ee9f706"
    tip_sha: "088d125c67d6306c1d1ddba28ee5cb01c1ec9f3d"
    human_fix_detected: false
    learning_item_count: 1
    tip_labels: ["spec-lgtm"]
    wave_accepted_present: false
    verify_command: ".venv/bin/python -m tests.verify.verify_checkpoint_status"
  next_candidates:
    - ground-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    commit_workspace: optional
    head_ref: feature/INIT-GATEFLOW-011-w0-checkpoint-status
    paths:
      - docs/specification/reports/Learning-Extract-INIT-GATEFLOW-011-W0.md
```

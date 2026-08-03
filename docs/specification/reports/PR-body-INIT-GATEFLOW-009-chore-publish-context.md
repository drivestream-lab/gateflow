## Summary

- **Fix publish crash on remote-only SHA** — `_git_diff_name_only` in `workspace_commit_paths.py` raised `ValueError` when `base_ref` was a bootstrap commit SHA created on GitHub by `ensure_branch_from_base` but not fetched into the local checkout. Now gracefully degrades to `[]` (safety net skipped); dirty/untracked files (the agent's actual output) still publish.
- **Enrich `run_stopped` event with handoff context** — `_finalize_run` now accepts an optional `handoff` and persists `stage`, `outcome`, `blockers`, `signals`, `next_candidates`, `human_checkpoint` into the `run_stopped` event payload. The ops portal can render "why this stopped" without parsing the baton file.

## Why

Spec-lane dogfood (INIT-GATEFLOW-009) crashed at the publish step after a successful `spec-draft` Cursor hop. The run was finalized as `FAILED` with `stop_reason: "git diff c93fb53... failed: fatal: Invalid revision range"`, masking the real handoff (`outcome: blocked`, `blockers: [Q-1]`). Even without the crash, the `stop_reason` alone ("Unresolved handoff blockers: Q-1") was too thin for the ops portal to show what a developer sees in the skill chat.

## Test plan

- [x] `make check && make test` → 217 passed (new: `test_collect_with_unknown_remote_sha_degrades_gracefully`)
- [ ] Human: re-run `.venv/bin/python -m tests.verify.verify_spec_lane` after merge — run should reach `spec-implementation-plan` STOP (not crash at publish)

## Initiative

- Initiative: INIT-GATEFLOW-009 (H1.5 closeout)
- Verify: `.venv/bin/python -m tests.verify.verify_spec_lane`

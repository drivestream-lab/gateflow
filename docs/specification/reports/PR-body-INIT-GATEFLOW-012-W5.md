## Summary

- Implement INIT-GATEFLOW-012 **W5** dormant `ForgeClient.delete_branch` (REQ-26–27): DELETE on existing `_git_ref_update_path` (same family as tip PATCH); fail closed on missing/protected; **zero production callers** this INIT (G5 / Q-6 code-guard).
- Unit + dormancy only — **P15 N/A** (no live verify script; no walker/route wiring).
- As-built W5 matrix + `tests/README.md` feature map document unit-only / dormant.

## Spec path

- `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` (REQ-26, REQ-27)
- Plan §9 / Pre-Implement / Wave-Execution W5 under `docs/specification/reports/`
- Board: [#190](https://github.com/drivestream-lab/gateflow/issues/190)

## Smoke command (human at wave-acceptance)

```text
N/A — P15 N/A; dormant zero live callers
```

Accept with: `make check` / `make test` green (includes `test_delete_branch_dormant`) + tip label `wave-accepted`. Then Pass-2 (`/learning-extract` → `/ground-spec`) **before** merge (do not skip — W4 L-01).

## Test plan

- [x] `make check`
- [x] `make test` (461 passed at loop-spec)
- [ ] Human: confirm dormancy (no production caller) + tip `wave-accepted`
- [ ] Pass-2 closeout before wave-signoff merge

## Summary

- Implement INIT-GATEFLOW-012 **W3** harness-readiness (REQ-20–22): `LaunchpadClient.sync_harness` requires `.harness-pin.yaml` + `.harness/`; named `harness_artifacts_missing` on miss; `tenant_repos.harness_verified` cache skip + `force_harness_recheck` re-probe.
- Wire after workspace resolve (+ checkout) and before Enter-at; implement wave-start companion returns 422 with 0 enqueue when harness fails.
- Co-ship `tests/verify/verify_harness_readiness.py` (P15) + README feature map + as-built W3 matrix.
- First-ever `tests/unit/test_launchpad_client.py` (FF-05).

## Spec path

- `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` (REQ-20–22)
- Plan §9 / Pre-Implement / Wave-Execution W3 under `docs/specification/reports/`

## Smoke command (human at wave-acceptance)

```bash
.venv/bin/python -m tests.verify.verify_harness_readiness
```

## Test plan

- [x] `make check`
- [x] `make test` (451 passed at loop-spec)
- [ ] Human: live verify above (API + programme token + board fields)
- [ ] Label tip `wave-accepted` when smoke passes

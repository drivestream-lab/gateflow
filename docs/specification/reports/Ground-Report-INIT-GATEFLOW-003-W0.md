# Ground report — INIT-GATEFLOW-003 W0

| Field | Value |
|-------|-------|
| Wave | W0 — Cursor SDK skeleton + start-gate honesty |
| Spec | `docs/specification/product/INIT-GATEFLOW-003-gateflow.md` |
| Date | 2026-07-24 |
| Branch | `feature/INIT-GATEFLOW-003-w0-cursor-skeleton` — same branch as wave code |
| Status | Draft |
| Review deadline | 2026-07-28 |
| Deciders | Tech lead / reviewer: prayog-pe-team — explicit LGTM required |
| Board issue | https://github.com/drivestream-lab/gateflow/issues/20 |
| Plan | `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-003.md` Phase W0 |

## Automated check output

`ground_command`: N/A (no Makefile ground target; manual FR validation + toolchain).

```text
$ make check
black / ruff / pyright / lint-imports — all pass
Contracts: 1 kept, 0 broken (layered architecture)

$ make test
83 passed in ~0.5s
```

Live Scenario B verify: **N/A for W0** (plan: W1). Laptop spike:
`docs/specification/reports/Spike-Cursor-Local-SDK-INIT-GATEFLOW-003-W0.md`
— bridge + auth **pass**; end-to-end `finished` **not proven** (`wait()` → `status=error`).

## FR checklist

| FR / REQ | Spec claim (W0 slice) | Verified artifact | Status |
|----------|----------------------|-------------------|--------|
| REQ-27 (partial) | Live local Cursor path exists; no cloud; stub not production evidence | `CursorAgentRunner._run_local_sdk` (`launch_bridge` + `LocalAgentOptions(cwd)`); unit mocked SUCCESS/FAILED; spike note; no `cloud=` | **partial** — skeleton + unit OK; live coding prove-it / Scenario B = **W1** |
| REQ-28 (W0) | Not-live / stub runners still fail closed at start; config-driven | `AdapterRegistry` + `SlotValidator` + `test_slot_validator` (opencode/unknown) | **pass** (inherit + retained) |
| REQ-29 (W0) | Missing Cursor credentials fail fast (precondition #12) | `SlotValidator` `CURSOR_API_KEY` check → `WaveStartService` 422; runner rejects without key; `test_wave_start_missing_cursor_api_key_422`, `test_cursor_agent_settings` | **pass** (unit); live invalid-auth / crash paths deepen in W1 |
| REQ-30 | Stage + wave cycle-time | — | **deferred** — W1/W2 |
| REQ-31 | Reuse 001/002 control plane; no rebuild | Wave-start / orchestrator / registry unchanged in role; only Cursor infra + start-gate credential check added | **pass** |
| inherit FR-6 | AgentRunner I/O `run_skill` → `AgentRunResult` | Same entry point; live path added behind it | **pass** |
| inherit FR-17 meaning | “Cursor implemented” for live exit | Registry still `implemented=True` with callable SDK path + credential gate (TDD §3.2); live coding work exit = W1 | **partial** — honesty fixed for W0; full product meaning = W1 prove-it |
| Q-3 quarantine | `mock-*` / `GATEFLOW_AGENT_STUB` not live exit evidence | README + runner docstring; unit doubles retained | **pass** |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| AgentRunner in infra; business does not import `cursor_sdk` | ADR-003 + MDC infra-services | **pass** |
| Secrets via settings env (`CURSOR_API_KEY`), never programme.yaml | ADR-004 + `CursorAgentSettings` | **pass** |
| Fail-closed at accept for missing credentials when runner=`cursor` | ADR-006 + REQ-29 #12 | **pass** |
| Settings via `get_instance()`, not DI | MDC dependency-injection | **pass** |
| No Alembic / schema edits in W0 | MDC database-migrations | **pass** |
| Layered imports (`import-linter`) | MDC python-tooling | **pass** |
| Never pass cloud agent options | Spec out-of-scope + TDD §3.3 | **pass** |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|------------------|--------|--------|
| `run_skill` → `AgentRunResult` | Ground-Report-002-W1 Cursor stub path / FR-6 | **yes** — same I/O; live path added |
| SlotValidator + WaveStartService 422 before enqueue | Ground-Report-002-W0 | **yes** — extended with `CURSOR_API_KEY` failure |
| AdapterRegistry `implemented` catalogue | ADR-006 / 002 W0 | **yes** — `cursor` remains implemented with live backend + credential gate |
| Programme config runner/model resolve | Ground-Report-002-W1 | **yes** — consumed; SDK model id mapped (`cursor/auto` → `composer-2`) |

## Discrepancies (must fix before human checkpoint)

| ID | FR | Finding | Severity |
|----|----|---------|----------|
| D-W0-L1 | REQ-27 | Laptop live `send`/`wait` returned `status=error` (~97 min); bridge+auth OK but `finished` not proven | **Medium** — accept for W0 skeleton exit; **blocking for W1 Scenario B prove-it** until resolved (spike note) |
| D-W0-M1 | REQ-27/29 | Programme profiles `cursor/auto` / `cursor/fast` are not SDK model ids; mapped via `_sdk_model_id` to `composer-2` / settings default | Low — document; consider programme.yaml alignment later |
| D-W0-V1 | REQ-27 | No W0 live Scenario B verify script (by plan) | Low — intentional defer to W1 |

No **blocking** discrepancies for **W0 skeleton exit** if PE accepts D-W0-L1 / D-W0-M1 / D-W0-V1 as in-scope for W0.

## Contracts produced by this wave

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Cursor credentials settings | `CursorAgentSettings` | `get_instance` / `has_api_key` / `require_api_key` | env `CURSOR_API_KEY`, optional `CURSOR_DEFAULT_MODEL` | typed settings; blank key = missing | Secret never in programme.yaml; never log full key | W1 |
| Local Cursor AgentRunner | `CursorAgentRunner` | `run_skill` | workspace path, skill id, prompt context, model profile (+ optional runner/model) | `AgentRunResult` (SUCCESS/FAILED) | Local `launch_bridge` + `LocalAgentOptions(cwd)` only; never `cloud=`; missing key → FAILED; SDK errors → FAILED | W1 Scenario B |
| SDK model id map | `CursorAgentRunner` | `_sdk_model_id` | programme model id (e.g. `cursor/auto`) | SDK model id (e.g. `composer-2`) | `auto`/`fast`/empty → settings default | W1 |
| Unit test doubles | `CursorAgentRunner` | `run_skill` | `mock-*` skill or `GATEFLOW_AGENT_STUB=1` | synthetic SUCCESS | Not live prove-it evidence (Q-3) | W1 verify must unset stub |
| Start-gate Cursor key | `SlotValidator` + `WaveStartService` | `validate_for_run` / `start_wave` | required runner ids include `cursor` | ok or 422 with `config_key=CURSOR_API_KEY` | No enqueue when key missing | W1 |
| Laptop SDK spike | spike report | inspection | local key + cwd | pass/fail note | Bridge required; live `finished` deferred | W1 Docker spike |

## PR instructions

> Commit this report + updated as-built row to the wave branch (last commit before PR is marked ready). Ground report and code are reviewed together on the same PR — do not open a separate PR for the ground report.

```
Branch:   feature/INIT-GATEFLOW-003-w0-cursor-skeleton
PR title: [INIT-GATEFLOW-003 W0] cursor-skeleton — implementation + ground report
Issue:    #20
Spec:     docs/specification/product/INIT-GATEFLOW-003-gateflow.md
Verify:   make check && make test
```

Required reviewer: per CODEOWNERS / prayog-pe-team  
Review deadline: 2026-07-28

After reviewer approves:
  Update as-built: INIT-GATEFLOW-003 W0 → **human_approved**
  Merge PR
  → `/pre-implement` for W1 (reads §Contracts produced above)

## Ready for human checkpoint?

**yes** — W0 skeleton + start-gate + unit + spike note are complete; D-W0-L1 accepted as W1 blocker for live `finished` prove-it, not as W0 skeleton blocker.

Human must:
- [ ] Review FR checklist — all pass or explicitly deferred
- [ ] Review §Contracts produced — accurate and complete for W1
- [ ] Accept or reject D-W0-L1 / D-W0-M1 / D-W0-V1
- [ ] Mark as-built: INIT-GATEFLOW-003 W0 = human_approved (human only — do not self-approve)

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-003-W0.md
    digest: sha256:5a94d4297dd0ae114f344def0f5e6c1253181f69e5c7caa980a41026c339bd7d
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-003
    wave: W0
    board_issue: https://github.com/drivestream-lab/gateflow/issues/20
    branch: feature/INIT-GATEFLOW-003-w0-cursor-skeleton
    contracts_produced: 6
    check_command: make check
    test_command: make test
    verify_command: N/A — W0 unit+spike; Scenario B in W1
    unit_tests: 83 passed
    discrepancies: [D-W0-L1, D-W0-M1, D-W0-V1]
    human_approved: false
  next_candidates:
    - wave-human-decision
  human_checkpoint: true
  external_action: false
```

# Ground report — INIT-GATEFLOW-005-BOUNDINPUT W0

| Field | Value |
|-------|-------|
| Wave | W0 — Resolve + bind + thin Cursor + handoff_path define/store |
| Spec | `docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md` |
| Date | 2026-07-28 |
| Branch | `feature/INIT-GATEFLOW-005-w0-bound-input` — same branch as wave code |
| Status | **human_approved** |
| Review deadline | 2026-07-30 |
| Deciders | Tech lead / reviewer: per CODEOWNERS — explicit LGTM required |
| Board issue | https://github.com/drivestream-lab/gateflow/issues/55 |
| Plan | `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-005-BOUNDINPUT.md` Phase W0 |
| HEAD (at ground) | `0287caa` (Alembic baseline `69de74666068`) |

## Automated check output

`ground_command`: N/A (no Makefile ground target; manual REQ validation + toolchain).

```text
$ make check
black / ruff / pyright / lint-imports — all pass
Contracts: 1 kept, 0 broken (layered architecture)

$ make test
119 passed in ~1.5s
```

Live prove-it (`verify_implement_lane`): **not green on this wave**.
Harness asserts `prompt_id` / `prompt_revision` and uses nested
`features.implement_lane` config. A live hop (`run_id=58d3e619-…`) completed
Cursor `pre-implement` success then **failed** post-stage because ingest still
uses ambient `find_latest_handoff` (picked Implementation-Plan handoff
`stage: spec-implementation-plan`). Owned baton under `GATEFLOW_HANDOFF_ROOT`
was created empty. Full implement-lane live exit is deferred to **W1** with
REQ-8b ingest-from-stored-path (product owner intent for this ground).

## REQ checklist

| REQ | Spec claim (W0 slice) | Verified artifact | Status |
|-----|----------------------|-------------------|--------|
| REQ-1 | Resolve pin `prompts/template.md` + `schema.yaml`; fail closed if missing | `PromptResolver.resolve` / `bind_and_render`; pin roots under `prayog-skills/skills/{development,requirements}/…/prompts/`; `test_prompt_resolver` missing package | **pass** (unit) |
| REQ-2 | Bind `ticket`, `initiative`, `skill_id`, `workspace`, `handoff_path` | `PromptBindInputs` + orchestrator bind; wave-start `ticket_id` required; `test_wave_start_missing_ticket_id`, `test_prompt_resolver` | **pass** (unit) |
| REQ-3 | Validate bound map against pin `schema.yaml` | `PromptResolver` required-miss path; `test_required_bind_miss_fails` | **pass** (unit) |
| REQ-4 | Simple `{{var}}` only; undeclared fails closed | `PromptResolver` undeclared-var path; `test_undeclared_template_var_fails` | **pass** (unit) |
| REQ-5 | Message == render; remove invent-prose; anti-hardcode | `CursorAgentRunner.run_skill(message=…)`; `assert not hasattr(…, "_build_prompt")`; orchestrator passes rendered message | **pass** (unit + inspection) |
| REQ-6 | Persist `prompt_id` + `prompt_revision` on packaged stages | ORM/DTO `stages.prompt_*`; orchestrator `StageCreate`; Alembic `69de74666068`; unit `test_dispatch_persists…` / walker asserts `prompt_id` | **pass** (unit + schema); live assert **deferred** (D-W0-V1) |
| REQ-7 | Persist `runner` + `model_id` on packaged stages | Existing stage persistence + W0 path retains fields; unit orchestrator | **pass** (unit) |
| REQ-8a | Define + persist `runs.handoff_path`; inject into bind | `WaveStartService` / `_ensure_run_handoff_path`; `GATEFLOW_HANDOFF_ROOT`; Alembic column; `test_orchestration_settings` | **pass** (unit + schema) |
| REQ-8b | Ingest only from stored path; no ambient SSOT | — | **deferred — W1** (as-built still calls `find_latest_handoff`) |
| REQ-9 | Fail closed before AgentRunner on package/schema/bind/`handoff_path` | PromptResolver + wave-start ticket + settings absolute root; unit coverage | **pass** (unit); live packaged fail paths deepen with W1 ingest |
| REQ-10 | ≥1 live Cursor hop with pin package (`pre-implement` default) | Harness `verify_implement_lane` (prompt field asserts); live hop **failed** after ambient mismatch | **partial** — harness ready; live green **W1** (D-W0-V1) |

Inherited control-plane REQs (001–003) remain in force; not re-proven here beyond toolchain green.

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Brief resolve/render in business; AgentRunner message-only | ADR-007 | **pass** |
| Automate handoff locator Gateflow-owned on run (define/store W0) | ADR-008 | **pass** for define/store; ingest SSOT switch = W1 |
| AgentRunner in infra; no `cursor_sdk` in business | ADR-003 | **pass** |
| RunStore via repository; no ORM in business | ADR-001 / MDC repository-pattern | **pass** |
| Settings `get_instance()` not DI (`GATEFLOW_HANDOFF_ROOT`) | MDC dependency-injection | **pass** |
| Human-owned Alembic revision for new columns | MDC database-migrations | **pass** — `69de74666068_first_version.py` |
| Layered imports | import-linter | **pass** |
| Verify client does not own `CURSOR_API_KEY` | testing-verify-flows / W0 verify config | **pass** — runtime `.env` only |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|------------------|--------|--------|
| `run_skill` → `AgentRunResult`; local Cursor path | Ground-Report-003-W0 / W1 | **yes** — message kwarg added; invent-prose removed |
| Wave-start + programme token + pin walker until gate | Ground-Report-002-W0/W1 | **yes** — extended with required `ticket_id` + handoff baton |
| Pin `dispatch: orchestrated` SSOT (no Gateflow skill allowlist) | ADR-006 / pin `workflow.yaml` | **yes** |
| Ambient `HandoffReader.find_latest_handoff` as pre-W1 ingest | Ground-Report-001 / as-built | **yes** — still used post-stage (W1 removes as automate SSOT) |

## Discrepancies (must fix before / during human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| D-W0-V1 | REQ-10 / REQ-6 live | Live implement-lane prove-it not green; first hop failed after ambient handoff stage mismatch; owner defers full lane live exit to W1 with REQ-8b | **Medium** — accept for W0 unit/schema exit only if PE agrees; **blocking for INIT-005 complete** until W1 live |
| D-W0-I1 | REQ-8b | Post-agent ingest still ambient (`find_latest_handoff`) — intentional W1 scope | Low for W0 exit; required for W1 |
| D-W0-B1 | REQ-8a / REQ-10 | Owned `handoff.md` created empty; agent did not write envelope to stored path on failed live hop | Medium — couples to prompt packages + W1 ingest; track in W1 |

No additional **code** blockers for W0 substrate if PE accepts D-W0-V1.

## Contracts produced by this wave

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Handoff root settings | `OrchestrationSettings` (or equivalent settings module) | `get_instance` / absolute `GATEFLOW_HANDOFF_ROOT` | env absolute path | typed settings; relative/blank rejected | Required for packaged automate; not under workspace by default | W1 |
| Prompt package models | `src.models.prompt_package_models` | Pydantic validate | schema.yaml + bind fields | typed package / bind / render result | Internal `extra=forbid` where applicable | W1–W2 |
| PromptResolver | `PromptResolver` | `resolve` / `bind_and_render` | skill_id + bind map + pin tree | `prompt_id`, `revision`, rendered message | Fail closed before AgentRunner; pin SSOT | W1–W2 |
| Run baton define/store | `WaveStartService` / `RunOrchestrator._ensure_run_handoff_path` | run create / before dispatch | run id + handoff root | non-empty `runs.handoff_path`; empty baton file ensured | Path Gateflow-owned; injected as bind `handoff_path` | W1 ingest |
| Thin Cursor dispatch | `RunOrchestrator` → `CursorAgentRunner.run_skill` | packaged automate hop | rendered `message` + runner/model | stage with `prompt_id` / `prompt_revision` / runner / model | No invent-prose; message == render | W1 |
| RunStore columns | ORM + DTO + Alembic `69de74666068` | repository map | nullable text/varchar | `runs.handoff_path`; `stages.prompt_id` / `prompt_revision` | Human-owned migration applied for live | W1 |
| Wave-start ticket | wave-start body model + `WaveStartService` | `POST /api/v1/waves/start` | non-empty `ticket_id` | bind `ticket` | Blank rejected before enqueue | W1 |
| Implement-lane verify harness | `tests.verify.verify_implement_lane` | opt-in live | `gateflow:` + `features.implement_lane` | asserts prompt fields + chain | Not in `verify_all`; Cursor key on Gateflow runtime | W1 live green |
| Spec-lane verify scaffold | `tests.verify.verify_spec_lane` | opt-in (disabled) | `features.spec_lane` | skip until W2 harness | Empty when disabled | W2 |

## PR instructions

> Commit this report + updated as-built row to the wave branch (last commits
> before PR is marked ready). Ground report and code are reviewed together
> on the same PR — do not open a separate PR for the ground report.

```
Branch:   feature/INIT-GATEFLOW-005-w0-bound-input
PR title: [INIT-GATEFLOW-005 W0] bound-input + thin Cursor — implementation + ground report
Issue:    #55
Spec:     docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md
Verify:   make check && make test
          (opt-in live deferred) .venv/bin/python -m tests.verify.verify_implement_lane
```

Required reviewer: per CODEOWNERS in this repo  
Review deadline: 2026-07-30

After reviewer approves:
  Update as-built: INIT-005 W0 → human_approved  
  Merge PR  
  → `/pre-implement` for W1 (ingest-only + dual-run + live implement-lane)

## Ready for human checkpoint?

**yes — human_approved** (2026-07-28). Verifier accepted W0 ground report with
D-W0-V1 (live implement-lane prove-it deferred to W1); as-built updated on this branch.

Human must:
- [x] Review REQ checklist — all W0 REQs pass or explicitly deferred (D-W0-V1)
- [x] Review §Contracts produced — accurate for W1 `/pre-implement`
- [x] Confirm Alembic `69de74666068` applied on dogfood DB
- [x] Mark as-built: INIT-GATEFLOW-005-BOUNDINPUT W0 = human_approved (after LGTM)

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-005-BOUNDINPUT-W0.md
    digest: sha256:dbafafb3de57130cf7a274e4c1395d28b7857709063c9abc5def507e4570120d
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-005-BOUNDINPUT
    wave: W0
    board_issue: https://github.com/drivestream-lab/gateflow/issues/55
    branch: feature/INIT-GATEFLOW-005-w0-bound-input
    contracts_produced: 9
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_implement_lane
    unit_tests: 119 passed
    human_alembic_revision: 69de74666068
    live_implement_lane: deferred_to_w1
    discrepancies_open: [D-W0-V1, D-W0-I1, D-W0-B1]
    as_built_status: human_approved
  next_candidates:
    - wave-human-decision
  human_checkpoint: true
  external_action: false
```

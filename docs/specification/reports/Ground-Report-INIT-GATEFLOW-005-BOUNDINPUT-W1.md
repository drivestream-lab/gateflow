# Ground report — INIT-GATEFLOW-005-BOUNDINPUT W1

| Field | Value |
|-------|-------|
| Wave | W1 — Ingest-only from stored handoff_path + dual-run isolation |
| Spec | `docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md` |
| Date | 2026-07-28 |
| Branch | `feature/INIT-GATEFLOW-005-w1-ingest` — same branch as wave code |
| Status | **human_approved** |
| Review deadline | 2026-07-30 |
| Deciders | Tech lead / reviewer: per CODEOWNERS — explicit LGTM required |
| Board issue | https://github.com/drivestream-lab/gateflow/issues/56 |
| Plan | `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-005-BOUNDINPUT.md` Phase W1 |
| HEAD (at ground) | `96e1d76` |

## Automated check output

`ground_command`: N/A (no Makefile ground target; manual REQ validation + toolchain).

```text
$ make check
black / ruff / pyright / lint-imports — all pass
Contracts: 1 kept, 0 broken (layered architecture)

$ make test
127 passed in ~1.75s
```

Live prove-it (`verify_implement_lane`): **not green**.

```text
$ .venv/bin/python -m tests.verify.verify_implement_lane
[OK] wave-start → run_id=9a6e6e34-f4ef-4d85-a6e0-8d48d8aa70b0 start_node=pre-implement
[ERROR] missing implement-lane stages ['loop-spec', 'verify', 'ground-spec'];
        got=['pre-implement'] status=failed

stop_reason (run detail):
  No handoff YAML block in stored path:
  …/run_gateflow/9a6e6e34-…/handoff.md
```

Stage `pre-implement` outcome **success** with non-null `prompt_id` / `prompt_revision`.
Stored baton file existed but was **0 bytes** — ingest correctly fail-closed (no ambient
fallback). Matches carry-forward **D-W0-B1** (agent did not write envelope to
`{{handoff_path}}`). Pin `pre-implement` template binds `handoff_path` for read
preference but does not instruct writing the durable envelope to that path;
prayog-skills package authoring is **out of scope** for this gateflow wave.

## REQ checklist

| REQ | Spec claim (W1 slice) | Verified artifact | Status |
|-----|----------------------|-------------------|--------|
| REQ-8b | Ingest only from stored `run.handoff_path`; ambient not automate SSOT; dual-run isolation | `HandoffReader.read_path`; `RunOrchestrator._ingest_handoff_after_stage`; `test_packaged_ingest_uses_read_path_not_ambient`; `test_dual_run_isolation_distinct_handoff_paths`; live fail-closed on empty baton | **pass** (unit + live fail-closed evidence); full lane green **deferred** (D-W1-V1 / D-W0-B1) |
| REQ-9 | Fail closed on missing/unreadable `handoff_path` at ingest; reason on run | `test_read_path_*`; `test_packaged_ingest_missing_path_fails_closed`; live stop_reason on empty baton | **pass** (ingest harden); pre-AgentRunner package/bind paths remain W0 |

Inherited W0 REQs (REQ-1…7, REQ-8a, REQ-9 package/bind, REQ-10 live) remain in force:

| REQ | Notes | Status this wave |
|-----|-------|------------------|
| REQ-1…7, REQ-8a | Unchanged substrate from Ground-Report-005-W0 | **pass** (not re-proven beyond toolchain) |
| REQ-10 | Live implement-lane chain | **partial** — first hop success + prompt fields; chain stopped on empty baton (D-W1-V1) |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Automate handoff ingest SSOT = Gateflow-owned stored locator | ADR-008 | **pass** — `read_path(run.handoff_path)` only on packaged path |
| Ambient glob/mtime not automate SSOT | ADR-008 / REQ-8b | **pass** — unit asserts `find_latest_handoff` not called; legacy method retained for debug |
| Handoff parse in business; no ORM in business | ADR-001 / ADR-003 / MDC repository-pattern | **pass** |
| Fail closed — no ambient fallback on empty/missing baton | MDC fail-fast | **pass** |
| Brief / message-only Cursor unchanged | ADR-007 | **pass** — W1 did not touch invent-prose |
| Layered imports | import-linter | **pass** |
| Pin package authoring out of scope | product Out of scope | **noted** — empty-baton write instruction is pin-side |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|------------------|--------|--------|
| `GATEFLOW_HANDOFF_ROOT` + define/store baton before dispatch | Ground-Report-005-W0 | **yes** |
| PromptResolver + thin Cursor message-only | Ground-Report-005-W0 | **yes** — live hop persisted prompt ids |
| Wave-start required `ticket_id` | Ground-Report-005-W0 | **yes** |
| Implement-lane verify harness | Ground-Report-005-W0 | **yes** — harness ran; chain incomplete |
| Ambient ingest as pre-W1 SSOT | Ground-Report-005-W0 D-W0-I1 | **superseded** — packaged path no longer calls ambient |

## Discrepancies (must fix before / during human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| D-W1-V1 | REQ-10 / REQ-8b live | Live implement-lane not green; hop-1 success then ingest fail on empty baton; same root cause as D-W0-B1 | **Medium** — accept for W1 unit exit if PE agrees; **blocking for INIT-005 complete** until pin writes baton or W2 dogfood proves green lane |
| D-W0-B1 | REQ-8b / pin | Owned `handoff.md` remains empty after Cursor success; pin template does not instruct write-to-`handoff_path` | **Medium** — out of gateflow W1 scope; track pin package follow-up |
| D-W0-V1 | REQ-10 | Carry-forward from W0; not closed this wave | Medium — alias of D-W1-V1 for live lane |
| D-W0-I1 | REQ-8b | Ambient still used as automate SSOT | **closed** — W1 packaged path uses `read_path` only |

No additional **gateflow code** blockers for W1 REQ-8b unit/schema exit if PE accepts D-W1-V1 / D-W0-B1 deferral.

## Contracts produced by this wave

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Stored-path handoff ingest | `HandoffReader` | `read_path` | filesystem path string/Path | `HandoffEnvelope` or fail closed | Blank/missing/empty/unreadable/no YAML block → error; no glob scan | W2 |
| Packaged automate ingest SSOT | `RunOrchestrator` | `_ingest_handoff_after_stage` | stored `handoff_path` + expected stage id | envelope; stage must match node | Never calls ambient `find_latest_handoff` on this path; empty path rejected | W2 |
| Legacy ambient scan | `HandoffReader` | `find_latest_handoff` | workspace root + optional globs | envelope from newest match | Debug/legacy only — not packaged automate SSOT | W2 (unchanged) |
| Dual-run baton isolation | unit fixture + path formula | `{GATEFLOW_HANDOFF_ROOT}/{run_id}/handoff.md` | two run ids, shared coding workspace | each `read_path` returns own envelope | Ambient decoys under workspace ignored by stored-path ingest | W2 |
| W0 contracts retained | PromptResolver, thin Cursor, define/store, ticket, RunStore columns | (see Ground-Report-005-W0) | — | — | Still valid for W2 dogfood | W2 |
| Implement-lane verify harness | `tests.verify.verify_implement_lane` | opt-in live | nested `features.implement_lane` | prompt-field asserts + chain | Live full chain still blocked on baton write (D-W1-V1) | W2 |

## PR instructions

> Commit this report + updated as-built row to the wave branch (last commits
> before PR is marked ready). Ground report and code are reviewed together
> on the same PR — do not open a separate PR for the ground report.

```
Branch:   feature/INIT-GATEFLOW-005-w1-ingest
PR title: [INIT-GATEFLOW-005 W1] ingest-only handoff_path + dual-run — implementation + ground report
Issue:    #56
Spec:     docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md
Verify:   make check && make test
          (opt-in live deferred) .venv/bin/python -m tests.verify.verify_implement_lane
```

Required reviewer: per CODEOWNERS in this repo  
Review deadline: 2026-07-30

After reviewer approves:
  Update as-built: INIT-005 W1 → human_approved  
  Merge PR  
  → `/pre-implement` for W2 (multi-skill dogfood; may also close D-W1-V1 if pin writes baton)

## Ready for human checkpoint?

**yes — human_approved** (2026-07-28). Verifier accepted W1 ground report with
D-W1-V1 / D-W0-B1 (live implement-lane deferred to pin baton write / W2); as-built
updated on this branch.

Human must:
- [x] Review REQ checklist — REQ-8b unit pass; live deferred (D-W1-V1)
- [x] Review §Contracts produced — accurate for W2 `/pre-implement`
- [x] Accept or reject live deferral (pin write-to-`handoff_path` follow-up)
- [x] Mark as-built: INIT-GATEFLOW-005-BOUNDINPUT W1 = human_approved (after LGTM)

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-005-BOUNDINPUT-W1.md
    digest: sha256:c59d49e43389b1e0f65793f52a84461065ab3345abe892aa17b487c171ee3406
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-005-BOUNDINPUT
    wave: W1
    board_issue: https://github.com/drivestream-lab/gateflow/issues/56
    branch: feature/INIT-GATEFLOW-005-w1-ingest
    contracts_produced: 6
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_implement_lane
    unit_tests: 127 passed
    live_implement_lane: deferred_pin_baton_write
    live_run_id: 9a6e6e34-f4ef-4d85-a6e0-8d48d8aa70b0
    discrepancies_open: [D-W1-V1, D-W0-B1, D-W0-V1]
    discrepancies_closed: [D-W0-I1]
    as_built_status: human_approved
  next_candidates:
    - wave-human-decision
  human_checkpoint: true
  external_action: false
```

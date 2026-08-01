## Pre-implement — gateflow / W2 — Full Pass-2 dogfood + docs

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-007-W2.md` |
| Initiative | INIT-GATEFLOW-007 |
| Wave | W2 |
| Date | 2026-08-01 |
| Outcome | `pass` |
| Outcome reason | W1 human_approved; §9 `prayog/v1` on develop via [#106](https://github.com/drivestream-lab/gateflow/pull/106); WorkManifest contract pass; board seeded; P15 live verify contract present; W1 contracts confirmed in source |
| Wave head context | Planned `feature/INIT-GATEFLOW-007-w2-closeout-prove` — **not** opened by this skill; cut from `develop` @ `99a82b1` before `/commit-workspace` |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — `develop` @ `99a82b1` (integration after chore #106); wave feature branch unbound until human/Forge cut |
| Spec PR merged | Implementation plan on integration branch | [x] yes — PR [#83](https://github.com/drivestream-lab/gateflow/pull/83) MERGED @ `560f11f` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — label `spec-lgtm` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#84](https://github.com/drivestream-lab/gateflow/issues/84) parent of W2 [#87](https://github.com/drivestream-lab/gateflow/issues/87); TASK-W2-01…04 in body |
| WorkManifest contract | `prayog/v1` §9 passes validator | [x] **pass** — `.venv/bin/python prayog-skills/scripts/workmanifest_contract.py …Implementation-Plan-INIT-GATEFLOW-007.md` (merged via [#106](https://github.com/drivestream-lab/gateflow/pull/106)) |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` | [x] complete — W2 tasks have `files` + `exit` + wave `verification` |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` | [x] contract — `verification.live.applicable: true`; deepen `tests/verify/verify_wave_closeout.py` |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — Gate 1 digests **WAIVED** (Q-1); feasibility + TDD CURRENT |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — **WAIVED** (Q-1) per plan §Source freshness |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies | [x] `.venv/bin/python -m tests.verify.verify_wave_closeout` |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` is Pass-2 pin skill (orchestrated) |
| Co-shipped live verify (P15) | FILE path under `live_verify_dir` listed | [x] path — FILE-W2-01 `tests/verify/verify_wave_closeout.py` (deepen smoke → dogfood) |
| Prior wave as-built row | `human_approved` | [x] W1 = **human_approved** — [#102](https://github.com/drivestream-lab/gateflow/pull/102) @ `c4ce8f6` (recorded on develop via #106) |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] exists — `Ground-Report-INIT-GATEFLOW-007-W1.md` (outcome **pass**) |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W2 |

**Gate verdict:** **PASS**

**Forge readiness:** Cut `feature/INIT-GATEFLOW-007-w2-closeout-prove` from `develop` @ `99a82b1`, then `/commit-workspace` to publish this checklist. Do **not** open Draft PR from this skill.

---

### Contracts consumed (from prior Ground Report)

> Read `Ground-Report-INIT-GATEFLOW-007-W1.md` §Contracts produced.
> Scan `source_roots` to confirm — not spec text alone.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Learning fence document | `LearningExtractDocument` | fenced `learning_extract:` YAML | validated items + enums | Ground-Report-W1; `src/models/learning_models.py` | [x] yes |
| Learning ORM + Alembic | `learning_extracts` / `learning_items` | run-scoped header + L-* rows | durable rows | Ground-Report-W1; `learning_schema.py`; `cc5feda8fe3d` | [x] yes |
| Learning repository | `upsert_extract` / `get_by_run_id` / `list_items` | session + create DTO + items | `LearningExtractModel` | Ground-Report-W1; `learning_repository.py` | [x] yes — prefer assert by `run_id` (latest extract); `list_items` aggregates initiative+wave |
| Learning ingest | `ingest_after_learning_extract` | run + workspace (+ optional tip SHA) | upserted extract | Ground-Report-W1; `learning_ingest_service.py` | [x] yes |
| Orchestrator hook | after handoff when node=`learning-extract` | session + run + workspace | continue or FAILED | Ground-Report-W1; `run_orchestrator.py` | [x] yes — publish → handoff → ingest → policy |
| Closeout start (W0) | `POST /api/v1/waves/closeout/start` | closeout body + programme token | `run_id`; Enter-at `learning-extract` | Ground-Report-W0; tip | [x] yes |
| Verify smoke base | `tests/verify/verify_wave_closeout` | `features.wave_closeout` | exit 0 smoke | Ground-Report-W0/W1 | [x] yes — deepen in TASK-W2-01 |

**Unconfirmed contracts:** none blocking. Live Pass-2 stop @ `wave-signoff` + learning row evidence are **this wave's** prove-it.

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered):
  - [x] `testing-verify-flows.mdc` — live verify vs pytest; feature map; config pattern
  - [x] `spec-driven-development.mdc` — as-built + README with behavior
  - [x] `fail-fast.mdc` — dogfood asserts fail closed when knobs require learning evidence
  - [ ] skipped — `http-api-conventions.mdc` / `repository-pattern.mdc` / `database-migrations.mdc` (no new HTTP/ORM)
- [x] ADRs:
  - [x] ADR-001 — Postgres learning SSOT (assert rows; no skill→HTTP)
  - [x] ADR-008 — baton / handoff for Pass-2 hops
  - [x] ADR-009 — publish-before-ingest already on tip
  - [x] ADR-010 §6 — closeout Enter-at `learning-extract`
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-007-gateflow.md` — REQ-7, REQ-9, REQ-12, REQ-14…17
- [x] Plan / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-007.md` W2
- [x] Board: https://github.com/drivestream-lab/gateflow/issues/87 — TASK projection:
  - [ ] TASK-W2-01 — REQ-7, REQ-9, REQ-14 — `verify_wave_closeout.py` + `config.yaml.example` — full dogfood exit 0
  - [ ] TASK-W2-02 — REQ-12, REQ-14, REQ-17 — as-built + `tests/README.md` — live row / L-* cite
  - [ ] TASK-W2-03 — REQ-15 — as-built — spec live or PE-waived deferral
  - [ ] TASK-W2-04 — REQ-16 — inspect/confirm `src/` clean of `gate-1`/`gate-2`/`wave-human-decision` (already clean on tip)

---

### Governance alignment

- [x] Spec does not contradict listed Accepted ADRs
- [x] Plan TASK MDC / ADR notes for W2 reviewed
- [x] Q-6 (REQ-15) — implement live first; document PE deferral if spec-lane skipped

---

### Must update (via `/loop-spec`)

- [ ] `tests/verify/verify_wave_closeout.py` + `tests/config.yaml.example` — dogfood depth
- [ ] `as-built/implementation-status.md` — W2 live row; REQ-15 parity or deferral
- [ ] `tests/README.md` — smoke vs full dogfood knobs
- [ ] Unit only if new helpers warrant it (do not duplicate live Pass-2 journey)
- [ ] Product spec / ADR — only on real contract drift

---

### Must not

- [ ] Contradict Accepted ADRs without superseding
- [ ] Duplicate full Pass-2 HTTP journey in pytest
- [ ] Skill→Gateflow HTTP for learning success (H6)
- [ ] Agent-write Alembic `versions/`
- [ ] Open branch / commit / PR / labels / board issues from this skill

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | Format, lint, types, layers | `make check` |
| Unit | Checkpoint hygiene / helper edges | `make test` |
| Live verify | Pass-2 implement closeout → `wave-signoff`; learning when configured | `.venv/bin/python -m tests.verify.verify_wave_closeout` |
| Ground check | Assigned REQs after live-verify | `/ground-spec` (Pass-2) — N/A Makefile |

### Human live-verify (after loop-spec)

- [ ] Run verify with dogfood knobs (API + worker + tip + migration)
- [ ] Capture `Live-Verify-INIT-GATEFLOW-007-W2.md`
- [ ] Tip hygiene before Pass-2 closeout if hotfixes land

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-007
- Issue: [#87](https://github.com/drivestream-lab/gateflow/issues/87)
- Spec path: `docs/specification/product/INIT-GATEFLOW-007-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_wave_closeout`
- ADRs: ADR-001, ADR-008, ADR-009, ADR-010
- Wave head: cut `feature/INIT-GATEFLOW-007-w2-closeout-prove` from `develop` @ `99a82b1`

---

### Checklist publish readiness (on `pass`)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` |
| Next | `loop-spec` — `human_checkpoint: false` |
| Forge (this hop) | `commit_workspace` **required** — publish checklist onto wave `head_ref` |
| Later | After `/loop-spec` → `wave-pr-action` (Draft PR) |

Recommend: cut wave branch → `/commit-workspace` → `/loop-spec`.

---

### Merge order

N/A — gateflow-only. W0/W1 + chore #106 already on `develop`.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-007-W2.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-007
    wave: W2
    board_issue: "87"
    epic_issue: "84"
    prior_wave: W1
    prior_merge: "c4ce8f65f8f2cdfdc8bb1ce5f411166e662627c3"
    develop_tip: "99a82b1ddf201dfec9fe6986a2f5782e0976540f"
    chore_workmanifest_pr: "106"
    workmanifest_contract: pass
    assigned_tasks:
      - TASK-W2-01
      - TASK-W2-02
      - TASK-W2-03
      - TASK-W2-04
    assigned_reqs:
      - REQ-7
      - REQ-9
      - REQ-12
      - REQ-14
      - REQ-15
      - REQ-16
      - REQ-17
    check_command: "make check"
    test_command: "make test"
    verify_command: ".venv/bin/python -m tests.verify.verify_wave_closeout"
    p15: deepen_verify_wave_closeout
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    draft: false
    apply_labels: []
    remove_labels: []
    title: "[INIT-GATEFLOW-007] W2 — Pre-implement checklist"
    body_path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-007-W2.md
    head_ref: feature/INIT-GATEFLOW-007-w2-closeout-prove
    base_ref: develop
```

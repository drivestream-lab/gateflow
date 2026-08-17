# INIT-GATEFLOW-019 — spec slice for gateflow (lane start binds)

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-019 |
| PRD | **skipped** — no `prayog-meta` Gate 1 this pass (local backfill) |
| PRD digest (H1) | **pending** |
| Meta PR | **pending** |
| Impact map | **pending** |
| Repo scope digest (H2) | **pending** |
| Tech-lead approval | **pending** — engineering backfill so as-built matches the Mission Control walk |
| Architecture | ADR-010 (lane intake); ADR-016 (tenant-scoped delivery); ADR-019 (JWT no programme claim) |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-15 |
| Status | Draft — **Gate 1 skipped**; not `/pre-implement` / board-seed ready. Consumer: sibling repo `gateflow-ops` `docs/specification/product/INIT-GATEFLOW-019-gateflow-ops.md`. |

> Local SSOT for this backfill. Remap `REQ-*` 1:1 if a later meta PRD assigns different numbers.

## Overview

Ops already starts spec / implement / closeout (016 CAP-C) by **forwarding a PE-shaped body**. The operator walk we want is: list last-10 meta PRs → **onboard** → start spec with programme-derived binds → later lanes from wave tickets. GitHub stays the governance log. Gateflow stays the join. Catalogue fetch does not admit. No backfill of walks that never ran here.

This slice is **gateflow only** (provider). Ops screens are the consumer INIT.

**016-ops D2 does not apply** — that INIT forbade contract change. This INIT **is** the contract change.

## Capabilities

| CAP | Intent |
|-----|--------|
| **CAP-A** | Meta PR picker + CAP-01 + join to spec run |
| **CAP-B** | Spec start resolves workspaces; omit paths / `start_node` / slug |
| **CAP-C** | Implement slug default; closeout unchanged (ticket + app PR) |
| **CAP-D** | Ground already-coded bind/connect/list hardening (`c575356`) |

## Functional requirements

| ID | Requirement | CAP | Wave |
|----|-------------|-----|------|
| REQ-01 | Authenticated caller can list the programme meta repo's PRs that **derive** `INIT-*` (open or merged). Return the **last 10** only. PRs with no derivable initiative are omitted | CAP-A | W1 |
| REQ-02 | Each listed PR includes `prd-impact-acceptance` (required `impact-map-lgtm`, no blocking labels, APPROVED review on **current** head — stale if `commit_id` ≠ head). The GitHub list + CAP-01 slice may be Redis-cached for `REDIS_META_PR_PICKER_TTL` (default 10 hours). `refresh=true` skips the cache, fetches GitHub, rewrites the cache, and returns that page. Spec start still evaluates live (REQ-09). Spec-run join is never cached | CAP-A | W1 |
| REQ-03 | Each listed PR includes join: spec runs per `(meta_pr_url, org, repo)` or an empty list. Missing run ≠ fabricated history. Do not attach another repo's spec run | CAP-A | W1 |
| REQ-04 | Spec start **resolves** app and meta workspaces as `{workspace_root}/{org}/{repo}` (clone/fetch). Client paths optional; missing tree is resolved, not guessed | CAP-B | W2 |
| REQ-05 | Spec start does not require `start_node` (pin default `spec-draft`) or `branch_slug` (head is `feature/{INIT}-spec`) | CAP-B | W2 |
| REQ-06 | Spec start derives `initiative_id` from the meta PR when omitted; mismatch with a supplied id fails closed | CAP-B | W2 |
| REQ-07 | Spec `org`/`repo` is the **app** repo, derived from the programme's admitted fleet when omitted. One admitted repo → derive. Several → required. Zero → named refuse. Meta org/repo is not a valid spec target | CAP-B | W2 |
| REQ-08 | When `runner` / `model_id` omitted, use `lane_defaults[spec]`. Empty defaults → named refuse (no invented runner) | CAP-B | W2 |
| REQ-09 | Spec start fails closed when CAP-01 is not satisfied (UI-only is not enough) | CAP-B | W2 |
| REQ-10 | Implement start: omitted `branch_slug` defaults to `implement`. Ticket + Done-column gate unchanged | CAP-C | W2 |
| REQ-11 | Closeout start remains ticket + existing app `pr_number`; slug / `start_node` stay unused for publish head | CAP-C | W2 |
| REQ-12 | Login/me grant rows include `tenant_id` + `programme_name` (join on `programmes`). No password; no factory roster | CAP-D | W0 |
| REQ-13 | Programme create auto-connects the onboarded meta checkout (no extra connect for catalogue browse) | CAP-D | W0 |
| REQ-14 | Connect target must be the programme meta repo; empty body defaults to that meta; mismatch → named refuse | CAP-D | W0 |
| REQ-15 | Initiative list/detail still returns Gateflow-owned runs when the board EPIC list is unavailable | CAP-D | W0 |
| REQ-16 | Forge `find_issues_by_labels` treats GitHub 404 as empty (no raise) | CAP-D | W0 |
| REQ-17 | Authenticated caller can list implemented runners and the models under each runner. Today that is Cursor and its first-party models. Stub runners are omitted | CAP-B | W2 |
| REQ-18 | Authenticated caller can **onboard** one INIT-* meta PR on this programme's meta repo (`POST …/meta/pulls/onboard`). Wrong repo → `meta_pr_wrong_repo`. Non-INIT → `not_init_meta_pr`. Idempotent when already admitted | CAP-A | W1 |
| REQ-19 | Catalogue `GET …/meta/pulls` includes `onboarded` per row. Listing does not admit | CAP-A | W1 |
| REQ-20 | Authenticated caller can list the admitted set (`GET …/meta/pulls/onboarded`) without a GitHub last-10 list. CAP-01 is live per row | CAP-A | W1 |
| REQ-21 | Spec start fails closed with `meta_pr_not_onboarded` when a programme is bound and the meta PR is not admitted | CAP-B | W2 |

## Out of scope

- `prayog-meta` PRD / impact map (skipped this pass)
- gateflow-ops screens (consumer INIT)
- Reconstructing pre-factory walks from GitHub
- Changing closeout/closure Enter-at
- New programme roles

## Open questions (defaults if PE silent)

| # | Default |
|---|---------|
| Q1 | Last 10 INIT-derived meta PRs (open + merged); no larger page |
| Q2 | REQ-09 on the **API** (not UI-only) |
| Q3 | CAP-D already on `fix/session-grant-tenant-binding` @ `c575356` — W0 grounds it, does not re-implement |

# Production path — gh-free inspection checklist (FR-25 / FR-26a)

Use before declaring INIT-GATEFLOW-002 W2 done.

| # | Check | How | Pass? |
|---|-------|-----|-------|
| 1 | ForgeClient source has no `subprocess` / `Popen` / `os.system` / `gh` CLI | `make test` → `test_forge_client_source_has_no_gh_subprocess` | |
| 2 | Production uses `GITHUB_AUTH_MODE=app`; `pat` rejected | Unit: `PatTokenProvider` / InfraModule raise when `APP_ENVIRONMENT=production` and mode=`pat` (ADR-003; TDD §3.5a) | |
| 3 | Board writes use ForgeClient httpx only | `BoardService` → `board_*` methods; routes never shell | |
| 4 | PR/comment path uses ForgeClient only | `create_or_update_pull_request` / `post_comment` | |
| 5 | Worker does not call board mutations | `test_process_job_never_calls_board_forge_mutations` | |
| 6 | Laptop `gh` policy documented separately | `docs/runbooks/laptop-gh-vs-deploy-forgeclient.md` (FR-26b) | |

Runtime rule: Gateflow **deploy** must not enable a `gh` transport. Laptop
board-seed may still use `gh` outside this process.

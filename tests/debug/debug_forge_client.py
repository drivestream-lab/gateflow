"""Live debug: ForgeClient against .env credentials (PAT or App).

Does not start the HTTP API. Loads ``.env``, ``tests/config.yaml`` (optional),
and exercises branch → PR → comment using the same settings/token path as
runtime ForgeClient.

Usage:
  cp tests/config.yaml.example tests/config.yaml   # optional
  set -a && source .env && set +a
  .venv/bin/python -m tests.debug.debug_forge_client

Cleanup (default on): closes the probe PR and deletes the probe branch.
  GATEFLOW_FORGE_PROBE_CLEANUP=0 to leave PR/branch for inspection.
"""

from __future__ import annotations

import asyncio
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv

from src.configs.base_settings import BaseSettings
from src.configs.github_settings import GithubSettings
from src.di.modules.infra_module import InfraModule
from src.infra_services.forge_client import ForgeClient
from src.models.github_auth_types import GithubAuthModeType
from tests._helpers.tests_config import load_tests_config


def _reset_settings() -> None:
    BaseSettings._instances.pop("GithubSettings", None)
    BaseSettings._instances.pop("AppSettings", None)


async def _cleanup(
    forge: ForgeClient,
    *,
    org: str,
    repo: str,
    branch: str,
    pr_number: int,
) -> None:
    client = forge._require_client()
    closed = await client.patch(
        f"/repos/{org}/{repo}/pulls/{pr_number}",
        json={"state": "closed"},
    )
    if closed.status_code >= 400:
        print(f"[WARNING] close PR #{pr_number} → {closed.status_code}: {closed.text[:200]}")
    else:
        print(f"[OK] closed probe PR #{pr_number}")

    deleted = await client.delete(ForgeClient._git_ref_update_path(org, repo, branch))
    if deleted.status_code not in {204, 404}:
        print(f"[WARNING] delete branch {branch} → {deleted.status_code}: {deleted.text[:200]}")
    else:
        print(f"[OK] deleted probe branch {branch}")


async def async_main() -> int:
    root = Path(__file__).resolve().parents[2]
    load_dotenv(root / ".env")
    _reset_settings()

    cfg = load_tests_config()
    forge_cfg = cfg.forge
    settings = GithubSettings.get_instance()

    print(f"[INFO] GITHUB_AUTH_MODE={settings.auth_mode.value}")
    print(f"[INFO] api_base_url={settings.api_base_url}")
    print(f"[INFO] target={forge_cfg.org}/{forge_cfg.repo} base={forge_cfg.base_branch}")

    if settings.auth_mode == GithubAuthModeType.PAT and not settings.personal_access_token:
        print("[ERROR] GITHUB_AUTH_MODE=pat but GITHUB_PERSONAL_ACCESS_TOKEN unset")
        return 1
    if settings.auth_mode == GithubAuthModeType.APP and (
        not settings.app_id or not settings.private_key_path
    ):
        print("[ERROR] GITHUB_AUTH_MODE=app but App id / private key path incomplete")
        return 1

    token_provider = InfraModule().provide_github_token_provider()
    forge = ForgeClient(token_provider=token_provider)
    await forge.initialize()
    print("[OK] ForgeClient initialized from .env token provider")

    suffix = uuid.uuid4().hex[:8]
    branch = f"{forge_cfg.probe_branch_prefix}{suffix}"
    title = f"[gateflow debug] forge probe {suffix}"
    body = (
        "Automated ForgeClient debug probe.\n\n"
        "Safe to close. Created by `python -m tests.debug.debug_forge_client`."
    )

    try:
        created_branch = await forge.ensure_branch_from_base(
            forge_cfg.org,
            forge_cfg.repo,
            branch=branch,
            base=forge_cfg.base_branch,
        )
        print(f"[OK] ensure_branch_from_base branch={branch} created={created_branch}")

        pr_number = await forge.create_or_update_pull_request(
            forge_cfg.org,
            forge_cfg.repo,
            title=title,
            body=body,
            head=branch,
            base=forge_cfg.base_branch,
        )
        print(f"[OK] create_or_update_pull_request pr_number={pr_number}")

        comment_id = await forge.post_comment(
            forge_cfg.org,
            forge_cfg.repo,
            pr_number,
            f"ForgeClient debug comment `{suffix}` — PAT/App path OK.",
        )
        print(f"[OK] post_comment comment_id={comment_id} on PR/issue #{pr_number}")

        issue = await forge.create_issue(
            forge_cfg.org,
            forge_cfg.repo,
            title=f"[gateflow debug] issue probe {suffix}",
            body="Debug issue from ForgeClient; close/delete as needed.",
            labels=[],
        )
        issue_number = int(issue["number"])
        print(f"[OK] create_issue issue_number={issue_number}")

        cleanup = os.environ.get("GATEFLOW_FORGE_PROBE_CLEANUP", "1").strip().lower() in {
            "1",
            "true",
            "yes",
        }
        if cleanup:
            await _cleanup(
                forge,
                org=forge_cfg.org,
                repo=forge_cfg.repo,
                branch=branch,
                pr_number=pr_number,
            )
            # Close debug issue (best-effort)
            client = forge._require_client()
            closed_issue = await client.patch(
                f"/repos/{forge_cfg.org}/{forge_cfg.repo}/issues/{issue_number}",
                json={"state": "closed"},
            )
            if closed_issue.status_code < 400:
                print(f"[OK] closed probe issue #{issue_number}")
            else:
                print(
                    f"[WARNING] close issue #{issue_number} → "
                    f"{closed_issue.status_code}: {closed_issue.text[:200]}"
                )
        else:
            print(
                f"[INFO] cleanup skipped — PR #{pr_number} branch={branch} "
                f"issue=#{issue_number} left open"
            )

        print("[OK] ForgeClient live probe passed")
        return 0
    except Exception as exc:
        print(f"[ERROR] ForgeClient probe failed: {type(exc).__name__}: {exc}")
        response = getattr(exc, "response", None)
        if response is not None:
            print(f"[ERROR] response status={response.status_code} body={response.text[:500]}")
        return 1
    finally:
        await forge.close()


def main() -> None:
    raise SystemExit(asyncio.run(async_main()))


if __name__ == "__main__":
    main()

"""Shared Launchpad CLI subprocess helpers (status + apply-harness)."""

from __future__ import annotations

import asyncio
import os
import shutil
from pathlib import Path


def launchpad_binary_available(cli_path: str) -> bool:
    cli = cli_path.strip() or "launchpad"
    path = Path(cli)
    if path.is_file() and os.access(path, os.X_OK):
        return True
    return shutil.which(cli) is not None


def resolve_launchpad_config_dir(meta_path: Path) -> Path:
    """Launchpad ``--config-dir`` is the meta ``config/`` directory, not the checkout root."""
    nested = meta_path / "config"
    if nested.is_dir():
        return nested
    return meta_path


def resolve_launchpad_workspace_root(repo_path: Path) -> Path:
    """Launchpad ``--workspace`` is the parent of the repo clone directory."""
    return repo_path.parent


async def run_launchpad_cli(argv: list[str], *, github_token: str) -> tuple[int, str, str]:
    """Run Launchpad; return ``(exit_code, stdout, stderr)``.

    With ``--format json``, JSON is on stdout and human TTY on stderr.
    """
    env = {**os.environ, "GITHUB_TOKEN": github_token}
    proc = await asyncio.create_subprocess_exec(
        *argv,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )
    stdout_b, stderr_b = await proc.communicate()
    code = proc.returncode if proc.returncode is not None else 1
    stdout = (stdout_b or b"").decode("utf-8", errors="replace")
    stderr = (stderr_b or b"").decode("utf-8", errors="replace")
    return code, stdout, stderr

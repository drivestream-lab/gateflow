"""Collect workspace paths eligible for forge commit_workspace publish."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path, PurePosixPath

# Hard denylist — never publish even if git status surfaces them.
_SECRET_BASENAME_EXACT = frozenset(
    {
        ".env",
        "credentials.json",
        "secrets.yaml",
        "secrets.yml",
        "id_rsa",
        "id_ed25519",
    }
)
_SECRET_BASENAME_PREFIXES = (".env.",)
_SECRET_SUFFIXES = (".pem", ".key", ".p12", ".pfx")
_SECRET_PATH_PARTS = frozenset({"github-secrets", ".ssh", ".aws"})
_HANDOFF_BASENAME = "handoff.md"


def collect_commit_paths(
    workspace_path: str | Path,
    *,
    handoff_root: str | Path | None = None,
    base_ref: str | None = None,
) -> list[str]:
    """Return relative POSIX paths to include in a forge commit.

    Happy path (packaged skills): leave the tree **dirty**; Forge publishes
    ``git status`` paths. Skills must not ``git commit`` / ``git push`` /
    ``gh`` — remote tip publish is ForgeClient only (ADR-009).

    Safety net: when ``base_ref`` is set (remote tip SHA/ref), also include
    files changed on ``base_ref..HEAD`` so a mistaken local commit still
    publishes content ahead of the run head.

    Uses ``git status --porcelain`` so **gitignore** applies to untracked
    files. Applies a hard secret denylist and excludes ``handoff_root``.
    """
    root = Path(workspace_path).resolve()
    if not root.is_dir():
        raise ValueError(f"workspace_path is not a directory: {root}")

    handoff_resolved: Path | None = None
    if handoff_root is not None and str(handoff_root).strip():
        handoff_resolved = Path(str(handoff_root).strip()).resolve()

    candidates: list[str] = []
    seen: set[str] = set()

    for rel in _git_porcelain(root):
        _maybe_add(
            rel,
            root=root,
            handoff_root=handoff_resolved,
            seen=seen,
            candidates=candidates,
        )

    if base_ref is not None and str(base_ref).strip():
        for rel in _git_diff_name_only(root, str(base_ref).strip()):
            _maybe_add(
                rel,
                root=root,
                handoff_root=handoff_resolved,
                seen=seen,
                candidates=candidates,
            )

    candidates.sort()
    return candidates


def _maybe_add(
    rel: str,
    *,
    root: Path,
    handoff_root: Path | None,
    seen: set[str],
    candidates: list[str],
) -> None:
    if rel in seen:
        return
    if _is_denied(rel, root=root, handoff_root=handoff_root):
        return
    abs_path = root / rel
    if not abs_path.is_file():
        # Deletions / dirs skipped in v1 — blobs need on-disk content.
        return
    seen.add(rel)
    candidates.append(rel)


def _git_porcelain(root: Path) -> list[str]:
    """Parse ``git status --porcelain=v1 -uall`` paths (gitignore-aware)."""
    proc = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain=v1", "-uall"],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        raise ValueError(f"git status failed in {root}: {err or proc.returncode}")

    paths: list[str] = []
    for line in proc.stdout.splitlines():
        if len(line) < 4:
            continue
        # XY␠path  or  XY␠old -> new (rename)
        entry = line[3:]
        if " -> " in entry:
            entry = entry.split(" -> ", 1)[1]
        entry = entry.strip().strip('"')
        if not entry:
            continue
        rel = PurePosixPath(entry.replace("\\", "/"))
        if rel.is_absolute() or ".." in rel.parts:
            continue
        paths.append(str(rel))
    return paths


def _git_diff_name_only(root: Path, base_ref: str) -> list[str]:
    """Files changed between ``base_ref`` and ``HEAD`` (Added/Copied/Modified/Renamed).

    This is a **safety net** for mistaken local commits ahead of the remote tip.
    When ``base_ref`` is a remote SHA that has not been fetched into the local
    object database (e.g. a bootstrap commit created on GitHub by
    ``ensure_branch_from_base``), git emits ``fatal: Invalid revision range``
    or ``bad revision``.  In that case we degrade to ``[]`` — the primary
    dirty/untracked collection in :func:`collect_commit_paths` still publishes
    the agent's actual output.
    """
    proc = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "diff",
            "--name-only",
            "--diff-filter=ACMR",
            f"{base_ref}..HEAD",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        if _is_unknown_revision_error(err):
            return []
        raise ValueError(f"git diff {base_ref}..HEAD failed in {root}: {err or proc.returncode}")

    paths: list[str] = []
    for line in proc.stdout.splitlines():
        entry = line.strip().strip('"')
        if not entry:
            continue
        rel = PurePosixPath(entry.replace("\\", "/"))
        if rel.is_absolute() or ".." in rel.parts:
            continue
        paths.append(str(rel))
    return paths


def _is_unknown_revision_error(stderr: str) -> bool:
    """True when git cannot resolve ``base_ref`` locally (remote-only SHA)."""
    markers = (
        "Invalid revision range",
        "bad revision",
        "bad object",
        "Not a valid commit name",
        "ambiguous argument",
        "no such commit",
    )
    return any(m.lower() in stderr.lower() for m in markers)


def _is_denied(rel: str, *, root: Path, handoff_root: Path | None) -> bool:
    posix = PurePosixPath(rel)
    name = posix.name
    lower_name = name.lower()

    if name in _SECRET_BASENAME_EXACT or lower_name in _SECRET_BASENAME_EXACT:
        return True
    if any(name.startswith(p) or lower_name.startswith(p) for p in _SECRET_BASENAME_PREFIXES):
        return True
    if any(lower_name.endswith(suf) for suf in _SECRET_SUFFIXES):
        return True
    if any(part in _SECRET_PATH_PARTS for part in posix.parts):
        return True
    if re.search(r"(^|/)(secret|credentials?|passwd|password)s?(\.|$)", rel, re.IGNORECASE):
        if lower_name.endswith((".json", ".yaml", ".yml", ".toml", ".env")):
            return True

    abs_path = (root / rel).resolve()
    if handoff_root is not None:
        try:
            abs_path.relative_to(handoff_root)
            return True
        except ValueError:
            pass
        if name == _HANDOFF_BASENAME and "GATEFLOW_HANDOFF" in rel.upper():
            return True

    return False

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
) -> list[str]:
    """Return relative POSIX paths to include in a forge commit.

    Uses ``git status --porcelain`` so **gitignore** (and global excludes) apply
    to untracked files. Additionally applies a hard secret denylist and
    excludes anything under ``handoff_root`` (run batons are not product tree).
    """
    root = Path(workspace_path).resolve()
    if not root.is_dir():
        raise ValueError(f"workspace_path is not a directory: {root}")

    handoff_resolved: Path | None = None
    if handoff_root is not None and str(handoff_root).strip():
        handoff_resolved = Path(str(handoff_root).strip()).resolve()

    status = _git_porcelain(root)
    candidates: list[str] = []
    seen: set[str] = set()
    for rel in status:
        if rel in seen:
            continue
        if _is_denied(rel, root=root, handoff_root=handoff_resolved):
            continue
        abs_path = root / rel
        if not abs_path.is_file():
            # Deletions / dirs skipped in v1 — blobs need on-disk content.
            continue
        seen.add(rel)
        candidates.append(rel)
    candidates.sort()
    return candidates


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
        # Normalize to POSIX relative path (no leading ./)
        rel = PurePosixPath(entry.replace("\\", "/"))
        if rel.is_absolute() or ".." in rel.parts:
            continue
        paths.append(str(rel))
    return paths


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
    # Common credential filename patterns
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
        # Also exclude if relative path looks like a baton under a known root name
        if name == _HANDOFF_BASENAME and "GATEFLOW_HANDOFF" in rel.upper():
            return True

    return False

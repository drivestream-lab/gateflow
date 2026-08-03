"""Unit tests for workspace commit path collection (gitignore + denylist)."""

import subprocess
from pathlib import Path

from src.business_services.workspace_commit_paths import collect_commit_paths


def _git_init(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "test"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    (root / ".gitignore").write_text(".venv/\n*.pyc\nlocal.secret\n", encoding="utf-8")
    (root / "README.md").write_text("hi\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md", ".gitignore"], cwd=root, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=root,
        check=True,
        capture_output=True,
    )


def test_collect_includes_dirty_tracked_and_untracked(tmp_path: Path) -> None:
    _git_init(tmp_path)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "note.md").write_text("n\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("changed\n", encoding="utf-8")

    paths = collect_commit_paths(tmp_path)
    assert "docs/note.md" in paths
    assert "README.md" in paths


def test_collect_respects_gitignore(tmp_path: Path) -> None:
    _git_init(tmp_path)
    (tmp_path / "local.secret").write_text("nope\n", encoding="utf-8")
    (tmp_path / "keep.md").write_text("yes\n", encoding="utf-8")

    paths = collect_commit_paths(tmp_path)
    assert "keep.md" in paths
    assert "local.secret" not in paths


def test_collect_denies_dotenv_even_if_forced(tmp_path: Path) -> None:
    _git_init(tmp_path)
    # Force-add would still show in status if we add -f; denylist must catch basename.
    (tmp_path / ".env").write_text("SECRET=1\n", encoding="utf-8")
    subprocess.run(["git", "add", "-f", ".env"], cwd=tmp_path, check=True)
    paths = collect_commit_paths(tmp_path)
    assert ".env" not in paths


def test_collect_excludes_handoff_root(tmp_path: Path) -> None:
    _git_init(tmp_path)
    handoff_root = tmp_path / "batons"
    baton = handoff_root / "run-1" / "handoff.md"
    baton.parent.mkdir(parents=True)
    baton.write_text("x\n", encoding="utf-8")
    (tmp_path / "ok.md").write_text("y\n", encoding="utf-8")

    paths = collect_commit_paths(tmp_path, handoff_root=handoff_root)
    assert "ok.md" in paths
    assert not any(p.endswith("handoff.md") for p in paths)


def test_collect_includes_ahead_of_base_ref_when_clean(tmp_path: Path) -> None:
    """Safety net: local commit ahead of remote tip still surfaces for publish."""
    _git_init(tmp_path)
    base = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "shipped.md").write_text("committed locally\n", encoding="utf-8")
    subprocess.run(["git", "add", "docs/shipped.md"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "local ahead"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    # Working tree clean — dirty-only collect would miss the tip content.
    assert collect_commit_paths(tmp_path) == []
    paths = collect_commit_paths(tmp_path, base_ref=base)
    assert "docs/shipped.md" in paths


def test_collect_with_unknown_remote_sha_degrades_gracefully(tmp_path: Path) -> None:
    """base_ref SHA not in local object DB (remote-only bootstrap commit) → no crash.

    The ``base_ref..HEAD`` diff is a safety net for mistaken local commits.
    When the SHA only exists on the remote (e.g. ``ensure_branch_from_base``),
    git emits ``fatal: Invalid revision range``.  ``collect_commit_paths``
    must degrade to ``[]`` for the diff leg and still return dirty/untracked
    files (the agent's actual output).
    """
    _git_init(tmp_path)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "spec.md").write_text("new spec\n", encoding="utf-8")

    bogus_sha = "c93fb53eb6ac9fb895ddd303ab6e54ff9f56a71d"
    paths = collect_commit_paths(tmp_path, base_ref=bogus_sha)
    assert "docs/spec.md" in paths

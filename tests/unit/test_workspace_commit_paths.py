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
